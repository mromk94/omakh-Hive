// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title OMKBridge
 * @dev Cross-chain bridge for OMK tokens between Ethereum and Solana
 * 
 * Features:
 * - Lock tokens on Ethereum
 * - Mint wrapped tokens on Solana (via relayer)
 * - Burn wrapped tokens on Solana
 * - Release locked tokens on Ethereum (with proof)
 * - Multi-signature validation
 * - Rate limiting for security
 * - Emergency pause functionality
 */
contract OMKBridge is AccessControl, Pausable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    bytes32 public constant RELAYER_ROLE = keccak256("RELAYER_ROLE");
    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");
    bytes32 public constant QUEEN_ROLE = keccak256("QUEEN_ROLE");

    IERC20 public immutable omkToken;

    // Bridge state
    uint256 public totalLocked;
    uint256 public totalReleased;
    uint256 public bridgeNonce;

    // Rate limiting
    uint256 public maxDailyBridge = 10_000_000 * 10**18; // 10M per day (adjustable)
    uint256 public dailyBridgeAmount;
    uint256 public lastResetTimestamp;

    // Multisig requirements
    uint256 public requiredValidations = 2; // Require 2 validator signatures
    mapping(bytes32 => uint256) public validationCount;
    mapping(bytes32 => mapping(address => bool)) public hasValidated;

    // Queen AI Proposal System
    enum ProposalType {
        UPDATE_RATE_LIMIT,
        ADD_RELAYER,
        REMOVE_RELAYER,
        ADD_VALIDATOR,
        REMOVE_VALIDATOR,
        UPDATE_REQUIRED_VALIDATIONS,
        PAUSE_BRIDGE,
        UNPAUSE_BRIDGE
    }

    struct BridgeProposal {
        uint256 id;
        address proposer;
        ProposalType proposalType;
        address targetAddress;
        uint256 newValue;
        string description;
        uint256 createdAt;
        bool approved;
        bool rejected;
        bool executed;
    }

    uint256 public proposalCount;
    mapping(uint256 => BridgeProposal) public proposals;

    // Lock/Release tracking
    struct BridgeTransaction {
        address user;
        uint256 amount;
        uint256 timestamp;
        bytes32 solanaAddress; // Target Solana address
        bool completed;
        TransactionType txType;
    }

    enum TransactionType {
        LOCK,    // Lock on Ethereum
        RELEASE  // Release on Ethereum
    }

    mapping(uint256 => BridgeTransaction) public transactions;
    mapping(bytes32 => bool) public processedSolanaProofs;

    // Events
    event TokensLocked(
        uint256 indexed nonce,
        address indexed user,
        uint256 amount,
        bytes32 solanaAddress,
        uint256 timestamp
    );
    event TokensReleased(
        uint256 indexed nonce,
        address indexed user,
        uint256 amount,
        bytes32 solanaProof,
        uint256 timestamp
    );
    event ValidatorApproved(
        bytes32 indexed txHash,
        address indexed validator,
        uint256 validationCount
    );
    event RelayerUpdated(address indexed oldRelayer, address indexed newRelayer);
    event RateLimitReset(uint256 timestamp);
    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        ProposalType proposalType,
        string description
    );
    event ProposalApproved(uint256 indexed proposalId, address indexed admin);
    event ProposalRejected(uint256 indexed proposalId, address indexed admin);
    event ProposalExecuted(uint256 indexed proposalId);
    event RateLimitUpdated(uint256 oldLimit, uint256 newLimit);

    constructor(
        address _omkToken,
        address _admin,
        address _queen,
        address[] memory _relayers,
        address[] memory _validators
    ) {
        require(_omkToken != address(0), "OMKBridge: Invalid token");
        require(_admin != address(0), "OMKBridge: Invalid admin");
        require(_queen != address(0), "OMKBridge: Invalid queen");

        omkToken = IERC20(_omkToken);
        lastResetTimestamp = block.timestamp;

        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(QUEEN_ROLE, _queen);

        // Setup relayers
        for (uint256 i = 0; i < _relayers.length; i++) {
            _grantRole(RELAYER_ROLE, _relayers[i]);
        }

        // Setup validators
        for (uint256 i = 0; i < _validators.length; i++) {
            _grantRole(VALIDATOR_ROLE, _validators[i]);
        }
    }

    // ============ LOCK TOKENS (ETH → SOL) ============

    /**
     * @notice Lock OMK tokens to bridge to Solana
     * @param amount Amount of tokens to lock
     * @param solanaAddress Target Solana wallet address (as bytes32)
     */
    function lockTokens(uint256 amount, bytes32 solanaAddress) 
        external 
        whenNotPaused 
        nonReentrant 
        returns (uint256) 
    {
        require(amount > 0, "OMKBridge: Invalid amount");
        require(solanaAddress != bytes32(0), "OMKBridge: Invalid Solana address");

        // Check rate limit
        _checkAndUpdateRateLimit(amount);

        // Transfer tokens to bridge
        omkToken.safeTransferFrom(msg.sender, address(this), amount);

        uint256 nonce = bridgeNonce++;
        totalLocked += amount;

        // Record transaction
        transactions[nonce] = BridgeTransaction({
            user: msg.sender,
            amount: amount,
            timestamp: block.timestamp,
            solanaAddress: solanaAddress,
            completed: true, // Lock is complete immediately
            txType: TransactionType.LOCK
        });

        emit TokensLocked(nonce, msg.sender, amount, solanaAddress, block.timestamp);

        return nonce;
    }

    // ============ RELEASE TOKENS (SOL → ETH) ============

    /**
     * @notice Release locked tokens after burning on Solana
     * @param to Recipient address on Ethereum
     * @param amount Amount to release
     * @param solanaProof Proof of burn on Solana (tx signature)
     */
    function releaseTokens(
        address to,
        uint256 amount,
        bytes32 solanaProof
    ) external onlyRole(RELAYER_ROLE) whenNotPaused nonReentrant returns (uint256) {
        require(to != address(0), "OMKBridge: Invalid recipient");
        require(amount > 0, "OMKBridge: Invalid amount");
        require(solanaProof != bytes32(0), "OMKBridge: Invalid proof");
        require(!processedSolanaProofs[solanaProof], "OMKBridge: Proof already processed");

        // Check rate limit
        _checkAndUpdateRateLimit(amount);

        // Create validation hash
        bytes32 txHash = keccak256(abi.encodePacked(to, amount, solanaProof));

        // Require multisig validation
        require(
            validationCount[txHash] >= requiredValidations,
            "OMKBridge: Insufficient validations"
        );

        // Mark proof as processed
        processedSolanaProofs[solanaProof] = true;

        uint256 nonce = bridgeNonce++;
        totalReleased += amount;

        // Record transaction
        transactions[nonce] = BridgeTransaction({
            user: to,
            amount: amount,
            timestamp: block.timestamp,
            solanaAddress: solanaProof, // Store proof as reference
            completed: true,
            txType: TransactionType.RELEASE
        });

        // Release tokens
        omkToken.safeTransfer(to, amount);

        emit TokensReleased(nonce, to, amount, solanaProof, block.timestamp);

        return nonce;
    }

    /**
     * @notice Validators approve release transaction
     */
    function validateRelease(
        address to,
        uint256 amount,
        bytes32 solanaProof
    ) external onlyRole(VALIDATOR_ROLE) {
        require(!processedSolanaProofs[solanaProof], "OMKBridge: Already processed");

        bytes32 txHash = keccak256(abi.encodePacked(to, amount, solanaProof));
        require(!hasValidated[txHash][msg.sender], "OMKBridge: Already validated");

        hasValidated[txHash][msg.sender] = true;
        validationCount[txHash]++;

        emit ValidatorApproved(txHash, msg.sender, validationCount[txHash]);
    }

    // ============ RATE LIMITING ============

    /**
     * @dev Check and update rate limit
     */
    function _checkAndUpdateRateLimit(uint256 amount) internal {
        // Reset daily counter if 24 hours passed
        if (block.timestamp >= lastResetTimestamp + 1 days) {
            dailyBridgeAmount = 0;
            lastResetTimestamp = block.timestamp;
            emit RateLimitReset(block.timestamp);
        }

        require(
            dailyBridgeAmount + amount <= maxDailyBridge,
            "OMKBridge: Daily limit exceeded"
        );

        dailyBridgeAmount += amount;
    }

    // ============ QUEEN AI PROPOSAL SYSTEM ============

    /**
     * @notice Queen AI proposes bridge changes
     */
    function proposeChange(
        ProposalType proposalType,
        address targetAddress,
        uint256 newValue,
        string calldata description
    ) external onlyRole(QUEEN_ROLE) returns (uint256) {
        uint256 proposalId = proposalCount++;

        BridgeProposal storage proposal = proposals[proposalId];
        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.proposalType = proposalType;
        proposal.targetAddress = targetAddress;
        proposal.newValue = newValue;
        proposal.description = description;
        proposal.createdAt = block.timestamp;

        emit ProposalCreated(proposalId, msg.sender, proposalType, description);

        return proposalId;
    }

    /**
     * @notice Admin approves Queen's proposal
     */
    function approveProposal(uint256 proposalId) external onlyRole(DEFAULT_ADMIN_ROLE) {
        BridgeProposal storage proposal = proposals[proposalId];
        require(!proposal.approved, "OMKBridge: Already approved");
        require(!proposal.rejected, "OMKBridge: Already rejected");
        require(!proposal.executed, "OMKBridge: Already executed");

        proposal.approved = true;

        emit ProposalApproved(proposalId, msg.sender);
    }

    /**
     * @notice Admin rejects Queen's proposal
     */
    function rejectProposal(uint256 proposalId) external onlyRole(DEFAULT_ADMIN_ROLE) {
        BridgeProposal storage proposal = proposals[proposalId];
        require(!proposal.approved, "OMKBridge: Already approved");
        require(!proposal.rejected, "OMKBridge: Already rejected");

        proposal.rejected = true;

        emit ProposalRejected(proposalId, msg.sender);
    }

    /**
     * @notice Execute approved proposal
     */
    function executeProposal(uint256 proposalId) external nonReentrant {
        BridgeProposal storage proposal = proposals[proposalId];
        require(proposal.approved, "OMKBridge: Not approved");
        require(!proposal.executed, "OMKBridge: Already executed");
        require(
            msg.sender == proposal.proposer || hasRole(DEFAULT_ADMIN_ROLE, msg.sender),
            "OMKBridge: Not authorized"
        );

        proposal.executed = true;

        // Execute based on proposal type
        if (proposal.proposalType == ProposalType.UPDATE_RATE_LIMIT) {
            uint256 oldLimit = maxDailyBridge;
            maxDailyBridge = proposal.newValue;
            emit RateLimitUpdated(oldLimit, proposal.newValue);

        } else if (proposal.proposalType == ProposalType.ADD_RELAYER) {
            _grantRole(RELAYER_ROLE, proposal.targetAddress);
            emit RelayerUpdated(address(0), proposal.targetAddress);

        } else if (proposal.proposalType == ProposalType.REMOVE_RELAYER) {
            _revokeRole(RELAYER_ROLE, proposal.targetAddress);
            emit RelayerUpdated(proposal.targetAddress, address(0));

        } else if (proposal.proposalType == ProposalType.ADD_VALIDATOR) {
            _grantRole(VALIDATOR_ROLE, proposal.targetAddress);

        } else if (proposal.proposalType == ProposalType.REMOVE_VALIDATOR) {
            _revokeRole(VALIDATOR_ROLE, proposal.targetAddress);

        } else if (proposal.proposalType == ProposalType.UPDATE_REQUIRED_VALIDATIONS) {
            requiredValidations = proposal.newValue;

        } else if (proposal.proposalType == ProposalType.PAUSE_BRIDGE) {
            _pause();

        } else if (proposal.proposalType == ProposalType.UNPAUSE_BRIDGE) {
            _unpause();
        }

        emit ProposalExecuted(proposalId);
    }

    // ============ ADMIN DIRECT FUNCTIONS (Emergency Override) ============

    /**
     * @notice Add relayer (Direct admin action, no proposal needed for emergencies)
     */
    function addRelayer(address relayer) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(relayer != address(0), "OMKBridge: Invalid relayer");
        _grantRole(RELAYER_ROLE, relayer);
        emit RelayerUpdated(address(0), relayer);
    }

    /**
     * @notice Remove relayer
     */
    function removeRelayer(address relayer) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _revokeRole(RELAYER_ROLE, relayer);
        emit RelayerUpdated(relayer, address(0));
    }

    /**
     * @notice Add validator
     */
    function addValidator(address validator) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(validator != address(0), "OMKBridge: Invalid validator");
        _grantRole(VALIDATOR_ROLE, validator);
    }

    /**
     * @notice Remove validator
     */
    function removeValidator(address validator) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _revokeRole(VALIDATOR_ROLE, validator);
    }

    /**
     * @notice Update required validations
     */
    function setRequiredValidations(uint256 required) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(required > 0, "OMKBridge: Invalid requirement");
        requiredValidations = required;
    }

    /**
     * @notice Emergency withdraw (admin only, for stuck tokens)
     */
    function emergencyWithdraw(address to, uint256 amount) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
        nonReentrant 
    {
        require(to != address(0), "OMKBridge: Invalid address");
        omkToken.safeTransfer(to, amount);
    }

    /**
     * @notice Pause bridge
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    /**
     * @notice Unpause bridge
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    // ============ VIEW FUNCTIONS ============

    /**
     * @notice Get bridge statistics
     */
    function getBridgeStats() external view returns (
        uint256 _totalLocked,
        uint256 _totalReleased,
        uint256 _bridgeNonce,
        uint256 _maxDailyBridge,
        uint256 _dailyRemaining,
        uint256 _lockedBalance
    ) {
        _totalLocked = totalLocked;
        _totalReleased = totalReleased;
        _bridgeNonce = bridgeNonce;
        _maxDailyBridge = maxDailyBridge;
        _dailyRemaining = maxDailyBridge > dailyBridgeAmount ? 
            maxDailyBridge - dailyBridgeAmount : 0;
        _lockedBalance = omkToken.balanceOf(address(this));
    }

    /**
     * @notice Get proposal details
     */
    function getProposal(uint256 proposalId) external view returns (
        address proposer,
        ProposalType proposalType,
        address targetAddress,
        uint256 newValue,
        string memory description,
        uint256 createdAt,
        bool approved,
        bool rejected,
        bool executed
    ) {
        BridgeProposal storage proposal = proposals[proposalId];
        return (
            proposal.proposer,
            proposal.proposalType,
            proposal.targetAddress,
            proposal.newValue,
            proposal.description,
            proposal.createdAt,
            proposal.approved,
            proposal.rejected,
            proposal.executed
        );
    }

    /**
     * @notice Get pending proposals count
     */
    function getPendingProposalsCount() external view returns (uint256) {
        uint256 pending = 0;
        for (uint256 i = 0; i < proposalCount; i++) {
            if (!proposals[i].approved && !proposals[i].rejected && !proposals[i].executed) {
                pending++;
            }
        }
        return pending;
    }

    /**
     * @notice Get transaction details
     */
    function getTransaction(uint256 nonce) external view returns (
        address user,
        uint256 amount,
        uint256 timestamp,
        bytes32 solanaAddress,
        bool completed,
        TransactionType txType
    ) {
        BridgeTransaction storage tx = transactions[nonce];
        return (
            tx.user,
            tx.amount,
            tx.timestamp,
            tx.solanaAddress,
            tx.completed,
            tx.txType
        );
    }

    /**
     * @notice Check if proof is processed
     */
    function isProofProcessed(bytes32 proof) external view returns (bool) {
        return processedSolanaProofs[proof];
    }

    /**
     * @notice Get validation status
     */
    function getValidationStatus(
        address to,
        uint256 amount,
        bytes32 solanaProof
    ) external view returns (uint256 validations, uint256 required, bool canExecute) {
        bytes32 txHash = keccak256(abi.encodePacked(to, amount, solanaProof));
        validations = validationCount[txHash];
        required = requiredValidations;
        canExecute = validations >= required && !processedSolanaProofs[solanaProof];
    }
}
