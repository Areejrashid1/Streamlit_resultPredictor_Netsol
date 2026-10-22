import random

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"  # our FastAPI server

st.set_page_config(
    page_title="Mom's Verdict",
    page_icon="👩🏻‍🦳",
    layout="centered",
)

# ─────────────────────────────────────────────────────────────
# Themes: each result gets its own background + mood
# ─────────────────────────────────────────────────────────────
THEMES = {
    "idle": {
        "bg": "linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe)",
        "speed": "18s",
    },
    "pass": {
        "bg": "linear-gradient(-45deg, #11998e, #38ef7d, #f9d423, #ff9a9e)",
        "speed": "8s",
    },
    "fail": {
        "bg": "linear-gradient(-45deg, #141e30, #8e0e00, #2c1a1a, #cb2d3e)",
        "speed": "5s",
    },
}

PASS_LINES = [
    "I'm SO proud of you, my champion! Close your eyes... surprise!",
    "All that studying paid off! You've earned this, sweetheart!",
    "That's my clever boy! Come here, I got you something special!",
    "Top marks! Dinner is whatever you want tonight. Plus this gift!",
]
FAIL_LINES = [
    "Young man! Put that phone down and open your books RIGHT NOW!",
    "I didn't raise you to waste time! No gift, no games, only study!",
    "Fail?! Do you know how hard we work for your education?!",
    "We need to talk, mister. Extra study hours starting tonight!",
]
GIFTS = {
    "big": ["🎮 Gaming Console", "🚲 Brand New Bicycle", "📱 New Smartphone"],
    "small": ["🍫 Chocolate Box", "🧸 Teddy Bear", "🎂 Favourite Cake", "🍦 Ice Cream Party"],
}

# ─────────────────────────────────────────────────────────────
# Session state (so the mood survives Streamlit reruns)
# ─────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "inputs" not in st.session_state:
    st.session_state.inputs = None

# ─────────────────────────────────────────────────────────────
# Inputs
# ─────────────────────────────────────────────────────────────
# We need slider values to know if the stored result is still valid,
# but the CSS must be injected first. So we read widget state early.
study_hours = st.session_state.get("study_hours", 4.0)
prev_score = st.session_state.get("prev_score", 60.0)

result = st.session_state.result
# If the user moves a slider after predicting, return to the calm "idle" mood
if result and st.session_state.inputs != (study_hours, prev_score):
    result = None
    st.session_state.result = None

mood = "idle" if result is None else ("pass" if result["prediction"] == 1 else "fail")
theme = THEMES[mood]

# ─────────────────────────────────────────────────────────────
# Falling particles: confetti (pass) / rain (fail)
# ─────────────────────────────────────────────────────────────
particles_html = ""
if mood == "pass":
    symbols = ["🎉", "🎊", "⭐", "🎈", "✨", "🍬", "🎁"]
    for _ in range(26):
        particles_html += (
            f'<span class="particle fall" style="left:{random.randint(0, 98)}%;'
            f"animation-duration:{random.uniform(4, 9):.1f}s;"
            f"animation-delay:{random.uniform(0, 5):.1f}s;"
            f'font-size:{random.randint(18, 34)}px">{random.choice(symbols)}</span>'
        )
