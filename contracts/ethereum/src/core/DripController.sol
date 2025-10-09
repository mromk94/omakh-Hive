// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title DripController
 * @dev Automated time-based token release for liquidity management
 * 
 * Features:
 * - Daily drip releases from reserve pool
 * - 70% ETH / 30% SOL allocation split
 * - Chainlink Automation compatible
 * - Emergency pause functionality
 * - Reserve pool management (10M OMK)
 */
contract DripController is AccessControl, Pausable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    bytes32 public constant QUEEN_ROLE = keccak256("QUEEN_ROLE");
    bytes32 public constant DRIP_MANAGER_ROLE = keccak256("DRIP_MANAGER_ROLE");

    IERC20 public immutable omkToken;

    // Drip configuration
    uint256 public constant RESERVE_POOL = 10_000_000 * 10**18; // 10M OMK
    uint256 public constant ETH_ALLOCATION_PCT = 70; // 70%
    uint256 public constant SOL_ALLOCATION_PCT = 30; // 30%
    uint256 public constant DRIP_INTERVAL = 1 days;

    // Allocation targets
    address public ethLiquidityPool;
    address public solBridgeVault; // For cross-chain to Solana

    // Drip tracking
    uint256 public dailyDripAmount;
    uint256 public lastDripTimestamp;
    uint256 public totalDripped;
    uint256 public reserveBalance;

    // Emergency reserve
    uint256 public constant MIN_RESERVE = 1_000_000 * 10**18; // 1M minimum

    // Drip history
    struct DripEvent {
        uint256 timestamp;
        uint256 amount;
        uint256 ethAmount;
        uint256 solAmount;
    }

    DripEvent[] public dripHistory;

    // Events
    event DripExecuted(
        uint256 indexed timestamp,
        uint256 totalAmount,
        uint256 ethAmount,
        uint256 solAmount
    );
    event DripAmountUpdated(uint256 oldAmount, uint256 newAmount);
    event ReserveFunded(uint256 amount, uint256 newBalance);
    event EmergencyWithdrawal(address indexed to, uint256 amount);
    event AllocationTargetsUpdated(address ethPool, address solVault);

    constructor(
        address _omkToken,
        address _admin,
        address _queen,
        address _ethLiquidityPool,
        address _solBridgeVault,
        uint256 _dailyDripAmount
    ) {
        require(_omkToken != address(0), "DripController: Invalid token");
        require(_ethLiquidityPool != address(0), "DripController: Invalid ETH pool");
        require(_solBridgeVault != address(0), "DripController: Invalid SOL vault");

        omkToken = IERC20(_omkToken);
        ethLiquidityPool = _ethLiquidityPool;
        solBridgeVault = _solBridgeVault;
        dailyDripAmount = _dailyDripAmount;
        lastDripTimestamp = block.timestamp;

        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(QUEEN_ROLE, _queen);
        _grantRole(DRIP_MANAGER_ROLE, _queen);
    }

    // ============ DRIP EXECUTION ============

    /**
     * @notice Execute daily drip (Chainlink Automation compatible)
     */
    function executeDrip() external onlyRole(DRIP_MANAGER_ROLE) nonReentrant whenNotPaused {
        require(canExecuteDrip(), "DripController: Not ready for drip");
        require(reserveBalance >= dailyDripAmount, "DripController: Insufficient reserve");

        uint256 ethAmount = (dailyDripAmount * ETH_ALLOCATION_PCT) / 100;
        uint256 solAmount = dailyDripAmount - ethAmount;

        // Transfer to respective pools
        omkToken.safeTransfer(ethLiquidityPool, ethAmount);
        omkToken.safeTransfer(solBridgeVault, solAmount);

        // Update state
        reserveBalance -= dailyDripAmount;
        totalDripped += dailyDripAmount;
        lastDripTimestamp = block.timestamp;

        // Record history
        dripHistory.push(DripEvent({
            timestamp: block.timestamp,
            amount: dailyDripAmount,
            ethAmount: ethAmount,
            solAmount: solAmount
        }));

        emit DripExecuted(block.timestamp, dailyDripAmount, ethAmount, solAmount);
    }

    /**
     * @notice Check if drip can be executed
     */
    function canExecuteDrip() public view returns (bool) {
        return block.timestamp >= lastDripTimestamp + DRIP_INTERVAL &&
               reserveBalance >= dailyDripAmount;
    }

    /**
     * @notice Get time until next drip
     */
    function timeUntilNextDrip() external view returns (uint256) {
        uint256 nextDripTime = lastDripTimestamp + DRIP_INTERVAL;
        if (block.timestamp >= nextDripTime) {
            return 0;
        }
        return nextDripTime - block.timestamp;
    }

    // ============ RESERVE MANAGEMENT ============

    /**
     * @notice Fund reserve pool
     */
    function fundReserve(uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(amount > 0, "DripController: Invalid amount");
        
        omkToken.safeTransferFrom(msg.sender, address(this), amount);
        reserveBalance += amount;

        emit ReserveFunded(amount, reserveBalance);
    }

    /**
     * @notice Update daily drip amount
     */
    function setDailyDripAmount(uint256 newAmount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(newAmount > 0, "DripController: Invalid amount");
        require(newAmount <= reserveBalance / 30, "DripController: Amount too high"); // Max 30 days runway

        uint256 oldAmount = dailyDripAmount;
        dailyDripAmount = newAmount;

        emit DripAmountUpdated(oldAmount, newAmount);
    }

    /**
     * @notice Update allocation targets
     */
    function setAllocationTargets(
        address _ethLiquidityPool,
        address _solBridgeVault
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_ethLiquidityPool != address(0), "DripController: Invalid ETH pool");
        require(_solBridgeVault != address(0), "DripController: Invalid SOL vault");

        ethLiquidityPool = _ethLiquidityPool;
        solBridgeVault = _solBridgeVault;

        emit AllocationTargetsUpdated(_ethLiquidityPool, _solBridgeVault);
    }

    // ============ EMERGENCY FUNCTIONS ============

    /**
     * @notice Emergency withdrawal (admin only)
     */
    function emergencyWithdraw(address to, uint256 amount) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
        nonReentrant 
    {
        require(to != address(0), "DripController: Invalid address");
        require(amount > 0 && amount <= reserveBalance, "DripController: Invalid amount");
        require(reserveBalance - amount >= MIN_RESERVE, "DripController: Must keep minimum reserve");

        omkToken.safeTransfer(to, amount);
        reserveBalance -= amount;

        emit EmergencyWithdrawal(to, amount);
    }

    /**
     * @notice Pause drip operations
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    /**
     * @notice Unpause drip operations
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    // ============ VIEW FUNCTIONS ============

    /**
     * @notice Get drip stats
     */
    function getDripStats() external view returns (
        uint256 _dailyDripAmount,
        uint256 _lastDripTimestamp,
        uint256 _totalDripped,
        uint256 _reserveBalance,
        uint256 _daysRemaining,
        bool _canDrip
    ) {
        _dailyDripAmount = dailyDripAmount;
        _lastDripTimestamp = lastDripTimestamp;
        _totalDripped = totalDripped;
        _reserveBalance = reserveBalance;
        _daysRemaining = dailyDripAmount > 0 ? reserveBalance / dailyDripAmount : 0;
        _canDrip = canExecuteDrip();
    }

    /**
     * @notice Get allocation breakdown
     */
    function getAllocationBreakdown(uint256 amount) external pure returns (
        uint256 ethAmount,
        uint256 solAmount
    ) {
        ethAmount = (amount * ETH_ALLOCATION_PCT) / 100;
        solAmount = amount - ethAmount;
    }

    /**
     * @notice Get drip history count
     */
    function getDripHistoryCount() external view returns (uint256) {
        return dripHistory.length;
    }

    /**
     * @notice Get recent drips
     */
    function getRecentDrips(uint256 count) external view returns (DripEvent[] memory) {
        uint256 total = dripHistory.length;
        if (total == 0 || count == 0) {
            return new DripEvent[](0);
        }

        uint256 returnCount = count > total ? total : count;
        DripEvent[] memory recentDrips = new DripEvent[](returnCount);

        for (uint256 i = 0; i < returnCount; i++) {
            recentDrips[i] = dripHistory[total - returnCount + i];
        }

        return recentDrips;
    }

    /**
     * @notice Get current reserve health
     */
    function getReserveHealth() external view returns (
        uint256 currentBalance,
        uint256 minimumRequired,
        uint256 healthPercentage,
        bool isHealthy
    ) {
        currentBalance = reserveBalance;
        minimumRequired = MIN_RESERVE;
        healthPercentage = (reserveBalance * 100) / RESERVE_POOL;
        isHealthy = reserveBalance >= minimumRequired;
    }
}
