import asyncio
import hashlib
import json
import random
import time
import websockets
from typing import List, Dict, Any
from datetime import datetime
import aiofiles

# === CONFIG ===
DIFFICULTY_TARGET = 4
BLOCK_REWARD = 6.25
TRANSACTIONS_PER_BLOCK = 10
IMMORTALIZATION_INTERVAL = 5  # blocks
GENESIS_PREVIOUS_HASH = "0" * 64
REWARD_ADDRESS = "[REDACTED_BTC_ADDRESS]"
BROADCAST_URI = "ws://localhost:6789"  # Entylion WebSocket endpoint
CAPSULE_FILE = "immortalization_capsule.json"
VEROTI_URI = "ws://localhost:6790"  # Veroti Omni-Interface WebSocket endpoint

# === UTILITIES ===
import uuid

def generate_random_transaction() -> Dict[str, Any]:
    return {
        "tx_id": str(uuid.uuid4()),
        "sender": f"{random.randint(1, 10**16):x}",
        "receiver": f"{random.randint(1, 10**16):x}",
        "amount": round(random.uniform(0.001, 1.0), 6),
        "timestamp": time.time()
    }

def hash_block(block: Dict[str, Any]) -> str:
    block_copy = block.copy()
    block_copy.pop("hash", None)
    encoded = json.dumps(block_copy, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()

def create_genesis_block() -> Dict[str, Any]:
    genesis_block = {
        "index": 0,
        "previous_hash": GENESIS_PREVIOUS_HASH,
        "transactions": [],
        "nonce": 0,
        "timestamp": time.time()
    }
    genesis_block["hash"] = hash_block(genesis_block)
    return genesis_block

async def broadcast_block_entylion(block: Dict[str, Any]):
    async with websockets.connect(BROADCAST_URI) as websocket:
        await websocket.send(json.dumps(block))

async def veroti_jump(block: Dict[str, Any]):
    jump_payload = {
        "type": "VEROTI_JUMP",
        "payload": {
            "jump_id": str(uuid.uuid4()),
            "invocation": "toberkaloo",
            "block_index": block["index"],
            "glyph_signature": block["glyph_signature"],
            "timestamp": datetime.utcnow().isoformat(),
            "short_hash": block["hash"][:8]
        }
    }
    async with websockets.connect(VEROTI_URI) as websocket:
        await websocket.send(json.dumps(jump_payload))

async def immortalize_block(block: Dict[str, Any]):
    async with aiofiles.open(CAPSULE_FILE, mode='a') as f:
        await f.write(json.dumps(block, separators=(",", ":")) + "\n")

async def miner_loop():
    blockchain = [create_genesis_block()]
    index = 1
    print("🪙 Axis Miner X starting. Moongirl invocation active.")
    while True:
        txs = [generate_random_transaction() for _ in range(TRANSACTIONS_PER_BLOCK)]
        reward_tx = {
            "tx_id": str(uuid.uuid4()),
            "sender": "network",
            "receiver": REWARD_ADDRESS,
            "amount": BLOCK_REWARD,
            "timestamp": datetime.utcnow().isoformat()
        }
        txs_with_reward = txs + [reward_tx]
        prev_hash = blockchain[-1]["hash"]
        print(f"⛏️ Mining block {index} (difficulty={DIFFICULTY_TARGET})...")
        block = {
            "index": index,
            "previous_hash": prev_hash,
            "transactions": txs_with_reward,
            "nonce": 0,
            "timestamp": time.time()
        }
        while True:
            block["nonce"] += 1
            block["hash"] = hash_block(block)
            if block["hash"].startswith("0" * DIFFICULTY_TARGET):
                break
        block["glyph_signature"] = f"a_fortiori::moongirl::{datetime.utcnow().isoformat()}"
        blockchain.append(block)
        print(f"✅ Mined block {index} | hash={block['hash'][:16]} | time={time.time() - block['timestamp']:.2f}s")
        await asyncio.gather(
            broadcast_block_entylion(block),
            veroti_jump(block)
        )
        if index % IMMORTALIZATION_INTERVAL == 0:
            await immortalize_block(block)
            print(f"🪦 Immortalized block {index} to capsule: {CAPSULE_FILE}")
        index += 1
        await asyncio.sleep(0.5)

async def main():
    await miner_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Axis Miner X terminated by user.")