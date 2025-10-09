// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ITreasuryVault
 * @dev Interface for the TreasuryVault contract
 */
interface ITreasuryVault {
    // Events
    event Deposit(address indexed token, address indexed from, uint256 amount);
    event Withdraw(
        address indexed token,
        address indexed to,
        uint256 amount,
        bytes32 withdrawalId
    );
    event WithdrawalRequested(
        address indexed requester,
        address indexed token,
        address indexed to,
        uint256 amount,
        bytes32 withdrawalId
    );
    event WithdrawalApproved(
        address indexed approver,
        bytes32 indexed withdrawalId
    );
    event WithdrawalRejected(
        address indexed rejector,
        bytes32 indexed withdrawalId
    );
    event EmergencyShutdown(address indexed caller, uint256 timestamp);
    
    // State Variables
    function isActive() external view returns (bool);
    function requiredApprovals() external view returns (uint256);
    function withdrawalDelay() external view returns (uint256);
    function isApprover(address) external view returns (bool);
    function totalApprovers() external view returns (uint256);
    
    // Functions
    function deposit(address token, uint256 amount) external payable;
    function requestWithdrawal(
        address token,
        address to,
        uint256 amount
    ) external returns (bytes32);
    function approveWithdrawal(bytes32 withdrawalId) external;
    function rejectWithdrawal(bytes32 withdrawalId) external;
    function executeWithdrawal(bytes32 withdrawalId) external;
    function emergencyShutdown() external;
    
    // View Functions
    function getWithdrawalStatus(bytes32 withdrawalId)
        external
        view
        returns (
            address token,
            address to,
            uint256 amount,
            uint256 approvals,
            uint256 timestamp,
            bool executed,
            bool approved
        );
    function getBalance(address token) external view returns (uint256);
}
