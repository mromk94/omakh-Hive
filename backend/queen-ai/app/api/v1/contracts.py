"""
Smart Contract Deployment & Management API
Handles contract compilation, deployment, and tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import subprocess
import os
from datetime import datetime
import structlog

from app.api.v1.admin import verify_admin

router = APIRouter(tags=["contracts"])
logger = structlog.get_logger(__name__)

# Contract base path - Go up to project root, then into contracts
CONTRACTS_PATH = Path(__file__).parent.parent.parent.parent.parent.parent / "contracts" / "ethereum"

# Deployment history (in production, use database)
deployment_history = []
contract_status = {}


# ==================== REQUEST MODELS ====================

class CompileContractRequest(BaseModel):
    contract_name: str
    optimize: bool = True
    runs: int = 200


class DeployContractRequest(BaseModel):
    contract_name: str
    network: str  # sepolia, mainnet
    constructor_args: List[Any] = []
    gas_limit: Optional[int] = None
    gas_price: Optional[int] = None


class BatchDeployRequest(BaseModel):
    contracts: List[DeployContractRequest]
    network: str


class VerifyContractRequest(BaseModel):
    contract_address: str
    contract_name: str
    network: str
    constructor_args: List[Any] = []


# ==================== ENDPOINTS ====================

@router.get("/admin/contracts")
async def list_contracts(
    admin: bool = Depends(verify_admin)
):
    """
    List all smart contracts in the project
    """
    try:
        contracts = []
        
        # Scan contracts directory
        contracts_src = CONTRACTS_PATH / "src"
        if not contracts_src.exists():
            return {
                "success": False,
                "error": "Contracts directory not found",
                "path": str(contracts_src)
            }
        
        # Find all .sol files
        for sol_file in contracts_src.rglob("*.sol"):
            relative_path = sol_file.relative_to(contracts_src)
            contract_name = sol_file.stem
            
            # Check if compiled - artifacts are in artifacts/src/ not artifacts/contracts/
            artifacts_path = CONTRACTS_PATH / "artifacts" / "src" / relative_path.parent / f"{contract_name}.sol" / f"{contract_name}.json"
            is_compiled = artifacts_path.exists()
            
            # Get compilation time
            compiled_at = None
            if is_compiled:
                compiled_at = datetime.fromtimestamp(artifacts_path.stat().st_mtime).isoformat()
            
            # Get deployment status
            status = contract_status.get(contract_name, "not_deployed")
            
            # Get deployed addresses
            deployments = [d for d in deployment_history if d["contract_name"] == contract_name]
            
            contracts.append({
                "name": contract_name,
                "path": str(relative_path),
                "full_path": str(sol_file),
                "is_compiled": is_compiled,
                "compiled_at": compiled_at,
                "status": status,
                "deployments": deployments,
                "deployment_count": len(deployments)
            })
        
        return {
            "success": True,
            "contracts": contracts,
            "total": len(contracts),
            "contracts_path": str(contracts_src)
        }
        
    except Exception as e:
        logger.error(f"Failed to list contracts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/contracts/{contract_name}/artifact")
async def get_contract_artifact(
    contract_name: str,
    admin: bool = Depends(verify_admin)
):
    """
    Get contract ABI and bytecode for frontend deployment
    """
    try:
        # Find contract artifacts
        contracts_src = CONTRACTS_PATH / "src"
        contract_file = None
        
        for sol_file in contracts_src.rglob(f"{contract_name}.sol"):
            contract_file = sol_file
            break
        
        if not contract_file:
            raise HTTPException(status_code=404, detail=f"Contract {contract_name} not found")
        
        # Get artifacts path
        relative_path = contract_file.relative_to(contracts_src)
        artifacts_path = CONTRACTS_PATH / "artifacts" / "src" / relative_path.parent / f"{contract_name}.sol" / f"{contract_name}.json"
        
        if not artifacts_path.exists():
            return {
                "success": False,
                "error": "Contract not compiled. Please compile first."
            }
        
        # Read artifact
        with open(artifacts_path, 'r') as f:
            artifact = json.load(f)
        
        return {
            "success": True,
            "abi": artifact.get("abi", []),
            "bytecode": artifact.get("bytecode", ""),
            "contract_name": contract_name
        }
        
    except Exception as e:
        logger.error(f"Failed to get contract artifact: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/contracts/save-deployment")
async def save_deployment(
    data: Dict[str, Any],
    admin: bool = Depends(verify_admin)
):
    """
    Save deployment information after successful deployment from frontend
    """
    try:
        deployment = {
            "id": f"deploy_{data['contract_name']}_{data['network']}_{int(datetime.utcnow().timestamp())}",
            "contract_name": data["contract_name"],
            "network": data["network"],
            "contract_address": data["contract_address"],
            "transaction_hash": data["transaction_hash"],
            "deployer": data["deployer"],
            "constructor_args": data.get("constructor_args", []),
            "status": "deployed",
            "created_at": datetime.utcnow().isoformat(),
            "deployed_at": datetime.utcnow().isoformat()
        }
        
        deployment_history.append(deployment)
        contract_status[data["contract_name"]] = "deployed"
        
        # Save to file
        deployments_dir = CONTRACTS_PATH / "deployments" / data["network"]
        deployments_dir.mkdir(parents=True, exist_ok=True)
        
        deployment_file = deployments_dir / f"{data['contract_name']}.json"
        with open(deployment_file, 'w') as f:
            json.dump(deployment, f, indent=2)
        
        logger.info(
            "Deployment saved",
            contract=data["contract_name"],
            network=data["network"],
            address=data["contract_address"]
        )
        
        return {
            "success": True,
            "message": "Deployment saved successfully",
            "deployment": deployment
        }
        
    except Exception as e:
        logger.error(f"Failed to save deployment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/contracts/{contract_name}")
async def get_contract_details(
    contract_name: str,
    admin: bool = Depends(verify_admin)
):
    """
    Get detailed information about a specific contract
    """
    try:
        # Find contract file
        contracts_src = CONTRACTS_PATH / "src"
        contract_file = None
        
        for sol_file in contracts_src.rglob(f"{contract_name}.sol"):
            contract_file = sol_file
            break
        
        if not contract_file:
            raise HTTPException(status_code=404, detail=f"Contract {contract_name} not found")
        
        # Read contract source
        source_code = contract_file.read_text()
        
        # Get ABI and bytecode if compiled
        relative_path = contract_file.relative_to(contracts_src)
        artifacts_path = CONTRACTS_PATH / "artifacts" / "src" / relative_path.parent / f"{contract_name}.sol" / f"{contract_name}.json"
        
        abi = None
        bytecode = None
        is_compiled = False
        
        if artifacts_path.exists():
            with open(artifacts_path, 'r') as f:
                artifact = json.load(f)
                abi = artifact.get("abi")
                bytecode = artifact.get("bytecode")
                is_compiled = True
        
        # Get deployments
        deployments = [d for d in deployment_history if d["contract_name"] == contract_name]
        
        return {
            "success": True,
            "contract": {
                "name": contract_name,
                "path": str(contract_file),
                "source_code": source_code,
                "is_compiled": is_compiled,
                "abi": abi,
                "bytecode": bytecode,
                "deployments": deployments
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get contract details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/contracts/compile")
async def compile_contracts(
    data: Optional[CompileContractRequest] = None,
    admin: bool = Depends(verify_admin)
):
    """
    Compile smart contracts using Hardhat
    """
    try:
        # Change to contracts directory
        original_dir = os.getcwd()
        os.chdir(CONTRACTS_PATH)
        
        logger.info("Compiling contracts", contract=data.contract_name if data else "all")
        
        # Run Hardhat compile
        cmd = ["npx", "hardhat", "compile"]
        if data and data.optimize:
            # Optimization is configured in hardhat.config.js
            pass
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        os.chdir(original_dir)
        
        if result.returncode == 0:
            # Update contract status
            if data and data.contract_name:
                contract_status[data.contract_name] = "compiled"
            
            return {
                "success": True,
                "message": "Contracts compiled successfully",
                "output": result.stdout,
                "contract": data.contract_name if data else "all"
            }
        else:
            return {
                "success": False,
                "error": "Compilation failed",
                "output": result.stderr
            }
    
    except subprocess.TimeoutExpired:
        os.chdir(original_dir)
        raise HTTPException(status_code=500, detail="Compilation timeout")
    except Exception as e:
        os.chdir(original_dir)
        logger.error(f"Compilation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/contracts/{contract_name}/deploy")
async def deploy_contract(
    contract_name: str,
    data: DeployContractRequest,
    admin: bool = Depends(verify_admin)
):
    """
    Deploy a smart contract to specified network
    
    IMPORTANT: This creates deployment scripts but doesn't execute yet.
    Use the admin UI to review and approve deployment.
    """
    try:
        # Validate network
        if data.network not in ["sepolia", "mainnet", "localhost"]:
            raise HTTPException(status_code=400, detail=f"Invalid network: {data.network}")
        
        # Check if contract is compiled
        relative_path = Path(contract_name + ".sol")
        artifacts_path = CONTRACTS_PATH / "artifacts" / "contracts" / relative_path.parent / f"{contract_name}.sol" / f"{contract_name}.json"
        
        if not artifacts_path.exists():
            return {
                "success": False,
                "error": "Contract not compiled. Please compile first."
            }
        
        # Create deployment record
        deployment = {
            "id": f"deploy_{contract_name}_{data.network}_{int(datetime.utcnow().timestamp())}",
            "contract_name": contract_name,
            "network": data.network,
            "constructor_args": data.constructor_args,
            "gas_limit": data.gas_limit,
            "gas_price": data.gas_price,
            "status": "prepared",
            "created_at": datetime.utcnow().isoformat(),
            "deployed_at": None,
            "contract_address": None,
            "transaction_hash": None,
            "deployer": "admin"
        }
        
        deployment_history.append(deployment)
        contract_status[contract_name] = "prepared"
        
        logger.info("Deployment prepared", deployment_id=deployment["id"])
        
        return {
            "success": True,
            "message": "Deployment prepared. Review and approve in the admin UI.",
            "deployment": deployment,
            "next_step": "Review deployment details and click 'Deploy' to execute"
        }
        
    except Exception as e:
        logger.error(f"Deployment preparation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/contracts/{deployment_id}/execute")
async def execute_deployment(
    deployment_id: str,
    admin: bool = Depends(verify_admin)
):
    """
    Execute a prepared deployment
    
    This actually deploys the contract to the blockchain.
    """
    try:
        from app.utils.deployment_helpers import (
            generate_deployment_script,
            execute_hardhat_deployment,
            cleanup_deployment_script,
            save_deployment_info,
            get_network_explorer_url
        )
        
        # Find deployment
        deployment = None
        deployment_index = None
        for i, d in enumerate(deployment_history):
            if d["id"] == deployment_id:
                deployment = d
                deployment_index = i
                break
        
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        if deployment["status"] != "prepared":
            return {
                "success": False,
                "error": f"Deployment status is '{deployment['status']}', must be 'prepared'"
            }
        
        # Update status
        deployment["status"] = "deploying"
        logger.info(f"Starting deployment execution", deployment_id=deployment_id)
        
        try:
            # Generate deployment script
            script_path = generate_deployment_script(
                contract_name=deployment["contract_name"],
                constructor_args=deployment["constructor_args"],
                deployment_id=deployment_id
            )
            
            logger.info(f"Generated deployment script: {script_path}")
            
            # Execute deployment
            result = execute_hardhat_deployment(
                script_path=script_path,
                network=deployment["network"],
                timeout=300  # 5 minutes
            )
            
            # Cleanup script
            cleanup_deployment_script(script_path)
            
            if result.get("success"):
                # Update deployment record with results
                deployment["status"] = "deployed"
                deployment["deployed_at"] = datetime.utcnow().isoformat()
                deployment["contract_address"] = result.get("contractAddress")
                deployment["transaction_hash"] = result.get("transactionHash")
                deployment["block_number"] = result.get("blockNumber")
                deployment["gas_used"] = result.get("gasUsed")
                deployment["deployer_address"] = result.get("deployer")
                
                # Save deployment info to file
                deployment_data = {
                    "contract": deployment["contract_name"],
                    "address": result.get("contractAddress"),
                    "transactionHash": result.get("transactionHash"),
                    "blockNumber": result.get("blockNumber"),
                    "gasUsed": result.get("gasUsed"),
                    "deployer": result.get("deployer"),
                    "network": deployment["network"],
                    "timestamp": deployment["deployed_at"],
                    "constructorArgs": deployment["constructor_args"]
                }
                save_deployment_info(
                    network=deployment["network"],
                    contract_name=deployment["contract_name"],
                    deployment_data=deployment_data
                )
                
                # Update contract status
                contract_status[deployment["contract_name"]] = "deployed"
                
                logger.info(
                    "Deployment successful",
                    contract=deployment["contract_name"],
                    address=result.get("contractAddress")
                )
                
                # Get explorer URL
                explorer_url = get_network_explorer_url(
                    deployment["network"],
                    result.get("contractAddress")
                )
                
                return {
                    "success": True,
                    "message": f"Contract {deployment['contract_name']} deployed successfully!",
                    "deployment": deployment,
                    "contract_address": result.get("contractAddress"),
                    "transaction_hash": result.get("transactionHash"),
                    "block_number": result.get("blockNumber"),
                    "gas_used": result.get("gasUsed"),
                    "explorer_url": explorer_url,
                    "network": deployment["network"]
                }
            else:
                # Deployment failed
                deployment["status"] = "failed"
                deployment["error"] = result.get("error", "Unknown error")
                
                logger.error(
                    "Deployment failed",
                    contract=deployment["contract_name"],
                    error=result.get("error")
                )
                
                return {
                    "success": False,
                    "error": result.get("error", "Deployment failed"),
                    "deployment": deployment,
                    "details": result
                }
        
        except Exception as deploy_error:
            # Update status to failed
            deployment["status"] = "failed"
            deployment["error"] = str(deploy_error)
            
            logger.error(f"Deployment execution error: {str(deploy_error)}")
            
            return {
                "success": False,
                "error": f"Deployment execution failed: {str(deploy_error)}",
                "deployment": deployment
            }
        
    except Exception as e:
        logger.error(f"Deployment execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/contracts/deployments")
async def list_deployments(
    network: Optional[str] = None,
    status: Optional[str] = None,
    admin: bool = Depends(verify_admin)
):
    """
    List all deployment records
    """
    try:
        deployments = deployment_history.copy()
        
        # Filter by network
        if network:
            deployments = [d for d in deployments if d["network"] == network]
        
        # Filter by status
        if status:
            deployments = [d for d in deployments if d["status"] == status]
        
        # Sort by created_at (newest first)
        deployments.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "success": True,
            "deployments": deployments,
            "total": len(deployments)
        }
        
    except Exception as e:
        logger.error(f"Failed to list deployments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/contracts/batch-deploy")
async def batch_deploy_contracts(
    data: BatchDeployRequest,
    admin: bool = Depends(verify_admin)
):
    """
    Prepare multiple contracts for deployment
    """
    try:
        results = []
        
        for contract_deploy in data.contracts:
            try:
                # Prepare each deployment
                deployment = {
                    "id": f"deploy_{contract_deploy.contract_name}_{data.network}_{int(datetime.utcnow().timestamp())}",
                    "contract_name": contract_deploy.contract_name,
                    "network": data.network,
                    "constructor_args": contract_deploy.constructor_args,
                    "gas_limit": contract_deploy.gas_limit,
                    "gas_price": contract_deploy.gas_price,
                    "status": "prepared",
                    "created_at": datetime.utcnow().isoformat(),
                    "deployed_at": None,
                    "contract_address": None,
                    "transaction_hash": None,
                    "deployer": "admin"
                }
                
                deployment_history.append(deployment)
                contract_status[contract_deploy.contract_name] = "prepared"
                
                results.append({
                    "contract": contract_deploy.contract_name,
                    "success": True,
                    "deployment_id": deployment["id"]
                })
                
            except Exception as e:
                results.append({
                    "contract": contract_deploy.contract_name,
                    "success": False,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "message": f"{successful}/{len(results)} contracts prepared for deployment",
            "results": results,
            "network": data.network
        }
        
    except Exception as e:
        logger.error(f"Batch deployment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/contracts/deployments/{deployment_id}")
async def cancel_deployment(
    deployment_id: str,
    admin: bool = Depends(verify_admin)
):
    """
    Cancel a prepared deployment
    """
    try:
        global deployment_history
        
        # Find and remove deployment
        deployment = None
        for i, d in enumerate(deployment_history):
            if d["id"] == deployment_id:
                if d["status"] not in ["prepared", "failed"]:
                    return {
                        "success": False,
                        "error": f"Cannot cancel deployment with status '{d['status']}'"
                    }
                deployment = deployment_history.pop(i)
                break
        
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        return {
            "success": True,
            "message": "Deployment cancelled",
            "deployment_id": deployment_id
        }
        
    except Exception as e:
        logger.error(f"Failed to cancel deployment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
