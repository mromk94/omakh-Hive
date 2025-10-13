// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title TokenVesting
 * @dev Handles the vesting of tokens with different schedules
 * HIGH-2 FIX: Now includes Pausable for emergency situations
 */
contract TokenVesting is AccessControl, Pausable {
    // FIX: Add dedicated role for vesting creation (principle of least privilege)
    bytes32 public constant VESTING_CREATOR_ROLE = keccak256("VESTING_CREATOR_ROLE");
    
    struct VestingSchedule {
        uint256 totalAmount;      // Total amount of tokens to be vested
        uint256 released;         // Amount of tokens already released
        uint256 start;            // Start time of the vesting
        uint256 cliff;            // Cliff period in seconds
        uint256 duration;         // Total duration of the vesting in seconds
        bool isLinear;            // True if linear vesting, false if cliff then linear
    }

    // Token being vested
    IERC20 public immutable token;

    // Vesting schedules for each beneficiary
    mapping(address => VestingSchedule) public vestingSchedules;

    event TokensVested(address indexed beneficiary, uint256 amount);
    event TokensReleased(address indexed beneficiary, uint256 amount);

    constructor(address _token, address admin) {
        require(_token != address(0), "TokenVesting: token is zero address");
        token = IERC20(_token);
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        // FIX: Grant limited VESTING_CREATOR_ROLE instead of full admin
        _grantRole(VESTING_CREATOR_ROLE, _token);
        _grantRole(VESTING_CREATOR_ROLE, admin);
    }

    /**
     * @notice Creates a new vesting schedule
     * @param beneficiary Address of the beneficiary
     * @param totalAmount Total amount of tokens to be vested
     * @param cliffDurationInMonths Cliff duration in months
     * @param vestingDurationInMonths Total vesting duration in months
     * @param isLinear If true, linear vesting. If false, cliff then linear
     */
    function createVestingSchedule(
        address beneficiary,
        uint256 totalAmount,
        uint256 cliffDurationInMonths,
        uint256 vestingDurationInMonths,
        bool isLinear
    ) external onlyRole(VESTING_CREATOR_ROLE) {
        require(beneficiary != address(0), "TokenVesting: beneficiary is zero address");
        require(totalAmount > 0, "TokenVesting: amount is 0");
        require(
            vestingSchedules[beneficiary].totalAmount == 0,
            "TokenVesting: beneficiary already has a vesting schedule"
        );

        uint256 cliff = block.timestamp + (cliffDurationInMonths * 30 days);
        uint256 duration = vestingDurationInMonths * 30 days;

        vestingSchedules[beneficiary] = VestingSchedule({
            totalAmount: totalAmount,
            released: 0,
            start: block.timestamp,
            cliff: cliff,
            duration: duration,
            isLinear: isLinear
        });

        emit TokensVested(beneficiary, totalAmount);
    }

    /**
     * @notice Releases vested tokens to the beneficiary
     * HIGH-2 FIX: Now pausable in emergency
     */
    function release(address beneficiary) external whenNotPaused {
        VestingSchedule storage schedule = vestingSchedules[beneficiary];
        require(schedule.totalAmount > 0, "TokenVesting: no vesting schedule");

        uint256 releasable = _releasableAmount(schedule);
        require(releasable > 0, "TokenVesting: no tokens to release");

        schedule.released += releasable;
        require(
            token.transfer(beneficiary, releasable),
            "TokenVesting: token transfer failed"
        );

        emit TokensReleased(beneficiary, releasable);
    }
    
    /**
     * @notice Pause vesting releases (emergency only)
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @notice Unpause vesting releases
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @dev Calculates the amount that has already vested but hasn't been released yet
     */
    function _releasableAmount(VestingSchedule memory schedule) private view returns (uint256) {
        return _vestedAmount(schedule) - schedule.released;
    }

    /**
     * @notice Get releasable amount for beneficiary
     */
    function getReleasableAmount(address beneficiary) external view returns (uint256) {
        VestingSchedule memory schedule = vestingSchedules[beneficiary];
        return _releasableAmount(schedule);
    }

    /**
     * @notice Get vested amount for beneficiary
     */
    function getVestedAmount(address beneficiary) external view returns (uint256) {
        VestingSchedule memory schedule = vestingSchedules[beneficiary];
        return _vestedAmount(schedule);
    }

    /**
     * @notice Get released amount for beneficiary
     */
    function getReleasedAmount(address beneficiary) external view returns (uint256) {
        return vestingSchedules[beneficiary].released;
    }

    /**
     * @notice Get vesting schedule info
     */
    function getVestingInfo(address beneficiary) external view returns (
        uint256 totalAmount,
        uint256 released,
        uint256 start,
        uint256 cliff,
        uint256 duration
    ) {
        VestingSchedule memory schedule = vestingSchedules[beneficiary];
        return (
            schedule.totalAmount,
            schedule.released,
            schedule.start,
            schedule.cliff,
            schedule.duration
        );
    }

    /**
     * @dev Calculates the amount that has already vested
     */
    function _vestedAmount(VestingSchedule memory schedule) private view returns (uint256) {
        if (block.timestamp < schedule.cliff) {
            return 0;
        } else if (block.timestamp >= schedule.start + schedule.duration) {
            return schedule.totalAmount;
        } else {
            if (schedule.isLinear) {
                // Linear vesting
                return (schedule.totalAmount * (block.timestamp - schedule.start)) / schedule.duration;
            } else {
                // Cliff then linear vesting
                if (block.timestamp < schedule.cliff) {
                    return 0;
                } else {
                    uint256 cliffAmount = schedule.totalAmount / 4; // 25% at cliff
                    uint256 remaining = schedule.totalAmount - cliffAmount;
                    uint256 vestingTime = block.timestamp - schedule.cliff;
                    uint256 vestingDuration = schedule.duration - (schedule.cliff - schedule.start);
                    return cliffAmount + (remaining * vestingTime) / vestingDuration;
                }
            }
        }
    }
}
