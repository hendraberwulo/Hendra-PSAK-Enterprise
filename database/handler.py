# database/handler.py
import json
import os

DB_FILE = "database/ledger_storage.json"

def save_ledger_data(transactions):
    """Menyimpan data transaksi ke file lokal"""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w") as f:
        json.dump(transactions, f, indent=4)

def load_ledger_data():
    """Memuat data transaksi dari file lokal jika ada"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []