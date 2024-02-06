import logging
import random
import time

from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.types import TxParams


def construct_transaction(
        account: LocalAccount,
        w3: Web3,
        from_address: str,
        to_address: str,
        value: int,
        data: str
):
    chain_id = w3.eth.chain_id
    nonce = w3.eth.get_transaction_count(account.address)
    transaction_body = {
        "from": account.address,
        "to": w3.to_checksum_address(to_address),
        "chainId": chain_id,
        "value": value,
        "gasPrice": w3.eth.gas_price * 2,
        "gas": 1,
        "nonce": nonce,
        "data": data
    }

    transaction = estimate_gas_limit(transaction_body, w3)

    signed_transaction = account.sign_transaction(transaction)

    try:
        result = w3.eth.send_raw_transaction(
            signed_transaction.rawTransaction
        )
        tx_hex = result.hex()
    except Exception as e:
        print('Error ', e)
        input()
        return construct_transaction(account, w3, from_address, to_address, value, data)

    if wait_transaction_final(
        tx_hex,
        w3=w3,
        from_address=from_address
    ):
        return tx_hex
    else:
        return False


def wait_transaction_final(tx_hex, w3, from_address):
    tx_uploaded = False
    retries = 0
    while not tx_uploaded and retries < 5:
        time.sleep(2)
        try:
            w3.eth.get_transaction_receipt(
                tx_hex
            )
            tx_uploaded = True
        except Exception as e:
            retries += 1
            tx_uploaded = False
    time.sleep(5)
    if tx_uploaded:
        return True
    else:
        logging.warning(
            "Transaction could not be uploaded for address {}".format(from_address)
        )
        return False


def estimate_gas_limit(transaction, w3: Web3):
    estimate_gas = w3.eth.estimate_gas(
        transaction=transaction
    )
    transaction["gas"] = estimate_gas + 15000
    return transaction

