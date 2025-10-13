"""
Blockchain Connector - Interface with Ethereum contracts
Interacts with all 16 PRIME2 contracts
"""
from typing import Dict, Optional, Any, List
from web3 import Web3
from web3.contract import Contract
from eth_account import Account
import structlog
from pathlib import Path
import json

from app.config.settings import settings

logger = structlog.get_logger(__name__)


class BlockchainConnector:
    """
    Connects Queen AI to Ethereum blockchain
    
    Manages interactions with:
    - BeeSpawner (register/update bees)
    - All governance contracts (submit proposals)
    - System Dashboard (read metrics)
    - Bridge (manage cross-chain)
    """
    
    def __init__(self):
        self.w3: Optional[Web3] = None
        self.account: Optional[Account] = None
        
        # Contract instances
        self.bee_spawner: Optional[Contract] = None
        self.queen_controller: Optional[Contract] = None
        self.ecosystem_manager: Optional[Contract] = None
        self.treasury_vault: Optional[Contract] = None
        self.governance_manager: Optional[Contract] = None
        self.omk_bridge: Optional[Contract] = None
        self.system_dashboard: Optional[Contract] = None
        self.advisors_manager: Optional[Contract] = None
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize blockchain connection and contracts"""
        logger.info("Initializing blockchain connector")
        
        try:
            # Connect to Ethereum
            self.w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
            
            if not self.w3.is_connected():
                logger.warning("⚠️  Failed to connect to Ethereum node - blockchain features disabled")
                self.initialized = False
                return
            
            logger.info("Connected to Ethereum", 
                       chain_id=self.w3.eth.chain_id,
                       block_number=self.w3.eth.block_number)
            
            # Load Queen wallet
            if settings.QUEEN_WALLET_PRIVATE_KEY:
                self.account = Account.from_key(settings.QUEEN_WALLET_PRIVATE_KEY)
                logger.info("Queen wallet loaded", address=self.account.address)
            else:
                logger.warning("No Queen wallet private key configured")
            
            # Load contract ABIs and initialize contracts
            await self._load_contracts()
            
            self.initialized = True
            logger.info("Blockchain connector initialized successfully")
            
        except Exception as e:
            logger.warning("⚠️  Blockchain connector initialization failed - running without blockchain", error=str(e))
            self.initialized = False
    
    async def _load_contracts(self):
        """Load all contract instances"""
        contracts_dir = Path(__file__).parent.parent.parent.parent / "contracts" / "ethereum" / "abis"
        
        # BeeSpawner - For managing bee agents
        if settings.BEE_SPAWNER_ADDRESS:
            self.bee_spawner = await self._load_contract(
                "BeeSpawner",
                settings.BEE_SPAWNER_ADDRESS,
                contracts_dir
            )
            logger.info("BeeSpawner contract loaded")
        
        # System Dashboard - For reading metrics
        if settings.SYSTEM_DASHBOARD_ADDRESS:
            self.system_dashboard = await self._load_contract(
                "SystemDashboard",
                settings.SYSTEM_DASHBOARD_ADDRESS,
                contracts_dir
            )
            logger.info("SystemDashboard contract loaded")
        
        # Governance Manager - For DAO proposals
        if settings.GOVERNANCE_MANAGER_ADDRESS:
            self.governance_manager = await self._load_contract(
                "GovernanceManager",
                settings.GOVERNANCE_MANAGER_ADDRESS,
                contracts_dir
            )
            logger.info("GovernanceManager contract loaded")
        
        # Treasury Vault - For treasury proposals
        if settings.TREASURY_VAULT_ADDRESS:
            self.treasury_vault = await self._load_contract(
                "TreasuryVault",
                settings.TREASURY_VAULT_ADDRESS,
                contracts_dir
            )
            logger.info("TreasuryVault contract loaded")
        
        # Ecosystem Manager - For ecosystem operations
        if settings.ECOSYSTEM_MANAGER_ADDRESS:
            self.ecosystem_manager = await self._load_contract(
                "EcosystemManager",
                settings.ECOSYSTEM_MANAGER_ADDRESS,
                contracts_dir
            )
            logger.info("EcosystemManager contract loaded")
        
        # OMK Bridge - For cross-chain proposals
        if settings.OMK_BRIDGE_ADDRESS:
            self.omk_bridge = await self._load_contract(
                "OMKBridge",
                settings.OMK_BRIDGE_ADDRESS,
                contracts_dir
            )
            logger.info("OMKBridge contract loaded")
        
        # Advisors Manager - For advisor proposals
        if getattr(settings, 'ADVISORS_MANAGER_ADDRESS', None):
            self.advisors_manager = await self._load_contract(
                "AdvisorsManager",
                settings.ADVISORS_MANAGER_ADDRESS,
                contracts_dir
            )
            logger.info("AdvisorsManager contract loaded")
    
    async def _load_contract(
        self, 
        name: str, 
        address: str, 
        abis_dir: Path
    ) -> Contract:
        """Load a contract instance from ABI"""
        try:
            abi_path = abis_dir / f"{name}.json"
            
            if not abi_path.exists():
                logger.warning(f"ABI file not found for {name} at {abi_path}")
                return None
            
            with open(abi_path, "r") as f:
                abi_data = json.load(f)
                
                # Handle different ABI formats
                if isinstance(abi_data, list):
                    abi = abi_data
                elif isinstance(abi_data, dict):
                    abi = abi_data.get("abi", abi_data)
                else:
                    raise ValueError(f"Invalid ABI format for {name}")
            
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(address),
                abi=abi
            )
            
            return contract
            
        except Exception as e:
            logger.error(f"Failed to load contract {name}", error=str(e))
            return None
    
    # ============ BEE SPAWNER INTERACTIONS ============
    
    async def register_bee(
        self,
        bee_type: int,
        name: str,
        endpoint: str,
        metadata: str
    ) -> Dict[str, Any]:
        """Register a new bee on-chain"""
        if not self.bee_spawner:
            raise ValueError("BeeSpawner contract not loaded")
        
        try:
            # Build transaction
            tx = self.bee_spawner.functions.spawnBee(
                bee_type,
                name,
                Web3.to_checksum_address(endpoint),
                metadata
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            # Sign and send
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info("Bee registered on-chain", 
                       bee_name=name,
                       tx_hash=tx_hash.hex())
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
            }
            
        except Exception as e:
            logger.error("Failed to register bee", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def update_bee_status(self, bee_id: int, status: int) -> Dict[str, Any]:
        """Update bee status on-chain"""
        if not self.bee_spawner:
            raise ValueError("BeeSpawner contract not loaded")
        
        try:
            # Activate or pause bee
            if status == 1:  # Active
                func = self.bee_spawner.functions.activateBee(bee_id)
            elif status == 2:  # Paused
                func = self.bee_spawner.functions.pauseBee(bee_id, "System request")
            else:
                raise ValueError(f"Invalid status: {status}")
            
            tx = func.build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info("Bee status updated", bee_id=bee_id, status=status)
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
            }
            
        except Exception as e:
            logger.error("Failed to update bee status", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def log_bee_task(
        self,
        bee_id: int,
        success: bool,
        response_time: int
    ) -> Dict[str, Any]:
        """Log bee task completion on-chain"""
        if not self.bee_spawner:
            raise ValueError("BeeSpawner contract not loaded")
        
        try:
            tx = self.bee_spawner.functions.logTask(
                bee_id,
                success,
                response_time
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return {"success": True, "tx_hash": tx_hash.hex()}
            
        except Exception as e:
            logger.error("Failed to log bee task", error=str(e))
            return {"success": False, "error": str(e)}
    
    # ============ PROPOSAL SUBMISSIONS ============
    
    async def submit_bridge_proposal(
        self,
        proposal_type: int,
        target_address: str,
        new_value: int,
        description: str
    ) -> Dict[str, Any]:
        """Submit proposal to OMKBridge"""
        if not self.omk_bridge:
            raise ValueError("OMKBridge contract not loaded")
        
        try:
            tx = self.omk_bridge.functions.proposeChange(
                proposal_type,
                Web3.to_checksum_address(target_address) if target_address else "0x" + "0" * 40,
                new_value,
                description
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Parse events to get proposal ID
            proposal_id = None
            for log in receipt.logs:
                try:
                    event = self.omk_bridge.events.ProposalCreated().process_log(log)
                    proposal_id = event.args.proposalId
                    break
                except:
                    continue
            
            logger.info("Bridge proposal submitted", 
                       proposal_id=proposal_id,
                       tx_hash=tx_hash.hex())
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "tx_hash": tx_hash.hex(),
            }
            
        except Exception as e:
            logger.error("Failed to submit bridge proposal", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def submit_treasury_proposal(
        self,
        category: int,
        amount: int,
        recipient: str,
        description: str
    ) -> Dict[str, Any]:
        """Submit proposal to TreasuryVault"""
        if not self.treasury_vault:
            raise ValueError("TreasuryVault contract not loaded")
        
        try:
            tx = self.treasury_vault.functions.createProposal(
                category,
                amount,
                Web3.to_checksum_address(recipient),
                description
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info("Treasury proposal submitted", tx_hash=tx_hash.hex())
            
            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
            }
            
        except Exception as e:
            logger.error("Failed to submit treasury proposal", error=str(e))
            return {"success": False, "error": str(e)}
    
    # ============ READ OPERATIONS ============
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics from SystemDashboard"""
        if not self.system_dashboard:
            return {}
        
        try:
            overview = self.system_dashboard.functions.getSystemOverview().call()
            
            return {
                "total_supply": overview[0],
                "circulating_supply": overview[1],
                "locked_tokens": overview[2],
                "emergency_active": overview[3],
                "active_proposals": overview[4],
                "queen_daily_remaining": overview[5],
            }
            
        except Exception as e:
            logger.error("Failed to get system metrics", error=str(e))
            return {}
    
    async def get_bee_info(self, bee_id: int) -> Dict[str, Any]:
        """Get bee information from BeeSpawner"""
        if not self.bee_spawner:
            return {}
        
        try:
            bee = self.bee_spawner.functions.getBee(bee_id).call()
            
            return {
                "bee_type": bee[0],
                "name": bee[1],
                "endpoint": bee[2],
                "status": bee[3],
                "activated_at": bee[4],
                "last_active_at": bee[5],
                "tasks_completed": bee[6],
                "success_rate": bee[7],
            }
            
        except Exception as e:
            logger.error("Failed to get bee info", error=str(e))
            return {}
    
    async def is_healthy(self) -> bool:
        """Check blockchain connection health"""
        if not self.w3 or not self.initialized:
            return False
        
        try:
            # Try to get latest block
            self.w3.eth.block_number
            return True
        except:
            return False
    
    async def shutdown(self):
        """Cleanup blockchain connections"""
        logger.info("Shutting down blockchain connector")
        self.initialized = False
