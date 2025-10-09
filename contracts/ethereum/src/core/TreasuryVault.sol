// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title TreasuryVault
 * @dev Manages 120M OMK treasury with budget proposals and multi-sig approvals
 * 
 * Responsibilities:
 * - Development funding
 * - Marketing budgets
 * - Operational expenses
 * - Strategic investments
 * - Emergency reserves
 */
contract TreasuryVault is AccessControl, Pausable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // Roles
    bytes32 public constant TREASURER_ROLE = keccak256("TREASURER_ROLE"); // Queen AI advisory
    bytes32 public constant APPROVER_ROLE = keccak256("APPROVER_ROLE"); // Multi-sig members
    bytes32 public constant EXECUTOR_ROLE = keccak256("EXECUTOR_ROLE"); // Can execute approved proposals

    // OMK Token
    IERC20 public immutable omkToken;
    
    // Budget categories
    enum Category {
        DEVELOPMENT,      // 0: Dev team salaries, contractors
        MARKETING,        // 1: Campaigns, partnerships, ads
        OPERATIONS,       // 2: Infrastructure, legal, admin
        INVESTMENTS,      // 3: Strategic investments
        EMERGENCY,        // 4: Emergency fund
        GOVERNANCE        // 5: DAO/Community initiatives
    }
    
    // Proposal structure
    struct Proposal {
        uint256 id;
        address proposer;
        Category category;
        uint256 amount;
        address recipient;
        string description;
        uint256 createdAt;
        uint256 executedAt;
        uint256 approvals;
        bool executed;
        bool rejected;
        mapping(address => bool) hasApproved;
    }
    
    // State
    uint256 public proposalCount;
    uint256 public requiredApprovals = 2; // Multi-sig: require 2 approvals
    mapping(uint256 => Proposal) public proposals;
    
    // Budget tracking
    mapping(Category => uint256) public categoryBudgets;
    mapping(Category => uint256) public categorySpent;
    
    // Monthly limits
    mapping(Category => uint256) public monthlyLimits;
    mapping(Category => mapping(uint256 => uint256)) public monthlySpent; // month => spent
    
    // Events
    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        Category category,
        uint256 amount,
        address recipient
    );
    event ProposalApproved(uint256 indexed proposalId, address indexed approver, uint256 approvals);
    event ProposalExecuted(uint256 indexed proposalId, uint256 amount, address indexed recipient);
    event ProposalRejected(uint256 indexed proposalId, address indexed rejector);
    event BudgetAllocated(Category indexed category, uint256 amount);
    event MonthlyLimitSet(Category indexed category, uint256 limit);
    event EmergencyWithdrawal(address indexed to, uint256 amount, string reason);

    constructor(
        address _omkToken,
        address _admin,
        address _treasurer
    ) {
        require(_omkToken != address(0), "TreasuryVault: Invalid token");
        require(_admin != address(0), "TreasuryVault: Invalid admin");
        
        omkToken = IERC20(_omkToken);
        
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(TREASURER_ROLE, _treasurer); // Queen AI
        _grantRole(APPROVER_ROLE, _admin);
        _grantRole(EXECUTOR_ROLE, _admin);
        
        // Set default monthly limits (10% of total budget per month)
        monthlyLimits[Category.DEVELOPMENT] = 5_000_000 * 10**18;
        monthlyLimits[Category.MARKETING] = 3_000_000 * 10**18;
        monthlyLimits[Category.OPERATIONS] = 2_000_000 * 10**18;
        monthlyLimits[Category.INVESTMENTS] = 1_000_000 * 10**18;
        monthlyLimits[Category.EMERGENCY] = 10_000_000 * 10**18;
        monthlyLimits[Category.GOVERNANCE] = 1_000_000 * 10**18;
    }

    // ============ PROPOSAL FUNCTIONS ============

    /**
     * @notice Create spending proposal (Queen AI or Admin)
     */
    function createProposal(
        Category category,
        uint256 amount,
        address recipient,
        string calldata description
    ) external onlyRole(TREASURER_ROLE) returns (uint256) {
        require(amount > 0, "TreasuryVault: Amount must be positive");
        require(recipient != address(0), "TreasuryVault: Invalid recipient");
        
        uint256 proposalId = proposalCount++;
        Proposal storage prop = proposals[proposalId];
        
        prop.id = proposalId;
        prop.proposer = msg.sender;
        prop.category = category;
        prop.amount = amount;
        prop.recipient = recipient;
        prop.description = description;
        prop.createdAt = block.timestamp;
        prop.approvals = 0;
        prop.executed = false;
        prop.rejected = false;
        
        emit ProposalCreated(proposalId, msg.sender, category, amount, recipient);
        
        return proposalId;
    }

    /**
     * @notice Approve proposal (Multi-sig approvers)
     */
    function approveProposal(uint256 proposalId) external onlyRole(APPROVER_ROLE) {
        Proposal storage prop = proposals[proposalId];
        
        require(!prop.executed, "TreasuryVault: Already executed");
        require(!prop.rejected, "TreasuryVault: Already rejected");
        require(!prop.hasApproved[msg.sender], "TreasuryVault: Already approved");
        
        prop.hasApproved[msg.sender] = true;
        prop.approvals++;
        
        emit ProposalApproved(proposalId, msg.sender, prop.approvals);
    }

    /**
     * @notice Execute approved proposal
     */
    function executeProposal(uint256 proposalId) external onlyRole(EXECUTOR_ROLE) nonReentrant {
        Proposal storage prop = proposals[proposalId];
        
        require(!prop.executed, "TreasuryVault: Already executed");
        require(!prop.rejected, "TreasuryVault: Rejected");
        require(prop.approvals >= requiredApprovals, "TreasuryVault: Insufficient approvals");
        
        // Check monthly limit
        uint256 currentMonth = block.timestamp / 30 days;
        require(
            monthlySpent[prop.category][currentMonth] + prop.amount <= monthlyLimits[prop.category],
            "TreasuryVault: Monthly limit exceeded"
        );
        
        // Check balance
        require(
            omkToken.balanceOf(address(this)) >= prop.amount,
            "TreasuryVault: Insufficient balance"
        );
        
        // Update state
        prop.executed = true;
        prop.executedAt = block.timestamp;
        categorySpent[prop.category] += prop.amount;
        monthlySpent[prop.category][currentMonth] += prop.amount;
        
        // Transfer
        omkToken.safeTransfer(prop.recipient, prop.amount);
        
        emit ProposalExecuted(proposalId, prop.amount, prop.recipient);
    }

    /**
     * @notice Reject proposal
     */
    function rejectProposal(uint256 proposalId) external onlyRole(DEFAULT_ADMIN_ROLE) {
        Proposal storage prop = proposals[proposalId];
        
        require(!prop.executed, "TreasuryVault: Already executed");
        require(!prop.rejected, "TreasuryVault: Already rejected");
        
        prop.rejected = true;
        
        emit ProposalRejected(proposalId, msg.sender);
    }

    // ============ ADMIN FUNCTIONS ============

    /**
     * @notice Set monthly limit for category
     */
    function setMonthlyLimit(Category category, uint256 limit) external onlyRole(DEFAULT_ADMIN_ROLE) {
        monthlyLimits[category] = limit;
        emit MonthlyLimitSet(category, limit);
    }

    /**
     * @notice Set required approvals
     */
    function setRequiredApprovals(uint256 _required) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_required > 0, "TreasuryVault: Must be positive");
        requiredApprovals = _required;
    }

    /**
     * @notice Emergency withdrawal (admin only, requires reason)
     */
    function emergencyWithdraw(
        address to,
        uint256 amount,
        string calldata reason
    ) external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
        require(to != address(0), "TreasuryVault: Invalid recipient");
        require(amount > 0, "TreasuryVault: Invalid amount");
        
        omkToken.safeTransfer(to, amount);
        
        emit EmergencyWithdrawal(to, amount, reason);
    }

    // ============ VIEW FUNCTIONS ============

    /**
     * @notice Get proposal details
     */
    function getProposal(uint256 proposalId) external view returns (
        address proposer,
        Category category,
        uint256 amount,
        address recipient,
        string memory description,
        uint256 createdAt,
        uint256 executedAt,
        uint256 approvals,
        bool executed,
        bool rejected
    ) {
        Proposal storage prop = proposals[proposalId];
        return (
            prop.proposer,
            prop.category,
            prop.amount,
            prop.recipient,
            prop.description,
            prop.createdAt,
            prop.executedAt,
            prop.approvals,
            prop.executed,
            prop.rejected
        );
    }

    /**
     * @notice Check if address has approved proposal
     */
    function hasApproved(uint256 proposalId, address approver) external view returns (bool) {
        return proposals[proposalId].hasApproved[approver];
    }

    /**
     * @notice Get current month's spending for category
     */
    function getCurrentMonthSpending(Category category) external view returns (uint256) {
        uint256 currentMonth = block.timestamp / 30 days;
        return monthlySpent[category][currentMonth];
    }

    /**
     * @notice Get treasury balance
     */
    function getBalance() external view returns (uint256) {
        return omkToken.balanceOf(address(this));
    }

    /**
     * @notice Get all category stats
     */
    function getCategoryStats() external view returns (
        uint256[6] memory spent,
        uint256[6] memory limits
    ) {
        for (uint256 i = 0; i < 6; i++) {
            spent[i] = categorySpent[Category(i)];
            limits[i] = monthlyLimits[Category(i)];
        }
    }

    // ============ PAUSE FUNCTIONS ============

    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
}
