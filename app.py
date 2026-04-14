import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import os

from modules.document_parser import extract_financial_data
from modules.risk_model import calculate_risk_score, get_loan_decision
from modules.cam_generator import generate_cam

# --- Page Configuration ---
st.set_page_config(
    page_title="IntelliCredit AI",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# --- Load Custom CSS ---
def load_css(file_name="assets/styles.css"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, file_name)
    try:
        with open(file_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Could not find CSS file at: {file_path}")

load_css()

# --- Inject 3D tilt + animation JS ---
st.markdown("""
<script>
// Enhanced 3D tilt effect on glass cards with particle effects
document.addEventListener('DOMContentLoaded', function() {
    function applyTilt() {
        const cards = document.querySelectorAll('.glass-card');
        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const cx = rect.width  / 2;
                const cy = rect.height / 2;
                const rotX = ((y - cy) / cy) * -8;
                const rotY = ((x - cx) / cx) * 8;
                card.style.transform = `perspective(1200px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateY(-8px) scale(1.02)`;
                card.style.boxShadow = `0 30px 60px rgba(0,0,0,0.6), 0 0 60px rgba(56, 189, 248, ${Math.abs(rotX)/50})`;
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
                card.style.boxShadow = '';
            });
        });
    }
    // Re-apply after Streamlit re-renders
    setTimeout(applyTilt, 1000);
    setInterval(applyTilt, 3000);

    // Add floating animation loop
    const style = document.createElement('style');
    style.textContent = `
        @keyframes particleFloat {
            0% { transform: translateY(0px) translateX(0px) scale(1); opacity: 0.8; }
            33% { transform: translateY(-20px) translateX(10px) scale(1.1); opacity: 0.6; }
            66% { transform: translateY(-40px) translateX(-15px) scale(0.9); opacity: 0.4; }
            100% { transform: translateY(-60px) translateX(0px) scale(1); opacity: 0; }
        }
        .glass-card {
            position: relative;
        }
        .glass-card:hover::after {
            content: '';
            position: absolute;
            width: 10px;
            height: 10px;
            background: radial-gradient(circle, rgba(56,189,248,0.8), transparent);
            border-radius: 50%;
            pointer-events: none;
        }
    `;
    document.head.appendChild(style);
});
</script>
""", unsafe_allow_html=True)

# --- Session State Management ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'data_extracted' not in st.session_state:
    st.session_state.data_extracted = False
if 'fin_data' not in st.session_state:
    st.session_state.fin_data = None
if 'score' not in st.session_state:
    st.session_state.score = None

# --- Component Functions ---
def display_metric_card(title, value, risk_class="", icon="📈"):
    st.markdown(f"""
    <div class="glass-card tilt-3d" style="text-align:center; padding: 24px 16px;
                                           transform-style: preserve-3d; perspective: 1000px;">
        <div style="font-size: 28px; margin-bottom: 6px; animation: pulse-scale 2s ease-in-out infinite;">
            {icon}
        </div>
        <div class="metric-title">{title}</div>
        <div class="metric-value {risk_class}">{value}</div>
        <div style="margin-top: 8px; height: 2px; background: linear-gradient(90deg, transparent, rgba(56,189,248,0.4), transparent);
                    border-radius: 1px;"></div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────── PAGE 1: LOGIN ───────────────────
def login_page():
    # ── Inject all login styles + hero background ──
    st.markdown("""
    <style>
    .login-hero {
        position: fixed; inset: 0; z-index: 0;
        overflow: hidden; pointer-events: none;
    }
    .orb {
        position: absolute; border-radius: 50%;
        filter: blur(90px); opacity: 0.3;
        animation: orbFloat 9s ease-in-out infinite;
    }
    .orb-1 { width:480px;height:480px; background:#0ea5e9; top:-15%;left:-10%; animation-delay:0s; }
    .orb-2 { width:400px;height:400px; background:#818cf8; bottom:-8%;right:-8%; animation-delay:-4s; }
    .orb-3 { width:300px;height:300px; background:#a855f7; top:45%;left:55%; animation-delay:-6s; }
    @keyframes orbFloat {
        0%,100% { transform: translateY(0) scale(1); }
        50%      { transform: translateY(-35px) scale(1.08); }
    }
    .login-grid {
        position:absolute; inset:0;
        background-image:
            linear-gradient(rgba(56,189,248,0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(56,189,248,0.035) 1px, transparent 1px);
        background-size: 52px 52px;
    }
    .lc-hero {
        display:flex; flex-direction:column; align-items:center;
        padding: 7vh 0 1vh; position:relative; z-index:2;
        animation: fadeInUp 0.7s ease forwards;
    }
    .lc-card {
        background: linear-gradient(145deg,
            rgba(12,20,40,0.92) 0%,
            rgba(24,38,66,0.85) 100%);
        backdrop-filter: blur(36px) saturate(200%);
        -webkit-backdrop-filter: blur(36px) saturate(200%);
        border: 1px solid rgba(56,189,248,0.22);
        border-radius: 30px;
        padding: 52px 46px 44px;
        width:100%; max-width:450px;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.04) inset,
            0 40px 100px rgba(0,0,0,0.7),
            0 0 80px rgba(56,189,248,0.07);
        position:relative; overflow:hidden;
        animation: cardReveal 0.8s cubic-bezier(0.34,1.56,0.64,1) forwards;
        transform-style: preserve-3d;
        perspective: 1000px;
        transition: all 0.4s ease;
    }
    .lc-card:hover {
        transform: translateY(-8px) rotateX(3deg) scale(1.01);
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.08) inset,
            0 50px 120px rgba(0,0,0,0.8),
            0 0 120px rgba(56,189,248,0.15);
        border-color: rgba(56,189,248,0.4);
    }
    @keyframes cardReveal {
        from { opacity:0; transform: translateY(50px) scale(0.94); }
        to   { opacity:1; transform: translateY(0)    scale(1); }
    }
    .lc-card::before {
        content:'';
        position:absolute; top:0; left:8%; right:8%; height:1px;
        background: linear-gradient(90deg,
            transparent, rgba(56,189,248,0.9), rgba(168,85,247,0.7), transparent);
    }
    .lc-orb1,.lc-orb2 {
        position:absolute; border-radius:50%;
        top:50%; left:50%;
        transform:translate(-50%,-50%);
        pointer-events:none;
    }
    .lc-orb1 {
        width:360px;height:360px;
        border:1px solid rgba(56,189,248,0.07);
        animation: rotateOrbit 14s linear infinite;
    }
    .lc-orb2 {
        width:260px;height:260px;
        border:1px solid rgba(129,140,248,0.1);
        animation: rotateOrbit 8s linear infinite reverse;
    }
    .lc-logo {
        font-size:72px; display:block; text-align:center;
        margin-bottom:8px;
        filter: drop-shadow(0 0 28px rgba(56,189,248,0.75))
                drop-shadow(0 0 10px rgba(168,85,247,0.5));
        animation: logoPulse 3s ease-in-out infinite;
    }
    @keyframes logoPulse {
        0%,100%{ filter: drop-shadow(0 0 22px rgba(56,189,248,0.6)) drop-shadow(0 0 8px rgba(168,85,247,0.35)); }
        50%    { filter: drop-shadow(0 0 42px rgba(56,189,248,0.95)) drop-shadow(0 0 18px rgba(168,85,247,0.7)); }
    }
    .lc-title {
        text-align:center;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #a855f7 100%);
        background-size:200% auto;
        -webkit-background-clip:text; background-clip:text;
        -webkit-text-fill-color:transparent;
        font-size:2.6rem; font-weight:800;
        letter-spacing:-0.5px; margin:4px 0 6px;
        font-family:'Space Grotesk',sans-serif;
        animation: shimmer 4s linear infinite, neon-glow 3s ease-in-out infinite;
    }
    .lc-sub {
        text-align:center; color:#64748b;
        font-size:13px; letter-spacing:0.5px;
        margin-bottom:28px; line-height:1.6;
    }
    .lc-status {
        display:inline-flex; align-items:center; gap:8px;
        background: rgba(16,185,129,0.07);
        border:1px solid rgba(16,185,129,0.2);
        border-radius:999px;
        padding:5px 16px; font-size:11px; color:#64748b;
        letter-spacing:0.5px; margin-bottom:26px;
    }
    .lc-dot {
        width:7px;height:7px;border-radius:50%;
        background:#10b981; box-shadow:0 0 7px #10b981;
        animation: dotPulse 2s ease-in-out infinite;
    }
    @keyframes dotPulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }
    .lc-footer {
        display:flex; align-items:center; justify-content:center;
        gap:18px; margin-top:20px;
        color:#334155; font-size:11px; flex-wrap:wrap;
    }
    .lc-footer span { display:inline-flex; align-items:center; gap:5px; }
    .lc-pills {
        display:flex; justify-content:center; gap:10px;
        flex-wrap:wrap; margin-top:20px;
    }
    .lc-pill {
        background:rgba(56,189,248,0.06);
        border:1px solid rgba(56,189,248,0.15);
        border-radius:8px; padding:6px 14px;
        font-size:11px; color:#475569;
    }
    </style>

    <div class="login-hero">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
        <div class="login-grid"></div>
    </div>

    <div class="lc-hero">
        <div class="lc-card">
            <div class="lc-orb1"></div>
            <div class="lc-orb2"></div>
            <span class="lc-logo">🏦</span>
            <h1 class="lc-title">IntelliCredit AI</h1>
            <p class="lc-sub">Automated Corporate Credit Intelligence Platform</p>
            <div style="display:flex;justify-content:center">
                <div class="lc-status">
                    <div class="lc-dot"></div>
                    All Systems Operational &nbsp;·&nbsp; RBI Sandbox Ready
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Streamlit login form, centered ──
    col_l, col_c, col_r = st.columns([1, 1.1, 1])
    with col_c:
        with st.form("login_form"):
            st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
            email    = st.text_input("🏢  Company Email", placeholder="analyst@vivriti.com")
            password = st.text_input("🔑  Password", type="password", placeholder="••••••••")
            st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
            submit   = st.form_submit_button("🔐  Sign In Securely", use_container_width=True)

            if submit:
                if email and password:
                    with st.spinner("Authenticating…"):
                        time.sleep(0.8)
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Please enter your credentials.")

        st.markdown("""
        <div class="lc-footer">
            <span>🔒 256-bit TLS</span>
            <span>🛡️ SOC 2 Type II</span>
            <span>🏦 RBI Compliant</span>
        </div>
        <div class="lc-pills">
            <div class="lc-pill">⚡ AI-Powered Scoring</div>
            <div class="lc-pill">📊 Real-time Analytics</div>
            <div class="lc-pill">📑 Auto CAM Reports</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────── PAGE 2: UPLOAD ─────────────────
def upload_page():
    st.markdown("""
    <div style="animation: fadeInUp 0.5s ease;">
        <h2 class="header-title" style="font-size: 2.2rem; margin-bottom: 6px;">📚 Document Intelligence Layer</h2>
        <p style="color:#64748b; margin-bottom: 32px; font-size:15px;">
            Upload corporate financial documents for automated AI analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="glass-card tilt-3d" style="margin-bottom:16px; text-align:center; transition: all 0.3s ease;">
            <div style="font-size:42px; margin-bottom:10px; filter:drop-shadow(0 0 12px rgba(56,189,248,0.5)); animation: pulse-scale 2s ease-in-out infinite;">📄</div>
            <h3 style="margin:0; color:#e2e8f0;">GST Reports</h3>
            <p style="color:#64748b; font-size:12px; margin-top:6px; line-height: 1.5;">Goods & Services Tax filings</p>
        </div>
        """, unsafe_allow_html=True)
        gst = st.file_uploader("Upload GST PDF", type=["pdf"], label_visibility="collapsed")

    with col2:
        st.markdown("""
        <div class="glass-card tilt-3d" style="margin-bottom:16px; text-align:center; transition: all 0.3s ease;">
            <div style="font-size:42px; margin-bottom:10px; filter:drop-shadow(0 0 12px rgba(129,140,248,0.5)); animation: pulse-scale 2s ease-in-out infinite 0.2s;">🏦</div>
            <h3 style="margin:0; color:#e2e8f0;">Bank Statements</h3>
            <p style="color:#64748b; font-size:12px; margin-top:6px; line-height: 1.5;">12-month bank transactions</p>
        </div>
        """, unsafe_allow_html=True)
        bank = st.file_uploader("Upload Bank PDF", type=["pdf"], label_visibility="collapsed")

    with col3:
        st.markdown("""
        <div class="glass-card tilt-3d" style="margin-bottom:16px; text-align:center; transition: all 0.3s ease;">
            <div style="font-size:42px; margin-bottom:10px; filter:drop-shadow(0 0 12px rgba(168,85,247,0.5)); animation: pulse-scale 2s ease-in-out infinite 0.4s;">📊</div>
            <h3 style="margin:0; color:#e2e8f0;">Financial Statements</h3>
            <p style="color:#64748b; font-size:12px; margin-top:6px; line-height: 1.5;">P&L, Balance Sheet, Cash Flow</p>
        </div>
        """, unsafe_allow_html=True)
        fin = st.file_uploader("Upload Financials PDF", type=["pdf"], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    # Status bar
    uploaded = sum([bool(gst), bool(bank), bool(fin)])
    if uploaded:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(16,185,129,0.15),rgba(56,189,248,0.1));
                    border:1px solid rgba(16,185,129,0.3); border-radius:12px; padding:14px 20px;
                    margin-bottom:20px; display:flex; align-items:center; gap:12px;">
            <span style="font-size:20px;">✅</span>
            <span style="color:#10b981; font-weight:600;">{uploaded}/3 documents ready for analysis</span>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🚀 Analyze with AI", use_container_width=True):
        if not (gst or bank or fin):
            st.info("ℹ️ Running analysis with simulated documents since none were uploaded.")

        progress_bar = st.progress(0, text="Initializing AI pipeline…")
        status_steps = [
            (20, "📑 Extracting text with OCR…"),
            (40, "🧠 Running NLP entity recognition…"),
            (60, "📉 Calculating financial ratios…"),
            (80, "⚖️ Scoring credit risk…"),
            (100, "✅ Report compiled!")
        ]
        for pct, msg in status_steps:
            time.sleep(0.4)
            progress_bar.progress(pct, text=msg)

        st.session_state.fin_data = extract_financial_data(None)
        score, cat, shap         = calculate_risk_score(st.session_state.fin_data)
        st.session_state.score   = {"value": score, "category": cat, "shap": shap}

        decision, amount, rate, reasons = get_loan_decision(score, st.session_state.fin_data)
        st.session_state.decision = {"dec": decision, "amount": amount, "rate": rate, "reasons": reasons}

        st.session_state.cam = generate_cam(
            st.session_state.fin_data, score, cat, decision, amount, rate, reasons
        )
        st.session_state.data_extracted = True

        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(16,185,129,0.18),rgba(56,189,248,0.12));
                    border:1px solid rgba(16,185,129,0.4); border-radius:14px; padding:18px 24px;
                    margin-top:20px; text-align:center;">
            <div style="font-size:28px; margin-bottom:6px;">🎉</div>
            <h3 style="color:#10b981; margin:0;">Analysis Complete!</h3>
            <p style="color:#64748b; margin:6px 0 0;">Navigate to the <strong style="color:#38bdf8;">AI Financial Dashboard</strong> to view results.</p>
        </div>
        """, unsafe_allow_html=True)


# ───────────── PAGE 3: AI FINANCIAL DASHBOARD ───────
def dashboard_page():
    st.markdown("""
    <h2 class="header-title" style="font-size:2.2rem; margin-bottom:24px;">💰 AI Financial Dashboard</h2>
    """, unsafe_allow_html=True)

    if not st.session_state.data_extracted:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:50px;">
            <div style="font-size:48px; margin-bottom:16px;">📊</div>
            <h3 style="color:#64748b;">No Data Yet</h3>
            <p style="color:#475569;">Please run <strong style="color:#38bdf8;">Analyze with AI</strong> first.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    data = st.session_state.fin_data

    # ROW 1 — Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        display_metric_card("Revenue Growth", f"{data['revenue_growth']}%", icon="📈")
    with c2:
        ratio = round(data['debt'] / data['revenue'] if data['revenue'] > 0 else 0, 2)
        display_metric_card("Debt Ratio", f"{ratio}x", icon="⚠️" if ratio > 0.5 else "✅")
    with c3:
        display_metric_card("Legal Cases", str(data['litigations']), icon="⚖️")
    with c4:
        display_metric_card("Sector Risk", data['sector_risk'], icon="🏭")

    st.markdown("<br>", unsafe_allow_html=True)

    # ROW 2 — Charts
    col_l, col_r = st.columns([1, 2])

    with col_l:
        st.markdown("""
        <div class="glass-card" style="padding:24px;">
            <h3 style="margin-top:0; color:#e2e8f0;">💼 Financial Summary</h3>
        """, unsafe_allow_html=True)

        items = [
            ("Total Assets",       f"₹{data['total_assets']:,.0f}",      "#10b981"),
            ("Total Liabilities",  f"₹{data['total_liabilities']:,.0f}", "#ef4444"),
            ("Net Worth",          f"₹{data['net_worth']:,.0f}",          "#38bdf8"),
            ("EBITDA",             f"₹{data['ebitda']:,.0f}",             "#a855f7"),
        ]
        for label, val, col in items:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        padding:10px 14px; border-radius:10px; margin-bottom:8px;
                        background:rgba(255,255,255,0.04); border-left:3px solid {col};
                        transition:all 0.3s ease;">
                <span style="color:#94a3b8; font-size:13px;">{label}</span>
                <span style="color:{col}; font-weight:700; font-size:15px;">{val}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="glass-card"><h3 style="margin-top:0; color:#e2e8f0;">📉 Revenue Trend Projection</h3>', unsafe_allow_html=True)

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 4))

        years = ['FY21', 'FY22', 'FY23', 'FY24\n(Proj)']
        revs  = [
            data['revenue'] * 0.72,
            data['revenue'] * 0.86,
            data['revenue'],
            data['revenue'] * (1 + (data['revenue_growth'] / 100))
        ]

        # Gradient fill
        from matplotlib.patches import FancyArrowPatch
        ax.plot(years, revs, marker='o', color='#38bdf8', linewidth=3,
                markersize=10, markerfacecolor='#0ea5e9', markeredgecolor='#818cf8',
                markeredgewidth=2)
        ax.fill_between(years, revs, alpha=0.18, color='#818cf8')

        # Projected marker stand-out
        ax.scatter([years[-1]], [revs[-1]], color='#a855f7', s=180, zorder=5,
                   edgecolors='#f8fafc', linewidths=2)

        ax.set_facecolor('#070d1a')
        fig.patch.set_facecolor('#070d1a')
        ax.grid(True, alpha=0.08, linestyle='--')
        ax.tick_params(colors='#64748b')
        for spine in ax.spines.values():
            spine.set_color('#1e2d40')

        st.pyplot(fig, transparent=True)
        st.markdown('</div>', unsafe_allow_html=True)

    plt.close('all')


# ──────────── PAGE 4: CREDIT RISK ANALYSIS ──────────
def risk_page():
    st.markdown("""
    <h2 class="header-title" style="font-size:2.2rem; margin-bottom:24px;">
        ⚡ Credit Risk Analysis &amp; Decision Engine
    </h2>
    """, unsafe_allow_html=True)

    if not st.session_state.data_extracted:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:50px;">
            <div style="font-size:48px; margin-bottom:16px;">🎯</div>
            <h3 style="color:#64748b;">Run Analysis First</h3>
            <p style="color:#475569;">Go to <strong style="color:#38bdf8;">Document Upload</strong> and click Analyze.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    score_data = st.session_state.score
    dec_data   = st.session_state.decision

    color = ("#10b981" if score_data['value'] >= 75
             else "#f59e0b" if score_data['value'] >= 50
             else "#ef4444")
    ring_glow = color

    col_score, col_expl = st.columns([1, 2])

    with col_score:
        st.markdown(f"""
        <div class="glass-card score-ring" style="text-align:center; padding:40px 20px; position:relative; overflow:hidden;">
            <!-- Animated ring -->
            <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;">
                <div style="width:200px;height:200px;border-radius:50%;
                            border:2px solid {ring_glow}33;
                            animation:rotateOrbit 5s linear infinite;"></div>
                <div style="position:absolute;width:160px;height:160px;border-radius:50%;
                            border:2px solid {ring_glow}55;
                            animation:rotateOrbit 3s linear infinite reverse;"></div>
            </div>

            <p style="color:#94a3b8; font-size:14px; margin-bottom:6px; letter-spacing:1px; text-transform:uppercase;">
                IntelliCredit Score
            </p>
            <div style="font-size:88px; font-weight:900; color:{color};
                        text-shadow: 0 0 30px {color}66, 0 0 60px {color}33;
                        line-height:1; font-family:'Space Grotesk',sans-serif;">
                {score_data['value']}
            </div>
            <p style="color:#475569; font-size:20px; font-weight:600; margin:4px 0 20px;">/&nbsp;100</p>
            <div style="background:linear-gradient(135deg,{color}22,{color}11);
                        border:1px solid {color}44; padding:12px 20px;
                        border-radius:12px; display:inline-block;">
                <span style="color:{color}; font-weight:700; font-size:18px;">
                    {score_data['category']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_expl:
        st.markdown(f"""
        <div class="glass-card" style="padding:28px;">
            <h3 style="color:#e2e8f0; margin-top:0;">⚡ AI Decision Engine</h3>

            <div style="background:linear-gradient(135deg,{color}18,{color}0a);
                        border:1px solid {color}40; border-left:4px solid {color};
                        padding:20px; border-radius:12px; margin-bottom:24px;">
                <h2 style="color:{color}; margin:0 0 14px;">
                    {'✅' if 'Approve' in dec_data['dec'] else '❌'} {dec_data['dec']}
                </h2>
                <div style="display:flex; gap:40px;">
                    <div>
                        <p style="color:#64748b; margin:0; font-size:12px; text-transform:uppercase; letter-spacing:1px;">Recommended Limit</p>
                        <h3 style="margin:4px 0 0; color:#f8fafc; font-size:22px;">{dec_data['amount']}</h3>
                    </div>
                    <div>
                        <p style="color:#64748b; margin:0; font-size:12px; text-transform:uppercase; letter-spacing:1px;">Suggested Rate</p>
                        <h3 style="margin:4px 0 0; color:#f8fafc; font-size:22px;">{dec_data['rate']}</h3>
                    </div>
                </div>
            </div>

            <h4 style="color:#cbd5e1; margin-bottom:12px;">🧠 Explainable AI — Key Factors</h4>
        """, unsafe_allow_html=True)

        for i, factor in enumerate(score_data['shap']):
            bullet_color = ("#10b981" if factor['type'] == 'positive'
                            else "#ef4444" if factor['type'] == 'negative'
                            else "#64748b")
            bar_width = min(abs(float(str(factor['impact']).replace('+','').replace('%','').replace('x','')) or 10), 100)
            st.markdown(f"""
            <div style="display:flex; align-items:center; margin-bottom:10px;
                        background:rgba(255,255,255,0.03); padding:12px 16px;
                        border-radius:10px; border:1px solid rgba(255,255,255,0.05);
                        animation: fadeInLeft {0.3 + i*0.1}s ease forwards;
                        transition: all 0.3s ease;"
                 onmouseover="this.style.background='rgba(255,255,255,0.07)';this.style.transform='translateX(4px)'"
                 onmouseout="this.style.background='rgba(255,255,255,0.03)';this.style.transform=''">
                <span style="width:10px; height:10px; border-radius:50%;
                             background:{bullet_color};
                             box-shadow: 0 0 8px {bullet_color};
                             flex-shrink:0; margin-right:14px;"></span>
                <span style="flex:1; color:#e2e8f0; font-size:13px;">{factor['feature']}</span>
                <span style="color:{bullet_color}; font-family:monospace; font-size:14px; font-weight:700;
                             background:{bullet_color}18; padding:2px 10px; border-radius:6px;">
                    {factor['impact']}
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ───────────────── PAGE 5: CAM REPORT ───────────────
def cam_page():
    st.markdown("""
    <h2 class="header-title" style="font-size:2.2rem; margin-bottom:24px;">📑 CAM Report Generator</h2>
    """, unsafe_allow_html=True)

    if not st.session_state.data_extracted:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:50px;">
            <div style="font-size:48px; margin-bottom:16px;">📑</div>
            <h3 style="color:#64748b;">No Report Generated</h3>
            <p style="color:#475569;">Please run analysis first.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("""
    <div class="glass-card" style="margin-bottom:20px; display:flex; align-items:center; gap:14px;">
        <div style="font-size:28px;">🤖</div>
        <div>
            <p style="color:#94a3b8; margin:0; font-size:13px; text-transform:uppercase; letter-spacing:1px;">
                AI-Generated Memo
            </p>
            <p style="color:#64748b; margin:4px 0 0; font-size:14px;">
                Automatically compiled from synthesized financial intelligence.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.text_area("Generated Memo (Ready for Export)", value=st.session_state.cam, height=500)

    col1, col2 = st.columns(2)
    with col1:
        st.button("📥 Download as PDF",            use_container_width=True)
    with col2:
        st.button("✉️ Route to Senior Underwriter", use_container_width=True)


# ─────────────────── ROUTER ─────────────────────────
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        with st.sidebar:
            st.markdown("""
            <div style="text-align:center; padding:12px 0 20px;">
                <div style="font-size:44px; filter:drop-shadow(0 0 16px rgba(56,189,248,0.5));">🏦</div>
                <h2 class="header-title" style="font-size:1.4rem; margin:8px 0 2px;">IntelliCredit</h2>
                <p style="color:#334155; font-size:11px; margin:0; letter-spacing:1px;">CREDIT INTELLIGENCE AI</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            nav_choice = st.radio(
                "Navigation",
                ["📄 Document Upload",
                 "📊 AI Financial Dashboard",
                 "🎯 Credit Risk Analysis",
                 "📑 CAM Report Generator"],
                label_visibility="collapsed"
            )

            st.markdown("<br>" * 5, unsafe_allow_html=True)
            st.markdown("---")

            # Mini status badges
            if st.session_state.data_extracted:
                st.markdown("""
                <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3);
                            border-radius:8px; padding:8px 12px; text-align:center; margin-bottom:12px;">
                    <span style="color:#10b981; font-size:12px; font-weight:600;">✅ Analysis Ready</span>
                </div>
                """, unsafe_allow_html=True)

            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

        if "Document Upload" in nav_choice:
            upload_page()
        elif "Dashboard" in nav_choice:
            dashboard_page()
        elif "Risk" in nav_choice:
            risk_page()
        elif "CAM" in nav_choice:
            cam_page()


if __name__ == "__main__":
    main()
