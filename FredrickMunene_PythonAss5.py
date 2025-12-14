# app.py — BUIS 305 / INSS 405 Assignment 6
# Streamlit dashboard: Poverty & Millionaire Analytics

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px

# Page config
st.set_page_config(page_title="Poverty & Millionaire Analytics", layout="wide")
st.title("Poverty & Millionaire Analytics Dashboard")
st.caption("Bowie State University – Assignment 6 (Streamlit + Pandas + Matplotlib + Plotly)")

# ------------------------------
# 1. File Upload Section
# ------------------------------
st.sidebar.header("1) Upload Dataset")

uploaded = st.sidebar.file_uploader(
    "Upload the Excel file (povertymillionaires.xlsx)",
    type=["xlsx", "xls"],
    help="File must include: State, Number in Poverty, Number of Millionaires, State Population"
)

@st.cache_data
def load_df(file) -> pd.DataFrame:
    df = pd.read_excel(file)

    df.columns = [c.strip() for c in df.columns]

    required = ["State", "Number in Poverty", "Number of Millionaires", "State Population"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    for col in ["Number in Poverty", "Number of Millionaires", "State Population"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna()

    # derived metrics
    df["Millionaire Density"] = df["Number of Millionaires"] / df["State Population"]
    df["Poverty Rate"] = df["Number in Poverty"] / df["State Population"]

    return df

if uploaded is None:
    st.info("⬅️ Upload **povertymillionaires.xlsx** in the sidebar to begin.")
    st.stop()

try:
    df = load_df(uploaded)
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

# ------------------------------
# 2. State Selection
# ------------------------------
st.sidebar.header("2) State Selection")
all_states = df["State"].tolist()
default_states = all_states[:5]

picked_states = st.sidebar.multiselect(
    "Choose at least 5 states",
    all_states,
    default=default_states
)

if len(picked_states) < 5:
    st.warning("Select **at least 5 states** to continue.")
    st.stop()

df_sel = df[df["State"].isin(picked_states)]

# ------------------------------
# 3. Tabs (Q1–Q3)
# ------------------------------
tab1, tab2, tab3 = st.tabs([
    "Poverty vs Millionaires",
    "Millionaire Density Map",
    "Poverty Rate"
])

# --------------------------------
# Q1: Side-by-side bar chart
# --------------------------------
with tab1:
    st.subheader("Q1: Compare Poverty vs Millionaires by State")

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(df_sel))
    width = 0.35

    ax.bar(x - width/2, df_sel["Number in Poverty"], width,
           label="Number in Poverty", color="#ff9999")
    ax.bar(x + width/2, df_sel["Number of Millionaires"], width,
           label="Number of Millionaires", color="#66b3ff")

    ax.set_xticks(x)
    ax.set_xticklabels(df_sel["State"])
    ax.set_ylabel("Population Count")
    ax.set_title("Poverty vs Millionaire Population by State")
    ax.legend()

    st.pyplot(fig)

# --------------------------------
# Q2: Choropleth Map
# --------------------------------
with tab2:
    st.subheader("Q2: Millionaire Density Across U.S. States")

    fig_map = px.choropleth(
        df,
        locations="State",
        locationmode="USA-states",
        color="Millionaire Density",
        hover_name="State",
        hover_data={
            "Number of Millionaires": True,
            "State Population": True,
            "Millionaire Density": True
        },
        scope="usa",
        color_continuous_scale="Viridis",
        title="Millionaire Density (Millionaires / State Population)"
    )

    st.plotly_chart(fig_map, use_container_width=True)

# --------------------------------
# Q3: Poverty Rate (horizontal)
# --------------------------------
with tab3:
    st.subheader("Q3: Poverty Rate Across Selected States")

    df_sorted = df_sel.sort_values("Poverty Rate", ascending=True)

    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.barh(df_sorted["State"], df_sorted["Poverty Rate"], color="skyblue")
    ax3.set_xlabel("Poverty Rate")
    ax3.set_ylabel("State")
    ax3.set_title("Poverty Rate Across Selected States")

    st.pyplot(fig3)
