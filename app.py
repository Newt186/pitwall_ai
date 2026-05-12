import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
sys.path.append('.')
from copilot.rag import ask_copilot
from racebrain.predict import predict_pit, predict_position

st.set_page_config(page_title="PitWall AI", page_icon="F1", layout="wide")

page = st.sidebar.radio("Navigate", ["Fan Copilot", "Race Brain", "Live Pulse"])

if page == "Fan Copilot":
    st.title("Fan Copilot")
    st.caption("Ask anything about F1 - rules, drivers, strategy, history.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "history" not in st.session_state:
        st.session_state.history = []

    suggested = [
        "What is an undercut?",
        "How does DRS work?",
        "Explain tyre degradation",
        "Who has the most poles in 2024?"
    ]

    cols = st.columns(4)
    for i, q in enumerate(suggested):
        if cols[i].button(q):
            st.session_state.pending = q

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Ask anything about F1...")

    if "pending" in st.session_state:
        prompt = st.session_state.pending
        del st.session_state.pending

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.spinner("Thinking..."):
            response = ask_copilot(prompt, st.session_state.history)
        st.session_state.history.append({"role": "user", "content": prompt})
        st.session_state.history.append({"role": "assistant", "content": response})
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

elif page == "Race Brain":
    st.title("Race Brain")
    st.caption("Pit stop predictions and strategy insights.")

    drivers = ["VER", "PER", "HAM", "RUS", "LEC", "SAI", "NOR", "PIA", "ALO", "STR",
            "OCO", "GAS", "BOT", "ZHO", "MAG", "HUL", "ALB", "SAR", "TSU", "RIC"]

    col1, col2 = st.columns(2)
    with col1:
        lap = st.slider("Lap Number", 1, 57, 25)
        driver = st.selectbox("Driver", drivers)
        compound_name = st.selectbox("Tyre Compound", ["SOFT", "MEDIUM", "HARD"])
    with col2:
        tyre_life = st.number_input("Tyre Age (laps)", 1, 50, 15)
        gap_ahead = st.number_input("Gap to Car Ahead (seconds)", 0.0, 60.0, 8.0)
        position = st.number_input("Current Position", 1, 20, 5)

    compound_map = {"SOFT": 0, "MEDIUM": 1, "HARD": 2}
    compound = compound_map[compound_name]
    deg_rate = tyre_life * 0.08
    undercut_risk = 1 if gap_ahead < 22 and tyre_life > 12 else 0

    if st.button("Get Prediction"):
        with st.spinner("Analysing..."):
            pit = predict_pit(lap, tyre_life, compound, deg_rate, gap_ahead, undercut_risk, position)
            pos = predict_position(lap, tyre_life, compound, deg_rate, gap_ahead, undercut_risk, position)

        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Pit Probability", f"{pit['probability']*100:.0f}%")
        m2.metric("Predicted Finish", f"P{pos}")
        m3.metric("Undercut Risk", "HIGH" if undercut_risk == 1 else "LOW")

        if pit["recommended"]:
            st.error("Pit window is open - recommend pitting this lap")
        else:
            st.success("Stay out - no pit stop needed yet")

        if undercut_risk == 1:
            st.warning("Undercut risk detected - car ahead is vulnerable")

    st.divider()
    st.subheader("2022 Bahrain GP - Lap by Lap Predictions")
    try:
        demo_df = pd.read_csv("data/processed/bahrain_2024_demo.csv")
        st.dataframe(demo_df, use_container_width=True)
    except:
        st.info("Demo data not found. Run racebrain/predict.py to generate it.")

elif page == "Live Pulse":
    st.title("Live Pulse")
    st.caption("Telemetry visualisations powered by FastF1 data.")

    try:
        df = pd.read_csv("data/processed/features.csv")

        race_options = df["EventName"].unique().tolist()
        selected_race = st.selectbox("Select Race", race_options)
        race_df = df[df["EventName"] == selected_race]

        st.divider()
        st.subheader("Gap to Car Ahead")
        fig1 = go.Figure()
        for driver in race_df["Driver"].unique():
            d = race_df[race_df["Driver"] == driver]
            fig1.add_trace(go.Scatter(x=d["LapNumber"], y=d["gap_ahead"],
                                    mode="lines", name=driver))
        fig1.update_layout(xaxis_title="Lap", yaxis_title="Gap (seconds)")
        st.plotly_chart(fig1, use_container_width=True)

        st.divider()
        st.subheader("Tyre Degradation Trends")
        fig2 = go.Figure()
        for driver in race_df["Driver"].unique():
            d = race_df[race_df["Driver"] == driver]
            fig2.add_trace(go.Scatter(x=d["LapNumber"], y=d["deg_rate"],
                                    mode="lines", name=driver))
        fig2.update_layout(xaxis_title="Lap", yaxis_title="Degradation Rate")
        st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        st.subheader("Tyre Stints")
        compound_colors = {0: "red", 1: "yellow", 2: "grey"}
        fig3 = go.Figure()
        for driver in race_df["Driver"].unique():
            d = race_df[race_df["Driver"] == driver]
            fig3.add_trace(go.Bar(
                x=d["TyreLife"],
                y=[driver] * len(d),
                orientation="h",
                marker_color=[compound_colors.get(c, "blue") for c in d["Compound"]],
                name=driver
            ))
        fig3.update_layout(xaxis_title="Tyre Age (laps)", yaxis_title="Driver")
        st.plotly_chart(fig3, use_container_width=True)

        st.divider()
        auto_refresh = st.checkbox("Enable auto refresh (every 10 seconds)")
        if auto_refresh:
            import time
            time.sleep(10)
            st.rerun()

    except Exception as e:
        st.error(f"Could not load race data: {e}")
        st.info("Run racebrain/data_pull.py first to generate the data.")
