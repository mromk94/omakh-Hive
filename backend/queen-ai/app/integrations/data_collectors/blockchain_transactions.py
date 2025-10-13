"""
Blockchain Transactions Data Collector for Fivetran
Collects transaction data from Ethereum, Solana, etc.
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class BlockchainTransactionsConnector:
    """
    Collects blockchain transaction data for Fivetran
    
    Data Sources:
    - Ethereum RPC
    - Solana RPC
    - Block explorers (Etherscan, etc.)
    """
    
    def __init__(self):
        self.last_block_ethereum = None
        self.last_slot_solana = None
    
    async def collect_ethereum_transactions(self, from_block: int = None, to_block: int = 'latest') -> List[Dict]:
        """
        Collect Ethereum transactions
        
        Returns:
            List of transaction dictionaries
        """
        try:
            from web3 import Web3
            from app.config.settings import settings
            
            if not settings.ETHEREUM_RPC_URL:
                logger.warning("Ethereum RPC URL not configured")
                return []
            
            w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
            
            if not w3.is_connected():
                logger.error("Failed to connect to Ethereum RPC")
                return []
            
            # Get latest block if not specified
            if from_block is None:
                from_block = w3.eth.block_number - 100  # Last 100 blocks
            
            if to_block == 'latest':
                to_block = w3.eth.block_number
            
            transactions = []
            
            for block_number in range(from_block, min(to_block + 1, from_block + 100)):
                try:
                    block = w3.eth.get_block(block_number, full_transactions=True)
                    
                    for tx in block.transactions:
                        transactions.append({
                            'block_number': block_number,
                            'block_timestamp': datetime.fromtimestamp(block.timestamp).isoformat(),
                            'transaction_hash': tx.hash.hex(),
                            'from_address': tx['from'],
                            'to_address': tx.to,
                            'value_wei': str(tx.value),
                            'value_eth': float(w3.from_wei(tx.value, 'ether')),
                            'gas_price_gwei': float(w3.from_wei(tx.gasPrice, 'gwei')),
                            'gas_limit': tx.gas,
                            'nonce': tx.nonce,
                            'transaction_index': tx.transactionIndex,
                            'input_data': tx.input[:66]  # First 32 bytes
                        })
                
                except Exception as e:
                    logger.error(f"Failed to process block {block_number}: {str(e)}")
                    continue
            
            self.last_block_ethereum = to_block
            logger.info(f"Collected {len(transactions)} Ethereum transactions")
            
            return transactions
        
        except Exception as e:
            logger.error(f"Failed to collect Ethereum transactions: {str(e)}")
            return []
    
    async def collect_solana_transactions(self, limit: int = 1000) -> List[Dict]:
        """
        Collect Solana transactions
        
        Returns:
            List of transaction dictionaries
        """
        try:
            from solana.rpc.async_api import AsyncClient
            from app.config.settings import settings
            
            if not settings.SOLANA_RPC_URL:
                logger.warning("Solana RPC URL not configured")
                return []
            
            client = AsyncClient(settings.SOLANA_RPC_URL)
            
            # Get recent signatures
            signatures_response = await client.get_signatures_for_address(
                settings.OMK_SOLANA_ADDRESS if hasattr(settings, 'OMK_SOLANA_ADDRESS') else None,
                limit=limit
            )
            
            transactions = []
            
            if signatures_response and hasattr(signatures_response, 'value'):
                for sig_info in signatures_response.value[:100]:  # Process first 100
                    transactions.append({
                        'signature': str(sig_info.signature),
                        'slot': sig_info.slot,
                        'timestamp': datetime.fromtimestamp(sig_info.block_time).isoformat() if sig_info.block_time else None,
                        'err': str(sig_info.err) if sig_info.err else None,
                        'memo': sig_info.memo
                    })
            
            await client.close()
            
            logger.info(f"Collected {len(transactions)} Solana transactions")
            return transactions
        
        except Exception as e:
            logger.error(f"Failed to collect Solana transactions: {str(e)}")
            return []
    
    async def collect_all(self) -> Dict[str, List[Dict]]:
        """
        Collect transactions from all blockchains
        
        Returns:
            Dictionary with blockchain names as keys and transaction lists as values
        """
        ethereum_txs, solana_txs = await asyncio.gather(
            self.collect_ethereum_transactions(),
            self.collect_solana_transactions(),
            return_exceptions=True
        )
        
        return {
            'ethereum': ethereum_txs if not isinstance(ethereum_txs, Exception) else [],
            'solana': solana_txs if not isinstance(solana_txs, Exception) else []
        }
