import sys
import os
import time
import random
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------
# Ensure project root is in Python path
# -------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from response.hybrid_decision import hybrid_decision, FEATURE_COLS, SEQ_LEN, LSTM_THRESHOLD

# -------------------------------------------------
# Fixed Monitoring Parameters (Improved Demo Defaults)
# -------------------------------------------------
SAMPLING_INTERVAL = 0.10   # Faster for demo
VISIBLE_TIMELINE_WINDOW = 80
MIX_STREAM = True
BEHAVIOR_MIX_BLOCK_SIZE = 25

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="R.A.P.P.T.R Security Console",
    page_icon="🛡️",
    layout="wide"
)

# -------------------------------------------------
# Custom CSS
# -------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0b0f17;
    color: #e5e7eb;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 98%;
}

.main-title {
    font-size: 36px;
    font-weight: 900;
    color: #00ffaa;
    letter-spacing: 1px;
    margin-bottom: 4px;
}

.sub-title {
    font-size: 15px;
    color: #9ca3af;
    margin-bottom: 8px;
}

.blink-critical {
    animation: blinkCritical 1s infinite;
}
@keyframes blinkCritical {
    0% { opacity: 1; box-shadow: 0 0 20px rgba(248,113,113,0.45); }
    50% { opacity: 0.78; box-shadow: 0 0 35px rgba(248,113,113,0.75); }
    100% { opacity: 1; box-shadow: 0 0 20px rgba(248,113,113,0.45); }
}

.status-banner {
    padding: 18px;
    border-radius: 18px;
    text-align: center;
    font-size: 24px;
    font-weight: 900;
    margin-bottom: 12px;
    border: 1px solid rgba(255,255,255,0.08);
}

