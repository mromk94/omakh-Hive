# 🚀 QUICK START: Deploy Your First Contract

**Time Required:** 15 minutes  
**Network:** Sepolia Testnet  
**Cost:** Free (testnet ETH)

---

## ⚡ **FASTEST PATH TO DEPLOYMENT**

### **Step 1: Get Testnet ETH (5 min)**

1. **Create MetaMask Wallet** (if you don't have one)
   - Install MetaMask extension
   - Create new wallet
   - Switch to Sepolia network

2. **Get Testnet ETH** from faucets:
   - https://sepoliafaucet.com
   - https://faucet.sepolia.dev
   - Request 0.5 ETH (free)

3. **Export Private Key:**
   - MetaMask → Account → Export Private Key
   - Copy the key (starts with `0x...`)

---

### **Step 2: Configure Deployment (3 min)**

1. **Create .env file:**
   ```bash
   cd /Users/mac/CascadeProjects/omakh-Hive/contracts/ethereum
   cp .env.example .env
   nano .env
   ```

2. **Add your keys:**
   ```bash
   # Use free public RPC (no signup needed)
   SEPOLIA_RPC_URL=https://ethereum-sepolia.publicnode.com
   
   # Your MetaMask private key
   PRIVATE_KEY=0xyour_private_key_here
   
   # Optional: Get from https://etherscan.io/myapikey
   ETHERSCAN_API_KEY=your_etherscan_key
   ```

3. **Save and exit:** `Ctrl+X`, `Y`, `Enter`

---

### **Step 3: Deploy Via UI (7 min)**

1. **Start Backend:**
   ```bash
   cd backend/queen-ai
   source venv/bin/activate
   python main.py
   ```

2. **Start Frontend** (new terminal):
   ```bash
   cd omk-frontend
   npm run dev
   ```

3. **Login:**
   - Go to http://localhost:3000/kingdom/login
   - Email: `king@omakh.io`
   - Password: `Admin2025!!`

4. **Navigate:**
   - Click "System" → "Contracts"

5. **Compile:**
   - Click "Compile All"
   - Wait for success toast

6. **Deploy:**
   - Click "Deploy" on any contract
   - Select "Sepolia Testnet"
   - Click "Prepare Deployment"

7. **Execute:**
   - Switch to "Deployments" tab
   - Click "Execute Deploy"
   - Confirm dialog
   - **Wait 2-5 minutes**

8. **Success!**
   - Get contract address
   - Click Etherscan link
   - View your deployed contract!

---

## ✅ **DONE!**

You just deployed a smart contract to Ethereum testnet! 🎉

**Next Steps:**
- Deploy more contracts
- Test contract functions
- Verify on Etherscan

---

## ⚠️ **TROUBLESHOOTING**

**"Insufficient funds"**
→ Get more testnet ETH from faucets

**"Deployment timeout"**
→ Wait and try again (network congestion)

**"Private key invalid"**
→ Check you copied full key from MetaMask (starts with 0x)

**"RPC error"**
→ Try alternative RPC: `https://rpc.sepolia.org`

---

## 📞 **HELP**

Read full guide: `PHASE3_DEPLOYMENT_COMPLETE.md`

Questions? Check troubleshooting section!
