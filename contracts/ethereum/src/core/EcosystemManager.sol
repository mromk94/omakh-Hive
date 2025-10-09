// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title EcosystemManager
 * @dev Manages entire 100M OMK ecosystem allocation
 * 
 * Categories:
 * - Staking Rewards: 40M (40%)
 * - Airdrops & Campaigns: 25M (25%)
 * - Hackathons & Grants: 15M (15%)
 * - Bug Bounties: 10M (10%)
 * - Liquidity Mining: 10M (10%)
 * 
 * All managed by Queen AI with dynamic allocation
 */
contract EcosystemManager is AccessControl, Pausable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // Roles
    bytes32 public constant REWARDS_MANAGER_ROLE = keccak256("REWARDS_MANAGER_ROLE"); // Queen AI
    bytes32 public constant APY_MANAGER_ROLE = keccak256("APY_MANAGER_ROLE"); // Queen AI

    // OMK Token
    IERC20 public immutable omkToken;
    
    // Ecosystem budget tracking (100M total)
    uint256 public constant TOTAL_ECOSYSTEM = 100_000_000 * 10**18;
    
    // Category budgets (targets, can be adjusted)
    uint256 public stakingBudget = 40_000_000 * 10**18;      // 40M
    uint256 public airdropsBudget = 25_000_000 * 10**18;     // 25M
    uint256 public hackathonsBudget = 15_000_000 * 10**18;   // 15M
    uint256 public bountiesBudget = 10_000_000 * 10**18;     // 10M
    uint256 public liquidityBudget = 10_000_000 * 10**18;    // 10M
    
    // Category spending tracking
    uint256 public stakingSpent;
    uint256 public airdropsSpent;
    uint256 public hackathonsSpent;
    uint256 public bountiesSpent;
    uint256 public liquiditySpent;
    
    // Staking parameters
    uint256 public constant MIN_STAKE = 1_000 * 10**18; // 1,000 OMK minimum
    uint256 public constant BASE_APY = 8; // 8% base APY
    uint256 public constant MAX_APY = 15; // 15% maximum APY
    uint256 public currentAPY = 10; // Current APY (starts at 10%)
    
    // Lock periods (in days) with APY multipliers
    uint256 public constant LOCK_7_DAYS = 7 days;
    uint256 public constant LOCK_30_DAYS = 30 days;
    uint256 public constant LOCK_90_DAYS = 90 days;
    uint256 public constant LOCK_180_DAYS = 180 days;
    
    uint256 public constant MULTIPLIER_7D = 100; // 1.0x (base APY)
    uint256 public constant MULTIPLIER_30D = 110; // 1.1x
    uint256 public constant MULTIPLIER_90D = 125; // 1.25x
    uint256 public constant MULTIPLIER_180D = 150; // 1.5x
    
    // Staking state
    struct Stake {
        uint256 amount;           // Amount staked
        uint256 startTime;        // When stake started
        uint256 lockPeriod;       // Lock duration
        uint256 lastClaimTime;    // Last reward claim
        uint256 stakedAPY;        // APY at time of staking
        uint256 multiplier;       // Lock period multiplier
        bool active;              // Is stake active
    }
    
    mapping(address => Stake[]) public userStakes;
    mapping(address => uint256) public totalStaked; // Per user
    
    uint256 public totalStakedGlobal;
    uint256 public totalRewardsPaid;
    uint256 public rewardsPoolBalance; // Available rewards
    
    // Events
    event Staked(address indexed user, uint256 stakeId, uint256 amount, uint256 lockPeriod, uint256 apy);
    event Unstaked(address indexed user, uint256 stakeId, uint256 amount, uint256 rewards);
    event RewardsClaimed(address indexed user, uint256 stakeId, uint256 rewards);
    event APYUpdated(uint256 oldAPY, uint256 newAPY, address indexed updatedBy);
    event RewardsDeposited(uint256 amount, address indexed depositor);
    event EmergencyWithdraw(address indexed user, uint256 stakeId, uint256 amount, uint256 penalty);
    
    // Ecosystem events
    event AirdropExecuted(address indexed recipient, uint256 amount, string campaign);
    event GrantAwarded(address indexed recipient, uint256 amount, string projectName);
    event BountyPaid(address indexed researcher, uint256 amount, string severity);
    event LiquidityRewardsPaid(address indexed pool, uint256 amount);
    event BudgetReallocated(string fromCategory, string toCategory, uint256 amount);

    constructor(
        address _omkToken,
        address _admin,
        address _queenManager
    ) {
        require(_omkToken != address(0), "StakingManager: Invalid token");
        require(_admin != address(0), "StakingManager: Invalid admin");
        require(_queenManager != address(0), "StakingManager: Invalid queen");

        omkToken = IERC20(_omkToken);
        
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(REWARDS_MANAGER_ROLE, _queenManager);
        _grantRole(APY_MANAGER_ROLE, _queenManager);
    }

    // ============ STAKING FUNCTIONS ============

    /**
     * @notice Stake OMK tokens
     * @param amount Amount to stake
     * @param lockPeriod Lock duration (7/30/90/180 days)
     */
    function stake(uint256 amount, uint256 lockPeriod) external nonReentrant whenNotPaused {
        require(amount >= MIN_STAKE, "StakingManager: Below minimum stake");
        require(_isValidLockPeriod(lockPeriod), "StakingManager: Invalid lock period");
        
        // Transfer tokens from user
        omkToken.safeTransferFrom(msg.sender, address(this), amount);
        
        // Get multiplier for lock period
        uint256 multiplier = _getMultiplier(lockPeriod);
        
        // Create stake
        userStakes[msg.sender].push(Stake({
            amount: amount,
            startTime: block.timestamp,
            lockPeriod: lockPeriod,
            lastClaimTime: block.timestamp,
            stakedAPY: currentAPY,
            multiplier: multiplier,
            active: true
        }));
        
        // Update totals
        totalStaked[msg.sender] += amount;
        totalStakedGlobal += amount;
        
        uint256 stakeId = userStakes[msg.sender].length - 1;
        emit Staked(msg.sender, stakeId, amount, lockPeriod, currentAPY);
    }

    /**
     * @notice Claim rewards from a stake
     * @param stakeId ID of the stake
     */
    function claimRewards(uint256 stakeId) external nonReentrant whenNotPaused {
        require(stakeId < userStakes[msg.sender].length, "StakingManager: Invalid stake ID");
        Stake storage userStake = userStakes[msg.sender][stakeId];
        require(userStake.active, "StakingManager: Stake not active");
        
        uint256 rewards = _calculateRewards(userStake);
        require(rewards > 0, "StakingManager: No rewards to claim");
        require(rewardsPoolBalance >= rewards, "StakingManager: Insufficient rewards pool");
        
        // Update claim time
        userStake.lastClaimTime = block.timestamp;
        
        // Transfer rewards
        rewardsPoolBalance -= rewards;
        totalRewardsPaid += rewards;
        omkToken.safeTransfer(msg.sender, rewards);
        
        emit RewardsClaimed(msg.sender, stakeId, rewards);
    }

    /**
     * @notice Unstake tokens after lock period
     * @param stakeId ID of the stake
     */
    function unstake(uint256 stakeId) external nonReentrant whenNotPaused {
        require(stakeId < userStakes[msg.sender].length, "StakingManager: Invalid stake ID");
        Stake storage userStake = userStakes[msg.sender][stakeId];
        require(userStake.active, "StakingManager: Stake not active");
        require(
            block.timestamp >= userStake.startTime + userStake.lockPeriod,
            "StakingManager: Lock period not ended"
        );
        
        uint256 amount = userStake.amount;
        uint256 rewards = _calculateRewards(userStake);
        
        // Mark as inactive
        userStake.active = false;
        
        // Update totals
        totalStaked[msg.sender] -= amount;
        totalStakedGlobal -= amount;
        
        // Transfer principal + rewards
        uint256 totalAmount = amount + rewards;
        if (rewards > 0 && rewardsPoolBalance >= rewards) {
            rewardsPoolBalance -= rewards;
            totalRewardsPaid += rewards;
        } else {
            totalAmount = amount; // Only return principal if no rewards
        }
        
        omkToken.safeTransfer(msg.sender, totalAmount);
        
        emit Unstaked(msg.sender, stakeId, amount, rewards);
    }

    /**
     * @notice Emergency unstake (with penalty if before lock period)
     * @param stakeId ID of the stake
     */
    function emergencyUnstake(uint256 stakeId) external nonReentrant {
        require(stakeId < userStakes[msg.sender].length, "StakingManager: Invalid stake ID");
        Stake storage userStake = userStakes[msg.sender][stakeId];
        require(userStake.active, "StakingManager: Stake not active");
        
        uint256 amount = userStake.amount;
        uint256 penalty = 0;
        
        // Apply penalty if unstaking early
        if (block.timestamp < userStake.startTime + userStake.lockPeriod) {
            penalty = (amount * 10) / 100; // 10% penalty
            amount -= penalty;
            // Penalty goes to rewards pool
            rewardsPoolBalance += penalty;
        }
        
        // Mark as inactive
        userStake.active = false;
        
        // Update totals
        totalStaked[msg.sender] -= userStake.amount;
        totalStakedGlobal -= userStake.amount;
        
        // Transfer (no rewards on emergency unstake)
        omkToken.safeTransfer(msg.sender, amount);
        
        emit EmergencyWithdraw(msg.sender, stakeId, amount, penalty);
    }

    // ============ QUEEN AI MANAGEMENT ============

    /**
     * @notice Update APY (Queen AI only)
     * @param newAPY New APY percentage (8-15)
     */
    function updateAPY(uint256 newAPY) external onlyRole(APY_MANAGER_ROLE) {
        require(newAPY >= BASE_APY && newAPY <= MAX_APY, "StakingManager: APY out of range");
        
        uint256 oldAPY = currentAPY;
        currentAPY = newAPY;
        
        emit APYUpdated(oldAPY, newAPY, msg.sender);
    }

    /**
     * @notice Deposit rewards (from ecosystem vesting)
     * @param amount Amount of rewards to deposit
     */
    function depositRewards(uint256 amount) external onlyRole(REWARDS_MANAGER_ROLE) {
        require(amount > 0, "StakingManager: Amount must be positive");
        
        omkToken.safeTransferFrom(msg.sender, address(this), amount);
        rewardsPoolBalance += amount;
        
        emit RewardsDeposited(amount, msg.sender);
    }

    // ============ VIEW FUNCTIONS ============

    /**
     * @notice Get user's stake details
     */
    function getUserStake(address user, uint256 stakeId) external view returns (
        uint256 amount,
        uint256 startTime,
        uint256 lockPeriod,
        uint256 pendingRewards,
        uint256 apy,
        bool active,
        bool canUnstake
    ) {
        require(stakeId < userStakes[user].length, "StakingManager: Invalid stake ID");
        Stake memory userStake = userStakes[user][stakeId];
        
        amount = userStake.amount;
        startTime = userStake.startTime;
        lockPeriod = userStake.lockPeriod;
        pendingRewards = _calculateRewards(userStake);
        apy = userStake.stakedAPY;
        active = userStake.active;
        canUnstake = block.timestamp >= userStake.startTime + userStake.lockPeriod;
    }

    /**
     * @notice Get user's total staked amount
     */
    function getUserTotalStaked(address user) external view returns (uint256) {
        return totalStaked[user];
    }

    /**
     * @notice Get number of stakes for user
     */
    function getUserStakeCount(address user) external view returns (uint256) {
        return userStakes[user].length;
    }

    /**
     * @notice Get global staking stats
     */
    function getGlobalStats() external view returns (
        uint256 _totalStaked,
        uint256 _totalRewardsPaid,
        uint256 _rewardsPoolBalance,
        uint256 _currentAPY
    ) {
        return (totalStakedGlobal, totalRewardsPaid, rewardsPoolBalance, currentAPY);
    }

    /**
     * @notice Calculate estimated yearly rewards for amount
     */
    function estimateYearlyRewards(uint256 amount, uint256 lockPeriod) external view returns (uint256) {
        require(_isValidLockPeriod(lockPeriod), "StakingManager: Invalid lock period");
        uint256 multiplier = _getMultiplier(lockPeriod);
        uint256 effectiveAPY = (currentAPY * multiplier) / 100;
        return (amount * effectiveAPY) / 100;
    }

    // ============ INTERNAL FUNCTIONS ============

    /**
     * @dev Calculate rewards for a stake
     */
    function _calculateRewards(Stake memory userStake) internal view returns (uint256) {
        if (!userStake.active) return 0;
        
        uint256 stakingDuration = block.timestamp - userStake.lastClaimTime;
        uint256 effectiveAPY = (userStake.stakedAPY * userStake.multiplier) / 100;
        
        // Calculate rewards: (amount * effectiveAPY * duration) / (365 days * 100)
        uint256 rewards = (userStake.amount * effectiveAPY * stakingDuration) / (365 days * 100);
        
        return rewards;
    }

    /**
     * @dev Check if lock period is valid
     */
    function _isValidLockPeriod(uint256 lockPeriod) internal pure returns (bool) {
        return lockPeriod == LOCK_7_DAYS ||
               lockPeriod == LOCK_30_DAYS ||
               lockPeriod == LOCK_90_DAYS ||
               lockPeriod == LOCK_180_DAYS;
    }

    /**
     * @dev Get multiplier for lock period
     */
    function _getMultiplier(uint256 lockPeriod) internal pure returns (uint256) {
        if (lockPeriod == LOCK_7_DAYS) return MULTIPLIER_7D;
        if (lockPeriod == LOCK_30_DAYS) return MULTIPLIER_30D;
        if (lockPeriod == LOCK_90_DAYS) return MULTIPLIER_90D;
        if (lockPeriod == LOCK_180_DAYS) return MULTIPLIER_180D;
        revert("StakingManager: Invalid lock period");
    }

    // ============ ECOSYSTEM FUNCTIONS ============

    /**
     * @notice Execute airdrop to recipients (Queen AI)
     * @param recipients Array of recipient addresses
     * @param amounts Array of amounts
     * @param campaign Campaign name
     */
    function executeAirdrop(
        address[] calldata recipients,
        uint256[] calldata amounts,
        string calldata campaign
    ) external onlyRole(REWARDS_MANAGER_ROLE) nonReentrant {
        require(recipients.length == amounts.length, "EcosystemManager: Length mismatch");
        
        uint256 total = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            total += amounts[i];
        }
        
        require(airdropsSpent + total <= airdropsBudget, "EcosystemManager: Airdrops budget exceeded");
        require(omkToken.balanceOf(address(this)) >= total, "EcosystemManager: Insufficient balance");
        
        // Transfer to each recipient
        for (uint256 i = 0; i < recipients.length; i++) {
            omkToken.safeTransfer(recipients[i], amounts[i]);
            emit AirdropExecuted(recipients[i], amounts[i], campaign);
        }
        
        airdropsSpent += total;
    }

    /**
     * @notice Award grant to project (Queen AI)
     * @param recipient Address of grant recipient
     * @param amount Amount of OMK
     * @param projectName Name of the project
     */
    function awardGrant(
        address recipient,
        uint256 amount,
        string calldata projectName
    ) external onlyRole(REWARDS_MANAGER_ROLE) nonReentrant {
        require(hackathonsSpent + amount <= hackathonsBudget, "EcosystemManager: Hackathons budget exceeded");
        require(omkToken.balanceOf(address(this)) >= amount, "EcosystemManager: Insufficient balance");
        
        omkToken.safeTransfer(recipient, amount);
        hackathonsSpent += amount;
        
        emit GrantAwarded(recipient, amount, projectName);
    }

    /**
     * @notice Pay bug bounty (Queen AI)
     * @param researcher Address of security researcher
     * @param amount Amount of OMK
     * @param severity Severity level (CRITICAL, HIGH, etc.)
     */
    function payBounty(
        address researcher,
        uint256 amount,
        string calldata severity
    ) external onlyRole(REWARDS_MANAGER_ROLE) nonReentrant {
        require(bountiesSpent + amount <= bountiesBudget, "EcosystemManager: Bounties budget exceeded");
        require(omkToken.balanceOf(address(this)) >= amount, "EcosystemManager: Insufficient balance");
        
        omkToken.safeTransfer(researcher, amount);
        bountiesSpent += amount;
        
        emit BountyPaid(researcher, amount, severity);
    }

    /**
     * @notice Fund liquidity mining rewards (Queen AI)
     * @param pool Address of the liquidity pool/farm
     * @param amount Amount of OMK
     */
    function fundLiquidityRewards(
        address pool,
        uint256 amount
    ) external onlyRole(REWARDS_MANAGER_ROLE) nonReentrant {
        require(liquiditySpent + amount <= liquidityBudget, "EcosystemManager: Liquidity budget exceeded");
        require(omkToken.balanceOf(address(this)) >= amount, "EcosystemManager: Insufficient balance");
        
        omkToken.safeTransfer(pool, amount);
        liquiditySpent += amount;
        
        emit LiquidityRewardsPaid(pool, amount);
    }

    /**
     * @notice Reallocate budget between categories (Admin only)
     * @param fromCategory 0=staking, 1=airdrops, 2=hackathons, 3=bounties, 4=liquidity
     * @param toCategory Same indices as above
     * @param amount Amount to reallocate
     */
    function reallocateBudget(
        uint8 fromCategory,
        uint8 toCategory,
        uint256 amount
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(fromCategory < 5 && toCategory < 5, "EcosystemManager: Invalid category");
        require(fromCategory != toCategory, "EcosystemManager: Same category");
        
        // Deduct from source
        if (fromCategory == 0) {
            require(stakingBudget >= amount, "EcosystemManager: Insufficient budget");
            stakingBudget -= amount;
        } else if (fromCategory == 1) {
            require(airdropsBudget >= amount, "EcosystemManager: Insufficient budget");
            airdropsBudget -= amount;
        } else if (fromCategory == 2) {
            require(hackathonsBudget >= amount, "EcosystemManager: Insufficient budget");
            hackathonsBudget -= amount;
        } else if (fromCategory == 3) {
            require(bountiesBudget >= amount, "EcosystemManager: Insufficient budget");
            bountiesBudget -= amount;
        } else {
            require(liquidityBudget >= amount, "EcosystemManager: Insufficient budget");
            liquidityBudget -= amount;
        }
        
        // Add to destination
        if (toCategory == 0) {
            stakingBudget += amount;
        } else if (toCategory == 1) {
            airdropsBudget += amount;
        } else if (toCategory == 2) {
            hackathonsBudget += amount;
        } else if (toCategory == 3) {
            bountiesBudget += amount;
        } else {
            liquidityBudget += amount;
        }
        
        string[5] memory categories = ["staking", "airdrops", "hackathons", "bounties", "liquidity"];
        emit BudgetReallocated(categories[fromCategory], categories[toCategory], amount);
    }

    /**
     * @notice Get ecosystem budget stats
     */
    function getEcosystemStats() external view returns (
        uint256[5] memory budgets,
        uint256[5] memory spent,
        uint256[5] memory remaining
    ) {
        budgets = [stakingBudget, airdropsBudget, hackathonsBudget, bountiesBudget, liquidityBudget];
        spent = [stakingSpent, airdropsSpent, hackathonsSpent, bountiesSpent, liquiditySpent];
        remaining = [
            stakingBudget - stakingSpent,
            airdropsBudget - airdropsSpent,
            hackathonsBudget - hackathonsSpent,
            bountiesBudget - bountiesSpent,
            liquidityBudget - liquiditySpent
        ];
    }

    // ============ ADMIN FUNCTIONS ============

    /**
     * @notice Pause staking
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    /**
     * @notice Unpause staking
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @notice Emergency withdraw stuck tokens
     */
    function emergencyWithdrawAdmin(address token, uint256 amount) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
    {
        IERC20(token).safeTransfer(msg.sender, amount);
    }
}