elif mood == "fail":
    symbols = ["💧", "⚡", "☁️", "📚", "💢"]
    for _ in range(30):
        particles_html += (
            f'<span class="particle fall" style="left:{random.randint(0, 98)}%;'
            f"animation-duration:{random.uniform(1.5, 4):.1f}s;"
            f"animation-delay:{random.uniform(0, 3):.1f}s;"
            f'font-size:{random.randint(14, 28)}px">{random.choice(symbols)}</span>'
        )

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
CSS = """
<style>
.stApp {
    background: %%BG%%;
    background-size: 400% 400%;
    animation: bgmove %%SPEED%% ease infinite;
    transition: background 1s;
}
@keyframes bgmove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
header[data-testid="stHeader"] {background: transparent;}
#MainMenu, footer {visibility: hidden;}

.stApp, .stApp p, .stApp label, .stApp span, .stApp h1, .stApp h2, .stApp h3 {
    color: #ffffff !important;
}
.block-container {padding-top: 2rem; max-width: 760px;}

.hero {text-align:center; margin-bottom: 0.5rem;}
.hero h1 {font-size: 2.6rem; margin-bottom: 0; text-shadow: 0 3px 12px rgba(0,0,0,.35);}
.hero p {opacity: .9; font-size: 1.05rem;}

.glass {
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.3);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 22px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 10px 35px rgba(0,0,0,.25);
    margin: 0.8rem 0;
}

div.stButton > button {
    background: linear-gradient(135deg, #ff9a9e, #fad0c4);
    color: #5a1a2a !important;
    font-weight: 800;
    font-size: 1.15rem;
    border: none;
    border-radius: 50px;
    padding: 0.75rem 1rem;
    box-shadow: 0 8px 22px rgba(0,0,0,.3);
    transition: transform .15s ease, box-shadow .15s ease;
}
div.stButton > button p {color: #5a1a2a !important; font-weight: 800;}
div.stButton > button:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 12px 28px rgba(0,0,0,.4);
}

[data-testid="stMetricValue"], [data-testid="stMetricLabel"] p {color: #fff !important;}
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.16);
    border-radius: 18px;
    padding: 0.8rem 1rem;
    text-align: center;
}

/* ── Scene ── */
.scene {
    display:flex; justify-content:space-around; align-items:flex-end;
    font-size: 5.5rem; padding: 1rem 0 0.2rem 0; position: relative;
}
.char {position: relative; display:inline-block;}
.mood {
    position:absolute; top:-1.2rem; right:-0.6rem; font-size:2.2rem;
}
.bubble {
    position: relative;
    background: #ffffff;
    border-radius: 20px;
    padding: 1rem 1.3rem;
    font-size: 1.15rem;
    font-weight: 700;
    text-align:center;
    box-shadow: 0 8px 25px rgba(0,0,0,.3);
    margin: 0.6rem 0 0.8rem 0;
}
.bubble, .bubble * {color: #2b2b2b !important;}
.bubble:before {
    content:""; position:absolute; top:-14px; left:22%;
    border-left:14px solid transparent; border-right:14px solid transparent;
    border-bottom:16px solid #ffffff;
}
.verdict {
    text-align:center; font-size: 2rem; font-weight: 900;
    letter-spacing: 1px; text-shadow: 0 3px 12px rgba(0,0,0,.4);
}

/* Pass animations */
.pass-mom {animation: bounce 0.9s ease-in-out infinite;}
.pass-kid {animation: jump 0.7s ease-in-out infinite;}
.gift-fly {
    position:absolute; font-size: 3.4rem; left: 28%; bottom: 1rem;
    animation: gift 2.4s ease-in-out infinite;
}
@keyframes bounce {0%,100%{transform:translateY(0)} 50%{transform:translateY(-14px)}}
@keyframes jump {0%,100%{transform:translateY(0) rotate(-6deg)} 50%{transform:translateY(-24px) rotate(6deg)}}
@keyframes gift {
    0% {transform: translateX(0) scale(1); opacity: 1;}
    70% {transform: translateX(200px) scale(1.3) rotate(15deg); opacity: 1;}
    100% {transform: translateX(215px) scale(1.4) rotate(-10deg); opacity: .0;}
}

/* Fail animations */
.fail-mom {animation: shake 0.45s linear infinite;}
.fail-kid {animation: sulk 2s ease-in-out infinite;}
.finger {
    position:absolute; font-size:3rem; left: 30%; bottom: 1.2rem;
    animation: wag 0.5s ease-in-out infinite;
}
@keyframes shake {
    0%,100%{transform:translateX(0) rotate(0)}
    25%{transform:translateX(-6px) rotate(-3deg)}
    75%{transform:translateX(6px) rotate(3deg)}
}
@keyframes sulk {0%,100%{transform:translateY(0) scale(1)} 50%{transform:translateY(6px) scale(.94)}}
@keyframes wag {
    0%,100%{transform: translateX(0) rotate(-20deg)}
    50%{transform: translateX(40px) rotate(20deg)}
}

/* Idle */
.idle-mom {animation: bounce 2.5s ease-in-out infinite;}

/* Particles */
.particle {position: fixed; top:-60px; z-index: 0; pointer-events:none;}
.fall {animation-name: drop; animation-iteration-count: infinite; animation-timing-function: linear;}
@keyframes drop {
    0% {transform: translateY(-60px) rotate(0deg); opacity: 1;}
    100% {transform: translateY(110vh) rotate(360deg); opacity: .8;}
}
</style>
"""
st.markdown(
    CSS.replace("%%BG%%", theme["bg"]).replace("%%SPEED%%", theme["speed"]),
    unsafe_allow_html=True,
)
if particles_html:
    st.markdown(particles_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>👩‍👦 Mom's Verdict</h1>
        <p>Set the student's study habits and see how Mom reacts!</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# Sliders
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="glass">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    study_hours = st.slider(
        "📖 Study Hours Per Day",
        min_value=0.0,
        max_value=10.0,
        value=4.0,
        step=0.5,
        key="study_hours",
        help="How many hours the student studies each day",
    )
with col2:
    prev_score = st.slider(
        "📝 Previous Exam Score",
        min_value=0.0,
        max_value=100.0,
        value=60.0,
        step=1.0,
        key="prev_score",
        help="Score from the most recent exam (out of 100)",
    )
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Predict
# ─────────────────────────────────────────────────────────────
if st.button("🔮 Show Mom the Result", use_container_width=True):
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json={"study_hours": study_hours, "prev_score": prev_score},
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            # Pick Mom's reaction ONCE so it doesn't change on reruns
            if data["prediction"] == 1:
                pool = GIFTS["big"] if data["confidence"] >= 0.8 else GIFTS["small"]
                data["gift"] = random.choice(pool)
                data["line"] = random.choice(PASS_LINES)
            else:
                data["line"] = random.choice(FAIL_LINES)
            st.session_state.result = data
            st.session_state.inputs = (study_hours, prev_score)
            st.session_state.celebrate = True
            st.rerun()  # rerun so the new background applies immediately
        else:
            st.error(f"API returned an error ({response.status_code}). Check the FastAPI logs.")
    except requests.exceptions.RequestException:
        st.error("😟 Could not reach the prediction API. Is FastAPI running on port 8000?")

# ─────────────────────────────────────────────────────────────
# Mom's reaction
# ─────────────────────────────────────────────────────────────
if result:
    conf = result["confidence"] * 100

    if result["prediction"] == 1:
        st.markdown(
            f"""
            <div class="verdict">🎉 PASSED! 🎉</div>
            <div class="glass">
                <div class="scene">
                    <div class="char pass-mom">👩🏻‍🦳<span class="mood">💖</span></div>
                    <div class="gift-fly">🎁</div>
                    <div class="char pass-kid">👦🏻<span class="mood">🥳</span></div>
                </div>
                <div class="bubble">💬 {result['line']}</div>
                <div class="verdict" style="font-size:1.4rem">
                    Gift unlocked: {result['gift']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.pop("celebrate", False):
            st.balloons()
    else:
        st.markdown(
            f"""
            <div class="verdict">😤 FAILED! 😤</div>
            <div class="glass">
                <div class="scene">
                    <div class="char fail-mom">👩🏻‍🦳<span class="mood">💢</span></div>
                    <div class="finger">👆</div>
                    <div class="char fail-kid">👦🏻<span class="mood">😭</span></div>
                </div>
                <div class="bubble">💬 {result['line']}</div>
                <div class="verdict" style="font-size:1.3rem">
                    Punishment: 📵 No phone &nbsp;•&nbsp; 📚 Extra study
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.session_state.pop("celebrate", None)

    c1, c2 = st.columns(2)
    c1.metric("Model Confidence", f"{conf:.1f}%")
    c2.metric("Result", result["result_label"])
    st.progress(min(max(result["confidence"], 0.0), 1.0))

    with st.expander("🔍 See what was sent to the API"):
        st.json({"study_hours": study_hours, "prev_score": prev_score})
        st.json({k: v for k, v in result.items() if k not in ("line", "gift")})
else:
    st.markdown(
        """
        <div class="glass">
            <div class="scene">
                <div class="char idle-mom">👩<span class="mood">🤔</span></div>
                <div class="char idle-mom">🧒<span class="mood">😬</span></div>
            </div>
            <div class="bubble">💬 Well? Let's see how you did, dear...</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# Live input summary (updates as sliders move)
# ─────────────────────────────────────────────────────────────
m1, m2 = st.columns(2)
m1.metric("Study Hours", f"{study_hours} hrs/day")
m2.metric("Previous Score", f"{prev_score:.0f}/100")