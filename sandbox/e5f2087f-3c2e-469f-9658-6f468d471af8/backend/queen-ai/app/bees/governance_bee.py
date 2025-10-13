"""
Governance Bee - Handles DAO governance, proposals, voting, and decision execution

Manages the decentralized governance system with Queen oversight.
Works with smart contracts for on-chain governance.
"""
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime, timedelta

from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class GovernanceBee(BaseBee):
    """
    Governance Management Bee
    
    Responsibilities:
    - Create and validate governance proposals
    - Track voting and quorum requirements
    - Execute approved proposals (with Queen permission)
    - Manage governance parameters (voting periods, quorum, etc.)
    - Track stakeholder participation
    - Generate governance reports and analytics
    - Enforce governance rules and timelock periods
    
    Governance Categories:
    - Treasury Spending (budget allocations, grants)
    - Protocol Parameters (fees, limits, rates)
    - Smart Contract Upgrades (with timelock)
    - Emergency Actions (with multi-sig)
    - Ecosystem Grants & Partnerships
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(
            bee_id=bee_id or 14,
            name="governance"
        )
        
        # Governance Parameters
        self.VOTING_PERIOD_DAYS = 7  # Standard voting period
        self.TIMELOCK_PERIOD_HOURS = 48  # Delay before execution
        self.QUORUM_PERCENTAGE = 10  # 10% of total supply must vote
        self.APPROVAL_THRESHOLD = 60  # 60% yes votes required
        
        # Proposal Categories with specific requirements
        self.PROPOSAL_TYPES = {
            "treasury_spending": {
                "quorum": 10,
                "approval": 60,
                "timelock_hours": 48,
                "max_amount_percentage": 5  # Max 5% of treasury per proposal
            },
            "parameter_change": {
                "quorum": 15,
                "approval": 65,
                "timelock_hours": 72,
                "queen_approval_required": True
            },
            "contract_upgrade": {
                "quorum": 20,
                "approval": 75,
                "timelock_hours": 168,  # 7 days
                "queen_approval_required": True,
                "security_audit_required": True
            },
            "emergency_action": {
                "quorum": 5,
                "approval": 50,
                "timelock_hours": 0,  # Immediate
                "queen_approval_required": True,
                "multisig_required": True
            },
            "ecosystem_grant": {
                "quorum": 8,
                "approval": 55,
                "timelock_hours": 24
            }
        }
        
        # Track proposals (in production, this would be from database/blockchain)
        self.proposals = []
        self.votes = {}  # proposal_id -> {voter: vote_weight, ...}
        self.executed_proposals = []
        
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute governance task
        
        Task Types:
        - create_proposal: Create new governance proposal
        - vote: Cast vote on proposal
        - get_proposal: Get proposal details
        - execute_proposal: Execute approved proposal
        - get_voting_power: Calculate voting power for address
        - get_active_proposals: List all active proposals
        - get_proposal_status: Check proposal status
        - delegate_votes: Delegate voting power
        - get_governance_stats: Governance analytics
        """
        task_type = task_data.get("type")
        
        logger.info(f"GovernanceBee executing: {task_type}", data=task_data)
        
        try:
            if task_type == "create_proposal":
                return await self._create_proposal(task_data)
            elif task_type == "vote":
                return await self._vote(task_data)
            elif task_type == "get_proposal":
                return await self._get_proposal(task_data)
            elif task_type == "execute_proposal":
                return await self._execute_proposal(task_data)
            elif task_type == "get_voting_power":
                return await self._get_voting_power(task_data)
            elif task_type == "get_active_proposals":
                return await self._get_active_proposals(task_data)
            elif task_type == "get_proposal_status":
                return await self._get_proposal_status(task_data)
            elif task_type == "delegate_votes":
                return await self._delegate_votes(task_data)
            elif task_type == "get_governance_stats":
                return await self._get_governance_stats(task_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown task type: {task_type}"
                }
                
        except Exception as e:
            logger.error(f"GovernanceBee error: {str(e)}", task_type=task_type)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_proposal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new governance proposal
        
        Validates proposal and determines requirements based on category
        """
        proposer = data.get("proposer_address")
        proposal_type = data.get("proposal_type")
        title = data.get("title")
        description = data.get("description")
        actions = data.get("actions", [])  # List of actions to execute
        
        # Validation 1: Proposal type exists
        if proposal_type not in self.PROPOSAL_TYPES:
            return {
                "success": False,
                "error": f"Invalid proposal type. Must be one of: {list(self.PROPOSAL_TYPES.keys())}"
            }
        
        # Validation 2: Proposer has minimum voting power
        voting_power_check = await self._get_voting_power({"address": proposer})
        min_proposal_power = 100_000  # Need 100K tokens to propose
        
        if voting_power_check["voting_power"] < min_proposal_power:
            return {
                "success": False,
                "error": f"Insufficient voting power. Need {min_proposal_power:,} tokens to propose."
            }
        
        # Get proposal requirements
        requirements = self.PROPOSAL_TYPES[proposal_type]
        
        # Create proposal
        proposal_id = len(self.proposals) + 1
        voting_start = datetime.utcnow()
        voting_end = voting_start + timedelta(days=self.VOTING_PERIOD_DAYS)
        timelock_end = voting_end + timedelta(hours=requirements["timelock_hours"])
        
        proposal = {
            "proposal_id": proposal_id,
            "proposer": proposer,
            "proposal_type": proposal_type,
            "title": title,
            "description": description,
            "actions": actions,
            "requirements": requirements,
            "voting_start": voting_start.isoformat(),
            "voting_end": voting_end.isoformat(),
            "timelock_end": timelock_end.isoformat() if requirements["timelock_hours"] > 0 else None,
            "status": "active",
            "yes_votes": 0,
            "no_votes": 0,
            "abstain_votes": 0,
            "total_votes": 0,
            "created_at": voting_start.isoformat()
        }
        
        self.proposals.append(proposal)
        self.votes[proposal_id] = {}
        
        logger.info(
            f"Proposal created",
            proposal_id=proposal_id,
            type=proposal_type,
            proposer=proposer
        )
        
        return {
            "success": True,
            "message": "Proposal created successfully",
            "proposal": proposal,
            "note": "Queen approval required" if requirements.get("queen_approval_required") else None
        }
    
    async def _vote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cast vote on proposal
        
        Vote options: yes, no, abstain
        Voting power is based on token holdings
        """
        proposal_id = data.get("proposal_id")
        voter = data.get("voter_address")
        vote_choice = data.get("vote")  # "yes", "no", "abstain"
        
        # Find proposal
        proposal = next((p for p in self.proposals if p["proposal_id"] == proposal_id), None)
        
        if not proposal:
            return {"success": False, "error": "Proposal not found"}
        
        # Check if voting is still active
        voting_end = datetime.fromisoformat(proposal["voting_end"])
        if datetime.utcnow() > voting_end:
            return {"success": False, "error": "Voting period has ended"}
        
        # Check if already voted
        if voter in self.votes[proposal_id]:
            return {"success": False, "error": "Already voted on this proposal"}
        
        # Get voting power
        power_result = await self._get_voting_power({"address": voter})
        voting_power = power_result["voting_power"]
        
        if voting_power == 0:
            return {"success": False, "error": "No voting power"}
        
        # Record vote
        self.votes[proposal_id][voter] = {
            "vote": vote_choice,
            "power": voting_power,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update proposal vote counts
        if vote_choice == "yes":
            proposal["yes_votes"] += voting_power
        elif vote_choice == "no":
            proposal["no_votes"] += voting_power
        elif vote_choice == "abstain":
            proposal["abstain_votes"] += voting_power
        
        proposal["total_votes"] += voting_power
        
        logger.info(
            f"Vote cast",
            proposal_id=proposal_id,
            voter=voter,
            vote=vote_choice,
            power=voting_power
        )
        
        return {
            "success": True,
            "message": "Vote recorded",
            "proposal_id": proposal_id,
            "vote": vote_choice,
            "voting_power": voting_power,
            "current_results": {
                "yes": proposal["yes_votes"],
                "no": proposal["no_votes"],
                "abstain": proposal["abstain_votes"],
                "total": proposal["total_votes"]
            }
        }
    
    async def _get_proposal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed proposal information"""
        proposal_id = data.get("proposal_id")
        
        proposal = next((p for p in self.proposals if p["proposal_id"] == proposal_id), None)
        
        if not proposal:
            return {"success": False, "error": "Proposal not found"}
        
        # Calculate status
        status_info = await self._calculate_proposal_status(proposal)
        
        return {
            "success": True,
            "proposal": proposal,
            "status_info": status_info,
            "vote_count": len(self.votes.get(proposal_id, {}))
        }
    
    async def _calculate_proposal_status(self, proposal: Dict) -> Dict:
        """Calculate detailed proposal status"""
        total_supply = 1_000_000_000  # 1B OMK tokens
        
        # Calculate percentages
        quorum_needed = (total_supply * proposal["requirements"]["quorum"]) / 100
        quorum_reached = proposal["total_votes"] >= quorum_needed
        quorum_percentage = (proposal["total_votes"] / total_supply) * 100
        
        # Calculate approval (of votes cast, excluding abstentions)
        votes_for_or_against = proposal["yes_votes"] + proposal["no_votes"]
        if votes_for_or_against > 0:
            approval_percentage = (proposal["yes_votes"] / votes_for_or_against) * 100
        else:
            approval_percentage = 0
        
        approval_needed = proposal["requirements"]["approval"]
        approval_reached = approval_percentage >= approval_needed
        
        # Check if voting ended
        voting_end = datetime.fromisoformat(proposal["voting_end"])
        voting_ended = datetime.utcnow() > voting_end
        
        # Determine overall status
        if proposal["status"] == "executed":
            status = "executed"
        elif proposal["status"] == "cancelled":
            status = "cancelled"
        elif not voting_ended:
            status = "voting_active"
        elif voting_ended and quorum_reached and approval_reached:
            # Check if still in timelock
            if proposal["timelock_end"]:
                timelock_end = datetime.fromisoformat(proposal["timelock_end"])
                if datetime.utcnow() < timelock_end:
                    status = "approved_timelock"
                else:
                    status = "ready_to_execute"
            else:
                status = "ready_to_execute"
        elif voting_ended and not quorum_reached:
            status = "failed_quorum"
        elif voting_ended and not approval_reached:
            status = "rejected"
        else:
            status = "failed"
        
        return {
            "status": status,
            "quorum_reached": quorum_reached,
            "quorum_percentage": round(quorum_percentage, 2),
            "quorum_needed_percentage": proposal["requirements"]["quorum"],
            "approval_percentage": round(approval_percentage, 2),
            "approval_needed_percentage": approval_needed,
            "approval_reached": approval_reached,
            "voting_ended": voting_ended,
            "time_remaining": str(voting_end - datetime.utcnow()) if not voting_ended else "0:00:00"
        }
    
    async def _execute_proposal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute approved proposal
        
        Requires Queen approval for certain proposal types
        """
        proposal_id = data.get("proposal_id")
        executor = data.get("executor_address")
        queen_approved = data.get("queen_approved", False)
        
        proposal = next((p for p in self.proposals if p["proposal_id"] == proposal_id), None)
        
        if not proposal:
            return {"success": False, "error": "Proposal not found"}
        
        # Check status
        status_info = await self._calculate_proposal_status(proposal)
        
        if status_info["status"] not in ["ready_to_execute", "approved_timelock"]:
            return {
                "success": False,
                "error": f"Proposal cannot be executed. Current status: {status_info['status']}"
            }
        
        # Check if Queen approval required
        if proposal["requirements"].get("queen_approval_required") and not queen_approved:
            return {
                "success": False,
                "requires_queen_approval": True,
                "message": "This proposal requires Queen approval before execution"
            }
        
        # Execute proposal actions
        execution_results = []
        for action in proposal["actions"]:
            # In production, this would interact with smart contracts
            execution_results.append({
                "action": action,
                "status": "executed",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Mark as executed
        proposal["status"] = "executed"
        proposal["executed_at"] = datetime.utcnow().isoformat()
        proposal["executed_by"] = executor
        
        self.executed_proposals.append(proposal_id)
        
        logger.info(
            f"Proposal executed",
            proposal_id=proposal_id,
            executor=executor
        )
        
        return {
            "success": True,
            "message": "Proposal executed successfully",
            "proposal_id": proposal_id,
            "execution_results": execution_results
        }
    
    async def _get_voting_power(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate voting power for an address
        
        In production, this would query token balances and staking contracts
        """
        address = data.get("address")
        
        # Simulated voting power (in production, query blockchain)
        # Voting power = tokens held + staked tokens + delegated votes
        token_balance = 500_000  # Simulated
        staked_balance = 200_000  # Simulated
        delegated_to_address = 50_000  # Simulated
        
        total_power = token_balance + staked_balance + delegated_to_address
        
        return {
            "success": True,
            "address": address,
            "voting_power": total_power,
            "breakdown": {
                "token_balance": token_balance,
                "staked_balance": staked_balance,
                "delegated_votes": delegated_to_address
            }
        }
    
    async def _get_active_proposals(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get all active proposals"""
        active = [p for p in self.proposals if p["status"] == "active"]
        
        return {
            "success": True,
            "active_proposals": active,
            "count": len(active)
        }
    
    async def _get_proposal_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get current status of proposal"""
        proposal_id = data.get("proposal_id")
        
        proposal = next((p for p in self.proposals if p["proposal_id"] == proposal_id), None)
        
        if not proposal:
            return {"success": False, "error": "Proposal not found"}
        
        status_info = await self._calculate_proposal_status(proposal)
        
        return {
            "success": True,
            "proposal_id": proposal_id,
            "status": status_info
        }
    
    async def _delegate_votes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate voting power to another address
        
        In production, this would interact with delegation contract
        """
        delegator = data.get("delegator_address")
        delegatee = data.get("delegatee_address")
        
        # Get current voting power
        power_result = await self._get_voting_power({"address": delegator})
        power_to_delegate = power_result["voting_power"]
        
        logger.info(
            f"Votes delegated",
            delegator=delegator,
            delegatee=delegatee,
            power=power_to_delegate
        )
        
        return {
            "success": True,
            "message": "Voting power delegated",
            "delegator": delegator,
            "delegatee": delegatee,
            "voting_power_delegated": power_to_delegate
        }
    
    async def _get_governance_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive governance statistics"""
        
        total_proposals = len(self.proposals)
        executed_count = len([p for p in self.proposals if p["status"] == "executed"])
        active_count = len([p for p in self.proposals if p["status"] == "active"])
        
        # Voter participation
        unique_voters = set()
        for votes in self.votes.values():
            unique_voters.update(votes.keys())
        
        return {
            "success": True,
            "stats": {
                "total_proposals": total_proposals,
                "executed_proposals": executed_count,
                "active_proposals": active_count,
                "unique_voters": len(unique_voters),
                "total_votes_cast": sum(len(v) for v in self.votes.values()),
                "governance_parameters": {
                    "voting_period_days": self.VOTING_PERIOD_DAYS,
                    "quorum_percentage": self.QUORUM_PERCENTAGE,
                    "approval_threshold": self.APPROVAL_THRESHOLD
                }
            }
        }
