import csv
import os
import requests
from decimal import Decimal

RPC_USER = "xxxx" #replace with the username set in btc config file
RPC_PASSWORD = "xxxx" #replace with the password set in btc config file
RPC_HOST = "127.0.0.1"
RPC_PORT = 8332
RPC_URL = f"http://{RPC_HOST}:{RPC_PORT}" 

START_BLOCK = 402000
END_BLOCK = 500010

OUTPUT_FOLDER = r"xxxx" #replace with your actual blk.dat file path
TOTAL_ROWS = 500_000
ROWS_PER_FILE = 50_000

COLUMNS = [
    "block_id",
    "block_hash",
    "previous_block_hash",
    "timestamp",
    "miner_wallet_id",
    "transaction_id",
    "tx_hash",
    "input_id",
    "input_wallet_id",
    "input_amount",
    "output_id",
    "output_wallet_id",
    "output_amount",
    "wallet_address",
    "balance"
]

wallet_ids = {}
wallet_balances = {}
transaction_cache = {}

next_wallet_id = 1
next_transaction_id = 1
next_input_id = 1
next_output_id = 1
rpc_counter = 0


def rpc_call(method, params=None):
    global rpc_counter

    rpc_counter += 1

    payload = {
        "jsonrpc": "2.0",
        "id": rpc_counter,
        "method": method,
        "params": params or []
    }

    response = requests.post(
        RPC_URL,
        json=payload,
        auth=(RPC_USER, RPC_PASSWORD),
        timeout=120
    )

    response.raise_for_status()
    data = response.json()

    if data.get("error") is not None:
        raise RuntimeError(f"{method}: {data['error']}")

    return data["result"]


def get_wallet_id(address):
    global next_wallet_id

    if not address:
        return None

    if address not in wallet_ids:
        wallet_ids[address] = next_wallet_id
        next_wallet_id += 1

    return wallet_ids[address]


def get_address(vout):
    script = vout.get("scriptPubKey", {})

    address = script.get("address")
    if address:
        return address

    addresses = script.get("addresses", [])
    return addresses[0] if addresses else None


def get_previous_transaction(txid):
    if txid not in transaction_cache:
        transaction_cache[txid] = rpc_call(
            "getrawtransaction",
            [txid, True]
        )

    return transaction_cache[txid]


def get_input_information(vin):
    if "coinbase" in vin:
        return None, None

    previous_txid = vin.get("txid")
    previous_vout_index = vin.get("vout")

    if previous_txid is None or previous_vout_index is None:
        return None, None

    try:
        previous_tx = get_previous_transaction(previous_txid)
        previous_outputs = previous_tx.get("vout", [])

        if previous_vout_index >= len(previous_outputs):
            return None, None

        previous_output = previous_outputs[previous_vout_index]
        address = get_address(previous_output)
        value = Decimal(str(previous_output.get("value", 0)))

        return address, value

    except Exception as e:
        print(
            f"\nCould not resolve input "
            f"{previous_txid}:{previous_vout_index}: {e}"
        )
        return None, None


def add_balance(address, amount):
    wallet_balances[address] = (
        wallet_balances.get(address, Decimal("0")) + amount
    )


def subtract_balance(address, amount):
    wallet_balances[address] = (
        wallet_balances.get(address, Decimal("0")) - amount
    )


def get_balance(address):
    return wallet_balances.get(address, Decimal("0"))


def open_csv_file(file_number):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    filename = os.path.join(
        OUTPUT_FOLDER,
        f"bitcoin_data_part_{file_number}.csv"
    )

    csv_file = open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    )

    writer = csv.DictWriter(csv_file, fieldnames=COLUMNS)
    writer.writeheader()

    print(f"\nOpened file {file_number}/4: {filename}")

    return csv_file, writer


