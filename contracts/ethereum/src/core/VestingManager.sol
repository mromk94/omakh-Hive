// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../utils/TokenVesting.sol";

/**
 * @title VestingManager
 * @dev Central manager for all vesting schedules (Founders, Advisors, Ecosystem)
 * 
 * Manages:
 * - Founders: 250M (12m cliff + 36m linear)
 * - Advisors: 20M (18m linear)
 * - Ecosystem: 100M (36m linear) - managed by Queen
 */
contract VestingManager is AccessControl {
    using SafeERC20 for IERC20;

    bytes32 public constant VESTING_ADMIN_ROLE = keccak256("VESTING_ADMIN_ROLE");

    IERC20 public immutable omkToken;
    
    // Vesting contracts
    TokenVesting public foundersVesting;
    TokenVesting public ecosystemVesting;
    // NOTE: Advisors managed by separate AdvisorsManager contract
    
    // Beneficiaries
    address public foundersWallet;
    address public ecosystemManager; // QueenAI's ecosystem manager
    address public advisorsManager; // AdvisorsManager contract (handles 40M dynamically)
    
    // Amounts
    uint256 public constant FOUNDERS_AMOUNT = 250_000_000 * 10**18;
    uint256 public constant ADVISORS_AMOUNT = 40_000_000 * 10**18; // Transferred to AdvisorsManager
    uint256 public constant ECOSYSTEM_AMOUNT = 100_000_000 * 10**18;
    
    // Events
    event VestingContractCreated(address indexed vestingContract, string vestingType, address indexed beneficiary);
    event TokensReleased(address indexed beneficiary, uint256 amount, string vestingType);
    event BeneficiaryUpdated(string vestingType, address oldBeneficiary, address newBeneficiary);

    constructor(
        address _omkToken,
        address _admin,
        address _foundersWallet,
        address _advisorsManager,
        address _ecosystemManager
    ) {
        require(_omkToken != address(0), "VestingManager: Invalid token");
        require(_admin != address(0), "VestingManager: Invalid admin");
        require(_foundersWallet != address(0), "VestingManager: Invalid founders wallet");
        require(_advisorsManager != address(0), "VestingManager: Invalid advisors manager");
        require(_ecosystemManager != address(0), "VestingManager: Invalid ecosystem manager");

        omkToken = IERC20(_omkToken);
        foundersWallet = _foundersWallet;
        advisorsManager = _advisorsManager;
        ecosystemManager = _ecosystemManager;
        
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(VESTING_ADMIN_ROLE, _admin);
        
        // Deploy vesting contracts (only Founders and Ecosystem)
        // Advisors handled by AdvisorsManager contract
        _deployVestingContracts();
    }

    /**
     * @dev Deploy vesting contracts (Founders and Ecosystem only)
     */
    function _deployVestingContracts() internal {
        // Founders: 12 month cliff + 36 month linear
        foundersVesting = new TokenVesting(address(omkToken), address(this));
        foundersVesting.createVestingSchedule(
            foundersWallet,
            FOUNDERS_AMOUNT,
            12, // 12 month cliff
            48, // 48 months total (12 cliff + 36 vesting)
            false // cliff then linear
        );
        emit VestingContractCreated(address(foundersVesting), "FOUNDERS", foundersWallet);
        
        // Ecosystem: 36 month linear (managed by Queen's EcosystemManager)
        ecosystemVesting = new TokenVesting(address(omkToken), address(this));
        ecosystemVesting.createVestingSchedule(
            ecosystemManager,
            ECOSYSTEM_AMOUNT,
            0, // No cliff
            36, // 36 months total
            true // linear from day 1
        );
        emit VestingContractCreated(address(ecosystemVesting), "ECOSYSTEM", ecosystemManager);
        
        // NOTE: Advisors managed by AdvisorsManager contract
        // 20M transferred directly to AdvisorsManager in fundVestingContracts()
    }

    /**
     * @notice Transfer tokens to vesting contracts and AdvisorsManager
     * @dev Called by OMKToken after deployment
     */
    function fundVestingContracts() external {
        // Transfer to vesting contracts
        omkToken.safeTransferFrom(msg.sender, address(foundersVesting), FOUNDERS_AMOUNT);
        omkToken.safeTransferFrom(msg.sender, address(ecosystemVesting), ECOSYSTEM_AMOUNT);
        
        // Transfer advisors pool to AdvisorsManager (they handle dynamic allocation)
        omkToken.safeTransferFrom(msg.sender, advisorsManager, ADVISORS_AMOUNT);
    }

    // ============ RELEASE FUNCTIONS ============

    /**
     * @notice Release vested tokens for founders
     */
    function releaseFoundersTokens() external {
        require(
            msg.sender == foundersWallet || hasRole(VESTING_ADMIN_ROLE, msg.sender),
            "VestingManager: Not authorized"
        );
        
        uint256 releasable = foundersVesting.getReleasableAmount(foundersWallet);
        require(releasable > 0, "VestingManager: No tokens to release");
        
        foundersVesting.release(foundersWallet);
        
        emit TokensReleased(foundersWallet, releasable, "FOUNDERS");
    }

    /**
     * @notice Release advisors tokens - NOW HANDLED BY AdvisorsManager
     * @dev Advisors should claim through AdvisorsManager.claimMyTokens()
     */
    function releaseAdvisorsTokens() external pure {
        revert("VestingManager: Use AdvisorsManager.claimMyTokens() instead");
    }

    /**
     * @notice Release ecosystem tokens (Queen's EcosystemManager calls this)
     */
    function releaseEcosystemTokens(uint256 amount) external {
        require(
            msg.sender == ecosystemManager || hasRole(VESTING_ADMIN_ROLE, msg.sender),
            "VestingManager: Not authorized"
        );
        
        uint256 releasable = ecosystemVesting.getReleasableAmount(ecosystemManager);
        require(amount <= releasable, "VestingManager: Amount exceeds releasable");
        
        // Transfer directly to ecosystem manager
        ecosystemVesting.release(ecosystemManager);
        
        emit TokensReleased(ecosystemManager, amount, "ECOSYSTEM");
    }

    // ============ VIEW FUNCTIONS ============

    /**
     * @notice Get founders vesting info
     */
    function getFoundersVestingInfo() external view returns (
        uint256 total,
        uint256 released,
        uint256 releasable,
        uint256 vested
    ) {
        total = FOUNDERS_AMOUNT;
        released = foundersVesting.getReleasedAmount(foundersWallet);
        releasable = foundersVesting.getReleasableAmount(foundersWallet);
        vested = foundersVesting.getVestedAmount(foundersWallet);
    }

    /**
     * @notice Get advisors pool info - NOW MANAGED BY AdvisorsManager
     * @dev For individual advisor info, query AdvisorsManager directly
     */
    function getAdvisorsVestingInfo() external pure returns (
        uint256 total,
        uint256 released,
        uint256 releasable,
        uint256 vested
    ) {
        // Return total pool, rest managed by AdvisorsManager
        total = ADVISORS_AMOUNT;
        released = 0;
        releasable = 0;
        vested = 0;
        // Query AdvisorsManager for actual distribution data
    }

    /**
     * @notice Get ecosystem vesting info
     */
    function getEcosystemVestingInfo() external view returns (
        uint256 total,
        uint256 released,
        uint256 releasable,
        uint256 vested
    ) {
        total = ECOSYSTEM_AMOUNT;
        released = ecosystemVesting.getReleasedAmount(ecosystemManager);
        releasable = ecosystemVesting.getReleasableAmount(ecosystemManager);
        vested = ecosystemVesting.getVestedAmount(ecosystemManager);
    }

    /**
     * @notice Get all vesting info at once
     */
    function getAllReleasableAmounts() external view returns (
        uint256 foundersReleasable,
        uint256 advisorsReleasable,
        uint256 ecosystemReleasable,
        uint256 totalLocked
    ) {
        foundersReleasable = foundersVesting.getReleasableAmount(foundersWallet);
        advisorsReleasable = 0; // Query AdvisorsManager for advisor details
        ecosystemReleasable = ecosystemVesting.getReleasableAmount(ecosystemManager);
        
        totalLocked = (FOUNDERS_AMOUNT + ADVISORS_AMOUNT + ECOSYSTEM_AMOUNT) - 
                     (foundersVesting.getReleasedAmount(foundersWallet) + 
                      ADVISORS_AMOUNT + // Advisors pool managed separately
                      ecosystemVesting.getReleasedAmount(ecosystemManager));
    }

    // ============ ADMIN FUNCTIONS ============

    /**
     * @notice Update founders wallet (emergency only)
     */
    function updateFoundersWallet(address newWallet) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(newWallet != address(0), "VestingManager: Invalid address");
        address oldWallet = foundersWallet;
        foundersWallet = newWallet;
        emit BeneficiaryUpdated("FOUNDERS", oldWallet, newWallet);
    }

    /**
     * @notice Update advisors manager address (if needed)
     */
    function updateAdvisorsManager(address newManager) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(newManager != address(0), "VestingManager: Invalid address");
        address oldManager = advisorsManager;
        advisorsManager = newManager;
        emit BeneficiaryUpdated("ADVISORS_MANAGER", oldManager, newManager);
    }
}
