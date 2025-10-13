"""
Deployment Helper Utilities
Handles Hardhat script generation and deployment execution
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)

CONTRACTS_PATH = Path(__file__).parent.parent.parent.parent.parent / "contracts" / "ethereum"


def generate_deployment_script(
    contract_name: str,
    constructor_args: List[Any],
    deployment_id: str
) -> Path:
    """
    Generate a Hardhat deployment script for a specific contract
    
    Args:
        contract_name: Name of the contract to deploy
        constructor_args: Constructor arguments as a list
        deployment_id: Unique deployment ID
        
    Returns:
        Path to the generated script
    """
    # Read template
    template_path = CONTRACTS_PATH / "scripts" / "deploy_template.js"
    if not template_path.exists():
        raise FileNotFoundError(f"Deployment template not found at {template_path}")
    
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Format constructor args as JavaScript array
    args_js = json.dumps(constructor_args)
    
    # Replace placeholders
    script_content = template.replace("{{CONTRACT_NAME}}", contract_name)
    script_content = script_content.replace("{{CONSTRUCTOR_ARGS}}", args_js)
    
    # Generate unique script file
    script_name = f"deploy_{contract_name}_{deployment_id}.js"
    script_path = CONTRACTS_PATH / "scripts" / "generated" / script_name
    
    # Create generated directory if it doesn't exist
    script_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write script
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    logger.info(f"Generated deployment script: {script_path}")
    return script_path


def execute_hardhat_deployment(
    script_path: Path,
    network: str,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Execute a Hardhat deployment script
    
    Args:
        script_path: Path to the deployment script
        network: Network to deploy to (localhost, sepolia, mainnet)
        timeout: Timeout in seconds
        
    Returns:
        Deployment result dictionary
    """
    logger.info(f"Executing deployment on {network}", script=str(script_path))
    
    # Build command
    cmd = [
        "npx", "hardhat", "run",
        str(script_path),
        "--network", network
    ]
    
    try:
        # Execute deployment
        result = subprocess.run(
            cmd,
            cwd=CONTRACTS_PATH,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ}
        )
        
        # Parse output
        stdout = result.stdout
        stderr = result.stderr
        
        logger.info(f"Deployment stdout: {stdout}")
        if stderr:
            logger.warning(f"Deployment stderr: {stderr}")
        
        # Extract deployment result from output
        deployment_result = parse_deployment_output(stdout)
        
        if result.returncode == 0:
            logger.info("Deployment successful", result=deployment_result)
            return deployment_result
        else:
            logger.error("Deployment failed", returncode=result.returncode, stderr=stderr)
            return {
                "success": False,
                "error": stderr or "Deployment failed with no error message",
                "stdout": stdout,
                "stderr": stderr
            }
    
    except subprocess.TimeoutExpired:
        logger.error("Deployment timeout")
        return {
            "success": False,
            "error": f"Deployment timeout after {timeout} seconds"
        }
    
    except Exception as e:
        logger.error(f"Deployment execution error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def parse_deployment_output(output: str) -> Dict[str, Any]:
    """
    Parse deployment output to extract contract address and transaction hash
    
    Args:
        output: Raw stdout from Hardhat deployment
        
    Returns:
        Parsed deployment result
    """
    try:
        # Look for JSON result between markers
        start_marker = "--- DEPLOYMENT_RESULT_START ---"
        end_marker = "--- DEPLOYMENT_RESULT_END ---"
        
        if start_marker in output and end_marker in output:
            start_idx = output.index(start_marker) + len(start_marker)
            end_idx = output.index(end_marker)
            json_str = output[start_idx:end_idx].strip()
            
            result = json.loads(json_str)
            logger.info("Parsed deployment result", result=result)
            return result
        
        # Fallback: Try to parse from console output
        contract_address = None
        tx_hash = None
        
        # Look for contract address
        address_match = re.search(r"Contract Address: (0x[a-fA-F0-9]{40})", output)
        if address_match:
            contract_address = address_match.group(1)
        
        # Look for transaction hash
        tx_match = re.search(r"Transaction Hash: (0x[a-fA-F0-9]{64})", output)
        if tx_match:
            tx_hash = tx_match.group(1)
        
        if contract_address:
            return {
                "success": True,
                "contractAddress": contract_address,
                "transactionHash": tx_hash,
                "parsed_from": "regex_fallback"
            }
        
        # No result found
        logger.warning("Could not parse deployment result from output")
        return {
            "success": False,
            "error": "Could not parse deployment result",
            "raw_output": output[:500]  # First 500 chars
        }
    
    except Exception as e:
        logger.error(f"Error parsing deployment output: {str(e)}")
        return {
            "success": False,
            "error": f"Parse error: {str(e)}"
        }


def cleanup_deployment_script(script_path: Path) -> bool:
    """
    Clean up generated deployment script after execution
    
    Args:
        script_path: Path to the script to delete
        
    Returns:
        True if deleted, False otherwise
    """
    try:
        if script_path.exists():
            script_path.unlink()
            logger.info(f"Cleaned up deployment script: {script_path}")
            return True
        return False
    except Exception as e:
        logger.warning(f"Failed to cleanup script: {str(e)}")
        return False


def verify_contract_on_etherscan(
    contract_address: str,
    contract_name: str,
    constructor_args: List[Any],
    network: str,
    timeout: int = 120
) -> Dict[str, Any]:
    """
    Verify contract on Etherscan
    
    Args:
        contract_address: Deployed contract address
        contract_name: Name of the contract
        constructor_args: Constructor arguments
        network: Network name
        timeout: Timeout in seconds
        
    Returns:
        Verification result
    """
    logger.info(f"Verifying contract on Etherscan", address=contract_address, network=network)
    
    # Build command
    cmd = [
        "npx", "hardhat", "verify",
        "--network", network,
        contract_address
    ] + [str(arg) for arg in constructor_args]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=CONTRACTS_PATH,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            logger.info("Contract verified successfully")
            return {
                "success": True,
                "message": "Contract verified on Etherscan",
                "output": result.stdout
            }
        else:
            # Check if already verified
            if "already verified" in result.stdout.lower() or "already verified" in result.stderr.lower():
                logger.info("Contract already verified")
                return {
                    "success": True,
                    "message": "Contract already verified",
                    "already_verified": True
                }
            
            logger.error("Verification failed", stderr=result.stderr)
            return {
                "success": False,
                "error": result.stderr or "Verification failed",
                "output": result.stdout
            }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Verification timeout after {timeout} seconds"
        }
    
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def get_network_explorer_url(network: str, address: str) -> str:
    """
    Get Etherscan URL for a contract
    
    Args:
        network: Network name
        address: Contract address
        
    Returns:
        Etherscan URL
    """
    explorers = {
        "mainnet": "https://etherscan.io",
        "sepolia": "https://sepolia.etherscan.io",
        "goerli": "https://goerli.etherscan.io",
        "polygon": "https://polygonscan.com",
        "mumbai": "https://mumbai.polygonscan.com",
        "bsc": "https://bscscan.com",
        "bsc-testnet": "https://testnet.bscscan.com",
    }
    
    base_url = explorers.get(network, "https://etherscan.io")
    return f"{base_url}/address/{address}"


