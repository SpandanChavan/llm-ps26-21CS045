import streamlit as st

from solver import MODEL, solve

st.set_page_config(page_title="Math Word Problem Solver", page_icon="🧮", layout="centered")

SAMPLES = [
    "A train travels 360 km in 4 hours. How long will it take to travel 540 km at the same speed?",
    "Riya has 3 times as many marbles as Aman. Together they have 64 marbles. How many marbles does Riya have?",
    "A shopkeeper buys a shirt for Rs 800 and sells it at a 25% profit. What is the selling price?",
    "The length of a rectangle is 5 cm more than its width. Its perimeter is 50 cm. Find its area.",
    "Rs 10000 is invested at 8% compound interest per year. What is the amount after 2 years?",
    "A tank is filled by pipe A in 6 hours and by pipe B in 3 hours. How long do both pipes together take?",
]

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Groq API key (optional if set in .env)", type="password")
    st.caption(f"Model: `{MODEL}`")
    st.markdown("Free key: https://console.groq.com/keys")

st.title("🧮 Math Word Problem Solver")
st.write("Type a word problem. The LLM solves it step by step, and SymPy re-checks the arithmetic.")

choice = st.selectbox("Try a sample problem", ["(write my own)"] + SAMPLES)
problem = st.text_area("Word problem", value="" if choice == "(write my own)" else choice, height=120)

if st.button("Solve", type="primary", disabled=not problem.strip()):
    with st.spinner("Thinking step by step..."):
        try:
            result = solve(problem, api_key or None)
        except Exception as e:  # noqa: BLE001
            st.error(str(e))
            st.stop()

    st.subheader("Step-by-step solution")
    st.markdown(result["steps"])

    st.subheader("Final answer")
    st.success(result["final_text"] or "Not found")

    v = result["verification"]
    st.subheader("Verification")
    if v["status"] == "pass":
        st.info(f"✅ {v['message']}  Expression `{result['expression']}` = {v['computed']:g}")
    elif v["status"] == "fail":
        st.warning(f"⚠️ {v['message']}  `{result['expression']}` = {v['computed']:g}, but answer says {v['stated']:g}")
    else:
        st.caption(f"ℹ️ {v['message']}")

    with st.expander("Raw LLM output"):
        st.code(result["raw"])
