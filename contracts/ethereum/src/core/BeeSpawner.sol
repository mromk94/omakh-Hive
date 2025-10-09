// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title BeeSpawner
 * @dev Registry and lifecycle manager for Queen AI's specialized bee agents
 * 
 * Bee Types:
 * - MathsBee: Mathematical analysis, statistical modeling
 * - SecurityBee: Smart contract auditing, vulnerability detection
 * - BlockchainBee: On-chain data analysis, transaction monitoring
 * - DataBee: Off-chain data aggregation, API integration
 * - LogicBee: Decision trees, logical reasoning
 * - PatternBee: Pattern recognition, anomaly detection
 */
contract BeeSpawner is AccessControl {
    
    bytes32 public constant QUEEN_ROLE = keccak256("QUEEN_ROLE");
    bytes32 public constant BEE_MANAGER_ROLE = keccak256("BEE_MANAGER_ROLE");

    enum BeeType {
        MATHS_BEE,      // Mathematical analysis
        SECURITY_BEE,   // Security & auditing
        BLOCKCHAIN_BEE, // Blockchain data
        DATA_BEE,       // Data aggregation
        LOGIC_BEE,      // Logical reasoning
        PATTERN_BEE     // Pattern recognition
    }

    enum BeeStatus {
        INACTIVE,    // Not yet activated
        ACTIVE,      // Currently operational
        PAUSED,      // Temporarily disabled
        RETIRED      // Permanently disabled
    }

    struct Bee {
        uint256 id;
        BeeType beeType;
        string name;
        address endpoint; // Off-chain API endpoint controller
        BeeStatus status;
        uint256 activatedAt;
        uint256 lastActiveAt;
        uint256 tasksCompleted;
        uint256 successRate; // Basis points (10000 = 100%)
        string metadata; // IPFS hash with bee details
    }

    // Storage
    uint256 public beeCount;
    mapping(uint256 => Bee) public bees;
    mapping(BeeType => uint256[]) public beesByType;
    mapping(address => uint256) public endpointToBeeId;

    // Performance tracking
    struct BeePerformance {
        uint256 totalTasks;
        uint256 successfulTasks;
        uint256 failedTasks;
        uint256 avgResponseTime; // milliseconds
        uint256 lastUpdated;
    }
    
    mapping(uint256 => BeePerformance) public beePerformance;

    // Events
    event BeeSpawned(uint256 indexed beeId, BeeType indexed beeType, string name, address endpoint);
    event BeeActivated(uint256 indexed beeId, uint256 timestamp);
    event BeePaused(uint256 indexed beeId, string reason);
    event BeeRetired(uint256 indexed beeId, string reason);
    event BeeTaskCompleted(uint256 indexed beeId, bool success, uint256 responseTime);
    event BeePerformanceUpdated(uint256 indexed beeId, uint256 successRate);

    constructor(address _admin, address _queen) {
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(QUEEN_ROLE, _queen);
        _grantRole(BEE_MANAGER_ROLE, _admin);
        _grantRole(BEE_MANAGER_ROLE, _queen);
    }

    // ============ BEE MANAGEMENT ============

    /**
     * @notice Spawn a new bee agent
     */
    function spawnBee(
        BeeType beeType,
        string calldata name,
        address endpoint,
        string calldata metadata
    ) external onlyRole(QUEEN_ROLE) returns (uint256) {
        require(endpoint != address(0), "BeeSpawner: Invalid endpoint");
        require(endpointToBeeId[endpoint] == 0, "BeeSpawner: Endpoint already registered");

        uint256 beeId = beeCount++;
        
        Bee storage bee = bees[beeId];
        bee.id = beeId;
        bee.beeType = beeType;
        bee.name = name;
        bee.endpoint = endpoint;
        bee.status = BeeStatus.INACTIVE;
        bee.activatedAt = 0;
        bee.lastActiveAt = 0;
        bee.tasksCompleted = 0;
        bee.successRate = 10000; // Start at 100%
        bee.metadata = metadata;

        beesByType[beeType].push(beeId);
        endpointToBeeId[endpoint] = beeId;

        emit BeeSpawned(beeId, beeType, name, endpoint);

        return beeId;
    }

    /**
     * @notice Activate a bee
     */
    function activateBee(uint256 beeId) external onlyRole(BEE_MANAGER_ROLE) {
        Bee storage bee = bees[beeId];
        require(bee.status == BeeStatus.INACTIVE, "BeeSpawner: Already activated");

        bee.status = BeeStatus.ACTIVE;
        bee.activatedAt = block.timestamp;
        bee.lastActiveAt = block.timestamp;

        emit BeeActivated(beeId, block.timestamp);
    }

    /**
     * @notice Pause a bee
     */
    function pauseBee(uint256 beeId, string calldata reason) external onlyRole(BEE_MANAGER_ROLE) {
        Bee storage bee = bees[beeId];
        require(bee.status == BeeStatus.ACTIVE, "BeeSpawner: Not active");

        bee.status = BeeStatus.PAUSED;

        emit BeePaused(beeId, reason);
    }

    /**
     * @notice Resume a paused bee
     */
    function resumeBee(uint256 beeId) external onlyRole(BEE_MANAGER_ROLE) {
        Bee storage bee = bees[beeId];
        require(bee.status == BeeStatus.PAUSED, "BeeSpawner: Not paused");

        bee.status = BeeStatus.ACTIVE;
        bee.lastActiveAt = block.timestamp;

        emit BeeActivated(beeId, block.timestamp);
    }

    /**
     * @notice Retire a bee permanently
     */
    function retireBee(uint256 beeId, string calldata reason) external onlyRole(QUEEN_ROLE) {
        Bee storage bee = bees[beeId];
        require(bee.status != BeeStatus.RETIRED, "BeeSpawner: Already retired");

        bee.status = BeeStatus.RETIRED;

        emit BeeRetired(beeId, reason);
    }

    // ============ PERFORMANCE TRACKING ============

    /**
     * @notice Log task completion
     */
    function logTask(
        uint256 beeId,
        bool success,
        uint256 responseTime
    ) external onlyRole(QUEEN_ROLE) {
        Bee storage bee = bees[beeId];
        require(bee.status == BeeStatus.ACTIVE, "BeeSpawner: Bee not active");

        bee.tasksCompleted++;
        bee.lastActiveAt = block.timestamp;

        BeePerformance storage perf = beePerformance[beeId];
        perf.totalTasks++;
        
        if (success) {
            perf.successfulTasks++;
        } else {
            perf.failedTasks++;
        }

        // Update average response time
        if (perf.avgResponseTime == 0) {
            perf.avgResponseTime = responseTime;
        } else {
            perf.avgResponseTime = (perf.avgResponseTime + responseTime) / 2;
        }

        perf.lastUpdated = block.timestamp;

        // Update success rate (basis points)
        if (perf.totalTasks > 0) {
            bee.successRate = (perf.successfulTasks * 10000) / perf.totalTasks;
        }

        emit BeeTaskCompleted(beeId, success, responseTime);
        emit BeePerformanceUpdated(beeId, bee.successRate);
    }

    /**
     * @notice Update bee metadata
     */
    function updateBeeMetadata(uint256 beeId, string calldata newMetadata) 
        external 
        onlyRole(BEE_MANAGER_ROLE) 
    {
        bees[beeId].metadata = newMetadata;
    }

    // ============ VIEW FUNCTIONS ============

    /**
     * @notice Get bee details
     */
    function getBee(uint256 beeId) external view returns (
        BeeType beeType,
        string memory name,
        address endpoint,
        BeeStatus status,
        uint256 activatedAt,
        uint256 lastActiveAt,
        uint256 tasksCompleted,
        uint256 successRate
    ) {
        Bee storage bee = bees[beeId];
        return (
            bee.beeType,
            bee.name,
            bee.endpoint,
            bee.status,
            bee.activatedAt,
            bee.lastActiveAt,
            bee.tasksCompleted,
            bee.successRate
        );
    }

    /**
     * @notice Get bee performance
     */
    function getBeePerformance(uint256 beeId) external view returns (
        uint256 totalTasks,
        uint256 successfulTasks,
        uint256 failedTasks,
        uint256 avgResponseTime,
        uint256 lastUpdated
    ) {
        BeePerformance storage perf = beePerformance[beeId];
        return (
            perf.totalTasks,
            perf.successfulTasks,
            perf.failedTasks,
            perf.avgResponseTime,
            perf.lastUpdated
        );
    }

    /**
     * @notice Get all bees of a specific type
     */
    function getBeesByType(BeeType beeType) external view returns (uint256[] memory) {
        return beesByType[beeType];
    }

    /**
     * @notice Get active bees count
     */
    function getActiveBeeCount() external view returns (uint256) {
        uint256 count = 0;
        for (uint256 i = 0; i < beeCount; i++) {
            if (bees[i].status == BeeStatus.ACTIVE) {
                count++;
            }
        }
        return count;
    }

    /**
     * @notice Get all active bees
     */
    function getActiveBees() external view returns (uint256[] memory) {
        uint256 activeCount = 0;
        
        // Count active bees
        for (uint256 i = 0; i < beeCount; i++) {
            if (bees[i].status == BeeStatus.ACTIVE) {
                activeCount++;
            }
        }

        // Populate array
        uint256[] memory activeBees = new uint256[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 0; i < beeCount; i++) {
            if (bees[i].status == BeeStatus.ACTIVE) {
                activeBees[index] = i;
                index++;
            }
        }

        return activeBees;
    }

    /**
     * @notice Get swarm health (average success rate)
     */
    function getSwarmHealth() external view returns (uint256) {
        if (beeCount == 0) return 0;

        uint256 totalSuccessRate = 0;
        uint256 activeBees = 0;

        for (uint256 i = 0; i < beeCount; i++) {
            if (bees[i].status == BeeStatus.ACTIVE) {
                totalSuccessRate += bees[i].successRate;
                activeBees++;
            }
        }

        if (activeBees == 0) return 0;
        return totalSuccessRate / activeBees;
    }
}
