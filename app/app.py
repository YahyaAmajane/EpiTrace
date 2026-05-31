"""
EPI-TRACE — Système d'Alerte Épidémiologique Précoce
Centre de Commandement Hospitalier — Île-de-France
ENSAM Meknès — IATD-SI  |  v3.0 Production
"""

import streamlit as st
import pandas as pd
import numpy as np
import os, sys
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime

# ── Chemins & Imports ──────────────────────────────────────────────────────────
chemin_racine = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if chemin_racine not in sys.path:
    sys.path.append(chemin_racine)

from app_utils import (load_ml_assets, get_latest_data,
                       predict_standard_forecast, predict_cascade_nowcast)
try:
    from src.agent_llm import generer_bulletin_alerte
except ModuleNotFoundError:
    try:
        sys.path.append(os.path.dirname(__file__))
        from agent_llm import generer_bulletin_alerte
    except ModuleNotFoundError:
        def generer_bulletin_alerte(*args, **kwargs):
            return "⚠️ Module agent_llm non trouvé. Vérifiez le chemin du fichier."

# ══════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURATION PAGE
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Epi-Trace | Commandement Hospitalier",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
# 2. CSS — THÈME "SALLE DE COMMANDEMENT" PREMIUM
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;600&family=Syne:wght@400;700;800&display=swap');

:root {
    --bg-void:       #04070F;
    --bg-deep:       #070D1C;
    --bg-surface:    #0C1425;
    --bg-card:       #101C30;
    --bg-card-hover: #142238;
    --bg-input:      #0A1220;
    --cyan:          #00C6FF;
    --cyan-dim:      rgba(0,198,255,0.12);
    --cyan-glow:     rgba(0,198,255,0.25);
    --blue:          #0057FF;
    --blue-dim:      rgba(0,87,255,0.1);
    --green:         #00E5A0;
    --green-dim:     rgba(0,229,160,0.1);
    --orange:        #FF9500;
    --orange-dim:    rgba(255,149,0,0.1);
    --red:           #FF3054;
    --red-dim:       rgba(255,48,84,0.1);
    --text-h:        #EFF4FF;
    --text-p:        #7D94B8;
    --text-dim:      #3D5070;
    --border:        rgba(255,255,255,0.06);
    --border-bright: rgba(0,198,255,0.2);
    --radius:        14px;
    --radius-sm:     8px;
}

/* ── RESET ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
.stApp {
    background: var(--bg-void) !important;
    font-family: 'Space Grotesk', sans-serif;
}
.main .block-container {
    padding: 1.5rem 2rem !important;
    max-width: 100% !important;
}

/* Fix du texte brut de l'icône de fermeture de sidebar natif de Streamlit */
[data-testid="collapsedControl"] svg { width: 1.5rem; height: 1.5rem; color: var(--text-p); }
[data-testid="collapsedControl"] { color: transparent !important; }

/* ── SIDEBAR ────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-deep) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: var(--text-p) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.88rem !important;
}

/* ── TYPOGRAPHIE ────────────────────────────────────── */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    color: var(--text-h) !important;
    letter-spacing: -0.02em;
}
h1 { font-size: 1.9rem !important; line-height: 1.1; }
h2 { font-size: 1.15rem !important; color: var(--cyan) !important; }
h3 { font-size: 0.95rem !important; }
p, span, label, li { font-family: 'Space Grotesk', sans-serif !important; color: var(--text-p) !important; }

/* ── METRICS ─────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.1rem 1.4rem !important;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}
[data-testid="metric-container"]:hover {
    border-color: var(--border-bright) !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,198,255,0.08);
}
[data-testid="metric-container"]::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, var(--blue-dim), transparent 60%);
    pointer-events: none;
}
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    color: var(--text-h) !important;
    font-size: 1.5rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-p) !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}
[data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ── BOUTONS ─────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #003ECC, var(--blue)) !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.05em;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.65rem 1.8rem !important;
    transition: all 0.25s ease;
    box-shadow: 0 0 0 1px rgba(0,87,255,0.3);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(0,87,255,0.4) !important;
    background: linear-gradient(135deg, var(--blue), var(--cyan)) !important;
}

/* ── TABS ────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-surface) !important;
    border-radius: var(--radius) !important;
    padding: 5px !important;
    gap: 3px;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-p) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-card) !important;
    color: var(--cyan) !important;
    box-shadow: 0 0 0 1px var(--border-bright) !important;
}

/* ── SELECT / RADIO ──────────────────────────────────── */
.stSelectbox > div > div,
.stRadio > div {
    background: var(--bg-input) !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
}
.stSelectbox label, .stRadio label {
    color: var(--text-p) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── SLIDERS ─────────────────────────────────────────── */
.stSlider > div { padding: 0.3rem 0 !important; }
.stSlider [data-testid="stTickBar"] { color: var(--text-dim) !important; }

/* ── DATAFRAME ───────────────────────────────────────── */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden;
}
.stDataFrame [data-testid="stDataFrameResizable"] { background: var(--bg-card) !important; }

/* ── ALERTS ──────────────────────────────────────────── */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: var(--radius-sm) !important;
    border: none !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.9rem !important;
}

/* ── DIVIDER ─────────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

/* ═══════════════════════════════════════════════════════
   COMPOSANTS PERSONNALISÉS
═══════════════════════════════════════════════════════ */

/* ─ Header Band ─ */
.hdr-band {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.2rem 1.8rem;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 1.5rem;
}
.hdr-logo {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.6rem;
    color: var(--text-h);
    letter-spacing: -0.03em;
}
.hdr-logo span { color: var(--cyan); }
.hdr-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ─ Status Pill ─ */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0.5rem 1.1rem;
    border-radius: 50px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.pill-green  { background: var(--green-dim);  border: 1px solid var(--green);  color: var(--green);  }
.pill-orange { background: var(--orange-dim); border: 1px solid var(--orange); color: var(--orange); }
.pill-red    { background: var(--red-dim);    border: 1px solid var(--red);    color: var(--red);    }

/* ─ Section Label ─ */
.sec-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--cyan);
    text-transform: uppercase;
    letter-spacing: 0.22em;
    margin-bottom: 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ─ Info Box ─ */
.info-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.4rem;
    margin-bottom: 1rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    color: var(--text-p);
    line-height: 1.65;
}
.info-box .hl { color: var(--cyan); font-weight: 600; }

/* ─ Arch Diagram ─ */
.arch-flow {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}
.arch-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.8rem 1.5rem;
    border-radius: var(--radius-sm);
    min-width: 120px;
    text-align: center;
}
.arch-node .label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 5px;
}
.arch-node .value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
}
.arch-arrow {
    color: var(--text-dim);
    font-size: 1.5rem;
}
.node-data   { background: rgba(0,87,255,0.12);  border: 1px solid rgba(0,87,255,0.3);  }
.node-model  { background: rgba(0,198,255,0.1);  border: 1px solid rgba(0,198,255,0.25); }
.node-output { background: rgba(0,229,160,0.1);  border: 1px solid rgba(0,229,160,0.25); }
.node-now    { background: rgba(255,149,0,0.1);  border: 1px solid rgba(255,149,0,0.3);  }

