# Contract Deployment Implementation Plan

## 🎯 **OBJECTIVE**
Enable admin to connect wallet and deploy contracts directly from the admin dashboard with network switching capability.

## 📊 **CURRENT STATE**

### **Frontend (`ContractDeployer.tsx`):**
- ✅ UI for listing contracts
- ✅ Compilation triggering
- ✅ Network selection dropdown (localhost, sepolia, mainnet)
- ⚠️ **MISSING**: Wallet connection
- ⚠️ **MISSING**: Direct contract deployment via wallet
- ⚠️ **MISSING**: Network switching

### **Backend (`contracts.py`):**
- ✅ Lists contracts
- ✅ Compiles contracts via hardhat
- ⚠️ **PROBLEM**: Tries to deploy server-side (requires private key - insecure!)
- ⚠️ **SOLUTION**: Backend should only prepare deployment data, not execute

## 🔧 **IMPLEMENTATION PLAN**

### **Phase 1: Add Wallet Connection**
1. Install/verify wagmi and viem dependencies
2. Add wallet connection button to ContractDeployer header
3. Show connected address and network
4. Add disconnect functionality

### **Phase 2: Network Switching**
5. Detect current connected network
6. Add network switch button
7. Handle network change requests
8. Validate network matches selected deployment target

### **Phase 3: Contract Deployment**
9. Fetch contract ABI and bytecode from backend
10. Use `wagmi`'s `useDeployContract` hook
11. Prepare constructor arguments
12. Sign and send deployment transaction
13. Track transaction status
14. Save deployment info to backend

### **Phase 4: User Experience**
15. Show gas estimation before deployment
16. Display transaction progress
17. Handle errors gracefully
18. Show Etherscan links after deployment

## 📁 **FILES TO MODIFY**

### **1. Frontend:**
- `omk-frontend/app/kingdom/components/ContractDeployer.tsx` - Add wallet integration
- `omk-frontend/lib/wagmi-config.ts` - Verify wagmi config exists
- Create new: `omk-frontend/hooks/useContractDeployer.ts` - Custom deployment hook

### **2. Backend:**
- `backend/queen-ai/app/api/v1/contracts.py` - Add ABI/bytecode endpoint
- Keep compilation endpoint
- Modify execute endpoint to just save deployment info (not deploy)

## 🔐 **SECURITY CONSIDERATIONS**

1. ✅ Admin wallet controls deployment (not server)
2. ✅ No private keys stored on server
3. ✅ Transactions signed in browser
4. ✅ Network validation before deployment
5. ✅ Gas limit controls

## 🎨 **UI FLOW**

```
[Contract Dashboard]
     │
     ├─> [Connect Wallet Button]
     │       │
     │       └─> Shows: Address, Network, Balance
     │
     ├─> [Select Contract]
     │       │
     │       └─> Shows: Status, ABI, Bytecode
     │
     ├─> [Choose Network]
     │       │
     │       ├─> Localhost (for testing)
     │       ├─> Sepolia Testnet
     │       └─> Ethereum Mainnet
     │
     ├─> [Deploy Button]
     │       │
     │       ├─> Check wallet connected
     │       ├─> Verify network matches
     │       ├─> Show gas estimate
     │       ├─> Request signature
     │       ├─> Send transaction
     │       └─> Track status
     │
     └─> [View Deployment]
             │
             ├─> Contract Address
             ├─> Transaction Hash
             ├─> Etherscan Link
             └─> Verification Status
```

## 🧪 **TESTING CHECKLIST**

- [ ] Connect wallet successfully
- [ ] Switch networks (Sepolia ↔ Mainnet)
- [ ] Deploy to Sepolia testnet
- [ ] View deployment on Etherscan
- [ ] Handle rejected transactions
- [ ] Handle insufficient gas
- [ ] Disconnect wallet
- [ ] Deploy multiple contracts
- [ ] Batch deployment

## 📦 **DEPENDENCIES NEEDED**

```json
{
  "wagmi": "^2.x",
  "viem": "^2.x",
  "@rainbow-me/rainbowkit": "^2.x" (optional, for better UX)
}
```

## 🚀 **DEPLOYMENT STEPS**

### **For Admin:**

1. **Connect Wallet**
   - Click "Connect Wallet" in Contract Dashboard
   - Approve connection in MetaMask/wallet

2. **Select Network**
   - Choose deployment target (Sepolia/Mainnet)
   - Switch wallet network if needed

3. **Compile Contracts**
   - Click "Compile All" button
   - Wait for compilation to complete

4. **Deploy Contract**
   - Select contract from list
   - Click "Deploy" button
   - Review deployment details
   - Confirm transaction in wallet
   - Wait for confirmation

5. **Verify Deployment**
   - View contract address
   - Check on Etherscan
   - Optionally verify source code

## 🔄 **INTEGRATION WITH EXISTING SYSTEM**

### **Keep:**
- ✅ Backend compilation (via hardhat)
- ✅ Contract listing and status
- ✅ Deployment history tracking

### **Change:**
- 🔧 Deployment execution → Frontend (via wallet)
- 🔧 Add ABI/bytecode API endpoint
- 🔧 Backend just saves deployment results

### **Add:**
- ➕ Wallet connection state management
- ➕ Network detection and switching
- ➕ Transaction status tracking
- ➕ Gas estimation display

---

## 📝 **IMPLEMENTATION NOTES**

### **Why Frontend Deployment?**
1. **Security**: No private keys on server
2. **Control**: Admin has full control
3. **Transparency**: See exactly what's being deployed
4. **Standard**: How most dApps work

### **Why Keep Backend Compilation?**
1. **Consistency**: Hardhat compilation is reliable
2. **Speed**: Faster than browser compilation
3. **Artifacts**: Generates all needed files
4. **Verification**: Easier to verify on Etherscan

---

## ✅ **ACCEPTANCE CRITERIA**

- [ ] Admin can connect wallet from dashboard
- [ ] Admin can see connected address and network
- [ ] Admin can switch between Sepolia and Mainnet
- [ ] Admin can deploy contracts using their wallet
- [ ] Deployment transactions are signed by admin wallet
- [ ] Deployment status is tracked and displayed
- [ ] Successful deployments show Etherscan links
- [ ] Failed deployments show clear error messages
- [ ] No private keys are stored on server
- [ ] All deployment data is saved to backend for tracking

---

**Next:** Proceed with Phase 1 implementation
