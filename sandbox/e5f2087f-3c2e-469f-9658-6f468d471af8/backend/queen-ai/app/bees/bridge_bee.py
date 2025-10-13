"""
BridgeBee - Cross-Chain Bridge Orchestrator

Responsibilities:
- Monitor bridge transactions
- Detect and recover stuck transactions
- Alert Queen AI of issues
- Manage bridge health
- Coordinate with blockchain clients
- Handle emergency interventions
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import structlog

from app.bees.base import BaseBee
from app.blockchain.bridge import cross_chain_bridge, BridgeStatus, BridgeDirection

logger = structlog.get_logger(__name__)


class BridgeBee(BaseBee):
    """
    Cross-chain bridge orchestrator and monitor
    
    Features:
    - Continuous bridge monitoring
    - Stuck transaction detection
    - Automatic recovery attempts
    - Queen AI alerts for critical issues
    - Bridge health monitoring
    - Liquidity management
    """
    
    def __init__(self, bee_id: int = 16):
        super().__init__("BridgeBee", bee_id)
        self.bridge = cross_chain_bridge
        
        # Monitoring configuration
        self.monitor_interval = 30  # seconds
        self.recovery_interval = 60  # seconds
        self.health_check_interval = 120  # seconds
        
        # Alert thresholds
        self.max_stuck_transactions = 5
        self.max_pending_time = 60  # minutes
        self.critical_liquidity_ratio = 0.2  # 20%
        
        # State
        self.monitoring = False
        self.last_health_check = None
        self.alert_count = 0
        
    async def initialize(self) -> bool:
        """Initialize BridgeBee"""
        try:
            await self.bridge.initialize()
            
            logger.info(
                "BridgeBee initialized",
                validators=len(self.bridge.validators),
                eth_liquidity=float(self.bridge.eth_liquidity),
                sol_liquidity=float(self.bridge.sol_liquidity)
            )
            
            self.initialized = True
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize BridgeBee: {str(e)}")
            return False
    
    async def start_monitoring(self):
        """
        Start continuous bridge monitoring
        
        Runs multiple monitoring loops in parallel:
        - Transaction monitoring
        - Recovery attempts
        - Health checks
        """
        if self.monitoring:
            logger.warning("BridgeBee monitoring already running")
            return
        
        self.monitoring = True
        
        logger.info("BridgeBee monitoring started")
        
        # Start all monitoring loops
        await asyncio.gather(
            self._transaction_monitor_loop(),
            self._recovery_loop(),
            self._health_check_loop(),
            return_exceptions=True
        )
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        logger.info("BridgeBee monitoring stopped")
    
    async def _transaction_monitor_loop(self):
        """Monitor bridge transactions continuously"""
        logger.info("Starting transaction monitor loop")
        
        while self.monitoring:
            try:
                # Detect stuck transactions
                stuck_txs = await self.bridge.monitor_stuck_transactions()
                
                if stuck_txs:
                    logger.warning(
                        f"Detected {len(stuck_txs)} stuck transactions",
                        count=len(stuck_txs)
                    )
                    
                    # Alert Queen AI if threshold exceeded
                    if len(stuck_txs) > self.max_stuck_transactions:
                        await self._alert_queen_critical_bridge_issue(
                            f"{len(stuck_txs)} stuck transactions detected"
                        )
                
                # Check for old pending transactions
                await self._check_old_pending_transactions()
                
            except Exception as e:
                logger.error(f"Transaction monitor error: {str(e)}")
            
            await asyncio.sleep(self.monitor_interval)
    
    async def _recovery_loop(self):
        """Automatic recovery loop"""
        logger.info("Starting recovery loop")
        
        while self.monitoring:
            try:
                # Attempt to recover stuck transactions
                recovered = await self.bridge.auto_recover_stuck_transactions()
                
                if recovered:
                    logger.info(
                        f"Successfully recovered {len(recovered)} transactions",
                        recovered=recovered
                    )
                    
                    # Report to Queen AI
                    await self._report_to_queen({
                        "event": "transactions_recovered",
                        "count": len(recovered),
                        "transaction_ids": recovered
                    })
            
            except Exception as e:
                logger.error(f"Recovery loop error: {str(e)}")
            
            await asyncio.sleep(self.recovery_interval)
    
    async def _health_check_loop(self):
        """Bridge health monitoring loop"""
        logger.info("Starting health check loop")
        
        while self.monitoring:
            try:
                health = await self.bridge.check_health()
                self.last_health_check = datetime.utcnow()
                
                # Check for critical issues
                if not health["is_healthy"]:
                    await self._alert_queen_critical_bridge_issue(
                        "Bridge is unhealthy",
                        health_data=health
                    )
                
                # Check liquidity imbalance
                if "liquidity_ratio" in health:
                    if health["liquidity_ratio"] < self.critical_liquidity_ratio:
                        await self._alert_queen_critical_bridge_issue(
                            f"Critical liquidity imbalance: {health['liquidity_ratio']:.1%}",
                            health_data=health
                        )
                        
                        # Trigger rebalancing
                        await self.bridge.rebalance_liquidity()
            
            except Exception as e:
                logger.error(f"Health check error: {str(e)}")
            
            await asyncio.sleep(self.health_check_interval)
    
    async def _check_old_pending_transactions(self):
        """Check for transactions pending too long"""
        for tx_id, tx in self.bridge.pending_transactions.items():
            age_minutes = (datetime.utcnow() - tx.created_at).total_seconds() / 60
            
            if age_minutes > self.max_pending_time:
                logger.warning(
                    f"Transaction pending too long: {tx_id}",
                    age_minutes=age_minutes,
                    status=tx.status.value
                )
    
    async def _alert_queen_critical_bridge_issue(
        self,
        message: str,
        health_data: Optional[Dict] = None
    ):
        """
        Alert Queen AI of critical bridge issue
        
        Queen can then decide to:
        - Override transactions
        - Pause bridge
        - Request admin intervention
        """
        self.alert_count += 1
        
        logger.critical(
            "CRITICAL BRIDGE ALERT",
            message=message,
            alert_count=self.alert_count,
            health_data=health_data
        )
        
        # Build alert data
        alert = {
            "bee": self.name,
            "severity": "CRITICAL",
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "bridge_stats": await self.bridge.get_bridge_stats(),
            "health_data": health_data,
            "recovery_dashboard": await self.bridge.get_recovery_dashboard()
        }
        
        # Send to Queen AI via message bus
        await self.send_message(
            to="Queen",
            subject="CRITICAL_BRIDGE_ALERT",
            body=alert,
            priority=10  # Highest priority
        )
        
        # Post to hive board
        await self.post_to_hive(
            category="alerts",
            title=f"🚨 Critical Bridge Alert: {message}",
            content=alert,
            priority="critical"
        )
    
    async def _report_to_queen(self, report: Dict[str, Any]):
        """Send status report to Queen AI"""
        await self.send_message(
            to="Queen",
            subject="BRIDGE_STATUS_REPORT",
            body=report
        )
    
    # ========== BEE INTERFACE METHODS ==========
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process messages from Queen or other bees
        
        Supported commands:
        - initiate_bridge: Start bridge transaction
        - check_transaction: Check transaction status
        - force_recovery: Force recovery of stuck transaction
        - get_stats: Get bridge statistics
        - pause_bridge: Pause bridge operations
        - resume_bridge: Resume bridge operations
        """
        action = message.get("action")
        
        if action == "initiate_bridge":
            return await self._handle_initiate_bridge(message)
        
        elif action == "check_transaction":
            return await self._handle_check_transaction(message)
        
        elif action == "force_recovery":
            return await self._handle_force_recovery(message)
        
        elif action == "get_stats":
            return await self._handle_get_stats()
        
        elif action == "pause_bridge":
            return await self._handle_pause_bridge()
        
        elif action == "resume_bridge":
            return await self._handle_resume_bridge()
        
        elif action == "queen_override":
            return await self._handle_queen_override(message)
        
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
    
    async def _handle_initiate_bridge(self, message: Dict) -> Dict:
        """Handle bridge initiation request"""
        try:
            direction = message.get("direction")  # "eth_to_sol" or "sol_to_eth"
            amount = message.get("amount")
            from_address = message.get("from_address")
            to_address = message.get("to_address")
            
            if direction == "eth_to_sol":
                tx_id = await self.bridge.bridge_eth_to_sol(
                    amount=amount,
                    from_eth_address=from_address,
                    to_sol_address=to_address
                )
            else:
                tx_id = await self.bridge.bridge_sol_to_eth(
                    amount=amount,
                    from_sol_address=from_address,
                    to_eth_address=to_address
                )
            
            return {
                "success": True,
                "transaction_id": tx_id,
                "message": "Bridge transaction initiated"
            }
        
        except Exception as e:
            logger.error(f"Bridge initiation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_check_transaction(self, message: Dict) -> Dict:
        """Check transaction status"""
        tx_id = message.get("transaction_id")
        
        tx = await self.bridge.get_transaction(tx_id)
        
        if not tx:
            return {
                "success": False,
                "error": "Transaction not found"
            }
        
        return {
            "success": True,
            "transaction": {
                "id": tx.id,
                "status": tx.status.value,
                "direction": tx.direction.value,
                "amount": float(tx.amount),
                "from_address": tx.from_address,
                "to_address": tx.to_address,
                "source_tx_hash": tx.source_tx_hash,
                "dest_tx_hash": tx.dest_tx_hash,
                "created_at": tx.created_at.isoformat(),
                "time_remaining": tx.time_remaining(),
                "retry_count": tx.retry_count,
                "error": tx.error
            }
        }
    
    async def _handle_force_recovery(self, message: Dict) -> Dict:
        """Force recovery of stuck transaction"""
        tx_id = message.get("transaction_id")
        
        tx = await self.bridge.get_transaction(tx_id)
        if not tx:
            return {"success": False, "error": "Transaction not found"}
        
        # Attempt recovery
        if tx.direction == BridgeDirection.ETH_TO_SOL:
            success = await self.bridge._recover_eth_to_sol(tx)
        else:
            success = await self.bridge._recover_sol_to_eth(tx)
        
        return {
            "success": success,
            "transaction_id": tx_id,
            "new_status": tx.status.value
        }
    
    async def _handle_get_stats(self) -> Dict:
        """Get bridge statistics"""
        stats = await self.bridge.get_bridge_stats()
        recovery = await self.bridge.get_recovery_dashboard()
        health = await self.bridge.check_health()
        
        return {
            "success": True,
            "stats": stats,
            "recovery": recovery,
            "health": health,
            "monitoring": self.monitoring,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None
        }
    
    async def _handle_pause_bridge(self) -> Dict:
        """Pause bridge operations"""
        self.bridge.is_healthy = False
        
        logger.warning("Bridge operations paused")
        
        await self._report_to_queen({
            "event": "bridge_paused",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "message": "Bridge paused"
        }
    
    async def _handle_resume_bridge(self) -> Dict:
        """Resume bridge operations"""
        # Re-check health before resuming
        health = await self.bridge.check_health()
        
        if health["ethereum_connected"] and health["solana_connected"]:
            self.bridge.is_healthy = True
            
            logger.info("Bridge operations resumed")
            
            await self._report_to_queen({
                "event": "bridge_resumed",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "success": True,
                "message": "Bridge resumed"
            }
        else:
            return {
                "success": False,
                "error": "Bridge health check failed",
                "health": health
            }
    
    async def _handle_queen_override(self, message: Dict) -> Dict:
        """
        Handle Queen AI override command
        
        Queen can override stuck transactions with:
        - retry: Force retry recovery
        - cancel: Cancel and refund
        - force_complete: Manually mark as complete
        - manual_review: Flag for admin review
        """
        tx_id = message.get("transaction_id")
        action = message.get("override_action")
        reason = message.get("reason", "Queen AI override")
        
        success = await self.bridge.queen_override_transaction(
            tx_id=tx_id,
            action=action,
            reason=reason
        )
        
        return {
            "success": success,
            "transaction_id": tx_id,
            "action": action,
            "message": f"Queen override {action} {'successful' if success else 'failed'}"
        }
    
    # ========== UTILITY METHODS ==========
    
    async def get_bridge_health_report(self) -> Dict[str, Any]:
        """
        Get comprehensive bridge health report
        
        Used by Queen AI for decision making
        """
        health = await self.bridge.check_health()
        stats = await self.bridge.get_bridge_stats()
        recovery = await self.bridge.get_recovery_dashboard()
        stuck_txs = await self.bridge.get_stuck_transactions()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "health": health,
            "statistics": stats,
            "recovery": recovery,
            "stuck_transactions": [
                {
                    "id": tx.id,
                    "age_minutes": (datetime.utcnow() - tx.created_at).total_seconds() / 60,
                    "retry_count": tx.retry_count,
                    "status": tx.status.value,
                    "amount": float(tx.amount),
                    "direction": tx.direction.value
                }
                for tx in stuck_txs
            ],
            "recommendations": await self._generate_recommendations(health, stats, recovery)
        }
    
    async def _generate_recommendations(
        self,
        health: Dict,
        stats: Dict,
        recovery: Dict
    ) -> List[str]:
        """Generate recommendations for Queen AI"""
        recommendations = []
        
        # Bridge health
        if not health["is_healthy"]:
            recommendations.append("CRITICAL: Bridge is unhealthy - investigate immediately")
        
        # Stuck transactions
        if recovery["total_stuck"] > 0:
            recommendations.append(
                f"ACTION: {recovery['total_stuck']} stuck transactions need attention"
            )
        
        if recovery["requiring_admin_review"] > 0:
            recommendations.append(
                f"ADMIN: {recovery['requiring_admin_review']} transactions require manual review"
            )
        
        # Liquidity
        if "liquidity_ratio" in health:
            if health["liquidity_ratio"] < 0.3:
                recommendations.append(
                    f"WARNING: Low liquidity ratio ({health['liquidity_ratio']:.1%}) - rebalance recommended"
                )
        
        # Connection issues
        if not health.get("ethereum_connected"):
            recommendations.append("ERROR: Ethereum client disconnected")
        
        if not health.get("solana_connected"):
            recommendations.append("ERROR: Solana client disconnected")
        
        if not recommendations:
            recommendations.append("OK: Bridge operating normally")
        
        return recommendations
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute bridge-specific tasks
        
        Args:
            task_data: Task parameters with 'type' field
            
        Returns:
            Result dictionary
        """
        task_type = task_data.get("type", "unknown")
        
        try:
            if task_type == "get_status":
                return await self.get_comprehensive_status()
            
            elif task_type == "monitor_transaction":
                tx_hash = task_data.get("tx_hash")
                if not tx_hash:
                    return {"success": False, "error": "Missing tx_hash"}
                return await self.monitor_bridge_transaction(tx_hash)
            
            elif task_type == "health_check":
                health = await self.health_check()
                return {"success": True, "health": health}
            
            elif task_type == "get_stats":
                stats = await self.get_bridge_stats()
                return {"success": True, "stats": stats}
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown task type: {task_type}"
                }
                
        except Exception as e:
            logger.error(f"BridgeBee execute error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
bridge_bee = BridgeBee()
