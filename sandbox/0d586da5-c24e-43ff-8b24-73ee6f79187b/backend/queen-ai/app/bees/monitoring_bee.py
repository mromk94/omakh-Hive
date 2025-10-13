"""
Monitoring Bee - Hive Health, Security, and Safety Monitoring

Critical bee for ensuring hive security, safety, and health.
Monitors all bees, detects anomalies, and alerts Queen of critical issues.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import structlog
from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class MonitoringBee(BaseBee):
    """
    Specialized bee for hive monitoring
    
    Responsibilities:
    - Monitor hive health (all bees)
    - Security monitoring and threat detection
    - Safety checks and compliance
    - Performance monitoring
    - Resource usage tracking
    - Alert generation for critical issues
    - System diagnostics
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="MonitoringBee")
        # Monitoring thresholds
        self.health_thresholds = {
            "bee_response_time": 5.0,  # seconds
            "bee_error_rate": 0.05,     # 5%
            "message_bus_latency": 1.0, # seconds
            "memory_usage": 80,         # percent
            "cpu_usage": 85,            # percent
        }
        self.alert_history = []
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring task"""
        task_type = task_data.get("type")
        
        if task_type == "check_hive_health":
            return await self._check_hive_health(task_data)
        elif task_type == "monitor_security":
            return await self._monitor_security(task_data)
        elif task_type == "check_safety":
            return await self._check_safety(task_data)
        elif task_type == "monitor_performance":
            return await self._monitor_performance(task_data)
        elif task_type == "check_resources":
            return await self._check_resources(task_data)
        elif task_type == "generate_diagnostics":
            return await self._generate_diagnostics(task_data)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _check_hive_health(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check overall hive health"""
        try:
            bees_status = data.get("bees_status", {})
            message_bus_stats = data.get("message_bus_stats", {})
            
            health_issues = []
            critical_issues = []
            warnings = []
            
            # Check each bee
            unhealthy_bees = []
            for bee_name, bee_status in bees_status.items():
                status = bee_status.get("status", "unknown")
                error_rate = bee_status.get("error_rate", 0)
                response_time = bee_status.get("avg_response_time", 0)
                
                if status == "error":
                    critical_issues.append(f"{bee_name} is in ERROR state")
                    unhealthy_bees.append(bee_name)
                elif error_rate > self.health_thresholds["bee_error_rate"]:
                    warnings.append(f"{bee_name} has high error rate: {error_rate*100:.1f}%")
                    unhealthy_bees.append(bee_name)
                elif response_time > self.health_thresholds["bee_response_time"]:
                    warnings.append(f"{bee_name} has slow response time: {response_time:.2f}s")
            
            # Check message bus
            bus_latency = message_bus_stats.get("avg_latency", 0)
            if bus_latency > self.health_thresholds["message_bus_latency"]:
                warnings.append(f"Message bus latency high: {bus_latency:.2f}s")
            
            # Calculate overall health score
            total_bees = len(bees_status)
            healthy_bees = total_bees - len(unhealthy_bees)
            health_score = (healthy_bees / total_bees * 100) if total_bees > 0 else 0
            
            # Determine overall status
            if critical_issues:
                overall_status = "critical"
            elif len(warnings) > 3:
                overall_status = "degraded"
            elif warnings:
                overall_status = "warning"
            else:
                overall_status = "healthy"
            
            # Generate alerts for critical issues
            for issue in critical_issues:
                await self._generate_alert({
                    "severity": "critical",
                    "message": issue,
                    "category": "hive_health",
                })
            
            return {
                "success": True,
                "overall_status": overall_status,
                "health_score": round(health_score, 2),
                "total_bees": total_bees,
                "healthy_bees": healthy_bees,
                "unhealthy_bees": unhealthy_bees,
                "critical_issues": critical_issues,
                "warnings": warnings,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _monitor_security(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor security threats and anomalies"""
        try:
            recent_transactions = data.get("recent_transactions", [])
            failed_auth_attempts = data.get("failed_auth_attempts", 0)
            unusual_activity = data.get("unusual_activity", [])
            
            security_alerts = []
            threat_level = "low"
            
            # Check for failed authentication
            if failed_auth_attempts > 5:
                security_alerts.append({
                    "type": "authentication",
                    "severity": "high",
                    "message": f"Multiple failed auth attempts: {failed_auth_attempts}",
                })
                threat_level = "high"
            
            # Check for unusual transactions
            for tx in recent_transactions:
                amount = tx.get("amount", 0)
                if amount > 10_000_000 * 10**18:  # >10M OMK
                    security_alerts.append({
                        "type": "large_transaction",
                        "severity": "medium",
                        "message": f"Large transaction detected: {amount / 10**18:.0f} OMK",
                        "tx_hash": tx.get("hash"),
                    })
                    if threat_level == "low":
                        threat_level = "medium"
            
            # Check unusual activity patterns
            if unusual_activity:
                for activity in unusual_activity:
                    security_alerts.append({
                        "type": "unusual_activity",
                        "severity": "medium",
                        "message": activity.get("description"),
                    })
                    if threat_level == "low":
                        threat_level = "medium"
            
            # Generate critical alerts
            for alert in security_alerts:
                if alert["severity"] == "high":
                    await self._generate_alert({
                        "severity": "critical",
                        "message": alert["message"],
                        "category": "security",
                    })
            
            return {
                "success": True,
                "threat_level": threat_level,
                "security_alerts": security_alerts,
                "failed_auth_attempts": failed_auth_attempts,
                "monitoring_status": "active",
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _check_safety(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check safety compliance and limits"""
        try:
            daily_transfers = data.get("daily_transfers", 0)
            daily_limit = data.get("daily_limit", 50_000_000 * 10**18)
            treasury_balance = data.get("treasury_balance", 0)
            min_treasury_balance = data.get("min_treasury_balance", 10_000_000 * 10**18)
            
            safety_issues = []
            compliance_status = "compliant"
            
            # Check daily transfer limit
            utilization = (daily_transfers / daily_limit * 100) if daily_limit > 0 else 0
            if utilization > 95:
                safety_issues.append({
                    "type": "rate_limit",
                    "severity": "critical",
                    "message": f"Daily transfer limit almost reached: {utilization:.1f}%",
                })
                compliance_status = "at_risk"
            elif utilization > 80:
                safety_issues.append({
                    "type": "rate_limit",
                    "severity": "warning",
                    "message": f"Daily transfer limit high: {utilization:.1f}%",
                })
            
            # Check treasury balance
            if treasury_balance < min_treasury_balance:
                safety_issues.append({
                    "type": "treasury",
                    "severity": "critical",
                    "message": f"Treasury below minimum: {treasury_balance / 10**18:.0f} OMK",
                })
                compliance_status = "violated"
            
            # Generate alerts for critical issues
            for issue in safety_issues:
                if issue["severity"] == "critical":
                    await self._generate_alert({
                        "severity": "critical",
                        "message": issue["message"],
                        "category": "safety",
                    })
            
            return {
                "success": True,
                "compliance_status": compliance_status,
                "safety_issues": safety_issues,
                "daily_transfer_utilization": round(utilization, 2),
                "treasury_status": "healthy" if treasury_balance >= min_treasury_balance else "critical",
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _monitor_performance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor system performance"""
        try:
            response_times = data.get("response_times", {})
            throughput = data.get("throughput", 0)
            error_rate = data.get("error_rate", 0)
            
            performance_issues = []
            performance_score = 100
            
            # Check response times
            slow_operations = []
            for operation, time_ms in response_times.items():
                if time_ms > 5000:  # >5 seconds
                    slow_operations.append({
                        "operation": operation,
                        "time_ms": time_ms,
                    })
                    performance_score -= 10
            
            if slow_operations:
                performance_issues.append({
                    "type": "slow_response",
                    "operations": slow_operations,
                })
            
            # Check error rate
            if error_rate > 0.05:  # >5%
                performance_issues.append({
                    "type": "high_error_rate",
                    "error_rate": error_rate,
                })
                performance_score -= 20
            
            # Check throughput
            if throughput < 10:  # <10 ops/sec
                performance_issues.append({
                    "type": "low_throughput",
                    "throughput": throughput,
                })
                performance_score -= 15
            
            performance_score = max(0, performance_score)
            
            # Determine status
            if performance_score >= 80:
                status = "excellent"
            elif performance_score >= 60:
                status = "good"
            elif performance_score >= 40:
                status = "degraded"
            else:
                status = "poor"
            
            return {
                "success": True,
                "performance_score": performance_score,
                "status": status,
                "throughput": throughput,
                "error_rate": error_rate,
                "performance_issues": performance_issues,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _check_resources(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check resource usage"""
        try:
            memory_usage = data.get("memory_usage_percent", 0)
            cpu_usage = data.get("cpu_usage_percent", 0)
            disk_usage = data.get("disk_usage_percent", 0)
            network_usage = data.get("network_usage_mbps", 0)
            
            resource_alerts = []
            
            # Check memory
            if memory_usage > self.health_thresholds["memory_usage"]:
                resource_alerts.append({
                    "resource": "memory",
                    "usage": memory_usage,
                    "threshold": self.health_thresholds["memory_usage"],
                    "severity": "high" if memory_usage > 90 else "medium",
                })
            
            # Check CPU
            if cpu_usage > self.health_thresholds["cpu_usage"]:
                resource_alerts.append({
                    "resource": "cpu",
                    "usage": cpu_usage,
                    "threshold": self.health_thresholds["cpu_usage"],
                    "severity": "high" if cpu_usage > 95 else "medium",
                })
            
            # Check disk
            if disk_usage > 85:
                resource_alerts.append({
                    "resource": "disk",
                    "usage": disk_usage,
                    "threshold": 85,
                    "severity": "high" if disk_usage > 95 else "medium",
                })
            
            # Overall status
            if any(alert["severity"] == "high" for alert in resource_alerts):
                status = "critical"
            elif resource_alerts:
                status = "warning"
            else:
                status = "healthy"
            
            return {
                "success": True,
                "status": status,
                "memory_usage_percent": memory_usage,
                "cpu_usage_percent": cpu_usage,
                "disk_usage_percent": disk_usage,
                "network_usage_mbps": network_usage,
                "resource_alerts": resource_alerts,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_diagnostics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive system diagnostics"""
        try:
            # Gather all monitoring data
            hive_health = await self._check_hive_health(data.get("hive_health", {}))
            security = await self._monitor_security(data.get("security", {}))
            safety = await self._check_safety(data.get("safety", {}))
            performance = await self._monitor_performance(data.get("performance", {}))
            resources = await self._check_resources(data.get("resources", {}))
            
            # Aggregate status
            statuses = [
                hive_health.get("overall_status"),
                "critical" if security.get("threat_level") == "high" else "healthy",
                safety.get("compliance_status"),
                performance.get("status"),
                resources.get("status"),
            ]
            
            # Overall system health
            if "critical" in statuses or "violated" in statuses:
                system_health = "critical"
            elif "degraded" in statuses or "warning" in statuses or "at_risk" in statuses:
                system_health = "degraded"
            else:
                system_health = "healthy"
            
            # Recommendations
            recommendations = []
            if hive_health.get("unhealthy_bees"):
                recommendations.append("Restart unhealthy bees")
            if security.get("security_alerts"):
                recommendations.append("Review security alerts immediately")
            if safety.get("safety_issues"):
                recommendations.append("Address safety compliance issues")
            if performance.get("performance_issues"):
                recommendations.append("Optimize slow operations")
            if resources.get("resource_alerts"):
                recommendations.append("Scale resources or optimize usage")
            
            return {
                "success": True,
                "system_health": system_health,
                "hive_health": hive_health,
                "security": security,
                "safety": safety,
                "performance": performance,
                "resources": resources,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_alert(self, alert_data: Dict[str, Any]):
        """Generate and store alert"""
        alert = {
            "id": f"ALERT-{len(self.alert_history) + 1}",
            "severity": alert_data.get("severity"),
            "message": alert_data.get("message"),
            "category": alert_data.get("category"),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self.alert_history.append(alert)
        
        logger.warning(
            "Alert generated",
            alert_id=alert["id"],
            severity=alert["severity"],
            message=alert["message"]
        )
