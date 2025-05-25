import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Cached Data Loading & Preprocessing
# -------------------------------
@st.cache_data
def load_and_preprocess_data():
    # Load CSVs
    pop = pd.read_csv("data/population.csv")
    life = pd.read_csv("data/life_expectancy.csv")
    gni = pd.read_csv("data/gni_per_capita.csv")

    # Convert to tidy format
    def tidy(df, value_name):
        # Detect country column
        if "Country Name" in df.columns:
            country_col = "Country Name"
        elif "country" in df.columns:
            country_col = "country"
        else:
            raise ValueError("Country column not found")

        # Drop extra columns if they exist
        df = df.drop(columns=["Indicator Name", "Indicator Code"], errors="ignore")

        # Melt wide to long format
        df = df.melt(id_vars=[country_col], var_name="year", value_name=value_name)
        df.rename(columns={country_col: "country"}, inplace=True)

        # Convert types
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df[value_name] = pd.to_numeric(df[value_name], errors="coerce")

        # Sort and forward fill
        df.sort_values(["country", "year"], inplace=True)
        df[value_name] = df.groupby("country")[value_name].ffill()

        return df

    # Clean each CSV
    df_pop = tidy(pop, "population")
    df_life = tidy(life, "life_expectancy")
    df_gni = tidy(gni, "gni_per_capita")

    # Merge all into one tidy DataFrame
    df = df_pop.merge(df_life, on=["country", "year"])
    df = df.merge(df_gni, on=["country", "year"])

    # Drop any rows with missing final values
    df.dropna(subset=["population", "life_expectancy", "gni_per_capita"], inplace=True)

    return df

# -------------------------------
# Load Data
# -------------------------------
df = load_and_preprocess_data()
years = sorted(df["year"].unique())
countries = sorted(df["country"].unique())

# -------------------------------
# Sidebar UI
# -------------------------------
st.sidebar.title("Gapminder Dashboard Filters")

selected_year = st.sidebar.slider("Select Year", min_value=years[0], max_value=years[-1], value=years[0], step=1)
selected_countries = st.sidebar.multiselect("Select Countries", options=countries, default=countries)

# -------------------------------
# Filtered Data
# -------------------------------
filtered_df = df[df["year"] == selected_year]

if selected_countries:
    filtered_df = filtered_df[filtered_df["country"].isin(selected_countries)]

# -------------------------------
# Main Title
# -------------------------------
st.title("🌍 Gapminder Bubble Chart")
st.markdown(f"### Year: {selected_year}")

# -------------------------------
# Plot
# -------------------------------
fig = px.scatter(
    filtered_df,
    x="gni_per_capita",
    y="life_expectancy",
    size="population",
    color="country",
    hover_name="country",
    log_x=True,
    size_max=60,
    range_x=[100, df["gni_per_capita"].max() * 1.1],
    labels={
        "gni_per_capita": "GNI per Capita (log)",
        "life_expectancy": "Life Expectancy",
        "population": "Population"
    },
    title="Life Expectancy vs GNI per Capita (Log Scale)"
)

st.plotly_chart(fig, use_container_width=True)

# Optional autoplay for future enhancement
# if st.sidebar.button("Play Animation"):
#     for year in years:
#         st.session_state["year"] = year
#         st.experimental_rerun()