/* ─ Nowcast Box ─ */
.nowcast-panel {
    background: var(--bg-card);
    border: 1px solid var(--orange);
    border-radius: var(--radius);
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
}
.nowcast-panel .title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    color: var(--orange);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.8rem;
}

/* ─ Feature Row ─ */
.feat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.45rem 0;
    border-bottom: 1px solid var(--border);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.88rem;
}
.feat-row:last-child { border-bottom: none; }
.feat-name { color: var(--text-p); }
.feat-val  { font-family: 'JetBrains Mono', monospace; color: var(--text-h); font-size: 0.85rem; }

/* ─ Model Badge ─ */
.model-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--cyan-dim);
    border: 1px solid var(--border-bright);
    border-radius: 6px;
    padding: 0.3rem 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--cyan);
    letter-spacing: 0.05em;
}

/* ─ Corr Card ─ */
.corr-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 12px;
}
.corr-icon { font-size: 1.4rem; }
.corr-name { font-family: 'Space Grotesk', sans-serif; font-size: 0.82rem; color: var(--text-p); }
.corr-val  { font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; font-weight: 600; margin-top: 2px; }

/* ─ Bulletin Box ─ */
.bulletin {
    background: var(--bg-card);
    border: 1px solid var(--border-bright);
    border-radius: var(--radius);
    padding: 1.8rem;
    margin-top: 1rem;
    font-family: 'Space Grotesk', sans-serif;
    line-height: 1.7;
}
.bulletin h3 { color: var(--cyan) !important; font-size: 1rem !important; margin: 1rem 0 0.5rem; }
.bulletin p  { color: var(--text-p) !important; font-size: 0.9rem !important; }

/* ─ Scenario tag ─ */
.scenario-delta {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 30px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 600;
}
.delta-up   { background: var(--red-dim);   color: var(--red);   border: 1px solid var(--red);   }
.delta-down { background: var(--green-dim); color: var(--green); border: 1px solid var(--green); }
.delta-flat { background: var(--cyan-dim);  color: var(--cyan);  border: 1px solid var(--cyan);  }

/* ─ Sidebar logo ─ */
.sidebar-logo {
    text-align: center;
    padding: 1.2rem 0 1rem;
}
.sidebar-logo .name {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.5rem;
    color: var(--cyan);
    letter-spacing: -0.02em;
}
.sidebar-logo .sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-dim);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 3px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 3. CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════
FEATURE_COLUMNS = [
    'inc', 'temperature_2m', 'relative_humidity_2m',
    'Topic_Toux', 'Topic_Grippe', 'Topic_Fievre', 'ratio_vacances'
]
ALL_FEATURES_LABELS = {
    'inc':                  'Incidence Sentinelles',
    'temperature_2m':       'Température (°C)',
    'relative_humidity_2m': 'Humidité relative (%)',
    'Topic_Toux':           'Google — "Toux"',
    'Topic_Grippe':         'Google — "Grippe"',
    'Topic_Fievre':         'Google — "Fièvre"',
    'ratio_vacances':       'Ratio Vacances',
}
LOOKBACK     = 12
# Seuils calibrés sur les percentiles réels IDF 2021–2026 (n=277 semaines)
SEUIL_N2 = 14206   # P50 — Médiane : début de tension
SEUIL_N3 = 20076   # P75 — 3e quartile : Plan Blanc
SEUIL_N4 = 26866   # P85 — Seuil de crise régionale
SEUIL_ALERTE = SEUIL_N4  # Alias pour compatibilité du code existant
RMSE_FORECAST = 4116
R2_FORECAST   = 0.73
R2_NOWCAST    = 0.85

PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#7D94B8', family='Space Grotesk', size=11),
    margin=dict(l=0, r=10, t=40, b=0),
    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)',
               zeroline=False, linecolor='rgba(255,255,255,0.06)',
               tickfont=dict(size=10)),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)',
               zeroline=False, linecolor='rgba(255,255,255,0.06)',
               tickfont=dict(size=10)),
)

# ══════════════════════════════════════════════════════════════════════════════
# 4. CHARGEMENT (CACHE)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    search_paths = [
        "epitrace_cube_live.csv",
        os.path.join("data", "traitees", "epitrace_cube_live.csv"),
        os.path.join("..", "data", "traitees", "epitrace_cube_live.csv"),
    ]
    for path in search_paths:
        if os.path.exists(path):
            return get_latest_data(path, LOOKBACK)
    st.error("❌ Fichier epitrace_cube_live.csv introuvable.")
    return None, None

@st.cache_resource
def init_models():
    model_roots = [
        "notebooks",
        os.path.join("..", "notebooks"),
        ".",
    ]
    for root in model_roots:
        s = os.path.join(root, "epi_trace_scaler.pkl")
        f = os.path.join(root, "epi_trace_bilstm.keras")
        n = os.path.join(root, "epi_trace_nowcast.keras")
        if os.path.exists(s) and os.path.exists(f) and os.path.exists(n):
            return load_ml_assets(s, f, n)
    return None, None, None

df_full, df_recent = load_data()
scaler, forecaster, nowcaster = init_models()

if df_full is None:
    st.error("⚠️ Données introuvables. Vérifiez le chemin du fichier CSV.")
    st.stop()

models_ok = scaler is not None and forecaster is not None and nowcaster is not None

# ── Calculs globaux ──────────────────────────────────────────────────────────
derniere   = df_recent.iloc[-1]
precedente = df_recent.iloc[-2]

if models_ok:
    _data_scaled   = scaler.transform(df_recent[FEATURE_COLUMNS].values)
    _prediction_j7 = predict_standard_forecast(forecaster, scaler, _data_scaled, FEATURE_COLUMNS)
else:
    _prediction_j7 = int(derniere['inc'] * 0.97)   # fallback demo

_inc_actuelle  = int(derniere['inc'])
_derniere_date = derniere['date']
_future_date   = _derniere_date + pd.Timedelta(weeks=1)
_variation     = int(derniere['inc'] - precedente['inc'])
_variation_pct = round((_variation / max(precedente['inc'], 1)) * 100, 1)

if _prediction_j7 < SEUIL_N2:
    _niveau, _pill_cls, _dot = "VEILLE",       "pill-green",  "🟢"
elif _prediction_j7 < SEUIL_N3:
    _niveau, _pill_cls, _dot = "PRÉ-ALERTE",   "pill-orange", "🟡"
elif _prediction_j7 < SEUIL_N4:
    _niveau, _pill_cls, _dot = "PLAN BLANC",   "pill-orange", "🟠"
else:
    _niveau, _pill_cls, _dot = "ALERTE ROUGE", "pill-red",    "🔴"

if _prediction_j7 < SEUIL_N2:
    _niveau_num, _label_orsan = 1, "Niveau 1 — VEILLE"
