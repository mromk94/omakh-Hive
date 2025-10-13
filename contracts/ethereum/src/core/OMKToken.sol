// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "../utils/TokenVesting.sol";

/**
 * @title OMKToken
 * @notice ERC-20 token for OMK Hive ecosystem with advanced vesting
 * @dev Includes pausable, burnable, and role-based access features
 */
contract OMKToken is ERC20, ERC20Burnable, ERC20Pausable, AccessControl {
    // Token distribution constants
    uint256 public constant TOTAL_SUPPLY = 1_000_000_000 * 10**18; // 1 billion tokens
    uint256 public constant FOUNDERS_AMOUNT = 250_000_000 * 10**18; // 25%
    uint256 public constant PRIVATE_INVESTORS_AMOUNT = 100_000_000 * 10**18; // 10%
    uint256 public constant ECOSYSTEM_AMOUNT = 100_000_000 * 10**18; // 10%
    uint256 public constant ADVISORS_AMOUNT = 40_000_000 * 10**18; // 4%
    uint256 public constant BREAKSWITCH_AMOUNT = 10_000_000 * 10**18; // 1%
    uint256 public constant TREASURY_AMOUNT = 100_000_000 * 10**18; // 10%
    uint256 public constant PUBLIC_ACQUISITION_AMOUNT = 400_000_000 * 10**18; // 40% (immediately available to Queen AI for market operations)

    // Roles
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant QUEEN_ROLE = keccak256("QUEEN_ROLE");
    bytes32 public constant VESTING_MANAGER_ROLE = keccak256("VESTING_MANAGER_ROLE");
    bytes32 public constant ECOSYSTEM_MANAGER_ROLE = keccak256("ECOSYSTEM_MANAGER_ROLE");

    // Addresses
    address public queenAddress;
    address public treasuryAddress;

    // Vesting contracts
    TokenVesting public foundersVesting;
    TokenVesting public advisorsVesting;
    TokenVesting public ecosystemVesting;
    
    // Private sale contract (manages 100M private investor tokens)
    address public privateSaleContract;

    // Whitelist
    mapping(address => bool) public isWhitelisted;

    // Queen Safeguards - Rate Limiting
    uint256 public constant MAX_QUEEN_DAILY_TRANSFER = 10_000_000 * 10**18; // 5% of total supply per day
    uint256 public constant LARGE_TRANSFER_THRESHOLD = 20_000_000 * 10**18; // 10% of total supply
    uint256 public lastQueenTransferDay;
    uint256 public todayQueenTransfers;
    bool public queenRateLimitEnabled = true;

    // Circuit Breaker - Global Volume Limits
    uint256 public maxDailyVolume = 50_000_000 * 10**18;  // 50M OMK/day (5% of supply)
    uint256 public dailyVolume;
    uint256 public lastVolumeReset;
    bool public circuitBreakerEnabled = true;

    // Events
    event WhitelistUpdated(address indexed account, bool isWhitelisted);
    event TreasuryUpdated(address indexed newTreasury);
    event VestingContractDeployed(address indexed vestingContract, string vestingType);
    event TokensTransferredToQueen(address indexed queen, uint256 amount);
    event QueenTransfer(address indexed from, address indexed to, uint256 amount, uint256 dailyTotal);
    event QueenRateLimitToggled(bool enabled);
    event LargeTransferAttempt(address indexed from, address indexed to, uint256 amount);
    event TokensDistributed();
    event CircuitBreakerTriggered(uint256 attemptedVolume, uint256 dailyLimit);
    event CircuitBreakerReset(uint256 timestamp);
    event MaxDailyVolumeUpdated(uint256 oldLimit, uint256 newLimit);

    /**
     * @dev Constructor that initializes the token with the given name and symbol
     * @param name_ Name of the token
     * @param symbol_ Symbol of the token
     * @param admin_ Address of the admin who will have all roles initially
     * @param treasury_ Address of the treasury wallet
     * @param queen_ Address of the Queen AI
     * @param founders_ Address of the founders' wallet
     * @param advisors_ Address of the advisors' wallet
     */
    constructor(
        string memory name_,
        string memory symbol_,
        address admin_,
        address treasury_,
        address queen_,
        address founders_,
        address advisors_
    ) ERC20(name_, symbol_) {
        require(admin_ != address(0), "OMKToken: admin is zero address");
        require(treasury_ != address(0), "OMKToken: treasury is zero address");
        require(queen_ != address(0), "OMKToken: queen is zero address");
        require(founders_ != address(0), "OMKToken: founders address is zero");
        require(advisors_ != address(0), "OMKToken: advisors address is zero");

        // Set up roles
        _grantRole(DEFAULT_ADMIN_ROLE, admin_);
        _grantRole(MINTER_ROLE, admin_);
        _grantRole(PAUSER_ROLE, admin_);
        _grantRole(QUEEN_ROLE, queen_);
        _grantRole(VESTING_MANAGER_ROLE, admin_);
        _grantRole(ECOSYSTEM_MANAGER_ROLE, queen_);

        // Set addresses
        treasuryAddress = treasury_;
        queenAddress = queen_;
        
        // Mint initial supply to the contract
        _mint(address(this), TOTAL_SUPPLY);

        // Deploy vesting contracts (excluding private sale - handled separately)
        _deployVestingContracts(admin_, founders_, advisors_);

        // Distribute initial allocations
        _distributeInitialAllocations(founders_, advisors_);
        
        // Note: 100M PRIVATE_INVESTORS tokens remain in contract
        // They will be transferred to PrivateSale contract when it's deployed
    }

    /**
     * @dev Deploys all necessary vesting contracts
     */
    function _deployVestingContracts(
        address admin_,
        address founders_,
        address advisors_
    ) internal {
        // Deploy Founders vesting (25% cliff at 12 months, then monthly over 3 years)
        foundersVesting = new TokenVesting(address(this), admin_);
        foundersVesting.createVestingSchedule(
            founders_,
            FOUNDERS_AMOUNT,
            12, // 12 months cliff
            48, // 48 months total (12 cliff + 36 vesting)
            false // Cliff then linear
        );
        emit VestingContractDeployed(address(foundersVesting), "FOUNDERS");

        // Deploy Advisors vesting (12-month cliff + 18-month linear)
        advisorsVesting = new TokenVesting(address(this), admin_);
        advisorsVesting.createVestingSchedule(
            advisors_,
            ADVISORS_AMOUNT,
            12, // 12 month cliff
            30, // 30 months total (12 cliff + 18 vesting)
            false // Cliff then linear
        );
        emit VestingContractDeployed(address(advisorsVesting), "ADVISORS");

        // Deploy Ecosystem vesting (released via staking rewards and grants over 3 years)
        ecosystemVesting = new TokenVesting(address(this), admin_);
        ecosystemVesting.createVestingSchedule(
            address(this), // Will be managed by Queen AI
            ECOSYSTEM_AMOUNT,
            0, // No cliff
            36, // 36 months
            true // Linear vesting
        );
        emit VestingContractDeployed(address(ecosystemVesting), "ECOSYSTEM");

        // Public Acquisition tokens are immediately available to Queen AI for market operations
        _transfer(address(this), queenAddress, PUBLIC_ACQUISITION_AMOUNT);
        emit TokensTransferredToQueen(queenAddress, PUBLIC_ACQUISITION_AMOUNT);
    }

    /**
     * @dev Distributes initial token allocations
     */
    function _distributeInitialAllocations(
        address founders_,
        address advisors_
    ) internal {
        // Transfer breakswitch amount to admin (immediately available)
        _transfer(address(this), msg.sender, BREAKSWITCH_AMOUNT);

        // Transfer treasury amount to treasury address
        _transfer(address(this), treasuryAddress, TREASURY_AMOUNT);

        // Transfer tokens to vesting contracts
        _transfer(address(this), address(foundersVesting), FOUNDERS_AMOUNT);
        _transfer(address(this), address(advisorsVesting), ADVISORS_AMOUNT);
        _transfer(address(this), address(ecosystemVesting), ECOSYSTEM_AMOUNT);
        
        // PRIVATE_INVESTORS_AMOUNT (100M) remains in contract for PrivateSale

        // Verify total supply matches all allocations
        uint256 expectedDistribution = 
            FOUNDERS_AMOUNT +
            PRIVATE_INVESTORS_AMOUNT +
            ECOSYSTEM_AMOUNT +
            ADVISORS_AMOUNT +
            BREAKSWITCH_AMOUNT +
            TREASURY_AMOUNT +
            PUBLIC_ACQUISITION_AMOUNT;
        
        require(
            expectedDistribution == TOTAL_SUPPLY,
            "OMKToken: Supply allocation mismatch"
        );
        
        emit TokensDistributed();
    }

    /**
     * @notice Whitelists admin and important addresses
     */
    function _whitelistImportantAddresses(
        address founders_,
        address advisors_
    ) internal {
        isWhitelisted[msg.sender] = true;
        isWhitelisted[treasuryAddress] = true;
        isWhitelisted[founders_] = true;
        isWhitelisted[advisors_] = true;
    }

    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    /**
     * @notice Sets the Queen contract address
     * @dev Only callable by addresses with QUEEN_ROLE
     * @param _queenAddress Address of the Queen contract
     */
    function setQueenAddress(address _queenAddress) external onlyRole(QUEEN_ROLE) {
        require(_queenAddress != address(0), "OMKToken: queen is zero address");
        queenAddress = _queenAddress;
    }

    /**
     * @notice Sets the PrivateSale contract and transfers 100M tokens to it
     * @dev Only callable once by DEFAULT_ADMIN_ROLE
     * @param _privateSaleContract Address of the PrivateSale contract
     */
    function setPrivateSaleContract(address _privateSaleContract) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_privateSaleContract != address(0), "OMKToken: private sale is zero address");
        require(privateSaleContract == address(0), "OMKToken: private sale already set");
        
        privateSaleContract = _privateSaleContract;
        
        // Transfer 100M OMK tokens to PrivateSale contract
        _transfer(address(this), _privateSaleContract, PRIVATE_INVESTORS_AMOUNT);
        
        // Whitelist the PrivateSale contract
        isWhitelisted[_privateSaleContract] = true;
    }

    /**
     * @notice Updates the treasury address
     * @dev Only callable by DEFAULT_ADMIN_ROLE
     * @param newTreasury New treasury address
     */
    function updateTreasury(address newTreasury) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(newTreasury != address(0), "OMKToken: treasury is zero address");
        treasuryAddress = newTreasury;
        emit TreasuryUpdated(newTreasury);
    }

    /**
     * @notice Adds or removes an address from the transfer whitelist
     * @dev Only callable by addresses with DEFAULT_ADMIN_ROLE
     * @param account Address to update
     * @param whitelisted Whether to add or remove from whitelist
     */
    function setWhitelisted(address account, bool whitelisted) external onlyRole(DEFAULT_ADMIN_ROLE) {
        isWhitelisted[account] = whitelisted;
        emit WhitelistUpdated(account, whitelisted);
    }

    /**
     * @notice Toggle Queen AI rate limiting
     * @dev Only callable by DEFAULT_ADMIN_ROLE. Allows emergency override of rate limits
     * @param enabled Whether to enable or disable rate limiting
     */
    function setQueenRateLimitEnabled(bool enabled) external onlyRole(DEFAULT_ADMIN_ROLE) {
        queenRateLimitEnabled = enabled;
        emit QueenRateLimitToggled(enabled);
    }

    /**
     * @notice Get Queen's current daily transfer stats
     * @return currentDay Current day timestamp
     * @return transferredToday Amount transferred today
     * @return remainingToday Amount remaining for today
     * @return rateLimitActive Whether rate limiting is active
     */
    function getQueenTransferStats() external view returns (
        uint256 currentDay,
        uint256 transferredToday,
        uint256 remainingToday,
        bool rateLimitActive
    ) {
        currentDay = block.timestamp / 1 days;
        
        // If it's a new day, transfers reset to 0
        if (currentDay > lastQueenTransferDay) {
            transferredToday = 0;
        } else {
            transferredToday = todayQueenTransfers;
        }
        
        remainingToday = MAX_QUEEN_DAILY_TRANSFER > transferredToday 
            ? MAX_QUEEN_DAILY_TRANSFER - transferredToday 
            : 0;
        
        rateLimitActive = queenRateLimitEnabled;
    }

    // ============ CIRCUIT BREAKER MANAGEMENT ============

    /**
     * @notice Set maximum daily volume (SecurityCouncil can adjust during emergency)
     * @param newLimit New daily volume limit
     */
    function setMaxDailyVolume(uint256 newLimit) external onlyRole(DEFAULT_ADMIN_ROLE) {
        uint256 oldLimit = maxDailyVolume;
        maxDailyVolume = newLimit;
        emit MaxDailyVolumeUpdated(oldLimit, newLimit);
    }

    /**
     * @notice Toggle circuit breaker
     * @param enabled Whether to enable or disable circuit breaker
     */
    function setCircuitBreakerEnabled(bool enabled) external onlyRole(DEFAULT_ADMIN_ROLE) {
        circuitBreakerEnabled = enabled;
    }

    /**
     * @notice Get circuit breaker stats
     */
    function getCircuitBreakerStats() external view returns (
        uint256 _maxDailyVolume,
        uint256 _dailyVolume,
        uint256 remainingVolume,
        bool enabled
    ) {
        uint256 currentDay = block.timestamp / 1 days;
        uint256 lastDay = lastVolumeReset / 1 days;
        
        // If new day, volume resets to 0
        uint256 currentVolume = (currentDay > lastDay) ? 0 : dailyVolume;
        
        return (
            maxDailyVolume,
            currentVolume,
            maxDailyVolume > currentVolume ? maxDailyVolume - currentVolume : 0,
            circuitBreakerEnabled
        );
    }

    /**
     * @dev Override _beforeTokenTransfer for OpenZeppelin 4.x compatibility
     * @notice This is called BEFORE balance updates
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override(ERC20, ERC20Pausable) {
        // Call parent pause check first
        super._beforeTokenTransfer(from, to, amount);
        
        // Allow whitelisted addresses to transfer when paused
        if (paused() && !isWhitelisted[from] && !isWhitelisted[to]) {
            require(
                from == address(0) || to == address(0),
                "OMKToken: token transfer while paused"
            );
        }

        // Circuit Breaker - Global Volume Limit (skip for minting/burning/whitelisted)
        if (circuitBreakerEnabled && 
            from != address(0) && 
            to != address(0) && 
            !isWhitelisted[from] && 
            !isWhitelisted[to]) {
            
            uint256 currentDay = block.timestamp / 1 days;
            uint256 lastDay = lastVolumeReset / 1 days;
            
            // Reset daily volume at day boundary
            if (currentDay > lastDay) {
                dailyVolume = 0;
                lastVolumeReset = currentDay * 1 days;
                emit CircuitBreakerReset(lastVolumeReset);
            }
            
            // Check circuit breaker
            if (dailyVolume + amount > maxDailyVolume) {
                emit CircuitBreakerTriggered(dailyVolume + amount, maxDailyVolume);
                revert("OMKToken: Circuit breaker triggered - daily volume limit exceeded");
            }
            
            dailyVolume += amount;
        }

        // Apply Queen rate limiting (if enabled)
        if (queenRateLimitEnabled && from == queenAddress && to != address(0) && to != address(this)) {
            uint256 today = block.timestamp / 1 days;
            
            // Reset daily counter if new day
            if (today > lastQueenTransferDay) {
                todayQueenTransfers = 0;
                lastQueenTransferDay = today;
            }
            
            // Check daily limit
            require(
                todayQueenTransfers + amount <= MAX_QUEEN_DAILY_TRANSFER,
                "OMKToken: Queen daily transfer limit exceeded"
            );
            
            // Update daily total
            todayQueenTransfers += amount;
            
            // Emit monitoring events
            emit QueenTransfer(from, to, amount, todayQueenTransfers);
            
            // Alert on large transfers
            if (amount >= LARGE_TRANSFER_THRESHOLD) {
                emit LargeTransferAttempt(from, to, amount);
            }
        }
    }
    
    /**
     * @notice Release vested tokens for a beneficiary
     * @param beneficiary Address of the beneficiary
     */
    function releaseVestedTokens(address beneficiary) external {
        require(
            msg.sender == beneficiary || hasRole(VESTING_MANAGER_ROLE, msg.sender),
            "OMKToken: not authorized to release tokens"
        );
        
        if (address(foundersVesting) != address(0)) {
            foundersVesting.release(beneficiary);
        }
        if (address(advisorsVesting) != address(0)) {
            advisorsVesting.release(beneficiary);
        }
        // Note: Private investors use PrivateSale contract for vesting
    }
    
    /**
     * @notice Release ecosystem tokens to a recipient
     * @param recipient Address to receive the tokens
     * @param amount Amount of tokens to release
     */
    function releaseEcosystemTokens(address recipient, uint256 amount) external onlyRole(ECOSYSTEM_MANAGER_ROLE) {
        require(amount > 0, "OMKToken: amount is zero");
        
        // Get the available amount
        uint256 availableAmount = getAvailableEcosystemTokens();
        require(amount <= availableAmount, "OMKToken: amount exceeds available ecosystem tokens");
        
        // Transfer the tokens to the recipient
        _transfer(address(this), recipient, amount);
    }
    
    /**
     * @notice Get the amount of tokens available for release from the ecosystem pool
     * @return Amount of tokens that can be released
     */
    function getAvailableEcosystemTokens() public view returns (uint256) {
        // In a real implementation, you would calculate the vested amount based on the vesting schedule
        // For now, we'll return the contract's balance as available
        return balanceOf(address(this));
    }
}
