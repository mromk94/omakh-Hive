# TreasuryVault Contract

A secure, multi-signature vault for managing treasury assets with withdrawal approval workflow.

## Features

- **Multi-signature Approval**: Requires multiple approvals for withdrawals
- **Timelock**: Enforces a delay between approval and execution
- **Emergency Shutdown**: Ability to pause all operations in case of emergency
- **Role-Based Access Control**: Granular permissions for different roles
- **Token Support**: Handles both ETH and ERC20 tokens
- **Event Logging**: Comprehensive event emission for all state changes

## Contracts

### TreasuryVault.sol

Main contract that handles deposits, withdrawals, and approvals.

#### Roles

- `DEFAULT_ADMIN_ROLE`: Can add/remove approvers and update settings
- `APPROVER_ROLE`: Can approve or reject withdrawal requests
- `EMERGENCY_ADMIN_ROLE`: Can trigger emergency shutdown

## Deployment

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env` file based on `.env.example` and fill in the required values.

3. Deploy to local network:
   ```bash
   npx hardhat deploy --network localhost
   ```

4. Deploy to testnet (e.g., Sepolia):
   ```bash
   npx hardhat deploy --network sepolia
   ```

## Testing

Run tests:
```bash
npx hardhat test
```

Run coverage:
```bash
npx hardhat coverage
```

## Usage

### Deposit ETH

```javascript
// Deposit 1 ETH
await treasury.deposit(ethers.ZeroAddress, ethers.parseEther("1.0"), { value: ethers.parseEther("1.0") });
```

### Deposit ERC20 Tokens

```javascript
// Approve tokens first
await token.approve(treasury.address, amount);

// Then deposit
await treasury.deposit(token.address, amount);
```

### Request Withdrawal

```javascript
const tx = await treasury.requestWithdrawal(
  tokenAddress, // or ethers.ZeroAddress for ETH
  recipientAddress,
  amount
);
```

### Approve Withdrawal

```javascript
await treasury.approveWithdrawal(withdrawalId);
```

### Execute Withdrawal

```javascript
// After the timelock has passed
await treasury.executeWithdrawal(withdrawalId);
```

## Security Considerations

- Always verify the contract after deployment
- Use a timelock appropriate for your security requirements
- Regularly audit the contract for vulnerabilities
- Use a multi-sig wallet for admin operations

## License

MIT
