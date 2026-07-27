# core/coa.py

STANDARD_COA = {
    # 1. Aset (Assets)
    1100: {"name": "Kas dan Setara Kas", "type": "Asset", "normal": "Debit"},
    1200: {"name": "Piutang Usaha", "type": "Asset", "normal": "Debit"},
    1300: {"name": "Persediaan", "type": "Asset", "normal": "Debit"},
    1500: {"name": "Aset Tetap", "type": "Asset", "normal": "Debit"},

    # 2. Liabilitas (Liabilities)
    2100: {"name": "Utang Usaha", "type": "Liability", "normal": "Kredit"},
    2200: {"name": "Utang Pajak", "type": "Liability", "normal": "Kredit"},
    2500: {"name": "Utang Bank Jangka Panjang", "type": "Liability", "normal": "Kredit"},

    # 3. Ekuitas (Equity)
    3100: {"name": "Modal Disetor", "type": "Equity", "normal": "Kredit"},
    3200: {"name": "Saldo Laba (Retained Earnings)", "type": "Equity", "normal": "Kredit"},

    # 4. Pendapatan (Revenue)
    4100: {"name": "Pendapatan Usaha", "type": "Revenue", "normal": "Kredit"},

    # 5. Beban (Expenses)
    5100: {"name": "Harga Pokok Penjualan (HPP)", "type": "Expense", "normal": "Debit"},
    6100: {"name": "Beban Operasional / Gaji", "type": "Expense", "normal": "Debit"}
}

def get_account_info(account_code):
    """Mengambil detail informasi akun berdasarkan kode."""
    return STANDARD_COA.get(account_code, None)