// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title PrivateInvestorRegistry
 * @dev Manages pre-TGE private investor OTC allocations
 * 
 * Features:
 * - Admin-controlled wallet registry
 * - Pre-TGE allocation tracking
 * - Automatic distribution at TGE
 * - Vesting integration
 * - Full admin control (founder wallet)
 */
contract PrivateInvestorRegistry is AccessControl, ReentrancyGuard {
    
    bytes32 public constant REGISTRY_MANAGER_ROLE = keccak256("REGISTRY_MANAGER_ROLE");
    
    // OMK Token
    IERC20 public immutable omkToken;
    
    // TGE status
    bool public tgeExecuted;
    uint256 public tgeTimestamp;
    
    // Investor data
    struct Investor {
        address wallet;
        uint256 allocation;      // Total OMK allocated
        uint256 amountPaid;      // USD paid (tracked for records)
        uint256 pricePerToken;   // Price paid per token (in USD, 6 decimals)
        uint256 registeredAt;
        bool distributed;
        bool vestingSetup;
        address vestingContract;
        string investorId;       // Off-chain reference (e.g., "INV-001")
    }
    
    mapping(address => Investor) public investors;
    address[] public investorList;
    
    uint256 public totalAllocated;
    uint256 public totalDistributed;
    uint256 public constant MAX_ALLOCATION = 100_000_000 * 10**18; // 100M OMK max
    uint256 public constant MAX_INVESTORS = 65000; // HIGH-1 FIX: Limit to prevent gas issues (updated to 65k per user request)
    
    // Events
    event InvestorRegistered(address indexed wallet, uint256 allocation, string investorId);
    event InvestorUpdated(address indexed wallet, uint256 newAllocation);
    event InvestorRemoved(address indexed wallet);
    event TGEExecuted(uint256 timestamp, uint256 totalInvestors);
    event TokensDistributed(address indexed investor, uint256 amount);
    event VestingSetup(address indexed investor, address vestingContract);
    
    /**
     * @dev Constructor
     * @param _omkToken OMK token address
     * @param _admin Admin address (founder wallet)
     */
    constructor(address _omkToken, address _admin) {
        require(_omkToken != address(0), "PrivateInvestorRegistry: Invalid token");
        require(_admin != address(0), "PrivateInvestorRegistry: Invalid admin");
        
        omkToken = IERC20(_omkToken);
        
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(REGISTRY_MANAGER_ROLE, _admin);
    }
    
    // ============ INVESTOR MANAGEMENT ============
    
    /**
     * @notice Register a new private investor (pre-TGE)
     * @param wallet Investor's wallet address
     * @param allocation OMK tokens allocated
     * @param amountPaid USD amount paid (6 decimals, e.g., 10000 * 10**6 = $10,000)
     * @param pricePerToken Price per token in USD (6 decimals, e.g., 100000 = $0.10)
     * @param investorId Off-chain reference ID
     */
    function registerInvestor(
        address wallet,
        uint256 allocation,
        uint256 amountPaid,
        uint256 pricePerToken,
        string calldata investorId
    ) external onlyRole(REGISTRY_MANAGER_ROLE) {
        require(!tgeExecuted, "PrivateInvestorRegistry: TGE already executed");
        require(wallet != address(0), "PrivateInvestorRegistry: Invalid wallet");
        require(allocation > 0, "PrivateInvestorRegistry: Zero allocation");
        require(investors[wallet].wallet == address(0), "PrivateInvestorRegistry: Already registered");
        require(totalAllocated + allocation <= MAX_ALLOCATION, "PrivateInvestorRegistry: Exceeds max allocation");
        require(investorList.length < MAX_INVESTORS, "PrivateInvestorRegistry: Max investors reached");
        
        investors[wallet] = Investor({
            wallet: wallet,
            allocation: allocation,
            amountPaid: amountPaid,
            pricePerToken: pricePerToken,
            registeredAt: block.timestamp,
            distributed: false,
            vestingSetup: false,
            vestingContract: address(0),
            investorId: investorId
        });
        
        investorList.push(wallet);
        totalAllocated += allocation;
        
        emit InvestorRegistered(wallet, allocation, investorId);
    }
    
    /**
     * @notice Update investor allocation (pre-TGE only)
     * @param wallet Investor's wallet address
     * @param newAllocation New allocation amount
     */
    function updateInvestorAllocation(
        address wallet,
        uint256 newAllocation
    ) external onlyRole(REGISTRY_MANAGER_ROLE) {
        require(!tgeExecuted, "PrivateInvestorRegistry: TGE already executed");
        require(investors[wallet].wallet != address(0), "PrivateInvestorRegistry: Not registered");
        
        uint256 oldAllocation = investors[wallet].allocation;
        totalAllocated = totalAllocated - oldAllocation + newAllocation;
        
        require(totalAllocated <= MAX_ALLOCATION, "PrivateInvestorRegistry: Exceeds max allocation");
        
        investors[wallet].allocation = newAllocation;
        
        emit InvestorUpdated(wallet, newAllocation);
    }
    
    /**
     * @notice Remove investor (pre-TGE only, emergency)
     * @param wallet Investor's wallet address
     */
    function removeInvestor(address wallet) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(!tgeExecuted, "PrivateInvestorRegistry: TGE already executed");
        require(investors[wallet].wallet != address(0), "PrivateInvestorRegistry: Not registered");
        
        uint256 allocation = investors[wallet].allocation;
        totalAllocated -= allocation;
        
        delete investors[wallet];
        
        // Remove from list (expensive, but pre-TGE only)
        for (uint256 i = 0; i < investorList.length; i++) {
            if (investorList[i] == wallet) {
                investorList[i] = investorList[investorList.length - 1];
                investorList.pop();
                break;
            }
        }
        
        emit InvestorRemoved(wallet);
    }
    
    // ============ TGE EXECUTION ============
    
    /**
     * @notice Execute TGE - distribute tokens to all investors
     * @dev Can only be called once by admin
     */
    function executeTGE() external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
        require(!tgeExecuted, "PrivateInvestorRegistry: TGE already executed");
        require(investorList.length > 0, "PrivateInvestorRegistry: No investors");
        
        // Check contract has enough tokens
        uint256 contractBalance = omkToken.balanceOf(address(this));
        require(contractBalance >= totalAllocated, "PrivateInvestorRegistry: Insufficient tokens");
        
        tgeExecuted = true;
        tgeTimestamp = block.timestamp;
        
        emit TGEExecuted(block.timestamp, investorList.length);
    }
    
    /**
     * @notice Distribute tokens to specific investor (after TGE)
     * @param wallet Investor wallet
     */
    function distributeToInvestor(address wallet) external onlyRole(REGISTRY_MANAGER_ROLE) nonReentrant {
        require(tgeExecuted, "PrivateInvestorRegistry: TGE not executed");
        require(investors[wallet].wallet != address(0), "PrivateInvestorRegistry: Not registered");
        require(!investors[wallet].distributed, "PrivateInvestorRegistry: Already distributed");
        
        uint256 amount = investors[wallet].allocation;
        investors[wallet].distributed = true;
        totalDistributed += amount;
        
        require(omkToken.transfer(wallet, amount), "PrivateInvestorRegistry: Transfer failed");
        
        emit TokensDistributed(wallet, amount);
    }
    
    /**
     * @notice Batch distribute to multiple investors
     * @param wallets Array of investor wallets
     */
    function batchDistribute(address[] calldata wallets) external onlyRole(REGISTRY_MANAGER_ROLE) nonReentrant {
        require(tgeExecuted, "PrivateInvestorRegistry: TGE not executed");
        
        for (uint256 i = 0; i < wallets.length; i++) {
            address wallet = wallets[i];
            
            if (investors[wallet].wallet != address(0) && !investors[wallet].distributed) {
                uint256 amount = investors[wallet].allocation;
                investors[wallet].distributed = true;
                totalDistributed += amount;
                
                require(omkToken.transfer(wallet, amount), "PrivateInvestorRegistry: Transfer failed");
                
                emit TokensDistributed(wallet, amount);
            }
        }
    }
    
    /**
     * @notice Distribute to all pending investors (gas intensive, use carefully)
     */
    function distributeToAll() external onlyRole(REGISTRY_MANAGER_ROLE) nonReentrant {
        require(tgeExecuted, "PrivateInvestorRegistry: TGE not executed");
        
        for (uint256 i = 0; i < investorList.length; i++) {
            address wallet = investorList[i];
            
            if (!investors[wallet].distributed) {
                uint256 amount = investors[wallet].allocation;
                investors[wallet].distributed = true;
                totalDistributed += amount;
                
                require(omkToken.transfer(wallet, amount), "PrivateInvestorRegistry: Transfer failed");
                
                emit TokensDistributed(wallet, amount);
            }
        }
    }
    
    // ============ VESTING SETUP ============
    
    /**
     * @notice Link vesting contract to investor
     * @param wallet Investor wallet
     * @param vestingContract Vesting contract address
     */
    function setInvestorVesting(
        address wallet,
        address vestingContract
    ) external onlyRole(REGISTRY_MANAGER_ROLE) {
        require(investors[wallet].wallet != address(0), "PrivateInvestorRegistry: Not registered");
        require(vestingContract != address(0), "PrivateInvestorRegistry: Invalid vesting contract");
        
        investors[wallet].vestingContract = vestingContract;
        investors[wallet].vestingSetup = true;
        
        emit VestingSetup(wallet, vestingContract);
    }
    
    // ============ VIEW FUNCTIONS ============
    
    /**
     * @notice Get investor details
     */
    function getInvestor(address wallet) external view returns (
        uint256 allocation,
        uint256 amountPaid,
        uint256 pricePerToken,
        uint256 registeredAt,
        bool distributed,
        bool vestingSetup,
        address vestingContract,
        string memory investorId
    ) {
        Investor memory inv = investors[wallet];
        return (
            inv.allocation,
            inv.amountPaid,
            inv.pricePerToken,
            inv.registeredAt,
            inv.distributed,
            inv.vestingSetup,
            inv.vestingContract,
            inv.investorId
        );
    }
    
    /**
     * @notice Get all investors
     */
    function getAllInvestors() external view returns (address[] memory) {
        return investorList;
    }
    
    /**
     * @notice Get pending distributions
     */
    function getPendingDistributions() external view returns (address[] memory, uint256[] memory) {
        uint256 pendingCount = 0;
        for (uint256 i = 0; i < investorList.length; i++) {
            if (!investors[investorList[i]].distributed) {
                pendingCount++;
            }
        }
        
        address[] memory pendingWallets = new address[](pendingCount);
        uint256[] memory pendingAmounts = new uint256[](pendingCount);
        
        uint256 index = 0;
        for (uint256 i = 0; i < investorList.length; i++) {
            address wallet = investorList[i];
            if (!investors[wallet].distributed) {
                pendingWallets[index] = wallet;
                pendingAmounts[index] = investors[wallet].allocation;
                index++;
            }
        }
        
        return (pendingWallets, pendingAmounts);
    }
    
    /**
     * @notice Get registry statistics
     */
    function getStats() external view returns (
        uint256 totalInvestors,
        uint256 _totalAllocated,
        uint256 _totalDistributed,
        uint256 pendingDistribution,
        bool _tgeExecuted,
        uint256 _tgeTimestamp
    ) {
        return (
            investorList.length,
            totalAllocated,
            totalDistributed,
            totalAllocated - totalDistributed,
            tgeExecuted,
            tgeTimestamp
        );
    }
    
    /**
     * @notice Check if address is registered investor
     */
    function isInvestor(address wallet) external view returns (bool) {
        return investors[wallet].wallet != address(0);
    }
    
    // ============ EMERGENCY ============
    
    /**
     * @notice Emergency withdraw tokens (only admin, only before TGE)
     * @param amount Amount to withdraw
     */
    function emergencyWithdraw(uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
        require(!tgeExecuted, "PrivateInvestorRegistry: TGE already executed");
        require(omkToken.transfer(msg.sender, amount), "PrivateInvestorRegistry: Transfer failed");
    }
}