.status-normal {
    background: linear-gradient(90deg, #0f5132, #14532d);
    color: white;
}

.status-elevated {
    background: linear-gradient(90deg, #7c5c00, #92400e);
    color: white;
}

.status-critical {
    background: linear-gradient(90deg, #7f1d1d, #991b1b);
    color: white;
}

.panel {
    background: #111827;
    padding: 18px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 0 20px rgba(0,0,0,0.25);
    margin-bottom: 12px;
}

.panel-title {
    font-size: 13px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}

.big-number {
    font-size: 28px;
    font-weight: 900;
    color: #f9fafb;
}

.phase-pill {
    display: inline-block;
    padding: 10px 14px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 14px;
    margin-top: 6px;
    border: 1px solid rgba(255,255,255,0.08);
}

.phase-normal {
    background-color: #14532d;
    color: white;
}

.phase-watch {
    background-color: #92400e;
    color: white;
}

.phase-critical {
    background-color: #991b1b;
    color: white;
}

.small-note {
    color: #9ca3af;
    font-size: 12px;
    margin-top: 4px;
}

.system-banner {
    padding: 14px;
    border-radius: 14px;
    text-align: center;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 12px;
    border: 1px solid rgba(255,255,255,0.08);
    background: linear-gradient(90deg, #1f2937, #111827);
    color: #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Title
# -------------------------------------------------
st.markdown('<div class="main-title">🛡️ R.A.P.P.T.R Security Console</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Real-Time Ransomware Monitoring, Anomaly Detection and Threat Escalation Console</div>',
    unsafe_allow_html=True
)
st.markdown("---")

# -------------------------------------------------
# Monitored Endpoint Panel
# -------------------------------------------------
st.markdown("### 🖥️ Monitored Endpoint")

endpoint_col1, endpoint_col2, endpoint_col3, endpoint_col4 = st.columns(4)
endpoint_col1.metric("Host", "DESKTOP-RPPTR")
endpoint_col2.metric("OS", "Windows")
endpoint_col3.metric("Monitoring Mode", "Behavioral Analysis")
endpoint_col4.metric("Detection Engine", "Hybrid RF + LSTM")

st.markdown("---")

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
st.sidebar.title("⚙️ Monitoring Controls")

data_path = "data/processed/test.csv"

start_button = st.sidebar.button("▶ Start Monitoring")
stop_button = st.sidebar.button("⏹ Stop Monitoring")
reset_button = st.sidebar.button("🔄 Reset Console")

st.sidebar.markdown("---")
st.sidebar.markdown("### Threat Escalation Logic")
st.sidebar.write("**CRITICAL** → RF confirms ransomware")
st.sidebar.write("**ELEVATED** → LSTM anomaly exceeds learned threshold")
st.sidebar.write("**NORMAL** → no active threat indicators")

st.sidebar.markdown("---")
st.sidebar.markdown("### Console Configuration")
st.sidebar.write(f"**Sampling Interval:** {SAMPLING_INTERVAL}s")
st.sidebar.write(f"**Timeline Window:** {VISIBLE_TIMELINE_WINDOW} steps")
st.sidebar.write(f"**Mixed Endpoint Activity:** Enabled")
st.sidebar.write(f"**Behavior Mixing Block Size:** {BEHAVIOR_MIX_BLOCK_SIZE}")
st.sidebar.write(f"**Sequence Length:** {SEQ_LEN}")

# -------------------------------------------------
# Session State
# -------------------------------------------------
if "running" not in st.session_state:
    st.session_state.running = False

if "history" not in st.session_state:
    st.session_state.history = []

if "buffer" not in st.session_state:
    st.session_state.buffer = []

if "step_index" not in st.session_state:
    st.session_state.step_index = 0

if "attack_started_at" not in st.session_state:
    st.session_state.attack_started_at = None

if "system_state" not in st.session_state:
    st.session_state.system_state = "IDLE"

if "demo_df" not in st.session_state:
    st.session_state.demo_df = None

# -------------------------------------------------
# Data Loader
# -------------------------------------------------
@st.cache_data
def load_and_prepare_data(path, mix_stream=True, chunk_size=25):
    df = pd.read_csv(path)

    if mix_stream:
        chunks = [df.iloc[i:i+chunk_size] for i in range(0, len(df), chunk_size)]
        rng = random.Random(42)
        rng.shuffle(chunks)
        df = pd.concat(chunks, ignore_index=True)

    return df

def build_demo_stream(df):
    """
    Create a presentation-friendly stream:
    BENIGN -> MIXED -> RANSOMWARE
    """
    if "label" not in df.columns:
        return df.copy()

    benign = df[df["label"] == 0].copy().reset_index(drop=True)
    ransomware = df[df["label"] == 1].copy().reset_index(drop=True)

    # Mixed transition zone
    mixed = df.sample(min(30, len(df)), random_state=42).reset_index(drop=True)

    benign_part = benign.iloc[:60] if len(benign) >= 60 else benign
    mixed_part = mixed.iloc[:30]
    ransomware_part = ransomware.iloc[:80] if len(ransomware) >= 80 else ransomware

    demo_df = pd.concat([benign_part, mixed_part, ransomware_part], ignore_index=True)
    return demo_df

try:
    df = load_and_prepare_data(
        data_path,
        mix_stream=MIX_STREAM,
        chunk_size=BEHAVIOR_MIX_BLOCK_SIZE
    )
except Exception as e:
    st.error(f"Dataset loading failed: {e}")
    st.stop()

# -------------------------------------------------
# Button Actions
# -------------------------------------------------
if start_button:
    st.session_state.running = True
    st.session_state.history = []
    st.session_state.attack_started_at = None
    st.session_state.system_state = "ACTIVE"

    # Build a realistic demo stream
    st.session_state.demo_df = build_demo_stream(df)
    active_df = st.session_state.demo_df

    # Preload only the initial benign sequence
    initial_rows = min(SEQ_LEN, len(active_df))
    st.session_state.buffer = [active_df.iloc[i] for i in range(initial_rows)]
    st.session_state.step_index = initial_rows

if stop_button:
    st.session_state.running = False
    st.session_state.system_state = "PAUSED"

if reset_button:
    st.session_state.running = False
    st.session_state.history = []
    st.session_state.buffer = []
    st.session_state.step_index = 0
    st.session_state.attack_started_at = None
    st.session_state.system_state = "IDLE"
    st.session_state.demo_df = None

# -------------------------------------------------
# Threat logic
# -------------------------------------------------
def classify_threat(decision):
    if "RANSOMWARE" in decision:
        return "CRITICAL", "status-critical", 100
    elif "SUSPICIOUS" in decision:
        return "ELEVATED", "status-elevated", 65
    else:
        return "NORMAL", "status-normal", 20

def detection_confidence(decision, rf_prob, lstm_score):
    if "RANSOMWARE" in decision:
        return min(99, int(rf_prob * 100))
    elif "SUSPICIOUS" in decision:
        ratio = min(1.0, lstm_score / max(LSTM_THRESHOLD, 1e-8))
        return int(55 + ratio * 40)
    return max(5, int(rf_prob * 40))

def attack_phase(decision):
    if "RANSOMWARE" in decision:
        return "ACTIVE ENCRYPTION / CONFIRMED THREAT", "phase-critical"
    elif "SUSPICIOUS" in decision:
        return "PRE-ENCRYPTION ANOMALY / ESCALATED WATCH", "phase-watch"
    return "BASELINE SYSTEM ACTIVITY", "phase-normal"

def analyze_attack_pattern(window_df):
    latest = window_df.iloc[-1]
    indicators = []

    if "disk_write_sum" in latest and latest["disk_write_sum"] > 1000:
        indicators.append("High disk write volume")

    if "active_writers" in latest and latest["active_writers"] > 5:
        indicators.append("Multiple active file writers")

    if "disk_write_rate" in latest and latest["disk_write_rate"] > 200:
        indicators.append("Abnormal write rate per process")

    if "process_count" in latest and latest["process_count"] > 50:
        indicators.append("Process activity spike")

    if "cpu_max" in latest and latest["cpu_max"] > 70:
        indicators.append("CPU surge during monitored activity")

    if not indicators:
        return ["No strong ransomware indicators detected"]

    return indicators

# -------------------------------------------------
# Layout placeholders
# -------------------------------------------------
system_banner_placeholder = st.empty()
banner_placeholder = st.empty()
row1_placeholder = st.empty()
row2_placeholder = st.empty()
row3_placeholder = st.empty()
row4_placeholder = st.empty()

# -------------------------------------------------
# Render function
# -------------------------------------------------
def render_console(history_df=None, latest=None, latest_window=None):
    # ---------------- System Status Banner ----------------
    if st.session_state.system_state == "IDLE":
        system_banner_placeholder.markdown(
            '<div class="system-banner">🟦 System Status: Idle — Ready to begin monitoring</div>',
            unsafe_allow_html=True
        )
    elif st.session_state.system_state == "PAUSED":
        system_banner_placeholder.markdown(
            '<div class="system-banner">⏸ System Status: Monitoring paused by analyst</div>',
            unsafe_allow_html=True
        )
    else:
        system_banner_placeholder.markdown(
            '<div class="system-banner">🟢 System Status: Monitoring active — Behavioral telemetry streaming</div>',
            unsafe_allow_html=True
        )

    if history_df is None or history_df.empty or latest is None:
        banner_placeholder.info("Press **Start Monitoring** to launch the R.A.P.P.T.R security console.")
        row1_placeholder.empty()
        row2_placeholder.empty()
        row3_placeholder.empty()
        row4_placeholder.empty()
        return

    threat_level, banner_class, threat_score = classify_threat(latest["decision"])
    confidence = detection_confidence(latest["decision"], latest["rf_prob"], latest["lstm_score"])
    phase_text, phase_class = attack_phase(latest["decision"])

    ransomware_count = (history_df["decision"].str.contains("RANSOMWARE")).sum()
    suspicious_count = (history_df["decision"].str.contains("SUSPICIOUS")).sum()
    benign_count = (history_df["decision"] == "BENIGN").sum()

    if threat_level == "CRITICAL":
        banner_text = "🚨 CRITICAL THREAT LEVEL — ACTIVE RANSOMWARE PATTERN DETECTED"
        banner_extra = "blink-critical"
    elif threat_level == "ELEVATED":
        banner_text = "⚠ ELEVATED THREAT LEVEL — ANOMALOUS FILE ACTIVITY DETECTED"
        banner_extra = ""
    else:
        banner_text = "✅ NORMAL THREAT LEVEL — SYSTEM BEHAVIOR WITHIN EXPECTED RANGE"
        banner_extra = ""

    with banner_placeholder.container():
        st.markdown(
            f'<div class="status-banner {banner_class} {banner_extra}">{banner_text}</div>',
            unsafe_allow_html=True
        )

    # ---------------- ROW 1 ----------------
    with row1_placeholder.container():
        c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])

        with c1:
            st.markdown(
                f'''
                <div class="panel">
                    <div class="panel-title">Current Threat Posture</div>
                    <div class="big-number">{threat_level}</div>
                    <div class="phase-pill {phase_class}">{phase_text}</div>
                    <div class="small-note">Operational state derived from RF + LSTM hybrid decision layer</div>
                </div>
                ''',
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                f'''
                <div class="panel">
                    <div class="panel-title">Detection Confidence</div>
                    <div class="big-number">{confidence}%</div>
                    <div class="small-note">Threat certainty estimate</div>
                </div>
                ''',
                unsafe_allow_html=True
            )

        with c3:
            st.markdown(
                f'''
                <div class="panel">
                    <div class="panel-title">RF Threat Score</div>
                    <div class="big-number">{latest["rf_prob"]*100:.1f}%</div>
                    <div class="small-note">Supervised ransomware classifier output</div>
                </div>
                ''',
                unsafe_allow_html=True
            )

        with c4:
            st.markdown(
                f'''
                <div class="panel">
                    <div class="panel-title">LSTM Anomaly Score</div>
                    <div class="big-number">{latest["lstm_score"]:.5f}</div>
                    <div class="small-note">Temporal anomaly reconstruction error</div>
                </div>
                ''',
                unsafe_allow_html=True
            )

    # ---------------- ROW 2 ----------------
    with row2_placeholder.container():
        left, right = st.columns([1.1, 1])

        with left:
            st.subheader("🎯 Threat Severity Gauge")

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=threat_score,
                title={"text": "Current Threat Severity"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"thickness": 0.35},
                    "steps": [
                        {"range": [0, 35], "color": "rgba(34,197,94,0.5)"},
                        {"range": [35, 75], "color": "rgba(250,204,21,0.5)"},
                        {"range": [75, 100], "color": "rgba(248,113,113,0.6)"}
                    ],
                    "threshold": {
                        "line": {"color": "white", "width": 4},
                        "thickness": 0.8,
                        "value": threat_score
                    }
                }
            ))
            fig_gauge.update_layout(template="plotly_dark", height=320)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with right:
            st.subheader("📌 Incident Snapshot")

            m1, m2 = st.columns(2)
            m3, m4 = st.columns(2)

            m1.metric("Critical Alerts", int(ransomware_count))
            m2.metric("Suspicious Alerts", int(suspicious_count))
            m3.metric("Normal Windows", int(benign_count))
            m4.metric("Detection Source", latest["source"])

            st.markdown("<br>", unsafe_allow_html=True)

            if st.session_state.attack_started_at:
                st.error(
                    f"🚨 Attack first detected at: {st.session_state.attack_started_at}\n"
                    f"System currently in active threat state"
                )
            else:
                st.success("No confirmed ransomware event timestamp recorded yet.")

    # ---------------- ROW 3 ----------------
    with row3_placeholder.container():
        st.subheader("📡 Live Threat Telemetry")

        recent_df = history_df.tail(VISIBLE_TIMELINE_WINDOW).copy()

        chart1, chart2 = st.columns(2)

        with chart1:
            fig_rf = px.line(
                recent_df,
                x="step",
                y="rf_prob",
                title="RF Threat Probability Timeline",
                markers=True
            )
            fig_rf.update_layout(
                template="plotly_dark",
                xaxis_title="Monitoring Step",
                yaxis_title="RF Threat Probability"
            )
            st.plotly_chart(fig_rf, use_container_width=True)

        with chart2:
            fig_lstm = px.line(
                recent_df,
                x="step",
                y="lstm_score",
                title="LSTM Sequence Anomaly Timeline",
                markers=True
            )
            fig_lstm.add_hline(
                y=LSTM_THRESHOLD,
                line_dash="dash",
                annotation_text="LSTM Alert Threshold"
            )
            fig_lstm.update_layout(
                template="plotly_dark",
                xaxis_title="Monitoring Step",
                yaxis_title="Anomaly Score"
            )
            st.plotly_chart(fig_lstm, use_container_width=True)

        threat_df = recent_df.copy()
        threat_df["threat_score"] = threat_df["decision"].apply(
            lambda x: 100 if "RANSOMWARE" in x else (65 if "SUSPICIOUS" in x else 20)
        )

        fig_threat = px.area(
            threat_df,
            x="step",
            y="threat_score",
            title="Threat Escalation Timeline"
        )
        fig_threat.update_layout(
            template="plotly_dark",
            xaxis_title="Monitoring Step",
            yaxis_title="Threat Severity"
        )
        st.plotly_chart(fig_threat, use_container_width=True)

    # ---------------- ROW 4 ----------------
    with row4_placeholder.container():
        left, right = st.columns([1.2, 1])

        with left:
            st.subheader("🧾 Live Incident Feed")
            feed_df = history_df.tail(15).iloc[::-1].copy()

            def style_decision(val):
                if "RANSOMWARE" in str(val):
                    return "color: #f87171; font-weight: bold;"
                elif "SUSPICIOUS" in str(val):
                    return "color: #facc15; font-weight: bold;"
                return "color: #4ade80; font-weight: bold;"

            st.dataframe(
                feed_df.style.map(style_decision, subset=["decision"]),
                use_container_width=True,
                height=420
            )

        with right:
            st.subheader("🛠 Recommended Response")

            if threat_level == "CRITICAL":
                st.error(
                    "Immediate containment recommended:\n"
                    "- Isolate suspicious process\n"
                    "- Stop write-heavy activity\n"
                    "- Preserve behavioral logs\n"
                    "- Trigger incident escalation"
                )
            elif threat_level == "ELEVATED":
                st.warning(
                    "Escalation recommended:\n"
                    "- Increase monitoring sensitivity\n"
                    "- Watch abnormal write bursts\n"
                    "- Validate sustained anomaly window"
                )
            else:
                st.success(
                    "No active threat escalation:\n"
                    "- Continue passive monitoring\n"
                    "- Maintain baseline logging"
                )

            st.markdown("<br>", unsafe_allow_html=True)

            st.subheader("🧠 Detected Behavior Patterns")

            if latest_window is not None:
                patterns = analyze_attack_pattern(latest_window)

                for p in patterns:
                    if "High" in p or "Abnormal" in p or "spike" in p or "surge" in p:
                        st.warning(f"⚠ {p}")
                    else:
                        st.info(f"• {p}")

            st.markdown("<br>", unsafe_allow_html=True)

            st.subheader("🧠 Current System Behavior Snapshot")
            if latest_window is not None:
                st.dataframe(latest_window.tail(8), use_container_width=True, height=260)

