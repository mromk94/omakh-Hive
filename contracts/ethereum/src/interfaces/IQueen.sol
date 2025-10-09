// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IQueen
 * @dev Interface for the Queen AI contract
 */
interface IQueen {
    // Events
    event BeeSpawned(address indexed bee, uint256 beeType, uint256 timestamp);
    event BeeRetired(address indexed bee, uint256 timestamp);
    event TaskAssigned(address indexed bee, bytes32 taskId, bytes taskData);
    event TaskCompleted(address indexed bee, bytes32 taskId, bytes result);
    event EmergencyShutdown(address indexed caller, uint256 timestamp);
    
    // State Variables
    function queenAddress() external view returns (address);
    function isActive() external view returns (bool);
    function totalBees() external view returns (uint256);
    
    // Functions
    function spawnBee(uint256 beeType, bytes calldata initData) external returns (address);
    function retireBee(address bee) external;
    function assignTask(address bee, bytes calldata taskData) external returns (bytes32);
    function completeTask(bytes32 taskId, bytes calldata result) external;
    function emergencyShutdown() external;
    
    // View Functions
    function getBeeAddress(uint256 beeId) external view returns (address);
    function getBeeType(address bee) external view returns (uint256);
    function isBeeActive(address bee) external view returns (bool);
    function getTaskStatus(bytes32 taskId) external view returns (bool completed, address assignedBee, bytes memory result);
}
