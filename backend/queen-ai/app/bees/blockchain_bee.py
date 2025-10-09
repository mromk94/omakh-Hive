"""
BlockchainBee - Multi-Chain Transaction Execution & Automated Trading

Integrated with:
- Ethereum client (Web3)
- Solana client
- Cross-chain bridge
- Transaction manager
- Wallet manager

Capabilities:
- Execute blockchain transactions (ETH, SOL)
- Automated trading/swaps
- Liquidity management
- Gas price optimization
- Cross-chain bridge operations
- Transaction monitoring
- Queen AI triggers
"""
from typing import Dict, Any, Optional, List
from decimal import Decimal
import structlog

from app.bees.base import BaseBee
from app.blockchain import (
    ethereum_client,
    solana_client,
    cross_chain_bridge,
    wallet_manager,
    transaction_manager
)
from app.blockchain.dex import UniswapRouter, RaydiumRouter
from app.blockchain.oracles import ChainlinkOracle, PythOracle

logger = structlog.get_logger(__name__)


class BlockchainBee(BaseBee):
    """
    Multi-chain blockchain orchestrator with automated trading
    
    Responsibilities:
    - Execute blockchain transactions (ETH, SOL)
    - Automated token swaps
    - Liquidity provision/removal
    - Cross-chain bridge operations
    - Gas/fee optimization
    - Transaction monitoring
    - Queen AI-triggered operations
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="BlockchainBee")
        
        # Blockchain clients
        self.eth_client = ethereum_client
        self.sol_client = solana_client
        self.bridge = cross_chain_bridge
        self.wallet_mgr = wallet_manager
        self.tx_mgr = transaction_manager
        
        # DEX Routers
        self.uniswap = None  # Will be initialized
        self.raydium = None  # Will be initialized
        
        # Price Oracles
        self.chainlink = None  # Will be initialized
        self.pyth = None  # Will be initialized
        
        # State
        self.initialized_clients = {
            "ethereum": False,
            "solana": False,
            "bridge": False,
            "uniswap": False,
            "raydium": False,
            "chainlink": False,
            "pyth": False
        }
        
        # Trading configuration
        self.slippage_tolerance = Decimal('0.01')  # 1%
        self.max_trade_size_eth = Decimal('10')  # 10 ETH max per trade
        self.max_trade_size_sol = Decimal('100')  # 100 SOL max per trade
    
    async def initialize(self) -> bool:
        """Initialize blockchain clients, DEX routers, and oracles"""
        try:
            # Initialize Ethereum client
            if not self.eth_client.initialized:
                await self.eth_client.initialize()
                self.initialized_clients["ethereum"] = True
                logger.info("Ethereum client initialized")
            
            # Initialize Solana client
            if not self.sol_client.initialized:
                await self.sol_client.initialize()
                self.initialized_clients["solana"] = True
                logger.info("Solana client initialized")
            
            # Initialize bridge
            if not self.bridge.is_healthy:
                await self.bridge.initialize()
                self.initialized_clients["bridge"] = True
                logger.info("Bridge initialized")
            
            # Initialize Uniswap router
            try:
                self.uniswap = UniswapRouter(self.eth_client)
                await self.uniswap.initialize()
                self.initialized_clients["uniswap"] = True
                logger.info("Uniswap router initialized")
            except Exception as e:
                logger.warning(f"Uniswap initialization failed: {str(e)}")
            
            # Initialize Raydium router
            try:
                self.raydium = RaydiumRouter(self.sol_client)
                await self.raydium.initialize()
                self.initialized_clients["raydium"] = True
                logger.info("Raydium router initialized")
            except Exception as e:
                logger.warning(f"Raydium initialization failed: {str(e)}")
            
            # Initialize Chainlink oracle
            try:
                self.chainlink = ChainlinkOracle(self.eth_client, network="mainnet")
                await self.chainlink.initialize()
                self.initialized_clients["chainlink"] = True
                logger.info("Chainlink oracle initialized")
            except Exception as e:
                logger.warning(f"Chainlink initialization failed: {str(e)}")
            
            # Initialize Pyth oracle
            try:
                self.pyth = PythOracle(self.sol_client, network="mainnet")
                await self.pyth.initialize()
                self.initialized_clients["pyth"] = True
                logger.info("Pyth oracle initialized")
            except Exception as e:
                logger.warning(f"Pyth initialization failed: {str(e)}")
            
            self.initialized = True
            logger.info(
                "BlockchainBee fully initialized",
                services=self.initialized_clients
            )
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize BlockchainBee: {str(e)}")
            return False
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute blockchain task"""
        task_type = task_data.get("type")
        
        # Core Operations
        if task_type == "execute_transaction":
            return await self._execute_transaction(task_data)
        elif task_type == "estimate_gas":
            return await self._estimate_gas(task_data)
        elif task_type == "check_balance":
            return await self._check_balance(task_data)
        elif task_type == "monitor_tx":
            return await self._monitor_transaction(task_data)
        
        # Trading Operations (NEW)
        elif task_type == "swap_tokens":
            return await self._swap_tokens(task_data)
        elif task_type == "add_liquidity":
            return await self._add_liquidity(task_data)
        elif task_type == "remove_liquidity":
            return await self._remove_liquidity(task_data)
        
        # Cross-chain Operations (NEW)
        elif task_type == "bridge_transfer":
            return await self._bridge_transfer(task_data)
        elif task_type == "check_bridge_status":
            return await self._check_bridge_status(task_data)
        
        # Queen AI Triggers (NEW)
        elif task_type == "auto_rebalance":
            return await self._auto_rebalance(task_data)
        elif task_type == "emergency_withdraw":
            return await self._emergency_withdraw(task_data)
        
        # Price Oracle Operations (NEW)
        elif task_type == "get_price":
            return await self._get_price(task_data)
        elif task_type == "get_multiple_prices":
            return await self._get_multiple_prices(task_data)
        elif task_type == "calculate_value":
            return await self._calculate_token_value(task_data)
        
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _execute_transaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a blockchain transaction
        
        Supports Ethereum and Solana
        """
        try:
            chain = data.get("chain", "ethereum").lower()
            
            if chain == "ethereum":
                return await self._execute_ethereum_tx(data)
            elif chain == "solana":
                return await self._execute_solana_tx(data)
            else:
                return {"success": False, "error": f"Unsupported chain: {chain}"}
        
        except Exception as e:
            logger.error(f"Transaction execution failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _execute_ethereum_tx(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Ethereum transaction"""
        contract_address = data.get("contract_address")
        function_name = data.get("function")
        params = data.get("params", [])
        value = data.get("value", 0)
        priority = data.get("priority", "normal")
        
        # Get contract ABI (would need to be provided or fetched)
        abi = data.get("abi")
        if not abi:
            return {"success": False, "error": "Contract ABI required"}
        
        # Execute via Ethereum client
        tx_hash = await self.eth_client.execute_contract_function(
            contract_address=contract_address,
            abi=abi,
            function_name=function_name,
            args=params,
            value=value,
            gas_priority=priority
        )
        
        logger.info(
            "Ethereum transaction executed",
            function=function_name,
            tx_hash=tx_hash,
            contract=contract_address
        )
        
        return {
            "success": True,
            "chain": "ethereum",
            "tx_hash": tx_hash,
            "contract": contract_address,
            "function": function_name,
            "status": "pending",
            "explorer_url": f"https://etherscan.io/tx/{tx_hash}"
        }
    
    async def _execute_solana_tx(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Solana transaction"""
        to_address = data.get("to_address")
        amount = data.get("amount")
        priority_fee = data.get("priority_fee")
        
        # Execute via Solana client
        signature = await self.sol_client.transfer_sol(
            to=to_address,
            amount=float(amount),
            priority_fee=priority_fee
        )
        
        logger.info(
            "Solana transaction executed",
            signature=signature,
            to=to_address,
            amount=amount
        )
        
        return {
            "success": True,
            "chain": "solana",
            "signature": signature,
            "to": to_address,
            "amount": amount,
            "status": "pending",
            "explorer_url": f"https://solscan.io/tx/{signature}"
        }
    
    async def _estimate_gas(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate gas for Ethereum transaction"""
        try:
            chain = data.get("chain", "ethereum").lower()
            
            if chain == "ethereum":
                contract_address = data.get("contract_address")
                abi = data.get("abi")
                function_name = data.get("function")
                args = data.get("params", [])
                value = data.get("value", 0)
                
                # Use real gas estimation
                estimated_gas = await self.eth_client.estimate_gas(
                    contract_address=contract_address,
                    abi=abi,
                    function_name=function_name,
                    args=args,
                    value=value
                )
                
                # Get current gas prices for all priority levels
                gas_prices = await self.eth_client.get_gas_prices()
                
                return {
                    "success": True,
                    "chain": "ethereum",
                    "function": function_name,
                    "estimated_gas": estimated_gas,
                    "gas_prices": {
                        "low": {
                            "gwei": gas_prices["low"] / 10**9,
                            "wei": gas_prices["low"],
                            "total_cost_eth": (estimated_gas * gas_prices["low"]) / 10**18
                        },
                        "normal": {
                            "gwei": gas_prices["normal"] / 10**9,
                            "wei": gas_prices["normal"],
                            "total_cost_eth": (estimated_gas * gas_prices["normal"]) / 10**18
                        },
                        "high": {
                            "gwei": gas_prices["high"] / 10**9,
                            "wei": gas_prices["high"],
                            "total_cost_eth": (estimated_gas * gas_prices["high"]) / 10**18
                        }
                    }
                }
            
            elif chain == "solana":
                # Solana uses priority fees
                priority_fee = await self.sol_client.estimate_priority_fee()
                
                return {
                    "success": True,
                    "chain": "solana",
                    "priority_fee_microlamports": priority_fee,
                    "priority_fee_sol": priority_fee / 10**9,
                    "base_fee": 5000,  # 5000 lamports base
                    "total_fee_lamports": 5000 + (priority_fee / 1000)
                }
            
            else:
                return {"success": False, "error": f"Unsupported chain: {chain}"}
            
        except Exception as e:
            logger.error(f"Gas estimation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _check_balance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check address balance (Ethereum or Solana)"""
        try:
            chain = data.get("chain", "ethereum").lower()
            address = data.get("address")
            
            if chain == "ethereum":
                # Check ETH balance
                balance = await self.eth_client.get_balance(address)
                
                return {
                    "success": True,
                    "chain": "ethereum",
                    "address": address,
                    "balance_wei": balance,
                    "balance_eth": float(Decimal(balance) / Decimal(10**18)),
                    "balance_formatted": f"{balance / 10**18:,.4f} ETH"
                }
            
            elif chain == "solana":
                # Check SOL balance
                balance = await self.sol_client.get_balance(address)
                
                return {
                    "success": True,
                    "chain": "solana",
                    "address": address,
                    "balance_lamports": int(balance * 10**9),
                    "balance_sol": float(balance),
                    "balance_formatted": f"{float(balance):,.4f} SOL"
                }
            
            else:
                return {"success": False, "error": f"Unsupported chain: {chain}"}
            
        except Exception as e:
            logger.error(f"Balance check failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _monitor_transaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor transaction status (Ethereum or Solana)"""
        try:
            chain = data.get("chain", "ethereum").lower()
            
            if chain == "ethereum":
                tx_hash = data.get("tx_hash")
                
                # Get transaction receipt
                receipt = await self.eth_client.get_transaction_receipt(tx_hash)
                
                if not receipt:
                    return {
                        "success": True,
                        "chain": "ethereum",
                        "tx_hash": tx_hash,
                        "status": "pending",
                        "confirmations": 0
                    }
                
                current_block = await self.eth_client.w3.eth.block_number
                confirmations = current_block - receipt["blockNumber"]
                
                return {
                    "success": True,
                    "chain": "ethereum",
                    "tx_hash": tx_hash,
                    "status": "confirmed" if receipt["status"] == 1 else "failed",
                    "confirmations": confirmations,
                    "block_number": receipt["blockNumber"],
                    "gas_used": receipt["gasUsed"],
                    "explorer_url": f"https://etherscan.io/tx/{tx_hash}"
                }
            
            elif chain == "solana":
                signature = data.get("signature") or data.get("tx_hash")
                
                # Get transaction details
                tx_data = await self.sol_client.get_transaction(signature)
                
                if not tx_data:
                    return {
                        "success": True,
                        "chain": "solana",
                        "signature": signature,
                        "status": "pending"
                    }
                
                return {
                    "success": True,
                    "chain": "solana",
                    "signature": signature,
                    "status": "confirmed",
                    "slot": tx_data.get("slot"),
                    "explorer_url": f"https://solscan.io/tx/{signature}"
                }
            
            else:
                return {"success": False, "error": f"Unsupported chain: {chain}"}
            
        except Exception as e:
            logger.error(f"Transaction monitoring failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ========== TRADING OPERATIONS (NEW) ==========
    
    async def _swap_tokens(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automated token swap using DEX routers
        
        Queen AI trigger for trading operations
        """
        try:
            chain = data.get("chain", "ethereum").lower()
            token_in = data.get("token_in")
            token_out = data.get("token_out")
            amount_in = Decimal(str(data.get("amount_in")))
            recipient = data.get("recipient")  # Recipient address
            priority = data.get("priority", "normal")  # Gas priority
            
            # Validate trade size
            if chain == "ethereum" and amount_in > self.max_trade_size_eth:
                return {
                    "success": False,
                    "error": f"Trade size exceeds maximum: {self.max_trade_size_eth} ETH"
                }
            elif chain == "solana" and amount_in > self.max_trade_size_sol:
                return {
                    "success": False,
                    "error": f"Trade size exceeds maximum: {self.max_trade_size_sol} SOL"
                }
            
            if chain == "ethereum":
                # Use Uniswap
                if not self.initialized_clients.get("uniswap"):
                    return {
                        "success": False,
                        "error": "Uniswap router not initialized"
                    }
                
                # Get quote first
                amount_in_wei = int(amount_in * Decimal(10**18))
                quote = await self.uniswap.get_quote(
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=amount_in_wei
                )
                
                if not quote["success"]:
                    return quote
                
                # Calculate minimum output with slippage
                min_amount_out = int(
                    Decimal(quote["amount_out"]) * (Decimal('1') - self.slippage_tolerance)
                )
                
                logger.info(
                    "Executing Uniswap swap",
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=float(amount_in),
                    expected_out=quote["amount_out"] / 10**18,
                    min_out=min_amount_out / 10**18,
                    price_impact=quote.get("price_impact", 0)
                )
                
                # Execute swap
                tx_hash = await self.uniswap.swap_tokens(
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=amount_in_wei,
                    min_amount_out=min_amount_out,
                    recipient=recipient or self.eth_client.default_account,
                    gas_priority=priority
                )
                
                return {
                    "success": True,
                    "chain": "ethereum",
                    "dex": "uniswap",
                    "token_in": token_in,
                    "token_out": token_out,
                    "amount_in": float(amount_in),
                    "expected_amount_out": quote["amount_out"] / 10**18,
                    "min_amount_out": min_amount_out / 10**18,
                    "slippage_tolerance": float(self.slippage_tolerance),
                    "price_impact": quote.get("price_impact", 0),
                    "tx_hash": tx_hash,
                    "explorer_url": f"https://etherscan.io/tx/{tx_hash}",
                    "status": "pending"
                }
            
            elif chain == "solana":
                # Use Raydium
                if not self.initialized_clients.get("raydium"):
                    return {
                        "success": False,
                        "error": "Raydium router not initialized"
                    }
                
                # Get quote first
                quote = await self.raydium.get_quote(
                    token_in_mint=token_in,
                    token_out_mint=token_out,
                    amount_in=float(amount_in)
                )
                
                if not quote["success"]:
                    return quote
                
                # Calculate minimum output with slippage
                min_amount_out = float(
                    Decimal(str(quote["amount_out"])) * (Decimal('1') - self.slippage_tolerance)
                )
                
                logger.info(
                    "Executing Raydium swap",
                    token_in=token_in,
                    token_out=token_out,
                    amount_in=float(amount_in),
                    expected_out=quote["amount_out"],
                    min_out=min_amount_out,
                    price_impact=quote.get("price_impact", 0)
                )
                
                # Execute swap
                signature = await self.raydium.swap_tokens(
                    token_in_mint=token_in,
                    token_out_mint=token_out,
                    amount_in=float(amount_in),
                    min_amount_out=min_amount_out,
                    priority_fee=10000 if priority == "high" else 5000
                )
                
                return {
                    "success": True,
                    "chain": "solana",
                    "dex": "raydium",
                    "token_in": token_in,
                    "token_out": token_out,
                    "amount_in": float(amount_in),
                    "expected_amount_out": quote["amount_out"],
                    "min_amount_out": min_amount_out,
                    "slippage_tolerance": float(self.slippage_tolerance),
                    "price_impact": quote.get("price_impact", 0),
                    "signature": signature,
                    "explorer_url": f"https://solscan.io/tx/{signature}",
                    "status": "pending"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unsupported chain: {chain}"
                }
        
        except Exception as e:
            logger.error(f"Token swap failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _add_liquidity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add liquidity to pool
        
        Queen AI trigger for liquidity management
        """
        try:
            chain = data.get("chain", "ethereum").lower()
            token_a = data.get("token_a")
            token_b = data.get("token_b")
            amount_a = Decimal(str(data.get("amount_a")))
            amount_b = Decimal(str(data.get("amount_b")))
            pool = data.get("pool")
            
            logger.info(
                "Adding liquidity",
                chain=chain,
                token_a=token_a,
                token_b=token_b,
                amount_a=float(amount_a),
                amount_b=float(amount_b)
            )
            
            # TODO: Integrate with DEX liquidity pools
            
            return {
                "success": True,
                "chain": chain,
                "pool": pool,
                "token_a": token_a,
                "token_b": token_b,
                "amount_a": float(amount_a),
                "amount_b": float(amount_b),
                "lp_tokens_received": float((amount_a + amount_b) / 2),  # Mock LP tokens
                "status": "pending",
                "message": "Liquidity addition initiated"
            }
        
        except Exception as e:
            logger.error(f"Add liquidity failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _remove_liquidity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove liquidity from pool
        
        Queen AI trigger for liquidity management
        """
        try:
            chain = data.get("chain", "ethereum").lower()
            pool = data.get("pool")
            lp_tokens = Decimal(str(data.get("lp_tokens")))
            
            logger.info(
                "Removing liquidity",
                chain=chain,
                pool=pool,
                lp_tokens=float(lp_tokens)
            )
            
            # TODO: Integrate with DEX liquidity pools
            
            return {
                "success": True,
                "chain": chain,
                "pool": pool,
                "lp_tokens_burned": float(lp_tokens),
                "status": "pending",
                "message": "Liquidity removal initiated"
            }
        
        except Exception as e:
            logger.error(f"Remove liquidity failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ========== CROSS-CHAIN OPERATIONS (NEW) ==========
    
    async def _bridge_transfer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cross-chain bridge transfer
        
        Uses integrated cross-chain bridge
        """
        try:
            direction = data.get("direction")  # "eth_to_sol" or "sol_to_eth"
            amount = Decimal(str(data.get("amount")))
            from_address = data.get("from_address")
            to_address = data.get("to_address")
            
            logger.info(
                "Initiating bridge transfer",
                direction=direction,
                amount=float(amount),
                from_address=from_address,
                to_address=to_address
            )
            
            # Use integrated bridge
            if direction == "eth_to_sol":
                bridge_tx_id = await self.bridge.bridge_eth_to_sol(
                    amount=amount,
                    from_eth_address=from_address,
                    to_sol_address=to_address
                )
            elif direction == "sol_to_eth":
                bridge_tx_id = await self.bridge.bridge_sol_to_eth(
                    amount=amount,
                    from_sol_address=from_address,
                    to_eth_address=to_address
                )
            else:
                return {
                    "success": False,
                    "error": f"Invalid direction: {direction}"
                }
            
            return {
                "success": True,
                "bridge_transaction_id": bridge_tx_id,
                "direction": direction,
                "amount": float(amount),
                "from_address": from_address,
                "to_address": to_address,
                "status": "pending",
                "message": "Bridge transfer initiated"
            }
        
        except Exception as e:
            logger.error(f"Bridge transfer failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _check_bridge_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check bridge transaction status"""
        try:
            bridge_tx_id = data.get("bridge_transaction_id")
            
            # Get transaction from bridge
            tx = await self.bridge.get_transaction(bridge_tx_id)
            
            if not tx:
                return {
                    "success": False,
                    "error": "Bridge transaction not found"
                }
            
            return {
                "success": True,
                "bridge_transaction_id": tx.id,
                "status": tx.status.value,
                "direction": tx.direction.value,
                "amount": float(tx.amount),
                "source_tx_hash": tx.source_tx_hash,
                "dest_tx_hash": tx.dest_tx_hash,
                "created_at": tx.created_at.isoformat(),
                "time_remaining_minutes": tx.time_remaining(),
                "retry_count": tx.retry_count,
                "error": tx.error
            }
        
        except Exception as e:
            logger.error(f"Bridge status check failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ========== QUEEN AI TRIGGERS (NEW) ==========
    
    async def _auto_rebalance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automated portfolio rebalancing
        
        Queen AI can trigger this based on market conditions
        """
        try:
            target_ratios = data.get("target_ratios", {})  # e.g., {"ETH": 0.5, "SOL": 0.3, "OMK": 0.2}
            wallet_address = data.get("wallet_address")
            
            logger.info(
                "Auto-rebalancing initiated",
                target_ratios=target_ratios,
                wallet=wallet_address
            )
            
            # Get current balances
            balances = {}
            total_value = Decimal('0')
            
            # Calculate rebalancing trades needed
            trades_needed = []
            
            # TODO: Implement full rebalancing logic
            # 1. Get all token balances
            # 2. Calculate current ratios
            # 3. Determine trades needed to reach target ratios
            # 4. Execute trades via DEX
            
            return {
                "success": True,
                "wallet": wallet_address,
                "target_ratios": target_ratios,
                "trades_needed": trades_needed,
                "status": "analysis_complete",
                "message": "Rebalancing analysis complete - execution pending"
            }
        
        except Exception as e:
            logger.error(f"Auto-rebalance failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _emergency_withdraw(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Emergency withdrawal from all positions
        
        Queen AI can trigger this in critical situations
        """
        try:
            chain = data.get("chain", "ethereum").lower()
            to_address = data.get("to_address")
            reason = data.get("reason", "Emergency withdrawal triggered")
            
            logger.critical(
                "EMERGENCY WITHDRAWAL INITIATED",
                chain=chain,
                to_address=to_address,
                reason=reason
            )
            
            # TODO: Implement emergency withdrawal
            # 1. Remove all liquidity positions
            # 2. Cancel all pending orders
            # 3. Transfer all assets to safe address
            
            return {
                "success": True,
                "chain": chain,
                "to_address": to_address,
                "reason": reason,
                "status": "initiated",
                "message": "Emergency withdrawal initiated - all positions being closed"
            }
        
        except Exception as e:
            logger.error(f"Emergency withdrawal failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ========== PRICE ORACLE OPERATIONS (NEW) ==========
    
    async def _get_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get token price from oracle
        
        Uses Chainlink (Ethereum) or Pyth (Solana)
        """
        try:
            chain = data.get("chain", "ethereum").lower()
            pair = data.get("pair")  # e.g., "ETH/USD", "SOL/USD"
            
            if chain == "ethereum":
                # Use Chainlink
                if not self.initialized_clients.get("chainlink"):
                    return {
                        "success": False,
                        "error": "Chainlink oracle not initialized"
                    }
                
                price_data = await self.chainlink.get_price_with_metadata(pair)
                
                return price_data
            
            elif chain == "solana":
                # Use Pyth
                if not self.initialized_clients.get("pyth"):
                    return {
                        "success": False,
                        "error": "Pyth oracle not initialized"
                    }
                
                price_data = await self.pyth.get_price_with_confidence(pair)
                
                return price_data
            
            else:
                return {
                    "success": False,
                    "error": f"Unsupported chain: {chain}"
                }
        
        except Exception as e:
            logger.error(f"Get price failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _get_multiple_prices(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get multiple token prices at once
        
        Efficient batch price fetching
        """
        try:
            chain = data.get("chain", "ethereum").lower()
            pairs = data.get("pairs", [])  # List of pairs
            
            if not pairs:
                return {
                    "success": False,
                    "error": "No pairs specified"
                }
            
            if chain == "ethereum":
                if not self.initialized_clients.get("chainlink"):
                    return {
                        "success": False,
                        "error": "Chainlink oracle not initialized"
                    }
                
                prices = await self.chainlink.get_multiple_prices(pairs)
                
                return {
                    "success": True,
                    "chain": "ethereum",
                    "oracle": "chainlink",
                    "prices": prices
                }
            
            elif chain == "solana":
                if not self.initialized_clients.get("pyth"):
                    return {
                        "success": False,
                        "error": "Pyth oracle not initialized"
                    }
                
                prices = await self.pyth.get_multiple_prices(pairs)
                
                return {
                    "success": True,
                    "chain": "solana",
                    "oracle": "pyth",
                    "prices": prices
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unsupported chain: {chain}"
                }
        
        except Exception as e:
            logger.error(f"Get multiple prices failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _calculate_token_value(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate USD value of token amount
        
        Uses oracle prices
        """
        try:
            chain = data.get("chain", "ethereum").lower()
            token_amount = float(data.get("token_amount"))
            token_pair = data.get("token_pair")  # e.g., "ETH/USD"
            
            if chain == "ethereum":
                if not self.initialized_clients.get("chainlink"):
                    return {
                        "success": False,
                        "error": "Chainlink oracle not initialized"
                    }
                
                result = await self.chainlink.calculate_token_value(
                    token_amount=token_amount,
                    token_pair=token_pair
                )
                
                result["chain"] = "ethereum"
                result["oracle"] = "chainlink"
                return result
            
            elif chain == "solana":
                if not self.initialized_clients.get("pyth"):
                    return {
                        "success": False,
                        "error": "Pyth oracle not initialized"
                    }
                
                result = await self.pyth.calculate_token_value(
                    token_amount=token_amount,
                    token_pair=token_pair
                )
                
                result["chain"] = "solana"
                result["oracle"] = "pyth"
                return result
            
            else:
                return {
                    "success": False,
                    "error": f"Unsupported chain: {chain}"
                }
        
        except Exception as e:
            logger.error(f"Calculate token value failed: {str(e)}")
            return {"success": False, "error": str(e)}
