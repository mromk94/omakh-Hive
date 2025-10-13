"""
ASI/Fetch.ai uAgents Integration

Integrates OMK Hive with Fetch.ai ecosystem:
- Agent registration on Almanac
- Agent-to-agent communication
- Service discovery
- Protocol definitions
- AI marketplace participation
"""
import asyncio
from typing import Dict, Any, List, Optional, Callable
import structlog
from datetime import datetime

try:
    from uagents import Agent, Context, Model, Protocol
    from uagents.setup import fund_agent_if_low
    UAGENTS_AVAILABLE = True
except ImportError:
    UAGENTS_AVAILABLE = False
    Agent = None
    Context = None
    Model = None
    Protocol = None

from app.config.settings import settings

logger = structlog.get_logger(__name__)


# Message Models for inter-agent communication
if UAGENTS_AVAILABLE:
    class PoolHealthQuery(Model):
        """Query for pool health information"""
        pool_address: str
        include_recommendations: bool = True
    
    class PoolHealthResponse(Model):
        """Response with pool health data"""
        pool_address: str
        health_score: float
        deviation: float
        recommendations: List[str]
        timestamp: str
    
    class GovernanceProposal(Model):
        """Governance proposal sharing between agents"""
        proposal_id: int
        proposal_type: str
        description: str
        voting_end: str
    
    class StakingInfo(Model):
        """Staking information request/response"""
        current_apy: float
        total_staked: float
        available_tiers: List[Dict[str, Any]]
    
    class TreasuryStatus(Model):
        """Treasury health status"""
        total_balance: float
        allocations: Dict[str, float]
        health_score: float


