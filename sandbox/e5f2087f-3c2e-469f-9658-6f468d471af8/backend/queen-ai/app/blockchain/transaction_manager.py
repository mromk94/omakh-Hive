"""
Transaction Manager - Queue & Batch Processing

Handles:
- Transaction queuing
- Batch processing
- Priority management
- Transaction tracking
- Failed transaction retry
- Gas optimization
"""
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class TransactionStatus(Enum):
    """Transaction status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TransactionPriority(Enum):
    """Transaction priority"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Transaction:
    """Transaction data structure"""
    id: str
    to: str
    value: int = 0
    data: str = "0x"
    priority: TransactionPriority = TransactionPriority.NORMAL
    status: TransactionStatus = TransactionStatus.PENDING
    tx_hash: Optional[str] = None
    block_number: Optional[int] = None
    gas_used: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TransactionManager:
    """
    Manages transaction queue and batch processing
    
    Features:
    - Priority queue for transactions
    - Batch processing for gas efficiency
    - Automatic retry for failed transactions
    - Transaction status tracking
    - Gas optimization across batches
    """
    
    def __init__(self, ethereum_client=None):
        self.ethereum_client = ethereum_client
        self.queue: List[Transaction] = []
        self.pending: Dict[str, Transaction] = {}
        self.confirmed: Dict[str, Transaction] = {}
        self.failed: Dict[str, Transaction] = {}
        
        self.processing = False
        self.max_batch_size = 10
        self.min_batch_delay = 5  # seconds
        
        self._lock = asyncio.Lock()
    
    async def add_transaction(
        self,
        tx_id: str,
        to: str,
        value: int = 0,
        data: str = "0x",
        priority: TransactionPriority = TransactionPriority.NORMAL,
        metadata: Optional[Dict] = None
    ) -> Transaction:
        """
        Add transaction to queue
        
        Args:
            tx_id: Unique transaction identifier
            to: Recipient address
            value: Amount in wei
            data: Transaction data
            priority: Transaction priority
            metadata: Additional metadata
            
        Returns:
            Transaction object
        """
        async with self._lock:
            tx = Transaction(
                id=tx_id,
                to=to,
                value=value,
                data=data,
                priority=priority,
                metadata=metadata or {}
            )
            
            # Insert in priority order
            inserted = False
            for i, queued_tx in enumerate(self.queue):
                if tx.priority.value > queued_tx.priority.value:
                    self.queue.insert(i, tx)
                    inserted = True
                    break
            
            if not inserted:
                self.queue.append(tx)
            
            logger.info(
                "Transaction queued",
                tx_id=tx_id,
                to=to,
                priority=priority.name,
                queue_size=len(self.queue)
            )
            
            return tx
    
    async def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        # Check all storage locations
        if tx_id in self.pending:
            return self.pending[tx_id]
        if tx_id in self.confirmed:
            return self.confirmed[tx_id]
        if tx_id in self.failed:
            return self.failed[tx_id]
        
        # Check queue
        for tx in self.queue:
            if tx.id == tx_id:
                return tx
        
        return None
    
    async def cancel_transaction(self, tx_id: str) -> bool:
        """
        Cancel pending transaction
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            True if cancelled
        """
        async with self._lock:
            # Remove from queue
            for i, tx in enumerate(self.queue):
                if tx.id == tx_id:
                    tx.status = TransactionStatus.CANCELLED
                    self.queue.pop(i)
                    self.failed[tx_id] = tx
                    
                    logger.info(f"Transaction cancelled: {tx_id}")
                    return True
            
            # Can't cancel if already submitted
            if tx_id in self.pending:
                logger.warning(f"Cannot cancel submitted transaction: {tx_id}")
                return False
            
            return False
    
    async def process_queue(self):
        """Process transaction queue"""
        if self.processing:
            logger.debug("Queue already processing")
            return
        
        self.processing = True
        
        try:
            while self.queue or self.pending:
                # Process pending confirmations
                await self._check_pending_transactions()
                
                # Process queued transactions
                if self.queue:
                    batch = await self._get_next_batch()
                    if batch:
                        await self._process_batch(batch)
                
                # Wait before next iteration
                await asyncio.sleep(self.min_batch_delay)
        
        finally:
            self.processing = False
    
    async def _get_next_batch(self) -> List[Transaction]:
        """Get next batch of transactions"""
        async with self._lock:
            batch = []
            
            for _ in range(min(self.max_batch_size, len(self.queue))):
                if self.queue:
                    tx = self.queue.pop(0)
                    batch.append(tx)
            
            return batch
    
    async def _process_batch(self, batch: List[Transaction]):
        """Process batch of transactions"""
        logger.info(f"Processing batch of {len(batch)} transactions")
        
        for tx in batch:
            try:
                await self._submit_transaction(tx)
            except Exception as e:
                logger.error(
                    f"Failed to submit transaction: {str(e)}",
                    tx_id=tx.id
                )
                
                tx.error = str(e)
                tx.retry_count += 1
                
                if tx.retry_count < tx.max_retries:
                    # Re-queue for retry
                    async with self._lock:
                        self.queue.append(tx)
                    logger.info(f"Transaction re-queued for retry: {tx.id}")
                else:
                    # Max retries reached
                    tx.status = TransactionStatus.FAILED
                    self.failed[tx.id] = tx
                    logger.error(f"Transaction failed (max retries): {tx.id}")
    
    async def _submit_transaction(self, tx: Transaction):
        """Submit single transaction"""
        if not self.ethereum_client:
            raise RuntimeError("Ethereum client not configured")
        
        logger.info(f"Submitting transaction: {tx.id}")
        
        # Send transaction
        tx_hash = await self.ethereum_client.send_transaction(
            to=tx.to,
            value=tx.value,
            data=tx.data
        )
        
        # Update transaction
        tx.tx_hash = tx_hash
        tx.status = TransactionStatus.SUBMITTED
        tx.submitted_at = datetime.utcnow()
        
        # Move to pending
        async with self._lock:
            self.pending[tx.id] = tx
        
        logger.info(
            "Transaction submitted",
            tx_id=tx.id,
            tx_hash=tx_hash
        )
    
    async def _check_pending_transactions(self):
        """Check status of pending transactions"""
        pending_ids = list(self.pending.keys())
        
        for tx_id in pending_ids:
            tx = self.pending[tx_id]
            
            try:
                if not tx.tx_hash:
                    continue
                
                # Check if confirmed
                receipt = await self.ethereum_client.w3.eth.get_transaction_receipt(
                    tx.tx_hash
                )
                
                if receipt:
                    # Transaction confirmed
                    tx.status = TransactionStatus.CONFIRMED
                    tx.confirmed_at = datetime.utcnow()
                    tx.block_number = receipt['blockNumber']
                    tx.gas_used = receipt['gasUsed']
                    
                    # Move to confirmed
                    async with self._lock:
                        del self.pending[tx_id]
                        self.confirmed[tx_id] = tx
                    
                    logger.info(
                        "Transaction confirmed",
                        tx_id=tx_id,
                        tx_hash=tx.tx_hash,
                        block=tx.block_number,
                        gas_used=tx.gas_used
                    )
            
            except Exception as e:
                # Transaction not yet mined
                logger.debug(f"Transaction pending: {tx_id}")
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get queue status"""
        return {
            "queued": len(self.queue),
            "pending": len(self.pending),
            "confirmed": len(self.confirmed),
            "failed": len(self.failed),
            "processing": self.processing,
            "queue_details": [
                {
                    "id": tx.id,
                    "priority": tx.priority.name,
                    "status": tx.status.name,
                    "retry_count": tx.retry_count
                }
                for tx in self.queue
            ]
        }
    
    async def clear_confirmed(self, older_than_minutes: int = 60):
        """
        Clear old confirmed transactions
        
        Args:
            older_than_minutes: Remove transactions older than this
        """
        cutoff = datetime.utcnow()
        cutoff = cutoff.replace(minute=cutoff.minute - older_than_minutes)
        
        to_remove = []
        for tx_id, tx in self.confirmed.items():
            if tx.confirmed_at and tx.confirmed_at < cutoff:
                to_remove.append(tx_id)
        
        async with self._lock:
            for tx_id in to_remove:
                del self.confirmed[tx_id]
        
        if to_remove:
            logger.info(f"Cleared {len(to_remove)} old confirmed transactions")
    
    async def retry_failed(self):
        """Retry all failed transactions"""
        async with self._lock:
            failed_txs = list(self.failed.values())
            self.failed.clear()
            
            for tx in failed_txs:
                tx.retry_count = 0
                tx.error = None
                tx.status = TransactionStatus.PENDING
                self.queue.append(tx)
        
        logger.info(f"Re-queued {len(failed_txs)} failed transactions")
    
    async def estimate_batch_gas(self, batch: List[Transaction]) -> int:
        """
        Estimate total gas for batch
        
        Args:
            batch: List of transactions
            
        Returns:
            Total estimated gas
        """
        if not self.ethereum_client:
            return 0
        
        total_gas = 0
        
        for tx in batch:
            try:
                gas = await self.ethereum_client.estimate_gas({
                    'to': tx.to,
                    'value': tx.value,
                    'data': tx.data
                })
                total_gas += gas
            except Exception as e:
                logger.warning(f"Gas estimation failed: {str(e)}")
                total_gas += 21000  # Default
        
        return total_gas
    
    async def optimize_batch_order(self, batch: List[Transaction]) -> List[Transaction]:
        """
        Optimize batch order for gas efficiency
        
        Args:
            batch: List of transactions
            
        Returns:
            Optimized list
        """
        # Sort by:
        # 1. Priority (descending)
        # 2. Gas estimate (ascending) - cheaper first
        # 3. Created time (ascending) - oldest first
        
        return sorted(
            batch,
            key=lambda tx: (
                -tx.priority.value,
                0,  # TODO: Add actual gas estimate
                tx.created_at
            )
        )


# Global instance
transaction_manager = TransactionManager()
