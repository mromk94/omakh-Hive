// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title GovernanceManager
 * @dev DAO governance system for community voting on proposals
 * 
 * Features:
 * - Token-weighted voting (1 OMK = 1 vote)
 * - Proposal creation with minimum threshold
 * - 7-day voting period
 * - 10% quorum requirement
 * - Queen AI can veto dangerous proposals
 */
contract GovernanceManager is AccessControl {
    
    bytes32 public constant PROPOSER_ROLE = keccak256("PROPOSER_ROLE");
    bytes32 public constant GUARDIAN_ROLE = keccak256("GUARDIAN_ROLE"); // Queen AI (veto power)

    IERC20 public immutable omkToken;
    
    // Governance parameters
    uint256 public constant VOTING_PERIOD = 7 days;
    uint256 public constant QUORUM_PERCENTAGE = 10; // 10% of circulating supply
    uint256 public constant MIN_PROPOSAL_THRESHOLD = 1_000_000 * 10**18; // 1M OMK to propose
    
    enum ProposalType {
        PARAMETER_CHANGE,    // Change system parameters
        TREASURY_ALLOCATION, // Allocate treasury funds
        EMERGENCY_ACTION,    // Emergency system action
        PROTOCOL_UPGRADE,    // Upgrade contract
        GENERAL              // General proposal
    }
    
    enum VoteOption {
        AGAINST,
        FOR,
        ABSTAIN
    }
    
    struct Proposal {
        uint256 id;
        address proposer;
        ProposalType proposalType;
        string title;
        string description;
        address targetContract;
        bytes callData;
        uint256 startTime;
        uint256 endTime;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        bool executed;
        bool vetoed;
        bool cancelled;
        mapping(address => VoteOption) hasVoted;
        mapping(address => uint256) voteWeight;
    }
    
    uint256 public proposalCount;
    mapping(uint256 => Proposal) public proposals;
    
    // Timelock for execution
    uint256 public constant TIMELOCK_PERIOD = 2 days;
    mapping(uint256 => uint256) public proposalExecutionTime;
    
    // Events
    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        ProposalType proposalType,
        string title
    );
    event VoteCast(
        uint256 indexed proposalId,
        address indexed voter,
        VoteOption vote,
        uint256 weight
    );
    event ProposalExecuted(uint256 indexed proposalId);
    event ProposalVetoed(uint256 indexed proposalId, address indexed guardian);
    event ProposalCancelled(uint256 indexed proposalId);
    
    constructor(
        address _omkToken,
        address _admin,
        address _guardian
    ) {
        require(_omkToken != address(0), "GovernanceManager: Invalid token");
        
        omkToken = IERC20(_omkToken);
        
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(GUARDIAN_ROLE, _guardian); // Queen AI
    }

    // ============ PROPOSAL FUNCTIONS ============

    /**
     * @notice Create a new proposal
     */
    function createProposal(
        ProposalType proposalType,
        string calldata title,
        string calldata description,
        address targetContract,
        bytes calldata callData
    ) external returns (uint256) {
        require(
            omkToken.balanceOf(msg.sender) >= MIN_PROPOSAL_THRESHOLD,
            "GovernanceManager: Insufficient tokens to propose"
        );
        
        uint256 proposalId = proposalCount++;
        Proposal storage proposal = proposals[proposalId];
        
        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.proposalType = proposalType;
        proposal.title = title;
        proposal.description = description;
        proposal.targetContract = targetContract;
        proposal.callData = callData;
        proposal.startTime = block.timestamp;
        proposal.endTime = block.timestamp + VOTING_PERIOD;
        
        emit ProposalCreated(proposalId, msg.sender, proposalType, title);
        
        return proposalId;
    }

    /**
     * @notice Cast vote on proposal
     */
    function castVote(uint256 proposalId, VoteOption vote) external {
        Proposal storage proposal = proposals[proposalId];
        
        require(block.timestamp < proposal.endTime, "GovernanceManager: Voting ended");
        require(!proposal.executed, "GovernanceManager: Already executed");
        require(!proposal.vetoed, "GovernanceManager: Proposal vetoed");
        require(!proposal.cancelled, "GovernanceManager: Proposal cancelled");
        require(proposal.voteWeight[msg.sender] == 0, "GovernanceManager: Already voted");
        
        uint256 weight = omkToken.balanceOf(msg.sender);
        require(weight > 0, "GovernanceManager: No voting power");
        
        proposal.hasVoted[msg.sender] = vote;
        proposal.voteWeight[msg.sender] = weight;
        
        if (vote == VoteOption.FOR) {
            proposal.forVotes += weight;
        } else if (vote == VoteOption.AGAINST) {
            proposal.againstVotes += weight;
        } else {
            proposal.abstainVotes += weight;
        }
        
        emit VoteCast(proposalId, msg.sender, vote, weight);
    }

    /**
     * @notice Execute passed proposal (after timelock)
     */
    function executeProposal(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        
        require(block.timestamp >= proposal.endTime, "GovernanceManager: Voting ongoing");
        require(!proposal.executed, "GovernanceManager: Already executed");
        require(!proposal.vetoed, "GovernanceManager: Proposal vetoed");
        require(!proposal.cancelled, "GovernanceManager: Proposal cancelled");
        
        // Check if passed
        require(_hasQuorum(proposalId), "GovernanceManager: Quorum not reached");
        require(proposal.forVotes > proposal.againstVotes, "GovernanceManager: Proposal rejected");
        
        // Check timelock
        if (proposalExecutionTime[proposalId] == 0) {
            // First time - set execution time
            proposalExecutionTime[proposalId] = block.timestamp + TIMELOCK_PERIOD;
            return;
        }
        
        require(
            block.timestamp >= proposalExecutionTime[proposalId],
            "GovernanceManager: Timelock not expired"
        );
        
        // Execute
        proposal.executed = true;
        
        if (proposal.targetContract != address(0) && proposal.callData.length > 0) {
            (bool success, ) = proposal.targetContract.call(proposal.callData);
            require(success, "GovernanceManager: Execution failed");
        }
        
        emit ProposalExecuted(proposalId);
    }

    /**
     * @notice Veto proposal (Guardian/Queen only)
     */
    function vetoProposal(uint256 proposalId) external onlyRole(GUARDIAN_ROLE) {
        Proposal storage proposal = proposals[proposalId];
        
        require(!proposal.executed, "GovernanceManager: Already executed");
        require(!proposal.vetoed, "GovernanceManager: Already vetoed");
        
        proposal.vetoed = true;
        
        emit ProposalVetoed(proposalId, msg.sender);
    }

    /**
     * @notice Cancel own proposal
     */
    function cancelProposal(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        
        require(msg.sender == proposal.proposer, "GovernanceManager: Not proposer");
        require(!proposal.executed, "GovernanceManager: Already executed");
        require(!proposal.cancelled, "GovernanceManager: Already cancelled");
        
        proposal.cancelled = true;
        
        emit ProposalCancelled(proposalId);
    }

    // ============ VIEW FUNCTIONS ============

    /**
     * @notice Get proposal details
     */
    function getProposal(uint256 proposalId) external view returns (
        address proposer,
        ProposalType proposalType,
        string memory title,
        string memory description,
        uint256 startTime,
        uint256 endTime,
        uint256 forVotes,
        uint256 againstVotes,
        uint256 abstainVotes,
        bool executed,
        bool vetoed
    ) {
        Proposal storage proposal = proposals[proposalId];
        return (
            proposal.proposer,
            proposal.proposalType,
            proposal.title,
            proposal.description,
            proposal.startTime,
            proposal.endTime,
            proposal.forVotes,
            proposal.againstVotes,
            proposal.abstainVotes,
            proposal.executed,
            proposal.vetoed
        );
    }

    /**
     * @notice Check if user voted
     */
    function hasVoted(uint256 proposalId, address voter) external view returns (bool, VoteOption, uint256) {
        Proposal storage proposal = proposals[proposalId];
        uint256 weight = proposal.voteWeight[voter];
        return (weight > 0, proposal.hasVoted[voter], weight);
    }

    /**
     * @notice Check if proposal has quorum
     */
    function _hasQuorum(uint256 proposalId) internal view returns (bool) {
        Proposal storage proposal = proposals[proposalId];
        uint256 totalVotes = proposal.forVotes + proposal.againstVotes + proposal.abstainVotes;
        uint256 totalSupply = omkToken.totalSupply();
        
        return totalVotes >= (totalSupply * QUORUM_PERCENTAGE) / 100;
    }

    /**
     * @notice Get proposal status
     */
    function getProposalStatus(uint256 proposalId) external view returns (
        bool isActive,
        bool hasPassed,
        bool hasQuorum,
        uint256 timeRemaining
    ) {
        Proposal storage proposal = proposals[proposalId];
        
        isActive = block.timestamp < proposal.endTime && !proposal.executed && !proposal.vetoed;
        hasQuorum = _hasQuorum(proposalId);
        hasPassed = hasQuorum && proposal.forVotes > proposal.againstVotes;
        
        if (block.timestamp < proposal.endTime) {
            timeRemaining = proposal.endTime - block.timestamp;
        } else {
            timeRemaining = 0;
        }
    }
}
