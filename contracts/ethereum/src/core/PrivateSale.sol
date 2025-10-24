// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../utils/TokenVesting.sol";

/**
 * @title PrivateSale
 * @dev Manages the private sale of OMK tokens with tiered pricing and whale limits
 * 
 * Private Sale Structure:
 * - Total: 100M OMK tokens
 * - 10 tiers of 10M tokens each
 * - Prices from $0.100 to $0.145 per token
 * - Whale limit: 20M OMK per investor
 * - Managed by Queen AI for off-chain portal integration
 * 
 * Vesting: 12-month cliff + 18-month linear vesting
 */
contract PrivateSale is AccessControl, Pausable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // Roles
    bytes32 public constant SALE_MANAGER_ROLE = keccak256("SALE_MANAGER_ROLE"); // Queen AI
    bytes32 public constant TREASURER_ROLE = keccak256("TREASURER_ROLE");

    // OMK Token
    IERC20 public immutable omkToken;
    
    // Sale parameters
    uint256 public constant TOTAL_SALE_AMOUNT = 100_000_000 * 10**18; // 100M tokens
    uint256 public constant TIER_SIZE = 10_000_000 * 10**18; // 10M tokens per tier
    uint256 public constant WHALE_LIMIT = 20_000_000 * 10**18; // 20M max per investor
    uint256 public constant TOTAL_TIERS = 10;
    uint256 public constant MAX_RAISE_USD = 12_250_000 * 10**6; // $12.25M max raise (6 decimals)
    uint256 public constant MIN_PURCHASE = 2000 * 10**18; // 2000 OMK minimum purchase (updated per user request)

    // Tier pricing (in mills = $0.001, so 100 = $0.100)
    uint256[TOTAL_TIERS] public tierPrices = [
        100, // Tier 0: $0.100 (10.0 cents)
        105, // Tier 1: $0.105 (10.5 cents)
        110, // Tier 2: $0.110 (11.0 cents)
        115, // Tier 3: $0.115 (11.5 cents)
        120, // Tier 4: $0.120 (12.0 cents)
        125, // Tier 5: $0.125 (12.5 cents)
        130, // Tier 6: $0.130 (13.0 cents)
        135, // Tier 7: $0.135 (13.5 cents)
        140, // Tier 8: $0.140 (14.0 cents)
        145  // Tier 9: $0.145 (14.5 cents)
    ];

    // Sale state
    uint256 public totalSold;
    uint256 public currentTier;
    uint256 public soldInCurrentTier;
    bool public saleActive;
    address public fundsRecipient; // Treasury address
    
    // Investor tracking
    struct Investment {
        uint256 totalPurchased;    // Total OMK purchased
        uint256 totalPaidUSD;      // Total USD paid (in wei equivalent)
        uint256 lastPurchaseTime;  // Timestamp of last purchase
        bool isWhitelisted;        // KYC/Whitelist status
        address vestingContract;   // TokenVesting contract for this investor
    }
    
    mapping(address => Investment) public investments;
    mapping(uint256 => uint256) public tierSales; // Track sales per tier
    
    // Payment tokens (stablecoins)
    mapping(address => bool) public acceptedPaymentTokens;
    
    // Vesting parameters (12-month cliff + 18-month linear)
    uint256 public constant VESTING_CLIFF_MONTHS = 12;
    uint256 public constant VESTING_DURATION_MONTHS = 30; // 12 cliff + 18 vesting
    
    // Events
    event SaleActivated(uint256 timestamp);
    event SaleDeactivated(uint256 timestamp);
    event TokensPurchased(
        address indexed buyer,
        uint256 amount,
        uint256 tier,
        uint256 pricePerToken,
        address paymentToken,
        uint256 paymentAmount
    );
    event InvestorWhitelisted(address indexed investor, bool status);
    event PaymentTokenUpdated(address indexed token, bool accepted);
    event FundsWithdrawn(address indexed token, uint256 amount, address indexed recipient);
    event TierAdvanced(uint256 newTier, uint256 timestamp);
    event VestingSetupComplete(address indexed investor, address indexed vestingContract, uint256 amount);

    constructor(
        address _omkToken,
        address _fundsRecipient,
        address _admin,
        address _queenManager
    ) {
        require(_omkToken != address(0), "PrivateSale: Invalid token address");
        require(_fundsRecipient != address(0), "PrivateSale: Invalid funds recipient");
        require(_admin != address(0), "PrivateSale: Invalid admin address");
        require(_queenManager != address(0), "PrivateSale: Invalid manager address");

        omkToken = IERC20(_omkToken);
        fundsRecipient = _fundsRecipient;
        
        // Set up roles
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(SALE_MANAGER_ROLE, _queenManager); // Queen AI manages the sale
        _grantRole(TREASURER_ROLE, _admin);
        
        // Initialize sale state
        currentTier = 0;
        soldInCurrentTier = 0;
        totalSold = 0;
        saleActive = false;
    }

    // ============ SALE MANAGEMENT ============

    /**
     * @notice Activate the private sale
     * @dev Only callable by SALE_MANAGER_ROLE (Queen AI)
     */
    function activateSale() external onlyRole(SALE_MANAGER_ROLE) {
        require(!saleActive, "PrivateSale: Sale already active");
        saleActive = true;
        emit SaleActivated(block.timestamp);
    }

    /**
     * @notice Deactivate the private sale
     * @dev Only callable by SALE_MANAGER_ROLE (Queen AI)
     */
    function deactivateSale() external onlyRole(SALE_MANAGER_ROLE) {
        require(saleActive, "PrivateSale: Sale not active");
        saleActive = false;
        emit SaleDeactivated(block.timestamp);
    }

    /**
     * @notice Whitelist an investor (KYC approved)
     * @param investor Address of the investor
     * @param status Whitelist status
     */
    function setInvestorWhitelist(address investor, bool status) 
        external 
        onlyRole(SALE_MANAGER_ROLE) 
    {
        investments[investor].isWhitelisted = status;
        emit InvestorWhitelisted(investor, status);
    }

    /**
     * @notice Batch whitelist investors
     * @param investors Array of investor addresses
     * @param status Whitelist status for all
     */
    function batchWhitelist(address[] calldata investors, bool status)
        external
        onlyRole(SALE_MANAGER_ROLE)
    {
        for (uint256 i = 0; i < investors.length; i++) {
            investments[investors[i]].isWhitelisted = status;
            emit InvestorWhitelisted(investors[i], status);
        }
    }

    /**
     * @notice Add or remove accepted payment token
     * @param token Address of the payment token (stablecoin)
     * @param accepted Whether to accept this token
     */
    function setPaymentToken(address token, bool accepted)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        acceptedPaymentTokens[token] = accepted;
        emit PaymentTokenUpdated(token, accepted);
    }

    // ============ PURCHASE FUNCTIONS ============

    /**
     * @notice Purchase OMK tokens with a stablecoin
     * @param amount Amount of OMK tokens to purchase
     * @param paymentToken Address of the stablecoin to pay with
     * @param maxPayment Maximum payment amount willing to pay (slippage protection)
     */
    function purchaseTokens(
        uint256 amount,
        address paymentToken,
        uint256 maxPayment
    ) external nonReentrant whenNotPaused {
        require(saleActive, "PrivateSale: Sale not active");
        require(investments[msg.sender].isWhitelisted, "PrivateSale: Not whitelisted");
        require(acceptedPaymentTokens[paymentToken], "PrivateSale: Payment token not accepted");
        require(amount >= MIN_PURCHASE, "PrivateSale: Below minimum purchase");
        
        // Check whale limit
        uint256 newTotal = investments[msg.sender].totalPurchased + amount;
        require(newTotal <= WHALE_LIMIT, "PrivateSale: Exceeds whale limit (20M)");
        
        // Check if enough tokens available
        require(totalSold + amount <= TOTAL_SALE_AMOUNT, "PrivateSale: Exceeds total sale amount");
        
        // Calculate payment required
        uint256 paymentRequired = calculatePayment(amount);
        require(paymentRequired <= maxPayment, "PrivateSale: Payment exceeds maximum");
        
        // HIGH-3 FIX: Check USD raise cap
        uint256 currentRaised = getTotalRaisedUSD();
        require(currentRaised + paymentRequired <= MAX_RAISE_USD, "PrivateSale: Max raise exceeded");
        
        // Process the purchase
        _processPurchase(msg.sender, amount, paymentToken, paymentRequired);
    }

    /**
     * @notice Internal function to process a purchase
     */
    function _processPurchase(
        address buyer,
        uint256 amount,
        address paymentToken,
        uint256 payment
    ) internal {
        uint256 remainingAmount = amount;
        uint256 tier = currentTier;
        
        // Transfer payment from buyer
        IERC20(paymentToken).safeTransferFrom(buyer, fundsRecipient, payment);
        
        // Allocate tokens across tiers if necessary
        while (remainingAmount > 0 && tier < TOTAL_TIERS) {
            uint256 availableInTier = TIER_SIZE - tierSales[tier];
            uint256 toAllocate = remainingAmount > availableInTier ? availableInTier : remainingAmount;
            
            tierSales[tier] += toAllocate;
            remainingAmount -= toAllocate;
            
            if (tierSales[tier] >= TIER_SIZE && tier < TOTAL_TIERS - 1) {
                tier++;
                emit TierAdvanced(tier, block.timestamp);
            }
        }
        
        // Update state
        totalSold += amount;
        currentTier = tier;
        soldInCurrentTier = tierSales[tier];
        
        // Update investor record (tokens stay in PrivateSale contract until vesting setup)
        investments[buyer].totalPurchased += amount;
        investments[buyer].totalPaidUSD += payment;
        investments[buyer].lastPurchaseTime = block.timestamp;
        
        emit TokensPurchased(buyer, amount, tier, tierPrices[tier], paymentToken, payment);
    }

    /**
     * @notice Calculate payment required for a given amount of tokens
     * @param amount Amount of OMK tokens to purchase
     * @return payment Payment required in USD (6 decimals for USDC/USDT)
     */
    function calculatePayment(uint256 amount) public view returns (uint256 payment) {
        uint256 remainingAmount = amount;
        uint256 tier = currentTier;
        payment = 0;
        
        while (remainingAmount > 0 && tier < TOTAL_TIERS) {
            uint256 availableInTier = TIER_SIZE - tierSales[tier];
            uint256 toAllocate = remainingAmount > availableInTier ? availableInTier : remainingAmount;
            
            // Price in mills ($0.001), convert to 6 decimals (USDC/USDT)
            // tierPrices[tier] is in mills (100 = $0.100)
            // toAllocate is in 18 decimals (OMK)
            // Result should be in 6 decimals (USDC)
            // FIX: Rearrange to minimize precision loss
            // (toAllocate / 10**12) first, then multiply, then divide
            uint256 tierPayment = (toAllocate / 10**12) * tierPrices[tier] / 1000;
            payment += tierPayment;
            
            remainingAmount -= toAllocate;
            
            if (tierSales[tier] + toAllocate >= TIER_SIZE) {
                tier++;
            }
        }
        
        require(remainingAmount == 0, "PrivateSale: Insufficient tokens available");
    }

    // ============ VIEW FUNCTIONS ============

    /**
     * @notice Get current sale status
     */
    function getSaleStatus() external view returns (
        uint256 _totalSold,
        uint256 _currentTier,
        uint256 _soldInCurrentTier,
        uint256 _currentPrice,
        uint256 _remainingInTier,
        bool _isActive
    ) {
        _totalSold = totalSold;
        _currentTier = currentTier;
        _soldInCurrentTier = tierSales[currentTier];
        _currentPrice = tierPrices[currentTier];
        _remainingInTier = TIER_SIZE - tierSales[currentTier];
        _isActive = saleActive;
    }

    /**
     * @notice Get investor details
     */
    function getInvestorInfo(address investor) external view returns (
        uint256 totalPurchased,
        uint256 totalPaidUSD,
        uint256 remainingAllocation,
        bool isWhitelisted
    ) {
        Investment memory inv = investments[investor];
        totalPurchased = inv.totalPurchased;
        totalPaidUSD = inv.totalPaidUSD;
        remainingAllocation = WHALE_LIMIT - inv.totalPurchased;
        isWhitelisted = inv.isWhitelisted;
    }

    /**
     * @notice Get all tier sales data
     */
    function getAllTierSales() external view returns (uint256[TOTAL_TIERS] memory) {
        uint256[TOTAL_TIERS] memory sales;
        for (uint256 i = 0; i < TOTAL_TIERS; i++) {
            sales[i] = tierSales[i];
        }
        return sales;
    }

    /**
     * @notice Setup vesting for an investor (after sale ends)
     * @param investor Address of the investor
     */
    function setupVestingForInvestor(address investor)
        external
        onlyRole(SALE_MANAGER_ROLE)
        whenNotPaused
    {
        require(investments[investor].totalPurchased > 0, "PrivateSale: No tokens purchased");
        require(investments[investor].vestingContract == address(0), "PrivateSale: Vesting already setup");
        
        uint256 amount = investments[investor].totalPurchased;
        
        // CRITICAL FIX: Check balance BEFORE any operations
        require(omkToken.balanceOf(address(this)) >= amount, "PrivateSale: Insufficient balance");
        
        // Create vesting contract
        TokenVesting vesting = new TokenVesting(address(omkToken), address(this));
        
        // Transfer tokens to vesting contract
        omkToken.safeTransfer(address(vesting), amount);
        
        // Create vesting schedule (12m cliff + 18m linear)
        vesting.createVestingSchedule(
            investor,
            amount,
            VESTING_CLIFF_MONTHS,
            VESTING_DURATION_MONTHS,
            false // Cliff then linear (25% at cliff, 75% linear)
        );
        
        // CRITICAL FIX: Set address ONLY after all operations succeed
        investments[investor].vestingContract = address(vesting);
        
        emit VestingSetupComplete(investor, address(vesting), amount);
    }

    /**
     * @notice Batch setup vesting for multiple investors
     * @param investors Array of investor addresses
     */
    function batchSetupVesting(address[] calldata investors)
        external
        onlyRole(SALE_MANAGER_ROLE)
        whenNotPaused
    {
        for (uint256 i = 0; i < investors.length; i++) {
            if (investments[investors[i]].totalPurchased > 0 && 
                investments[investors[i]].vestingContract == address(0)) {
                
                uint256 amount = investments[investors[i]].totalPurchased;
                
                // CRITICAL FIX: Check balance BEFORE operations
                require(omkToken.balanceOf(address(this)) >= amount, "PrivateSale: Insufficient balance");
                
                // Create vesting contract
                TokenVesting vesting = new TokenVesting(address(omkToken), address(this));
                
                // Transfer tokens to vesting contract
                omkToken.safeTransfer(address(vesting), amount);
                
                // Create vesting schedule
                vesting.createVestingSchedule(
                    investors[i],
                    amount,
                    VESTING_CLIFF_MONTHS,
                    VESTING_DURATION_MONTHS,
                    false
                );
                
                // CRITICAL FIX: Set address ONLY after all operations succeed
                investments[investors[i]].vestingContract = address(vesting);
                
                emit VestingSetupComplete(investors[i], address(vesting), amount);
            }
        }
    }

    /**
     * @notice Calculate total raised USD (estimated)
     */
    function getTotalRaisedUSD() public view returns (uint256 totalUSD) {
        for (uint256 i = 0; i < TOTAL_TIERS; i++) {
            // tierSales[i] is in 18 decimals (OMK)
            // tierPrices[i] is in mills ($0.001)
            // Result in 6 decimals (USD)
            totalUSD += (tierSales[i] * tierPrices[i]) / (1000 * 10**12);
        }
    }

    // ============ ADMIN FUNCTIONS ============

    /**
     * @notice Withdraw funds to treasury
     * @param token Address of the token to withdraw (0x0 for ETH)
     * @param amount Amount to withdraw
     */
    function withdrawFunds(address token, uint256 amount)
        external
        onlyRole(TREASURER_ROLE)
        nonReentrant
    {
        if (token == address(0)) {
            // Withdraw ETH
            (bool success, ) = fundsRecipient.call{value: amount}("");
            require(success, "PrivateSale: ETH transfer failed");
        } else {
            // Withdraw ERC20
            IERC20(token).safeTransfer(fundsRecipient, amount);
        }
        
        emit FundsWithdrawn(token, amount, fundsRecipient);
    }

    /**
     * @notice Update funds recipient address
     */
    function setFundsRecipient(address newRecipient)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        require(newRecipient != address(0), "PrivateSale: Invalid recipient");
        fundsRecipient = newRecipient;
    }

    /**
     * @notice Emergency pause
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    /**
     * @notice Unpause
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @notice Receive ETH
     */
    receive() external payable {}
}
