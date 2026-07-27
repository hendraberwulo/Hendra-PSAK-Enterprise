# main.py
import streamlit as st
import pandas as pd
import io
import os
import json
from datetime import datetime, timedelta
from core.coa import STANDARD_COA
from core.ledger import GeneralLedger
from core.validator import calculate_balance_sheet
from modules.stress_test import run_financial_stress_test
from ui.components import apply_custom_style, display_header
from database.handler import save_ledger_data, load_ledger_data

st.set_page_config(page_title="Hendra PSAK Enterprise", layout="wide")
apply_custom_style()

# --- SISTEM TRIAL 5 HARI ---
TRIAL_DAYS = 5
TRIAL_FILE = "trial_config.json"

def check_trial_status():
    today = datetime.now().date()
    if not os.path.exists(TRIAL_FILE):
        data = {"first_run": str(today)}
        try:
            with open(TRIAL_FILE, "w") as f:
                json.dump(data, f)
        except Exception:
            pass
        return True, TRIAL_DAYS
    else:
        try:
            with open(TRIAL_FILE, "r") as f:
                data = json.load(f)
            first_run = datetime.strptime(data["first_run"], "%Y-%m-%d").date()
            expiry_date = first_run + timedelta(days=TRIAL_DAYS)
            remaining = (expiry_date - today).days
            
            if today > expiry_date:
                return False, 0
            else:
                return True, max(0, remaining)
        except Exception:
            return True, TRIAL_DAYS

is_trial_active, remaining_days = check_trial_status()

# Jika Masa Trial Habis, Blokir Akses Aplikasi
if not is_trial_active:
    st.error("🚨 **Masa Uji Coba (Trial) 5 Hari Telah Berakhir!**")
    st.warning("Aplikasi Hendra PSAK Enterprise ini memerlukan lisensi aktif untuk dapat terus dioperasikan. Silakan hubungi administrator untuk memperpanjang lisensi Anda.")
    st.stop()
# ---------------------------

# Inisialisasi Sidebar & Branding
st.sidebar.markdown("### 🏛️ Hendra PSAK Enterprise")
st.sidebar.info(f"⏳ Status Lisensi: **Trial ({remaining_days} hari tersisa)**")
st.sidebar.markdown("---")

# Inisialisasi Ledger dengan memuat data tersimpan
if "ledger" not in st.session_state:
    st.session_state.ledger = GeneralLedger()
    saved_data = load_ledger_data()
    st.session_state.ledger.transactions = saved_data

# Fungsi penghitungan Laba Rugi
def calculate_income_statement(ledger_transactions):
    balances = {code: 0.0 for code in STANDARD_COA.keys()}
    for tx in ledger_transactions:
        for entry in tx["entries"]:
            code = entry["code"]
            debit = entry["debit"]
            credit = entry["credit"]
            normal_balance = STANDARD_COA[code]["normal"]
            if normal_balance == "Debit":
                balances[code] += (debit - credit)
            else:
                balances[code] += (credit - debit)
                
    revenues = {STANDARD_COA[code]["name"]: v for code, v in balances.items() if STANDARD_COA[code]["type"] == "Revenue" and v != 0}
    expenses = {STANDARD_COA[code]["name"]: v for code, v in balances.items() if STANDARD_COA[code]["type"] == "Expense" and v != 0}
    
    total_revenue = sum(revenues.values())
    total_expense = sum(expenses.values())
    net_income = total_revenue - total_expense
    
    return {
        "Daftar Pendapatan": revenues,
        "Total Pendapatan": total_revenue,
        "Daftar Beban": expenses,
        "Total Beban": total_expense,
        "Laba Bersih": net_income
    }

# Menu Sidebar
menu = st.sidebar.selectbox("Navigasi Modul", [
    "Input Jurnal", 
    "Daftar Jurnal Umum", 
    "Impor Jurnal Massal", 
    "Rekening Koran (RK)", 
    "Buku Besar & Neraca", 
    "Laporan Laba Rugi", 
    "Stress Test Keuangan"
])