def get_deployment_info_path(network: str, contract_name: str) -> Path:
    """
    Get path to deployment info file
    
    Args:
        network: Network name
        contract_name: Contract name
        
    Returns:
        Path to deployment info JSON file
    """
    return CONTRACTS_PATH / "deployments" / network / f"{contract_name}.json"


def save_deployment_info(
    network: str,
    contract_name: str,
    deployment_data: Dict[str, Any]
) -> bool:
    """
    Save deployment information to file
    
    Args:
        network: Network name
        contract_name: Contract name
        deployment_data: Deployment data to save
        
    Returns:
        True if saved successfully
    """
    try:
        deployment_file = get_deployment_info_path(network, contract_name)
        deployment_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(deployment_file, 'w') as f:
            json.dump(deployment_data, f, indent=2)
        
        logger.info(f"Saved deployment info to {deployment_file}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to save deployment info: {str(e)}")
        return False


def load_deployment_info(network: str, contract_name: str) -> Optional[Dict[str, Any]]:
    """
    Load deployment information from file
    
    Args:
        network: Network name
        contract_name: Contract name
        
    Returns:
        Deployment data or None if not found
    """
    try:
        deployment_file = get_deployment_info_path(network, contract_name)
        if not deployment_file.exists():
            return None
        
        with open(deployment_file, 'r') as f:
            return json.load(f)
    
    except Exception as e:
        logger.error(f"Failed to load deployment info: {str(e)}")
        return None
