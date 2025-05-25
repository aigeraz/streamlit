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
        country_col = "country"
        df = df.drop(columns=["Indicator Name", "Indicator Code"], errors="ignore")
        df = df.melt(id_vars=[country_col], var_name="year", value_name=value_name)
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df[value_name] = pd.to_numeric(df[value_name], errors="coerce")
        df.sort_values([country_col, "year"], inplace=True)
        df[value_name] = df.groupby(country_col)[value_name].ffill()
        return df

    df_pop = tidy(pop, "population")
    df_life = tidy(life, "life_expectancy")
    df_gni = tidy(gni, "gni_per_capita")

    df = df_pop.merge(df_life, on=["country", "year"])
    df = df.merge(df_gni, on=["country", "year"])

    # <-- dropna removed, keep all rows even if some data missing
    # df.dropna(subset=["population", "life_expectancy", "gni_per_capita"], inplace=True)

    return df