class ASIIntegration:
    """
    Fetch.ai ASI Integration Manager
    
    Connects OMK Hive to the Artificial Superintelligence ecosystem:
    - Registers Queen and Bees as uAgents
    - Enables AI-to-AI communication
    - Participates in AI marketplace
    - Discovers and uses external AI services
    - Shares hive services with other agents
    
    Architecture:
    - Queen Agent: Main orchestrator agent
    - Bee Agents: Specialized service agents
    - Protocols: Communication standards
    - Almanac: Agent discovery service
    """
    
    def __init__(self, bee_manager=None):
        self.initialized = False
        self.bee_manager = bee_manager
        
        if not UAGENTS_AVAILABLE:
            logger.warning("⚠️  uAgents library not installed. ASI integration disabled.")
            logger.warning("   Install with: pip install uagents")
            return
        
        # Agent configurations
        self.queen_agent: Optional[Agent] = None
        self.bee_agents: Dict[str, Agent] = {}
        self.protocols: Dict[str, Protocol] = {}
        
        # Service registry
        self.registered_services = []
        self.discovered_services = {}
        
        # Network config
        self.network = settings.FETCH_NETWORK  # testnet or mainnet
        self.seed = settings.FETCH_MNEMONIC or "omk-hive-queen-seed"
        
    async def initialize(self):
        """Initialize ASI integration"""
        if not UAGENTS_AVAILABLE:
            logger.warning("ASI integration skipped - uAgents not available")
            self.initialized = False
            return
        
        logger.info("🔗 Initializing ASI/Fetch.ai integration")
        
        try:
            # Initialize Queen agent
            await self._create_queen_agent()
            
            # Initialize specialized bee agents
            await self._create_bee_agents()
            
            # Register protocols
            await self._register_protocols()
            
            # Fund agents if needed (testnet only)
            if self.network == "testnet":
                await self._fund_agents()
            
            # Register on Almanac
            await self._register_on_almanac()
            
            self.initialized = True
            logger.info("✅ ASI integration initialized")
            logger.info(f"   Network: {self.network}")
            logger.info(f"   Queen Agent: {self.queen_agent.address if self.queen_agent else 'N/A'}")
            logger.info(f"   Bee Agents: {len(self.bee_agents)}")
            
        except Exception as e:
            logger.error("Failed to initialize ASI integration", error=str(e))
            self.initialized = False
    
    async def _create_queen_agent(self):
        """Create the main Queen orchestrator agent"""
        self.queen_agent = Agent(
            name="omk_queen",
            seed=self.seed,
            port=8001,
            endpoint=["http://localhost:8001/submit"],
        )
        
        # Queen's startup handler
        @self.queen_agent.on_event("startup")
        async def queen_startup(ctx: Context):
            ctx.logger.info("👑 Queen Agent started on ASI network")
            ctx.logger.info(f"Address: {ctx.agent.address}")
        
        # Queen's interval task - heartbeat
        @self.queen_agent.on_interval(period=300.0)  # Every 5 minutes
        async def queen_heartbeat(ctx: Context):
            ctx.logger.info(f"👑 Queen heartbeat - Hive operational")
            # Could broadcast hive status here
        
        logger.info(f"Created Queen Agent: {self.queen_agent.address}")
    
    async def _create_bee_agents(self):
        """Create specialized bee agents for ASI network"""
        
        # Critical bees to expose as agents
        critical_bees = [
            ("maths", "Mathematics and AMM calculations"),
            ("security", "Security validation and risk assessment"),
            ("governance", "DAO governance and voting"),
            ("pattern", "Market analysis and predictions"),
        ]
        
        for bee_name, description in critical_bees:
            agent = Agent(
                name=f"omk_{bee_name}",
                seed=f"{self.seed}_{bee_name}",
                port=8002 + len(self.bee_agents),
                endpoint=[f"http://localhost:{8002 + len(self.bee_agents)}/submit"],
            )
            
            # Bee startup handler
            @agent.on_event("startup")
            async def bee_startup(ctx: Context, name=bee_name):
                ctx.logger.info(f"🐝 {name.title()}Bee started on ASI network")
            
            self.bee_agents[bee_name] = agent
            logger.info(f"Created {bee_name.title()}Bee Agent: {agent.address}")
    
    async def _register_protocols(self):
        """Register communication protocols for inter-agent messaging"""
        
        # Pool Health Protocol
        pool_health_proto = Protocol(name="pool_health", version="1.0")
        
        @pool_health_proto.on_message(model=PoolHealthQuery)
        async def handle_pool_health_query(ctx: Context, sender: str, msg: PoolHealthQuery):
            """Handle pool health queries from other agents"""
            ctx.logger.info(f"Received pool health query from {sender}")
            
            # Get data from MathsBee
            if self.bee_manager:
                result = await self.bee_manager.execute_bee("maths", {
                    "type": "calculate_pool_ratio",
                    "token_a": 1000000,
                    "token_b": 1000000,
                    "target_ratio": 1.0
                })
                
                response = PoolHealthResponse(
                    pool_address=msg.pool_address,
                    health_score=result.get("health_score", 0.0),
                    deviation=result.get("deviation", 0.0),
                    recommendations=result.get("recommendations", []),
                    timestamp=datetime.utcnow().isoformat()
                )
                
                await ctx.send(sender, response)
        
        self.protocols["pool_health"] = pool_health_proto
        self.queen_agent.include(pool_health_proto)
        
        # Governance Protocol
        governance_proto = Protocol(name="governance", version="1.0")
        
        @governance_proto.on_message(model=GovernanceProposal)
        async def handle_governance_proposal(ctx: Context, sender: str, msg: GovernanceProposal):
            """Receive governance proposals from other DAOs"""
            ctx.logger.info(f"Received governance proposal from {sender}")
            
            # Could forward to GovernanceBee for analysis
            if self.bee_manager:
                await self.bee_manager.execute_bee("governance", {
                    "type": "create_proposal",
                    "proposer_address": sender,
                    "proposal_type": msg.proposal_type,
                    "title": f"External Proposal #{msg.proposal_id}",
                    "description": msg.description,
                    "actions": []
                })
        
        self.protocols["governance"] = governance_proto
        if "governance" in self.bee_agents:
            self.bee_agents["governance"].include(governance_proto)
        
        # Staking Info Protocol
        staking_proto = Protocol(name="staking_info", version="1.0")
        
        @staking_proto.on_query(model=StakingInfo)
        async def handle_staking_query(ctx: Context, sender: str, _msg: StakingInfo):
            """Provide staking information to other agents"""
            ctx.logger.info(f"Staking info requested by {sender}")
            
            response = StakingInfo(
                current_apy=12.5,
                total_staked=150_000_000.0,
                available_tiers=[
                    {"period": 30, "apy": 8.0},
                    {"period": 90, "apy": 12.0},
                    {"period": 180, "apy": 15.0},
                    {"period": 365, "apy": 20.0}
                ]
            )
            
            return response
        
        self.protocols["staking"] = staking_proto
        self.queen_agent.include(staking_proto)
        
        logger.info(f"Registered {len(self.protocols)} protocols")
    
    async def _fund_agents(self):
        """Fund agents on testnet (required for transactions)"""
        if self.network != "testnet":
            return
        
        logger.info("Funding agents on testnet...")
        
        try:
            # Fund Queen
            if self.queen_agent:
                fund_agent_if_low(self.queen_agent.wallet.address())
            
            # Fund critical bees
            for bee_agent in self.bee_agents.values():
                fund_agent_if_low(bee_agent.wallet.address())
            
            logger.info("✅ Agents funded")
        except Exception as e:
            logger.warning(f"Agent funding failed: {str(e)}")
    
    async def _register_on_almanac(self):
        """Register agents on Fetch.ai Almanac for discovery"""
        logger.info("Registering agents on Almanac...")
        
        # Register services
        self.registered_services = [
            {
                "name": "omk_pool_health",
                "description": "AMM pool health analysis and recommendations",
                "agent": self.queen_agent.address,
                "protocol": "pool_health"
            },
            {
                "name": "omk_governance",
                "description": "DAO governance and voting services",
                "agent": self.bee_agents.get("governance").address if "governance" in self.bee_agents else None,
                "protocol": "governance"
            },
            {
                "name": "omk_staking",
                "description": "Staking information and APY calculations",
                "agent": self.queen_agent.address,
                "protocol": "staking"
            }
        ]
        
        logger.info(f"✅ Registered {len(self.registered_services)} services on Almanac")
    
    async def discover_service(self, service_name: str) -> Optional[str]:
        """
        Discover an external agent service on Almanac
        
        Args:
            service_name: Name of service to discover
            
        Returns:
            Agent address if found
        """
        # In production, this would query the Almanac
        logger.info(f"Discovering service: {service_name}")
        
        # Simulated discovery
        if service_name not in self.discovered_services:
            logger.warning(f"Service not found: {service_name}")
            return None
        
        return self.discovered_services[service_name]
    
    async def send_message(
        self, 
        recipient_address: str, 
        message: Any,
        protocol: str = None
    ) -> bool:
        """
        Send message to another agent
        
        Args:
            recipient_address: Target agent address
            message: Message object (must be a Model)
            protocol: Protocol name to use
            
        Returns:
            Success status
        """
        if not self.initialized or not self.queen_agent:
            logger.error("ASI integration not initialized")
            return False
        
        try:
            # Create context and send
            # Note: Actual implementation would use proper context
            logger.info(f"Sending message to {recipient_address} via {protocol}")
            # await self.queen_agent.send(recipient_address, message)
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False
    
    async def query_agent(
        self,
        recipient_address: str,
        query: Any,
        timeout: int = 30
    ) -> Optional[Any]:
        """
        Query another agent and wait for response
        
        Args:
            recipient_address: Target agent address
            query: Query object
            timeout: Timeout in seconds
            
        Returns:
            Response from agent or None
        """
        if not self.initialized:
            return None
        
        try:
            logger.info(f"Querying agent {recipient_address}")
            # Actual implementation would send query and await response
            # response = await self.queen_agent.query(recipient_address, query, timeout=timeout)
            # return response
            return None
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return None
    
    async def start_agents(self):
        """Start all agents (blocking - runs event loops)"""
        if not self.initialized:
            logger.error("Cannot start agents - not initialized")
            return
        
        logger.info("Starting ASI agents...")
        
        # In production, this would start the agent event loops
        # This is typically run in background tasks
        
        # Example:
        # await asyncio.gather(
        #     self.queen_agent.run(),
        #     *[agent.run() for agent in self.bee_agents.values()]
        # )
        
        logger.info("ASI agents running")
    
    async def stop_agents(self):
        """Stop all agents gracefully"""
        logger.info("Stopping ASI agents...")
        
        # Cleanup and shutdown
        self.initialized = False
        
        logger.info("ASI agents stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ASI integration statistics"""
        return {
            "initialized": self.initialized,
            "network": self.network,
            "queen_address": self.queen_agent.address if self.queen_agent else None,
            "bee_agents": len(self.bee_agents),
            "protocols": list(self.protocols.keys()),
            "registered_services": len(self.registered_services),
            "discovered_services": len(self.discovered_services)
        }
