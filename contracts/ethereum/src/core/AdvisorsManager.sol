// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../utils/TokenVesting.sol";

/**
 * @title AdvisorsManager
 * @dev Dynamic management of advisor token allocations
 * 
 * Features:
 * - Admin can add advisors at any time
 * - Split 20M across multiple advisors (5-10+ wallets)
 * - Each advisor gets individual vesting: 12m cliff + 18m linear
 * - Admin can allocate different amounts per advisor
 * - Queen AI can propose, Admin approves
 * - Track total allocated vs available
 */
contract AdvisorsManager is AccessControl, Pausable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    bytes32 public constant ADVISOR_MANAGER_ROLE = keccak256("ADVISOR_MANAGER_ROLE");
    bytes32 public constant QUEEN_ROLE = keccak256("QUEEN_ROLE");

    IERC20 public immutable omkToken;

    // Total advisor pool
    uint256 public constant TOTAL_ADVISORS_POOL = 40_000_000 * 10**18; // 40M OMK
    
    // Vesting parameters (same for all advisors)
    uint256 public constant CLIFF_DURATION = 12; // 12 months
    uint256 public constant VESTING_DURATION = 30; // 30 months total (12 cliff + 18 linear)

    struct Advisor {
        address wallet;
        uint256 allocation; // Amount allocated to this advisor
        address vestingContract; // Individual TokenVesting contract
        uint256 addedAt;
        bool active;
        string role; // e.g., "Marketing Advisor", "Tech Advisor"
    }

    // Storage
    uint256 public advisorCount;
    mapping(uint256 => Advisor) public advisors;
    mapping(address => uint256) public walletToAdvisorId;
    mapping(address => bool) public isAdvisor;

    // Tracking
    uint256 public totalAllocated;
    uint256 public availablePool;

    // Proposal system (Queen proposes, Admin approves)
    struct AdvisorProposal {
        uint256 proposalId;
        address proposer;
        address advisorWallet;
        uint256 allocation;
        string role;
        uint256 createdAt;
        bool approved;
        bool rejected;
    }

    uint256 public proposalCount;
    mapping(uint256 => AdvisorProposal) public proposals;

    // Events
    event AdvisorProposed(
        uint256 indexed proposalId,
        address indexed proposer,
        address indexed advisorWallet,
        uint256 allocation,
        string role
    );
    event ProposalApproved(uint256 indexed proposalId, uint256 indexed advisorId);
    event ProposalRejected(uint256 indexed proposalId, string reason);
    event AdvisorAdded(
        uint256 indexed advisorId,
        address indexed wallet,
        uint256 allocation,
        address vestingContract
    );
    event AdvisorRemoved(uint256 indexed advisorId, string reason);
    event TokensReleased(uint256 indexed advisorId, address indexed wallet, uint256 amount);
    event PoolFunded(uint256 amount);

    constructor(
        address _omkToken,
        address _admin,
        address _queen
    ) {
        require(_omkToken != address(0), "AdvisorsManager: Invalid token");
        require(_admin != address(0), "AdvisorsManager: Invalid admin");
        require(_queen != address(0), "AdvisorsManager: Invalid queen");

        omkToken = IERC20(_omkToken);
        availablePool = TOTAL_ADVISORS_POOL;

        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(ADVISOR_MANAGER_ROLE, _admin);
        _grantRole(QUEEN_ROLE, _queen);
    }

    // ============ PROPOSAL SYSTEM ============

    /**
     * @notice Propose new advisor (Queen or Admin)
     */
    function proposeAdvisor(
        address advisorWallet,
        uint256 allocation,
        string calldata role
    ) external returns (uint256) {
        require(
            hasRole(QUEEN_ROLE, msg.sender) || hasRole(ADVISOR_MANAGER_ROLE, msg.sender),
            "AdvisorsManager: Not authorized"
        );
        require(advisorWallet != address(0), "AdvisorsManager: Invalid wallet");
        require(!isAdvisor[advisorWallet], "AdvisorsManager: Already advisor");
        require(allocation > 0, "AdvisorsManager: Invalid allocation");
        require(allocation <= availablePool, "AdvisorsManager: Exceeds available pool");

        uint256 proposalId = proposalCount++;

        AdvisorProposal storage proposal = proposals[proposalId];
        proposal.proposalId = proposalId;
        proposal.proposer = msg.sender;
        proposal.advisorWallet = advisorWallet;
        proposal.allocation = allocation;
        proposal.role = role;
        proposal.createdAt = block.timestamp;

        emit AdvisorProposed(proposalId, msg.sender, advisorWallet, allocation, role);

        return proposalId;
    }

    /**
     * @notice Approve advisor proposal (Admin only)
     */
    function approveProposal(uint256 proposalId) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
        nonReentrant 
        returns (uint256) 
    {
        AdvisorProposal storage proposal = proposals[proposalId];
        require(!proposal.approved, "AdvisorsManager: Already approved");
        require(!proposal.rejected, "AdvisorsManager: Already rejected");
        require(proposal.allocation <= availablePool, "AdvisorsManager: Insufficient pool");

        proposal.approved = true;

        // Add advisor
        uint256 advisorId = _addAdvisor(
            proposal.advisorWallet,
            proposal.allocation,
            proposal.role
        );

        emit ProposalApproved(proposalId, advisorId);

        return advisorId;
    }

    /**
     * @notice Reject advisor proposal (Admin only)
     */
    function rejectProposal(uint256 proposalId, string calldata reason) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
    {
        AdvisorProposal storage proposal = proposals[proposalId];
        require(!proposal.approved, "AdvisorsManager: Already approved");
        require(!proposal.rejected, "AdvisorsManager: Already rejected");

        proposal.rejected = true;

        emit ProposalRejected(proposalId, reason);
    }

    // ============ DIRECT ADMIN ADD (Bypass proposal) ============

    /**
     * @notice Add advisor directly (Admin only, no proposal needed)
     */
    function addAdvisorDirect(
        address advisorWallet,
        uint256 allocation,
        string calldata role
    ) external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant returns (uint256) {
        require(advisorWallet != address(0), "AdvisorsManager: Invalid wallet");
        require(!isAdvisor[advisorWallet], "AdvisorsManager: Already advisor");
        require(allocation > 0, "AdvisorsManager: Invalid allocation");
        require(allocation <= availablePool, "AdvisorsManager: Exceeds available pool");

        return _addAdvisor(advisorWallet, allocation, role);
    }

    /**
     * @dev Internal function to add advisor
     */
    function _addAdvisor(
        address advisorWallet,
        uint256 allocation,
        string memory role
    ) internal returns (uint256) {
        uint256 advisorId = advisorCount++;

        // Create individual vesting contract for this advisor
        TokenVesting vestingContract = new TokenVesting(address(omkToken), address(this));
        vestingContract.createVestingSchedule(
            advisorWallet,
            allocation,
            CLIFF_DURATION,    // 12 months cliff
            VESTING_DURATION,  // 30 months total (12 cliff + 18 linear)
            false              // cliff then linear
        );

        // Transfer tokens to vesting contract
        omkToken.safeTransfer(address(vestingContract), allocation);

        // Record advisor
        Advisor storage advisor = advisors[advisorId];
        advisor.wallet = advisorWallet;
        advisor.allocation = allocation;
        advisor.vestingContract = address(vestingContract);
        advisor.addedAt = block.timestamp;
        advisor.active = true;
        advisor.role = role;

        walletToAdvisorId[advisorWallet] = advisorId;
        isAdvisor[advisorWallet] = true;

        // Update tracking
        totalAllocated += allocation;
        availablePool -= allocation;

        emit AdvisorAdded(advisorId, advisorWallet, allocation, address(vestingContract));

        return advisorId;
    }

    // ============ VESTING RELEASE ============

    /**
     * @notice Release vested tokens for an advisor
     */
    function releaseAdvisorTokens(uint256 advisorId) external nonReentrant {
        Advisor storage advisor = advisors[advisorId];
        require(advisor.active, "AdvisorsManager: Advisor not active");
        require(
            msg.sender == advisor.wallet || hasRole(ADVISOR_MANAGER_ROLE, msg.sender),
            "AdvisorsManager: Not authorized"
        );

        TokenVesting vesting = TokenVesting(advisor.vestingContract);
        uint256 releasable = vesting.getReleasableAmount(advisor.wallet);
        require(releasable > 0, "AdvisorsManager: Nothing to release");

        vesting.release(advisor.wallet);

        emit TokensReleased(advisorId, advisor.wallet, releasable);
    }

    /**
     * @notice Advisors can claim their own tokens
     */
    function claimMyTokens() external nonReentrant {
        require(isAdvisor[msg.sender], "AdvisorsManager: Not an advisor");
        
        uint256 advisorId = walletToAdvisorId[msg.sender];
        Advisor storage advisor = advisors[advisorId];
        require(advisor.active, "AdvisorsManager: Not active");

        TokenVesting vesting = TokenVesting(advisor.vestingContract);
        uint256 releasable = vesting.getReleasableAmount(msg.sender);
        require(releasable > 0, "AdvisorsManager: Nothing to claim");

        vesting.release(msg.sender);

        emit TokensReleased(advisorId, msg.sender, releasable);
    }

    // ============ ADMIN MANAGEMENT ============

    /**
     * @notice Remove advisor (Admin only, emergency)
     */
    function removeAdvisor(uint256 advisorId, string calldata reason) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
    {
        Advisor storage advisor = advisors[advisorId];
        require(advisor.active, "AdvisorsManager: Already removed");

        advisor.active = false;
        isAdvisor[advisor.wallet] = false;

        emit AdvisorRemoved(advisorId, reason);
    }

    /**
     * @notice Fund the pool (receives 20M from OMKToken)
     */
    function fundPool(uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(amount > 0, "AdvisorsManager: Invalid amount");
        
        omkToken.safeTransferFrom(msg.sender, address(this), amount);
        
        emit PoolFunded(amount);
    }

    // ============ VIEW FUNCTIONS ============

    /**
     * @notice Get advisor details
     */
    function getAdvisor(uint256 advisorId) external view returns (
        address wallet,
        uint256 allocation,
        address vestingContract,
        uint256 addedAt,
        bool active,
        string memory role
    ) {
        Advisor storage advisor = advisors[advisorId];
        return (
            advisor.wallet,
            advisor.allocation,
            advisor.vestingContract,
            advisor.addedAt,
            advisor.active,
            advisor.role
        );
    }

    /**
     * @notice Get advisor vesting info
     */
    function getAdvisorVestingInfo(uint256 advisorId) external view returns (
        uint256 total,
        uint256 released,
        uint256 releasable,
        uint256 vested
    ) {
        Advisor storage advisor = advisors[advisorId];
        require(advisor.active, "AdvisorsManager: Not active");

        TokenVesting vesting = TokenVesting(advisor.vestingContract);
        
        total = advisor.allocation;
        released = vesting.getReleasedAmount(advisor.wallet);
        releasable = vesting.getReleasableAmount(advisor.wallet);
        vested = vesting.getVestedAmount(advisor.wallet);
    }

    /**
     * @notice Get all active advisors
     */
    function getActiveAdvisors() external view returns (uint256[] memory) {
        uint256 activeCount = 0;
        
        // Count active advisors
        for (uint256 i = 0; i < advisorCount; i++) {
            if (advisors[i].active) activeCount++;
        }

        // Build array
        uint256[] memory activeAdvisors = new uint256[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 0; i < advisorCount; i++) {
            if (advisors[i].active) {
                activeAdvisors[index] = i;
                index++;
            }
        }

        return activeAdvisors;
    }

    /**
     * @notice Get pool stats
     */
    function getPoolStats() external view returns (
        uint256 totalPool,
        uint256 allocated,
        uint256 available,
        uint256 activeAdvisorCount
    ) {
        uint256 active = 0;
        for (uint256 i = 0; i < advisorCount; i++) {
            if (advisors[i].active) active++;
        }

        return (
            TOTAL_ADVISORS_POOL,
            totalAllocated,
            availablePool,
            active
        );
    }

    /**
     * @notice Get proposal details
     */
    function getProposal(uint256 proposalId) external view returns (
        address proposer,
        address advisorWallet,
        uint256 allocation,
        string memory role,
        uint256 createdAt,
        bool approved,
        bool rejected
    ) {
        AdvisorProposal storage proposal = proposals[proposalId];
        return (
            proposal.proposer,
            proposal.advisorWallet,
            proposal.allocation,
            proposal.role,
            proposal.createdAt,
            proposal.approved,
            proposal.rejected
        );
    }

    // ============ ADMIN FUNCTIONS ============

    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
}
