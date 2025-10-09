// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title LiquiditySentinel
 * @dev Monitors DEX pool health and triggers Queen AI for liquidity operations
 * 
 * Queen AI uses this to:
 * - Monitor pool ratios
 * - Detect low liquidity
 * - Track slippage
 * - Trigger automated liquidity injections
 */
contract LiquiditySentinel is AccessControl, Pausable {
    
    // Roles
    bytes32 public constant MONITOR_ROLE = keccak256("MONITOR_ROLE"); // Queen AI
    bytes32 public constant POOL_MANAGER_ROLE = keccak256("POOL_MANAGER_ROLE"); // Queen AI

    // Pool tracking
    struct PoolMetrics {
        address poolAddress;
        uint256 omkReserve;
        uint256 pairReserve;
        uint256 liquidity;
        uint256 lastUpdate;
        uint256 targetRatio; // Desired OMK:Pair ratio (scaled by 1e18)
        uint256 minLiquidity; // Minimum liquidity threshold
        bool isActive;
        bool needsAttention; // Flag set by Queen AI
    }
    
    mapping(address => PoolMetrics) public pools;
    address[] public poolList;
    
    // Health thresholds
    uint256 public constant CRITICAL_THRESHOLD = 80; // 80% deviation = critical
    uint256 public constant WARNING_THRESHOLD = 50; // 50% deviation = warning
    uint256 public constant SLIPPAGE_THRESHOLD = 5; // 5% max acceptable slippage
    
    // Events
    event PoolRegistered(address indexed pool, uint256 targetRatio, uint256 minLiquidity);
    event PoolUpdated(address indexed pool, uint256 omkReserve, uint256 pairReserve, uint256 liquidity);
    event PoolHealthAlert(address indexed pool, string alertType, uint256 severity);
    event PoolFlagged(address indexed pool, string reason);
    event LiquidityActionRequired(address indexed pool, uint256 recommendedAmount);

    constructor(address _admin, address _queenMonitor) {
        require(_admin != address(0), "LiquiditySentinel: Invalid admin");
        require(_queenMonitor != address(0), "LiquiditySentinel: Invalid queen");
        
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(MONITOR_ROLE, _queenMonitor);
        _grantRole(POOL_MANAGER_ROLE, _queenMonitor);
    }

    // ============ POOL MANAGEMENT ============

    /**
     * @notice Register a new pool for monitoring
     * @param poolAddress Address of the DEX pool
     * @param targetRatio Desired OMK:Pair ratio (scaled by 1e18)
     * @param minLiquidity Minimum liquidity threshold
     */
    function registerPool(
        address poolAddress,
        uint256 targetRatio,
        uint256 minLiquidity
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(poolAddress != address(0), "LiquiditySentinel: Invalid pool");
        require(!pools[poolAddress].isActive, "LiquiditySentinel: Pool already registered");
        
        pools[poolAddress] = PoolMetrics({
            poolAddress: poolAddress,
            omkReserve: 0,
            pairReserve: 0,
            liquidity: 0,
            lastUpdate: block.timestamp,
            targetRatio: targetRatio,
            minLiquidity: minLiquidity,
            isActive: true,
            needsAttention: false
        });
        
        poolList.push(poolAddress);
        
        emit PoolRegistered(poolAddress, targetRatio, minLiquidity);
    }

    /**
     * @notice Update pool metrics (called by Queen AI or oracle)
     * @param poolAddress Address of the pool
     * @param omkReserve Current OMK reserve
     * @param pairReserve Current pair token reserve
     * @param liquidity Total liquidity
     */
    function updatePoolMetrics(
        address poolAddress,
        uint256 omkReserve,
        uint256 pairReserve,
        uint256 liquidity
    ) external onlyRole(MONITOR_ROLE) {
        require(pools[poolAddress].isActive, "LiquiditySentinel: Pool not registered");
        
        PoolMetrics storage pool = pools[poolAddress];
        pool.omkReserve = omkReserve;
        pool.pairReserve = pairReserve;
        pool.liquidity = liquidity;
        pool.lastUpdate = block.timestamp;
        
        // Analyze health and emit alerts if needed
        _analyzePoolHealth(poolAddress);
        
        emit PoolUpdated(poolAddress, omkReserve, pairReserve, liquidity);
    }

    /**
     * @notice Flag pool for attention
     * @param poolAddress Address of the pool
     * @param reason Reason for flagging
     */
    function flagPool(address poolAddress, string calldata reason) 
        external 
        onlyRole(POOL_MANAGER_ROLE) 
    {
        require(pools[poolAddress].isActive, "LiquiditySentinel: Pool not registered");
        
        pools[poolAddress].needsAttention = true;
        
        emit PoolFlagged(poolAddress, reason);
    }

    /**
     * @notice Clear pool flag after action taken
     * @param poolAddress Address of the pool
     */
    function clearPoolFlag(address poolAddress) 
        external 
        onlyRole(POOL_MANAGER_ROLE) 
    {
        require(pools[poolAddress].isActive, "LiquiditySentinel: Pool not registered");
        
        pools[poolAddress].needsAttention = false;
    }

    // ============ VIEW FUNCTIONS ============

    /**
     * @notice Get pool health score (0-100, 100 = perfect)
     * @param poolAddress Address of the pool
     */
    function getPoolHealth(address poolAddress) external view returns (uint256 healthScore) {
        require(pools[poolAddress].isActive, "LiquiditySentinel: Pool not registered");
        
        PoolMetrics memory pool = pools[poolAddress];
        
        // Calculate ratio deviation
        uint256 currentRatio = (pool.omkReserve * 1e18) / pool.pairReserve;
        uint256 deviation = _calculateDeviation(currentRatio, pool.targetRatio);
        
        // Check liquidity
        bool liquidityOK = pool.liquidity >= pool.minLiquidity;
        
        // Calculate health score
        if (deviation < WARNING_THRESHOLD && liquidityOK) {
            healthScore = 100 - deviation / 2; // 100-75 range
        } else if (deviation < CRITICAL_THRESHOLD && liquidityOK) {
            healthScore = 75 - deviation / 4; // 75-50 range
        } else {
            healthScore = deviation < 100 ? 50 - deviation / 4 : 0; // 50-0 range
        }
        
        return healthScore;
    }

    /**
     * @notice Get all pools needing attention
     */
    function getPoolsNeedingAttention() external view returns (address[] memory) {
        uint256 count = 0;
        
        // Count flagged pools
        for (uint256 i = 0; i < poolList.length; i++) {
            if (pools[poolList[i]].needsAttention && pools[poolList[i]].isActive) {
                count++;
            }
        }
        
        // Build array
        address[] memory flaggedPools = new address[](count);
        uint256 index = 0;
        
        for (uint256 i = 0; i < poolList.length; i++) {
            if (pools[poolList[i]].needsAttention && pools[poolList[i]].isActive) {
                flaggedPools[index] = poolList[i];
                index++;
            }
        }
        
        return flaggedPools;
    }

    /**
     * @notice Get recommended liquidity injection amount
     * @param poolAddress Address of the pool
     */
    function getRecommendedLiquidityAmount(address poolAddress) 
        external 
        view 
        returns (uint256 omkAmount, uint256 pairAmount) 
    {
        require(pools[poolAddress].isActive, "LiquiditySentinel: Pool not registered");
        
        PoolMetrics memory pool = pools[poolAddress];
        
        // Calculate how much needed to reach target
        uint256 targetOmkReserve = (pool.pairReserve * pool.targetRatio) / 1e18;
        
        if (targetOmkReserve > pool.omkReserve) {
            omkAmount = targetOmkReserve - pool.omkReserve;
            // Calculate proportional pair amount
            pairAmount = (omkAmount * pool.pairReserve) / pool.omkReserve;
        } else {
            omkAmount = 0;
            pairAmount = 0;
        }
        
        return (omkAmount, pairAmount);
    }

    /**
     * @notice Calculate estimated slippage for trade
     * @param poolAddress Address of the pool
     * @param amountIn Amount of tokens to trade
     * @param isOMKIn True if trading OMK for pair, false otherwise
     */
    function calculateSlippage(
        address poolAddress,
        uint256 amountIn,
        bool isOMKIn
    ) external view returns (uint256 slippagePercent) {
        require(pools[poolAddress].isActive, "LiquiditySentinel: Pool not registered");
        
        PoolMetrics memory pool = pools[poolAddress];
        
        uint256 reserveIn = isOMKIn ? pool.omkReserve : pool.pairReserve;
        uint256 reserveOut = isOMKIn ? pool.pairReserve : pool.omkReserve;
        
        // Constant product formula: amountOut = (amountIn * reserveOut) / (reserveIn + amountIn)
        uint256 amountOut = (amountIn * reserveOut) / (reserveIn + amountIn);
        
        // Ideal rate (no slippage)
        uint256 idealOut = (amountIn * reserveOut) / reserveIn;
        
        // Slippage percentage
        slippagePercent = ((idealOut - amountOut) * 100) / idealOut;
        
        return slippagePercent;
    }

    /**
     * @notice Get all active pools
     */
    function getAllPools() external view returns (address[] memory) {
        uint256 activeCount = 0;
        
        for (uint256 i = 0; i < poolList.length; i++) {
            if (pools[poolList[i]].isActive) {
                activeCount++;
            }
        }
        
        address[] memory activePools = new address[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 0; i < poolList.length; i++) {
            if (pools[poolList[i]].isActive) {
                activePools[index] = poolList[i];
                index++;
            }
        }
        
        return activePools;
    }

    // ============ INTERNAL FUNCTIONS ============

    /**
     * @dev Analyze pool health and emit alerts
     */
    function _analyzePoolHealth(address poolAddress) internal {
        PoolMetrics memory pool = pools[poolAddress];
        
        // Check ratio deviation
        uint256 currentRatio = (pool.omkReserve * 1e18) / pool.pairReserve;
        uint256 deviation = _calculateDeviation(currentRatio, pool.targetRatio);
        
        if (deviation >= CRITICAL_THRESHOLD) {
            emit PoolHealthAlert(poolAddress, "CRITICAL_DEVIATION", deviation);
            
            // Calculate recommended action
            (uint256 omkAmount, uint256 pairAmount) = this.getRecommendedLiquidityAmount(poolAddress);
            if (omkAmount > 0) {
                emit LiquidityActionRequired(poolAddress, omkAmount);
            }
        } else if (deviation >= WARNING_THRESHOLD) {
            emit PoolHealthAlert(poolAddress, "WARNING_DEVIATION", deviation);
        }
        
        // Check liquidity
        if (pool.liquidity < pool.minLiquidity) {
            emit PoolHealthAlert(poolAddress, "LOW_LIQUIDITY", pool.liquidity);
        }
    }

    /**
     * @dev Calculate percentage deviation between two values
     */
    function _calculateDeviation(uint256 value, uint256 target) internal pure returns (uint256) {
        if (value > target) {
            return ((value - target) * 100) / target;
        } else {
            return ((target - value) * 100) / target;
        }
    }

    // ============ ADMIN FUNCTIONS ============

    /**
     * @notice Deactivate a pool
     */
    function deactivatePool(address poolAddress) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(pools[poolAddress].isActive, "LiquiditySentinel: Pool not active");
        pools[poolAddress].isActive = false;
    }

    /**
     * @notice Update pool thresholds
     */
    function updatePoolThresholds(
        address poolAddress,
        uint256 newTargetRatio,
        uint256 newMinLiquidity
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(pools[poolAddress].isActive, "LiquiditySentinel: Pool not registered");
        
        pools[poolAddress].targetRatio = newTargetRatio;
        pools[poolAddress].minLiquidity = newMinLiquidity;
    }

    /**
     * @notice Pause monitoring
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    /**
     * @notice Unpause monitoring
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
}