def extract():
    global next_transaction_id
    global next_input_id
    global next_output_id

    total_rows = 0
    rows_in_current_file = 0
    file_number = 1
    stop = False

    csv_file, writer = open_csv_file(file_number)

    def write_row(row):
        nonlocal total_rows
        nonlocal rows_in_current_file
        nonlocal file_number
        nonlocal csv_file
        nonlocal writer
        nonlocal stop

        writer.writerow(row)

        total_rows += 1
        rows_in_current_file += 1

        if total_rows % 1000 == 0:
            print(f"Rows: {total_rows:,}/{TOTAL_ROWS:,}")

        if total_rows >= TOTAL_ROWS:
            stop = True
            return

        if rows_in_current_file >= ROWS_PER_FILE:
            csv_file.close()

            print(
                f"Part {file_number} complete: "
                f"{ROWS_PER_FILE:,} rows"
            )

            file_number += 1
            rows_in_current_file = 0
            csv_file, writer = open_csv_file(file_number)

    for block_height in range(START_BLOCK, END_BLOCK + 1):
        if stop:
            break

        print(f"\nBlock {block_height:,}")

        try:
            block_hash = rpc_call("getblockhash", [block_height])
            block = rpc_call("getblock", [block_hash, 2])
        except Exception as e:
            print(f"Could not retrieve block {block_height}: {e}")
            continue

        block_id = block_height
        previous_block_hash = block.get("previousblockhash")
        timestamp = block.get("time")
        transactions = block.get("tx", [])

        print(f"Transactions: {len(transactions):,}")

        miner_wallet_id = None

        if transactions:
            coinbase_tx = transactions[0]

            for output in coinbase_tx.get("vout", []):
                miner_address = get_address(output)

                if miner_address:
                    miner_wallet_id = get_wallet_id(miner_address)
                    break

        for tx_position, tx in enumerate(transactions, start=1):
            if stop:
                break

            tx_hash = tx.get("txid")
            transaction_id = next_transaction_id
            next_transaction_id += 1

            print(
                f"\rTX {tx_position:,}/{len(transactions):,} | "
                f"Rows {total_rows:,}/{TOTAL_ROWS:,}",
                end="",
                flush=True
            )

            if tx_hash:
                transaction_cache[tx_hash] = tx

            for vin in tx.get("vin", []):
                if stop:
                    break

                if "coinbase" in vin:
                    continue

                address, amount = get_input_information(vin)

                if not address:
                    continue

                wallet_id = get_wallet_id(address)

                subtract_balance(address, amount)
                balance = get_balance(address)

                row = {
                    "block_id": block_id,
                    "block_hash": block_hash,
                    "previous_block_hash": previous_block_hash,
                    "timestamp": timestamp,
                    "miner_wallet_id": miner_wallet_id,
                    "transaction_id": transaction_id,
                    "tx_hash": tx_hash,
                    "input_id": next_input_id,
                    "input_wallet_id": wallet_id,
                    "input_amount": f"{amount:.8f}",
                    "output_id": "",
                    "output_wallet_id": "",
                    "output_amount": "",
                    "wallet_address": address,
                    "balance": f"{balance:.8f}"
                }

                write_row(row)
                next_input_id += 1

            for vout in tx.get("vout", []):
                if stop:
                    break

                address = get_address(vout)

                if not address:
                    continue

                amount = Decimal(str(vout.get("value", 0)))
                wallet_id = get_wallet_id(address)

                add_balance(address, amount)
                balance = get_balance(address)

                row = {
                    "block_id": block_id,
                    "block_hash": block_hash,
                    "previous_block_hash": previous_block_hash,
                    "timestamp": timestamp,
                    "miner_wallet_id": miner_wallet_id,
                    "transaction_id": transaction_id,
                    "tx_hash": tx_hash,
                    "input_id": "",
                    "input_wallet_id": "",
                    "input_amount": "",
                    "output_id": next_output_id,
                    "output_wallet_id": wallet_id,
                    "output_amount": f"{amount:.8f}",
                    "wallet_address": address,
                    "balance": f"{balance:.8f}"
                }

                write_row(row)
                next_output_id += 1

        print(
            f"\nBlock {block_height:,} complete | "
            f"Rows: {total_rows:,}/{TOTAL_ROWS:,}"
        )

    if not csv_file.closed:
        csv_file.close()

    print(f"\nExtraction complete: {total_rows:,} rows")


if __name__ == "__main__":
    extract()