# ============================================================
# Dashboard Business Intelligence ISPU Jakarta
# Tugas 6 - Analisis Kualitas Udara Jakarta Berbasis Data ISPU
# ------------------------------------------------------------
# Cara menjalankan:
# 1. Letakkan file ispu_jakarta_objek_data_tugas5.csv satu folder dengan app.py
# 2. Install dependency: pip install -r requirements.txt
# 3. Jalankan: streamlit run app.py
# ============================================================

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# Konfigurasi Halaman
# ============================================================
st.set_page_config(
    page_title="Dashboard ISPU Jakarta",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path("ispu_jakarta_objek_data_tugas5.csv")

UNHEALTHY_CATEGORIES = ["TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]
CATEGORY_ORDER = ["BAIK", "SEDANG", "TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]
CRITICAL_ORDER = ["PM10", "PM2.5", "SO2", "CO", "O3", "NO2"]
MONTH_ORDER = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

# Warna dibuat konsisten, mudah dibaca, dan secara semantik berurutan.
CATEGORY_COLORS = {
    "BAIK": "#16A34A",                 # hijau
    "SEDANG": "#FACC15",              # kuning
    "TIDAK SEHAT": "#F97316",         # oranye
    "SANGAT TIDAK SEHAT": "#DC2626",  # merah
    "BERBAHAYA": "#7F1D1D",           # marun tua
}

CRITICAL_COLORS = {
    "PM10": "#2563EB",
    "PM2.5": "#7C3AED",
    "SO2": "#0891B2",
    "CO": "#0F766E",
    "O3": "#EA580C",
    "NO2": "#BE123C",
}

CRITICAL_LABELS = {
    "PM10": "PM10",
    "PM2.5": "PM2.5",
    "SO2": "SO2",
    "CO": "CO",
    "O3": "O3 (Ozon)",
    "NO2": "NO2",
}

# Warna stasiun dibuat tegas agar mudah dibedakan saat membandingkan risiko Tidak Sehat+.
STATION_COLORS = {
    "DKI1 Bunderan HI": "#1E3A8A",
    "DKI2 Kelapa Gading": "#C2410C",
    "DKI3 Jagakarsa": "#B91C1C",
    "DKI4 Lubang Buaya": "#7F1D1D",
    "DKI5 Kebon Jeruk": "#581C87",
}

CRITICAL_TO_POLLUTANT_COL = {
    "PM10": "pm10",
    "PM2.5": "pm25",
    "SO2": "so2",
    "CO": "co",
    "O3": "o3",
    "NO2": "no2",
}

# Koordinat hanya untuk visualisasi peta, tidak menambah kolom pada dataset Tugas 5.
STATION_COORDS = {
    "DKI1 Bunderan HI": {"lat": -6.19521, "lon": 106.82265},
    "DKI2 Kelapa Gading": {"lat": -6.13704, "lon": 106.89363},
    "DKI3 Jagakarsa": {"lat": -6.34192, "lon": 106.80644},
    "DKI4 Lubang Buaya": {"lat": -6.31064, "lon": 106.97430},
    "DKI5 Kebon Jeruk": {"lat": -6.17150, "lon": 106.77330},
}

PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}

# ============================================================
# Styling
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    :root {
        --page-bg: #F3F6FA;
        --card-bg: #FFFFFF;
        --navy: #0B2545;
        --navy-2: #123B63;
        --blue: #2563EB;
        --cyan: #0891B2;
        --green: #16A34A;
        --orange: #F97316;
        --red: #DC2626;
        --text: #0F172A;
        --muted: #64748B;
        --border: #DDE5EF;
        --soft-blue: #EFF6FF;
        --soft-gray: #F8FAFC;
        --shadow: 0 14px 34px rgba(15, 23, 42, 0.08);
    }

    html, body, .stApp, [data-testid="stAppViewContainer"], main {
        background: var(--page-bg) !important;
        color: var(--text) !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }

    [data-testid="stHeader"] {
        background: rgba(243, 246, 250, 0.92) !important;
        backdrop-filter: blur(10px);
        box-shadow: none !important;
    }

    /* Hilangkan toolbar/deploy agar tidak ada teks kecil yang mengganggu tampilan presentasi. */
    [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        visibility: hidden !important;
        height: 0 !important;
        position: fixed !important;
    }


    #MainMenu, footer, header [data-testid="stToolbarActions"],
    [data-testid="stDeployButton"], [data-testid="stBaseButton-headerNoPadding"],
    [data-testid="stActionButton"] {
        display: none !important;
        visibility: hidden !important;
    }

    .main .block-container {
        max-width: 1360px;
        padding-top: 1.1rem;
        padding-bottom: 2.8rem;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div {
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }

    h1, h2, h3 {
        color: var(--text) !important;
        letter-spacing: -0.035em;
    }

    div[data-testid="stMarkdownContainer"] p {
        color: var(--muted);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%) !important;
        border-right: 1px solid var(--border);
        box-shadow: 10px 0 28px rgba(15, 23, 42, 0.05);
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-top: 1.5rem;
        padding-left: 1.15rem;
        padding-right: 1.15rem;
    }

    .sidebar-brand {
        background: linear-gradient(135deg, #0B2545 0%, #0E7490 100%);
        border-radius: 20px;
        padding: 1rem 1rem 1.05rem 1rem;
        color: #FFFFFF !important;
        box-shadow: 0 16px 34px rgba(11, 37, 69, 0.18);
        margin-bottom: 1rem;
    }

    .sidebar-brand-title {
        font-size: 1.05rem;
        font-weight: 900;
        color: #FFFFFF !important;
        letter-spacing: -0.02em;
        margin-bottom: 0.35rem;
    }

    .sidebar-brand-subtitle {
        font-size: 0.82rem;
        color: #DDEBFF !important;
        line-height: 1.45;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: var(--text) !important;
    }

    section[data-testid="stSidebar"] h3 {
        font-size: 1.05rem !important;
        font-weight: 900 !important;
        margin: 0.55rem 0 0.55rem 0 !important;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-size: 0.86rem !important;
        line-height: 1.2 !important;
        font-weight: 700 !important;
        color: #334155 !important;
        margin-bottom: 0.25rem !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: #E2E8F0 !important;
        margin: 1rem 0 !important;
    }

    .sidebar-section-label {
        font-size: 0.86rem;
        font-weight: 850;
        color: #334155 !important;
        margin: 0.8rem 0 0.35rem 0;
        letter-spacing: -0.01em;
    }

    /* Checkbox stasiun dibuat seperti pilihan penuh, bukan chip yang terpotong. */
    section[data-testid="stSidebar"] [data-testid="stCheckbox"] {
        margin-bottom: 0.28rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
        background: #FFFFFF !important;
        border: 1px solid #D8E2F0 !important;
        border-radius: 13px !important;
        padding: 0.48rem 0.55rem !important;
        box-shadow: 0 5px 14px rgba(15, 23, 42, 0.035) !important;
        display: flex !important;
        align-items: flex-start !important;
        gap: 0.45rem !important;
        min-height: 36px !important;
        width: 100% !important;
    }

    section[data-testid="stSidebar"] [data-testid="stCheckbox"] label:hover {
        background: #EFF6FF !important;
        border-color: #BFDBFE !important;
    }

    section[data-testid="stSidebar"] [data-testid="stCheckbox"] label p,
    section[data-testid="stSidebar"] [data-testid="stCheckbox"] label span {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        font-size: 0.78rem !important;
        line-height: 1.22 !important;
        font-weight: 750 !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        max-width: 190px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stCheckbox"] svg {
        color: #2563EB !important;
    }

    /* Slider tanggal/tahun dibuat lebih ringkas agar tidak ada kotak input yang mengganggu. */
    section[data-testid="stSidebar"] [data-testid="stSlider"] {
        padding-top: 0.05rem !important;
        padding-bottom: 0.35rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSlider"] p,
    section[data-testid="stSidebar"] [data-testid="stSlider"] span,
    section[data-testid="stSidebar"] [data-testid="stSlider"] div {
        color: #334155 !important;
        -webkit-text-fill-color: #334155 !important;
        font-size: 0.78rem !important;
    }

    /* Radio menu lebih rapi dan terbaca */
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 0.28rem !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        padding: 0.55rem 0.6rem !important;
        margin-bottom: 0 !important;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.04) !important;
        min-height: 42px !important;
        display: flex !important;
        align-items: center !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: #EFF6FF !important;
        border-color: #BFDBFE !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label p,
    section[data-testid="stSidebar"] div[role="radiogroup"] label span,
    section[data-testid="stSidebar"] [data-testid="stRadio"] p,
    section[data-testid="stSidebar"] [data-testid="stRadio"] span {
        font-size: 0.84rem !important;
        line-height: 1.25 !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        font-weight: 750 !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] svg {
        flex: 0 0 auto !important;
    }

    /* Paksa semua input filter menjadi terang, compact, dan tidak hitam. */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] div[data-baseweb="input"] > div,
    section[data-testid="stSidebar"] div[data-baseweb="datepicker"] input,
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: #FFFFFF !important;
        color: var(--text) !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        min-height: 38px !important;
        font-size: 0.82rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stDateInput"] input {
        font-size: 0.78rem !important;
        letter-spacing: -0.02em !important;
        padding-left: 0.55rem !important;
        padding-right: 0.35rem !important;
        min-width: 0 !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] {
        font-size: 0.82rem !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        max-height: 158px !important;
        overflow-y: auto !important;
    }

    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea,
    div[data-baseweb="select"] input {
        background: transparent !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[role="listbox"] {
        background: #FFFFFF !important;
        color: var(--text) !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 14px !important;
        box-shadow: 0 16px 34px rgba(15, 23, 42, 0.14) !important;
    }

    li[role="option"] {
        color: var(--text) !important;
        background: #FFFFFF !important;
    }

    li[role="option"]:hover {
        background: #EFF6FF !important;
    }

    div[data-baseweb="tag"], span[data-baseweb="tag"], [data-baseweb="tag"] {
        background: #DBEAFE !important;
        border: 1px solid #BFDBFE !important;
        color: #1E3A8A !important;
        border-radius: 999px !important;
        font-weight: 750 !important;
        height: 28px !important;
        max-width: 100% !important;
        margin: 0.12rem 0.18rem 0.12rem 0 !important;
    }

    div[data-baseweb="tag"] span, span[data-baseweb="tag"] span, [data-baseweb="tag"] * {
        color: #1E3A8A !important;
        -webkit-text-fill-color: #1E3A8A !important;
        font-size: 0.78rem !important;
        line-height: 1.1 !important;
    }

    [data-testid="stDateInput"] input, [data-testid="stMultiSelect"] input {
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }

    [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Kartu header */
    .hero-card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #0B2545 0%, #113B63 50%, #0E7490 100%);
        border-radius: 30px;
        padding: 2rem 2.15rem;
        color: white;
        box-shadow: 0 24px 60px rgba(11, 37, 69, 0.22);
        margin-bottom: 1.15rem;
        border: 1px solid rgba(255, 255, 255, 0.18);
    }

    .hero-card::after {
        content: '';
        position: absolute;
        width: 380px;
        height: 380px;
        right: -130px;
        top: -170px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.12);
    }

    .hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.42rem 0.78rem;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.22);
        border-radius: 999px;
        color: #E0F2FE !important;
        font-weight: 800;
        font-size: 0.82rem;
        margin-bottom: 0.9rem;
    }

    .hero-title {
        color: #FFFFFF !important;
        font-size: 2.35rem;
        line-height: 1.05;
        font-weight: 900;
        letter-spacing: -0.045em;
        margin: 0 0 0.55rem 0;
        max-width: 900px;
    }

    .hero-subtitle {
        color: #DDEBFF !important;
        font-size: 1.02rem;
        line-height: 1.58;
        max-width: 900px;
        margin: 0;
    }

    .page-title {
        font-size: 1.85rem;
        line-height: 1.16;
        font-weight: 900;
        color: var(--text) !important;
        margin: 1.1rem 0 0.3rem 0;
    }

    .page-description {
        font-size: 1rem;
        color: var(--muted) !important;
        line-height: 1.55;
        margin-bottom: 1rem;
    }

    .metric-card {
        position: relative;
        overflow: hidden;
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 1.1rem 1.15rem 1rem 1.15rem;
        box-shadow: var(--shadow);
        min-height: 140px;
        transition: all 0.18s ease-in-out;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 22px 42px rgba(15, 23, 42, 0.11);
    }

    .metric-accent {
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 6px;
        background: var(--accent-color);
    }

    .metric-icon {
        width: 34px;
        height: 34px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        background: var(--accent-soft);
        color: var(--accent-color);
        font-size: 1.1rem;
        margin-bottom: 0.7rem;
    }

    .metric-label {
        font-size: 0.76rem;
        color: var(--muted) !important;
        font-weight: 850;
        letter-spacing: 0.055em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .metric-value {
        font-size: 1.92rem;
        color: var(--text) !important;
        line-height: 1.05;
        font-weight: 900;
        letter-spacing: -0.04em;
        margin-bottom: 0.45rem;
    }

    .metric-help {
        color: var(--muted) !important;
        font-size: 0.84rem;
        line-height: 1.35;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 24px !important;
        box-shadow: var(--shadow) !important;
    }

    .stPlotlyChart {
        background: #FFFFFF !important;
        border-radius: 16px !important;
    }

    .chart-title {
        color: var(--text) !important;
        font-size: 1.08rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        margin-bottom: 0.16rem;
    }

    .chart-subtitle {
        color: var(--muted) !important;
        font-size: 0.9rem;
        line-height: 1.45;
        margin-bottom: 0.7rem;
    }

    .insight-card {
        background: linear-gradient(180deg, #EFF6FF 0%, #F8FAFC 100%);
        border: 1px solid #BFDBFE;
        border-left: 6px solid #2563EB;
        border-radius: 18px;
        padding: 1rem 1.15rem;
        box-shadow: 0 12px 26px rgba(37, 99, 235, 0.08);
        margin-top: 0.85rem;
        margin-bottom: 1.1rem;
    }

    .insight-title {
        color: #1E3A8A !important;
        font-weight: 900;
        font-size: 0.95rem;
        margin-bottom: 0.32rem;
        letter-spacing: 0.01em;
    }

    .insight-text {
        color: #1E3A8A !important;
        font-size: 0.95rem;
        line-height: 1.55;
    }

    .mini-note {
        background: #F8FAFC;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.75rem 0.9rem;
        color: #475569 !important;
        font-size: 0.88rem;
        line-height: 1.45;
        margin-top: 0.6rem;
    }

    .filter-summary {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
        color: var(--muted) !important;
        font-size: 0.86rem;
        line-height: 1.55;
        margin-bottom: 1rem;
    }

    .filter-summary b { color: var(--text) !important; }

    .small-muted {
        color: var(--muted) !important;
        font-size: 0.86rem;
        line-height: 1.45;
    }

    /* Tabel HTML custom agar tidak ikut dark theme komponen bawaan. */
    .custom-table-wrapper {
        width: 100%;
        overflow-x: auto;
        border: 1px solid var(--border);
        border-radius: 16px;
        background: #FFFFFF;
    }

    table.custom-table {
        width: 100%;
        border-collapse: collapse;
        background: #FFFFFF;
        color: var(--text);
        font-size: 0.9rem;
    }

    table.custom-table thead th {
        background: #F1F5F9;
        color: #334155;
        text-align: left;
        padding: 0.8rem 0.85rem;
        border-bottom: 1px solid var(--border);
        white-space: nowrap;
        font-weight: 850;
    }

    table.custom-table tbody td {
        padding: 0.78rem 0.85rem;
        border-bottom: 1px solid #EEF2F7;
        color: #0F172A;
        white-space: nowrap;
    }

    table.custom-table tbody tr:nth-child(even) { background: #FAFCFF; }
    table.custom-table tbody tr:hover { background: #EFF6FF; }

    /* Kurangi padding iframe plotly agar tidak muncul tulisan/ruang aneh. */
    .js-plotly-plot .plotly .main-svg { border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Utility Functions
# ============================================================
@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        st.error(f"File `{path}` tidak ditemukan. Letakkan file CSV di folder yang sama dengan `app.py`.")
        st.stop()

    df = pd.read_csv(path)
    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

    # Kolom turunan minimal untuk memastikan dashboard tetap jalan jika CSV berbeda versi.
    if "tahun" not in df.columns:
        df["tahun"] = df["tanggal"].dt.year
    if "bulan" not in df.columns:
        df["bulan"] = df["tanggal"].dt.month
    if "nama_bulan" not in df.columns:
        df["nama_bulan"] = df["bulan"].map(dict(enumerate(MONTH_ORDER, start=1)))
    if "periode_bulanan" not in df.columns:
        df["periode_bulanan"] = df["tanggal"].dt.to_period("M").astype(str)
    if "periode_tahunan" not in df.columns:
        df["periode_tahunan"] = df["tanggal"].dt.year.astype(str)
    if "kode_stasiun" not in df.columns:
        df["kode_stasiun"] = df["stasiun"].str.extract(r"^(DKI\d)", expand=False)

    numeric_cols = ["pm10", "pm25", "so2", "co", "o3", "no2", "max"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["categori"] = df["categori"].astype(str).str.upper().str.strip()
    df["critical"] = df["critical"].astype(str).str.upper().str.strip()
    df["_tidak_sehat_plus"] = df["categori"].isin(UNHEALTHY_CATEGORIES)
    df["critical_label"] = df["critical"].map(CRITICAL_LABELS).fillna(df["critical"])
    df["nama_bulan"] = pd.Categorical(df["nama_bulan"], categories=MONTH_ORDER, ordered=True)
    return df


def add_station_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    coord_df = pd.DataFrame.from_dict(STATION_COORDS, orient="index").reset_index()
    coord_df = coord_df.rename(columns={"index": "stasiun"})
    return df.merge(coord_df, on="stasiun", how="left")


def format_number(value, decimals=1):
    if pd.isna(value):
        return "-"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percent(value, decimals=1):
    if pd.isna(value):
        return "-"
    return f"{value:.{decimals}f}%".replace(".", ",")


def format_int(value):
    if pd.isna(value):
        return "-"
    return f"{int(value):,}".replace(",", ".")


def get_dominant(series: pd.Series):
    counts = series.dropna().value_counts()
    if counts.empty:
        return "-", 0
    return counts.index[0], int(counts.iloc[0])


def metric_card(label: str, value: str, help_text: str, icon: str = "•", accent: str = "#2563EB", soft: str = "#EFF6FF"):
    st.markdown(
        f"""
        <div class="metric-card" style="--accent-color:{accent}; --accent-soft:{soft};">
            <div class="metric-accent"></div>
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, description: str):
    st.markdown(f"<div class='page-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-description'>{description}</div>", unsafe_allow_html=True)


def insight_card(text: str):
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">Insight utama</div>
            <div class="insight-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mini_note(text: str):
    st.markdown(f"<div class='mini-note'>{text}</div>", unsafe_allow_html=True)


def render_html_table(df: pd.DataFrame, max_rows: int | None = None):
    """Render tabel terang dan rapi agar tidak ikut dark style bawaan komponen dataframe."""
    display_df = df.copy()
    if max_rows is not None:
        display_df = display_df.head(max_rows)
    html = display_df.to_html(index=False, escape=False, classes="custom-table")
    st.markdown(f"<div class='custom-table-wrapper'>{html}</div>", unsafe_allow_html=True)


def ispu_threshold_color(value):
    """Warna berdasarkan rentang kategori ISPU: baik sampai berbahaya."""
    if pd.isna(value):
        return "#CBD5E1"
    if value <= 50:
        return CATEGORY_COLORS["BAIK"]
    if value <= 100:
        return CATEGORY_COLORS["SEDANG"]
    if value <= 200:
        return CATEGORY_COLORS["TIDAK SEHAT"]
    if value <= 300:
        return CATEGORY_COLORS["SANGAT TIDAK SEHAT"]
    return CATEGORY_COLORS["BERBAHAYA"]


def risk_percent_color(value):
    """Warna persentase risiko: makin tinggi makin merah."""
    if pd.isna(value):
        return "#CBD5E1"
    if value < 10:
        return "#FACC15"
    if value < 20:
        return "#F97316"
    if value < 30:
        return "#DC2626"
    return "#7F1D1D"


def chart_container(title: str, subtitle: str = ""):
    box = st.container(border=True)
    with box:
        st.markdown(f"<div class='chart-title'>{title}</div>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(f"<div class='chart-subtitle'>{subtitle}</div>", unsafe_allow_html=True)
    return box


def apply_common_layout(fig, height=None, legend_title=""):
    fig.update_layout(
        title_text="",
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#0F172A", family="Inter, Segoe UI, sans-serif", size=13),
        title_font=dict(color="#0F172A", size=19),
        legend_title_text=legend_title,
        legend=dict(
            font=dict(size=12, color="#0F172A"),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0)",
            borderwidth=0,
        ),
        legend_title_font=dict(size=12, color="#0F172A"),
        margin=dict(l=18, r=18, t=28, b=42),
        hoverlabel=dict(bgcolor="#0F172A", bordercolor="#0F172A", font_color="#FFFFFF"),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        color="#334155",
        title_font=dict(color="#334155", size=13),
        tickfont=dict(color="#334155", size=12),
    )
    fig.update_yaxes(
        gridcolor="#E2E8F0",
        zeroline=False,
        color="#334155",
        title_font=dict(color="#334155", size=13),
        tickfont=dict(color="#334155", size=12),
    )
    if height:
        fig.update_layout(height=height)
    return fig


def show_plot(fig):
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)


def empty_state():
    st.warning("Tidak ada data untuk kombinasi filter yang dipilih. Silakan ubah filter di sidebar.")
    st.stop()


def period_label(dt_value, granularity: str):
    dt = pd.to_datetime(dt_value)
    if granularity == "Tahunan":
        return dt.strftime("%Y")
    if granularity == "Bulanan":
        return dt.strftime("%Y-%m")
    return dt.strftime("%Y-%m-%d")

# ============================================================
# Load Data dan Sidebar
# ============================================================
df = load_data(DATA_PATH)

st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">🌤️ ISPU Jakarta</div>
        <div class="sidebar-brand-subtitle">Dashboard interaktif kualitas udara DKI Jakarta.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

menu = st.sidebar.radio(
    "Pilih dashboard",
    [
        "1. Overview Kualitas Udara",
        "2. Tren Temporal Kualitas Udara",
        "3. Perbandingan Antar Stasiun",
        "4. Parameter Pencemar Kritis",
        "5. Pola Musiman Kualitas Udara",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filter Data")

min_date = df["tanggal"].min().date()
max_date = df["tanggal"].max().date()

date_range = st.sidebar.slider(
    "Rentang tanggal",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD",
    help="Geser titik awal dan akhir untuk membatasi periode analisis.",
)
start_date, end_date = date_range

station_lookup = (
    df[["kode_stasiun", "stasiun"]]
    .dropna()
    .drop_duplicates()
    .sort_values("kode_stasiun")
)
st.sidebar.markdown("<div class='sidebar-section-label'>Stasiun SPKU</div>", unsafe_allow_html=True)
selected_station_codes = []
for _, row in station_lookup.iterrows():
    label = f"{row['kode_stasiun']} — {row['stasiun'].replace(str(row['kode_stasiun']) + ' ', '')}"
    checked = st.sidebar.checkbox(label, value=True, key=f"station_{row['kode_stasiun']}")
    if checked:
        selected_station_codes.append(row["kode_stasiun"])

if not selected_station_codes:
    st.sidebar.warning("Pilih minimal satu stasiun agar dashboard dapat ditampilkan.")
    st.stop()

min_year = int(df["tahun"].min())
max_year = int(df["tahun"].max())
selected_year_range = st.sidebar.slider(
    "Rentang tahun",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1,
    help="Filter tambahan berdasarkan tahun pengukuran.",
)

mask = (
    (df["tanggal"].dt.date >= start_date)
    & (df["tanggal"].dt.date <= end_date)
    & (df["kode_stasiun"].isin(selected_station_codes))
    & (df["tahun"].astype(int).between(selected_year_range[0], selected_year_range[1]))
)
dff = df.loc[mask].copy()

if dff.empty:
    empty_state()

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    <div class='filter-summary'>
        <b>Cakupan data terfilter</b><br>
        {format_int(len(dff))} catatan pengukuran<br>
        {format_int(dff['stasiun'].nunique())} stasiun terpantau<br>
        {pd.to_datetime(dff['tanggal'].min()).strftime('%d %b %Y')} - {pd.to_datetime(dff['tanggal'].max()).strftime('%d %b %Y')}
    </div>
    """,
    unsafe_allow_html=True,
)

# Header umum
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-kicker">Business Intelligence Dashboard</div>
        <div class="hero-title">Dashboard ISPU Jakarta</div>
        <p class="hero-subtitle">
            Analisis kualitas udara harian dari 5 stasiun SPKU DKI Jakarta untuk mendukung pemantauan, prioritas intervensi, dan komunikasi kebijakan berbasis data.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Dashboard 1: Overview
# ============================================================
if menu == "1. Overview Kualitas Udara":
    page_header(
        "1. Overview Kualitas Udara Jakarta",
        "Ringkasan kondisi kualitas udara melalui KPI utama, distribusi kategori ISPU, pencemar kritis dominan, dan peta lokasi stasiun.",
    )

    # KPI utama dibuat fokus pada 1 tahun terakhir agar lebih relevan untuk stakeholder.
    # Visualisasi lain tetap memakai dff, yaitu data sesuai filter sidebar.
    latest_date = dff["tanggal"].max()
    kpi_start_date = latest_date - pd.DateOffset(years=1) + pd.DateOffset(days=1)
    kpi_dff = dff[dff["tanggal"] >= kpi_start_date].copy()
    if kpi_dff.empty:
        kpi_dff = dff.copy()
        kpi_start_date = dff["tanggal"].min()

    avg_daily_ispu = kpi_dff.groupby("tanggal", as_index=False)["max"].mean()["max"].mean()
    unhealthy_pct = kpi_dff["_tidak_sehat_plus"].mean() * 100
    dominant_pollutant, dominant_count = get_dominant(kpi_dff["critical"])
    dominant_label = CRITICAL_LABELS.get(dominant_pollutant, dominant_pollutant)
    station_count = kpi_dff["stasiun"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Rata-rata ISPU harian", format_number(avg_daily_ispu, 1), "Rata-rata nilai ISPU pada 1 tahun terakhir.", "📈", "#2563EB", "#DBEAFE")
    with c2:
        metric_card("Tidak sehat+", format_percent(unhealthy_pct, 1), "Kategori Tidak Sehat atau lebih buruk pada 1 tahun terakhir.", "⚠️", "#F97316", "#FFEDD5")
    with c3:
        metric_card("Pencemar dominan", dominant_label, f"Muncul {format_int(dominant_count)} kali pada 1 tahun terakhir.", "🌫️", "#7C3AED", "#F3E8FF")
    with c4:
        metric_card("Stasiun terpantau", format_int(station_count), "Jumlah SPKU aktif pada 1 tahun terakhir.", "📍", "#16A34A", "#DCFCE7")

    mini_note(
        f"KPI utama dihitung dari 1 tahun terakhir dalam rentang "
        f"({pd.to_datetime(kpi_start_date).strftime('%d %b %Y')} - {pd.to_datetime(latest_date).strftime('%d %b %Y')})."
    )

    latest_station = dff[dff["tanggal"] == latest_date].sort_values(["stasiun"]).copy()
    latest_station_map = add_station_coordinates(latest_station)

    left, right = st.columns([1.25, 1])

    with left:
        with st.container(border=True):
            st.markdown("<div class='chart-title'>Peta kondisi terbaru per stasiun</div>", unsafe_allow_html=True)
            st.markdown("<div class='chart-subtitle'>Ukuran titik menunjukkan nilai ISPU terbaru pada periode terfilter.</div>", unsafe_allow_html=True)
            map_df = latest_station_map.dropna(subset=["lat", "lon"]).copy()
            if map_df.empty:
                st.info("Koordinat stasiun tidak tersedia untuk data terfilter.")
            else:
                fig_map = px.scatter_mapbox(
                    map_df,
                    lat="lat",
                    lon="lon",
                    size="max",
                    color="categori",
                    color_discrete_map=CATEGORY_COLORS,
                    hover_name="stasiun",
                    hover_data={
                        "tanggal": True,
                        "max": ":.1f",
                        "critical_label": True,
                        "lat": False,
                        "lon": False,
                    },
                    category_orders={"categori": CATEGORY_ORDER},
                    zoom=9.6,
                    height=470,
                    size_max=34,
                )
                fig_map.update_layout(
                    mapbox_style="open-street-map",
                    margin=dict(l=0, r=0, t=44, b=0),
                    legend_title_text="Kategori ISPU",
                    paper_bgcolor="#FFFFFF",
                    font=dict(color="#0F172A", family="Inter, Segoe UI, sans-serif"),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="left",
                        x=0,
                        bgcolor="rgba(255,255,255,0)",
                        borderwidth=0,
                        font=dict(color="#0F172A", size=12),
                        title=dict(font=dict(color="#0F172A", size=13)),
                        entrywidth=118,
                        entrywidthmode="pixels",
                    ),
                )
                show_plot(fig_map)
                mini_note("Koordinat stasiun digunakan sebagai referensi visualisasi lokasi SPKU pada peta.")

    with right:
        with st.container(border=True):
            st.markdown("<div class='chart-title'>Distribusi kategori ISPU per tahun</div>", unsafe_allow_html=True)
            st.markdown("<div class='chart-subtitle'>Komposisi kategori kualitas udara setiap tahun berdasarkan filter sidebar.</div>", unsafe_allow_html=True)
            year_cat = dff.groupby(["tahun", "categori"], as_index=False).size().rename(columns={"size": "jumlah"})
            full_index = pd.MultiIndex.from_product(
                [sorted(dff["tahun"].dropna().unique()), CATEGORY_ORDER],
                names=["tahun", "categori"],
            )
            year_cat = (
                year_cat.set_index(["tahun", "categori"])
                .reindex(full_index, fill_value=0)
                .reset_index()
            )
            year_cat["total_tahun"] = year_cat.groupby("tahun")["jumlah"].transform("sum")
            year_cat["persentase"] = np.where(
                year_cat["total_tahun"] > 0,
                year_cat["jumlah"] / year_cat["total_tahun"] * 100,
                0,
            )
            year_cat["tahun_label"] = year_cat["tahun"].astype(str)
            fig_cat = px.bar(
                year_cat,
                x="tahun_label",
                y="persentase",
                color="categori",
                category_orders={"categori": CATEGORY_ORDER, "tahun_label": [str(y) for y in sorted(dff["tahun"].dropna().unique())]},
                color_discrete_map=CATEGORY_COLORS,
                height=500,
                custom_data=["jumlah", "total_tahun"],
            )
            fig_cat.update_traces(
                marker_line_width=0,
                hovertemplate="Tahun=%{x}<br>Kategori=%{fullData.name}<br>Persentase=%{y:.1f}%<br>Jumlah=%{customdata[0]} dari %{customdata[1]} catatan<extra></extra>",
            )
            fig_cat.update_layout(
                xaxis_title="Tahun",
                yaxis_title="Persentase kategori (%)",
                barmode="stack",
                legend_title_text="Kategori ISPU",
                yaxis=dict(range=[0, 100]),
            )
            fig_cat = apply_common_layout(fig_cat, height=500, legend_title="Kategori ISPU")
            fig_cat.update_layout(
                margin=dict(l=18, r=18, t=92, b=56),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.10,
                    xanchor="left",
                    x=0,
                    bgcolor="rgba(255,255,255,0)",
                    borderwidth=0,
                    font=dict(color="#0F172A", size=11),
                    title=dict(font=dict(color="#0F172A", size=12)),
                    entrywidth=118,
                    entrywidthmode="pixels",
                ),
            )
            fig_cat.update_xaxes(tickangle=90)
            show_plot(fig_cat)

    bottom1, bottom2 = st.columns([1, 1])
    with bottom1:
        with st.container(border=True):
            st.markdown("<div class='chart-title'>Persentase kemunculan pencemar kritis</div>", unsafe_allow_html=True)
            st.markdown("<div class='chart-subtitle'>Grafik ini menormalkan kemunculan berdasarkan ketersediaan masing-masing parameter.</div>", unsafe_allow_html=True)
            normalized_rows = []
            for critical_name in CRITICAL_ORDER:
                pollutant_col = CRITICAL_TO_POLLUTANT_COL.get(critical_name)
                if pollutant_col not in dff.columns:
                    continue
                available_mask = dff[pollutant_col].notna()
                available_count = int(available_mask.sum())
                critical_count = int(((dff["critical"] == critical_name) & available_mask).sum())
                first_available = dff.loc[available_mask, "tanggal"].min() if available_count > 0 else pd.NaT
                normalized_rows.append({
                    "critical": critical_name,
                    "critical_label": CRITICAL_LABELS.get(critical_name, critical_name),
                    "jumlah": critical_count,
                    "catatan_tersedia": available_count,
                    "persentase": (critical_count / available_count * 100) if available_count > 0 else 0,
                    "periode_awal": pd.to_datetime(first_available).strftime("%Y-%m-%d") if pd.notna(first_available) else "-",
                })
            critical_norm = pd.DataFrame(normalized_rows)
            fig_critical = px.bar(
                critical_norm,
                x="critical_label",
                y="persentase",
                text="persentase",
                color="critical",
                color_discrete_map=CRITICAL_COLORS,
                height=420,
                custom_data=["jumlah", "catatan_tersedia", "periode_awal"],
            )
            fig_critical.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                marker_line_width=0,
                cliponaxis=False,
                hovertemplate="Parameter=%{x}<br>Persentase=%{y:.1f}%<br>Kemunculan=%{customdata[0]}<br>Catatan tersedia=%{customdata[1]}<br>Data tersedia sejak=%{customdata[2]}<extra></extra>",
            )
            fig_critical.update_layout(xaxis_title="Parameter pencemar kritis", yaxis_title="Persentase kemunculan (%)", showlegend=False)
            show_plot(apply_common_layout(fig_critical))

    with bottom2:
        with st.container(border=True):
            st.markdown("<div class='chart-title'>Kondisi terbaru per stasiun</div>", unsafe_allow_html=True)
            st.markdown("<div class='chart-subtitle'>Ringkasan nilai ISPU dan pencemar kritis pada tanggal terakhir di filter.</div>", unsafe_allow_html=True)
            latest_table = latest_station[["tanggal", "kode_stasiun", "stasiun", "max", "critical", "categori"]].copy()
            latest_table["tanggal"] = latest_table["tanggal"].dt.strftime("%Y-%m-%d")
            latest_table["critical"] = latest_table["critical"].map(CRITICAL_LABELS).fillna(latest_table["critical"])
            latest_table = latest_table.rename(columns={
                "tanggal": "Tanggal",
                "kode_stasiun": "Kode",
                "stasiun": "Stasiun",
                "max": "Nilai ISPU",
                "critical": "Pencemar Kritis",
                "categori": "Kategori",
            })
            render_html_table(latest_table)

    insight_card(
        f"Pada 1 tahun terakhir dalam filter aktif, rata-rata ISPU harian berada pada angka <b>{format_number(avg_daily_ispu, 1)}</b>. "
        f"Sebanyak <b>{format_percent(unhealthy_pct, 1)}</b> catatan pengukuran masuk kategori Tidak Sehat atau lebih buruk. "
        f"Parameter yang paling sering menjadi pencemar kritis adalah <b>{dominant_label}</b>, sehingga parameter ini perlu menjadi perhatian awal dalam evaluasi pengendalian pencemaran udara."
    )

# ============================================================
# Dashboard 2: Tren Temporal
# ============================================================
elif menu == "2. Tren Temporal Kualitas Udara":
    page_header(
        "2. Tren Temporal Kualitas Udara",
        "Melihat perubahan nilai ISPU dan frekuensi kondisi Tidak Sehat+ dari waktu ke waktu pada granularitas harian, bulanan, atau tahunan.",
    )

    # Card KPI temporal dibuat fokus pada 1 tahun terakhir agar konsisten dengan Overview.
    # Visualisasi tren di bawah tetap mengikuti filter sidebar dan granularitas yang dipilih.
    latest_date_temporal = dff["tanggal"].max()
    temporal_kpi_start_date = latest_date_temporal - pd.DateOffset(years=1) + pd.DateOffset(days=1)
    temporal_kpi_dff = dff[dff["tanggal"] >= temporal_kpi_start_date].copy()
    if temporal_kpi_dff.empty:
        temporal_kpi_dff = dff.copy()
        temporal_kpi_start_date = dff["tanggal"].min()

    temporal_kpi_dff["periode_kpi"] = pd.to_datetime(temporal_kpi_dff["periode_bulanan"].astype(str) + "-01")
    kpi_trend = (
        temporal_kpi_dff.groupby("periode_kpi", as_index=False)
        .agg(
            rata_rata_ispu=("max", "mean"),
            persen_tidak_sehat_plus=("_tidak_sehat_plus", lambda x: x.mean() * 100),
            jumlah_catatan=("max", "count"),
        )
        .sort_values("periode_kpi")
    )

    first_val = kpi_trend["rata_rata_ispu"].iloc[0]
    last_val = kpi_trend["rata_rata_ispu"].iloc[-1]
    change = last_val - first_val
    risk_peak = kpi_trend.loc[kpi_trend["persen_tidak_sehat_plus"].idxmax()]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "ISPU awal",
            format_number(first_val, 1),
            f"Periode {pd.to_datetime(kpi_trend['periode_kpi'].iloc[0]).strftime('%Y-%m')}",
            "⏮️",
            "#2563EB",
            "#DBEAFE",
        )
    with c2:
        metric_card(
            "ISPU akhir",
            format_number(last_val, 1),
            f"Periode {pd.to_datetime(kpi_trend['periode_kpi'].iloc[-1]).strftime('%Y-%m')}",
            "⏭️",
            "#0F766E",
            "#CCFBF1",
        )
    with c3:
        metric_card(
            "Perubahan",
            format_number(change, 1),
            "Selisih rata-rata ISPU pada 1 tahun terakhir.",
            "↕️",
            "#F97316",
            "#FFEDD5",
        )
    with c4:
        metric_card(
            "Puncak risiko",
            format_percent(risk_peak["persen_tidak_sehat_plus"], 1),
            f"Periode {pd.to_datetime(risk_peak['periode_kpi']).strftime('%Y-%m')}",
            "⚠️",
            "#DC2626",
            "#FEE2E2",
        )

    mini_note(
        f"KPI utama dihitung dari 1 tahun terakhir dalam rentang "
        f"({pd.to_datetime(temporal_kpi_start_date).strftime('%d %b %Y')} - {pd.to_datetime(latest_date_temporal).strftime('%d %b %Y')})."
    )

    st.markdown("<div class='sidebar-section-label'>Pilih granularitas waktu</div>", unsafe_allow_html=True)
    granularity = st.selectbox("Granularitas waktu", ["Harian", "Bulanan", "Tahunan"], index=1, label_visibility="collapsed")

    if granularity == "Harian":
        dff["periode_plot"] = dff["tanggal"]
    elif granularity == "Bulanan":
        dff["periode_plot"] = pd.to_datetime(dff["periode_bulanan"].astype(str) + "-01")
    else:
        dff["periode_plot"] = pd.to_datetime(dff["periode_tahunan"].astype(str) + "-01-01")

    trend = (
        dff.groupby("periode_plot", as_index=False)
        .agg(
            rata_rata_ispu=("max", "mean"),
            median_ispu=("max", "median"),
            jumlah_catatan=("max", "count"),
            persen_tidak_sehat_plus=("_tidak_sehat_plus", lambda x: x.mean() * 100),
        )
        .sort_values("periode_plot")
    )

    peak_row = trend.loc[trend["rata_rata_ispu"].idxmax()]

    with st.container(border=True):
        st.markdown("<div class='chart-title'>Tren rata-rata ISPU</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-subtitle'>Menampilkan rata-rata seluruh stasiun. Pilih stasiun pembanding untuk melihat tren lokasi tertentu. Garis putus-putus menunjukkan ambang masuk kategori Tidak Sehat (ISPU > 100).</div>", unsafe_allow_html=True)

        station_compare_options = sorted(dff["stasiun"].dropna().unique().tolist())
        selected_compare_stations = st.multiselect(
            "Pilih stasiun pembanding",
            options=station_compare_options,
            default=[],
            placeholder="Opsional: pilih satu atau beberapa stasiun",
            help="Jika tidak dipilih, grafik hanya menampilkan tren agregat seluruh stasiun.",
        )

        # Jika tidak ada stasiun pembanding, tampilkan agregat seluruh stasiun.
        # Jika ada stasiun dipilih, agregat seluruh stasiun disembunyikan agar grafik lebih fokus.
        if selected_compare_stations:
            trend_plot = (
                dff[dff["stasiun"].isin(selected_compare_stations)]
                .groupby(["periode_plot", "stasiun"], as_index=False)
                .agg(
                    rata_rata_ispu=("max", "mean"),
                    median_ispu=("max", "median"),
                    jumlah_catatan=("max", "count"),
                    persen_tidak_sehat_plus=("_tidak_sehat_plus", lambda x: x.mean() * 100),
                )
                .rename(columns={"stasiun": "seri"})
                .sort_values("periode_plot")
            )
        else:
            trend_plot = trend.copy()
            trend_plot["seri"] = "Semua Stasiun"
            trend_plot = trend_plot[["periode_plot", "seri", "rata_rata_ispu", "median_ispu", "jumlah_catatan", "persen_tidak_sehat_plus"]]

        fig_trend = px.line(
            trend_plot,
            x="periode_plot",
            y="rata_rata_ispu",
            color="seri",
            markers=(granularity != "Harian"),
            hover_data={"persen_tidak_sehat_plus": ":.1f", "jumlah_catatan": True, "seri": True},
            height=500,
        )
        fig_trend.update_traces(line=dict(width=3), marker=dict(size=7))
        fig_trend.update_layout(
            xaxis_title="Periode",
            yaxis_title="Rata-rata ISPU",
            showlegend=bool(selected_compare_stations),
            legend_title_text="",
        )
        fig_trend.add_hline(
            y=100,
            line_dash="dash",
            line_color="#F97316",
            line_width=2,
            annotation_text="Ambang Tidak Sehat (ISPU > 100)",
            annotation_position="top left",
            annotation_font_color="#9A3412",
            annotation_font_size=12,
        )
        fig_trend = apply_common_layout(fig_trend)
        y_upper_trend = max(110, float(trend_plot["rata_rata_ispu"].max()) * 1.08)
        fig_trend.update_yaxes(range=[0, y_upper_trend])
        fig_trend.update_layout(
            legend=dict(
                font=dict(color="#0F172A", size=12),
                title_font=dict(color="#0F172A", size=12),
                orientation="h",
                yanchor="bottom",
                y=1.03,
                xanchor="left",
                x=0,
                bgcolor="rgba(255,255,255,0)",
                borderwidth=0,
            )
        )
        show_plot(fig_trend)

    with st.container(border=True):
        st.markdown("<div class='chart-title'>Persentase Tidak Sehat+ bulanan (1 tahun terakhir)</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='chart-subtitle'>Membandingkan proporsi categori Tidak Sehat atau lebih buruk per bulan pada 1 tahun terakhir.</div>",
            unsafe_allow_html=True,
        )

        # Grafik risiko dibuat tetap bulanan dan fokus 1 tahun terakhir agar mudah dibaca stakeholder.
        # Grafik ini tidak mengikuti pilihan granularitas waktu di atas, tetapi tetap mengikuti filter sidebar.
        latest_risk_date = dff["tanggal"].max()
        risk_start_date = latest_risk_date - pd.DateOffset(years=1) + pd.DateOffset(days=1)
        risk_month_dff = dff[dff["tanggal"] >= risk_start_date].copy()
        if risk_month_dff.empty:
            risk_month_dff = dff.copy()
            risk_start_date = dff["tanggal"].min()

        risk_month_dff["periode_bulanan_plot"] = pd.to_datetime(risk_month_dff["periode_bulanan"].astype(str) + "-01")
        risk_month_dff["bulan_tampil"] = risk_month_dff["periode_bulanan_plot"].dt.strftime("%Y-%m")

        if selected_compare_stations:
            risk_plot = (
                risk_month_dff[risk_month_dff["stasiun"].isin(selected_compare_stations)]
                .groupby(["periode_bulanan_plot", "bulan_tampil", "stasiun"], as_index=False)
                .agg(
                    jumlah_catatan=("max", "count"),
                    jumlah_tidak_sehat_plus=("_tidak_sehat_plus", "sum"),
                    persen_tidak_sehat_plus=("_tidak_sehat_plus", lambda x: x.mean() * 100),
                )
                .rename(columns={"stasiun": "seri"})
                .sort_values("periode_bulanan_plot")
            )
            show_risk_legend = True
        else:
            risk_plot = (
                risk_month_dff.groupby(["periode_bulanan_plot", "bulan_tampil"], as_index=False)
                .agg(
                    jumlah_catatan=("max", "count"),
                    jumlah_tidak_sehat_plus=("_tidak_sehat_plus", "sum"),
                    persen_tidak_sehat_plus=("_tidak_sehat_plus", lambda x: x.mean() * 100),
                )
                .sort_values("periode_bulanan_plot")
            )
            risk_plot["seri"] = "Semua Stasiun"
            show_risk_legend = False

        if risk_plot.empty:
            st.info("Tidak ada data risiko Tidak Sehat+ pada 1 tahun terakhir dari filter aktif.")
            risk_peak_temporal = None
        else:
            # Paksa semua bulan tampil di sumbu X agar tidak ada label bulan yang tersembunyi otomatis.
            month_labels = (
                risk_plot[["periode_bulanan_plot", "bulan_tampil"]]
                .drop_duplicates()
                .sort_values("periode_bulanan_plot")["bulan_tampil"]
                .tolist()
            )

            fig_unhealthy_period = go.Figure()
            for series_name, series_df in risk_plot.groupby("seri", sort=False):
                series_df = series_df.sort_values("periode_bulanan_plot")
                if selected_compare_stations:
                    # Jika membandingkan stasiun, warna dipakai untuk membedakan stasiun.
                    # Tinggi bar tetap menjadi indikator besarnya risiko Tidak Sehat+.
                    marker_colors = STATION_COLORS.get(series_name, "#334155")
                else:
                    # Jika hanya agregat semua stasiun, warna mengikuti tingkat risiko persentase Tidak Sehat+.
                    marker_colors = series_df["persen_tidak_sehat_plus"].apply(risk_percent_color).tolist()
                fig_unhealthy_period.add_trace(
                    go.Bar(
                        x=series_df["bulan_tampil"],
                        y=series_df["persen_tidak_sehat_plus"],
                        name=series_name,
                        text=series_df["persen_tidak_sehat_plus"],
                        texttemplate="%{text:.1f}%",
                        textposition="outside",
                        marker=dict(color=marker_colors, line=dict(width=0)),
                        offsetgroup=series_name,
                        customdata=np.stack(
                            [
                                series_df["jumlah_tidak_sehat_plus"].to_numpy(),
                                series_df["jumlah_catatan"].to_numpy(),
                                series_df["seri"].to_numpy(),
                            ],
                            axis=-1,
                        ),
                        hovertemplate=(
                            "Bulan=%{x}<br>"
                            "Seri=%{customdata[2]}<br>"
                            "Persentase Tidak Sehat+=%{y:.1f}%<br>"
                            "Jumlah Tidak Sehat+=%{customdata[0]}<br>"
                            "Jumlah Catatan=%{customdata[1]}"
                            "<extra></extra>"
                        ),
                        cliponaxis=False,
                    )
                )

            fig_unhealthy_period.update_layout(
                barmode="group",
                xaxis_title="Bulan",
                yaxis_title="Persentase Tidak Sehat+ (%)",
                showlegend=show_risk_legend,
                legend_title_text="",
                height=470,
            )
            fig_unhealthy_period = apply_common_layout(fig_unhealthy_period)
            fig_unhealthy_period.update_xaxes(
                tickmode="array",
                tickvals=month_labels,
                ticktext=month_labels,
                tickangle=-30,
                categoryorder="array",
                categoryarray=month_labels,
            )
            fig_unhealthy_period.update_layout(
                legend=dict(
                    font=dict(color="#0F172A", size=12),
                    title_font=dict(color="#0F172A", size=12),
                    orientation="h",
                    yanchor="bottom",
                    y=1.03,
                    xanchor="left",
                    x=0,
                    bgcolor="rgba(255,255,255,0)",
                    borderwidth=0,
                )
            )
            show_plot(fig_unhealthy_period)
            risk_peak_temporal = risk_plot.loc[risk_plot["persen_tidak_sehat_plus"].idxmax()]

    direction = "meningkat/memburuk" if change > 0 else "menurun/membaik" if change < 0 else "relatif tetap"
    if risk_peak_temporal is not None:
        risk_month_label = pd.to_datetime(risk_peak_temporal["periode_bulanan_plot"]).strftime("%Y-%m")
        if selected_compare_stations:
            risk_sentence = (
                f"Risiko Tidak Sehat+ bulanan tertinggi pada grafik terjadi di <b>{risk_peak_temporal['seri']}</b> "
                f"periode <b>{risk_month_label}</b> sebesar "
                f"<b>{format_percent(risk_peak_temporal['persen_tidak_sehat_plus'], 1)}</b>."
            )
        else:
            risk_sentence = (
                f"Risiko Tidak Sehat+ agregat bulanan tertinggi pada grafik terjadi pada periode "
                f"<b>{risk_month_label}</b> sebesar "
                f"<b>{format_percent(risk_peak_temporal['persen_tidak_sehat_plus'], 1)}</b>."
            )
    else:
        risk_sentence = "Grafik risiko bulanan tidak menampilkan data pada filter aktif."

    insight_card(
        f"Pada 1 tahun terakhir dalam filter aktif, rata-rata ISPU akhir tercatat <b>{format_number(last_val, 1)}</b>, "
        f"dibandingkan periode awal <b>{format_number(first_val, 1)}</b>. Selisihnya <b>{format_number(change, 1)}</b>, sehingga tren terbaru terlihat <b>{direction}</b>. "
        f"Pada grafik historis dengan granularitas <b>{granularity.lower()}</b>, periode dengan rata-rata ISPU tertinggi adalah <b>{period_label(peak_row['periode_plot'], granularity)}</b> dengan nilai <b>{format_number(peak_row['rata_rata_ispu'], 1)}</b>. "
        f"{risk_sentence}"
    )

# ============================================================
# Dashboard 3: Perbandingan Stasiun
# ============================================================
elif menu == "3. Perbandingan Antar Stasiun":
    page_header(
        "3. Perbandingan Kualitas Udara Antar Stasiun",
        "Membandingkan kondisi kualitas udara antar 5 SPKU melalui ranking nilai ISPU, persentase Tidak Sehat+, dan distribusi kategori.",
    )

    # Bagian utama dashboard ini difokuskan pada 1 tahun terakhir dari data terfilter
    # agar perbandingan antar stasiun lebih relevan untuk kebutuhan stakeholder.
    latest_date_station = dff["tanggal"].max()
    station_start_date = latest_date_station - pd.DateOffset(years=1) + pd.DateOffset(days=1)
    station_dff = dff[dff["tanggal"] >= station_start_date].copy()
    if station_dff.empty:
        station_dff = dff.copy()
        station_start_date = dff["tanggal"].min()

    station_summary = (
        station_dff.groupby(["kode_stasiun", "stasiun"], as_index=False)
        .agg(
            rata_rata_ispu=("max", "mean"),
            median_ispu=("max", "median"),
            max_tertinggi=("max", "max"),
            jumlah_catatan=("max", "count"),
            persen_tidak_sehat_plus=("_tidak_sehat_plus", lambda x: x.mean() * 100),
        )
        .sort_values("rata_rata_ispu", ascending=False)
    )
    station_summary["warna_ispu"] = station_summary["rata_rata_ispu"].apply(ispu_threshold_color)
    station_summary["warna_risiko"] = station_summary["persen_tidak_sehat_plus"].apply(risk_percent_color)

    worst_station = station_summary.iloc[0]
    best_station = station_summary.iloc[-1]
    risk_station = station_summary.sort_values("persen_tidak_sehat_plus", ascending=False).iloc[0]

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card(
            "ISPU tertinggi",
            worst_station["kode_stasiun"],
            f"{worst_station['stasiun']} · rata-rata {format_number(worst_station['rata_rata_ispu'], 1)} pada 1 tahun terakhir",
            "🔴",
            "#DC2626",
            "#FEE2E2",
        )
    with c2:
        metric_card(
            "ISPU terendah",
            best_station["kode_stasiun"],
            f"{best_station['stasiun']} · rata-rata {format_number(best_station['rata_rata_ispu'], 1)} pada 1 tahun terakhir",
            "🟢",
            "#16A34A",
            "#DCFCE7",
        )
    with c3:
        metric_card(
            "Risiko tertinggi",
            risk_station["kode_stasiun"],
            f"{format_percent(risk_station['persen_tidak_sehat_plus'], 1)} catatan Tidak Sehat+ pada 1 tahun terakhir",
            "⚠️",
            "#F97316",
            "#FFEDD5",
        )

    mini_note(
        f"KPI utama dihitung dari 1 tahun terakhir dalam rentang "
        f"({pd.to_datetime(station_start_date).strftime('%d %b %Y')} - {pd.to_datetime(latest_date_station).strftime('%d %b %Y')})."
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        with st.container(border=True):
            st.markdown("<div class='chart-title'>Ranking rata-rata ISPU per stasiun</div>", unsafe_allow_html=True)
            st.markdown("<div class='chart-subtitle'>Perbandingan rata-rata ISPU antar stasiun pada 1 tahun terakhir.</div>", unsafe_allow_html=True)
            fig_station = px.bar(
                station_summary,
                x="rata_rata_ispu",
                y="stasiun",
                orientation="h",
                text="rata_rata_ispu",
                height=440,
            )
            fig_station.update_traces(
                texttemplate="%{text:.1f}",
                textposition="outside",
                marker_color=station_summary["warna_ispu"],
                marker_line_width=0,
                cliponaxis=False,
            )
            fig_station.update_layout(
                xaxis_title="Rata-rata ISPU",
                yaxis_title="Stasiun",
                yaxis={"categoryorder": "total ascending"},
                showlegend=False,
            )
            show_plot(apply_common_layout(fig_station))

    with col2:
        with st.container(border=True):
            st.markdown("<div class='chart-title'>Persentase Tidak Sehat+ per stasiun</div>", unsafe_allow_html=True)
            st.markdown("<div class='chart-subtitle'>Proporsi catatan Tidak Sehat atau lebih buruk per stasiun pada 1 tahun terakhir.</div>", unsafe_allow_html=True)
            risk_station_df = station_summary.sort_values("persen_tidak_sehat_plus", ascending=False)
            fig_unhealthy_station = px.bar(
                risk_station_df,
                x="persen_tidak_sehat_plus",
                y="stasiun",
                orientation="h",
                text="persen_tidak_sehat_plus",
                height=440,
            )
            fig_unhealthy_station.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                marker_color=risk_station_df["warna_risiko"],
                marker_line_width=0,
                cliponaxis=False,
            )
            fig_unhealthy_station.update_layout(
                xaxis_title="Persentase Tidak Sehat+ (%)",
                yaxis_title="Stasiun",
                yaxis={"categoryorder": "total ascending"},
                showlegend=False,
            )
            show_plot(apply_common_layout(fig_unhealthy_station))

    with st.container(border=True):
        st.markdown("<div class='chart-title'>Distribusi kategori ISPU per stasiun</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-subtitle'>Komposisi kategori ISPU per stasiun pada 1 tahun terakhir.</div>", unsafe_allow_html=True)
        station_cat = (
            station_dff.groupby(["stasiun", "categori"], as_index=False)
            .size()
            .rename(columns={"size": "jumlah"})
        )
        station_totals = station_cat.groupby("stasiun")["jumlah"].transform("sum")
        station_cat["persentase"] = station_cat["jumlah"] / station_totals * 100
        fig_stack = px.bar(
            station_cat,
            x="stasiun",
            y="persentase",
            color="categori",
            category_orders={"categori": CATEGORY_ORDER},
            color_discrete_map=CATEGORY_COLORS,
            height=520,
        )
        fig_stack.update_layout(
            xaxis_title="Stasiun",
            yaxis_title="Persentase (%)",
            barmode="stack",
            legend_title_text="Kategori ISPU",
            margin=dict(l=18, r=18, t=78, b=48),
        )
        fig_stack = apply_common_layout(fig_stack, legend_title="Kategori ISPU")
        fig_stack.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,
                xanchor="left",
                x=0.0,
                font=dict(size=12, color="#0F172A"),
                bgcolor="rgba(255,255,255,0)",
                borderwidth=0,
                itemwidth=30,
            ),
            legend_title_font=dict(size=12, color="#0F172A"),
            margin=dict(l=18, r=18, t=84, b=48),
        )
        show_plot(fig_stack)

    with st.container(border=True):
        st.markdown("<div class='chart-title'>Tabel ringkasan stasiun</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-subtitle'>Ringkasan statistik 1 tahun terakhir untuk mendukung penentuan lokasi prioritas.</div>", unsafe_allow_html=True)
        display_summary = station_summary.copy()
        display_summary["rata_rata_ispu"] = display_summary["rata_rata_ispu"].round(2)
        display_summary["median_ispu"] = display_summary["median_ispu"].round(2)
        display_summary["persen_tidak_sehat_plus"] = display_summary["persen_tidak_sehat_plus"].round(2)
        display_summary = display_summary[[
            "kode_stasiun",
            "stasiun",
            "rata_rata_ispu",
            "median_ispu",
            "max_tertinggi",
            "jumlah_catatan",
            "persen_tidak_sehat_plus",
        ]]
        display_summary = display_summary.rename(columns={
            "kode_stasiun": "Kode",
            "stasiun": "Stasiun",
            "rata_rata_ispu": "Rata-rata ISPU",
            "median_ispu": "Median ISPU",
            "max_tertinggi": "ISPU Tertinggi",
            "jumlah_catatan": "Jumlah Catatan",
            "persen_tidak_sehat_plus": "Tidak Sehat+ (%)",
        })
        render_html_table(display_summary)

    insight_card(
        f"Pada 1 tahun terakhir dalam filter aktif, stasiun dengan rata-rata ISPU tertinggi adalah <b>{worst_station['stasiun']}</b> dengan rata-rata <b>{format_number(worst_station['rata_rata_ispu'], 1)}</b>. "
        f"Stasiun dengan risiko Tidak Sehat+ tertinggi adalah <b>{risk_station['stasiun']}</b> sebesar <b>{format_percent(risk_station['persen_tidak_sehat_plus'], 1)}</b>. "
        "Hasil ini dapat digunakan untuk menentukan prioritas pengawasan dan intervensi berbasis lokasi."
    )

# ============================================================
# Dashboard 4: Parameter Pencemar Kritis
# ============================================================
elif menu == "4. Parameter Pencemar Kritis":
    page_header(
        "4. Analisis Parameter Pencemar Kritis",
        "Menganalisis parameter yang paling sering menjadi pencemar kritis, termasuk perbandingan antar stasiun dan tren bulanan.",
    )

    available_critical = [c for c in CRITICAL_ORDER if c in dff["critical"].unique()]
    critical_filter = st.multiselect(
        "Filter parameter pencemar kritis",
        options=available_critical,
        default=available_critical,
        format_func=lambda x: CRITICAL_LABELS.get(x, x),
    )
    dcrit = dff[dff["critical"].isin(critical_filter)].copy()
    if dcrit.empty:
        st.warning("Tidak ada data untuk filter parameter pencemar yang dipilih.")
        st.stop()

    # Card KPI dan donut komposisi difokuskan pada 1 tahun terakhir agar relevan untuk stakeholder.
    critical_latest_date = dcrit["tanggal"].max()
    critical_start_date = critical_latest_date - pd.DateOffset(years=1) + pd.DateOffset(days=1)
    dcrit_recent = dcrit[dcrit["tanggal"] >= critical_start_date].copy()
    if dcrit_recent.empty:
        dcrit_recent = dcrit.copy()
        critical_start_date = dcrit["tanggal"].min()

    dominant_pollutant, dominant_count = get_dominant(dcrit_recent["critical"])
    dominant_label = CRITICAL_LABELS.get(dominant_pollutant, dominant_pollutant)
    dominant_pct = dominant_count / len(dcrit_recent) * 100
    critical_unique = dcrit_recent["critical"].nunique()

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Pencemar paling dominan", dominant_label, f"{format_int(dominant_count)} kemunculan pada 1 tahun terakhir.", "🌫️", "#7C3AED", "#F3E8FF")
    with c2:
        metric_card("Kontribusi dominan", format_percent(dominant_pct, 1), "Persentase dari catatan pencemar kritis pada 1 tahun terakhir.", "📊", "#EA580C", "#FFEDD5")
    with c3:
        metric_card("Parameter terpantau", format_int(critical_unique), "Jumlah jenis pencemar kritis yang muncul pada 1 tahun terakhir.", "🧪", "#0891B2", "#CFFAFE")

    mini_note(
        f"KPI utama dihitung dari 1 tahun terakhir dalam rentang "
        f"({pd.to_datetime(critical_start_date).strftime('%d %b %Y')} - {pd.to_datetime(critical_latest_date).strftime('%d %b %Y')})."
    )

    selected_critical_order = [c for c in CRITICAL_ORDER if c in critical_filter]

    # Persentase kemunculan dinormalisasi berdasarkan ketersediaan masing-masing parameter.
    normalized_rows = []
    for critical_name in selected_critical_order:
        pollutant_col = CRITICAL_TO_POLLUTANT_COL.get(critical_name)
        if pollutant_col not in dff.columns:
            continue
        available_mask = dff[pollutant_col].notna()
        available_count = int(available_mask.sum())
        critical_count = int(((dff["critical"] == critical_name) & available_mask).sum())
        first_available = dff.loc[available_mask, "tanggal"].min() if available_count > 0 else pd.NaT
        normalized_rows.append({
            "critical": critical_name,
            "critical_label": CRITICAL_LABELS.get(critical_name, critical_name),
            "jumlah": critical_count,
            "catatan_tersedia": available_count,
            "persentase": (critical_count / available_count * 100) if available_count > 0 else 0,
            "periode_awal": pd.to_datetime(first_available).strftime("%Y-%m-%d") if pd.notna(first_available) else "-",
        })
    critical_norm = pd.DataFrame(normalized_rows)

    crit_counts_recent = dcrit_recent["critical"].value_counts().reindex(CRITICAL_ORDER, fill_value=0).reset_index()
    crit_counts_recent.columns = ["critical", "jumlah"]
    crit_counts_recent = crit_counts_recent[(crit_counts_recent["jumlah"] > 0) & (crit_counts_recent["critical"].isin(selected_critical_order))]
    crit_counts_recent["critical_label"] = crit_counts_recent["critical"].map(CRITICAL_LABELS)

    col1, col2 = st.columns([1.1, 0.9])
    with col1:
        with st.container(border=True):
            st.markdown("<div class='chart-title'>Persentase kemunculan pencemar kritis</div>", unsafe_allow_html=True)
            st.markdown("<div class='chart-subtitle'>Grafik ini menormalkan kemunculan berdasarkan ketersediaan masing-masing parameter.</div>", unsafe_allow_html=True)
            if critical_norm.empty:
                st.info("Tidak ada data ketersediaan parameter untuk filter yang dipilih.")
            else:
                fig_crit_dist = px.bar(
                    critical_norm,
                    x="critical_label",
                    y="persentase",
                    text="persentase",
                    height=440,
                    color="critical",
                    category_orders={"critical": selected_critical_order, "critical_label": [CRITICAL_LABELS[c] for c in selected_critical_order]},
                    color_discrete_map=CRITICAL_COLORS,
                    custom_data=["jumlah", "catatan_tersedia", "periode_awal"],
                )
                fig_crit_dist.update_traces(
                    texttemplate="%{text:.1f}%",
                    textposition="outside",
                    marker_line_width=0,
                    cliponaxis=False,
                    hovertemplate="Parameter=%{x}<br>Persentase=%{y:.1f}%<br>Kemunculan sebagai kritis=%{customdata[0]}<br>Catatan tersedia=%{customdata[1]}<br>Data tersedia sejak=%{customdata[2]}<extra></extra>",
                )
                fig_crit_dist.update_layout(xaxis_title="Parameter", yaxis_title="Persentase kemunculan (%)", showlegend=False)
                show_plot(apply_common_layout(fig_crit_dist))

    with col2:
        with st.container(border=True):
            st.markdown("<div class='chart-title'>Komposisi pencemar kritis</div>", unsafe_allow_html=True)
            st.markdown("<div class='chart-subtitle'>Proporsi masing-masing parameter sebagai pencemar kritis pada 1 tahun terakhir.</div>", unsafe_allow_html=True)
            if crit_counts_recent.empty:
                st.info("Tidak ada data komposisi pencemar kritis pada 1 tahun terakhir.")
            else:
                fig_crit_pie = px.pie(
                    crit_counts_recent,
                    names="critical_label",
                    values="jumlah",
                    hole=0.55,
                    height=440,
                    color="critical",
                    category_orders={"critical": selected_critical_order},
                    color_discrete_map=CRITICAL_COLORS,
                )
                fig_crit_pie.update_traces(textposition="inside", textinfo="percent+label", textfont_size=12)
                fig_crit_pie.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=20))
                show_plot(apply_common_layout(fig_crit_pie))

    with st.container(border=True):
        st.markdown("<div class='chart-title'>Persentase kemunculan pencemar kritis per stasiun</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-subtitle'>Menunjukkan seberapa sering setiap parameter menjadi pencemar kritis pada masing-masing stasiun setelah dinormalisasi berdasarkan ketersediaan data parameter.</div>", unsafe_allow_html=True)

        station_order = sorted(dff["stasiun"].dropna().unique().tolist())
        station_rows = []
        for station_name in station_order:
            station_df = dff[dff["stasiun"] == station_name]
            for critical_name in selected_critical_order:
                pollutant_col = CRITICAL_TO_POLLUTANT_COL.get(critical_name)
                if pollutant_col not in station_df.columns:
                    continue
                available_mask = station_df[pollutant_col].notna()
                available_count = int(available_mask.sum())
                critical_count = int(((station_df["critical"] == critical_name) & available_mask).sum())
                station_rows.append({
                    "stasiun": station_name,
                    "critical": critical_name,
                    "critical_label": CRITICAL_LABELS.get(critical_name, critical_name),
                    "jumlah_kritis": critical_count,
                    "catatan_tersedia": available_count,
                    "persentase": (critical_count / available_count * 100) if available_count > 0 else 0,
                })

        crit_station_norm = pd.DataFrame(station_rows)
        if crit_station_norm.empty:
            st.info("Tidak ada data ketersediaan parameter untuk perbandingan antar stasiun.")
        else:
            fig_crit_station = px.bar(
                crit_station_norm,
                x="stasiun",
                y="persentase",
                color="critical_label",
                barmode="group",
                text="persentase",
                category_orders={
                    "stasiun": station_order,
                    "critical_label": [CRITICAL_LABELS[c] for c in selected_critical_order],
                },
                color_discrete_map={CRITICAL_LABELS[k]: v for k, v in CRITICAL_COLORS.items()},
                height=520,
                custom_data=["jumlah_kritis", "catatan_tersedia"],
            )
            fig_crit_station.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                marker_line_width=0,
                cliponaxis=False,
                hovertemplate="Stasiun=%{x}<br>Parameter=%{fullData.name}<br>Persentase=%{y:.1f}%<br>Kemunculan sebagai kritis=%{customdata[0]}<br>Catatan parameter tersedia=%{customdata[1]}<extra></extra>",
            )
            fig_crit_station.update_layout(
                xaxis_title="Stasiun",
                yaxis_title="Persentase kemunculan (%)",
                legend_title_text="Parameter",
                bargap=0.22,
                bargroupgap=0.08,
            )
            fig_crit_station = apply_common_layout(fig_crit_station, legend_title="Parameter")
            fig_crit_station.update_layout(
                margin=dict(l=18, r=18, t=74, b=42),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.08,
                    xanchor="left",
                    x=0,
                    bgcolor="rgba(255,255,255,0)",
                    borderwidth=0,
                    font=dict(color="#0F172A", size=12),
                    title=dict(font=dict(color="#0F172A", size=12)),
                    entrywidth=110,
                    entrywidthmode="pixels",
                ),
            )
            show_plot(fig_crit_station)

    with st.container(border=True):
        st.markdown("<div class='chart-title'>Tren bulanan pencemar kritis</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-subtitle'>Perubahan frekuensi kemunculan pencemar kritis per bulan.</div>", unsafe_allow_html=True)
        crit_month = dcrit.groupby(["periode_bulanan", "critical"], as_index=False).size().rename(columns={"size": "jumlah"})
        crit_month["periode_plot"] = pd.to_datetime(crit_month["periode_bulanan"].astype(str) + "-01")
        crit_month["critical_label"] = crit_month["critical"].map(CRITICAL_LABELS)
        fig_crit_trend = px.line(
            crit_month,
            x="periode_plot",
            y="jumlah",
            color="critical_label",
            category_orders={"critical_label": [CRITICAL_LABELS[c] for c in selected_critical_order]},
            color_discrete_map={CRITICAL_LABELS[k]: v for k, v in CRITICAL_COLORS.items()},
            height=480,
        )
        fig_crit_trend.update_layout(xaxis_title="Periode bulanan", yaxis_title="Jumlah kemunculan", legend_title_text="Parameter")
        fig_crit_trend = apply_common_layout(fig_crit_trend, legend_title="Parameter")
        fig_crit_trend.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,
                xanchor="left",
                x=0,
                bgcolor="rgba(255,255,255,0)",
                borderwidth=0,
                font=dict(color="#0F172A", size=12),
                title=dict(font=dict(color="#0F172A", size=12)),
            ),
            margin=dict(l=18, r=18, t=74, b=42),
        )
        show_plot(fig_crit_trend)

    insight_card(
        f"Pada 1 tahun terakhir dalam filter aktif, parameter pencemar kritis paling dominan adalah <b>{dominant_label}</b> dengan kontribusi <b>{format_percent(dominant_pct, 1)}</b>. "
        "Perbandingan berbasis persentase membantu melihat dominansi pencemar secara lebih adil, baik antar parameter maupun antar stasiun."
    )

