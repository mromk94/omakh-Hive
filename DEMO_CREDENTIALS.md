# 🔐 Demo Credentials & Test Accounts

## Test User Accounts

### Demo Investor Account
```
Email: demo@omakh.com
Password: Demo1234!
Wallet: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb9
Balance: 5,250 USDT (mock)
Holdings: 
  - 0.5 ETH
  - 10,000 OMK tokens
  - 10 blocks of Dubai Marina property
```

### Test Institutional Account
```
Email: institution@omakh.com
Password: Inst1234!
Wallet: 0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199
Balance: 125,000 USDT (mock)
Holdings:
  - 5 ETH
  - 250,000 OMK tokens
  - 100+ property blocks across 5 properties
```

### Test New User (No Holdings)
```
Email: newuser@omakh.com
Password: New1234!
Wallet: (not connected)
Balance: 0
```

## Mock Wallet Addresses (for testing without real wallet)

### Ethereum Addresses
```
1. 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb9 (Demo investor)
2. 0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199 (Institution)
3. 0x1234567890123456789012345678901234567890 (Empty wallet)
```

### Solana Addresses
```
1. 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU (Demo investor)
2. 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM (Institution)
```

## Quick Test Flow

### 1. First Time User Journey
```
1. Open chat
2. Select theme (light/dark)
3. Choose "No, I'm new here"
4. Select "Yes, I have a wallet"
5. Connect wallet (use demo address)
6. View dashboard
7. Browse properties
8. Calculate ROI
9. Make investment
```

### 2. Returning User Journey
```
1. Open chat
2. Choose "Yes, I have an account"
3. Login with email (demo@omakh.com)
4. View dashboard
5. Check balance
6. Explore new properties
```

### 3. Wallet-First Journey
```
1. Say "connect wallet"
2. Use MetaMask/injected wallet
3. Auto-detect holdings
4. Show personalized dashboard
5. Suggest next actions
```

## Teacher Bee Test Queries

Try these with Teacher Bee mode:
```
- "What is a wallet?"
- "How do I buy crypto?"
- "Is this safe?"
- "How do smart contracts work?"
- "What's the difference between ETH and SOL?"
- "Explain tokenization"
```

## Queen AI Test Queries

Try these for general chat:
```
- "hello"
- "tell me about yourself"
- "how does this work?"
- "show me properties"
- "calculate my returns"
- "what's the price of OMK?"
- "is it safe?"
- "connect wallet"
- "I want to invest"
```

## Admin Access (Future)
```
Email: admin@omakh.com
Password: Admin1234!
Permissions: Full system access
```

## API Keys (for testing integrations)

### Test API Key
```
X-API-Key: test_omk_hive_123456789
```

### Rate Limits (Development)
- 100 requests/minute
- No authentication required for health checks
- Session tokens expire after 24 hours

## Notes

⚠️ **All credentials are for DEVELOPMENT/TESTING only**
- Mock data, not real funds
- No real blockchain transactions
- Safe to share within team
- Reset daily in dev environment

🔐 **Production credentials will be different**
- Stored in secure vault (GCP Secret Manager)
- Never committed to git
- Rotated monthly
- MFA required for admin
