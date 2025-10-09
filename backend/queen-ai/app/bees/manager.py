"""
Bee Manager - Manages all bee agents
"""
from typing import Dict, List, Any, Optional
import structlog

from app.bees.base import BaseBee
from app.bees.maths_bee import MathsBee
from app.bees.security_bee import SecurityBee
from app.bees.data_bee import DataBee
from app.bees.treasury_bee import TreasuryBee
from app.bees.blockchain_bee import BlockchainBee
from app.bees.logic_bee import LogicBee
from app.bees.pattern_bee import PatternBee
from app.bees.purchase_bee import PurchaseBee
from app.bees.liquidity_sentinel_bee import LiquiditySentinelBee
from app.bees.stake_bot_bee import StakeBotBee
from app.bees.tokenization_bee import TokenizationBee
from app.bees.monitoring_bee import MonitoringBee
from app.bees.private_sale_bee import PrivateSaleBee
from app.bees.governance_bee import GovernanceBee
from app.bees.visualization_bee import VisualizationBee
from app.bees.bridge_bee import BridgeBee
from app.integrations.elastic_search import ElasticSearchIntegration

logger = structlog.get_logger(__name__)


class BeeManager:
    """
    Manages lifecycle and coordination of all bee agents
    
    Responsibilities:
    - Initialize bees
    - Provide LLM access to bees that need it
    - Route tasks to appropriate bees
    - Monitor bee health
    - Handle bee failures
    """
    
    def __init__(self, llm_abstraction=None, elastic_search=None):
        self.bees: Dict[str, BaseBee] = {}
        self.initialized = False
        self.llm = llm_abstraction  # LLM abstraction for bees that need it
        self.elastic = elastic_search  # Elastic Search for activity logging
    
    async def initialize(self):
        """Initialize all bee agents"""
        logger.info("🐝 Initializing bee agents...")
        
        try:
            # Core Analysis Bees
            self.bees["maths"] = MathsBee(bee_id=1)
            logger.info("✅ MathsBee initialized")
            
            self.bees["security"] = SecurityBee(bee_id=2)
            logger.info("✅ SecurityBee initialized")
            
            self.bees["data"] = DataBee(bee_id=3)
            logger.info("✅ DataBee initialized")
            
            self.bees["treasury"] = TreasuryBee(bee_id=4)
            logger.info("✅ TreasuryBee initialized")
            
            # Execution & Logic Bees
            self.bees["blockchain"] = BlockchainBee(bee_id=5)
            logger.info("✅ BlockchainBee initialized")
            
            self.bees["logic"] = LogicBee(bee_id=6)
            logger.info("✅ LogicBee initialized")
            
            self.bees["pattern"] = PatternBee(bee_id=7)
            logger.info("✅ PatternBee initialized")
            
            # Specialized Operation Bees
            self.bees["purchase"] = PurchaseBee(bee_id=8)
            logger.info("✅ PurchaseBee initialized")
            
            self.bees["liquidity_sentinel"] = LiquiditySentinelBee(bee_id=9)
            logger.info("✅ LiquiditySentinelBee initialized")
            
            self.bees["stake_bot"] = StakeBotBee(bee_id=10)
            logger.info("✅ StakeBotBee initialized")
            
            self.bees["tokenization"] = TokenizationBee(bee_id=11)
            logger.info("✅ TokenizationBee initialized")
            
            # Critical Monitoring Bee (HIGHEST PRIORITY)
            self.bees["monitoring"] = MonitoringBee(bee_id=12)
            logger.info("✅ MonitoringBee initialized")
            
            # Private Sale Bee (Token Sales)
            self.bees["private_sale"] = PrivateSaleBee(bee_id=13)
            logger.info("✅ PrivateSaleBee initialized")
            
            # Governance Bee (DAO Governance) - LLM ENABLED
            self.bees["governance"] = GovernanceBee(bee_id=14)
            logger.info("✅ GovernanceBee initialized")
            
            # Visualization Bee (Dashboards & Charts)
            self.bees["visualization"] = VisualizationBee(bee_id=15)
            logger.info("✅ VisualizationBee initialized")
            
            # Bridge Bee (Cross-Chain Bridge Orchestrator)
            self.bees["bridge"] = BridgeBee(bee_id=16)
            logger.info("✅ BridgeBee initialized")
            
            # Provide LLM access to bees that need intelligent reasoning
            if self.llm:
                llm_enabled_bees = ["logic", "pattern", "governance", "security"]
                for bee_name in llm_enabled_bees:
                    if bee_name in self.bees:
                        self.bees[bee_name].llm_enabled = True
                        self.bees[bee_name].set_llm(self.llm)
                logger.info(f"🧠 LLM enabled for: {', '.join(llm_enabled_bees)}")
            else:
                logger.warning("⚠️  LLM not provided - bees running without AI reasoning")
            
            # Provide Elastic Search access to all bees for activity logging
            if self.elastic:
                # Initialize Elastic indices
                await self.elastic.initialize()
                
                # Enable for all bees
                for bee_name, bee in self.bees.items():
                    bee.elastic = self.elastic
                
                logger.info(f"🔍 Elastic Search enabled for all {len(self.bees)} bees")
            else:
                logger.warning("⚠️  Elastic Search not provided - activity logging disabled")
            
            # Wire bee connections for coordinated operations
            await self._wire_bee_connections()
            logger.info("🔗 Bee connections wired")
            
            self.initialized = True
            logger.info(f"🎉 Hive initialized with {len(self.bees)} specialized bees")
            logger.info(f"   Core: Maths, Security, Data, Treasury")
            logger.info(f"   Logic: Blockchain, Logic, Pattern")
            logger.info(f"   Operations: Purchase, LiquiditySentinel, StakeBot, Tokenization")
            logger.info(f"   Sales: PrivateSale (Tiered Token Sales)")
            logger.info(f"   Governance: Governance (DAO Proposals & Voting)")
            logger.info(f"   Visualization: Visualization (Dashboards & Simulations)")
            logger.info(f"   Bridge: Bridge (Cross-Chain Orchestration & Recovery)")
            logger.info(f"   Critical: Monitoring (Security/Health/Safety)")
            
        except Exception as e:
            logger.error("Failed to initialize bees", error=str(e))
            raise
    
    async def _wire_bee_connections(self):
        """
        Wire connections between bees for coordinated operations
        
        Hierarchy:
        Queen AI
          ↓
        LiquiditySentinelBee (coordinates liquidity & price monitoring)
          ↓
        BlockchainBee (executes on DEX via routers & gets prices from oracles)
          ↓
        DEX Routers (Uniswap, Raydium) + Price Oracles (Chainlink, Pyth)
        """
        try:
            # Connect LiquiditySentinelBee to BlockchainBee
            if "liquidity_sentinel" in self.bees and "blockchain" in self.bees:
                self.bees["liquidity_sentinel"].set_blockchain_bee(self.bees["blockchain"])
                logger.info("✅ LiquiditySentinelBee → BlockchainBee connection established")
            
            # Connect LiquiditySentinelBee to PatternBee (for ML predictions)
            if "liquidity_sentinel" in self.bees and "pattern" in self.bees:
                self.bees["liquidity_sentinel"].set_pattern_bee(self.bees["pattern"])
                logger.info("✅ LiquiditySentinelBee → PatternBee connection established")
            
            # Connect TreasuryBee to BlockchainBee (for balance checks, etc.)
            if "treasury" in self.bees and "blockchain" in self.bees:
                # TreasuryBee can query balances via BlockchainBee
                logger.info("✅ TreasuryBee → BlockchainBee connection available")
            
            # Connect BridgeBee to BlockchainBee (already inherent via imports)
            if "bridge" in self.bees and "blockchain" in self.bees:
                logger.info("✅ BridgeBee → BlockchainBee connection available")
            
            # Connect DataBee to Elastic Search (for data queries & RAG)
            if "data" in self.bees and self.elastic:
                self.bees["data"].set_elastic_client(self.elastic)
                logger.info("✅ DataBee → Elastic Search connection established")
            
            logger.info("🔗 All bee connections wired successfully")
        
        except Exception as e:
            logger.error(f"Failed to wire bee connections: {str(e)}")
            # Don't raise - connections are optional enhancements
    
    async def execute_bee(self, bee_name: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task with specific bee
        
        Args:
            bee_name: Name of bee to use
            task_data: Task parameters
            
        Returns:
            Task result
        """
        if bee_name not in self.bees:
            return {
                "success": False,
                "error": f"Bee '{bee_name}' not found. Available: {list(self.bees.keys())}"
            }
        
        bee = self.bees[bee_name]
        return await bee.process_task(task_data)
    
    async def execute_multi(self, bee_names: List[str], task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute task with multiple bees
        
        Args:
            bee_names: List of bee names
            task_data: Task parameters
            
        Returns:
            List of results from each bee
        """
        results = []
        for bee_name in bee_names:
            result = await self.execute_bee(bee_name, task_data)
            results.append(result)
        return results
    
    async def check_all_health(self) -> Dict[str, Any]:
        """Check health of all bees"""
        health_reports = {}
        all_healthy = True
        any_critical = False
        
        for bee_name, bee in self.bees.items():
            health = await bee.health_check()
            health_reports[bee_name] = health
            
            if health["status"] == "error":
                any_critical = True
                all_healthy = False
            elif health["status"] != "active":
                all_healthy = False
        
        return {
            "all_healthy": all_healthy,
            "any_critical": any_critical,
            "bees": health_reports,
            "total_bees": len(self.bees),
        }
    
    async def get_bee_stats(self) -> Dict[str, Any]:
        """Get statistics for all bees"""
        stats = {}
        for bee_name, bee in self.bees.items():
            stats[bee_name] = bee.get_stats()
        return stats
    
    async def shutdown(self):
        """Shutdown all bees"""
        logger.info("Shutting down bee manager")
        self.initialized = False
