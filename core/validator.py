# core/validator.py

from core.coa import STANDARD_COA

def calculate_balance_sheet(ledger_transactions):
    """
    Menghitung saldo akhir tiap akun dan memvalidasi persamaan dasar akuntansi:
    Aset = Liabilitas + Ekuitas + Laba Bersih (Pendapatan - Beban)
    """
    # Inisialisasi saldo awal 0 untuk setiap kode akun di COA
    balances = {code: 0.0 for code in STANDARD_COA.keys()}

    for tx in ledger_transactions:
        for entry in tx["entries"]:
            code = entry["code"]
            debit = entry["debit"]
            credit = entry["credit"]
            
            normal_balance = STANDARD_COA[code]["normal"]
            
            # Menghitung berdasarkan posisi saldo normal akuntansi
            if normal_balance == "Debit":
                balances[code] += (debit - credit)
            else:
                balances[code] += (credit - debit)

    # Akumulasi per kategori laporan keuangan
    total_asset = sum(v for code, v in balances.items() if STANDARD_COA[code]["type"] == "Asset")
    total_liability = sum(v for code, v in balances.items() if STANDARD_COA[code]["type"] == "Liability")
    total_equity = sum(v for code, v in balances.items() if STANDARD_COA[code]["type"] == "Equity")
    total_revenue = sum(v for code, v in balances.items() if STANDARD_COA[code]["type"] == "Revenue")
    total_expense = sum(v for code, v in balances.items() if STANDARD_COA[code]["type"] == "Expense")

    # Laba Bersih = Pendapatan - Beban
    net_income = total_revenue - total_expense
    
    # Total Pasiva (Liabilitas + Ekuitas + Laba Berjalan)
    total_liability_equity = total_liability + total_equity + net_income
    
    # Validasi keseimbangan (dengan toleransi kecil untuk pembulatan float)
    is_balanced = abs(total_asset - total_liability_equity) < 0.01

    return {
        "Total Aset": total_asset,
        "Total Liabilitas": total_liability,
        "Total Ekuitas": total_equity,
        "Laba Bersih": net_income,
        "Total Liabilitas & Ekuitas": total_liability_equity,
        "Status Seimbang": is_balanced
    }