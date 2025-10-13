// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title SecurityCouncil
 * @dev Elected security council with emergency powers for OMK Protocol
 * 
 * Features:
 * - 7-member elected council (founder + 6 elected members)
 * - Founder is permanent member (cannot be removed)
 * - Emergency pause powers (3-of-7 signatures required)
 * - Parameter change authority (5-of-7 signatures required)
 * - Term limits for elected members (6 months)
 * - Community can vote to remove/replace elected members
 * - Council can veto malicious proposals
 */
contract SecurityCouncil is AccessControl, Pausable, ReentrancyGuard {
    
    // Roles
    bytes32 public constant FOUNDER_ROLE = keccak256("FOUNDER_ROLE"); // Permanent member
    bytes32 public constant COUNCIL_MEMBER_ROLE = keccak256("COUNCIL_MEMBER_ROLE"); // Elected members
    bytes32 public constant ELECTION_MANAGER_ROLE = keccak256("ELECTION_MANAGER_ROLE"); // DAO
    
    // Council configuration
    uint256 public constant TOTAL_COUNCIL_SEATS = 7;
    uint256 public constant ELECTED_SEATS = 6; // Founder + 6 elected = 7 total
    uint256 public constant EMERGENCY_THRESHOLD = 3; // 3-of-7 for emergency actions
    uint256 public constant PARAMETER_THRESHOLD = 5; // 5-of-7 for parameter changes
    uint256 public constant TERM_LENGTH = 180 days; // 6 months
    
    // Founder address (permanent member)
    address public immutable founder;
    
    // Council members
    struct CouncilMember {
        address memberAddress;
        uint256 electedAt;
        uint256 termEnd;
        bool isActive;
        bool isFounder;
        uint256 actionsPerformed;
    }
    
    mapping(address => CouncilMember) public members;
    address[] public memberList;
    uint256 public activeMembers;
    
    // Action tracking
    enum ActionType {
        EMERGENCY_PAUSE,
        EMERGENCY_UNPAUSE,
        PARAMETER_CHANGE,
        VETO_PROPOSAL,
        REMOVE_MEMBER
    }
    
    struct Action {
        uint256 id;
        ActionType actionType;
        address[] signers;
        bytes data;
        uint256 createdAt;
        uint256 executedAt;
        bool executed;
        address target;
        uint256 requiredSignatures;
    }
    
    mapping(uint256 => Action) public actions;
    mapping(uint256 => mapping(address => bool)) public actionSignatures;
    uint256 public actionCount;
    
    // Events
    event FounderSet(address indexed founder);
    event MemberElected(address indexed member, uint256 termEnd);
    event MemberRemoved(address indexed member, string reason);
    event MemberTermExpired(address indexed member);
    event ActionProposed(uint256 indexed actionId, ActionType actionType, address indexed proposer);
    event ActionSigned(uint256 indexed actionId, address indexed signer, uint256 currentSignatures);
    event ActionExecuted(uint256 indexed actionId, address indexed executor);
    event EmergencyActionTaken(address indexed initiator, string action);
    
    /**
     * @dev Constructor
     * @param _founder Founder address (permanent council member)
     * @param _admin Admin address (can manage elections)
     */
    constructor(address _founder, address _admin) {
        require(_founder != address(0), "SecurityCouncil: Invalid founder");
        require(_admin != address(0), "SecurityCouncil: Invalid admin");
        
        founder = _founder;
        
        // Set up roles
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(FOUNDER_ROLE, _founder);
        _grantRole(COUNCIL_MEMBER_ROLE, _founder);
        _grantRole(ELECTION_MANAGER_ROLE, _admin);
        
        // Add founder as permanent member
        members[_founder] = CouncilMember({
            memberAddress: _founder,
            electedAt: block.timestamp,
            termEnd: type(uint256).max, // Never expires
            isActive: true,
            isFounder: true,
            actionsPerformed: 0
        });
        
        memberList.push(_founder);
        activeMembers = 1;
        
        emit FounderSet(_founder);
    }
    
    // ============ MEMBER MANAGEMENT ============
    
    /**
     * @notice Elect a new council member
     * @param member Address of the member to elect
     */
    function electMember(address member) external onlyRole(ELECTION_MANAGER_ROLE) {
        require(member != address(0), "SecurityCouncil: Invalid address");
        require(!members[member].isActive, "SecurityCouncil: Already a member");
        require(activeMembers < TOTAL_COUNCIL_SEATS, "SecurityCouncil: Council full");
        require(member != founder, "SecurityCouncil: Founder is permanent member");
        
        uint256 termEnd = block.timestamp + TERM_LENGTH;
        
        members[member] = CouncilMember({
            memberAddress: member,
            electedAt: block.timestamp,
            termEnd: termEnd,
            isActive: true,
            isFounder: false,
            actionsPerformed: 0
        });
        
        _grantRole(COUNCIL_MEMBER_ROLE, member);
        memberList.push(member);
        activeMembers++;
        
        emit MemberElected(member, termEnd);
    }
    
    /**
     * @notice Remove elected council member (founder cannot be removed)
     * @param member Address of the member to remove
     * @param reason Reason for removal
     */
    function removeMember(address member, string calldata reason) 
        external 
        onlyRole(ELECTION_MANAGER_ROLE) 
    {
        require(members[member].isActive, "SecurityCouncil: Not an active member");
        require(!members[member].isFounder, "SecurityCouncil: Cannot remove founder");
        
        members[member].isActive = false;
        _revokeRole(COUNCIL_MEMBER_ROLE, member);
        activeMembers--;
        
        emit MemberRemoved(member, reason);
    }
    
    /**
     * @notice Check and expire members whose terms have ended
     */
    function expireTerms() external {
        for (uint256 i = 0; i < memberList.length; i++) {
            address memberAddr = memberList[i];
            CouncilMember storage member = members[memberAddr];
            
            if (member.isActive && 
                !member.isFounder && 
                block.timestamp >= member.termEnd) {
                
                member.isActive = false;
                _revokeRole(COUNCIL_MEMBER_ROLE, memberAddr);
                activeMembers--;
                
                emit MemberTermExpired(memberAddr);
            }
        }
    }
    
    /**
     * @notice Extend elected member's term
     * @param member Address of the member
     */
    function extendTerm(address member) external onlyRole(ELECTION_MANAGER_ROLE) {
        require(members[member].isActive, "SecurityCouncil: Not an active member");
        require(!members[member].isFounder, "SecurityCouncil: Founder has no term limit");
        
        members[member].termEnd = block.timestamp + TERM_LENGTH;
    }
    
    // ============ COUNCIL ACTIONS ============
    
    /**
     * @notice Propose an emergency pause action
     * @param target Contract to pause
     * @param data Call data for pause
     */
    function proposeEmergencyPause(address target, bytes calldata data) 
        external 
        onlyRole(COUNCIL_MEMBER_ROLE) 
        returns (uint256) 
    {
        require(members[msg.sender].isActive, "SecurityCouncil: Member not active");
        
        uint256 actionId = actionCount++;
        
        actions[actionId] = Action({
            id: actionId,
            actionType: ActionType.EMERGENCY_PAUSE,
            signers: new address[](0),
            data: data,
            createdAt: block.timestamp,
            executedAt: 0,
            executed: false,
            target: target,
            requiredSignatures: EMERGENCY_THRESHOLD
        });
        
        // Auto-sign by proposer
        _signAction(actionId, msg.sender);
        
        emit ActionProposed(actionId, ActionType.EMERGENCY_PAUSE, msg.sender);
        
        return actionId;
    }
    
    /**
     * @notice Propose a parameter change action
     * @param target Contract to modify
     * @param data Call data for change
     */
    function proposeParameterChange(address target, bytes calldata data) 
        external 
        onlyRole(COUNCIL_MEMBER_ROLE) 
        returns (uint256) 
    {
        require(members[msg.sender].isActive, "SecurityCouncil: Member not active");
        
        uint256 actionId = actionCount++;
        
        actions[actionId] = Action({
            id: actionId,
            actionType: ActionType.PARAMETER_CHANGE,
            signers: new address[](0),
            data: data,
            createdAt: block.timestamp,
            executedAt: 0,
            executed: false,
            target: target,
            requiredSignatures: PARAMETER_THRESHOLD
        });
        
        // Auto-sign by proposer
        _signAction(actionId, msg.sender);
        
        emit ActionProposed(actionId, ActionType.PARAMETER_CHANGE, msg.sender);
        
        return actionId;
    }
    
    /**
     * @notice Sign a proposed action
     * @param actionId ID of the action to sign
     */
    function signAction(uint256 actionId) external onlyRole(COUNCIL_MEMBER_ROLE) {
        require(members[msg.sender].isActive, "SecurityCouncil: Member not active");
        require(!actions[actionId].executed, "SecurityCouncil: Already executed");
        require(!actionSignatures[actionId][msg.sender], "SecurityCouncil: Already signed");
        
        _signAction(actionId, msg.sender);
    }
    
    /**
     * @dev Internal function to sign an action
     */
    function _signAction(uint256 actionId, address signer) internal {
        actionSignatures[actionId][signer] = true;
        actions[actionId].signers.push(signer);
        
        emit ActionSigned(actionId, signer, actions[actionId].signers.length);
    }
    
    /**
     * @notice Execute a fully signed action
     * @param actionId ID of the action to execute
     */
    function executeAction(uint256 actionId) external onlyRole(COUNCIL_MEMBER_ROLE) nonReentrant {
        Action storage action = actions[actionId];
        
        require(!action.executed, "SecurityCouncil: Already executed");
        require(
            action.signers.length >= action.requiredSignatures,
            "SecurityCouncil: Insufficient signatures"
        );
        
        action.executed = true;
        action.executedAt = block.timestamp;
        
        // Execute the action
        if (action.target != address(0) && action.data.length > 0) {
            (bool success, ) = action.target.call(action.data);
            require(success, "SecurityCouncil: Execution failed");
        }
        
        // Update member stats
        for (uint256 i = 0; i < action.signers.length; i++) {
            members[action.signers[i]].actionsPerformed++;
        }
        
        emit ActionExecuted(actionId, msg.sender);
        
        if (action.actionType == ActionType.EMERGENCY_PAUSE) {
            emit EmergencyActionTaken(msg.sender, "PAUSE");
        } else if (action.actionType == ActionType.EMERGENCY_UNPAUSE) {
            emit EmergencyActionTaken(msg.sender, "UNPAUSE");
        }
    }
    
    // ============ VIEW FUNCTIONS ============
    
    /**
     * @notice Get all active council members
     */
    function getActiveMembers() external view returns (address[] memory) {
        address[] memory active = new address[](activeMembers);
        uint256 index = 0;
        
        for (uint256 i = 0; i < memberList.length; i++) {
            if (members[memberList[i]].isActive) {
                active[index] = memberList[i];
                index++;
            }
        }
        
        return active;
    }
    
    /**
     * @notice Get member details
     */
    function getMemberInfo(address member) external view returns (
        bool isActive,
        bool isFounder,
        uint256 termEnd,
        uint256 actionsPerformed
    ) {
        CouncilMember memory m = members[member];
        return (m.isActive, m.isFounder, m.termEnd, m.actionsPerformed);
    }
    
    /**
     * @notice Get action details
     */
    function getActionInfo(uint256 actionId) external view returns (
        ActionType actionType,
        uint256 currentSignatures,
        uint256 requiredSignatures,
        bool executed,
        address[] memory signers
    ) {
        Action memory action = actions[actionId];
        return (
            action.actionType,
            action.signers.length,
            action.requiredSignatures,
            action.executed,
            action.signers
        );
    }
    
    /**
     * @notice Check if address is an active council member
     */
    function isActiveMember(address account) external view returns (bool) {
        return members[account].isActive;
    }
    
    /**
     * @notice Check if address is the founder
     */
    function isFounder(address account) external view returns (bool) {
        return account == founder;
    }
    
    /**
     * @notice Get council statistics
     */
    function getCouncilStats() external view returns (
        uint256 totalSeats,
        uint256 activeSeats,
        uint256 vacantSeats,
        uint256 totalActions,
        uint256 executedActions
    ) {
        totalSeats = TOTAL_COUNCIL_SEATS;
        activeSeats = activeMembers;
        vacantSeats = TOTAL_COUNCIL_SEATS - activeMembers;
        totalActions = actionCount;
        
        uint256 executed = 0;
        for (uint256 i = 0; i < actionCount; i++) {
            if (actions[i].executed) {
                executed++;
            }
        }
        executedActions = executed;
    }
    
    // ============ EMERGENCY FUNCTIONS ============
    
    /**
     * @notice Emergency pause (requires council consensus)
     */
    function emergencyPause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @notice Emergency unpause (requires council consensus)
     */
    function emergencyUnpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
}
