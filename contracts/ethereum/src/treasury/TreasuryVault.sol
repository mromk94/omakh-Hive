// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "./ITreasuryVault.sol";

/**
 * @title TreasuryVault
 * @dev A multi-signature vault for managing treasury assets with withdrawal approval workflow
 */
contract TreasuryVault is ITreasuryVault, AccessControl, ReentrancyGuard, Pausable {
    using SafeERC20 for IERC20;
    
    // Role definitions
    bytes32 public constant APPROVER_ROLE = keccak256("APPROVER_ROLE");
    bytes32 public constant EMERGENCY_ADMIN_ROLE = keccak256("EMERGENCY_ADMIN_ROLE");
    
    // Withdrawal request structure
    struct WithdrawalRequest {
        address token;      // Token address (address(0) for ETH)
        address to;         // Recipient address
        uint256 amount;     // Amount to withdraw
        uint256 approvals;  // Number of approvals received
        uint256 timestamp;  // When the request was created
        bool executed;      // Whether the withdrawal was executed
        bool approved;      // Whether the withdrawal was approved
        mapping(address => bool) hasApproved; // Tracks which approvers have approved
    }
    
    // State variables
    bool public override isActive = true;
    uint256 public override requiredApprovals = 2; // Default to 2/3 multi-sig
    uint256 public override withdrawalDelay = 24 hours; // Default 24h timelock
    uint256 public override totalApprovers;
    
    // Mappings
    mapping(address => bool) public override isApprover;
    mapping(bytes32 => WithdrawalRequest) public withdrawalRequests;
    mapping(address => uint256) public balances; // Track token balances (for ETH, use address(0))
    
    // Modifiers
    modifier onlyActive() {
        require(isActive, "TreasuryVault: contract is not active");
        _;
    }
    
    modifier onlyApprover() {
        require(hasRole(APPROVER_ROLE, msg.sender), "TreasuryVault: caller is not an approver");
        _;
    }
    
    /**
     * @dev Constructor
     * @param _admin The admin address with DEFAULT_ADMIN_ROLE
     * @param _approvers Array of initial approver addresses
     * @param _emergencyAdmin Address with emergency admin privileges
     */
    constructor(
        address _admin,
        address[] memory _approvers,
        address _emergencyAdmin
    ) {
        require(_admin != address(0), "TreasuryVault: admin is zero address");
        require(_emergencyAdmin != address(0), "TreasuryVault: emergency admin is zero address");
        
        // Set up roles
        _setupRole(DEFAULT_ADMIN_ROLE, _admin);
        _setupRole(EMERGENCY_ADMIN_ROLE, _emergencyAdmin);
        
        // Add approvers
        for (uint256 i = 0; i < _approvers.length; i++) {
            _addApprover(_approvers[i]);
        }
        
        // Set initial required approvals (majority of approvers)
        if (_approvers.length > 0) {
            requiredApprovals = (_approvers.length / 2) + 1;
        }
    }
    
    // Receive function to accept ETH deposits
    receive() external payable {
        emit Deposit(address(0), msg.sender, msg.value);
    }
    
    /**
     * @dev Deposit ETH or ERC20 tokens into the vault
     * @param token Token address (address(0) for ETH)
     * @param amount Amount to deposit
     */
    function deposit(address token, uint256 amount) external payable override nonReentrant whenNotPaused onlyActive {
        if (token == address(0)) {
            // Handle ETH deposit
            require(msg.value == amount, "TreasuryVault: ETH amount mismatch");
            balances[address(0)] += amount;
        } else {
            // Handle ERC20 deposit
            require(msg.value == 0, "TreasuryVault: ETH sent with token deposit");
            IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
            balances[token] += amount;
        }
        
        emit Deposit(token, msg.sender, amount);
    }
    
    /**
     * @dev Request a withdrawal from the vault
     * @param token Token address (address(0) for ETH)
     * @param to Recipient address
     * @param amount Amount to withdraw
     * @return withdrawalId The ID of the withdrawal request
     */
    function requestWithdrawal(
        address token,
        address to,
        uint256 amount
    ) external override nonReentrant whenNotPaused onlyActive returns (bytes32) {
        require(to != address(0), "TreasuryVault: cannot withdraw to zero address");
        require(amount > 0, "TreasuryVault: amount must be greater than zero");
        
        // Check balance
        if (token == address(0)) {
            require(balances[address(0)] >= amount, "TreasuryVault: insufficient ETH balance");
        } else {
            require(balances[token] >= amount, "TreasuryVault: insufficient token balance");
        }
        
        // Generate withdrawal ID
        bytes32 withdrawalId = keccak256(
            abi.encodePacked(
                block.timestamp,
                msg.sender,
                token,
                to,
                amount,
                block.prevrandao
            )
        );
        
        // Create withdrawal request
        WithdrawalRequest storage request = withdrawalRequests[withdrawalId];
        require(request.timestamp == 0, "TreasuryVault: duplicate withdrawal ID");
        
        request.token = token;
        request.to = to;
        request.amount = amount;
        request.timestamp = block.timestamp;
        request.executed = false;
        request.approved = false;
        
        // Auto-approve if the caller is an approver
        if (hasRole(APPROVER_ROLE, msg.sender)) {
            request.approvals = 1;
            request.hasApproved[msg.sender] = true;
            
            // Check if we have enough approvals to auto-approve
            if (request.approvals >= requiredApprovals) {
                request.approved = true;
            }
        }
        
        emit WithdrawalRequested(msg.sender, token, to, amount, withdrawalId);
        
        return withdrawalId;
    }
    
    /**
     * @dev Approve a withdrawal request
     * @param withdrawalId The ID of the withdrawal request to approve
     */
    function approveWithdrawal(bytes32 withdrawalId) external override nonReentrant whenNotPaused onlyActive onlyApprover {
        WithdrawalRequest storage request = withdrawalRequests[withdrawalId];
        require(request.timestamp > 0, "TreasuryVault: invalid withdrawal ID");
        require(!request.executed, "TreasuryVault: withdrawal already executed");
        require(!request.hasApproved[msg.sender], "TreasuryVault: already approved");
        
        // Mark as approved by this approver
        request.hasApproved[msg.sender] = true;
        request.approvals++;
        
        emit WithdrawalApproved(msg.sender, withdrawalId);
        
        // Auto-approve if we have enough approvals
        if (!request.approved && request.approvals >= requiredApprovals) {
            request.approved = true;
            emit WithdrawalApproved(address(0), withdrawalId); // Indicate final approval
        }
    }
    
    /**
     * @dev Reject a withdrawal request
     * @param withdrawalId The ID of the withdrawal request to reject
     */
    function rejectWithdrawal(bytes32 withdrawalId) external override nonReentrant whenNotPaused onlyApprover {
        WithdrawalRequest storage request = withdrawalRequests[withdrawalId];
        require(request.timestamp > 0, "TreasuryVault: invalid withdrawal ID");
        require(!request.executed, "TreasuryVault: withdrawal already executed");
        
        // Only allow rejection if not yet approved or if the withdrawal delay hasn't passed
        require(!request.approved || block.timestamp < request.timestamp + withdrawalDelay, 
            "TreasuryVault: cannot reject after approval and timelock");
        
        // Mark as executed to prevent further actions
        request.executed = true;
        
        emit WithdrawalRejected(msg.sender, withdrawalId);
    }
    
    /**
     * @dev Execute an approved withdrawal
     * @param withdrawalId The ID of the withdrawal request to execute
     */
    function executeWithdrawal(bytes32 withdrawalId) external override nonReentrant whenNotPaused onlyActive {
        WithdrawalRequest storage request = withdrawalRequests[withdrawalId];
        require(request.timestamp > 0, "TreasuryVault: invalid withdrawal ID");
        require(!request.executed, "TreasuryVault: withdrawal already executed");
        require(request.approved, "TreasuryVault: withdrawal not approved");
        require(block.timestamp >= request.timestamp + withdrawalDelay, "TreasuryVault: withdrawal delay not passed");
        
        // Mark as executed to prevent reentrancy
        request.executed = true;
        
        // Update balances
        if (request.token == address(0)) {
            // Handle ETH withdrawal
            require(balances[address(0)] >= request.amount, "TreasuryVault: insufficient ETH balance");
            balances[address(0)] -= request.amount;
            
            // Transfer ETH
            (bool success, ) = request.to.call{value: request.amount}("");
            require(success, "TreasuryVault: ETH transfer failed");
        } else {
            // Handle ERC20 withdrawal
            require(balances[request.token] >= request.amount, "TreasuryVault: insufficient token balance");
            balances[request.token] -= request.amount;
            
            // Transfer tokens
            IERC20(request.token).safeTransfer(request.to, request.amount);
        }
        
        emit Withdraw(request.token, request.to, request.amount, withdrawalId);
    }
    
    /**
     * @dev Emergency shutdown the vault (only callable by emergency admin)
     */
    function emergencyShutdown() external override onlyRole(EMERGENCY_ADMIN_ROLE) {
        require(isActive, "TreasuryVault: already inactive");
        isActive = false;
        emit EmergencyShutdown(msg.sender, block.timestamp);
    }
    
    /**
     * @dev Get withdrawal status
     * @param withdrawalId The ID of the withdrawal request
     */
    function getWithdrawalStatus(bytes32 withdrawalId)
        external
        view
        override
        returns (
            address token,
            address to,
            uint256 amount,
            uint256 approvals,
            uint256 timestamp,
            bool executed,
            bool approved
        )
    {
        WithdrawalRequest storage request = withdrawalRequests[withdrawalId];
        require(request.timestamp > 0, "TreasuryVault: invalid withdrawal ID");
        
        return (
            request.token,
            request.to,
            request.amount,
            request.approvals,
            request.timestamp,
            request.executed,
            request.approved
        );
    }
    
    /**
     * @dev Get balance of a token in the vault
     * @param token Token address (address(0) for ETH)
     * @return Balance of the token in the vault
     */
    function getBalance(address token) external view override returns (uint256) {
        if (token == address(0)) {
            return address(this).balance;
        } else {
            return IERC20(token).balanceOf(address(this));
        }
    }
    
    /**
     * @dev Add a new approver
     * @param _approver Address of the new approver
     */
    function addApprover(address _approver) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_approver != address(0), "TreasuryVault: approver is zero address");
        _addApprover(_approver);
        
        // Update required approvals (majority of approvers)
        if (totalApprovers > 1) {
            requiredApprovals = (totalApprovers / 2) + 1;
        }
    }
    
    /**
     * @dev Remove an approver
     * @param _approver Address of the approver to remove
     */
    function removeApprover(address _approver) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(isApprover[_approver], "TreasuryVault: not an approver");
        require(totalApprovers > 1, "TreasuryVault: cannot remove last approver");
        
        // Revoke role and update state
        _revokeRole(APPROVER_ROLE, _approver);
        isApprover[_approver] = false;
        totalApprovers--;
        
        // Update required approvals (majority of approvers)
        requiredApprovals = (totalApprovers / 2) + 1;
    }
    
    /**
     * @dev Set the withdrawal delay
     * @param _withdrawalDelay New withdrawal delay in seconds
     */
    function setWithdrawalDelay(uint256 _withdrawalDelay) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_withdrawalDelay <= 7 days, "TreasuryVault: delay too long");
        withdrawalDelay = _withdrawalDelay;
    }
    
    /**
     * @dev Internal function to add an approver
     * @param _approver Address of the approver to add
     */
    function _addApprover(address _approver) internal {
        require(!isApprover[_approver], "TreasuryVault: already an approver");
        
        _grantRole(APPROVER_ROLE, _approver);
        isApprover[_approver] = true;
        totalApprovers++;
    }
    
    /**
     * @dev Pause the contract (only callable by admin)
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause the contract (only callable by admin)
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
}
