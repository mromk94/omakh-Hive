# OMK Hive API Documentation

## Overview

OMK Hive provides a comprehensive API with multiple interfaces:
- **REST API**: Traditional HTTP endpoints
- **GraphQL API**: Flexible query interface
- **WebSocket API**: Real-time updates

**Base URLs**:
- Development: `http://localhost:3000`
- Staging: `https://api-staging.omkhive.io`
- Production: `https://api.omkhive.io`

## Authentication

### JWT Authentication
Most endpoints require JWT authentication.

**Get Token**:
```bash
POST /auth/login
Content-Type: application/json

{
  "wallet": "0x...",
  "signature": "..."
}

Response:
{
  "accessToken": "eyJhbGciOi...",
  "refreshToken": "...",
  "expiresIn": 3600
}
```

**Use Token**:
```bash
GET /api/v1/user/profile
Authorization: Bearer eyJhbGciOi...
```

**Refresh Token**:
```bash
POST /auth/refresh
Content-Type: application/json

{
  "refreshToken": "..."
}
```

## REST API Endpoints

### Health & Status
```
GET /health
GET /health/ready
GET /health/live
```

### Authentication
```
POST /auth/login              # Wallet login
POST /auth/refresh            # Refresh token
POST /auth/logout             # Logout
GET  /auth/nonce             # Get signing nonce
```

### User
```
GET    /api/v1/user/profile           # Get user profile
PUT    /api/v1/user/profile           # Update profile
GET    /api/v1/user/balance           # Get token balance
GET    /api/v1/user/transactions      # Transaction history
GET    /api/v1/user/staking           # Staking info
```

### Token
```
GET    /api/v1/token/info             # Token information
GET    /api/v1/token/supply           # Total supply
GET    /api/v1/token/price            # Current price
GET    /api/v1/token/holders          # Top holders
```

### Staking
```
POST   /api/v1/staking/stake          # Stake tokens
POST   /api/v1/staking/unstake        # Unstake tokens
POST   /api/v1/staking/claim          # Claim rewards
GET    /api/v1/staking/apy            # Current APY
GET    /api/v1/staking/rewards        # Pending rewards
```

### Queen AI
```
GET    /api/v1/queen/status           # Queen AI status
GET    /api/v1/queen/decisions        # Recent decisions
GET    /api/v1/queen/proposals        # Active proposals
POST   /api/v1/queen/vote             # Vote on proposal
```

### Bees
```
GET    /api/v1/bees                   # List all bees
GET    /api/v1/bees/:id               # Get bee details
GET    /api/v1/bees/:id/performance   # Bee performance
GET    /api/v1/bees/:id/status        # Bee health status
```

### Treasury
```
GET    /api/v1/treasury/balance       # Treasury balance
GET    /api/v1/treasury/allocations   # Asset allocations
GET    /api/v1/treasury/history       # Transaction history
```

### Analytics
```
GET    /api/v1/analytics/overview     # Dashboard overview
GET    /api/v1/analytics/charts       # Chart data
GET    /api/v1/analytics/metrics      # Key metrics
```

## GraphQL API

**Endpoint**: `/graphql`

### Example Queries

**Get User Info**:
```graphql
query GetUser($walletAddress: String!) {
  user(walletAddress: $walletAddress) {
    id
    walletAddress
    balance
    stakedAmount
    transactions(limit: 10) {
      hash
      amount
      timestamp
      type
    }
  }
}
```

**Get Queen AI Status**:
```graphql
query GetQueenStatus {
  queenAI {
    status
    activeProvider
    decisions(limit: 5) {
      id
      type
      confidence
      outcome
      timestamp
    }
    proposals {
      id
      title
      description
      votesFor
      votesAgainst
      status
    }
  }
}
```

**Get Bee Performance**:
```graphql
query GetBees {
  bees {
    id
    name
    type
    status
    performance {
      accuracy
      tasksCompleted
      averageResponseTime
    }
  }
}
```

### Mutations

**Stake Tokens**:
```graphql
mutation StakeTokens($amount: Float!) {
  stake(amount: $amount) {
    success
    transactionHash
    newBalance
  }
}
```

**Vote on Proposal**:
```graphql
mutation Vote($proposalId: ID!, $vote: VoteType!) {
  voteOnProposal(proposalId: $proposalId, vote: $vote) {
    success
    proposal {
      id
      votesFor
      votesAgainst
    }
  }
}
```

### Subscriptions

**Token Price Updates**:
```graphql
subscription TokenPrice {
  tokenPriceUpdated {
    price
    change24h
    volume24h
    timestamp
  }
}
```

**Queen AI Decisions**:
```graphql
subscription QueenDecisions {
  newDecision {
    id
    type
    description
    confidence
    timestamp
  }
}
```

## WebSocket API

**Endpoint**: `ws://localhost:3000` or `wss://api.omkhive.io`

### Connection
```javascript
const ws = new WebSocket('ws://localhost:3000');

ws.onopen = () => {
  // Authenticate
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your-jwt-token'
  }));
};
```

### Subscribe to Events
```javascript
// Subscribe to token price
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'token.price'
}));

// Subscribe to Queen decisions
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'queen.decisions'
}));

// Subscribe to user events
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'user.transactions'
}));
```

### Event Types
- `token.price` - Real-time price updates
- `token.transfer` - Token transfers
- `queen.decisions` - AI decisions
- `queen.proposals` - New proposals
- `bees.status` - Bee status changes
- `user.transactions` - User transactions
- `staking.rewards` - Staking rewards

## Rate Limiting

**Limits**:
- Unauthenticated: 100 requests/15 minutes
- Authenticated: 1000 requests/15 minutes
- WebSocket: 100 messages/minute

**Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1633024800
```

## Error Handling

**Error Response Format**:
```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "error": "Bad Request",
  "details": [
    {
      "field": "amount",
      "message": "Amount must be greater than 0"
    }
  ]
}
```

**Common Error Codes**:
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error
- `503` - Service Unavailable

## API Versioning

Current version: `v1`

**Version in URL**: `/api/v1/...`

**Version in Header**:
```
Accept: application/vnd.omkhive.v1+json
```

## SDKs & Client Libraries

### JavaScript/TypeScript
```bash
npm install @omk-hive/sdk
```

```typescript
import { OMKHiveClient } from '@omk-hive/sdk';

const client = new OMKHiveClient({
  apiUrl: 'https://api.omkhive.io',
  apiKey: 'your-api-key'
});

const balance = await client.user.getBalance();
```

### Python
```bash
pip install omk-hive-sdk
```

```python
from omk_hive import OMKHiveClient

client = OMKHiveClient(
    api_url='https://api.omkhive.io',
    api_key='your-api-key'
)

balance = client.user.get_balance()
```

## Swagger Documentation

Interactive API documentation available at:
- Development: `http://localhost:3000/api/docs`
- Production: `https://api.omkhive.io/api/docs`

## GraphQL Playground

Interactive GraphQL interface:
- Development: `http://localhost:3000/graphql`
- Production: `https://api.omkhive.io/graphql`

## Support

- **GitHub Issues**: Report bugs or request features
- **Discord**: Real-time community support
- **Email**: api-support@omkhive.io

---

**Last Updated**: October 8, 2025
