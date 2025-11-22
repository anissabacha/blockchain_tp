# blockchain_app.py
import hashlib
import json
import time
from datetime import datetime
from typing import List

# -------------------- Block Class --------------------
class Block:
    def __init__(self, index: int, timestamp: float, data, previous_hash: str = '', nonce: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': datetime.utcfromtimestamp(self.timestamp).isoformat() + 'Z',
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }

# -------------------- Blockchain Class --------------------
class Blockchain:
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(index=0, timestamp=time.time(), data="Genesis Block", previous_hash="0")
        genesis.hash, _, _ = self.proof_of_work(genesis)  # Mine genesis block
        self.chain.append(genesis)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def proof_of_work(self, block: Block) -> tuple[str, int, float]:
        target = '0' * self.difficulty
        start = time.time()
        while True:
            block.hash = block.compute_hash()
            if block.hash.startswith(target):
                end = time.time()
                return block.hash, block.nonce, end - start
            block.nonce += 1

    def add_block(self, data) -> dict:
        new_block = Block(
            index=self.last_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=self.last_block.hash
        )
        mined_hash, nonce_used, time_taken = self.proof_of_work(new_block)
        new_block.hash = mined_hash
        self.chain.append(new_block)
        return {
            'index': new_block.index,
            'hash': new_block.hash,
            'nonce': new_block.nonce,
            'time_taken_sec': time_taken
        }

    def is_chain_valid(self) -> tuple[bool, str]:
        target = '0' * self.difficulty
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.previous_hash != previous.hash:
                return False, f"Block {current.index} previous_hash mismatch."
            if current.compute_hash() != current.hash:
                return False, f"Block {current.index} hash mismatch."
            if not current.hash.startswith(target):
                return False, f"Block {current.index} does not meet difficulty."
        return True, "Chain is valid."

    def tamper_with_block(self, index: int, new_data):
        if index <= 0 or index >= len(self.chain):
            raise IndexError("Invalid block index to tamper with.")
        self.chain[index].data = new_data

    def print_chain(self):
        for b in self.chain:
            print(json.dumps(b.to_dict(), indent=2, ensure_ascii=False))

    def average_nonce(self) -> float:
        if len(self.chain) <= 1:
            return 0.0
        total_nonce = sum(b.nonce for b in self.chain[1:])
        return total_nonce / (len(self.chain) - 1)


# -------------------- Main Execution --------------------
if __name__ == "__main__":
    blockchain = Blockchain(difficulty=2)

    # Add blocks
    blockchain.add_block("First transaction")
    blockchain.add_block("Second transaction")
    blockchain.add_block("Third transaction")

    print("\nFull Blockchain:")
    blockchain.print_chain()

    # Validate blockchain
    valid, message = blockchain.is_chain_valid()
    print(f"\nIs blockchain valid? {valid}, Message: {message}")

    # Tamper with a block
    print("\nTampering with Block 1...")
    blockchain.tamper_with_block(1, "Hacked data")

    # Validate again
    valid, message = blockchain.is_chain_valid()
    print(f"Is blockchain valid after tampering? {valid}, Message: {message}")

    # Average nonce
    print(f"\nAverage nonce: {blockchain.average_nonce():.2f}")