# -------------------------------------------------
# Monitoring loop
# -------------------------------------------------
active_df = st.session_state.demo_df if st.session_state.demo_df is not None else df

if st.session_state.running:

    if st.session_state.step_index >= len(active_df):
        st.session_state.running = False
        st.session_state.system_state = "PAUSED"
        st.success("✅ Monitoring stream completed.")
    else:
        row = active_df.iloc[st.session_state.step_index]
        st.session_state.buffer.append(row)

        if len(st.session_state.buffer) > SEQ_LEN:
            st.session_state.buffer.pop(0)

        if len(st.session_state.buffer) >= SEQ_LEN:
            window_df = pd.DataFrame(st.session_state.buffer)

            rf_prob, lstm_score, decision, source = hybrid_decision(window_df)

            if "RANSOMWARE" in decision and st.session_state.attack_started_at is None:
                st.session_state.attack_started_at = datetime.now().strftime("%H:%M:%S")

            log_row = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "step": st.session_state.step_index,
                "rf_prob": rf_prob,
                "lstm_score": lstm_score,
                "decision": decision,
                "source": source
            }

            st.session_state.history.append(log_row)

        st.session_state.step_index += 1

# -------------------------------------------------
# Static / Current Render
# -------------------------------------------------
if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    latest = st.session_state.history[-1]
    latest_window = pd.DataFrame(st.session_state.buffer)[FEATURE_COLS] if st.session_state.buffer else None
    render_console(history_df, latest, latest_window)
else:
    render_console()

# -------------------------------------------------
# Auto-refresh loop
# -------------------------------------------------
if st.session_state.running:
    time.sleep(SAMPLING_INTERVAL)
    st.rerun()
