# modules/stress_test.py

def run_financial_stress_test(balance_sheet_data, stress_params):
    """
    Melakukan simulasi stress test keuangan berdasarkan parameter tekanan:
    - revenue_drop_pct: Persentase penurunan omzet (contoh: 0.30 untuk 30%)
    - cost_spike_pct: Persentase lonjakan biaya operasional (contoh: 0.20 untuk 20%)
    - bad_debt_pct: Persentase piutang tertagih yang macet (contoh: 0.15 untuk 15%)
    """
    total_asset = balance_sheet_data["Total Aset"]
    total_liability = balance_sheet_data["Total Liabilitas"]
    net_income = balance_sheet_data["Laba Bersih"]

    rev_drop = stress_params.get("revenue_drop_pct", 0.0)
    cost_spike = stress_params.get("cost_spike_pct", 0.0)
    bad_debt = stress_params.get("bad_debt_pct", 0.0)

    estimated_revenue_loss = net_income * rev_drop
    estimated_cost_increase = net_income * cost_spike
    estimated_bad_debt_loss = total_asset * bad_debt

    simulated_net_income = net_income - estimated_revenue_loss - estimated_cost_increase - estimated_bad_debt_loss

    simulated_asset = total_asset - estimated_bad_debt_loss
    if simulated_asset <= 0:
        debt_ratio = 999.0
    else:
        debt_ratio = total_liability / simulated_asset

    if simulated_net_income < 0 or debt_ratio > 0.8:
        status = "🔴 BAHAYA / DEFAULT RISK (Risiko Gagal Bayar Tinggi)"
        advice = "Arus kas terancam kolaps. Perlu restrukturisasi utang dan efisiensi biaya segera."
    elif simulated_net_income < (net_income * 0.5) or debt_ratio > 0.5:
        status = "🟡 WASPADA (Ketahanan Tipis)"
        advice = "Kinerja keuangan melambat. Perketat penagihan piutang dan pantau pengeluaran."
    else:
        status = "🟢 AMAN (Finansial Tangguh)"
        advice = "Perusahaan masih memiliki buffer kas yang cukup kuat menghadapi tekanan skenario ini."

    return {
        "Skenario Tekanan": stress_params,
        "Simulasi Laba Bersih Baru": simulated_net_income,
        "Rasio Utang Terhadap Aset": debt_ratio,
        "Status Kesehatan": status,
        "Rekomendasi Strategis": advice
    }