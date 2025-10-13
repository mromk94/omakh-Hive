"""
Wallet Manager - Multi-Wallet Management

Handles:
- Multiple wallet management
- HD wallet derivation
- Secure key storage
- Wallet rotation
- Balance tracking
"""
import os
from typing import Dict, Optional, List
from eth_account import Account
from eth_account.hdaccount import generate_mnemonic, seed_from_mnemonic
from eth_typing import HexStr
import structlog

logger = structlog.get_logger(__name__)


class WalletManager:
    """
    Manages multiple Ethereum wallets
    
    Features:
    - HD wallet generation from mnemonic
    - Multiple wallet accounts
    - Secure key management
    - Balance tracking across wallets
    """
    
    def __init__(self):
        self.wallets: Dict[str, Account] = {}
        self.mnemonic: Optional[str] = None
        self.current_wallet: Optional[str] = None
    
    def generate_wallet(self, name: str = "main") -> Account:
        """
        Generate new wallet with random private key
        
        Args:
            name: Wallet identifier
            
        Returns:
            Account object
        """
        account = Account.create()
        self.wallets[name] = account
        
        if not self.current_wallet:
            self.current_wallet = name
        
        logger.info(
            "Wallet generated",
            name=name,
            address=account.address
        )
        
        return account
    
    def create_from_mnemonic(
        self,
        mnemonic: Optional[str] = None,
        num_accounts: int = 1
    ) -> List[Account]:
        """
        Create HD wallet from mnemonic phrase
        
        Args:
            mnemonic: BIP39 mnemonic (generates if None)
            num_accounts: Number of accounts to derive
            
        Returns:
            List of Account objects
        """
        if mnemonic is None:
            mnemonic = generate_mnemonic(num_words=12, lang="english")
        
        self.mnemonic = mnemonic
        seed = seed_from_mnemonic(mnemonic, "")
        
        accounts = []
        for i in range(num_accounts):
            # Derive account using BIP44 path
            # m/44'/60'/0'/0/{i}
            account = Account.from_mnemonic(
                mnemonic,
                account_path=f"m/44'/60'/0'/0/{i}"
            )
            
            name = f"account_{i}"
            self.wallets[name] = account
            accounts.append(account)
            
            logger.info(
                "HD wallet account created",
                index=i,
                address=account.address
            )
        
        if not self.current_wallet and accounts:
            self.current_wallet = "account_0"
        
        return accounts
    
    def import_wallet(
        self,
        private_key: str,
        name: str = "imported"
    ) -> Account:
        """
        Import wallet from private key
        
        Args:
            private_key: Private key (hex string)
            name: Wallet identifier
            
        Returns:
            Account object
        """
        account = Account.from_key(private_key)
        self.wallets[name] = account
        
        if not self.current_wallet:
            self.current_wallet = name
        
        logger.info(
            "Wallet imported",
            name=name,
            address=account.address
        )
        
        return account
    
    def get_wallet(self, name: Optional[str] = None) -> Optional[Account]:
        """
        Get wallet by name
        
        Args:
            name: Wallet name (uses current if None)
            
        Returns:
            Account object or None
        """
        if name is None:
            name = self.current_wallet
        
        return self.wallets.get(name)
    
    def set_current_wallet(self, name: str):
        """Set active wallet"""
        if name not in self.wallets:
            raise ValueError(f"Wallet '{name}' not found")
        
        self.current_wallet = name
        logger.info(f"Current wallet set to: {name}")
    
    def list_wallets(self) -> List[Dict[str, str]]:
        """
        List all wallets
        
        Returns:
            List of wallet info dicts
        """
        return [
            {
                "name": name,
                "address": account.address,
                "is_current": name == self.current_wallet
            }
            for name, account in self.wallets.items()
        ]
    
    def export_private_key(self, name: str) -> str:
        """
        Export wallet private key
        
        Args:
            name: Wallet name
            
        Returns:
            Private key as hex string
        """
        wallet = self.get_wallet(name)
        if not wallet:
            raise ValueError(f"Wallet '{name}' not found")
        
        logger.warning(
            "Private key exported",
            name=name,
            address=wallet.address
        )
        
        return wallet.key.hex()
    
    def get_mnemonic(self) -> Optional[str]:
        """
        Get mnemonic phrase
        
        Returns:
            Mnemonic phrase or None
        """
        if self.mnemonic:
            logger.warning("Mnemonic phrase accessed")
        
        return self.mnemonic
    
    def sign_message(
        self,
        message: str,
        wallet_name: Optional[str] = None
    ) -> HexStr:
        """
        Sign message with wallet
        
        Args:
            message: Message to sign
            wallet_name: Wallet to use (current if None)
            
        Returns:
            Signature as hex string
        """
        wallet = self.get_wallet(wallet_name)
        if not wallet:
            raise ValueError("No wallet available")
        
        # Sign message
        signed_message = Account.sign_message(
            wallet._get_signing_key(),
            message.encode()
        )
        
        logger.debug(
            "Message signed",
            wallet=wallet_name or self.current_wallet,
            message_hash=signed_message.messageHash.hex()
        )
        
        return signed_message.signature.hex()
    
    def remove_wallet(self, name: str):
        """Remove wallet"""
        if name in self.wallets:
            del self.wallets[name]
            
            if self.current_wallet == name:
                self.current_wallet = next(iter(self.wallets.keys()), None)
            
            logger.info(f"Wallet removed: {name}")


# Global instance
wallet_manager = WalletManager()
