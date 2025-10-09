// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../interfaces/IQueen.sol";

/**
 * @title QueenController
 * @dev Central controller for the Queen AI that manages bee agents, task delegation, and autonomous token operations
 * 
 * Key responsibilities:
 * - Coordinate bee agents (LogicBee, MathsBee, BlockchainBee, etc.)
 * - Manage autonomous liquidity operations
 * - Control DEX interactions
 * - Distribute staking rewards and airdrops
 * - Execute treasury management decisions
 */
contract QueenController is IQueen, AccessControl, Pausable, ReentrancyGuard {
    // Role definitions
    bytes32 public constant BEE_WHITELISTER_ROLE = keccak256("BEE_WHITELISTER_ROLE");
    bytes32 public constant TASK_MANAGER_ROLE = keccak256("TASK_MANAGER_ROLE");
    bytes32 public constant TREASURY_MANAGER_ROLE = keccak256("TREASURY_MANAGER_ROLE");
    bytes32 public constant LIQUIDITY_MANAGER_ROLE = keccak256("LIQUIDITY_MANAGER_ROLE");
    
    // State variables
    address public override queenAddress;
    bool public override isActive;
    uint256 public override totalBees;
    
    // Token integration
    IERC20 public omkToken;
    address public treasuryVault;
    address public liquiditySentinel;
    
    // Bee management
    struct Bee {
        uint256 beeType;  // 1 = LogicBee, 2 = MathBee, etc.
        bool isActive;
        uint256 lastActive;
    }
    
    // Task management
    struct Task {
        address assignedBee;
        bool completed;
        bytes result;
        uint256 createdAt;
        uint256 completedAt;
    }
    
    // Mappings
    mapping(address => Bee) public bees;
    mapping(address => uint256) public beeToId;
    mapping(uint256 => address) public idToBee;
    mapping(bytes32 => Task) public tasks;
    
    // Bee type whitelist
    mapping(uint256 => bool) public isBeeTypeWhitelisted;
    
    // Queen operation tracking
    struct QueenOperation {
        string operationType; // "DEX_ADD_LIQUIDITY", "STAKING_REWARD", "AIRDROP", etc.
        uint256 amount;
        address target;
        uint256 timestamp;
        bool executed;
    }
    
    mapping(bytes32 => QueenOperation) public queenOperations;
    uint256 public totalOperations;
    
    // Events (inherited from IQueen)
    event QueenOperationProposed(bytes32 indexed operationId, string operationType, uint256 amount, address target);
    event QueenOperationExecuted(bytes32 indexed operationId, bool success);
    event TreasuryVaultUpdated(address indexed newVault);
    event LiquiditySentinelUpdated(address indexed newSentinel);
    event OMKTokenUpdated(address indexed newToken);
    
    // Modifiers
    modifier onlyQueen() {
        require(msg.sender == queenAddress, "QueenController: Caller is not the Queen");
        _;
    }
    
    modifier onlyActive() {
        require(isActive, "QueenController: Contract is not active");
        _;
    }
    
    /**
     * @dev Constructor
     * @param _admin The address that will have the DEFAULT_ADMIN_ROLE
     * @param _queenAddress The address of the Queen AI backend service
     * @param _omkToken The address of the OMK token contract
     */
    constructor(
        address _admin, 
        address _queenAddress,
        address _omkToken
    ) {
        require(_admin != address(0), "QueenController: Invalid admin address");
        require(_queenAddress != address(0), "QueenController: Invalid queen address");
        require(_omkToken != address(0), "QueenController: Invalid token address");
        
        // Set up roles
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(BEE_WHITELISTER_ROLE, _admin);
        _grantRole(TASK_MANAGER_ROLE, _admin);
        _grantRole(TREASURY_MANAGER_ROLE, _queenAddress);
        _grantRole(LIQUIDITY_MANAGER_ROLE, _queenAddress);
        
        // Initialize state
        queenAddress = _queenAddress;
        omkToken = IERC20(_omkToken);
        isActive = true;
        totalBees = 0;
        totalOperations = 0;
        
        // Whitelist default bee types (can be extended later)
        isBeeTypeWhitelisted[1] = true; // LogicBee
        isBeeTypeWhitelisted[2] = true; // MathsBee
        isBeeTypeWhitelisted[3] = true; // PatternRecognitionBee
        isBeeTypeWhitelisted[4] = true; // BlockchainBee
        isBeeTypeWhitelisted[5] = true; // SecurityBee
        isBeeTypeWhitelisted[6] = true; // DataBee
    }
    
    // External functions
    
    /**
     * @notice Spawn a new bee agent
     * @param beeType The type of bee to spawn
     * @param initData Initialization data for the bee
     * @return The address of the newly spawned bee
     */
    function spawnBee(
        uint256 beeType,
        bytes calldata initData
    ) external override onlyRole(BEE_WHITELISTER_ROLE) whenNotPaused nonReentrant returns (address) {
        require(isBeeTypeWhitelisted[beeType], "QueenController: Invalid bee type");
        
        // In a real implementation, this would deploy a new Bee contract
        // For now, we'll simulate it with a new address
        address newBee = address(
            uint160(
                uint256(
                    keccak256(
                        abi.encodePacked(
                            block.timestamp,
                            block.prevrandao,
                            msg.sender,
                            totalBees
                        )
                    )
                )
            )
        );
        
        // Register the new bee
        bees[newBee] = Bee({
            beeType: beeType,
            isActive: true,
            lastActive: block.timestamp
        });
        
        beeToId[newBee] = totalBees;
        idToBee[totalBees] = newBee;
        totalBees++;
        
        emit BeeSpawned(newBee, beeType, block.timestamp);
        
        return newBee;
    }
    
    /**
     * @notice Retire a bee agent
     * @param bee The address of the bee to retire
     */
    function retireBee(address bee) external override onlyRole(BEE_WHITELISTER_ROLE) whenNotPaused {
        require(bees[bee].isActive, "QueenController: Bee is not active");
        
        bees[bee].isActive = false;
        bees[bee].lastActive = block.timestamp;
        
        emit BeeRetired(bee, block.timestamp);
    }
    
    /**
     * @notice Assign a task to a bee
     * @param bee The address of the bee to assign the task to
     * @param taskData The task data
     * @return taskId The ID of the created task
     */
    function assignTask(
        address bee,
        bytes calldata taskData
    ) external override onlyRole(TASK_MANAGER_ROLE) whenNotPaused onlyActive returns (bytes32) {
        require(bees[bee].isActive, "QueenController: Bee is not active");
        
        bytes32 taskId = keccak256(
            abi.encodePacked(
                block.timestamp,
                msg.sender,
                bee,
                taskData
            )
        );
        
        tasks[taskId] = Task({
            assignedBee: bee,
            completed: false,
            result: "",
            createdAt: block.timestamp,
            completedAt: 0
        });
        
        emit TaskAssigned(bee, taskId, taskData);
        
        return taskId;
    }
    
    /**
     * @notice Complete a task
     * @param taskId The ID of the task to complete
     * @param result The result of the task
     */
    function completeTask(
        bytes32 taskId,
        bytes calldata result
    ) external override onlyQueen whenNotPaused onlyActive {
        require(tasks[taskId].assignedBee != address(0), "QueenController: Invalid task ID");
        require(!tasks[taskId].completed, "QueenController: Task already completed");
        
        tasks[taskId].completed = true;
        tasks[taskId].result = result;
        tasks[taskId].completedAt = block.timestamp;
        
        emit TaskCompleted(tasks[taskId].assignedBee, taskId, result);
    }
    
    /**
     * @notice Emergency shutdown the Queen and all bees
     */
    function emergencyShutdown() external override onlyRole(DEFAULT_ADMIN_ROLE) {
        isActive = false;
        _pause();
        
        emit EmergencyShutdown(msg.sender, block.timestamp);
    }
    
    // ============ QUEEN AUTONOMOUS OPERATIONS ============
    
    /**
     * @notice Propose a Queen operation (e.g., liquidity addition, reward distribution)
     * @param operationType Type of operation (DEX_ADD_LIQUIDITY, STAKING_REWARD, etc.)
     * @param amount Amount of tokens involved
     * @param target Target address for the operation
     * @return operationId The ID of the proposed operation
     */
    function proposeOperation(
        string calldata operationType,
        uint256 amount,
        address target
    ) external onlyRole(TREASURY_MANAGER_ROLE) whenNotPaused returns (bytes32) {
        require(amount > 0, "QueenController: Amount must be positive");
        require(target != address(0), "QueenController: Invalid target");
        
        bytes32 operationId = keccak256(
            abi.encodePacked(
                block.timestamp,
                operationType,
                amount,
                target,
                totalOperations
            )
        );
        
        queenOperations[operationId] = QueenOperation({
            operationType: operationType,
            amount: amount,
            target: target,
            timestamp: block.timestamp,
            executed: false
        });
        
        totalOperations++;
        
        emit QueenOperationProposed(operationId, operationType, amount, target);
        
        return operationId;
    }
    
    /**
     * @notice Execute a proposed operation
     * @param operationId The ID of the operation to execute
     * @dev This is called by Queen's backend after bee analysis/consensus
     */
    function executeOperation(bytes32 operationId) external onlyQueen whenNotPaused nonReentrant {
        QueenOperation storage operation = queenOperations[operationId];
        require(operation.timestamp != 0, "QueenController: Operation does not exist");
        require(!operation.executed, "QueenController: Operation already executed");
        
        operation.executed = true;
        
        // Execute the operation based on type
        // Note: In production, this would interact with actual contracts (DEX, Staking, etc.)
        bool success = true;
        
        emit QueenOperationExecuted(operationId, success);
    }
    
    /**
     * @notice Get Queen's current token balance
     * @return balance The OMK token balance held by Queen
     */
    function getQueenBalance() external view returns (uint256) {
        return omkToken.balanceOf(queenAddress);
    }
    
    /**
     * @notice Get operation details
     * @param operationId The ID of the operation
     * @return operation The operation struct
     */
    function getOperation(bytes32 operationId) external view returns (QueenOperation memory) {
        return queenOperations[operationId];
    }
    
    // View functions
    
    /**
     * @notice Get the address of a bee by its ID
     * @param beeId The ID of the bee
     * @return The address of the bee
     */
    function getBeeAddress(uint256 beeId) external view override returns (address) {
        return idToBee[beeId];
    }
    
    /**
     * @notice Get the type of a bee
     * @param bee The address of the bee
     * @return The type of the bee
     */
    function getBeeType(address bee) external view override returns (uint256) {
        return bees[bee].beeType;
    }
    
    /**
     * @notice Check if a bee is active
     * @param bee The address of the bee
     * @return True if the bee is active, false otherwise
     */
    function isBeeActive(address bee) external view override returns (bool) {
        return bees[bee].isActive;
    }
    
    /**
     * @notice Get the status of a task
     * @param taskId The ID of the task
     * @return completed Whether the task is completed
     * @return assignedBee The address of the bee assigned to the task
     * @return result The result of the task (empty if not completed)
     */
    function getTaskStatus(
        bytes32 taskId
    ) external view override returns (bool completed, address assignedBee, bytes memory result) {
        Task memory task = tasks[taskId];
        return (task.completed, task.assignedBee, task.result);
    }
    
    // Admin functions
    
    /**
     * @notice Whitelist a bee type
     * @param beeType The type of bee to whitelist
     * @param whitelisted Whether to whitelist or unwhitelist the bee type
     */
    function setBeeTypeWhitelist(
        uint256 beeType,
        bool whitelisted
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        isBeeTypeWhitelisted[beeType] = whitelisted;
    }
    
    /**
     * @notice Update the Queen's address
     * @param newQueenAddress The new address of the Queen
     */
    function updateQueenAddress(
        address newQueenAddress
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(newQueenAddress != address(0), "QueenController: Invalid address");
        queenAddress = newQueenAddress;
    }
    
    /**
     * @notice Pause the contract
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @notice Unpause the contract
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @notice Set the TreasuryVault contract address
     * @param _treasuryVault Address of the TreasuryVault contract
     */
    function setTreasuryVault(address _treasuryVault) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_treasuryVault != address(0), "QueenController: Invalid treasury vault address");
        treasuryVault = _treasuryVault;
        emit TreasuryVaultUpdated(_treasuryVault);
    }
    
    /**
     * @notice Set the LiquiditySentinel contract address
     * @param _liquiditySentinel Address of the LiquiditySentinel contract
     */
    function setLiquiditySentinel(address _liquiditySentinel) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_liquiditySentinel != address(0), "QueenController: Invalid liquidity sentinel address");
        liquiditySentinel = _liquiditySentinel;
        emit LiquiditySentinelUpdated(_liquiditySentinel);
    }
    
    /**
     * @notice Update the OMK token contract address
     * @param _omkToken Address of the new OMK token contract
     */
    function setOMKToken(address _omkToken) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_omkToken != address(0), "QueenController: Invalid token address");
        omkToken = IERC20(_omkToken);
        emit OMKTokenUpdated(_omkToken);
    }
}
