// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title OMKDispenser
 * @notice Automated token dispenser for swapping assets for OMK tokens
 * @dev Controlled by Queen AI and Hive governance
 * 
 * Features:
 * - Instant swaps: ETH, USDT, USDC → OMK
 * - Dynamic pricing based on oracle
 * - Controlled by Queen (DISPENSER_ROLE)
 * - Emergency pause capability
 * - Slippage protection
 * - Multi-destination support (optional)
 */
contract OMKDispenser is AccessControl, ReentrancyGuard, Pausable {
    using SafeERC20 for IERC20;

    // ==================== ROLES ====================
    bytes32 public constant QUEEN_ROLE = keccak256("QUEEN_ROLE");
    bytes32 public constant DISPENSER_ROLE = keccak256("DISPENSER_ROLE");
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");

    // ==================== STATE ====================
    IERC20 public immutable omkToken;
    
    // Supported payment tokens
    mapping(address => bool) public supportedTokens;
    mapping(address => uint256) public tokenDecimals;
    
    // Pricing (in USD with 8 decimals, e.g., 10000000 = $0.10)
    mapping(address => uint256) public tokenPricesUSD; // Price per token in USD
    uint256 public omkPriceUSD; // OMK price in USD (8 decimals)
    
    // Limits
    uint256 public minSwapAmountUSD; // Minimum swap in USD (8 decimals)
    uint256 public maxSwapAmountUSD; // Maximum swap in USD (8 decimals)
    uint256 public dailyLimitUSD; // Daily limit per user
    
    // Tracking
    mapping(address => uint256) public dailySwapVolume; // User => USD amount today
    mapping(address => uint256) public lastSwapDay; // User => day number
    uint256 public totalSwapVolumeUSD;
    uint256 public totalOMKDispensed;
    
    // CRITICAL FIX: Price update controls
    mapping(address => uint256) public lastPriceUpdate; // Token => last update timestamp
    uint256 public constant PRICE_UPDATE_DELAY = 30 minutes; // Minimum time between updates
    uint256 public constant MAX_PRICE_CHANGE_PERCENT = 20; // 20% maximum change per update
    
    // Events
    event TokenSwapped(
        address indexed user,
        address indexed tokenIn,
        uint256 amountIn,
        uint256 omkOut,
        address recipient
    );
    event TokenPriceUpdated(address indexed token, uint256 newPrice);
    event OMKPriceUpdated(uint256 newPrice);
    event TokenSupportUpdated(address indexed token, bool supported);
    event LimitsUpdated(uint256 minSwap, uint256 maxSwap, uint256 dailyLimit);
    event OMKDeposited(uint256 amount);
    event OMKWithdrawn(uint256 amount);
    event FundsRecovered(address indexed token, uint256 amount);

    // ==================== CONSTRUCTOR ====================
    constructor(
        address _omkToken,
        address _admin,
        address _queen
    ) {
        require(_omkToken != address(0), "Invalid OMK token");
        require(_admin != address(0), "Invalid admin");
        require(_queen != address(0), "Invalid queen");

        omkToken = IERC20(_omkToken);
        
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(QUEEN_ROLE, _queen);
        _grantRole(DISPENSER_ROLE, _queen);
        _grantRole(ORACLE_ROLE, _admin);

        // Default limits (in USD with 8 decimals)
        minSwapAmountUSD = 100 * 10**8; // $100 minimum
        maxSwapAmountUSD = 100000 * 10**8; // $100k maximum
        dailyLimitUSD = 500000 * 10**8; // $500k per day per user

        // Default OMK price: $0.10
        omkPriceUSD = 10 * 10**6; // $0.10 in 8 decimals
    }

    // ==================== SWAP FUNCTIONS ====================
    
    /**
     * @notice Swap ETH for OMK tokens
     * @param minOMKOut Minimum OMK tokens expected (slippage protection)
     * @param recipient Address to receive OMK (optional, defaults to msg.sender)
     */
    function swapETHForOMK(
        uint256 minOMKOut,
        address recipient
    ) external payable nonReentrant whenNotPaused returns (uint256 omkOut) {
        require(msg.value > 0, "No ETH sent");
        require(supportedTokens[address(0)], "ETH not supported");
        
        if (recipient == address(0)) {
            recipient = msg.sender;
        }

        // Calculate OMK amount
        omkOut = _calculateOMKAmount(address(0), msg.value);
        require(omkOut >= minOMKOut, "Slippage exceeded");

        // Check limits
        uint256 swapValueUSD = _calculateUSDValue(address(0), msg.value);
        _checkLimits(msg.sender, swapValueUSD);

        // Update tracking
        _updateTracking(msg.sender, swapValueUSD, omkOut);

        // Transfer OMK to recipient
        require(omkToken.balanceOf(address(this)) >= omkOut, "Insufficient OMK");
        omkToken.safeTransfer(recipient, omkOut);

        emit TokenSwapped(msg.sender, address(0), msg.value, omkOut, recipient);
    }

    /**
     * @notice Swap ERC20 token for OMK tokens
     * @param tokenIn Address of token to swap
     * @param amountIn Amount of tokens to swap
     * @param minOMKOut Minimum OMK tokens expected
     * @param recipient Address to receive OMK (optional)
     */
    function swapTokenForOMK(
        address tokenIn,
        uint256 amountIn,
        uint256 minOMKOut,
        address recipient
    ) external nonReentrant whenNotPaused returns (uint256 omkOut) {
        require(tokenIn != address(0), "Invalid token");
        require(amountIn > 0, "Amount must be > 0");
        require(supportedTokens[tokenIn], "Token not supported");

        if (recipient == address(0)) {
            recipient = msg.sender;
        }

        // Transfer token from user
        IERC20(tokenIn).safeTransferFrom(msg.sender, address(this), amountIn);

        // Calculate OMK amount
        omkOut = _calculateOMKAmount(tokenIn, amountIn);
        require(omkOut >= minOMKOut, "Slippage exceeded");

        // Check limits
        uint256 swapValueUSD = _calculateUSDValue(tokenIn, amountIn);
        _checkLimits(msg.sender, swapValueUSD);

        // Update tracking
        _updateTracking(msg.sender, swapValueUSD, omkOut);

        // Transfer OMK to recipient
        require(omkToken.balanceOf(address(this)) >= omkOut, "Insufficient OMK");
        omkToken.safeTransfer(recipient, omkOut);

        emit TokenSwapped(msg.sender, tokenIn, amountIn, omkOut, recipient);
    }

    // ==================== VIEW FUNCTIONS ====================

    /**
     * @notice Get quote for swap
     * @param tokenIn Address of input token (address(0) for ETH)
     * @param amountIn Amount of input token
     * @return omkOut Amount of OMK tokens user will receive
     * @return valueUSD USD value of swap
     */
    function getSwapQuote(
        address tokenIn,
        uint256 amountIn
    ) external view returns (uint256 omkOut, uint256 valueUSD) {
        require(supportedTokens[tokenIn], "Token not supported");
        omkOut = _calculateOMKAmount(tokenIn, amountIn);
        valueUSD = _calculateUSDValue(tokenIn, amountIn);
    }

    /**
     * @notice Check if user can swap
     * @param user User address
     * @param amountUSD Amount in USD (8 decimals)
     */
    function canSwap(address user, uint256 amountUSD) external view returns (bool) {
        if (amountUSD < minSwapAmountUSD || amountUSD > maxSwapAmountUSD) {
            return false;
        }

        uint256 currentDay = block.timestamp / 1 days;
        if (lastSwapDay[user] == currentDay) {
            if (dailySwapVolume[user] + amountUSD > dailyLimitUSD) {
                return false;
            }
        }

        return true;
    }

    /**
     * @notice Get user's remaining daily limit
     */
    function getRemainingDailyLimit(address user) external view returns (uint256) {
        uint256 currentDay = block.timestamp / 1 days;
        if (lastSwapDay[user] != currentDay) {
            return dailyLimitUSD;
        }
        if (dailySwapVolume[user] >= dailyLimitUSD) {
            return 0;
        }
        return dailyLimitUSD - dailySwapVolume[user];
    }

    /**
     * @notice Get available OMK balance in dispenser
     */
    function getAvailableOMK() external view returns (uint256) {
        return omkToken.balanceOf(address(this));
    }

    // ==================== INTERNAL FUNCTIONS ====================

    function _calculateOMKAmount(address tokenIn, uint256 amountIn) internal view returns (uint256) {
        // Get token price in USD
        uint256 tokenPrice = tokenPricesUSD[tokenIn];
        require(tokenPrice > 0, "Price not set");

        // Get token decimals
        uint256 decimals = tokenIn == address(0) ? 18 : tokenDecimals[tokenIn];
        
        // Calculate USD value: (amountIn * tokenPrice) / 10^decimals
        uint256 valueUSD = (amountIn * tokenPrice) / (10**decimals);

        // Calculate OMK amount: (valueUSD * 10^18) / omkPriceUSD
        uint256 omkAmount = (valueUSD * 10**18) / omkPriceUSD;

        return omkAmount;
    }

    function _calculateUSDValue(address tokenIn, uint256 amountIn) internal view returns (uint256) {
        uint256 tokenPrice = tokenPricesUSD[tokenIn];
        uint256 decimals = tokenIn == address(0) ? 18 : tokenDecimals[tokenIn];
        return (amountIn * tokenPrice) / (10**decimals);
    }

    function _checkLimits(address user, uint256 swapValueUSD) internal view {
        require(swapValueUSD >= minSwapAmountUSD, "Below minimum");
        require(swapValueUSD <= maxSwapAmountUSD, "Above maximum");

        uint256 currentDay = block.timestamp / 1 days;
        if (lastSwapDay[user] == currentDay) {
            require(
                dailySwapVolume[user] + swapValueUSD <= dailyLimitUSD,
                "Daily limit exceeded"
            );
        }
    }

    function _updateTracking(address user, uint256 swapValueUSD, uint256 omkOut) internal {
        uint256 currentDay = block.timestamp / 1 days;
        
        if (lastSwapDay[user] != currentDay) {
            dailySwapVolume[user] = 0;
            lastSwapDay[user] = currentDay;
        }

        dailySwapVolume[user] += swapValueUSD;
        totalSwapVolumeUSD += swapValueUSD;
        totalOMKDispensed += omkOut;
    }

    // ==================== ADMIN FUNCTIONS ====================

    /**
     * @notice Add/update supported token
     */
    function setSupportedToken(
        address token,
        bool supported,
        uint256 decimals,
        uint256 priceUSD
    ) external onlyRole(DISPENSER_ROLE) {
        supportedTokens[token] = supported;
        if (supported) {
            tokenDecimals[token] = decimals;
            tokenPricesUSD[token] = priceUSD;
        }
        emit TokenSupportUpdated(token, supported);
    }

    /**
     * @notice Update token price (Oracle role)
     * CRITICAL FIX: Now includes time-lock and maximum change limits
     */
    function updateTokenPrice(address token, uint256 newPrice) external onlyRole(ORACLE_ROLE) {
        require(supportedTokens[token], "Token not supported");
        require(newPrice > 0, "Price must be positive");
        
        // Check time delay
        require(
            block.timestamp >= lastPriceUpdate[token] + PRICE_UPDATE_DELAY,
            "OMKDispenser: Price update too soon"
        );
        
        uint256 oldPrice = tokenPricesUSD[token];
        
        // Allow first-time price setting without limit
        if (oldPrice > 0) {
            // Calculate max allowed change
            uint256 maxIncrease = oldPrice + (oldPrice * MAX_PRICE_CHANGE_PERCENT) / 100;
            uint256 maxDecrease = oldPrice - (oldPrice * MAX_PRICE_CHANGE_PERCENT) / 100;
            
            require(
                newPrice >= maxDecrease && newPrice <= maxIncrease,
                "OMKDispenser: Price change exceeds limit"
            );
        }
        
        tokenPricesUSD[token] = newPrice;
        lastPriceUpdate[token] = block.timestamp;
        emit TokenPriceUpdated(token, newPrice);
    }

    /**
     * @notice Update OMK price
     * CRITICAL FIX: Now includes time-lock and maximum change limits
     */
    function updateOMKPrice(uint256 newPrice) external onlyRole(ORACLE_ROLE) {
        require(newPrice > 0, "Invalid price");
        
        // Use address(omkToken) as key for OMK price updates
        address key = address(omkToken);
        
        // Check time delay
        require(
            block.timestamp >= lastPriceUpdate[key] + PRICE_UPDATE_DELAY,
            "OMKDispenser: Price update too soon"
        );
        
        uint256 oldPrice = omkPriceUSD;
        
        // Allow first-time price setting without limit
        if (oldPrice > 0) {
            // Calculate max allowed change
            uint256 maxIncrease = oldPrice + (oldPrice * MAX_PRICE_CHANGE_PERCENT) / 100;
            uint256 maxDecrease = oldPrice - (oldPrice * MAX_PRICE_CHANGE_PERCENT) / 100;
            
            require(
                newPrice >= maxDecrease && newPrice <= maxIncrease,
                "OMKDispenser: Price change exceeds limit"
            );
        }
        
        omkPriceUSD = newPrice;
        lastPriceUpdate[key] = block.timestamp;
        emit OMKPriceUpdated(newPrice);
    }

    /**
     * @notice Update swap limits
     */
    function updateLimits(
        uint256 _minSwap,
        uint256 _maxSwap,
        uint256 _dailyLimit
    ) external onlyRole(DISPENSER_ROLE) {
        minSwapAmountUSD = _minSwap;
        maxSwapAmountUSD = _maxSwap;
        dailyLimitUSD = _dailyLimit;
        emit LimitsUpdated(_minSwap, _maxSwap, _dailyLimit);
    }

    /**
     * @notice Deposit OMK tokens into dispenser
     */
    function depositOMK(uint256 amount) external onlyRole(DISPENSER_ROLE) {
        omkToken.safeTransferFrom(msg.sender, address(this), amount);
        emit OMKDeposited(amount);
    }

    /**
     * @notice Withdraw OMK tokens from dispenser
     */
    function withdrawOMK(uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        omkToken.safeTransfer(msg.sender, amount);
        emit OMKWithdrawn(amount);
    }

    /**
     * @notice Recover stuck tokens
     */
    function recoverTokens(address token, uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (token == address(0)) {
            payable(msg.sender).transfer(amount);
        } else {
            IERC20(token).safeTransfer(msg.sender, amount);
        }
        emit FundsRecovered(token, amount);
    }

    /**
     * @notice Pause/unpause dispenser
     */
    function pause() external onlyRole(QUEEN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(QUEEN_ROLE) {
        _unpause();
    }

    // Allow contract to receive ETH
    receive() external payable {}
}
