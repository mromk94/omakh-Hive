"""
Queen AI Orchestrator - Central coordination system

Integrates with all 16 PRIME2 smart contracts:
- Manages bee agents via BeeSpawner
- Submits proposals to governance contracts
- Monitors system via SystemDashboard
- Coordinates cross-chain via OMKBridge
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog

from app.config.settings import settings
from app.utils.blockchain import BlockchainConnector
from app.core.state_manager import StateManager
from app.core.decision_engine import DecisionEngine
from app.llm.abstraction import LLMAbstraction
from app.bees.manager import BeeManager
from app.core.message_bus import MessageBus
from app.core.hive_board import HiveInformationBoard
from app.uagents.integration import ASIIntegration

logger = structlog.get_logger(__name__)


class QueenOrchestrator:
    """
    Central AI orchestration system
    
    Responsibilities:
    - Coordinate all bee agents
    - Make autonomous decisions
    - Generate and submit blockchain proposals
    - Monitor system health
    - Route tasks to appropriate bees
    - Manage cross-chain operations
    """
    
    def __init__(self):
        self.blockchain = BlockchainConnector()
        self.state_manager = StateManager()
        self.llm = LLMAbstraction()  # Queen has LLM for intelligent orchestration
        self.message_bus = MessageBus()
        self.hive_board = HiveInformationBoard()
        self.bee_manager = BeeManager(llm_abstraction=self.llm)  # Provide LLM to bees
        self.decision_engine = DecisionEngine(self.llm)
        self.asi_integration = None  # ASI/Fetch.ai integration (optional)
        
        # State
        self.initialized = False
        self.running = False
        self.decision_count = 0
        self.proposal_count = 0
        
        # Bee registry (will be synced with BeeSpawner contract)
        self.bees: Dict[int, Dict[str, Any]] = {}
        
        # System metrics cache
        self.system_metrics: Dict[str, Any] = {}
        self.last_metrics_update: Optional[datetime] = None
        
        # Background tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.decision_task: Optional[asyncio.Task] = None
        self.staking_task: Optional[asyncio.Task] = None
        self.data_pipeline_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize all Queen AI components"""
        logger.info("🚀 Initializing Queen AI Orchestrator")
        
        try:
            # Initialize blockchain connector
            await self.blockchain.initialize()
            logger.info("✅ Blockchain connector initialized")
            
            # Initialize LLM providers
            await self.llm.initialize()
            logger.info("✅ LLM abstraction initialized")
            
            # Initialize message bus (CRITICAL for inter-bee communication)
            await self.message_bus.initialize()
            logger.info("✅ Message bus initialized - unrestricted communication enabled")
            
            # Initialize hive information board (shared knowledge system)
            await self.hive_board.initialize()
            logger.info("✅ Hive Information Board initialized - shared knowledge enabled")
            
            # Initialize bee manager
            await self.bee_manager.initialize()
            logger.info("✅ Bee manager initialized")
            
            # Register all bees with message bus
            for bee_name in self.bee_manager.bees.keys():
                self.message_bus.register_bee(bee_name)
            self.message_bus.register_bee("queen")
            logger.info("✅ All bees registered with message bus")
            
            # Load registered bees from BeeSpawner
            await self._sync_bees_from_chain()
            logger.info(f"✅ Loaded {len(self.bees)} bees from chain")
            
            # Load state manager
            await self.state_manager.load_state()
            logger.info("✅ State manager loaded")
            
            # Load initial system metrics
            await self._update_system_metrics()
            logger.info("✅ System metrics loaded")
            
            # Initialize ASI integration (optional - only if enabled)
            try:
                self.asi_integration = ASIIntegration(bee_manager=self.bee_manager)
                await self.asi_integration.initialize()
                if self.asi_integration.initialized:
                    logger.info("✅ ASI/Fetch.ai integration initialized")
                else:
                    logger.info("⚠️  ASI integration available but not activated")
            except Exception as e:
                logger.warning(f"ASI integration skipped: {str(e)}")
                self.asi_integration = None
            
            # Initialize Market Data Agent
            from app.agents.market_data_agent import MarketDataAgent
            self.market_data_agent = MarketDataAgent(self)
            logger.info("✅ Market Data Agent initialized")
            
            self.initialized = True
            self.running = True
            
            # Start background tasks
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.decision_task = asyncio.create_task(self._decision_loop())
            self.staking_task = asyncio.create_task(self._staking_rewards_loop())
            self.data_pipeline_task = asyncio.create_task(self._data_pipeline_loop())
            
            logger.info("✅ Background tasks started:")
            logger.info("   📊 Monitoring loop (system health)")
            logger.info("   🧠 Decision loop (autonomous operations)")
            logger.info("   💎 Staking rewards loop (daily distributions)")
            logger.info("   🔄 Data pipeline loop (every 15 minutes)")
            
            logger.info("🎉 Queen AI Orchestrator fully initialized and operational")
            
        except Exception as e:
            logger.error("❌ Failed to initialize Queen AI", error=str(e), exc_info=True)
            raise
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down Queen AI Orchestrator")
        
        self.running = False
        
        # Cancel background tasks
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.decision_task:
            self.decision_task.cancel()
        if self.staking_task:
            self.staking_task.cancel()
        if self.data_pipeline_task:
            self.data_pipeline_task.cancel()
        
        # Shutdown components
        await self.hive_board.shutdown()
        await self.message_bus.shutdown()
        await self.llm.shutdown()
        await self.bee_manager.shutdown()
        await self.blockchain.shutdown()
        
        logger.info("✅ Queen AI shutdown complete")
    
    # ============ BEE MANAGEMENT ============
    
    async def _sync_bees_from_chain(self):
        """Sync bee registry from BeeSpawner contract"""
        try:
            if not self.blockchain.bee_spawner:
                logger.warning("BeeSpawner contract not loaded, skipping bee sync")
                return
            
            # Get bee count from contract
            bee_count = self.blockchain.bee_spawner.functions.beeCount().call()
            
            logger.info(f"Syncing {bee_count} bees from chain")
            
            # Load each bee's info
            for bee_id in range(bee_count):
                bee_info = await self.blockchain.get_bee_info(bee_id)
                if bee_info:
                    self.bees[bee_id] = bee_info
                    logger.debug(f"Loaded bee", bee_id=bee_id, name=bee_info.get('name'))
            
        except Exception as e:
            logger.error("Failed to sync bees from chain", error=str(e))
    
    async def register_bee(
        self,
        bee_type: int,
        name: str,
        endpoint: str,
        metadata: str = ""
    ) -> Dict[str, Any]:
        """
        Register a new bee agent on-chain
        
        Args:
            bee_type: Type of bee (0=MATHS, 1=SECURITY, 2=BLOCKCHAIN, etc.)
            name: Human-readable name
            endpoint: API endpoint or address
            metadata: IPFS hash or JSON metadata
        """
        logger.info("Registering new bee", name=name, type=bee_type)
        
        result = await self.blockchain.register_bee(
            bee_type=bee_type,
            name=name,
            endpoint=endpoint,
            metadata=metadata
        )
        
        if result["success"]:
            # Resync bees
            await self._sync_bees_from_chain()
            logger.info("✅ Bee registered successfully", name=name)
        else:
            logger.error("❌ Failed to register bee", name=name, error=result.get("error"))
        
        return result
    
    async def get_active_bees(self) -> List[Dict[str, Any]]:
        """Get list of active bees"""
        return [
            {**bee, "id": bee_id}
            for bee_id, bee in self.bees.items()
            if bee.get("status") == 1  # Active status
        ]
    
    # ============ PROPOSAL GENERATION ============
    
    async def propose_bridge_change(
        self,
        proposal_type: int,
        target_address: str = "",
        new_value: int = 0,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Submit proposal to OMKBridge contract
        
        Proposal Types:
        0 = UPDATE_RATE_LIMIT
        1 = ADD_RELAYER
        2 = REMOVE_RELAYER
        3 = ADD_VALIDATOR
        4 = REMOVE_VALIDATOR
        5 = UPDATE_REQUIRED_VALIDATIONS
        6 = PAUSE_BRIDGE
        7 = UNPAUSE_BRIDGE
        """
        logger.info("Proposing bridge change", 
                   type=proposal_type, 
                   description=description)
        
        result = await self.blockchain.submit_bridge_proposal(
            proposal_type=proposal_type,
            target_address=target_address,
            new_value=new_value,
            description=description
        )
        
        if result["success"]:
            self.proposal_count += 1
            logger.info("✅ Bridge proposal submitted", 
                       proposal_id=result.get("proposal_id"))
        else:
            logger.error("❌ Bridge proposal failed", error=result.get("error"))
        
        return result
    
    async def propose_treasury_spending(
        self,
        category: int,
        amount: int,
        recipient: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Submit treasury spending proposal
        
        Categories:
        0 = DEVELOPMENT
        1 = MARKETING  
        2 = OPERATIONS
        3 = INVESTMENTS
        4 = EMERGENCY
        5 = GOVERNANCE
        """
        logger.info("Proposing treasury spending",
                   category=category,
                   amount=amount,
                   description=description)
        
        result = await self.blockchain.submit_treasury_proposal(
            category=category,
            amount=amount,
            recipient=recipient,
            description=description
        )
        
        if result["success"]:
            self.proposal_count += 1
            logger.info("✅ Treasury proposal submitted")
        else:
            logger.error("❌ Treasury proposal failed", error=result.get("error"))
        
        return result
    
    # ============ MONITORING ============
    
    async def _update_system_metrics(self):
        """Update system metrics from SystemDashboard"""
        try:
            metrics = await self.blockchain.get_system_metrics()
            if metrics:
                self.system_metrics = metrics
                self.last_metrics_update = datetime.utcnow()
                logger.debug("System metrics updated", metrics=metrics)
        except Exception as e:
            logger.error("Failed to update system metrics", error=str(e))
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        blockchain_healthy = await self.blockchain.is_healthy()
        
        active_bees = len([b for b in self.bees.values() if b.get("status") == 1])
        total_bees = len(self.bees)
        
        status = "healthy"
        if not blockchain_healthy:
            status = "critical"
        elif active_bees < total_bees * 0.5:
            status = "degraded"
        
        return {
            "status": status,
            "blockchain_connected": blockchain_healthy,
            "active_bees": active_bees,
            "total_bees": total_bees,
            "decision_count": self.decision_count,
            "proposal_count": self.proposal_count,
            "system_metrics": self.system_metrics,
            "last_metrics_update": self.last_metrics_update.isoformat() if self.last_metrics_update else None,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    # ============ BACKGROUND LOOPS ============
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        logger.info("📊 Starting monitoring loop")
        
        while self.running:
            try:
                # Update system metrics
                await self._update_system_metrics()
                
                # Check system health
                health = await self.get_system_health()
                
                if health["status"] != "healthy":
                    logger.warning("System health degraded", health=health)
                
            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))
            
            # Wait before next check
            await asyncio.sleep(settings.QUEEN_MONITORING_INTERVAL)
    
    async def _decision_loop(self):
        """Background autonomous decision loop"""
        logger.info("🧠 Starting decision loop")
        
        while self.running:
            try:
                # Check if any autonomous decisions need to be made
                pending = await self.decision_engine.get_pending()
                
                for decision in pending:
                    decision_type = decision.get("type")
                    
                    if decision_type == "liquidity_management":
                        await self._execute_liquidity_decision(decision)
                    elif decision_type == "airdrop_campaign":
                        await self._execute_airdrop_decision(decision)
                    elif decision_type == "bridge_operation":
                        await self._execute_bridge_decision(decision)
                
                self.decision_count += 1
                logger.debug("Decision cycle complete", count=self.decision_count)
                
            except Exception as e:
                logger.error("Error in decision loop", error=str(e))
            
            # Wait before next decision cycle
            await asyncio.sleep(settings.QUEEN_DECISION_INTERVAL)
    
    async def _staking_rewards_loop(self):
        """Background loop for daily staking rewards distribution"""
        logger.info("💎 Starting staking rewards loop")
        
        while self.running:
            try:
                # Check if it's time for daily distribution (00:00 UTC)
                now = datetime.utcnow()
                if now.hour == 0 and now.minute < 5:  # Within first 5 minutes of day
                    logger.info("⏰ Time for daily staking rewards distribution")
                    
                    # Get staking data (in production, from StakingManager contract)
                    staking_data = await self._get_staking_data()
                    
                    # Calculate rewards
                    decision = await self.decision_engine.calculate_staking_rewards(staking_data)
                    
                    if decision:
                        await self._execute_staking_rewards(decision)
                
            except Exception as e:
                logger.error("Error in staking rewards loop", error=str(e))
            
            # Check every 5 minutes
            await asyncio.sleep(300)
    
    async def _data_pipeline_loop(self):
        """Background loop for automated data collection and sync"""
        logger.info("📊 Starting data pipeline loop")
        
        # Wait 30 seconds for system to fully initialize
        await asyncio.sleep(30)
        
        while self.running:
            try:
                logger.info("🔄 Running automated data pipeline")
                
                # Execute full data pipeline via DataPipelineBee
                result = await self.bee_manager.execute_bee("data_pipeline", {
                    "type": "run_pipeline"
                })
                
                if result.get("success"):
                    logger.info(
                        "✅ Data pipeline completed successfully",
                        duration=result.get("duration_seconds"),
                        records=result.get("total_records"),
                        files=result.get("csv_files_uploaded")
                    )
                else:
                    logger.error(
                        "❌ Data pipeline failed",
                        error=result.get("error")
                    )
                
            except Exception as e:
                logger.error("Error in data pipeline loop", error=str(e), exc_info=True)
            
            # Wait 15 minutes before next run (900 seconds)
            logger.info("⏰ Data pipeline sleeping for 15 minutes")
            await asyncio.sleep(900)
    
    async def _execute_liquidity_decision(self, decision: Dict[str, Any]):
        """Execute a liquidity management decision"""
        try:
            action = decision.get("action")
            amount = decision.get("amount")
            pool = decision.get("pool")
            
            logger.info("Executing liquidity decision",
                       action=action,
                       amount=amount,
                       pool=pool)
            
            # In production, would interact with DEX contracts
            # For now, log the decision
            await self.state_manager.record_operation("liquidity_management", amount)
            
        except Exception as e:
            logger.error("Failed to execute liquidity decision", error=str(e))
    
    async def _execute_airdrop_decision(self, decision: Dict[str, Any]):
        """Execute an airdrop campaign"""
        try:
            campaign_type = decision.get("campaign_type")
            total_amount = decision.get("total_amount")
            recipients = decision.get("recipients", [])
            
            logger.info("Executing airdrop campaign",
                       type=campaign_type,
                       amount=total_amount,
                       recipients=len(recipients))
            
            # In production, would batch transfer to recipients
            await self.state_manager.record_operation("airdrop", total_amount)
            
        except Exception as e:
            logger.error("Failed to execute airdrop", error=str(e))
    
    async def _execute_bridge_decision(self, decision: Dict[str, Any]):
        """Execute a bridge operation"""
        try:
            operation = decision.get("operation")
            amount = decision.get("amount")
            
            logger.info("Executing bridge operation",
                       operation=operation,
                       amount=amount)
            
            # In production, would interact with OMKBridge contract
            await self.state_manager.record_operation("bridge", amount)
            
        except Exception as e:
            logger.error("Failed to execute bridge operation", error=str(e))
    
    async def _execute_staking_rewards(self, decision: Dict[str, Any]):
        """Execute staking rewards distribution"""
        try:
            total_amount = decision.get("total_amount")
            distributions = decision.get("distributions", [])
            
            logger.info("Distributing staking rewards",
                       total=total_amount,
                       stakers=len(distributions))
            
            # In production, would:
            # 1. Release tokens from ecosystem vesting
            # 2. Transfer to StakingManager contract
            # 3. Trigger distribution to stakers
            
            await self.state_manager.record_operation("staking_rewards", total_amount)
            
        except Exception as e:
            logger.error("Failed to distribute staking rewards", error=str(e))
    
    async def _get_staking_data(self) -> Dict[str, Any]:
        """Get current staking data from blockchain"""
        # In production, would query StakingManager contract
        # For now, return mock data
        return {
            "total_staked": 10_000_000 * 10**18,
            "treasury_health": 1.2,
            "stakers": [],
        }
    
    # ============ TASK ROUTING ============
    
    async def process_request(self, request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming request and route to appropriate handler
        
        Args:
            request_type: Type of request
            data: Request data
            
        Returns:
            Response dictionary
        """
        logger.info("Processing request", type=request_type)
        
        try:
            # Route based on request type
            if request_type == "check_system_health":
                return await self.get_system_health()
            
            elif request_type == "list_bees":
                return {"bees": await self.get_active_bees()}
            
            elif request_type == "register_bee":
                return await self.register_bee(**data)
            
            elif request_type == "propose_bridge_change":
                return await self.propose_bridge_change(**data)
            
            elif request_type == "propose_treasury_spending":
                return await self.propose_treasury_spending(**data)
            
            else:
                return {
                    "error": f"Unknown request type: {request_type}",
                    "supported_types": [
                        "check_system_health",
                        "list_bees",
                        "register_bee",
                        "propose_bridge_change",
                        "propose_treasury_spending",
                    ]
                }
                
        except Exception as e:
            logger.error("Error processing request", error=str(e), exc_info=True)
            return {"error": str(e)}
