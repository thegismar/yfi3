from brownie import *
import requests
from tqdm import tqdm
import pandas as pd
import os
import time

URL = "https://api.etherscan.io/api?"
KEY = os.getenv("ETHERSCAN_TOKEN")


def get_transactions_by_account(account):
    """
    queries etherscan and gets all the transactions that involve a certain acount
    :param account:
    :return:
    """
    r = None

    url = (
            URL + f"module=account&action=txlist&address={account}&startblock=0&"
                  f"endblock=99999999&sort=asc&apikey={KEY}"
    )
    while True:
        try:
            r = requests.get(url).json()
        except requests.exceptions.Timeout:
            time.sleep(5)
            continue
        except requests.exceptions.TooManyRedirects as e:
            print(f"URL cannot be reached. {e}")
            break
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        else:
            break

    users = []
    if r["status"] != "1":
        return 1
    else:
        for u in r['result']:
            users.append(u['from'])

    return users


def main():
    block = 11445892
    yr = Contract.from_explorer('0x10C4B173755cF42B0A313e042E83e30Cc2F0B948')

    # getting ALL accounts that ever interacted with the contract
    users = get_transactions_by_account(yr.address)
    df = pd.DataFrame(users, columns=['accounts'])

    # drop duplicate accounts
    df.drop_duplicates(inplace=True, keep='first')

    table = []
    for u in tqdm(desc='Creating snapshot...', iterable=df.accounts):
        table.append({'account': u, 'ycrv_balance': yr.balanceOf(u, block_identifier=block),
                      'rewards': yr.earned(u, block_identifier=block)})

    snapshot = pd.DataFrame(table)
    snapshot.to_csv('../snapshot.csv')

    # test
    print(f'\nTest of balances of each account against the total as exposed by the smart contract..')
    df = pd.read_csv('../snapshot.csv')

    bal = 0
    for b in df.ycrv_balance:
        bal += int(b)

    totalSupply = yr.totalSupply(block_identifier=block)
    print(f'Sum of individual balances: {bal}, totalSupply: {totalSupply}')
    assert bal == totalSupply
