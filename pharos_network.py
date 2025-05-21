import json
import time
import random
import asyncio
import sys
import aiohttp
from web3 import Web3, AsyncWeb3
from eth_account import Account
from eth_account.messages import encode_defunct
from aiohttp import ClientTimeout
from datetime import datetime

# Constants
BASE_URL = "https://api.pharosnetwork.xyz"
LOGIN = "/user/login"
CHECK_IN = "/sign/in"
FAUCET_STATUS = "/faucet/status"
CLAIM_FAUCET = "/faucet/daily"
PROFILE = "/user/profile"
TASK_VERIFY = "/task/verify"

ORIGIN = "https://testnet.pharosnetwork.xyz"
REFERER = "https://testnet.pharosnetwork.xyz/"

RPC_URL = "https://testnet.dplabs-internal.com"
CHAINID = 688688
WPHRS_CONTRACT = "0x76aaada469d23216be5f7c596fa25f282ff9b364"

# ERC20 ABI for WPHRS token
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [{"name": "wad", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

# Simple logger
class Logger:
    colors = {
        "reset": "\033[0m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
    }
    
    @staticmethod
    def log(message, color=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if color and color in Logger.colors:
            print(f"[{timestamp}] {Logger.colors[color]}{message}{Logger.colors['reset']}")
        else:
            print(f"[{timestamp}] {message}")
    
    @staticmethod
    def info(message):
        Logger.log(message, "blue")
    
    @staticmethod
    def success(message):
        Logger.log(message, "green")
    
    @staticmethod
    def warning(message):
        Logger.log(message, "yellow")
    
    @staticmethod
    def error(message):
        Logger.log(message, "red")

class PharosClient:
    def __init__(self, private_key):
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.token = None
        self.points = 0
        self.web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(RPC_URL))
        self.session = None
        
    def mask_address(self):
        addr = self.address
        return f"{addr[:6]}...{addr[-4:]}"
    
    async def initialize_session(self):
        timeout = ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        self.session.headers.update({
            "Origin": ORIGIN,
            "Referer": REFERER,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })
    
    def get_signature(self, message):
        try:
            Logger.info(f"Getting signature for {self.mask_address()}")
            msg = encode_defunct(text=message)
            signed = self.account.sign_message(msg)
            return f"0x{signed.signature.hex()}"
        except Exception as e:
            Logger.error(f"Error getting signature: {str(e)}")
            return None
    
    async def login(self):
        Logger.info(f"Logging in as {self.mask_address()}")
        
        message = "pharos"
        signature = self.get_signature(message)
        if not signature:
            return False
            
        url = f"{BASE_URL}{LOGIN}?address={self.address}&signature={signature}"
        
        try:
            async with self.session.post(url) as response:
                result = await response.json()
                
                if result.get("code") == 0:
                    self.token = result.get("data", {}).get("jwt", None)
                    self.session.headers.update({"authorization": f"Bearer {self.token}"})
                    Logger.success("Login successful")
                    return True
                else:
                    Logger.error(f"Login failed: {result.get('msg', 'Unknown error')}")
                    return False
        except Exception as e:
            Logger.error(f"Login request failed: {str(e)}")
            return False
    
    async def get_points(self):
        Logger.info(f"Getting points for {self.mask_address()}")
        
        url = f"{BASE_URL}{PROFILE}?address={self.address}"
        
        try:
            async with self.session.get(url) as response:
                result = await response.json()
                
                if result.get("code") == 0:
                    user_info = result.get("data", {}).get("user_info", {})
                    self.points = user_info.get("TotalPoints", 0)
                    Logger.success(f"Total Points: {self.points}")
                    return self.points
                else:
                    Logger.error(f"Failed to get points: {result.get('msg', 'Unknown error')}")
                    return 0
        except Exception as e:
            Logger.error(f"Points request failed: {str(e)}")
            return 0
    
    async def check_in(self):
        Logger.info("Performing daily check-in")
        
        url = f"{BASE_URL}{CHECK_IN}?address={self.address}"
        
        try:
            async with self.session.post(url) as response:
                result = await response.json()
                
                if result.get("code") == 0:
                    Logger.success("Check-in successful")
                    return True
                else:
                    Logger.error(f"Check-in failed: {result.get('msg', 'Unknown error')}")
                    return False
        except Exception as e:
            Logger.error(f"Check-in request failed: {str(e)}")
            return False
    
    async def get_faucet_status(self):
        Logger.info("Checking faucet status")
        
        url = f"{BASE_URL}{FAUCET_STATUS}?address={self.address}"
        
        try:
            async with self.session.get(url) as response:
                result = await response.json()
                
                if result.get("code") == 0:
                    is_able_to_faucet = result.get("data", {}).get("is_able_to_faucet", False)
                    
                    if is_able_to_faucet:
                        Logger.success("Faucet is available for claim")
                        return True
                    else:
                        available_timestamp = result.get("data", {}).get("avaliable_timestamp", 0)
                        current_timestamp = int(time.time())
                        remaining_seconds = available_timestamp - current_timestamp
                        
                        hours, remainder = divmod(remaining_seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        
                        Logger.warning(f"Faucet not ready. Next claim in: {int(hours)}h {int(minutes)}m {int(seconds)}s")
                        return False
                else:
                    Logger.error(f"Failed to check faucet status: {result.get('msg', 'Unknown error')}")
                    return False
        except Exception as e:
            Logger.error(f"Faucet status request failed: {str(e)}")
            return False
    
    async def claim_faucet(self):
        if not await self.get_faucet_status():
            return False
            
        Logger.info("Claiming faucet")
        
        url = f"{BASE_URL}{CLAIM_FAUCET}?address={self.address}"
        
        try:
            async with self.session.post(url) as response:
                result = await response.json()
                
                if result.get("code") == 0:
                    Logger.success("Faucet claimed successfully")
                    return True
                else:
                    Logger.error(f"Failed to claim faucet: {result.get('msg', 'Unknown error')}")
                    return False
        except Exception as e:
            Logger.error(f"Faucet claim request failed: {str(e)}")
            return False
    
    async def get_balance(self, token_address=None):
        try:
            if token_address is None:
                balance_wei = await self.web3.eth.get_balance(self.address)
                balance_eth = self.web3.from_wei(balance_wei, "ether")
                return float(balance_eth)
            else:
                token_contract = self.web3.eth.contract(
                    address=Web3.to_checksum_address(token_address), 
                    abi=ERC20_ABI
                )
                decimals = await token_contract.functions.decimals().call()
                balance_wei = await token_contract.functions.balanceOf(self.address).call()
                balance = balance_wei / (10**decimals)
                return float(balance)
        except Exception as e:
            Logger.error(f"Error getting balance: {str(e)}")
            return 0
    
    async def get_gas_params(self):
        try:
            latest_block = await self.web3.eth.get_block("latest")
            base_fee = latest_block["baseFeePerGas"]
            max_priority_fee = await self.web3.eth.max_priority_fee
            max_fee = base_fee + max_priority_fee
            return {
                "maxFeePerGas": max_fee,
                "maxPriorityFeePerGas": max_priority_fee,
            }
        except:
            # Fallback to gasPrice if EIP-1559 is not supported
            gas_price = await self.web3.eth.gas_price
            return {"gasPrice": gas_price}
    
    async def transfer(self, index, target_address=None):
        try:
            if target_address is None:
                target_address = self.address
                
            amount = round(random.uniform(0.001, 0.01), 6)
            address = Web3.to_checksum_address(target_address)
            total_bal = await self.get_balance()
            
            if amount > total_bal:
                Logger.warning(f"Insufficient balance: {total_bal} < {amount}")
                return None
            
            amount_in_wei = self.web3.to_wei(amount, "ether")
            nonce = await self.web3.eth.get_transaction_count(self.address)
            
            gas_params = await self.get_gas_params()
            
            tx = {
                "to": address,
                "value": amount_in_wei,
                "chainId": CHAINID,
                "nonce": nonce,
                "gas": 21000,  # Standard gas for ETH transfer
                **gas_params
            }
            
            signed_txn = self.web3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = await self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            await self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            hex_hash = f"0x{tx_hash.hex()}"
            Logger.success(f"Transfer [{index}] - Amount: {amount} - Hash: {hex_hash[:10]}...")
            return hex_hash
            
        except Exception as e:
            Logger.error(f"Transfer error: {str(e)}")
            return None
    
    async def verify_task(self, task_id, tx_hash):
        Logger.info(f"Verifying task {task_id}")
        
        url = f"{BASE_URL}{TASK_VERIFY}?address={self.address}&task_id={task_id}&tx_hash={tx_hash}"
        
        try:
            async with self.session.post(url) as response:
                result = await response.json()
                
                if result.get("code") == 0:
                    Logger.success(f"Task verification successful: {result.get('msg', '')}")
                    return True
                else:
                    Logger.error(f"Task verification failed: {result.get('msg', 'Unknown error')}")
                    return False
        except Exception as e:
            Logger.error(f"Task verification request failed: {str(e)}")
            return False
    
    async def perform_wrapped(self, amount):
        try:
            contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(WPHRS_CONTRACT), 
                abi=ERC20_ABI
            )
            
            amount_wei = self.web3.to_wei(amount, "ether")
            gas_price = await self.web3.eth.gas_price
            nonce = await self.web3.eth.get_transaction_count(self.address)
            
            txn = await contract.functions.deposit().build_transaction({
                "from": self.address,
                "value": amount_wei,
                "gas": 50000,
                "gasPrice": gas_price,
                "nonce": nonce,
            })
            
            signed_tx = self.web3.eth.account.sign_transaction(txn, self.private_key)
            tx_hash = self.web3.to_hex(
                await self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            )
            receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            Logger.success(f"Wrapped {amount} PHRS to WPHRS - Hash: {tx_hash[:10]}...")
            return tx_hash, receipt.blockNumber
            
        except Exception as e:
            Logger.error(f"Wrapping error: {str(e)}")
            return None, None
    
    async def perform_unwrapped(self, amount):
        try:
            contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(WPHRS_CONTRACT), 
                abi=ERC20_ABI
            )
            
            amount_wei = self.web3.to_wei(amount, "ether")
            gas_price = await self.web3.eth.gas_price
            nonce = await self.web3.eth.get_transaction_count(self.address)
            
            txn = await contract.functions.withdraw(amount_wei).build_transaction({
                "from": self.address,
                "gas": 50000,
                "gasPrice": gas_price,
                "nonce": nonce,
            })
            
            signed_tx = self.web3.eth.account.sign_transaction(txn, self.private_key)
            tx_hash = self.web3.to_hex(
                await self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            )
            receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            Logger.success(f"Unwrapped {amount} WPHRS to PHRS - Hash: {tx_hash[:10]}...")
            return tx_hash, receipt.blockNumber
            
        except Exception as e:
            Logger.error(f"Unwrapping error: {str(e)}")
            return None, None
            
    async def perform_swap(self, count):
        total_balance = await self.get_balance()
        Logger.info(f"Current balance: {total_balance} PHRS")
        
        for i in range(count):
            amount = round(random.uniform(0.001, 0.005), 6)
            
            if amount > total_balance:
                Logger.warning(f"Insufficient balance for swap {i+1}, skipping")
                continue
                
            Logger.info(f"Performing swap {i+1}/{count}")
            
            Logger.info(f"Wrapping {amount} PHRS")
            wrap_tx, _ = await self.perform_wrapped(amount)
            if not wrap_tx:
                Logger.error(f"Failed to wrap for swap {i+1}")
                continue
                
            await asyncio.sleep(5)
            
            Logger.info(f"Unwrapping {amount} WPHRS")
            unwrap_tx, _ = await self.perform_unwrapped(amount)
            if not unwrap_tx:
                Logger.error(f"Failed to unwrap for swap {i+1}")
                continue
                
            Logger.success(f"Completed swap {i+1}/{count}")
            await asyncio.sleep(5)
            
    async def send_to_friend(self, count):
        for i in range(count):
            Logger.info(f"Performing transfer {i+1}/{count}")
            tx_hash = await self.transfer(i+1, self.address)
            
            if not tx_hash:
                Logger.error(f"Failed to transfer {i+1}")
                continue
                
            await asyncio.sleep(5)
            
            task_result = await self.verify_task(task_id=103, tx_hash=tx_hash)
            if task_result:
                Logger.success(f"Task verification successful for transfer {i+1}")
            else:
                Logger.error(f"Task verification failed for transfer {i+1}")
                
            await asyncio.sleep(5)
            
    async def close(self):
        if self.session:
            await self.session.close()

async def main():
    print("\n=== Pharos Network Script ===\n")
    
    # Ask for private key
    private_key = input("Enter your private key (or press Enter to exit): ").strip()
    
    if not private_key:
        Logger.warning("No private key provided. Exiting...")
        return
        
    # Initialize client
    client = PharosClient(private_key)
    await client.initialize_session()
    
    # Login
    if not await client.login():
        Logger.error("Failed to login. Exiting...")
        await client.close()
        return
    
    # Get initial points 877d2508ea8fdf0702e04c0fb25c1b2c2a67007ec0c2f77a794b24e0c3d54b53
    await client.get_points()
    
    while True:
        # Show menu
        print("\n=== Main Menu ===")
        print("1. Claim Faucet")
        print("2. Check In")
        print("3. Send to Friend Task")
        print("4. Swap")
        print("5. Quit")
        
        choice = input("\nSelect an option: ").lower().strip()
        
        if choice == "1":
            await client.claim_faucet()
        
        elif choice == "2":
            await client.check_in()
        
        elif choice == "3":
            try:
                count = int(input("How many transfers do you want to perform? "))
                if count > 0:
                    await client.send_to_friend(count)
                else:
                    Logger.warning("Invalid number. Must be greater than 0.")
            except ValueError:
                Logger.error("Please enter a valid number")
        
        elif choice == "4":
            try:
                count = int(input("How many swaps do you want to perform? "))
                if count > 0:
                    await client.perform_swap(count)
                else:
                    Logger.warning("Invalid number. Must be greater than 0.")
            except ValueError:
                Logger.error("Please enter a valid number")
        
        elif choice == "5":
            Logger.info("Exiting...")
            break
        
        else:
            Logger.warning("Invalid option. Please try again.")
    
    # Clean up
    await client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)
