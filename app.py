import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Manuals Executive Dashboard", layout="wide")

# -------------------------------------------------
# EXECUTIVE STYLE
# -------------------------------------------------
st.markdown("""
<style>
.metric-card {
    padding: 18px;
    border-radius: 12px;
    background: #ffffff;
    border: 1px solid #e6e9ef;
    text-align: center;
    color: #111111;
}
.big-metric {
    font-size: 34px;
    font-weight: 700;
    color: #111111;
}
.metric-label {
    font-size: 14px;
    color: #444444;
}
.manual-card {
    background:#ffffff;
    color:#111111;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# LOAD DATA — FROM SHAREPOINT URL
# -------------------------------------------------
st.sidebar.markdown("### 📂 Data Source")

EXCEL_URL = "https://marcconsultores.sharepoint.com/:x:/s/Proyectos2025-BancobunqMxico/IQD28Ssy0nUrS7oX2ylJaDgfAYAeqPvUDNgO_KbFxreLwuk?download=1"

@st.cache_data(ttl=300)
def load_data():

    df = pd.read_excel(
        EXCEL_URL,
        sheet_name="02_Req_Register"
    )

    df = df.drop(columns=[c for c in df.columns if "Unnamed" in c])
    df = df[df["Manual Name"] != "Cross-cutting Annex"]

    return df

if st.sidebar.button("🔄 Refresh data"):
    load_data.clear()

try:
    df = load_data()
    st.sidebar.success("✅ Excel conectado")
except Exception as e:
    st.error("❌ No se pudo cargar el Excel desde SharePoint")
    st.write(e)
    st.stop()

# -------------------------------------------------
# STATUS MODEL
# -------------------------------------------------
status_weights = {
    "Not started": 0,
    "Applies partially": 0.5,
    "QA": 0.9,
    "Final": 1
}

status_order = ["Not started", "Applies partially", "QA", "Final"]

status_colors = {
    "Not started": "#d62728",
    "Applies partially": "#ff7f0e",
    "QA": "#f2c94c",
    "Final": "#2ca02c"
}

df["progress_weight"] = df["Status"].map(status_weights).fillna(0)

# -------------------------------------------------
# LANGUAGE
# -------------------------------------------------
st.sidebar.header("⚙️ Settings")
lang_es = st.sidebar.toggle("🇪🇸 Español", value=False)
LANG = "ES" if lang_es else "EN"

T = {
    "title": "📘 Manuals Executive Progress Dashboard",
    "filters": "Filters",
    "type": "Manual type",
    "status": "Status",
    "manual": "Manual",
    "all": "All",
    "committee": "👔 Committee mode",
    "kpi_total": "Total Requirements",
    "kpi_final": "Final %",
    "kpi_qa": "QA %",
    "kpi_weighted": "Weighted Progress",
    "gauge": "Executive Overall Progress",
    "completion": "Completion",
    "progress_manual": "Progress by Manual",
    "status_dist": "Global Status Distribution",
    "status_breakdown": "Status Breakdown by Manual (%)",
    "action_table": "🚀 Focus Action Table — Non Final Items",
    "download": "⬇️ Download Focus Items",
    "active_filters": "Active filters"
}

if LANG == "ES":
    T.update({
        "title": "📘 Dashboard Ejecutivo de Avance de Manuales",
        "filters": "Filtros",
        "type": "Tipo de manual",
        "status": "Estatus",
        "manual": "Manual",
        "all": "Todos",
        "committee": "👔 Modo Comité",
        "kpi_total": "Total Requerimientos",
        "kpi_final": "% Final",
        "kpi_qa": "% QA",
        "kpi_weighted": "Avance Ponderado",
        "gauge": "Avance Ejecutivo Global",
        "completion": "Avance",
        "progress_manual": "Avance por Manual",
        "status_dist": "Distribución Global de Estatus",
        "status_breakdown": "Distribución de Estatus por Manual (%)",
        "action_table": "🚀 Tabla de Acción — No Final",
        "download": "⬇️ Descargar Pendientes",
        "active_filters": "Filtros activos"
    })

# -------------------------------------------------
# TRANSLATIONS
# -------------------------------------------------
manual_translate = {
    "AML/CTF Manual": "Manual de Cumplimiento PLD/FT",
    "Accounting and Financial Policies Manual": "Manual de Políticas Contables y Financieras",
    "Code of Ethics": "Código de Ética",
    "Comprehensive Risk Management Manual": "Manual de Gestión Integral de Riesgos",
    "Credit Manual": "Manual de Crédito",
    "Internal Control Manual": "Manual de Control Interno",
    "Manual of Funding Product Policies and Guidelines": "Manual de Políticas y Lineamientos de Productos de Captación",
    "Organization and Job Description Manual": "Manual de Organización y Descripción de Puestos",
    "Treasury Manual": "Manual de Tesorería"
}

def manual_label(name):
    return manual_translate.get(name, name) if LANG == "ES" else name

type_translate = {
    "Auth-ready": {"EN": "Auth-ready", "ES": "Listo para autorización"},
    "Pre-op": {"EN": "Pre-op", "ES": "Pre-operativo"}
}

# -------------------------------------------------
# FILTERS
# -------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.header(T["filters"])

type_raw = df["Auth-ready vs Pre-op"].dropna().unique().tolist()
type_labels = []
type_lookup = {}

for t in type_raw:
    lab = type_translate.get(t, {}).get(LANG, t)
    type_labels.append(lab)
    type_lookup[lab] = t

selected_type_label = st.sidebar.radio(T["type"], [T["all"]] + type_labels)
selected_status = st.sidebar.radio(T["status"], [T["all"]] + status_order)

manual_raw = sorted(df["Manual Name"].dropna().unique())
manual_labels = [manual_label(m) for m in manual_raw]
manual_lookup = dict(zip(manual_labels, manual_raw))

selected_manual_label = st.sidebar.radio(T["manual"], [T["all"]] + manual_labels)

st.sidebar.markdown("---")
view_mode = st.sidebar.toggle(T["committee"], value=False)

# -------------------------------------------------
# APPLY FILTERS
# -------------------------------------------------
df_f = df.copy()

if selected_type_label != T["all"]:
    df_f = df_f[df_f["Auth-ready vs Pre-op"] == type_lookup[selected_type_label]]

if selected_status != T["all"]:
    df_f = df_f[df_f["Status"] == selected_status]

if selected_manual_label != T["all"]:
    df_f = df_f[df_f["Manual Name"] == manual_lookup[selected_manual_label]]

# -------------------------------------------------
# TITLE
# -------------------------------------------------
title = T["title"] + (" — COMITÉ" if view_mode and LANG=="ES" else " — COMMITTEE VIEW" if view_mode else "")
st.title(title)

# -------------------------------------------------
# KPIs
# -------------------------------------------------
total_req = len(df_f)
pct_final = (df_f["Status"]=="Final").mean()*100 if total_req else 0
pct_qa = (df_f["Status"]=="QA").mean()*100 if total_req else 0
overall_weighted = df_f["progress_weight"].mean()*100 if total_req else 0

def card(label, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="big-metric">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

k1,k2,k3,k4 = st.columns(4)
with k1: card(T["kpi_weighted"], f"{overall_weighted:.1f}%")
with k2: card(T["kpi_final"], f"{pct_final:.1f}%")
with k3: card(T["kpi_qa"], f"{pct_qa:.1f}%")
with k4: card(T["kpi_total"], total_req)

# -------------------------------------------------
# GAUGE
# -------------------------------------------------
st.subheader("🎯 " + T["gauge"])
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=overall_weighted,
    gauge={'axis': {'range': [0,100]}}
))
st.plotly_chart(fig_gauge, use_container_width=True)
