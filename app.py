"""
AI Decision Simulator System
Main Streamlit UI — app entry point
"""

import streamlit as st
import os
import json
from utils.risk_calculator import risk_level_label, risk_color
from utils.helpers import percentage, score_label


# PAGE CONFIG

st.set_page_config(
    page_title="AI Decision Simulator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CUSTOM CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* Dark theme overrides */
.stApp {
    background: #0a0e1a;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f1424;
    border-right: 1px solid #1e2a45;
}

/* Cards */
.sim-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}

.sim-card-accent {
    background: linear-gradient(135deg, #0f172a 0%, #1a1f35 100%);
    border: 1px solid #3b82f6;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}

/* Section headers */
.section-title {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 12px;
}

/* Decision type badge */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 500;
    background: #1e3a5f;
    color: #60a5fa;
    border: 1px solid #2563eb44;
    margin-right: 6px;
    margin-bottom: 6px;
}

/* Risk bar container */
.risk-bar-bg {
    background: #1e293b;
    border-radius: 999px;
    height: 8px;
    width: 100%;
    overflow: hidden;
    margin-top: 4px;
}

/* Scenario card */
.scenario-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}

.scenario-card.best {
    border-color: #3b82f6;
    background: linear-gradient(135deg, #0f172a 0%, #112240 100%);
}

/* Metric numbers */
.big-metric {
    font-size: 36px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}

/* Recommendation box */
.recommendation-box {
    background: linear-gradient(135deg, #0d2137 0%, #0f2d4a 100%);
    border: 2px solid #3b82f6;
    border-radius: 16px;
    padding: 28px 32px;
    margin-top: 8px;
}

/* Warning pill */
.warning-pill {
    background: #2d1b00;
    border: 1px solid #f97316;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #fed7aa;
}

.success-pill {
    background: #052e16;
    border: 1px solid #22c55e;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #bbf7d0;
}

/* Timeline action step */
.action-step {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #1e293b;
}

.step-num {
    background: #1e3a5f;
    color: #60a5fa;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    flex-shrink: 0;
    font-family: 'JetBrains Mono', monospace;
}

/* Impact chip */
.impact-positive {
    background: #052e16;
    border: 1px solid #166534;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    color: #86efac;
    margin-bottom: 6px;
}

.impact-negative {
    background: #2d0e0e;
    border: 1px solid #991b1b;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    color: #fca5a5;
    margin-bottom: 6px;
}

/* Divider */
.sim-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #1e293b, transparent);
    margin: 24px 0;
}

/* Hero title */
.hero-title {
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    margin-bottom: 6px;
}

.hero-sub {
    font-size: 16px;
    color: #64748b;
    margin-bottom: 32px;
}

/* Tabs */
[data-testid="stTab"] {
    font-size: 13px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# SESSION STATE INIT
if "result" not in st.session_state:
    st.session_state.result = None
if "error" not in st.session_state:
    st.session_state.error = None
if "running" not in st.session_state:
    st.session_state.running = False

# SIDEBAR
with st.sidebar:
    st.markdown("### 📖 About")
    st.markdown("""
    **AI Decision Simulator** uses a multi-agent pipeline:

    1. 🔍 **Context Analyzer** — understands your problem  
    2. 🌐 **Scenario Generator** — builds future paths  
    3. 🎯 **Outcome Predictor** — forecasts impacts  
    4. ⚖️ **Decision Engine** — ranks & recommends  

    All AI agents are powered by **Google Gemini**.
    """)

    st.markdown("---")
    st.markdown("### 💡 Example Problems")
    examples = [
        "Should I switch jobs to a startup for 30% more pay?",
        "Should I relocate to another country for my career?",
        "Should I start my own business or stay employed?",
        "Should I invest my savings in real estate or stocks?",
        "Should I go back to school for a master's degree?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True, key=f"ex_{ex[:20]}"):
            st.session_state["example_input"] = ex
            st.rerun()

    # History section
    st.markdown("---")
    st.markdown("### 🗂️ History")
    history_file = os.path.join(os.path.dirname(__file__), "data", "history.json")
    if os.path.exists(history_file):
        try:
            with open(history_file) as f:
                history = json.load(f)
            if history:
                st.caption(f"{len(history)} past decision(s) stored")
                for h in reversed(history[-5:]):
                    st.caption(f"• {h['user_input'][:50]}…" if len(h['user_input']) > 50 else f"• {h['user_input']}")
            else:
                st.caption("No history yet")
        except Exception:
            st.caption("No history yet")

# MAIN CONTENT
st.markdown('<div class="hero-title">AI Decision Simulator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Enter a decision problem. Multi-agent AI will simulate scenarios, predict outcomes, and recommend the best path.</div>', unsafe_allow_html=True)

# Input area 
col_input, col_btn = st.columns([5, 1])

default_input = st.session_state.pop("example_input", "")

with col_input:
    user_input = st.text_area(
        "Your Decision Problem",
        value=default_input,
        height=100,
        placeholder="Example: Should I switch jobs to a startup offering 30% more pay but higher risk?",
        label_visibility="collapsed",
    )

with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    analyze_btn = st.button("🧠 Analyze", use_container_width=True, type="primary")


#  Run pipeline 
if analyze_btn:
    if not user_input.strip():
        st.warning("Please describe your decision problem.")
    else:
        st.session_state.result = None
        st.session_state.error = None

        with st.spinner("🤖 Running multi-agent simulation..."):
            try:
                import sys
                sys.path.insert(0, os.path.dirname(__file__))
                from core.pipeline import DecisionPipeline

                pipeline = DecisionPipeline()
                result = pipeline.run(user_input)
                st.session_state.result = result
            except Exception as e:
                st.session_state.error = str(e)


#  Error display 
if st.session_state.error:
    st.error(f"❌ Simulation failed: {st.session_state.error}")

# Results
if st.session_state.result:
    result = st.session_state.result
    context = result.get("context", {})
    scenarios_data = result.get("scenarios", {}).get("scenarios", [])
    outcomes_data = result.get("outcomes", {}).get("outcomes", [])
    risk_scores = result.get("risk_scores", {})
    final = result.get("final_decision", {})

    # Build lookup maps
    outcome_map = {o["scenario_id"]: o for o in outcomes_data}

    st.markdown('<div class="sim-divider"></div>', unsafe_allow_html=True)

    #  TABS 
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Overview",
        "🌐 Scenarios",
        "🎯 Outcomes",
        "📊 Risk Analysis",
        "✅ Recommendation",
    ])
    # TAB 1: OVERVIEW
    with tab1:
        st.markdown("#### Problem Summary")
        st.markdown(f"""<div class="sim-card">
            <p style="font-size:18px; font-weight:500; color:#e2e8f0; margin:0 0 12px 0">
                {context.get('problem_summary', user_input)}
            </p>
        </div>""", unsafe_allow_html=True)

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("Decision Type", context.get("decision_type", "—").title())
        with col_b:
            st.metric("Urgency", context.get("urgency", "—").title())
        with col_c:
            st.metric("Complexity", context.get("complexity", "—").title())
        with col_d:
            st.metric("Time Horizon", context.get("time_horizon", "—"))

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div class="section-title">🎯 Primary Goal</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="sim-card">{context.get('primary_goal', '—')}</div>""", unsafe_allow_html=True)

            st.markdown('<div class="section-title">📌 Constraints</div>', unsafe_allow_html=True)
            constraints = context.get("constraints", [])
            items = "".join([f"<div class='badge'>{c}</div>" for c in constraints]) if constraints else "None identified"
            st.markdown(f"""<div class="sim-card">{items}</div>""", unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="section-title">🔑 Key Factors</div>', unsafe_allow_html=True)
            factors = context.get("key_factors", [])
            factor_html = "".join([f"<div style='padding:4px 0; color:#94a3b8; font-size:14px'>• {f}</div>" for f in factors])
            st.markdown(f"""<div class="sim-card">{factor_html or '—'}</div>""", unsafe_allow_html=True)

            st.markdown('<div class="section-title">👥 Stakeholders</div>', unsafe_allow_html=True)
            stakeholders = context.get("stakeholders", [])
            s_html = "".join([f"<div class='badge' style='background:#1a1f35; color:#a78bfa; border-color:#7c3aed44'>{s}</div>" for s in stakeholders])
            st.markdown(f"""<div class="sim-card">{s_html or '—'}</div>""", unsafe_allow_html=True)
    # TAB 2: SCENARIOS
    with tab2:
        st.markdown(f"**{len(scenarios_data)} scenarios generated** across different strategic approaches")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        for scenario in scenarios_data:
            sid = scenario["id"]
            is_best = sid == final.get("recommended_scenario_id")
            css_class = "scenario-card best" if is_best else "scenario-card"
            badge = "⭐ Recommended" if is_best else ""

            actions_html = "".join([
                f"<div style='font-size:13px; color:#94a3b8; padding:3px 0'>→ {a}</div>"
                for a in scenario.get("key_actions", [])
            ])

            approach_color = {
                "conservative": "#22c55e",
                "balanced": "#3b82f6",
                "optimistic": "#a78bfa",
                "bold": "#f97316",
                "alternative": "#38bdf8",
            }.get(scenario.get("approach", ""), "#64748b")

            st.markdown(f"""
            <div class="{css_class}">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px">
                    <span style="font-size:16px; font-weight:600; color:#e2e8f0">{scenario.get('title','')}</span>
                    <div>
                        <span style="font-size:11px; background:#0a1628; color:{approach_color}; border:1px solid {approach_color}44; padding:2px 8px; border-radius:999px; text-transform:uppercase; letter-spacing:0.05em">{scenario.get('approach','')}</span>
                        {"<span style='font-size:11px; background:#1e3a5f; color:#60a5fa; border:1px solid #2563eb44; padding:2px 8px; border-radius:999px; margin-left:6px'>" + badge + "</span>" if badge else ""}
                    </div>
                </div>
                <p style="font-size:14px; color:#94a3b8; margin-bottom:12px">{scenario.get('description','')}</p>
                <div style="display:flex; gap:24px; margin-bottom:12px; font-size:13px">
                    <span>⏱️ {scenario.get('timeframe','—')}</span>
                    <span>📊 Probability: <strong>{percentage(scenario.get('probability',0))}</strong></span>
                    <span>💪 Difficulty: <strong>{scenario.get('difficulty','—').title()}</strong></span>
                </div>
                <div style="font-size:13px; color:#64748b; margin-bottom:6px; font-weight:500">KEY ACTIONS</div>
                {actions_html}
            </div>
            """, unsafe_allow_html=True)
    # TAB 3: OUTCOMES
    with tab3:
        for scenario in scenarios_data:
            sid = scenario["id"]
            outcome = outcome_map.get(sid, {})
            if not outcome:
                continue

            col_title, col_metric = st.columns([3, 1])
            with col_title:
                st.markdown(f"**{scenario['title']}**")
                st.caption(f"Financial: {outcome.get('financial_impact','—')} | Emotional: {outcome.get('emotional_impact','—')} | Career: {outcome.get('career_impact','—')}")
            with col_metric:
                sp = outcome.get("success_probability", 0)
                st.metric("Success Probability", percentage(sp))

            col_pos, col_neg = st.columns(2)
            with col_pos:
                st.markdown("✅ **Positive Impacts**")
                for item in outcome.get("positive_impacts", []):
                    if isinstance(item, dict):
                        st.markdown(f"""<div class="impact-positive">
                            <strong>{item.get('magnitude','').title()}</strong> likelihood {item.get('likelihood','').lower()} — {item.get('impact','')}
                        </div>""", unsafe_allow_html=True)
            with col_neg:
                st.markdown("❌ **Negative Impacts**")
                for item in outcome.get("negative_impacts", []):
                    if isinstance(item, dict):
                        st.markdown(f"""<div class="impact-negative">
                            <strong>{item.get('magnitude','').title()}</strong> likelihood {item.get('likelihood','').lower()} — {item.get('impact','')}
                        </div>""", unsafe_allow_html=True)

            col3a, col3b = st.columns(2)
            with col3a:
                st.info(f"📅 **Short-term:** {outcome.get('short_term_outlook','—')}")
            with col3b:
                st.info(f"🔭 **Long-term:** {outcome.get('long_term_outlook','—')}")

            st.markdown('<div class="sim-divider"></div>', unsafe_allow_html=True)
    # TAB 4: RISK ANALYSIS
    with tab4:
        st.markdown("#### Risk Scores by Scenario")
        st.caption("Scores computed from negative impacts, reversibility, urgency, difficulty, and regret potential.")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Sorted by risk
        sorted_risks = sorted(risk_scores.items(), key=lambda x: x[1])
        scenario_title_map = {s["id"]: s["title"] for s in scenarios_data}

        for sid, score in sorted_risks:
            title = scenario_title_map.get(sid, sid)
            color = risk_color(score)
            label = risk_level_label(score)
            pct = int(score)

            st.markdown(f"""
            <div class="sim-card" style="margin-bottom:10px">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px">
                    <span style="font-size:14px; font-weight:500">{title}</span>
                    <span style="font-size:22px; font-weight:700; font-family:'JetBrains Mono',monospace; color:{color}">{score:.0f}</span>
                </div>
                <div style="color:{color}; font-size:12px; margin-bottom:8px">{label}</div>
                <div class="risk-bar-bg">
                    <div style="width:{pct}%; background:{color}; height:100%; border-radius:999px; transition:width 0.6s ease"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Ranked breakdown
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("#### Scenario Rankings")
        ranked = final.get("ranked_scenarios", [])
        cols = st.columns(len(ranked)) if ranked else []
        for i, (rank, col) in enumerate(zip(ranked, cols)):
            with col:
                is_top = i == 0
                border = "border: 2px solid #3b82f6;" if is_top else ""
                st.markdown(f"""
                <div class="sim-card" style="{border} text-align:center">
                    <div style="font-size:24px; margin-bottom:4px">{'🥇' if i==0 else '🥈' if i==1 else '🥉' if i==2 else '4️⃣'}</div>
                    <div style="font-size:13px; font-weight:600; margin-bottom:8px">{rank.get('scenario_title','')}</div>
                    <div style="font-size:28px; font-weight:700; font-family:'JetBrains Mono',monospace; color:{'#60a5fa' if is_top else '#e2e8f0'}">{rank.get('score',0):.0f}</div>
                    <div style="font-size:11px; color:#64748b; margin-top:4px">composite score</div>
                    <div style="margin-top:8px; font-size:12px; color:{risk_color(rank.get('risk_score',50))}">{rank.get('risk_label','')}</div>
                </div>
                """, unsafe_allow_html=True)

    #  TAB 5: RECOMMENDATION
    with tab5:
        rec_title = final.get("recommended_scenario_title", "—")
        confidence = final.get("confidence_score", 0)

        st.markdown(f"""
        <div class="recommendation-box">
            <div style="font-size:12px; letter-spacing:0.1em; text-transform:uppercase; color:#60a5fa; margin-bottom:8px">🏆 Recommended Decision</div>
            <div style="font-size:28px; font-weight:700; color:#e2e8f0; margin-bottom:12px">{rec_title}</div>
            <div style="font-size:14px; color:#94a3b8; line-height:1.7">{final.get('reasoning','')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_conf, col_risk_sum = st.columns(2)
        with col_conf:
            st.metric("AI Confidence Score", f"{confidence:.0f} / 100", delta=score_label(confidence))
        with col_risk_sum:
            st.caption(final.get("risk_summary", ""))

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_act, col_warn = st.columns(2)
        with col_act:
            st.markdown("#### 📋 Action Plan")
            for i, action in enumerate(final.get("action_plan", []), 1):
                st.markdown(f"""
                <div class="action-step">
                    <div class="step-num">{i}</div>
                    <div style="font-size:14px; color:#94a3b8; padding-top:2px">{action}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_warn:
            st.markdown("#### ⚠️ Warnings & Notices")
            for w in final.get("warnings", []):
                css_class = "success-pill" if "✅" in w else "warning-pill"
                st.markdown(f'<div class="{css_class}">{w}</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.markdown("---")

        # Raw JSON export
        with st.expander("📥 Export Full Analysis (JSON)"):
            st.json(result)

# FOOTER (empty state)
if not st.session_state.result and not st.session_state.error:
    st.markdown("""
    <div style="text-align:center; padding: 60px 0; color:#1e293b">
        <div style="font-size:64px; margin-bottom:16px">🧠</div>
        <div style="font-size:18px; color:#334155; font-weight:500">Enter a decision problem above to begin</div>
        <div style="font-size:14px; color:#1e293b; margin-top:8px">Try the example problems in the sidebar →</div>
    </div>
    """, unsafe_allow_html=True)