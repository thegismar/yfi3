# yfi3

To generate the snapshot data:

pip install -r requirements.txt

brownie networks add Ethereum main host=$YOUR_WEB3_PROVIDER chainid=1 explorer=https://api.etherscan.io/api

set environment variable for etherscan KEY or change it in the code.

then:

brownie run scripts/main.py --network main
