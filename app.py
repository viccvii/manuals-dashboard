import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Manuals Executive Dashboard",
    layout="wide"
)


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
# LOAD DATA — FROM UPLOAD
# -------------------------------------------------
st.sidebar.markdown("### 📂 Data Source")

uploaded = st.sidebar.file_uploader(
    "Upload tracking Excel",
    type=["xlsx"]
)


@st.cache_data(ttl=300)
def load_data(file):
    df = pd.read_excel(
        file,
        sheet_name="02_Req_Register"
    )

    df = df.drop(columns=[c for c in df.columns if "Unnamed" in c])

    # Exclude cross cutting
    df = df[df["Manual Name"] != "Cross-cutting Annex"]

    return df


if uploaded is None:
    st.warning("⬅️ Upload the tracking Excel file to start")
    st.stop()

df = load_data(uploaded)


# -------------------------------------------------
# STATUS MODEL
# -------------------------------------------------
status_weights = {
    "Not started": 0,
    "Mapped": 0.3,
    "QA": 0.6,
    "In bunq review": 0.85,
    "Final": 1
}

status_order = [
    "Not started",
    "Mapped",
    "QA",
    "In bunq review",
    "Final"
]

status_colors = {
    "Not started": "#d62728",
    "Mapped": "#ff7f0e",
    "QA": "#f2c94c",
    "In bunq review": "#4dabf7",
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

selected_type_label = st.sidebar.radio(
    T["type"],
    [T["all"]] + type_labels
)

selected_status = st.sidebar.radio(
    T["status"],
    [T["all"]] + status_order
)

manual_raw = sorted(df["Manual Name"].dropna().unique())
manual_labels = [manual_label(m) for m in manual_raw]
manual_lookup = dict(zip(manual_labels, manual_raw))

selected_manual_label = st.sidebar.radio(
    T["manual"],
    [T["all"]] + manual_labels
)

st.sidebar.markdown("---")
view_mode = st.sidebar.toggle(T["committee"], value=False)


# -------------------------------------------------
# APPLY FILTERS
# -------------------------------------------------
df_f = df.copy()

if selected_type_label != T["all"]:
    df_f = df_f[
        df_f["Auth-ready vs Pre-op"] ==
        type_lookup[selected_type_label]
    ]

if selected_status != T["all"]:
    df_f = df_f[df_f["Status"] == selected_status]

if selected_manual_label != T["all"]:
    df_f = df_f[
        df_f["Manual Name"] ==
        manual_lookup[selected_manual_label]
    ]


# -------------------------------------------------
# TITLE + ACTIVE FILTERS
# -------------------------------------------------
title = T["title"]

if view_mode:
    title += " — COMITÉ" if LANG == "ES" else " — COMMITTEE VIEW"

st.title(title)

active = [
    x for x in
    [selected_type_label, selected_status, selected_manual_label]
    if x != T["all"]
]

if active:
    st.caption(
        f"🔎 {T['active_filters']}: " + " | ".join(active)
    )


# -------------------------------------------------
# KPIs EXECUTIVE CARDS (EXPANDED)
# -------------------------------------------------

total_req = len(df_f)

status_summary = (
    df_f["Status"]
    .value_counts()
    .reindex(status_order, fill_value=0)
)

status_pct = (
    status_summary / total_req * 100
    if total_req else status_summary
)

remaining_req = total_req - status_summary["Final"]
overall_weighted = (
    df_f["progress_weight"].mean() * 100
    if total_req else 0
)


def card(label, value, color=None):
    border = f"border-top:6px solid {color};" if color else ""
    st.markdown(f"""
    <div class="metric-card" style="{border}">
        <div class="big-metric">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


# -------- Row 1 (Executive KPIs)
k1, k2, k3 = st.columns(3)

with k1:
    card("Weighted Progress", f"{overall_weighted:.1f}%")

with k2:
    card("Total Requirements", total_req)

with k3:
    card("Remaining (Non Final)", remaining_req)


# -------- Row 2 (Status Breakdown)
st.markdown("### Status Overview")

cols = st.columns(len(status_order))

for i, status in enumerate(status_order):
    with cols[i]:
        card(
            f"{status}",
            f"{status_pct[status]:.1f}%  \n({status_summary[status]})",
            status_colors.get(status)
        )


# -------------------------------------------------
# GAUGE + PIE
# -------------------------------------------------
c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("🎯 " + T["gauge"])

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_weighted,
        gauge={'axis': {'range': [0, 100]}}
    ))

    st.plotly_chart(fig_gauge, use_container_width=True)

with c2:
    st.subheader("📊 " + T["status_dist"])

    status_dist = df_f["Status"].value_counts().reset_index()
    status_dist.columns = ["Status", "Count"]

    fig_pie = px.pie(
        status_dist,
        names="Status",
        values="Count",
        color="Status",
        color_discrete_map=status_colors
    )

    st.plotly_chart(fig_pie, use_container_width=True)


# -------------------------------------------------
# PROGRESS PER MANUAL (ONLY WHEN ALL MANUALS)
# -------------------------------------------------
if selected_manual_label == T["all"]:

    progress = (
        df_f.groupby("Manual Name")
        .agg(
            total=("Req ID", "count"),
            weighted=("progress_weight", "mean")
        )
        .reset_index()
    )

    progress["pct"] = progress["weighted"] * 100
    progress["Manual Label"] = progress["Manual Name"].apply(manual_label)

    st.subheader("📘 " + T["progress_manual"])

    for _, row in progress.iterrows():

        color = (
            "#2ca02c" if row.pct >= 80
            else "#ff7f0e" if row.pct >= 50
            else "#d62728"
        )

        st.markdown(f"""
        <div class="manual-card"
             style="border-left:8px solid {color};
                    padding:14px;
                    margin-bottom:10px;
                    border-radius:10px;
                    border:1px solid #e6e9ef;">
            <h4>{row['Manual Label']}</h4>
            <b>{T["completion"]}: {row.pct:.1f}%</b>
        </div>
        """, unsafe_allow_html=True)

        st.progress(row.pct / 100)


# -------------------------------------------------
# STACKED STATUS (ONLY WHEN ALL MANUALS)
# -------------------------------------------------
if selected_manual_label == T["all"]:

    st.subheader("📊 " + T["status_breakdown"])

    stack = (
        df_f.groupby(["Manual Name", "Status"])
        .size()
        .reset_index(name="count")
    )

    stack["Manual Label"] = stack["Manual Name"].apply(manual_label)

    stack["pct"] = (
        stack["count"] /
        stack.groupby("Manual Name")["count"].transform("sum")
    ) * 100

    fig_stack = px.bar(
        stack,
        y="Manual Label",
        x="pct",
        color="Status",
        orientation="h",
        barmode="stack",
        color_discrete_map=status_colors,
        text="pct"
    )

    fig_stack.update_traces(texttemplate='%{text:.1f}%')
    fig_stack.update_layout(
        height=120 + 45 * len(stack["Manual Label"].unique())
    )

    st.plotly_chart(fig_stack, use_container_width=True)


# -------------------------------------------------
# ACTION TABLE
# -------------------------------------------------
if not view_mode:

    st.subheader(T["action_table"])

    pending = df_f[df_f["Status"] != "Final"].copy()
    pending["Manual"] = pending["Manual Name"].apply(manual_label)

    show_cols = [
        "Manual",
        "Content Element",
        "Requirement (minimum content)",
        "Status",
        "Comments (SPANISH)"
    ]

    st.dataframe(
        pending[show_cols],
        use_container_width=True
    )

    csv = pending.to_csv(index=False).encode("utf-8")

    st.download_button(
        T["download"],
        csv,
        "focus_items.csv",
        "text/csv"
    )

