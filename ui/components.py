# ui/components.py
import streamlit as st

def apply_custom_style():
    """Mengatur tema dan styling CSS kustom ala Enterprise ERP Kelas Mahal"""
    st.markdown("""
        <style>
        /* Global & Background */
        .main {
            background-color: #f4f6f9;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Sidebar Styling (Deep Navy Corporate) */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            color: #ffffff;
            border-right: 1px solid #1e293b;
        }
        [data-testid="stSidebar"] .stSelectbox label, 
        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] span {
            color: #cbd5e1 !important;
            font-weight: 500;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #f8fafc !important;
        }

        /* Executive Header Banner */
        .erp-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: white;
            padding: 28px 32px;
            border-radius: 14px;
            margin-bottom: 25px;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
            border: 1px solid #334155;
        }
        .erp-header h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 700;
            letter-spacing: -0.5px;
            color: #ffffff;
        }
        .erp-header p {
            margin: 6px 0 0 0;
            font-size: 13px;
            color: #94a3b8;
        }

        /* Card Container */
        .erp-card {
            background: #ffffff;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
            border: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }

        /* Buttons Styling */
        div.stButton > button {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            border: none;
            box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
            transition: all 0.3s ease;
            width: 100%;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
            box-shadow: 0 6px 12px rgba(37, 99, 235, 0.3);
            transform: translateY(-1px);
        }

        /* Metric Styling override */
        div[data-testid="metric-container"] {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 16px;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }
        </style>
    """, unsafe_allow_html=True)

def display_header(title, subtitle):
    """Menampilkan header mewah kelas enterprise"""
    st.markdown(f"""
        <div class="erp-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)