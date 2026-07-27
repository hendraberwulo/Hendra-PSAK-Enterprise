# core/ledger.py

from core.coa import get_account_info

class GeneralLedger:
    def __init__(self):
        # Menyimpan daftar transaksi jurnal umum
        self.transactions = []

    def record_journal(self, date, description, entries):
        """
        Mencatat jurnal umum dengan banyak baris (multi-line entries).
        entries: list of dict, contoh:
        [
            {"code": 1100, "debit": 5000000, "credit": 0},
            {"code": 4100, "debit": 0, "credit": 5000000}
        ]
        """
        total_debit = sum(item["debit"] for item in entries)
        total_credit = sum(item["credit"] for item in entries)

        # Validasi mutlak: Total Debit harus sama dengan Total Kredit
        if total_debit != total_credit:
            raise ValueError(
                f"Jurnal tidak seimbang! Total Debit (Rp {total_debit:,.2f}) "
                f"tidak sama dengan Total Kredit (Rp {total_credit:,.2f})."
            )

        # Validasi eksistensi kode akun PSAK
        for item in entries:
            account_info = get_account_info(item["code"])
            if not account_info:
                raise ValueError(f"Kode akun {item['code']} tidak terdaftar dalam COA PSAK.")

        # Jika valid, masukkan ke buku besar
        transaction_record = {
            "date": date,
            "description": description,
            "entries": entries,
            "total": total_debit
        }
        self.transactions.append(transaction_record)
        return True

    def get_all_transactions(self):
        """Mengambil seluruh riwayat transaksi buku besar."""
        return self.transactions