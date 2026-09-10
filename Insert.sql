CREATE DATABASE IF NOT EXISTS BitcoinDB;
USE BitcoinDB;

CREATE TABLE Wallets (
    wallet_id INT AUTO_INCREMENT PRIMARY KEY,
    address VARCHAR(255) UNIQUE NOT NULL,
    balance DECIMAL(18,8) NOT NULL DEFAULT 0
);

CREATE INDEX idx_wallet_address
ON Wallets(address);


CREATE TABLE Blocks (
    block_id INT AUTO_INCREMENT PRIMARY KEY,
    block_hash VARCHAR(255) UNIQUE NOT NULL,
    previous_block_hash VARCHAR(255),
    timestamp DATETIME NOT NULL,
    miner_wallet_id INT,
    FOREIGN KEY (miner_wallet_id)
        REFERENCES Wallets(wallet_id)
);

CREATE INDEX idx_block_hash
ON Blocks(block_hash);

CREATE INDEX idx_block_timestamp
ON Blocks(timestamp);

CREATE INDEX idx_block_miner
ON Blocks(miner_wallet_id, timestamp);


CREATE TABLE Transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    tx_hash VARCHAR(255) UNIQUE NOT NULL,
    block_id INT,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (block_id)
        REFERENCES Blocks(block_id)
);

CREATE INDEX idx_transaction_tx_hash
ON Transactions(tx_hash);

CREATE INDEX idx_transaction_timestamp
ON Transactions(timestamp);

CREATE INDEX idx_transaction_block
ON Transactions(block_id, timestamp);


CREATE TABLE Inputs (
    input_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT,
    wallet_id INT,
    amount DECIMAL(18,8) NOT NULL,
    FOREIGN KEY (transaction_id)
        REFERENCES Transactions(transaction_id),
    FOREIGN KEY (wallet_id)
        REFERENCES Wallets(wallet_id)
);

CREATE INDEX idx_input_transaction_id
ON Inputs(transaction_id);

CREATE INDEX idx_input_wallet_id
ON Inputs(wallet_id);

CREATE INDEX idx_input_wallet_transaction
ON Inputs(wallet_id, transaction_id);


CREATE TABLE Outputs (
    output_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT,
    wallet_id INT,
    amount DECIMAL(18,8) NOT NULL,
    FOREIGN KEY (transaction_id)
        REFERENCES Transactions(transaction_id),
    FOREIGN KEY (wallet_id)
        REFERENCES Wallets(wallet_id)
);

CREATE INDEX idx_output_transaction_id
ON Outputs(transaction_id);

CREATE INDEX idx_output_wallet_id
ON Outputs(wallet_id);

CREATE INDEX idx_output_wallet_transaction
ON Outputs(wallet_id, transaction_id);


CREATE TABLE IoT_Devices (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    device_name VARCHAR(255) NOT NULL,
    wallet_id INT,
    location VARCHAR(255),
    FOREIGN KEY (wallet_id)
        REFERENCES Wallets(wallet_id)
);

CREATE INDEX idx_iot_wallet_id
ON IoT_devices(wallet_id);