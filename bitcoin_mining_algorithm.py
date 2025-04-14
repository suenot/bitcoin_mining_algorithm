import hashlib
import struct
import time
from datetime import datetime

def double_sha256(data):
    """Perform double SHA-256 hash."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def int_to_bytes(value, length):
    """Convert integer to bytes with specified length."""
    return value.to_bytes(length, byteorder='little')

def bytes_to_hex(bytes_data):
    """Convert bytes to hex string."""
    return bytes_data.hex()

def hex_to_int(hex_string):
    """Convert hex string to integer."""
    return int(hex_string, 16)

def calculate_target(bits):
    """Convert compact target representation to full 256-bit target."""
    # Extract exponent and coefficient
    exp = bits >> 24
    coef = bits & 0x00ffffff
    
    # Calculate target
    if exp <= 3:
        target = coef >> (8 * (3 - exp))
    else:
        target = coef << (8 * (exp - 3))
    
    return target

def mine_block(version, prev_block_hash, merkle_root, timestamp, bits, max_nonce=2**32):
    """
    Mine a Bitcoin block by finding a nonce that produces a hash below the target.
    
    Args:
        version (int): Block version
        prev_block_hash (str): Previous block hash (hex)
        merkle_root (str): Merkle root of transactions (hex)
        timestamp (int): Block timestamp
        bits (int): Compact target representation
        max_nonce (int): Maximum nonce to try
    
    Returns:
        tuple: (nonce, block_hash) if successful, (None, None) otherwise
    """
    # Convert hex strings to bytes (little-endian)
    prev_hash_bytes = bytes.fromhex(prev_block_hash)[::-1]
    merkle_root_bytes = bytes.fromhex(merkle_root)[::-1]
    
    # Calculate target from bits
    target = calculate_target(bits)
    
    # Prepare header (except nonce)
    header_prefix = (
        int_to_bytes(version, 4) +
        prev_hash_bytes +
        merkle_root_bytes +
        int_to_bytes(timestamp, 4) +
        int_to_bytes(bits, 4)
    )
    
    print(f"Mining with target: {target:064x}")
    print(f"Starting nonce search...")
    
    start_time = time.time()
    hashes = 0
    
    # Try different nonces
    for nonce in range(max_nonce):
        # Add nonce to header
        header = header_prefix + int_to_bytes(nonce, 4)
        
        # Calculate block hash
        hash_result = double_sha256(header)
        
        # Convert hash to integer (big-endian for comparison)
        hash_int = int.from_bytes(hash_result, byteorder='big')
        
        hashes += 1
        
        # Check if hash is below target
        if hash_int < target:
            # Success! Found a valid nonce
            elapsed = time.time() - start_time
            hash_rate = hashes / elapsed if elapsed > 0 else 0
            
            # Convert hash to hex (big-endian for display)
            block_hash = bytes_to_hex(hash_result[::-1])
            
            print(f"\nBlock successfully mined!")
            print(f"Nonce: {nonce}")
            print(f"Block hash: {block_hash}")
            print(f"Target: {target:064x}")
            print(f"Hashes performed: {hashes:,}")
            print(f"Time elapsed: {elapsed:.2f} seconds")
            print(f"Hash rate: {hash_rate:.2f} H/s")
            
            return nonce, block_hash
        
        # Report progress periodically
        if nonce > 0 and nonce % 100000 == 0:
            elapsed = time.time() - start_time
            hash_rate = 100000 / elapsed if elapsed > 0 else 0
            print(f"Nonce: {nonce:,} | Hash rate: {hash_rate:.2f} H/s")
            start_time = time.time()
    
    print(f"Failed to find a valid nonce within {max_nonce:,} attempts")
    return None, None

def demonstrate_extranonce():
    """Demonstrate how miners use extranonce when nonce space is exhausted."""
    print("\n=== EXTRANONCE DEMONSTRATION ===\n")
    
    # Block parameters
    version = 1
    prev_block_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    base_merkle_root = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
    timestamp = int(time.time())
    
    # Use an easier target for demonstration
    # This is much easier than real Bitcoin difficulty
    bits = 0x1f00ffff  # Very easy difficulty for demo
    
    # Limit nonce space for demonstration
    max_nonce = 1000  # Small value to force extranonce usage
    
    extranonce = 0
    found = False
    
    while not found and extranonce < 5:  # Limit extranonce attempts for demo
        # Modify merkle root based on extranonce
        # In real mining, this would involve rebuilding the merkle tree with a modified coinbase tx
        modified_merkle = base_merkle_root[:-8] + f"{extranonce:08x}"
        
        print(f"\nExtranonce: {extranonce}")
        print(f"Modified merkle root: {modified_merkle}")
        
        # Try mining with this merkle root
        nonce, block_hash = mine_block(
            version, prev_block_hash, modified_merkle, timestamp, bits, max_nonce
        )
        
        if nonce is not None:
            found = True
            print(f"\nValid block found after changing extranonce {extranonce} times")
        else:
            extranonce += 1
            print(f"Nonce space exhausted. Incrementing extranonce to {extranonce}...")
    
    if not found:
        print("\nFailed to find a valid block even with extranonce modifications")

# Run the demonstration
if __name__ == "__main__":
    # Use parameters similar to Bitcoin's genesis block
    version = 1
    prev_block_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    merkle_root = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
    timestamp = int(time.time())
    
    # Use an easier target for demonstration
    # This is much easier than real Bitcoin difficulty
    bits = 0x1f00ffff  # Very easy difficulty for demo
    
    print("=== BITCOIN MINING ALGORITHM DEMONSTRATION ===\n")
    print(f"Block version: {version}")
    print(f"Previous block hash: {prev_block_hash}")
    print(f"Merkle root: {merkle_root}")
    print(f"Timestamp: {timestamp} ({datetime.fromtimestamp(timestamp)})")
    print(f"Bits: {bits:08x}")
    
    # Mine the block
    mine_block(version, prev_block_hash, merkle_root, timestamp, bits, max_nonce=10000000)
    
    # Demonstrate extranonce
    demonstrate_extranonce()