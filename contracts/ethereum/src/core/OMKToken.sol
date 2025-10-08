// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title OMKToken
 * @notice ERC-20 token for OMK Hive ecosystem
 * @dev Includes pausable, burnable, and role-based access features
 */
contract OMKToken is ERC20, ERC20Burnable, ERC20Pausable, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant QUEEN_ROLE = keccak256("QUEEN_ROLE");

    /// @notice Maximum total supply (760M tokens)
    uint256 public constant MAX_SUPPLY = 760_000_000 * 10**18;

    /// @notice Queen Controller contract address
    address public queenController;

    /// @notice Learning function observer contract
    address public learningObserver;

    /// @notice Emitted when tokens are minted
    event TokensMinted(address indexed to, uint256 amount);

    /// @notice Emitted when Queen Controller is updated
    event QueenControllerUpdated(address indexed oldController, address indexed newController);

    /// @notice Emitted when transfer is logged for learning
    event TransferLogged(address indexed from, address indexed to, uint256 amount, uint256 timestamp);

    constructor(
        string memory name,
        string memory symbol,
        address admin
    ) ERC20(name, symbol) {
        require(admin != address(0), "OMKToken: admin is zero address");
        
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(MINTER_ROLE, admin);
        _grantRole(PAUSER_ROLE, admin);
    }

    /**
     * @notice Mint tokens (only MINTER_ROLE)
     * @param to Recipient address
     * @param amount Amount to mint
     */
    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        require(totalSupply() + amount <= MAX_SUPPLY, "OMKToken: max supply exceeded");
        _mint(to, amount);
        emit TokensMinted(to, amount);
    }

    /**
     * @notice Pause token transfers (only PAUSER_ROLE)
     */
    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    /**
     * @notice Unpause token transfers (only PAUSER_ROLE)
     */
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    /**
     * @notice Set Queen Controller address
     * @param _queenController New Queen Controller address
     */
    function setQueenController(address _queenController) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_queenController != address(0), "OMKToken: zero address");
        address oldController = queenController;
        queenController = _queenController;
        _grantRole(QUEEN_ROLE, _queenController);
        if (oldController != address(0)) {
            _revokeRole(QUEEN_ROLE, oldController);
        }
        emit QueenControllerUpdated(oldController, _queenController);
    }

    /**
     * @notice Set learning observer address
     * @param _observer Learning observer contract address
     */
    function setLearningObserver(address _observer) external onlyRole(DEFAULT_ADMIN_ROLE) {
        learningObserver = _observer;
    }

    /**
     * @dev Override _update to add learning function hook
     */
    function _update(
        address from,
        address to,
        uint256 amount
    ) internal virtual override(ERC20, ERC20Pausable) {
        super._update(from, to, amount);
        
        // Log transfer for learning function
        if (learningObserver != address(0) && from != address(0) && to != address(0)) {
            emit TransferLogged(from, to, amount, block.timestamp);
        }
    }
}
