// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title SystemDashboard
 * @dev Read-only dashboard aggregating data from all OMK Hive contracts
 * 
 * Provides single view of:
 * - Token distribution
 * - Vesting status
 * - Treasury health
 * - Ecosystem spending
 * - Queen operations
 * - Pool health
 * - Governance status
 */
contract SystemDashboard {
    
    // Contract references
    address public omkToken;
    address public vestingManager;
    address public ecosystemManager;
    address public treasuryVault;
    address public privateSale;
    address public queenController;
    address public liquiditySentinel;
    address public governanceManager;
    address public emergencySystem;
    
    constructor(
        address _omkToken,
        address _vestingManager,
        address _ecosystemManager,
        address _treasuryVault,
        address _privateSale,
        address _queenController,
        address _liquiditySentinel,
        address _governanceManager,
        address _emergencySystem
    ) {
        omkToken = _omkToken;
        vestingManager = _vestingManager;
        ecosystemManager = _ecosystemManager;
        treasuryVault = _treasuryVault;
        privateSale = _privateSale;
        queenController = _queenController;
        liquiditySentinel = _liquiditySentinel;
        governanceManager = _governanceManager;
        emergencySystem = _emergencySystem;
    }

    // ============ SYSTEM OVERVIEW ============

    /**
     * @notice Get complete system health overview
     */
    function getSystemOverview() external view returns (
        uint256 totalSupply,
        uint256 circulatingSupply,
        uint256 lockedTokens,
        bool emergencyActive,
        uint256 activeProposals,
        uint256 queenDailyRemaining
    ) {
        // Total supply
        totalSupply = IERC20(omkToken).totalSupply();
        
        // Get vesting info
        (uint256 foundersLocked, uint256 advisorsLocked, uint256 ecosystemLocked) = _getLockedTokens();
        lockedTokens = foundersLocked + advisorsLocked + ecosystemLocked;
        
        // Circulating = Total - Locked
        circulatingSupply = totalSupply - lockedTokens;
        
        // Emergency status
        (bool shutdown, , , , ) = _getEmergencyStatus();
        emergencyActive = shutdown;
        
        // Active proposals
        activeProposals = _getActiveProposalCount();
        
        // Queen's remaining daily limit
        queenDailyRemaining = _getQueenDailyRemaining();
    }

    /**
     * @notice Get token distribution breakdown
     */
    function getTokenDistribution() external view returns (
        uint256[7] memory distribution
    ) {
        // [0] queenBalance
        // [1] treasuryBalance  
        // [2] ecosystemBalance
        // [3] privateSaleBalance
        // [4] foundersVested
        // [5] advisorsVested
        // [6] circulatingSupply
        
        distribution[0] = _getBalance(_getQueenAddress());
        distribution[1] = _getBalance(treasuryVault);
        distribution[2] = _getBalance(ecosystemManager);
        distribution[3] = _getBalance(privateSale);
        
        (, , uint256 foundersRel, ) = _getFoundersVesting();
        (, , uint256 advisorsRel, ) = _getAdvisorsVesting();
        
        distribution[4] = foundersRel;
        distribution[5] = advisorsRel;
        
        uint256 totalSupply = IERC20(omkToken).totalSupply();
        (uint256 foundersLocked, uint256 advisorsLocked, uint256 ecosystemLocked) = _getLockedTokens();
        distribution[6] = totalSupply - (foundersLocked + advisorsLocked + ecosystemLocked);
    }

    // ============ VESTING STATUS ============

    /**
     * @notice Get all vesting information
     */
    function getAllVestingInfo() external view returns (uint256[9] memory vestingInfo) {
        // [0-2] founders: total, released, releasable
        // [3-5] advisors: total, released, releasable
        // [6-8] ecosystem: total, released, releasable
        
        (uint256 ft, , uint256 fr, uint256 frel) = _getFoundersVesting();
        vestingInfo[0] = ft;
        vestingInfo[1] = fr;
        vestingInfo[2] = frel;
        
        (uint256 at, , uint256 ar, uint256 arel) = _getAdvisorsVesting();
        vestingInfo[3] = at;
        vestingInfo[4] = ar;
        vestingInfo[5] = arel;
        
        (uint256 et, , uint256 er, uint256 erel) = _getEcosystemVesting();
        vestingInfo[6] = et;
        vestingInfo[7] = er;
        vestingInfo[8] = erel;
    }

    // ============ ECOSYSTEM STATUS ============

    /**
     * @notice Get ecosystem spending overview
     */
    function getEcosystemOverview() external view returns (
        uint256[5] memory budgets,
        uint256[5] memory spent,
        uint256[5] memory remaining,
        uint256 totalBudget,
        uint256 totalSpent
    ) {
        (budgets, spent, remaining) = _getEcosystemStats();
        
        for (uint256 i = 0; i < 5; i++) {
            totalBudget += budgets[i];
            totalSpent += spent[i];
        }
    }

    // ============ TREASURY STATUS ============

    /**
     * @notice Get treasury overview
     */
    function getTreasuryOverview() external view returns (
        uint256 balance,
        uint256 pendingProposals,
        uint256 approvedProposals,
        uint256[6] memory categorySpent
    ) {
        balance = _getBalance(treasuryVault);
        
        // Get proposal counts
        uint256 proposalCount = _getTreasuryProposalCount();
        for (uint256 i = 0; i < proposalCount; i++) {
            // Count proposals by status
            // (Would need to call treasury contract methods)
        }
        
        // Get category spending
        (categorySpent, ) = _getTreasuryStats();
    }

    // ============ QUEEN OPERATIONS ============

    /**
     * @notice Get Queen activity summary
     */
    function getQueenActivity() external view returns (
        uint256 totalOperations,
        uint256 dailyTransfersUsed,
        uint256 dailyTransfersRemaining,
        bool rateLimitActive,
        uint256 lastOperationTime
    ) {
        totalOperations = _getQueenOperationCount();
        
        (dailyTransfersUsed, dailyTransfersRemaining, rateLimitActive) = _getQueenTransferStats();
        
        // Get last operation time (would need QueenController method)
        lastOperationTime = block.timestamp; // Placeholder
    }

    // ============ POOL HEALTH ============

    /**
     * @notice Get liquidity pool overview
     */
    function getPoolsOverview() external view returns (
        uint256 totalPools,
        uint256 healthyPools,
        uint256 warningPools,
        uint256 criticalPools
    ) {
        address[] memory pools = _getAllPools();
        totalPools = pools.length;
        
        for (uint256 i = 0; i < pools.length; i++) {
            uint256 health = _getPoolHealth(pools[i]);
            
            if (health >= 75) {
                healthyPools++;
            } else if (health >= 50) {
                warningPools++;
            } else {
                criticalPools++;
            }
        }
    }

    // ============ GOVERNANCE STATUS ============

    /**
     * @notice Get governance overview
     */
    function getGovernanceOverview() external view returns (
        uint256 totalProposals,
        uint256 activeProposals,
        uint256 passedProposals,
        uint256 rejectedProposals,
        uint256 vetoedProposals
    ) {
        totalProposals = _getGovernanceProposalCount();
        
        for (uint256 i = 0; i < totalProposals; i++) {
            (bool isActive, bool hasPassed, , ) = _getProposalStatus(i);
            
            if (isActive) {
                activeProposals++;
            } else if (hasPassed) {
                passedProposals++;
            }
            // Would need to check veto/reject status
        }
    }

    // ============ PRIVATE VIEW HELPERS ============

    function _getBalance(address account) private view returns (uint256) {
        return IERC20(omkToken).balanceOf(account);
    }

    function _getQueenAddress() private view returns (address) {
        (bool success, bytes memory data) = omkToken.staticcall(abi.encodeWithSignature("queenAddress()"));
        if (success) {
            return abi.decode(data, (address));
        }
        return address(0);
    }

    function _getLockedTokens() private view returns (uint256, uint256, uint256) {
        (bool success, bytes memory data) = vestingManager.staticcall(
            abi.encodeWithSignature("getAllVestingInfo()")
        );
        if (success) {
            (, , , uint256 totalLocked) = abi.decode(data, (uint256, uint256, uint256, uint256));
            return (83333333, 6666667, totalLocked); // Placeholder
        }
        return (0, 0, 0);
    }

    function _getFoundersVesting() private view returns (uint256, uint256, uint256, uint256) {
        (bool success, bytes memory data) = vestingManager.staticcall(
            abi.encodeWithSignature("getFoundersVestingInfo()")
        );
        if (success) {
            return abi.decode(data, (uint256, uint256, uint256, uint256));
        }
        return (0, 0, 0, 0);
    }

    function _getAdvisorsVesting() private view returns (uint256, uint256, uint256, uint256) {
        (bool success, bytes memory data) = vestingManager.staticcall(
            abi.encodeWithSignature("getAdvisorsVestingInfo()")
        );
        if (success) {
            return abi.decode(data, (uint256, uint256, uint256, uint256));
        }
        return (0, 0, 0, 0);
    }

    function _getEcosystemVesting() private view returns (uint256, uint256, uint256, uint256) {
        (bool success, bytes memory data) = vestingManager.staticcall(
            abi.encodeWithSignature("getEcosystemVestingInfo()")
        );
        if (success) {
            return abi.decode(data, (uint256, uint256, uint256, uint256));
        }
        return (0, 0, 0, 0);
    }

    function _getEcosystemStats() private view returns (uint256[5] memory, uint256[5] memory, uint256[5] memory) {
        (bool success, bytes memory data) = ecosystemManager.staticcall(
            abi.encodeWithSignature("getEcosystemStats()")
        );
        if (success) {
            return abi.decode(data, (uint256[5], uint256[5], uint256[5]));
        }
        return ([uint256(0), 0, 0, 0, 0], [uint256(0), 0, 0, 0, 0], [uint256(0), 0, 0, 0, 0]);
    }

    function _getTreasuryProposalCount() private view returns (uint256) {
        (bool success, bytes memory data) = treasuryVault.staticcall(
            abi.encodeWithSignature("proposalCount()")
        );
        if (success) {
            return abi.decode(data, (uint256));
        }
        return 0;
    }

    function _getTreasuryStats() private view returns (uint256[6] memory, uint256[6] memory) {
        (bool success, bytes memory data) = treasuryVault.staticcall(
            abi.encodeWithSignature("getCategoryStats()")
        );
        if (success) {
            return abi.decode(data, (uint256[6], uint256[6]));
        }
        return ([uint256(0), 0, 0, 0, 0, 0], [uint256(0), 0, 0, 0, 0, 0]);
    }

    function _getQueenOperationCount() private view returns (uint256) {
        (bool success, bytes memory data) = queenController.staticcall(
            abi.encodeWithSignature("totalOperations()")
        );
        if (success) {
            return abi.decode(data, (uint256));
        }
        return 0;
    }

    function _getQueenTransferStats() private view returns (uint256, uint256, bool) {
        (bool success, bytes memory data) = omkToken.staticcall(
            abi.encodeWithSignature("getQueenTransferStats()")
        );
        if (success) {
            (, uint256 transferred, uint256 remaining, bool active) = abi.decode(data, (uint256, uint256, uint256, bool));
            return (transferred, remaining, active);
        }
        return (0, 0, false);
    }

    function _getQueenDailyRemaining() private view returns (uint256) {
        (, uint256 remaining, ) = _getQueenTransferStats();
        return remaining;
    }

    function _getAllPools() private view returns (address[] memory) {
        (bool success, bytes memory data) = liquiditySentinel.staticcall(
            abi.encodeWithSignature("getAllPools()")
        );
        if (success) {
            return abi.decode(data, (address[]));
        }
        return new address[](0);
    }

    function _getPoolHealth(address pool) private view returns (uint256) {
        (bool success, bytes memory data) = liquiditySentinel.staticcall(
            abi.encodeWithSignature("getPoolHealth(address)", pool)
        );
        if (success) {
            return abi.decode(data, (uint256));
        }
        return 0;
    }

    function _getGovernanceProposalCount() private view returns (uint256) {
        (bool success, bytes memory data) = governanceManager.staticcall(
            abi.encodeWithSignature("proposalCount()")
        );
        if (success) {
            return abi.decode(data, (uint256));
        }
        return 0;
    }

    function _getActiveProposalCount() private view returns (uint256) {
        uint256 total = _getGovernanceProposalCount();
        uint256 active = 0;
        
        for (uint256 i = 0; i < total; i++) {
            (bool isActive, , , ) = _getProposalStatus(i);
            if (isActive) active++;
        }
        
        return active;
    }

    function _getProposalStatus(uint256 proposalId) private view returns (bool, bool, bool, uint256) {
        (bool success, bytes memory data) = governanceManager.staticcall(
            abi.encodeWithSignature("getProposalStatus(uint256)", proposalId)
        );
        if (success) {
            return abi.decode(data, (bool, bool, bool, uint256));
        }
        return (false, false, false, 0);
    }

    function _getEmergencyStatus() private view returns (bool, bool, uint256, uint256, uint256) {
        (bool success, bytes memory data) = emergencySystem.staticcall(
            abi.encodeWithSignature("getEmergencyStatus()")
        );
        if (success) {
            return abi.decode(data, (bool, bool, uint256, uint256, uint256));
        }
        return (false, false, 0, 0, 0);
    }
}