elif _prediction_j7 < SEUIL_N3:
    _niveau_num, _label_orsan = 2, "Niveau 2 — PRÉ-ALERTE"
elif _prediction_j7 < SEUIL_N4:
    _niveau_num, _label_orsan = 3, "Niveau 3 — PLAN BLANC"
else:
    _niveau_num, _label_orsan = 4, "Niveau 4 — CRISE MAJEURE"

# ══════════════════════════════════════════════════════════════════════════════
# 5. SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo">
        <div class="name">EPI<span style="color:#EFF4FF">·</span>TRACE</div>
        <div class="sub">Système d'Alerte Épidémiologique</div>
    </div>
    <div style="text-align:center; margin-bottom:1.2rem;">
        <span class="status-pill {_pill_cls}">{_dot} {_niveau}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius);
                padding:0.9rem 1rem; margin-bottom:1rem;">
        <div class="feat-row">
            <span class="feat-name">Dernière donnée</span>
            <span class="feat-val">{_derniere_date.strftime('%d/%m/%Y')}</span>
        </div>
        <div class="feat-row">
            <span class="feat-name">Incidence S-0</span>
            <span class="feat-val">{_inc_actuelle:,} cas</span>
        </div>
        <div class="feat-row">
            <span class="feat-name">Prévision J+7</span>
            <span class="feat-val" style="color:var(--orange)">{_prediction_j7:,} cas</span>
        </div>
        <div class="feat-row">
            <span class="feat-name">Seuil critique</span>
            <span class="feat-val" style="color:var(--red)">{SEUIL_N4:,} cas (P85)</span>
        </div>
        <div class="feat-row">
            <span class="feat-name">Température</span>
            <span class="feat-val">{derniere['temperature_2m']:.1f} °C</span>
        </div>
        <div class="feat-row">
            <span class="feat-name">Humidité</span>
            <span class="feat-val">{derniere['relative_humidity_2m']:.0f} %</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not models_ok:
        st.warning("⚠️ Modèles .keras non trouvés — Mode démo actif")

    st.markdown("""
    <div style="border-top:1px solid var(--border); padding-top:1rem; margin-top:0.5rem;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:var(--text-dim);
                    line-height:2; text-transform:uppercase; letter-spacing:0.1em;">
            <div style="color:var(--cyan); margin-bottom:4px;">📍 Région : Île-de-France</div>
            <div>🎓 ENSAM Meknès — IATD-SI</div>
            <div>Yahya Amajane</div>
            <div>Mohamed Amine Belasri</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 6. EN-TÊTE GLOBAL
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hdr-band">
    <div>
        <div class="hdr-logo">🔬 EPI<span>TRACE</span> — Centre de Commandement</div>
        <div class="hdr-sub">Plateforme Prédictive d'Intelligence Épidémiologique</div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;">
        <span class="model-badge">IA PRÉDICTIVE</span>
        <span class="status-pill {_pill_cls}">{_dot} STATUT : {_niveau}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 7. ONGLETS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠  Tableau de Bord",
    "🔮  Moteur de Prévision",
    "📡  Signaux Précurseurs",
    "🤖  Agent IA — Rapport",
    "🧪  Simulateur What-If"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TABLEAU DE BORD STRATÉGIQUE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

    c1.metric("🏥 Incidence S-0",
              f"{_inc_actuelle:,}",
              f"{_variation:+,} ({_variation_pct:+.1f}%)",
              delta_color="inverse")
    c2.metric("🔮 Prévision J+7",
              f"{_prediction_j7:,}",
              f"{_prediction_j7 - _inc_actuelle:+,} projetés",
              delta_color="inverse")
    c3.metric("🌡️ Température",
              f"{derniere['temperature_2m']:.1f} °C")
    c4.metric("💧 Humidité",
              f"{derniere['relative_humidity_2m']:.0f} %")
    c5.metric("🤒 Grippe (Web)",
              f"{int(derniere['Topic_Grippe'])} /100")
    c6.metric("🤧 Toux (Web)",
              f"{int(derniere['Topic_Toux'])} /100")
    c7.metric("🌡️ Fièvre (Web)",
              f"{int(derniere['Topic_Fievre'])} /100")

    st.markdown("---")

    # ── Graphique principal ────────────────────────────────────────────────────
    col_main, col_right = st.columns([7, 3])

    with col_main:
        st.markdown('<div class="sec-label">📈 Évolution Épidémique — Île-de-France (80 dernières semaines)</div>',
                    unsafe_allow_html=True)

        df_plot = df_full.tail(80).copy()
        fig = go.Figure()

        # Zone remplie
        fig.add_trace(go.Scatter(
            x=df_plot['date'], y=df_plot['inc'],
            fill='tozeroy', fillcolor='rgba(0,87,255,0.07)',
            line=dict(color='rgba(0,0,0,0)'),
            showlegend=False, hoverinfo='skip'
        ))
        # Courbe historique
        fig.add_trace(go.Scatter(
            x=df_plot['date'], y=df_plot['inc'],
            mode='lines', name='Incidence Sentinelles',
            line=dict(color='#00C6FF', width=2.5),
            hovertemplate='%{x|%d/%m/%Y}<br><b>%{y:,} cas</b><extra></extra>'
        ))
        # Zone alerte (fond rouge)
        fig.add_hrect(y0=SEUIL_ALERTE, y1=df_plot['inc'].max() * 1.15,
                      fillcolor="rgba(255,48,84,0.04)", line_width=0)
        # Ligne seuil
        fig.add_hline(y=SEUIL_ALERTE, line_dash="dot",
                      line_color="#FF3054", line_width=1.5,
                      annotation_text=f"  Seuil critique ({SEUIL_ALERTE:,})",
                      annotation_font_color="#FF3054", annotation_font_size=10)
        # Point actuel
        fig.add_trace(go.Scatter(
            x=[_derniere_date], y=[_inc_actuelle],
            mode='markers', name='Semaine actuelle',
            marker=dict(color='#00E5A0', size=13, symbol='diamond',
                        line=dict(width=2, color='white')),
            hovertemplate=f'<b>S-0 : {_inc_actuelle:,} cas</b><extra></extra>'
        ))
        # Prévision J+7
        fig.add_trace(go.Scatter(
            x=[_derniere_date, _future_date],
            y=[_inc_actuelle, _prediction_j7],
            mode='lines+markers', name=f'Prévision J+7',
            line=dict(color='#FF9500', width=3, dash='dash'),
            marker=dict(size=[10, 14], color=['#FF9500', '#FF3054'],
                        symbol=['circle', 'star'],
                        line=dict(width=2, color='white')),
            hovertemplate='%{x|%d/%m/%Y}<br><b>%{y:,} cas projetés</b><extra></extra>'
        ))

        fig.update_layout(
            **PLOTLY_THEME, height=360,
            legend=dict(orientation="h", yanchor="bottom", y=1.01,
                        xanchor="right", x=1, bgcolor='rgba(0,0,0,0)',
                        font=dict(size=10)),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown('<div class="sec-label">📊 Répartition des Signaux</div>',
                    unsafe_allow_html=True)

        # Radar chart avec correction de l'affichage au survol (hovertext exact)
        categories = ['Grippe', 'Toux', 'Fièvre', 'Hum.', 'Temp.↑', 'Vacances']
        raw = [
            int(derniere['Topic_Grippe']),
            int(derniere['Topic_Toux']),
            int(derniere['Topic_Fievre']),
            min(derniere['relative_humidity_2m'], 100),
            max(0, min((derniere['temperature_2m'] + 10) * 100 / 40, 100)),
            derniere['ratio_vacances'] * 100
        ]
        vals = raw + [raw[0]]
        cats = categories + [categories[0]]
        
        hover_texts = [
            f"Grippe : {int(derniere['Topic_Grippe'])} /100",
            f"Toux : {int(derniere['Topic_Toux'])} /100",
            f"Fièvre : {int(derniere['Topic_Fievre'])} /100",
            f"Humidité : {derniere['relative_humidity_2m']:.0f} %",
            f"Température : {derniere['temperature_2m']:.1f} °C",
            f"Ratio Vacances : {derniere['ratio_vacances']:.2f}"
        ]
        hover_texts_loop = hover_texts + [hover_texts[0]]

        fig_r = go.Figure(go.Scatterpolar(
            r=vals, theta=cats,
            fill='toself',
            fillcolor='rgba(0,198,255,0.12)',
            line=dict(color='#00C6FF', width=2),
            marker=dict(color='#00C6FF', size=6),
            text=hover_texts_loop,
            hoverinfo="text"
        ))
        fig_r.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#7D94B8', size=10),
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0, 100],
                                gridcolor='rgba(255,255,255,0.06)',
                                tickfont=dict(color='#3D5070', size=8),
                                tickvals=[25, 50, 75, 100]),
                angularaxis=dict(gridcolor='rgba(255,255,255,0.06)',
                                 tickfont=dict(color='#7D94B8', size=9))
            ),
            margin=dict(l=20, r=20, t=30, b=20),
            height=310
        )
        st.plotly_chart(fig_r, use_container_width=True)

        # Jauges Google Trends
        st.markdown("""<div style="margin-top:-0.5rem;">""", unsafe_allow_html=True)
        for topic, col in [('Topic_Grippe', '#FF9500'), ('Topic_Toux', '#00C6FF'), ('Topic_Fievre', '#FF3054')]:
            v = int(derniere[topic])
            label = topic.replace("Topic_", "Google ")
            bar_w = v
            st.markdown(f"""
            <div style="margin:0.35rem 0;">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                    <span style="font-size:0.75rem;color:var(--text-p);">{label}</span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:{col};">{v}/100</span>
                </div>
                <div style="background:rgba(255,255,255,0.05);border-radius:4px;height:6px;overflow:hidden;">
                    <div style="width:{bar_w}%;height:100%;background:{col};border-radius:4px;
                                box-shadow:0 0 8px {col}60;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("""</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Tableau historique ─────────────────────────────────────────────────────
    st.markdown('<div class="sec-label">📋 Historique Récent — 12 dernières semaines</div>',
                unsafe_allow_html=True)

    df_display = df_recent[[
        'date', 'inc', 'temperature_2m', 'relative_humidity_2m',
        'Topic_Grippe', 'Topic_Toux', 'Topic_Fievre', 'ratio_vacances'
    ]].copy()
    df_display.columns = ['Date', 'Incidence', 'Temp. (°C)', 'Humidité (%)',
                           'Google Grippe', 'Google Toux', 'Google Fièvre', 'Ratio Vacances']
    df_display['Date']      = df_display['Date'].dt.strftime('%d/%m/%Y')
    df_display['Incidence'] = df_display['Incidence'].apply(lambda x: f"{int(x):,}")
    df_display['Temp. (°C)']  = df_display['Temp. (°C)'].apply(lambda x: f"{x:.1f}")
    df_display['Humidité (%)'] = df_display['Humidité (%)'].apply(lambda x: f"{x:.0f}")
    df_display['Ratio Vacances'] = df_display['Ratio Vacances'].apply(lambda x: f"{x:.2f}")
    st.dataframe(df_display.iloc[::-1], use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — MOTEUR DE PRÉVISION EN CASCADE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown('<div class="sec-label">⚙️ Architecture Logique — Modèles de Deep Learning</div>',
                unsafe_allow_html=True)

    # ── Mode selector ──────────────────────────────────────────────────────────
    mode = st.radio("", [
        "🟢  Mode Standard — Données cliniques disponibles (Forecasting pur)",
        "🔴  Mode Urgence — Rapport Sentinelles absent (Cascade Nowcast → Forecast)"
    ], horizontal=False)

    st.markdown("---")

    if models_ok:
        data_scaled = scaler.transform(df_recent[FEATURE_COLUMNS].values)
    else:
        st.warning("⚠️ Modèles non chargés — affichage en mode démo.")
        data_scaled = None

    if "Standard" in mode:
        # Architecture détaillée pour le mode standard
        st.markdown("""
        <div class="arch-flow">
            <div class="arch-node node-data">
                <div class="label" style="color:#0057FF;">VÉRITÉ TERRAIN</div>
                <div class="value" style="color:#4D90FF;">Tenseur (12 × 7)</div>
                <div style="font-size:0.68rem; color:var(--text-p); margin-top:6px; line-height:1.4;">
                    Incidence S-12 à S-0<br>+ Variables Météo<br>+ Infodémiologie (Web)
                </div>
            </div>
            <div class="arch-arrow">→</div>
            <div class="arch-node node-model">
                <div class="label" style="color:#00C6FF;">RÉSEAU DEEP LEARNING</div>
                <div class="value" style="color:#4DDBFF;">BiLSTM Forecaster</div>
                <div style="font-size:0.68rem; color:var(--text-p); margin-top:6px; line-height:1.4;">
                    Apprentissage Bidirectionnel<br>
                    <span style="color:#00C6FF;">R² = 0.73 | RMSE = 4 116</span>
                </div>
            </div>
            <div class="arch-arrow">→</div>
            <div class="arch-node node-output">
                <div class="label" style="color:#00E5A0;">PROJECTION LOGISTIQUE</div>
                <div class="value" style="color:#00E5A0;">Horizon J+7</div>
                <div style="font-size:0.68rem; color:var(--text-p); margin-top:6px; line-height:1.4;">
                    Incidence prévue<br>pour la semaine S+1
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if models_ok:
            cas_prevus   = predict_standard_forecast(forecaster, scaler, data_scaled, FEATURE_COLUMNS)
        else:
            cas_prevus = _prediction_j7
        inc_actuelle = _inc_actuelle
        source_label = "Donnée officielle Sentinelles"
        couleur_pt   = '#00E5A0'
        mode_label   = "FORECASTING PUR"
        st.success(f"✅ **Mode Standard** actif — Utilisation de l'incidence clinique officielle pour la projection.")

    else:
        # Architecture  en cascade pour le mode urgence
        st.markdown("""
        <div class="arch-flow">
            <div class="arch-node node-data" style="border-color:rgba(255,149,0,0.5);">
                <div class="label" style="color:#FF9500;">SÉQUENCE D'ENTRÉE</div>
                <div class="value" style="color:#FFB84D;">Tenseur (12 × 7)</div>
                <div style="font-size:0.68rem; color:var(--text-p); margin-top:6px; line-height:1.4;">
                    Météo + Web complets<br><span style="color:#FF3054; font-weight:600;">Incidence S-0 masquée</span>
                </div>
            </div>
            <div class="arch-arrow" style="color:#FF9500;">→</div>
            <div class="arch-node node-now">
                <div class="label" style="color:#FF9500;">RÉSEAU NOWCASTER</div>
                <div class="value" style="color:#FFB84D;">Estimation S-0</div>
                <div style="font-size:0.68rem; color:var(--text-p); margin-top:6px; line-height:1.4;">
                    Reconstitution de la<br>donnée clinique absente
                </div>
            </div>
            <div class="arch-arrow">→</div>
            <div class="arch-node node-model">
                <div class="label" style="color:#00C6FF;">RÉSEAU BILSTM</div>
                <div class="value" style="color:#4DDBFF;">Forecaster Principal</div>
                <div style="font-size:0.68rem; color:var(--text-p); margin-top:6px; line-height:1.4;">
                    Analyse de la séquence<br>12 semaines complétée
                </div>
            </div>
            <div class="arch-arrow">→</div>
            <div class="arch-node node-output">
                <div class="label" style="color:#00E5A0;">PROJECTION LOGISTIQUE</div>
                <div class="value" style="color:#00E5A0;">Horizon J+7</div>
                <div style="font-size:0.68rem; color:var(--text-p); margin-top:6px; line-height:1.4;">
                    Incidence prévue<br>pour la semaine S+1
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if models_ok:
            inc_actuelle, inc_scaled = predict_cascade_nowcast(nowcaster, scaler, data_scaled, FEATURE_COLUMNS)
            data_for_forecast        = data_scaled.copy()
            data_for_forecast[-1, 0] = inc_scaled
            cas_prevus = predict_standard_forecast(forecaster, scaler, data_for_forecast, FEATURE_COLUMNS)
        else:
            inc_actuelle = _inc_actuelle
            inc_scaled   = 0
            cas_prevus   = _prediction_j7
        source_label = "Estimation Nowcaster"
        couleur_pt   = '#FF9500'
        mode_label   = "CASCADE NOWCAST → FORECAST"
        st.warning(f"⚠️ **Mode Urgence** — Substitution de la donnée manquante par le réseau Nowcaster.")

        # Panel nowcast (avec ajouts fièvres et vacances)
        inc_vraie  = _inc_actuelle
        erreur     = abs(inc_actuelle - inc_vraie)
        erreur_pct = round(erreur / max(inc_vraie, 1) * 100, 1)

        st.markdown(f"""
        <div class="nowcast-panel">
            <div class="title">🔴 Résultat du Nowcasting — Estimation de la semaine en cours</div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;">
                <div>
                    <div style="font-size:0.72rem;color:var(--text-dim);text-transform:uppercase;
                                letter-spacing:0.1em;margin-bottom:6px;">Entrée (inc masquée)</div>
                    <div style="font-family:'JetBrains Mono',monospace;color:var(--orange);">inc(T) = ■■■■■</div>
                    <div style="font-size:0.82rem;color:var(--text-p);margin-top:4px;">
                        Météo : {derniere['temperature_2m']:.1f}°C · {derniere['relative_humidity_2m']:.0f}%<br>
                        Google : Grippe {int(derniere['Topic_Grippe'])} · Toux {int(derniere['Topic_Toux'])} · Fièvre {int(derniere['Topic_Fievre'])}<br>
                        Vacances : {derniere['ratio_vacances']:.2f}
                    </div>
                </div>
                <div>
                    <div style="font-size:0.72rem;color:var(--text-dim);text-transform:uppercase;
                                letter-spacing:0.1em;margin-bottom:6px;">Estimation Nowcaster</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;color:var(--orange);">
                        {inc_actuelle:,} <span style="font-size:0.8rem;">cas</span>
                    </div>
                </div>
                <div>
                    <div style="font-size:0.72rem;color:var(--text-dim);text-transform:uppercase;
                                letter-spacing:0.1em;margin-bottom:6px;">Vérification (vérité terrain)</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;color:var(--green);">
                        {inc_vraie:,} <span style="font-size:0.8rem;">cas</span>
                    </div>
                    <div style="font-size:0.82rem;color:var(--text-p);margin-top:4px;">
                        Écart : {erreur:,} cas ({erreur_pct:.1f}%)
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── KPIs prévision ─────────────────────────────────────────────────────────
    kA, kB, kC, kD = st.columns(4)
    kA.metric("📌 Incidence Actuelle", f"{inc_actuelle:,} cas", source_label)
    kB.metric(f"🔮 Prévision — {_future_date.strftime('%d/%m/%Y')}",
              f"{cas_prevus:,} cas",
              f"{cas_prevus - inc_actuelle:+,} cas projetés",
              delta_color="inverse")
    occupation = min(100, int((cas_prevus / SEUIL_ALERTE) * 75))
    kC.metric("🏨 Pression Hospitalière", f"{occupation} %",
              "du seuil de saturation estimé", delta_color="off")

    if cas_prevus >= SEUIL_N4:
        kD.metric("🔴 Statut Prévisionnel", "ALERTE ROUGE",
                  f"Crise > {SEUIL_N4:,} cas (P85)")
    elif cas_prevus >= SEUIL_N3:
        kD.metric("🟠 Statut Prévisionnel", "PLAN BLANC",
                  f"Tension > {SEUIL_N3:,} cas (P75)")
    elif cas_prevus >= SEUIL_N2:
        kD.metric("🟡 Statut Prévisionnel", "PRÉ-ALERTE",
                  f"Hausse > {SEUIL_N2:,} cas (P50)")
    else:
        kD.metric("✅ Statut Prévisionnel", "VEILLE",
                  "Situation sous contrôle")

    # ── Graphique prévision ────────────────────────────────────────────────────
    df_plot2 = df_full.tail(40).copy()
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=df_plot2['date'], y=df_plot2['inc'],
        fill='tozeroy', fillcolor='rgba(0,87,255,0.05)',
        line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'
    ))
    fig2.add_trace(go.Scatter(
        x=df_plot2['date'], y=df_plot2['inc'],
        mode='lines', name='Historique',
        line=dict(color='#4D6A8A', width=2),
        hovertemplate='%{x|%d/%m/%Y} — %{y:,} cas<extra></extra>'
    ))
    fig2.add_trace(go.Scatter(
        x=[_derniere_date], y=[inc_actuelle],
        mode='markers', name=source_label,
        marker=dict(color=couleur_pt, size=14, symbol='diamond',
                    line=dict(width=2, color='white'))
    ))
    # Cône d'incertitude
    fig2.add_trace(go.Scatter(
        x=[_derniere_date, _future_date, _future_date, _derniere_date],
        y=[inc_actuelle, cas_prevus + RMSE_FORECAST, cas_prevus - RMSE_FORECAST, inc_actuelle],
        fill='toself', fillcolor='rgba(255,149,0,0.07)',
        line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'
    ))
    fig2.add_trace(go.Scatter(
        x=[_derniere_date, _future_date],
        y=[inc_actuelle, cas_prevus],
        mode='lines+markers', name=f'Prévision BiLSTM J+7',
        line=dict(color='#FF9500', width=3, dash='dash'),
        marker=dict(size=[10, 16], color=['#FF9500', '#FF3054'],
                    symbol=['circle', 'star-dot'],
                    line=dict(width=2, color='white')),
        hovertemplate='%{x|%d/%m/%Y}<br><b>%{y:,} cas projetés</b><extra></extra>'
    ))
    fig2.add_hline(y=SEUIL_ALERTE, line_dash="dot",
                   line_color="#FF3054", line_width=1.5,
                   annotation_text=f"  Seuil critique",
                   annotation_font_color="#FF3054", annotation_font_size=10)

    fig2.update_layout(**PLOTLY_THEME, height=380, hovermode="x unified",
                       legend=dict(orientation="h", yanchor="bottom", y=1.01,
                                   xanchor="right", x=1, bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(f"🔹 Mode : {mode_label} ")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SIGNAUX PRÉCURSEURS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:

    signal_choisi = st.selectbox("Prisme d'analyse :", [
        "🌐 Infodémiologie — Google Trends vs Incidence Sentinelles",
        "🌡️ Météorologie — Température, Humidité & Dispersion",
        "📊 Heatmap — Corrélations entre toutes les variables"
    ])

    if "Google" in signal_choisi:
        st.markdown('<div class="sec-label">🌐 Corrélation Google Trends ↔ Sentinelles</div>',
                    unsafe_allow_html=True)

        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        fig3.add_trace(go.Scatter(
            x=df_full['date'], y=df_full['inc'],
            name="Incidence Sentinelles",
            line=dict(color='#FF3054', width=2.5),
            hovertemplate='%{x|%d/%m/%Y} — <b>%{y:,} cas</b><extra></extra>'
        ), secondary_y=False)
        fig3.add_trace(go.Scatter(
            x=df_full['date'], y=df_full['Topic_Grippe'],
            name="Google 'Grippe' (r=0.81)",
            line=dict(color='#00C6FF', width=1.8, dash='dot')
        ), secondary_y=True)
        fig3.add_trace(go.Scatter(
            x=df_full['date'], y=df_full['Topic_Toux'],
            name="Google 'Toux' (r=0.84)",
            line=dict(color='#00E5A0', width=1.8, dash='dash')
        ), secondary_y=True)
        fig3.add_trace(go.Scatter(
            x=df_full['date'], y=df_full['Topic_Fievre'],
            name="Google 'Fièvre' (r=0.72)",
            line=dict(color='#FF9500', width=1.5, dash='longdash')
        ), secondary_y=True)
        fig3.update_yaxes(title_text="Cas confirmés Sentinelles",
                          secondary_y=False, color='#FF3054', showgrid=False)
        fig3.update_yaxes(title_text="Intérêt Google (0–100)",
                          secondary_y=True, color='#00C6FF',
                          showgrid=True, gridcolor='rgba(255,255,255,0.04)')
        fig3.update_layout(**PLOTLY_THEME, height=420, hovermode="x unified",
                           legend=dict(orientation="h", yanchor="bottom", y=1.01,
                                       xanchor="right", x=1, bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig3, use_container_width=True)

        # Corr cards
        cc = st.columns(3)
        corr_data = [
            ("🤧", "Google 'Toux'",   "r = +0.842", "#00E5A0", "Signal le plus fort"),
            ("🤒", "Google 'Grippe'", "r = +0.812", "#00C6FF", "Signal fort"),
            ("🌡️", "Google 'Fièvre'", "r = +0.717", "#FF9500", "Signal significatif"),
        ]
        for col, (icon, name, val, clr, tag) in zip(cc, corr_data):
            with col:
                st.markdown(f"""
                <div class="corr-card">
                    <div class="corr-icon">{icon}</div>
                    <div>
                        <div class="corr-name">{name}</div>
                        <div class="corr-val" style="color:{clr};">{val}</div>
                        <div style="font-size:0.72rem;color:var(--text-dim);margin-top:2px;">{tag}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    elif "Météo" in signal_choisi:
        st.markdown('<div class="sec-label">🌡️ Relation Température / Humidité → Incidence</div>',
                    unsafe_allow_html=True)

        col_l, col_r = st.columns(2)
        with col_l:
            fig4 = px.scatter(
                df_full, x="temperature_2m", y="inc",
                color="relative_humidity_2m",
                size="Topic_Toux",
                color_continuous_scale=[[0, '#0057FF'], [0.4, '#00C6FF'], [1, '#00E5A0']],
                labels={"temperature_2m": "Température (°C)",
                        "inc": "Incidence (cas)",
                        "relative_humidity_2m": "Humidité (%)",
                        "Topic_Toux": "Google Toux"},
                hover_data={"date": "|%d/%m/%Y"}
            )
            fig4.update_traces(marker=dict(opacity=0.7,
                                           line=dict(width=0.5, color='rgba(255,255,255,0.2)')))
            fig4.update_layout(**PLOTLY_THEME, height=380,
                               coloraxis_colorbar=dict(
                                   title=dict(text="Humidité", font=dict(color='#7D94B8')),
                                   tickfont=dict(color='#7D94B8')))
            st.plotly_chart(fig4, use_container_width=True)

        with col_r:
            # Série temporelle température / incidence
            fig5 = make_subplots(specs=[[{"secondary_y": True}]])
            fig5.add_trace(go.Scatter(
                x=df_full['date'], y=df_full['inc'],
                name="Incidence", line=dict(color='#FF3054', width=2)
            ), secondary_y=False)
            fig5.add_trace(go.Scatter(
                x=df_full['date'], y=df_full['temperature_2m'],
                name="Température (°C) (r=−0.60)",
                line=dict(color='#00C6FF', width=1.5, dash='dot')
            ), secondary_y=True)
            fig5.add_trace(go.Scatter(
                x=df_full['date'], y=df_full['relative_humidity_2m'],
                name="Humidité (%) (r=+0.52)",
                line=dict(color='#00E5A0', width=1.5, dash='dash')
            ), secondary_y=True)
            fig5.update_layout(**PLOTLY_THEME, height=380,
                               legend=dict(orientation="h", y=1.05, bgcolor='rgba(0,0,0,0)'))
            st.plotly_chart(fig5, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Corrélation Température", "r = −0.604", "Froid → pic épidémique")
        c2.metric("Corrélation Humidité",    "r = +0.524", "Signal modéré mais significatif")
        c3.metric("Corrélation Vacances",    "r = −0.18",  "Effet modérateur partiel")

    else:  # Heatmap
        st.markdown('<div class="sec-label">📊 Matrice de Corrélation — Toutes les Variables</div>',
                    unsafe_allow_html=True)

        cols_corr  = ['inc', 'temperature_2m', 'relative_humidity_2m',
                      'Topic_Toux', 'Topic_Grippe', 'Topic_Fievre', 'ratio_vacances']
        labels_corr = ['Incidence', 'Temp.', 'Humidité',
                       'Toux', 'Grippe', 'Fièvre', 'Vacances']
        corr_matrix = df_full[cols_corr].corr().values

        fig6 = go.Figure(go.Heatmap(
            z=corr_matrix,
            x=labels_corr, y=labels_corr,
            colorscale=[[0, '#FF3054'], [0.5, '#0C1425'], [1, '#00C6FF']],
            zmin=-1, zmax=1,
            text=[[f"{v:.2f}" for v in row] for row in corr_matrix],
            texttemplate="%{text}",
            textfont=dict(size=11, color='rgba(255,255,255,0.85)'),
            showscale=True,
            colorbar=dict(tickfont=dict(color='#7D94B8'),
                          title=dict(text="r", font=dict(color='#7D94B8')),
                          tickvals=[-1, -0.5, 0, 0.5, 1])
        ))
        _theme6 = {k: v for k, v in PLOTLY_THEME.items() if k not in ('xaxis', 'yaxis')}
        fig6.update_layout(**_theme6, height=440,
                           xaxis=dict(side='bottom', showgrid=False,
                                      gridcolor='rgba(255,255,255,0.04)',
                                      tickfont=dict(size=10), zeroline=False),
                           yaxis=dict(showgrid=False,
                                      gridcolor='rgba(255,255,255,0.04)',
                                      tickfont=dict(size=10), zeroline=False))
        st.plotly_chart(fig6, use_container_width=True)
        st.caption("Corrélation de Pearson · Variables du Cube OLAP · n=277 observations hebdomadaires")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — AGENT IA & RAG
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="sec-label">🤖 Agent RAG — Gemini 2.5 Flash + Protocole ORSAN REB</div>',
                unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-box">
        L'agent lit le <span class="hl">Protocole ORSAN REB officiel</span> (technique RAG),
        analyse les prédictions du BiLSTM, et rédige un <span class="hl">bulletin de commandement</span>
        directement exploitable par le directeur médical — sans hallucination de procédure médicale.
        <br><br>
        Niveau ORSAN détecté : <span class="hl">{_label_orsan}</span> (prévision {_prediction_j7:,} cas pour la semaine du {_future_date.strftime('%d/%m/%Y')})
    </div>
    """, unsafe_allow_html=True)

    # Contexte pré-bulletin
    kc1, kc2 = st.columns(2)
    kc1.metric("🔮 Prévision BiLSTM J+7",  f"{_prediction_j7:,} cas",
               f"Semaine du {_future_date.strftime('%d/%m')}")
    kc2.metric("📋 Niveau ORSAN", _label_orsan)
    

    st.markdown("---")

    col_btn, col_info = st.columns([2, 3])
    with col_btn:
        gen_btn = st.button("🤖  Générer le Bulletin d'Alerte Officiel",
                            use_container_width=True)
    with col_info:
        st.markdown(f"""
        <div style="padding:0.7rem 1rem;background:var(--bg-card);border-radius:var(--radius-sm);
                    border:1px solid var(--border);font-size:0.82rem;color:var(--text-p);">
            <strong style="color:var(--text-h);">Flux d'exécution :</strong>
            Lecture ORSAN REB → Analyse des 7 features → Identification du seuil → Rédaction directive
        </div>
        """, unsafe_allow_html=True)

    if gen_btn:
        with st.spinner("📚 Lecture du Protocole ORSAN REB et génération du bulletin..."):
            chemin_md = os.path.join("docs", "protocole_orsan_reb.md")
            bulletin  = generer_bulletin_alerte(
                cas_prevus=_prediction_j7,
                niveau_alerte=_niveau_num,
                chemin_protocole=chemin_md
            )

        st.success("✅ Bulletin généré avec succès")
        st.markdown(f"""
        <div class="bulletin">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:var(--text-dim);
                        text-transform:uppercase;letter-spacing:0.15em;margin-bottom:1rem;">
                BULLETIN EPI-TRACE · {_future_date.strftime('%d/%m/%Y')} · {_label_orsan.upper()}
            </div>
        """, unsafe_allow_html=True)
        st.markdown(bulletin)
        st.markdown("</div>", unsafe_allow_html=True)

        # Génération du HTML Stylisé pour le téléchargement
        html_theme = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Bulletin d'Alerte Epi-Trace</title>
            <style>
                body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f4f7f6; color: #333; padding: 40px; }}
                .container {{ max-width: 800px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); border-top: 6px solid #2c3e50; }}
                h1 {{ color: #e74c3c; text-align: center; font-size: 24px; text-transform: uppercase; letter-spacing: 1px; }}
                h2, h3 {{ color: #2980b9; }}
                .meta-info {{ text-align: center; font-size: 14px; color: #7f8c8d; margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
                .content {{ line-height: 1.8; font-size: 15px; }}
                .footer {{ text-align: center; margin-top: 50px; font-size: 12px; color: #bdc3c7; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚨 Bulletin d'Alerte Logistique</h1>
                <div class="meta-info">
                    <strong>Système :</strong> Epi-Trace AI<br>
                    <strong>Généré le :</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}<br>
                    <strong>Cible :</strong> Semaine du {_future_date.strftime('%d/%m/%Y')}
                </div>
                <div class="content">
                    {bulletin.replace(chr(10), '<br>')}
                </div>
                <div class="footer">
                    Document généré automatiquement par Intelligence Artificielle (BiLSTM + Gemini RAG).<br>
                    Confidentiel Médical - Ne pas diffuser au public.
                </div>
            </div>
        </body>
        </html>
        """

        st.download_button(
            label="📥  Télécharger le Rapport  (HTML)",
            data=html_theme,
            file_name=f"Alerte_EpiTrace_{_future_date.strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=False
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SIMULATEUR WHAT-IF
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="sec-label">🧪 Simulateur de Scénarios Épidémiques — What-If Analysis</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        Manipulez les <span class="hl">7 variables d'entrée du modèle</span> en temps réel et observez
        l'impact causal sur la prévision J+7. Cet outil prouve que le BiLSTM ne produit pas de
        "magie noire" — il répond de façon causale aux variables validées par le <span class="hl">Test de Granger (p&lt;0.05)</span>.
    </div>
    """, unsafe_allow_html=True)

    # ── Sliders ────────────────────────────────────────────────────────────────
    col_s1, col_s2, col_s3 = st.columns(3)

    with col_s1:
        st.markdown("**🌡️ Conditions Climatiques**")
        sim_temp = st.slider("Température (°C)", -10.0, 35.0,
                             float(round(derniere['temperature_2m'], 1)), step=0.5)
        sim_humid = st.slider("Humidité Relative (%)", 30.0, 100.0,
                              float(round(derniere['relative_humidity_2m'], 0)), step=1.0)

    with col_s2:
        st.markdown("**🔍 Signaux Google Trends**")
        sim_toux   = st.slider("Topic 'Toux'",   0, 100, int(derniere['Topic_Toux']),   step=1)
        sim_grippe = st.slider("Topic 'Grippe'", 0, 100, int(derniere['Topic_Grippe']), step=1)
        sim_fievre = st.slider("Topic 'Fièvre'", 0, 100, int(derniere['Topic_Fievre']), step=1)

    with col_s3:
        st.markdown("**📅 Contexte Social**")
        sim_vacances = st.slider("Ratio Vacances (0–1)", 0.0, 1.0,
                                 float(round(derniere['ratio_vacances'], 2)), step=0.01)
        sim_inc = st.slider("Incidence simulée S-0",
                            int(df_full['inc'].min()),
                            int(df_full['inc'].max()),
                            int(derniere['inc']),
                            step=100)

    # ── Calcul simulation ──────────────────────────────────────────────────────
    data_sim = df_recent[FEATURE_COLUMNS].values.copy()
    data_sim[-1] = [sim_inc, sim_temp, sim_humid, sim_toux, sim_grippe, sim_fievre, sim_vacances]

    if models_ok:
        data_sim_scaled = scaler.transform(data_sim)
        prediction_sim  = predict_standard_forecast(forecaster, scaler, data_sim_scaled, FEATURE_COLUMNS)
    else:
        prediction_sim = int(_prediction_j7 * (sim_temp / max(derniere['temperature_2m'], 1)) *
                             (sim_grippe / max(derniere['Topic_Grippe'], 1)))

    delta_sim  = prediction_sim - _prediction_j7
    gain_pct   = round(delta_sim / max(_prediction_j7, 1) * 100, 1)

    # ── KPIs simulation ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="sec-label">📊 Résultat du Scénario Simulé vs Scénario Réel</div>',
                unsafe_allow_html=True)

    cs1, cs2, cs3, cs4 = st.columns(4)
    cs1.metric("📊 Prévision RÉELLE J+7",  f"{_prediction_j7:,} cas", "Données officielles")
    cs2.metric("🧪 Prévision SIMULÉE J+7", f"{prediction_sim:,} cas",
               f"{delta_sim:+,} cas vs réel", delta_color="inverse")

    if prediction_sim >= SEUIL_N4:
        cs3.metric("🔴 Statut Simulé", "ALERTE ROUGE ⛔", f"> {SEUIL_N4:,} cas (P85)")
    elif prediction_sim >= SEUIL_N3:
        cs3.metric("🟠 Statut Simulé", "PLAN BLANC 🟠", f"> {SEUIL_N3:,} cas (P75)")
    elif prediction_sim >= SEUIL_N2:
        cs3.metric("🟡 Statut Simulé", "PRÉ-ALERTE 🟡", f"> {SEUIL_N2:,} cas (P50)")
    else:
        cs3.metric("✅ Statut Simulé", "VEILLE 🟢", "Situation maîtrisée")

    delta_cls = "delta-up" if delta_sim > 500 else "delta-down" if delta_sim < -500 else "delta-flat"
    cs4.markdown(f"""
    <div style="text-align:center; padding:1rem;">
        <div style="font-size:0.75rem;color:var(--text-p);text-transform:uppercase;
                    letter-spacing:0.1em;margin-bottom:8px;">Impact Scénario</div>
        <span class="scenario-delta {delta_cls}">{gain_pct:+.1f}%</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Graphique comparatif ───────────────────────────────────────────────────
    df_base = df_full.tail(30).copy()
    fig_sim = go.Figure()

    fig_sim.add_trace(go.Scatter(
        x=df_base['date'], y=df_base['inc'],
        mode='lines', name='Historique Réel',
        line=dict(color='#4D6A8A', width=2)
    ))
    fig_sim.add_trace(go.Scatter(
        x=[_derniere_date, _future_date],
        y=[_inc_actuelle, _prediction_j7],
        mode='lines+markers', name=f'Prévision Réelle ({_prediction_j7:,} cas)',
        line=dict(color='#00C6FF', width=3, dash='dash'),
        marker=dict(size=[8, 14], color='#00C6FF',
                    symbol=['circle', 'star'],
                    line=dict(width=2, color='white'))
    ))

    couleur_sim = '#FF3054' if prediction_sim >= SEUIL_N4 else \
                  '#FF9500' if prediction_sim >= SEUIL_N3 else \
                  '#FFD000' if prediction_sim >= SEUIL_N2 else '#00E5A0'
    fig_sim.add_trace(go.Scatter(
        x=[_derniere_date, _future_date],
        y=[sim_inc, prediction_sim],
        mode='lines+markers', name=f'Scénario Simulé ({prediction_sim:,} cas)',
        line=dict(color=couleur_sim, width=3, dash='dot'),
        marker=dict(size=[8, 14], color=couleur_sim,
                    symbol=['circle', 'star'],
                    line=dict(width=2, color='white'))
    ))
    fig_sim.add_hline(y=SEUIL_ALERTE, line_dash="dot",
                      line_color="#FF3054", line_width=1.5,
                      annotation_text="  Seuil critique",
                      annotation_font_color="#FF3054", annotation_font_size=10)

    fig_sim.update_layout(**PLOTLY_THEME, height=380, hovermode="x unified",
                          legend=dict(orientation="h", yanchor="bottom", y=1.01,
                                      xanchor="right", x=1, bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig_sim, use_container_width=True)

    # ── Interprétation automatique ─────────────────────────────────────────────
    if abs(delta_sim) < 500:
        interp_icon = "🔵"
        interp_text = (f"Le scénario simulé ne modifie pas significativement la prévision "
                       f"(±{abs(delta_sim):,} cas, &lt;500). La dynamique épidémique historique est le facteur dominant.")
        interp_color = "var(--cyan)"
    elif delta_sim > 0:
        interp_icon = "🔴"
        interp_text = (f"Ce scénario <strong>aggraverait la situation</strong> de {delta_sim:+,} cas "
                       f"({gain_pct:+.1f}%). Les hôpitaux devront anticiper davantage de ressources.")
        interp_color = "var(--red)"
    else:
        interp_icon = "🟢"
        interp_text = (f"Ce scénario <strong>réduirait la pression hospitalière</strong> de "
                       f"{abs(delta_sim):,} cas ({gain_pct:.1f}%). La situation serait plus favorable.")
        interp_color = "var(--green)"

    st.markdown(f"""
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);
                padding:1rem 1.4rem;margin-top:0.5rem;">
        <span style="font-size:1.1rem;">{interp_icon}</span>
        <strong style="color:{interp_color}; font-family:'Syne',sans-serif;"> Interprétation : </strong>
        <span style="color:var(--text-p);font-size:0.9rem;">{interp_text}</span>
    </div>
    """, unsafe_allow_html=True)