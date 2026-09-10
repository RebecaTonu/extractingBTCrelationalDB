# Extracting Bitcoin Transactions to Relational Databases for Analysis in IoT

This repository provides the code, datasets, and supporting resources associated with the paper **“Extracting Bitcoin Transactions to Relational Databases for Analysis in IoT,”** by **Rebeca Tonu, Otilia Muntean, and Ciprian Pungilă**. It includes a reproducible pipeline for retrieving blockchain data from a Bitcoin Core node, storing the extracted information in CSV datasets, importing it into a relational database, and evaluating SQL query execution times.

---

## Repository Structure

The repository contains the following main components:

* **`Retrieve.py`** – extracts Bitcoin blockchain data from a Bitcoin Core node.
* **`Dataset/`** – contains a subset of the extracted Bitcoin transaction data and the IoT device data used in the experiments.
* **`DB schema`** – defines the relational database structure and indexes.
* **`Insert.sql`** – imports the extracted data into the relational database.
* **`Test SQL query time`** – executes representative IoT-oriented SQL queries and measures their execution time.

---

## Requirements

* Python 3.8+
* Bitcoin Core node
* Fully synchronized Bitcoin blockchain
* Bitcoin Core RPC enabled
* MySQL database

### Install Dependencies

```bash id="fzm00r"
pip install python-bitcoinrpc
```

---

## Dataset Extraction

The `Retrieve.py` script connects directly to a Bitcoin Core node through JSON-RPC and extracts blockchain information over a configurable block range.

The extracted data includes information about:

### Blocks

* `block_id`
* `block_hash`
* `previous_block_hash`
* `timestamp`
* `miner_wallet_id`

### Transactions

* `transaction_id`
* `tx_hash`

### Inputs

* `input_id`
* `input_wallet_id`
* `input_amount`

### Outputs

* `output_id`
* `output_wallet_id`
* `output_amount`

### Wallets

* `wallet_address`
* `balance`

---

## Bitcoin Core Configuration

Configure Bitcoin Core by editing the `bitcoin.conf` file:

```ini id="2jq54z"
server=1
txindex=1
rpcuser=your_user
rpcpassword=your_password
rpcallowip=127.0.0.1
rpcport=8332
```

The node should be fully synchronized before running the extraction.

---

## Configure the Extraction Script

In `Retrieve.py`, replace the RPC credentials and output path with your local configuration:

```python id="1tb8xv"
RPC_USER = "xxxx"
RPC_PASSWORD = "xxxx"

RPC_HOST = "127.0.0.1"
RPC_PORT = 8332

OUTPUT_FOLDER = r"xxxx"
```

---

## Run the Extraction

Run:

```bash id="eb7kcb"
python Retrieve.py
```

The script retrieves blocks, transactions, inputs, outputs, and wallet information from the Bitcoin blockchain and exports the resulting records as CSV files.

---

## Dataset

The **`Dataset`** folder contains a subset of the extracted Bitcoin data used for the experiments.

It also contains **`Iot_devices.csv`**, which provides the IoT device information used by the database queries and includes the following attributes:

* `device_id`
* `device_name`
* `device_type`
* `wallet_id`


---

## Relational Database

The **`DB schema`** file defines the relational representation used to store the extracted blockchain data.

The database contains the following main tables:

* `Wallets`
* `Blocks`
* `Transactions`
* `Inputs`
* `Outputs`
* `IoT_Devices`

---

## Database Views

The schema also defines SQL views for representative IoT-oriented blockchain analysis scenarios, including:

* total spending associated with IoT devices;
* identification of the most frequently used IoT devices;
* detection of large transactions associated with toll-road devices.

---

## Importing the Dataset

The `Insert.sql` script can be used to insert the extracted CSV data into the relational database.

Before running the script, configure the appropriate dataset paths and database settings for your local environment.

---

## SQL Query Performance

The **`Test SQL query time`** script evaluates the execution time of representative queries over the relational database.

Configure your MySQL connection:

```python id="0dkb55"
DB_CONFIG = {
    'host': 'your_host',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'your_database',
}
```

Then run the script.

The experiments evaluate queries corresponding to scenarios such as:

1. Calculating the total amount spent by an IoT device during the previous seven days.
2. Identifying the most frequently used IoT devices during the previous day.
3. Retrieving large transactions associated with toll-road IoT devices.

For each scenario, the execution time is measured and reported in seconds.

---
