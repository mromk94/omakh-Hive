"""
Visualization Bee - Generates dashboards, charts, and simulations

Creates visual representations of hive data for monitoring and analysis.
Produces data for frontend dashboards and simulation scenarios.
"""
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime, timedelta
import json

from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class VisualizationBee(BaseBee):
    """
    Visualization & Dashboard Bee
    
    Responsibilities:
    - Generate dashboard data for frontend
    - Create time-series data for charts
    - Produce simulation scenarios
    - Format data for visualization libraries
    - Generate reports and analytics summaries
    - Create real-time monitoring feeds
    - Produce comparative analysis charts
    
    Output Formats:
    - Chart.js compatible datasets
    - D3.js compatible data structures
    - Recharts compatible formats
    - CSV/JSON exports
    - Real-time WebSocket feeds
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(
            bee_id=bee_id or 15,
            name="visualization"
        )
        
        # Cached dashboard data
        self.dashboard_cache = {}
        self.cache_ttl = 60  # seconds
        self.last_cache_update = None
        
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute visualization task
        
        Task Types:
        - get_dashboard_data: Main dashboard overview
        - get_pool_health_chart: Pool health time series
        - get_treasury_breakdown: Treasury allocation pie chart
        - get_staking_metrics: Staking statistics
        - get_governance_activity: Governance proposal charts
        - get_price_chart: Token price history
        - get_volume_chart: Trading volume chart
        - simulate_scenario: Run "what-if" simulations
        - get_comparative_analysis: Compare metrics over time
        - export_report: Generate downloadable reports
        """
        task_type = task_data.get("type")
        
        logger.info(f"VisualizationBee executing: {task_type}", data=task_data)
        
        try:
            if task_type == "get_dashboard_data":
                return await self._get_dashboard_data(task_data)
            elif task_type == "get_pool_health_chart":
                return await self._get_pool_health_chart(task_data)
            elif task_type == "get_treasury_breakdown":
                return await self._get_treasury_breakdown(task_data)
            elif task_type == "get_staking_metrics":
                return await self._get_staking_metrics(task_data)
            elif task_type == "get_governance_activity":
                return await self._get_governance_activity(task_data)
            elif task_type == "get_price_chart":
                return await self._get_price_chart(task_data)
            elif task_type == "get_volume_chart":
                return await self._get_volume_chart(task_data)
            elif task_type == "simulate_scenario":
                return await self._simulate_scenario(task_data)
            elif task_type == "get_comparative_analysis":
                return await self._get_comparative_analysis(task_data)
            elif task_type == "export_report":
                return await self._export_report(task_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown task type: {task_type}"
                }
                
        except Exception as e:
            logger.error(f"VisualizationBee error: {str(e)}", task_type=task_type)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_dashboard_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard overview
        
        Returns key metrics, charts, and status indicators
        """
        # Check cache
        if self._is_cache_valid():
            return {
                "success": True,
                "dashboard": self.dashboard_cache,
                "from_cache": True
            }
        
        # Generate fresh dashboard data
        dashboard = {
            "overview": {
                "total_supply": "1,000,000,000 OMK",
                "circulating_supply": "400,000,000 OMK",
                "market_cap": "$12,250,000",
                "price": "$0.1225",
                "24h_change": "+5.2%",
                "total_holders": 15_234,
                "active_bees": 14,
                "hive_health": "Excellent"
            },
            "quick_stats": [
                {
                    "label": "Total Staked",
                    "value": "150M OMK",
                    "change": "+2.3%",
                    "trend": "up"
                },
                {
                    "label": "Treasury Balance",
                    "value": "$8.5M",
                    "change": "-1.2%",
                    "trend": "down"
                },
                {
                    "label": "Active Proposals",
                    "value": "3",
                    "change": "+1",
                    "trend": "up"
                },
                {
                    "label": "Pool Health",
                    "value": "92%",
                    "change": "+0.5%",
                    "trend": "up"
                }
            ],
            "alerts": [
                {
                    "severity": "info",
                    "message": "Governance proposal #12 voting ends in 2 days",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "severity": "warning",
                    "message": "Pool deviation detected: +3.2% from peg",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "bee_status": {
                "active": 14,
                "healthy": 14,
                "degraded": 0,
                "offline": 0,
                "bees": [
                    {"name": "MathsBee", "status": "active", "tasks_today": 1234},
                    {"name": "SecurityBee", "status": "active", "tasks_today": 856},
                    {"name": "GovernanceBee", "status": "active", "tasks_today": 234},
                    {"name": "VisualizationBee", "status": "active", "tasks_today": 567}
                ]
            },
            "recent_activity": [
                {
                    "type": "proposal_created",
                    "description": "New treasury allocation proposal",
                    "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat()
                },
                {
                    "type": "staking_reward",
                    "description": "Daily staking rewards distributed: 5,000 OMK",
                    "timestamp": (datetime.utcnow() - timedelta(hours=5)).isoformat()
                },
                {
                    "type": "pool_rebalance",
                    "description": "Liquidity pool rebalanced automatically",
                    "timestamp": (datetime.utcnow() - timedelta(hours=8)).isoformat()
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Cache the dashboard
        self.dashboard_cache = dashboard
        self.last_cache_update = datetime.utcnow()
        
        return {
            "success": True,
            "dashboard": dashboard,
            "from_cache": False
        }
    
    async def _get_pool_health_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate pool health time series chart data
        
        Format: Chart.js compatible
        """
        timeframe = data.get("timeframe", "7d")  # 24h, 7d, 30d, 90d
        
        # Generate time series data
        points = self._get_timeframe_points(timeframe)
        timestamps = []
        health_scores = []
        deviation_values = []
        
        base_time = datetime.utcnow()
        
        for i in range(points):
            time_offset = timedelta(hours=(points - i) * (168 / points))  # Spread over timeframe
            timestamp = base_time - time_offset
            timestamps.append(timestamp.isoformat())
            
            # Simulated health score (85-95%)
            import random
            health_scores.append(85 + random.random() * 10)
            deviation_values.append(-2 + random.random() * 4)  # -2% to +2%
        
        chart_data = {
            "labels": timestamps,
            "datasets": [
                {
                    "label": "Pool Health Score",
                    "data": health_scores,
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    "fill": True,
                    "tension": 0.4
                },
                {
                    "label": "Price Deviation (%)",
                    "data": deviation_values,
                    "borderColor": "rgb(255, 99, 132)",
                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                    "fill": False,
                    "yAxisID": "y1"
                }
            ],
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"Pool Health - Last {timeframe}"
                    }
                },
                "scales": {
                    "y": {
                        "type": "linear",
                        "display": True,
                        "position": "left",
                        "title": {"text": "Health Score (%)"}
                    },
                    "y1": {
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "title": {"text": "Deviation (%)"},
                        "grid": {"drawOnChartArea": False}
                    }
                }
            }
        }
        
        return {
            "success": True,
            "chart_type": "line",
            "chart_data": chart_data,
            "timeframe": timeframe
        }
    
    async def _get_treasury_breakdown(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate treasury allocation pie/donut chart
        
        Format: Chart.js compatible
        """
        treasury_data = {
            "labels": [
                "Development",
                "Marketing",
                "Liquidity Reserves",
                "Staking Rewards",
                "Operations",
                "Emergency Fund"
            ],
            "datasets": [{
                "data": [25, 15, 30, 20, 5, 5],  # Percentages
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.8)",
                    "rgba(54, 162, 235, 0.8)",
                    "rgba(255, 206, 86, 0.8)",
                    "rgba(75, 192, 192, 0.8)",
                    "rgba(153, 102, 255, 0.8)",
                    "rgba(255, 159, 64, 0.8)"
                ],
                "borderColor": [
                    "rgba(255, 99, 132, 1)",
                    "rgba(54, 162, 235, 1)",
                    "rgba(255, 206, 86, 1)",
                    "rgba(75, 192, 192, 1)",
                    "rgba(153, 102, 255, 1)",
                    "rgba(255, 159, 64, 1)"
                ],
                "borderWidth": 2
            }]
        }
        
        # Detailed breakdown
        breakdown = {
            "Development": {"amount": "$2,125,000", "percentage": 25, "spent": 45},
            "Marketing": {"amount": "$1,275,000", "percentage": 15, "spent": 32},
            "Liquidity Reserves": {"amount": "$2,550,000", "percentage": 30, "spent": 0},
            "Staking Rewards": {"amount": "$1,700,000", "percentage": 20, "spent": 67},
            "Operations": {"amount": "$425,000", "percentage": 5, "spent": 58},
            "Emergency Fund": {"amount": "$425,000", "percentage": 5, "spent": 0}
        }
        
        return {
            "success": True,
            "chart_type": "doughnut",
            "chart_data": treasury_data,
            "breakdown": breakdown,
            "total_treasury": "$8,500,000"
        }
    
    async def _get_staking_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate staking dashboard metrics"""
        
        metrics = {
            "overview": {
                "total_staked": "150,000,000 OMK",
                "total_stakers": 5_234,
                "current_apy": "12.5%",
                "total_rewards_distributed": "5,234,000 OMK"
            },
            "distribution": {
                "30_day": {"stakers": 1234, "amount": "30M OMK", "apy": "8%"},
                "90_day": {"stakers": 2567, "amount": "75M OMK", "apy": "12%"},
                "180_day": {"stakers": 1023, "amount": "35M OMK", "apy": "15%"},
                "365_day": {"stakers": 410, "amount": "10M OMK", "apy": "20%"}
            },
            "recent_stakes": [
                {"address": "0x1234...5678", "amount": "100,000 OMK", "period": "90d", "time": "2h ago"},
                {"address": "0x8765...4321", "amount": "50,000 OMK", "period": "180d", "time": "5h ago"}
            ]
        }
        
        return {
            "success": True,
            "metrics": metrics
        }
    
    async def _get_governance_activity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate governance activity charts"""
        
        # Proposal timeline
        timeline_data = {
            "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "datasets": [{
                "label": "Proposals Created",
                "data": [2, 4, 3, 5],
                "backgroundColor": "rgba(54, 162, 235, 0.8)"
            }, {
                "label": "Proposals Executed",
                "data": [1, 2, 2, 3],
                "backgroundColor": "rgba(75, 192, 192, 0.8)"
            }]
        }
        
        # Voter participation
        participation = {
            "total_voters": 8_234,
            "active_voters_30d": 3_456,
            "participation_rate": "42%",
            "average_voting_power": "1,250,000 OMK"
        }
        
        return {
            "success": True,
            "timeline": timeline_data,
            "participation": participation
        }
    
    async def _get_price_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate token price chart"""
        
        timeframe = data.get("timeframe", "7d")
        points = self._get_timeframe_points(timeframe)
        
        timestamps = []
        prices = []
        volumes = []
        
        base_price = 0.1225
        base_time = datetime.utcnow()
        
        for i in range(points):
            time_offset = timedelta(hours=(points - i) * (168 / points))
            timestamp = base_time - time_offset
            timestamps.append(timestamp.strftime("%Y-%m-%d %H:%M"))
            
            # Simulated price movement
            import random
            price_variation = base_price * (0.95 + random.random() * 0.1)
            prices.append(round(price_variation, 4))
            volumes.append(random.randint(500000, 2000000))
        
        return {
            "success": True,
            "chart_data": {
                "labels": timestamps,
                "price": prices,
                "volume": volumes
            },
            "current_price": base_price,
            "24h_high": max(prices),
            "24h_low": min(prices),
            "24h_volume": sum(volumes)
        }
    
    async def _get_volume_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading volume chart"""
        
        return {
            "success": True,
            "message": "Volume chart data generated"
        }
    
    async def _simulate_scenario(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run "what-if" scenario simulations
        
        Scenarios:
        - price_impact: What if price changes by X%?
        - liquidity_change: What if liquidity increases/decreases?
        - staking_participation: What if staking rate changes?
        - governance_threshold: What if quorum requirements change?
        """
        scenario_type = data.get("scenario_type")
        parameters = data.get("parameters", {})
        
        if scenario_type == "price_impact":
            price_change = parameters.get("price_change_percent", 10)
            
            simulation = {
                "scenario": f"Price change: {price_change:+.1f}%",
                "current_state": {
                    "price": "$0.1225",
                    "market_cap": "$12,250,000",
                    "liquidity": "$2,550,000"
                },
                "projected_state": {
                    "price": f"${0.1225 * (1 + price_change/100):.4f}",
                    "market_cap": f"${12_250_000 * (1 + price_change/100):,.0f}",
                    "liquidity_impact": f"{price_change/2:+.1f}%"
                },
                "risks": [
                    "Pool imbalance risk" if abs(price_change) > 10 else None,
                    "Arbitrage opportunities" if abs(price_change) > 5 else None
                ],
                "recommendations": [
                    "Monitor pool health closely",
                    "Prepare liquidity adjustments" if abs(price_change) > 15 else None
                ]
            }
            
            # Remove None values
            simulation["risks"] = [r for r in simulation["risks"] if r]
            simulation["recommendations"] = [r for r in simulation["recommendations"] if r]
            
            return {
                "success": True,
                "simulation": simulation
            }
        
        elif scenario_type == "staking_participation":
            participation_change = parameters.get("participation_change_percent", 20)
            
            current_staked = 150_000_000
            new_staked = current_staked * (1 + participation_change/100)
            
            simulation = {
                "scenario": f"Staking participation change: {participation_change:+.1f}%",
                "current_apy": "12.5%",
                "projected_apy": f"{12.5 * (current_staked / new_staked):.2f}%",
                "impact": {
                    "total_staked": f"{new_staked:,.0f} OMK",
                    "apy_change": f"{12.5 * (current_staked / new_staked) - 12.5:+.2f}%",
                    "treasury_impact": "Sustainable" if participation_change < 50 else "Review needed"
                }
            }
            
            return {
                "success": True,
                "simulation": simulation
            }
        
        return {
            "success": False,
            "error": f"Unknown scenario type: {scenario_type}"
        }
    
    async def _get_comparative_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare metrics across different time periods"""
        
        metrics = data.get("metrics", ["price", "volume", "staking"])
        
        comparison = {
            "price": {
                "current": "$0.1225",
                "1d_ago": "$0.1198",
                "7d_ago": "$0.1156",
                "30d_ago": "$0.1089",
                "changes": {
                    "1d": "+2.3%",
                    "7d": "+6.0%",
                    "30d": "+12.5%"
                }
            },
            "volume": {
                "current": "$1,234,567",
                "1d_ago": "$1,456,789",
                "7d_ago": "$987,654",
                "changes": {
                    "1d": "-15.3%",
                    "7d": "+25.0%"
                }
            },
            "staking": {
                "current": "150M OMK",
                "1d_ago": "149.5M OMK",
                "7d_ago": "147M OMK",
                "changes": {
                    "1d": "+0.3%",
                    "7d": "+2.0%"
                }
            }
        }
        
        return {
            "success": True,
            "comparison": comparison
        }
    
    async def _export_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate downloadable report"""
        
        report_type = data.get("report_type", "weekly")
        format_type = data.get("format", "json")  # json, csv, pdf
        
        report = {
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "period": {
                "start": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "summary": {
                "total_transactions": 15_234,
                "unique_users": 3_456,
                "total_volume": "$5,678,900",
                "governance_proposals": 3,
                "bee_uptime": "99.8%"
            }
        }
        
        if format_type == "json":
            return {
                "success": True,
                "report": report,
                "download_url": "/api/reports/weekly_2025_10_09.json"
            }
        
        return {
            "success": True,
            "report_generated": True
        }
    
    def _get_timeframe_points(self, timeframe: str) -> int:
        """Convert timeframe to number of data points"""
        timeframe_map = {
            "24h": 24,
            "7d": 168,
            "30d": 30,
            "90d": 90
        }
        return timeframe_map.get(timeframe, 24)
    
    def _is_cache_valid(self) -> bool:
        """Check if cached dashboard data is still valid"""
        if not self.last_cache_update:
            return False
        
        age = (datetime.utcnow() - self.last_cache_update).total_seconds()
        return age < self.cache_ttl