if menu == "Input Jurnal":
    display_header("Pencatatan Jurnal Umum", "Standar Akuntansi Keuangan (PSAK) - Double-Entry Engine")
    
    col_date, col_faktur, col_desc = st.columns([1, 1, 2])
    with col_date:
        date = st.date_input("Tanggal Transaksi")
    with col_faktur:
        no_faktur = st.text_input("No. Faktur / Referensi", "INV/2026/001")
    with col_desc:
        desc = st.text_input("Keterangan Transaksi", "Contoh: Pendapatan Jasa Tunai dari Klien")
    
    st.write("")
    st.markdown("#### ⚖️ Alokasi Jurnal Berpasangan")
    
    coa_options = {f"{k} - {v['name']}": k for k, v in STANDARD_COA.items()}
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 📌 Posisi Debit")
        deb_choice = st.selectbox("Pilih Akun Debit", list(coa_options.keys()), key="d_acc")
        deb_code = coa_options[deb_choice]
        deb_val = st.number_input("Nominal Debit (Rp)", min_value=0.0, step=1000.0, format="%.2f", key="d_val")

    with col2:
        st.markdown("##### 📌 Posisi Kredit")
        cred_choice = st.selectbox("Pilih Akun Kredit", list(coa_options.keys()), key="c_acc")
        cred_code = coa_options[cred_choice]
        cred_val = st.number_input("Nominal Kredit (Rp)", min_value=0.0, step=1000.0, format="%.2f", key="c_val")

    st.write("---")
    if st.button("Simpan Transaksi ke Buku Besar"):
        if deb_val != cred_val:
            st.error("Gagal: Total Debit harus sama persis dengan Total Kredit!")
        else:
            try:
                entries = [
                    {"code": deb_code, "debit": deb_val, "credit": 0.0},
                    {"code": cred_code, "debit": 0.0, "credit": cred_val}
                ]
                st.session_state.ledger.record_journal(str(date), desc, entries)
                if st.session_state.ledger.transactions:
                    st.session_state.ledger.transactions[-1]["no_faktur"] = no_faktur
                
                save_ledger_data(st.session_state.ledger.get_all_transactions())
                st.success("Transaksi berfaktur berhasil divalidasi dan dicatat permanen ke Buku Besar!")
            except Exception as e:
                st.error(f"Gagal mencatat transaksi: {e}")

