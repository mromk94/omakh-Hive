// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title EmergencySystem
 * @dev Centralized emergency control for entire OMK Hive system
 * 
 * Emergency Actions:
 * - Pause all contracts
 * - Emergency withdrawal
 * - Circuit breaker activation
 * - Rate limit override
 * - Blacklist malicious addresses
 */
contract EmergencySystem is AccessControl, Pausable {
    
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");
    bytes32 public constant GUARDIAN_ROLE = keccak256("GUARDIAN_ROLE");

    // Registered contracts
    address[] public registeredContracts;
    mapping(address => bool) public isRegistered;
    mapping(address => bool) public isPaused;
    
    // Emergency state
    bool public emergencyShutdown;
    bool public circuitBreakerActive;
    uint256 public circuitBreakerUntil;
    
    // Blacklist
    mapping(address => bool) public isBlacklisted;
    mapping(address => string) public blacklistReason;
    
    // Emergency actions log
    struct EmergencyAction {
        uint256 timestamp;
        address executor;
        string actionType;
        string description;
    }
    
    EmergencyAction[] public emergencyLog;
    
    // Events
    event ContractRegistered(address indexed contractAddress);
    event ContractPaused(address indexed contractAddress, address indexed executor);
    event ContractUnpaused(address indexed contractAddress, address indexed executor);
    event EmergencyShutdownActivated(address indexed executor, string reason);
    event EmergencyShutdownDeactivated(address indexed executor);
    event CircuitBreakerActivated(address indexed executor, uint256 duration);
    event AddressBlacklisted(address indexed addr, string reason);
    event AddressWhitelisted(address indexed addr);
    event EmergencyActionLogged(string actionType, string description);

    constructor(address _admin, address _guardian) {
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(EMERGENCY_ROLE, _admin);
        _grantRole(GUARDIAN_ROLE, _guardian); // Queen AI
    }

    // ============ CONTRACT MANAGEMENT ============

    /**
     * @notice Register contract for emergency control
     */
    function registerContract(address contractAddress) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(!isRegistered[contractAddress], "EmergencySystem: Already registered");
        
        registeredContracts.push(contractAddress);
        isRegistered[contractAddress] = true;
        
        emit ContractRegistered(contractAddress);
    }

    /**
     * @notice Pause specific contract
     */
    function pauseContract(address contractAddress) external onlyRole(EMERGENCY_ROLE) {
        require(isRegistered[contractAddress], "EmergencySystem: Not registered");
        require(!isPaused[contractAddress], "EmergencySystem: Already paused");
        
        isPaused[contractAddress] = true;
        
        // Call pause on the contract (if it has Pausable)
        (bool success, ) = contractAddress.call(abi.encodeWithSignature("pause()"));
        require(success, "EmergencySystem: Pause failed");
        
        emit ContractPaused(contractAddress, msg.sender);
        _logAction("CONTRACT_PAUSE", string(abi.encodePacked("Paused: ", _addressToString(contractAddress))));
    }

    /**
     * @notice Unpause specific contract
     */
    function unpauseContract(address contractAddress) external onlyRole(EMERGENCY_ROLE) {
        require(isRegistered[contractAddress], "EmergencySystem: Not registered");
        require(isPaused[contractAddress], "EmergencySystem: Not paused");
        require(!emergencyShutdown, "EmergencySystem: System in emergency shutdown");
        
        isPaused[contractAddress] = false;
        
        // Call unpause on the contract
        (bool success, ) = contractAddress.call(abi.encodeWithSignature("unpause()"));
        require(success, "EmergencySystem: Unpause failed");
        
        emit ContractUnpaused(contractAddress, msg.sender);
        _logAction("CONTRACT_UNPAUSE", string(abi.encodePacked("Unpaused: ", _addressToString(contractAddress))));
    }

    /**
     * @notice Pause ALL registered contracts
     */
    function pauseAllContracts() external onlyRole(EMERGENCY_ROLE) {
        for (uint256 i = 0; i < registeredContracts.length; i++) {
            address contractAddress = registeredContracts[i];
            if (!isPaused[contractAddress]) {
                isPaused[contractAddress] = true;
                contractAddress.call(abi.encodeWithSignature("pause()"));
                emit ContractPaused(contractAddress, msg.sender);
            }
        }
        
        _logAction("PAUSE_ALL", "All contracts paused");
    }

    // ============ EMERGENCY SHUTDOWN ============

    /**
     * @notice Activate full emergency shutdown
     */
    function activateEmergencyShutdown(string calldata reason) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(!emergencyShutdown, "EmergencySystem: Already in shutdown");
        
        emergencyShutdown = true;
        
        // Pause all contracts
        for (uint256 i = 0; i < registeredContracts.length; i++) {
            address contractAddress = registeredContracts[i];
            isPaused[contractAddress] = true;
            contractAddress.call(abi.encodeWithSignature("pause()"));
        }
        
        emit EmergencyShutdownActivated(msg.sender, reason);
        _logAction("EMERGENCY_SHUTDOWN", reason);
    }

    /**
     * @notice Deactivate emergency shutdown
     */
    function deactivateEmergencyShutdown() external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(emergencyShutdown, "EmergencySystem: Not in shutdown");
        
        emergencyShutdown = false;
        
        emit EmergencyShutdownDeactivated(msg.sender);
        _logAction("SHUTDOWN_DEACTIVATED", "Emergency shutdown lifted");
    }

    // ============ CIRCUIT BREAKER ============

    /**
     * @notice Activate circuit breaker (temporary halt)
     */
    function activateCircuitBreaker(uint256 durationHours) external onlyRole(GUARDIAN_ROLE) {
        require(durationHours <= 24, "EmergencySystem: Max 24 hours");
        
        circuitBreakerActive = true;
        circuitBreakerUntil = block.timestamp + (durationHours * 1 hours);
        
        // Pause all contracts temporarily
        for (uint256 i = 0; i < registeredContracts.length; i++) {
            address contractAddress = registeredContracts[i];
            if (!isPaused[contractAddress]) {
                isPaused[contractAddress] = true;
                contractAddress.call(abi.encodeWithSignature("pause()"));
            }
        }
        
        emit CircuitBreakerActivated(msg.sender, durationHours);
        _logAction("CIRCUIT_BREAKER", string(abi.encodePacked("Activated for ", _uint2str(durationHours), " hours")));
    }

    /**
     * @notice Check and auto-deactivate circuit breaker
     */
    function checkCircuitBreaker() external {
        if (circuitBreakerActive && block.timestamp >= circuitBreakerUntil) {
            circuitBreakerActive = false;
            
            // Auto-unpause if not in emergency shutdown
            if (!emergencyShutdown) {
                for (uint256 i = 0; i < registeredContracts.length; i++) {
                    address contractAddress = registeredContracts[i];
                    if (isPaused[contractAddress]) {
                        isPaused[contractAddress] = false;
                        contractAddress.call(abi.encodeWithSignature("unpause()"));
                    }
                }
            }
            
            _logAction("CIRCUIT_BREAKER_AUTO_OFF", "Circuit breaker automatically deactivated");
        }
    }

    // ============ BLACKLIST ============

    /**
     * @notice Blacklist malicious address
     */
    function blacklistAddress(address addr, string calldata reason) external onlyRole(EMERGENCY_ROLE) {
        require(!isBlacklisted[addr], "EmergencySystem: Already blacklisted");
        
        isBlacklisted[addr] = true;
        blacklistReason[addr] = reason;
        
        emit AddressBlacklisted(addr, reason);
        _logAction("BLACKLIST", string(abi.encodePacked("Address blacklisted: ", _addressToString(addr))));
    }

    /**
     * @notice Remove address from blacklist
     */
    function whitelistAddress(address addr) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(isBlacklisted[addr], "EmergencySystem: Not blacklisted");
        
        isBlacklisted[addr] = false;
        delete blacklistReason[addr];
        
        emit AddressWhitelisted(addr);
        _logAction("WHITELIST", string(abi.encodePacked("Address whitelisted: ", _addressToString(addr))));
    }

    // ============ VIEW FUNCTIONS ============

    /**
     * @notice Get emergency status
     */
    function getEmergencyStatus() external view returns (
        bool shutdown,
        bool circuitBreaker,
        uint256 circuitBreakerEnds,
        uint256 pausedContracts,
        uint256 totalContracts
    ) {
        uint256 paused = 0;
        for (uint256 i = 0; i < registeredContracts.length; i++) {
            if (isPaused[registeredContracts[i]]) paused++;
        }
        
        return (
            emergencyShutdown,
            circuitBreakerActive,
            circuitBreakerUntil,
            paused,
            registeredContracts.length
        );
    }

    /**
     * @notice Get emergency log
     */
    function getEmergencyLog(uint256 offset, uint256 limit) external view returns (EmergencyAction[] memory) {
        uint256 total = emergencyLog.length;
        if (offset >= total) return new EmergencyAction[](0);
        
        uint256 end = offset + limit > total ? total : offset + limit;
        uint256 size = end - offset;
        
        EmergencyAction[] memory actions = new EmergencyAction[](size);
        for (uint256 i = 0; i < size; i++) {
            actions[i] = emergencyLog[offset + i];
        }
        
        return actions;
    }

    /**
     * @notice Get all registered contracts
     */
    function getAllContracts() external view returns (address[] memory, bool[] memory) {
        bool[] memory pausedStatus = new bool[](registeredContracts.length);
        for (uint256 i = 0; i < registeredContracts.length; i++) {
            pausedStatus[i] = isPaused[registeredContracts[i]];
        }
        return (registeredContracts, pausedStatus);
    }

    // ============ INTERNAL FUNCTIONS ============

    function _logAction(string memory actionType, string memory description) internal {
        emergencyLog.push(EmergencyAction({
            timestamp: block.timestamp,
            executor: msg.sender,
            actionType: actionType,
            description: description
        }));
        
        emit EmergencyActionLogged(actionType, description);
    }

    function _addressToString(address addr) internal pure returns (string memory) {
        bytes memory alphabet = "0123456789abcdef";
        bytes memory data = abi.encodePacked(addr);
        bytes memory str = new bytes(42);
        str[0] = '0';
        str[1] = 'x';
        for (uint256 i = 0; i < 20; i++) {
            str[2+i*2] = alphabet[uint8(data[i] >> 4)];
            str[3+i*2] = alphabet[uint8(data[i] & 0x0f)];
        }
        return string(str);
    }

    function _uint2str(uint256 value) internal pure returns (string memory) {
        if (value == 0) return "0";
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buffer);
    }
}
