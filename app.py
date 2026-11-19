
import pandas as pd
import plotly.express as px
import pycountry
import requests
import streamlit as st

# reminder to use python -m streamlit run c:/Users/alexf/Downloads/app.py 

URLS = [
    "https://api.ransomware.live/v2/recentvictims",
    "https://api.ransomware.live/v2/recentcyberattacks",
    
]

COL = {
    "Group": ["group", "group_name", "gang", "actor", "attacker"],
    "Country": ["country", "location"],
    "Date": ["attackdate", "date", "discovered", "published", "published_date"],
    "Sector": ["activity", "sector", "industry"],
    "Victim": ["victim", "title", "name"],
    "Url": ["url", "link", "source_url", "article_url", "sources"],
    "Description": ["description", "summary", "details", "notes"],
}
st.set_page_config(page_title="Global Ransomware Landscape Explorer", layout="wide")

@st.cache_data(ttl=3600, show_spinner="Loading attack data...") # I learned this helps to use the previous data instead of making a new request a change happens. 

def load_data():
    last_error = None
    for url in URLS:
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            df = pd.DataFrame(r.json())
            if not df.empty:
                return df, url
        except Exception as e: 
            last_error = e
    raise RuntimeError("Could not load data: " + str(last_error))


def pick(df, key):
    for col in COL[key]:
        if col in df.columns:
            return col
    return None

df_raw, source_url = load_data()

cols = {}

for k in COL:
    cols[k] = pick(df_raw, k)

df = df_raw.copy()


#st.title("Global Ransomware Landscape Explorer")
st.markdown("# Global Ransomware Landscape Explorer  \n  ##### (**Explorador del Panorama Global del Ransomware**)")
st.sidebar.header("Filters")
filtered = df



#print("Available columns:", df_raw.columns.tolist())

#print("\nIdentified columns:", cols)

country = cols.get("Country")
sector = cols.get("Sector")
victim = cols.get("Victim")
description = cols.get("Description")
table = []


if victim:
    table.append(victim)
if country:
    table.append(country)
if sector:
    table.append(sector)
if description:
    table.append(description)

    
bar_graph = (country is not None) and (victim is not None)
vict_table = bar_graph and (sector is not None)

if country:
    countries = sorted(filtered[country].dropna().unique())
    sel = st.sidebar.multiselect("Location by Country (Locacion por Pais)", countries)
    if sel:
        filtered = filtered[filtered[country].isin(sel)]


if sector:
    sectors = sorted(filtered[sector].dropna().unique())
    sel = st.sidebar.multiselect("Sector (Sector)", sectors)
    if sel:
        filtered = filtered[filtered[sector].isin(sel)]

if country:
    country_counts = filtered[country].value_counts().reset_index()
    country_counts.columns = ["Country(Pais)", "Attacks(Ataques)"]

if victim:
    rename_columns = {
    victim: "Victim",
    country: "Country",
    sector: "Sector",
    description: "Description"}
    victim_table = filtered[table].copy()
    victim_table = victim_table.rename(columns=rename_columns)
    victim_counts = filtered[victim].value_counts().reset_index()
    victim_counts.columns = ["Victim", "Times Attacked"]
    victim_counts = victim_counts.merge(victim_table, on ="Victim")



if bar_graph:
    fig = px.bar(
        country_counts,
        x="Country(Pais)",
        y="Attacks(Ataques)",
        title="Ransomware Attacks by Country",
        text="Attacks(Ataques)"
        
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, width='stretch')

if victim:
    st.subheader("Ransomware Attacks Table (Tabla de Ataques de Ransomware)")
    st.dataframe(victim_counts, width='stretch')