elif menu == "Daftar Jurnal Umum":
    display_header("Daftar Jurnal Umum (General Journal Register)", "Riwayat lengkap seluruh transaksi berpasangan beserta nomor faktur")
    
    transactions = st.session_state.ledger.get_all_transactions()
    
    if not transactions:
        st.info("Belum ada data transaksi jurnal yang tercatat.")
    else:
        flat_data = []
        for idx, tx in enumerate(transactions, 1):
            date_t = tx.get("date", "-")
            faktur_t = tx.get("no_faktur", "-")
            desc_t = tx.get("description", "-")
            for entry in tx.get("entries", []):
                code = entry.get("code")
                acc_name = STANDARD_COA.get(code, {}).get("name", "Unknown")
                flat_data.append({
                    "ID_Transaksi": f"TRX-{idx:03d}",
                    "Tanggal": date_t,
                    "No_Faktur": faktur_t,
                    "Keterangan": desc_t,
                    "Kode Akun": code,
                    "Nama Akun": acc_name,
                    "Debit": entry.get("debit", 0.0),
                    "Kredit": entry.get("credit", 0.0)
                })
        
        df_journal = pd.DataFrame(flat_data)
        st.dataframe(df_journal, use_container_width=True)
        
        st.write("---")
        
        col_del, col_ex1, col_ex2, col_ex3 = st.columns([2, 1, 1, 1])
        
        with col_del:
            st.markdown("##### 🗑️ Hapus Transaksi Spesifik")
            tx_options = {f"TRX-{i+1:03d} | {tx.get('date')} | {tx.get('description')}": i for i, tx in enumerate(transactions)}
            selected_tx_to_del = st.selectbox("Pilih Transaksi yang Akan Dihapus", list(tx_options.keys()), label_visibility="collapsed")
            if st.button("Hapus Transaksi Ini"):
                idx_del = tx_options[selected_tx_to_del]
                del st.session_state.ledger.transactions[idx_del]
                save_ledger_data(st.session_state.ledger.get_all_transactions())
                st.success("Transaksi berhasil dihapus!")
                st.rerun()
                
        with col_ex1:
            buffer_export = io.BytesIO()
            with pd.ExcelWriter(buffer_export, engine='openpyxl') as writer:
                df_journal.to_excel(writer, index=False, sheet_name='Jurnal Umum')
            st.download_button(
                label="📥 Unduh Excel",
                data=buffer_export.getvalue(),
                file_name="jurnal_umum_psak.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        with col_ex2:
            csv_data = df_journal.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Unduh CSV",
                data=csv_data,
                file_name="jurnal_umum_psak.csv",
                mime="text/csv"
            )
            
        with col_ex3:
            if st.button("🗑️ Bersihkan Semua"):
                st.session_state.ledger.transactions = []
                save_ledger_data([])
                st.rerun()

elif menu == "Impor Jurnal Massal":
    display_header("Impor Data Jurnal Massal", "Unggah file laporan transaksi (.xlsx atau .csv) lengkap dengan kolom No. Faktur")
    
    df_template_jurnal = pd.DataFrame(
        [["2026-07-27", "INV/2026/001", "Contoh Pendapatan Jasa Tunai", "1100", "4100", 5000000]],
        columns=["Tanggal", "No_Faktur", "Keterangan", "Akun_Debit", "Akun_Kredit", "Nominal"]
    )
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        buffer_jurnal = io.BytesIO()
        with pd.ExcelWriter(buffer_jurnal, engine='openpyxl') as writer:
            df_template_jurnal.to_excel(writer, index=False, sheet_name='Template Jurnal')
        st.download_button(
            label="📥 Template Excel (.xlsx)",
            data=buffer_jurnal.getvalue(),
            file_name="template_jurnal_psak.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col_t2:
        csv_template_jurnal = df_template_jurnal.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Template CSV (.csv)",
            data=csv_template_jurnal,
            file_name="template_jurnal_psak.csv",
            mime="text/csv"
        )
    
    st.write("---")
    uploaded_file = st.file_uploader("Pilih File Jurnal (Excel / CSV)", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, sep=None, engine='python') if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.dataframe(df, use_container_width=True)
            
            if st.button("Proses Impor Jurnal"):
                count = 0
                for _, row in df.iterrows():
                    date_val = str(row['Tanggal']).split(" ")[0]
                    faktur_val = str(row.get('No_Faktur', '-'))
                    desc_val = str(row['Keterangan'])
                    entries = [
                        {"code": str(row['Akun_Debit']).strip(), "debit": float(row['Nominal']), "credit": 0.0},
                        {"code": str(row['Akun_Kredit']).strip(), "debit": 0.0, "credit": float(row['Nominal'])}
                    ]
                    st.session_state.ledger.record_journal(date_val, desc_val, entries)
                    if st.session_state.ledger.transactions:
                        st.session_state.ledger.transactions[-1]["no_faktur"] = faktur_val
                    count += 1
                save_ledger_data(st.session_state.ledger.get_all_transactions())
                st.success(f"Berhasil mengimpor {count} transaksi jurnal!")
        except Exception as e:
            st.error(f"Terjadi kesalahan format: {e}")

