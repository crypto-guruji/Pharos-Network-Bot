# Pharos Network Automation Tool

A Python-based automation tool for interacting with the Pharos Network testnet. This script allows users to perform various tasks including daily check-ins, faucet claims, transfers, and token swaps.

## Features

- **Authentication**: Secure login using Ethereum wallet signatures
- **Daily Check-in**: Perform daily check-ins to earn points
- **Faucet Claiming**: Claim testnet tokens from the faucet when available
- **Token Transfers**: Send PHRS tokens to yourself or others
- **Swap Operations**: Wrap/unwrap between PHRS and WPHRS tokens
- **Task Verification**: Verify completed tasks with the Pharos Network API
- **Balance Checking**: Check your PHRS and WPHRS balances
- **Interactive CLI**: Easy-to-use command-line interface

## Requirements

- Python 3.7+
- Required packages:
  - `web3`
  - `aiohttp`
  - `eth-account`
  - `asyncio`

## Installation

1. Clone this repository or download the script
2. Install the required packages:

```bash
pip install web3 aiohttp eth_account asyncio
```

## Usage

Run the script with:

```bash
python pharos_network.py
```

You will be prompted to enter your Ethereum private key. The script will then connect to the Pharos Network testnet and display a menu of available actions.

### Menu Options

- **1. Claim Faucet**: Claim daily testnet tokens (if available)
- **2. Check In**: Perform daily check-in to earn points
- **3. Send to Friend Task**: Execute transfers to complete the "Send to Friend" task
- **4. Swap**: Perform swap operations (wrap/unwrap) between PHRS and WPHRS tokens
- **5. Quit**: Exit the program

## Security Notice

This script requires your Ethereum private key to sign transactions. Please ensure:

1. You are only using testnet private keys
2. You never share your private key with others
3. The script is run in a secure environment
4. You review the code before running it

⚠️ **IMPORTANT**: Never use a private key that controls real assets on mainnet!

## Technical Details

- The script uses the Web3.py library to interact with the Pharos Network blockchain
- API interactions are handled using aiohttp for asynchronous requests
- All operations are performed using the EIP-1559 gas mechanism when available
- The script includes detailed logging with color-coded messages

## Constants

- RPC URL: `https://testnet.dplabs-internal.com`
- Chain ID: `688688`
- WPHRS Contract: `0x76aaada469d23216be5f7c596fa25f282ff9b364`
- API Base URL: `https://api.pharosnetwork.xyz`

## Troubleshooting

If you encounter any issues:

1. Ensure you have a sufficient PHRS balance for transactions
2. Check your internet connection
3. Verify that the Pharos Network testnet is operational
4. Ensure you're using the correct and latest version of the script

## License

This script is provided for educational and testing purposes only.

## Disclaimer

This is an unofficial tool. Use at your own risk. The developers are not responsible for any loss or damage caused by the use of this script.
