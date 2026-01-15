import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🏇 Australian Horse Racing Ratings Platform")

# Load data
runs = pd.read_csv("data/raw/runs.csv")
benchmarks = pd.read_csv("data/benchmarks/track_benchmarks.csv")
sectionals = pd.read_csv("data/raw/sectionals.csv")
market = pd.read_csv("data/raw/market_odds.csv")

race_id = st.selectbox("Select Race", runs["race_id"].unique())
race = runs[runs["race_id"] == race_id]

race = race.merge(benchmarks, on=["track", "distance"], how="left")
race = race.merge(sectionals, on="horse", how="left")
race = race.merge(market, on="horse", how="left")

ratings = []
pace_scores = []

for _, r in race.iterrows():
    adjusted_time = r["time_seconds"] - r["variant"]

    bpr = 100 - (adjusted_time - r["benchmark_time"]) * 10
    bpr -= (r["weight"] - 58) * 0.85
    bpr -= r["margin"] * 0.85

    if r["last_400"] < 23:
        bpr += 1.5
    elif r["last_400"] < 23.5:
        bpr += 0.75

    ratings.append(round(bpr, 2))
    pace_scores.append(5 - r["barrier"] * 0.05)

race["rating"] = ratings
race["pace"] = pace_scores

race["probability"] = race["rating"] / race["rating"].sum()
race["fair_odds"] = (1 / race["probability"]).round(2)
race["value"] = (race["market_odds"] / race["fair_odds"]).round(2)
race = race.sort_values("rating", ascending=False)
race["rank"] = range(1, len(race) + 1)

st.subheader("📊 Ratings & Fair Odds")
st.dataframe(race[["horse", "rating", "fair_odds", "market_odds", "value", "rank"]])

st.subheader("⚡ Speed Map")
fig, ax = plt.subplots()
ax.scatter(race["barrier"], race["pace"])
for _, r in race.iterrows():
    ax.text(r["barrier"], r["pace"], r["horse"])
ax.set_xlabel("Barrier")
ax.set_ylabel("Early Speed")
st.pyplot(fig)

st.subheader("⏱️ Sectionals")
st.dataframe(race[["horse", "early_400", "mid_400", "last_400"]])