# ============================================================
# Dashboard 5: Pola Musiman
# ============================================================
elif menu == "5. Pola Musiman Kualitas Udara":
    page_header(
        "5. Pola Musiman Kualitas Udara",
        "Mengidentifikasi bulan dan periode yang cenderung memiliki kualitas udara lebih buruk untuk mendukung kesiapsiagaan operasional.",
    )

    # Agregasi dibuat berdasarkan kode bulan, lalu nama bulan ditambahkan kembali.
    # Ini menghindari error pandas saat groupby memakai kolom categorical nama_bulan
    # dengan kombinasi tahun-bulan yang tidak lengkap pada data terfilter.
    seasonal = (
        dff.groupby(["tahun", "bulan"], as_index=False)
        .agg(
            rata_rata_ispu=("max", "mean"),
            median_ispu=("max", "median"),
            persen_tidak_sehat_plus=("_tidak_sehat_plus", lambda x: x.mean() * 100),
            jumlah_catatan=("max", "count"),
        )
        .sort_values(["tahun", "bulan"])
    )
    seasonal["nama_bulan"] = seasonal["bulan"].map(dict(enumerate(MONTH_ORDER, start=1)))
    seasonal["nama_bulan"] = pd.Categorical(seasonal["nama_bulan"], categories=MONTH_ORDER, ordered=True)

    monthly_pattern = (
        dff.groupby(["bulan"], as_index=False)
        .agg(
            rata_rata_ispu=("max", "mean"),
            persen_tidak_sehat_plus=("_tidak_sehat_plus", lambda x: x.mean() * 100),
            jumlah_catatan=("max", "count"),
        )
        .sort_values("bulan")
    )
    monthly_pattern["nama_bulan"] = monthly_pattern["bulan"].map(dict(enumerate(MONTH_ORDER, start=1)))
    monthly_pattern["bulan_label"] = monthly_pattern["nama_bulan"].astype(str)
    monthly_pattern["nama_bulan"] = pd.Categorical(monthly_pattern["nama_bulan"], categories=MONTH_ORDER, ordered=True)
    monthly_pattern["warna_ispu"] = monthly_pattern["rata_rata_ispu"].apply(ispu_threshold_color)
    monthly_pattern["warna_risiko"] = monthly_pattern["persen_tidak_sehat_plus"].apply(risk_percent_color)

    # KPI musiman difokuskan pada 1 tahun terakhir dari data terfilter,
    # agar card utama menunjukkan kondisi/pola terkini untuk stakeholder.
    latest_date_seasonal = dff["tanggal"].max()
    seasonal_kpi_start_date = latest_date_seasonal - pd.DateOffset(years=1) + pd.DateOffset(days=1)
    seasonal_kpi_dff = dff[dff["tanggal"] >= seasonal_kpi_start_date].copy()
    if seasonal_kpi_dff.empty:
        seasonal_kpi_dff = dff.copy()
        seasonal_kpi_start_date = dff["tanggal"].min()

    monthly_pattern_kpi = (
        seasonal_kpi_dff.groupby(["bulan"], as_index=False)
        .agg(
            rata_rata_ispu=("max", "mean"),
            persen_tidak_sehat_plus=("_tidak_sehat_plus", lambda x: x.mean() * 100),
            jumlah_catatan=("max", "count"),
        )
        .sort_values("bulan")
    )
    monthly_pattern_kpi["nama_bulan"] = monthly_pattern_kpi["bulan"].map(dict(enumerate(MONTH_ORDER, start=1)))
    monthly_pattern_kpi["nama_bulan"] = pd.Categorical(monthly_pattern_kpi["nama_bulan"], categories=MONTH_ORDER, ordered=True)

    worst_month = monthly_pattern_kpi.loc[monthly_pattern_kpi["rata_rata_ispu"].idxmax()]
    best_month = monthly_pattern_kpi.loc[monthly_pattern_kpi["rata_rata_ispu"].idxmin()]
    highest_risk_month = monthly_pattern_kpi.loc[monthly_pattern_kpi["persen_tidak_sehat_plus"].idxmax()]
    seasonal_kpi_period_label = f"{pd.to_datetime(seasonal_kpi_start_date).strftime('%d %b %Y')} - {pd.to_datetime(latest_date_seasonal).strftime('%d %b %Y')}"

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Bulan ISPU tertinggi", str(worst_month["nama_bulan"]), f"Rata-rata ISPU {format_number(worst_month['rata_rata_ispu'], 1)} · 1 tahun terakhir", "🔴", "#DC2626", "#FEE2E2")
    with c2:
        metric_card("Bulan ISPU terendah", str(best_month["nama_bulan"]), f"Rata-rata ISPU {format_number(best_month['rata_rata_ispu'], 1)} · 1 tahun terakhir", "🟢", "#16A34A", "#DCFCE7")
    with c3:
        metric_card("Risiko bulanan tertinggi", str(highest_risk_month["nama_bulan"]), f"Tidak Sehat+ {format_percent(highest_risk_month['persen_tidak_sehat_plus'], 1)} · 1 tahun terakhir", "⚠️", "#F97316", "#FFEDD5")

    mini_note(f"KPI utama dihitung dari 1 tahun terakhir dalam rentang ({seasonal_kpi_period_label}).")

    with st.container(border=True):
        st.markdown("<div class='chart-title'>Heatmap rata-rata ISPU bulanan per tahun</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-subtitle'>Warna lebih merah menunjukkan rata-rata ISPU lebih tinggi pada bulan dan tahun tersebut.</div>", unsafe_allow_html=True)
        heatmap_data = seasonal.pivot_table(
            index="tahun",
            columns="nama_bulan",
            values="rata_rata_ispu",
            aggfunc="mean",
            observed=True,
        ).reindex(columns=MONTH_ORDER)
        fig_heat = px.imshow(
            heatmap_data,
            aspect="auto",
            labels=dict(x="Bulan", y="Tahun", color="Rata-rata ISPU"),
            color_continuous_scale="YlOrRd",
            height=540,
        )
        fig_heat.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Tahun",
            coloraxis_colorbar=dict(
                title=dict(text="ISPU", font=dict(color="#0F172A", size=14)),
                tickfont=dict(color="#0F172A", size=12),
                bgcolor="rgba(255,255,255,0.88)",
                outlinewidth=0,
            ),
        )
        show_plot(apply_common_layout(fig_heat))

    col1, col2 = st.columns([1, 1])
    with col1:
        with st.container(border=True):
            st.markdown("<div class='chart-title'>Rata-rata ISPU per bulan kalender</div>", unsafe_allow_html=True)
            st.markdown("<div class='chart-subtitle'>Rata-rata lintas tahun untuk melihat pola bulanan berulang.</div>", unsafe_allow_html=True)
            fig_month_avg = px.bar(
                monthly_pattern,
                x="bulan_label",
                y="rata_rata_ispu",
                text="rata_rata_ispu",
                height=440,
            )
            fig_month_avg.update_traces(
                texttemplate="%{text:.1f}",
                textposition="outside",
                marker_color=monthly_pattern["warna_ispu"],
                marker_line_width=0,
                cliponaxis=False,
            )
            fig_month_avg.update_layout(xaxis_title="Bulan", yaxis_title="Rata-rata ISPU", showlegend=False)
            show_plot(apply_common_layout(fig_month_avg))

    with col2:
        with st.container(border=True):
            st.markdown("<div class='chart-title'>Persentase Tidak Sehat+ per bulan</div>", unsafe_allow_html=True)
            st.markdown("<div class='chart-subtitle'>Mengukur seberapa sering kategori Tidak Sehat atau lebih buruk muncul pada setiap bulan kalender.</div>", unsafe_allow_html=True)
            fig_month_bad = px.bar(
                monthly_pattern,
                x="bulan_label",
                y="persen_tidak_sehat_plus",
                text="persen_tidak_sehat_plus",
                height=440,
            )
            fig_month_bad.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                marker_color=monthly_pattern["warna_risiko"],
                marker_line_width=0,
                cliponaxis=False,
            )
            fig_month_bad.update_layout(xaxis_title="Bulan", yaxis_title="Persentase Tidak Sehat+ (%)", showlegend=False)
            show_plot(apply_common_layout(fig_month_bad))

    with st.container(border=True):
        st.markdown("<div class='chart-title'>Tabel pola bulanan</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-subtitle'>Ringkasan angka untuk mendukung interpretasi pola musiman.</div>", unsafe_allow_html=True)
        monthly_display = monthly_pattern.copy()
        monthly_display["rata_rata_ispu"] = monthly_display["rata_rata_ispu"].round(2)
        monthly_display["persen_tidak_sehat_plus"] = monthly_display["persen_tidak_sehat_plus"].round(2)
        monthly_display = monthly_display.rename(columns={
            "bulan": "No Bulan",
            "nama_bulan": "Bulan",
            "rata_rata_ispu": "Rata-rata ISPU",
            "persen_tidak_sehat_plus": "Tidak Sehat+ (%)",
            "jumlah_catatan": "Jumlah Catatan",
        })
        monthly_display = monthly_display[["No Bulan", "Bulan", "Rata-rata ISPU", "Tidak Sehat+ (%)", "Jumlah Catatan"]]
        render_html_table(monthly_display)

    insight_card(
        f"Pada 1 tahun terakhir dari data terfilter, bulan dengan rata-rata ISPU tertinggi adalah <b>{worst_month['nama_bulan']}</b> dengan nilai <b>{format_number(worst_month['rata_rata_ispu'], 1)}</b>. "
        f"Bulan dengan rata-rata ISPU terendah adalah <b>{best_month['nama_bulan']}</b> dengan nilai <b>{format_number(best_month['rata_rata_ispu'], 1)}</b>. "
        "Pola ini dapat digunakan sebagai dasar kesiapsiagaan operasional pada periode rawan, dengan catatan bahwa interpretasi musim bersifat indikatif karena dataset tidak memuat variabel meteorologi langsung."
    )
