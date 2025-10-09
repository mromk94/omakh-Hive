// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title Fractionalizer
 * @dev Tokenize and fractionalize real-world assets using ERC1155
 * 
 * Asset Types:
 * - Real estate properties
 * - Revenue-generating assets
 * - Tokenized investments
 * 
 * Features:
 * - Asset tokenization (ERC721-like unique asset)
 * - Fractionalization into ERC1155 shares
 * - Marketplace for share trading
 * - Rent/revenue distribution
 * - Asset revaluation
 * - KYC integration hooks
 */
contract Fractionalizer is ERC1155, AccessControl, Pausable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    bytes32 public constant ASSET_MANAGER_ROLE = keccak256("ASSET_MANAGER_ROLE");
    bytes32 public constant KYC_ROLE = keccak256("KYC_ROLE");

    enum AssetType {
        REAL_ESTATE,
        REVENUE_ASSET,
        TOKENIZED_INVESTMENT,
        OTHER
    }

    enum AssetStatus {
        PENDING,        // Awaiting approval
        ACTIVE,         // Live and tradable
        PAUSED,         // Trading paused
        LIQUIDATED      // Asset sold/closed
    }

    struct Asset {
        uint256 assetId;
        AssetType assetType;
        AssetStatus status;
        string name;
        string metadataURI; // IPFS hash
        address owner;
        uint256 totalValue; // In USD (wei)
        uint256 totalShares;
        uint256 availableShares;
        uint256 pricePerShare; // In payment token (wei)
        uint256 createdAt;
        uint256 lastValuation;
        bool isFramentalized;
    }

    struct ShareListing {
        uint256 assetId;
        address seller;
        uint256 shares;
        uint256 pricePerShare;
        bool active;
    }

    // Storage
    uint256 public assetCount;
    mapping(uint256 => Asset) public assets;
    mapping(uint256 => mapping(address => bool)) public kycApproved; // assetId => address => approved

    uint256 public listingCount;
    mapping(uint256 => ShareListing) public listings;
    mapping(uint256 => uint256[]) public assetListings; // assetId => listingIds

    // Revenue tracking
    mapping(uint256 => uint256) public totalRevenueDistributed;
    mapping(uint256 => mapping(address => uint256)) public claimedRevenue;

    // Payment token (e.g., USDC)
    IERC20 public paymentToken;

    // Events
    event AssetTokenized(
        uint256 indexed assetId,
        AssetType assetType,
        string name,
        uint256 totalValue,
        address indexed owner
    );
    event AssetFractionalized(
        uint256 indexed assetId,
        uint256 totalShares,
        uint256 pricePerShare
    );
    event SharesListed(
        uint256 indexed listingId,
        uint256 indexed assetId,
        address indexed seller,
        uint256 shares,
        uint256 pricePerShare
    );
    event SharesPurchased(
        uint256 indexed listingId,
        uint256 indexed assetId,
        address indexed buyer,
        uint256 shares,
        uint256 totalPrice
    );
    event RevenueDistributed(
        uint256 indexed assetId,
        uint256 amount,
        uint256 perShare
    );
    event AssetRevalued(
        uint256 indexed assetId,
        uint256 oldValue,
        uint256 newValue
    );
    event KYCApproved(uint256 indexed assetId, address indexed user);

    constructor(
        address _admin,
        address _paymentToken,
        string memory _baseURI
    ) ERC1155(_baseURI) {
        require(_paymentToken != address(0), "Fractionalizer: Invalid payment token");

        paymentToken = IERC20(_paymentToken);

        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(ASSET_MANAGER_ROLE, _admin);
        _grantRole(KYC_ROLE, _admin);
    }

    // ============ ASSET TOKENIZATION ============

    /**
     * @notice Tokenize a new asset
     */
    function tokenizeAsset(
        AssetType assetType,
        string calldata name,
        string calldata metadataURI,
        uint256 totalValue
    ) external onlyRole(ASSET_MANAGER_ROLE) returns (uint256) {
        require(totalValue > 0, "Fractionalizer: Invalid value");

        uint256 assetId = assetCount++;

        Asset storage asset = assets[assetId];
        asset.assetId = assetId;
        asset.assetType = assetType;
        asset.status = AssetStatus.PENDING;
        asset.name = name;
        asset.metadataURI = metadataURI;
        asset.owner = msg.sender;
        asset.totalValue = totalValue;
        asset.createdAt = block.timestamp;
        asset.lastValuation = block.timestamp;
        asset.isFramentalized = false;

        emit AssetTokenized(assetId, assetType, name, totalValue, msg.sender);

        return assetId;
    }

    /**
     * @notice Fractionalize asset into shares
     */
    function fractionalize(
        uint256 assetId,
        uint256 totalShares,
        uint256 pricePerShare
    ) external onlyRole(ASSET_MANAGER_ROLE) {
        Asset storage asset = assets[assetId];
        require(!asset.isFramentalized, "Fractionalizer: Already fractionalized");
        require(totalShares > 0, "Fractionalizer: Invalid shares");
        require(pricePerShare > 0, "Fractionalizer: Invalid price");

        asset.totalShares = totalShares;
        asset.availableShares = totalShares;
        asset.pricePerShare = pricePerShare;
        asset.isFramentalized = true;
        asset.status = AssetStatus.ACTIVE;

        // Mint shares to contract (to be sold)
        _mint(address(this), assetId, totalShares, "");

        emit AssetFractionalized(assetId, totalShares, pricePerShare);
    }

    // ============ MARKETPLACE ============

    /**
     * @notice List shares for sale
     */
    function listForSale(
        uint256 assetId,
        uint256 shares,
        uint256 pricePerShare
    ) external whenNotPaused nonReentrant returns (uint256) {
        Asset storage asset = assets[assetId];
        require(asset.status == AssetStatus.ACTIVE, "Fractionalizer: Asset not active");
        require(asset.isFramentalized, "Fractionalizer: Not fractionalized");
        require(kycApproved[assetId][msg.sender], "Fractionalizer: KYC required");
        require(shares > 0, "Fractionalizer: Invalid shares");
        require(balanceOf(msg.sender, assetId) >= shares, "Fractionalizer: Insufficient shares");

        uint256 listingId = listingCount++;

        ShareListing storage listing = listings[listingId];
        listing.assetId = assetId;
        listing.seller = msg.sender;
        listing.shares = shares;
        listing.pricePerShare = pricePerShare;
        listing.active = true;

        assetListings[assetId].push(listingId);

        // Transfer shares to escrow
        _safeTransferFrom(msg.sender, address(this), assetId, shares, "");

        emit SharesListed(listingId, assetId, msg.sender, shares, pricePerShare);

        return listingId;
    }

    /**
     * @notice Purchase shares from listing
     */
    function purchaseShares(uint256 listingId) external whenNotPaused nonReentrant {
        ShareListing storage listing = listings[listingId];
        require(listing.active, "Fractionalizer: Listing not active");
        require(kycApproved[listing.assetId][msg.sender], "Fractionalizer: KYC required");

        uint256 totalPrice = listing.shares * listing.pricePerShare;

        // Transfer payment
        paymentToken.safeTransferFrom(msg.sender, listing.seller, totalPrice);

        // Transfer shares
        _safeTransferFrom(address(this), msg.sender, listing.assetId, listing.shares, "");

        // Mark listing as inactive
        listing.active = false;

        emit SharesPurchased(listingId, listing.assetId, msg.sender, listing.shares, totalPrice);
    }

    /**
     * @notice Cancel listing
     */
    function cancelListing(uint256 listingId) external nonReentrant {
        ShareListing storage listing = listings[listingId];
        require(listing.active, "Fractionalizer: Listing not active");
        require(listing.seller == msg.sender, "Fractionalizer: Not seller");

        // Return shares to seller
        _safeTransferFrom(address(this), msg.sender, listing.assetId, listing.shares, "");

        listing.active = false;
    }

    // ============ REVENUE DISTRIBUTION ============

    /**
     * @notice Distribute revenue to shareholders
     */
    function distributeRevenue(uint256 assetId, uint256 amount) 
        external 
        onlyRole(ASSET_MANAGER_ROLE) 
        nonReentrant 
    {
        Asset storage asset = assets[assetId];
        require(asset.isFramentalized, "Fractionalizer: Not fractionalized");
        require(amount > 0, "Fractionalizer: Invalid amount");

        // Transfer revenue to contract
        paymentToken.safeTransferFrom(msg.sender, address(this), amount);

        totalRevenueDistributed[assetId] += amount;

        uint256 perShare = amount / asset.totalShares;

        emit RevenueDistributed(assetId, amount, perShare);
    }

    /**
     * @notice Claim revenue share
     */
    function claimRevenue(uint256 assetId) external nonReentrant {
        Asset storage asset = assets[assetId];
        require(asset.isFramentalized, "Fractionalizer: Not fractionalized");

        uint256 shares = balanceOf(msg.sender, assetId);
        require(shares > 0, "Fractionalizer: No shares owned");

        uint256 totalRevenue = totalRevenueDistributed[assetId];
        uint256 perShare = totalRevenue / asset.totalShares;
        uint256 entitled = shares * perShare;
        uint256 claimed = claimedRevenue[assetId][msg.sender];

        require(entitled > claimed, "Fractionalizer: Nothing to claim");

        uint256 toClaim = entitled - claimed;
        claimedRevenue[assetId][msg.sender] = entitled;

        paymentToken.safeTransfer(msg.sender, toClaim);
    }

    // ============ ASSET MANAGEMENT ============

    /**
     * @notice Update asset valuation
     */
    function updateAssetValue(uint256 assetId, uint256 newValue) 
        external 
        onlyRole(ASSET_MANAGER_ROLE) 
    {
        Asset storage asset = assets[assetId];
        require(newValue > 0, "Fractionalizer: Invalid value");

        uint256 oldValue = asset.totalValue;
        asset.totalValue = newValue;
        asset.lastValuation = block.timestamp;

        // Update price per share proportionally
        if (asset.isFramentalized) {
            asset.pricePerShare = newValue / asset.totalShares;
        }

        emit AssetRevalued(assetId, oldValue, newValue);
    }

    /**
     * @notice Approve KYC for user
     */
    function approveKYC(uint256 assetId, address user) external onlyRole(KYC_ROLE) {
        kycApproved[assetId][user] = true;
        emit KYCApproved(assetId, user);
    }

    /**
     * @notice Batch approve KYC
     */
    function batchApproveKYC(uint256 assetId, address[] calldata users) external onlyRole(KYC_ROLE) {
        for (uint256 i = 0; i < users.length; i++) {
            kycApproved[assetId][users[i]] = true;
            emit KYCApproved(assetId, users[i]);
        }
    }

    /**
     * @notice Pause asset trading
     */
    function pauseAsset(uint256 assetId) external onlyRole(ASSET_MANAGER_ROLE) {
        assets[assetId].status = AssetStatus.PAUSED;
    }

    /**
     * @notice Resume asset trading
     */
    function resumeAsset(uint256 assetId) external onlyRole(ASSET_MANAGER_ROLE) {
        assets[assetId].status = AssetStatus.ACTIVE;
    }

    // ============ VIEW FUNCTIONS ============

    /**
     * @notice Get asset details
     */
    function getAsset(uint256 assetId) external view returns (
        AssetType assetType,
        AssetStatus status,
        string memory name,
        uint256 totalValue,
        uint256 totalShares,
        uint256 availableShares,
        uint256 pricePerShare
    ) {
        Asset storage asset = assets[assetId];
        return (
            asset.assetType,
            asset.status,
            asset.name,
            asset.totalValue,
            asset.totalShares,
            asset.availableShares,
            asset.pricePerShare
        );
    }

    /**
     * @notice Get asset listings
     */
    function getAssetListings(uint256 assetId) external view returns (uint256[] memory) {
        return assetListings[assetId];
    }

    /**
     * @notice Get claimable revenue
     */
    function getClaimableRevenue(uint256 assetId, address user) external view returns (uint256) {
        Asset storage asset = assets[assetId];
        if (!asset.isFramentalized) return 0;

        uint256 shares = balanceOf(user, assetId);
        if (shares == 0) return 0;

        uint256 totalRevenue = totalRevenueDistributed[assetId];
        uint256 perShare = totalRevenue / asset.totalShares;
        uint256 entitled = shares * perShare;
        uint256 claimed = claimedRevenue[assetId][user];

        return entitled > claimed ? entitled - claimed : 0;
    }

    // ============ ADMIN FUNCTIONS ============

    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    function setURI(string memory newuri) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _setURI(newuri);
    }

    // Required override
    function supportsInterface(bytes4 interfaceId) 
        public 
        view 
        override(ERC1155, AccessControl) 
        returns (bool) 
    {
        return super.supportsInterface(interfaceId);
    }
}
