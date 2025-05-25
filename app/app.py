import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --- Data loading and preprocessing ---
@st.cache_data
def load_and_preprocess_data():
    # Load CSVs
    pop = pd.read_csv("data/population.csv")
    life = pd.read_csv("data/life_expectancy.csv")
    gni = pd.read_csv("data/gni_per_capita.csv")

    def tidy_and_fill(df, value_name):
        # Drop extra columns if exist
        df = df.drop(columns=["Indicator Name", "Indicator Code"], errors="ignore")

        # Melt wide to long format
        df = df.melt(id_vars=["country"], var_name="year", value_name=value_name)
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df[value_name] = pd.to_numeric(df[value_name], errors="coerce")

        # Sort by country and year for forward fill
        df = df.sort_values(["country", "year"])

        # Forward fill missing values by country
        df[value_name] = df.groupby("country")[value_name].ffill()

        return df

    df_pop = tidy_and_fill(pop, "population")
    df_life = tidy_and_fill(life, "life_expectancy")
    df_gni = tidy_and_fill(gni, "gni_per_capita")

    # Merge dataframes on country and year
    df = df_pop.merge(df_life, on=["country", "year"], how="inner")
    df = df.merge(df_gni, on=["country", "year"], how="inner")

    # Drop rows with missing values after ffill (optional)
    df = df.dropna(subset=["population", "life_expectancy", "gni_per_capita"])

    return df

# Load data
df = load_and_preprocess_data()

# Sort years and countries
years = sorted(df["year"].unique())
countries_all = sorted(df["country"].unique())

# --- Streamlit UI ---
st.sidebar.title("Gapminder Dashboard Filters")

# Year slider with play button
selected_year = st.sidebar.slider(
    "Select Year",
    min_value=years[0],
    max_value=years[-1],
    value=years[0],
    step=1,
    key="year_slider"
)

# Countries available for selected year
countries_for_year = sorted(df[df["year"] == selected_year]["country"].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=countries_for_year,
    default=countries_for_year,
    key="country_selector"
)

# Play button to animate years
if st.sidebar.button("▶ Play Animation"):
    for year in years:
        st.session_state["year_slider"] = year
        time.sleep(0.2)
        st.experimental_rerun()

# Filter dataframe by year and countries
filtered_df = df[(df["year"] == selected_year) & (df["country"].isin(selected_countries))]

# --- Plot ---
st.title("🌍 Gapminder Bubble Chart")
st.markdown(f"### Year: {selected_year}")

max_gni = df["gni_per_capita"].max()

fig = px.scatter(
    filtered_df,
    x="gni_per_capita",
    y="life_expectancy",
    size="population",
    color="country",
    hover_name="country",
    log_x=True,
    size_max=60,
    range_x=[100, max_gni * 1.1],
    labels={
        "gni_per_capita": "GNI per Capita (log scale)",
        "life_expectancy": "Life Expectancy",
        "population": "Population"
    },
    title="Life Expectancy vs GNI per Capita (PPP, log scale)"
)

st.plotly_chart(fig, use_container_width=True)
