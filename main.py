from config import blast_rpc, mint_data
from web3 import Web3, HTTPProvider, Account
from web3.middleware import geth_poa_middleware
import random
import asyncio

from utils import construct_transaction

with open("privates.txt", "r") as file:
    privates = [line.strip() for line in file.readlines()]

with open("proxies.txt", "r") as file:
    proxies = [line.split() for line in file.readlines()]


def mint(private):
    if proxies:
        proxy = random.choice(proxies)
        rk = {"proxies": {'https': proxy, 'http': proxy}}
    else:
        rk = None
    w3 = Web3(
        HTTPProvider(
            blast_rpc, request_kwargs=rk
        )
    )
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    account = Account.from_key(private)
    try:
        construct_transaction(
            account,
            w3,
            from_address=account.address,
            to_address=w3.to_checksum_address("0x68dc8D3ab93220e84b9923706B3DDc926C77f1Df"),
            value=0,
            data=mint_data
        )
        print("+1", account.address)
    except:
        return


async def main():
    count = len(privates)
    done = 0
    while True:
        tasks = []
        for i in range(5):
            task = asyncio.create_task(mint(privates[done]))
            done += 1
            tasks.append(task)
        await asyncio.gather(*tasks)
        if done >= count:
            break


if __name__ == '__main__':
    asyncio.run(main())

