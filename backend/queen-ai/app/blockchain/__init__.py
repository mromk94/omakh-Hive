"""
Blockchain Integration Package

Multi-chain blockchain interactions for OMK Hive.
"""
from .ethereum_client import EthereumClient, ethereum_client
from .solana_client import SolanaClient, solana_client
from .wallet_manager import WalletManager, wallet_manager
from .transaction_manager import TransactionManager, transaction_manager
from .bridge import CrossChainBridge, cross_chain_bridge

__all__ = [
    'EthereumClient',
    'ethereum_client',
    'SolanaClient',
    'solana_client',
    'WalletManager',
    'wallet_manager',
    'TransactionManager',
    'transaction_manager',
    'CrossChainBridge',
    'cross_chain_bridge'
]