elif menu == "Rekening Koran (RK)":
    display_header("Rekonsiliasi & Impor Rekening Koran (Bank Statement)", "Otomatisasi pencatatan mutasi bank masuk dan keluar")
    
    df_template_rk = pd.DataFrame(
        [["2026-07-27", "Contoh Transfer Masuk Klien", 2500000, "CR"],
         ["2026-07-27", "Contoh Biaya Administrasi Bank", 15000, "DB"]],
        columns=["Tanggal", "Uraian", "Mutasi", "DK"]
    )
    
    col_rk1, col_rk2 = st.columns(2)
    with col_rk1:
        buffer_rk = io.BytesIO()
        with pd.ExcelWriter(buffer_rk, engine='openpyxl') as writer:
            df_template_rk.to_excel(writer, index=False, sheet_name='Template Rekening Koran')
        st.download_button(
            label="📥 Template RK Excel (.xlsx)",
            data=buffer_rk.getvalue(),
            file_name="template_rekening_koran.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col_rk2:
        csv_template_rk = df_template_rk.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Template RK CSV (.csv)",
            data=csv_template_rk,
            file_name="template_rekening_koran.csv",
            mime="text/csv"
        )
    
    st.write("---")
    rk_file = st.file_uploader("Unggah File Rekening Koran (Excel / CSV)", type=["csv", "xlsx", "xls"], key="rk_uploader")
    
    if rk_file is not None:
        try:
            df_rk = pd.read_csv(rk_file, sep=None, engine='python') if rk_file.name.endswith('.csv') else pd.read_excel(rk_file)
            st.dataframe(df_rk, use_container_width=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                default_rev_acc = st.selectbox("Akun Default Pendapatan (jika CR)", [k + " - " + v["name"] for k, v in STANDARD_COA.items() if v["type"] == "Revenue"])
            with col_b:
                default_exp_acc = st.selectbox("Akun Default Beban (jika DB)", [k + " - " + v["name"] for k, v in STANDARD_COA.items() if v["type"] == "Expense"])
            
            if st.button("Proses Rekening Koran ke Buku Besar"):
                rev_code_target = default_rev_acc.split(" - ")[0]
                exp_code_target = default_exp_acc.split(" - ")[0]
                cash_code = "1100" 
                
                success_count = 0
                for _, row in df_rk.iterrows():
                    date_val = str(row['Tanggal']).split(" ")[0]
                    desc = str(row['Uraian'])
                    amount = float(row['Mutasi'])
                    dk_type = str(row['DK']).strip().upper()
                    
                    if dk_type == "CR":
                        entries = [
                            {"code": cash_code, "debit": amount, "credit": 0.0},
                            {"code": rev_code_target, "debit": 0.0, "credit": amount}
                        ]
                    else:
                        entries = [
                            {"code": exp_code_target, "debit": amount, "credit": 0.0},
                            {"code": cash_code, "debit": 0.0, "credit": amount}
                        ]
                    
                    st.session_state.ledger.record_journal(date_val, f"[RK] {desc}", entries)
                    if st.session_state.ledger.transactions:
                        st.session_state.ledger.transactions[-1]["no_faktur"] = f"BNK-{date_val.replace('-', '')}"
                    success_count += 1
                
                save_ledger_data(st.session_state.ledger.get_all_transactions())
                st.success(f"Berhasil merekonsiliasi {success_count} mutasi Rekening Koran!")
        except Exception as e:
            st.error(f"Gagal memproses file Rekening Koran: {e}")

elif menu == "Buku Besar & Neraca":
    display_header("Buku Besar & Validasi Neraca", "Pemeriksaan Real-Time Persamaan Dasar Akuntansi (Aset = Liabilitas + Ekuitas)")
    transactions = st.session_state.ledger.get_all_transactions()
    
    if not transactions:
        st.info("Belum ada data transaksi tercatat dalam sistem.")
    else:
        balance_data = calculate_balance_sheet(transactions)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Aset", f"Rp {balance_data['Total Aset']:,.0f}")
        m2.metric("Total Liabilitas", f"Rp {balance_data['Total Liabilitas']:,.0f}")
        m3.metric("Total Ekuitas", f"Rp {balance_data['Total Ekuitas']:,.0f}")
        m4.metric("Status Keseimbangan", "Seimbang (Balanced)" if balance_data["Status Seimbang"] else "Tidak Seimbang")
        
        st.write("---")
        st.subheader("📋 Ringkasan Posisi Neraca Akuntansi")
        st.write(balance_data)

elif menu == "Laporan Laba Rugi":
    display_header("Laporan Laba Rugi Komprehensif", "Ringkasan Kinerja Operasional Perusahaan")
    transactions = st.session_state.ledger.get_all_transactions()
    if not transactions:
        st.info("Belum ada data transaksi operasional.")
    else:
        income_data = calculate_income_statement(transactions)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Pendapatan", f"Rp {income_data['Total Pendapatan']:,.0f}")
        c2.metric("Total Beban", f"Rp {income_data['Total Beban']:,.0f}")
        c3.metric("Laba Bersih", f"Rp {income_data['Laba Bersih']:,.0f}")
        
        st.write("---")
        st.subheader("Detail Komponen Laba Rugi")
        st.json(income_data)
        
        df_lr = pd.DataFrame([
            {"Kategori": "Total Pendapatan", "Jumlah (Rp)": income_data['Total Pendapatan']},
            {"Kategori": "Total Beban", "Jumlah (Rp)": income_data['Total Beban']},
            {"Kategori": "Laba Bersih", "Jumlah (Rp)": income_data['Laba Bersih']}
        ])
        
        col_el1, col_el2 = st.columns(2)
        with col_el1:
            buffer_lr = io.BytesIO()
            with pd.ExcelWriter(buffer_lr, engine='openpyxl') as writer:
                df_lr.to_excel(writer, index=False, sheet_name='Laba Rugi')
            st.download_button(
                label="📥 Unduh Laba Rugi Excel (.xlsx)",
                data=buffer_lr.getvalue(),
                file_name="laporan_laba_rugi.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col_el2:
            csv_lr = df_lr.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Unduh Laba Rugi CSV (.csv)",
                data=csv_lr,
                file_name="laporan_laba_rugi.csv",
                mime="text/csv"
            )

elif menu == "Stress Test Keuangan":
    display_header("Modul Uji Ketahanan Keuangan (Stress Test)", "Simulasi Manajemen Risiko & Ketahanan Likuiditas Korporasi")
    transactions = st.session_state.ledger.get_all_transactions()
    balance_data = calculate_balance_sheet(transactions)
    
    st.markdown("##### Atur Parameter Simulasi Tekanan Pasar:")
    c1, c2, c3 = st.columns(3)
    with c1:
        rev_drop = st.slider("Penurunan Omzet (%)", 0, 100, 20) / 100.0
    with c2:
        cost_spike = st.slider("Lonjakan Biaya (%)", 0, 100, 15) / 100.0
    with c3:
        bad_debt = st.slider("Piutang Macet (%)", 0, 100, 10) / 100.0
    
    st.write("")
    if st.button("Jalankan Simulasi Stress Test"):
        params = {
            "revenue_drop_pct": rev_drop,
            "cost_spike_pct": cost_spike,
            "bad_debt_pct": bad_debt
        }
        result = run_financial_stress_test(balance_data, params)
        
        st.write("---")
        st.subheader("Hasil Analisis Risiko & Rekomendasi Strategis")
        
        r1, r2 = st.columns(2)
        r1.metric("Simulasi Laba Bersih Baru", f"Rp {result['Simulasi Laba Bersih Baru']:,.0f}")
        r2.metric("Status Kesehatan", result["Status Kesehatan"])
        
        st.info(f"**Rekomendasi Strategis AI:** {result['Rekomendasi Strategis']}")