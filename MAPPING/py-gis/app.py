import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
import json
import numpy as np
from scipy import stats
from datetime import datetime
import base64
from io import BytesIO

# ────────────────────────────────────────────────
# PAGE CONFIG
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Delhi Crime Analytics",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────
SHAPE_PATH = "shp/delhi_1997-2012_district/Districts.shp"
CSV_FOLDER = "data/"
SHAPE_DISTRICT_COL = "DISTRICT"
OLLAMA_API = "http://localhost:11434/api/generate"

# ────────────────────────────────────────────────
# HELPER: Ollama LLM Call
# ────────────────────────────────────────────────
def ask_llm(prompt, model="llama3.2"):
    """Call local Ollama API for LLM insights"""
    try:
        response = requests.post(
            OLLAMA_API,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("response", "No response received")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Could not connect to Ollama: {str(e)}"

# ────────────────────────────────────────────────
# HELPER: Calculate Hotspot Zones
# ────────────────────────────────────────────────
def classify_hotspots(gdf, crime_var):
    """Classify districts into High/Medium/Low risk zones using quantiles"""
    values = gdf[crime_var].dropna()
    
    # Use quantiles to classify
    q33 = values.quantile(0.33)
    q67 = values.quantile(0.67)
    
    def categorize(val):
        if pd.isna(val):
            return "No Data"
        elif val >= q67:
            return "High Risk"
        elif val >= q33:
            return "Medium Risk"
        else:
            return "Low Risk"
    
    gdf['Hotspot_Category'] = gdf[crime_var].apply(categorize)
    return gdf

# ────────────────────────────────────────────────
# HELPER: Simple Forecasting
# ────────────────────────────────────────────────
def forecast_trend(df_all, district, crime_var, forecast_years=3):
    """Simple linear regression forecast for a district"""
    district_data = df_all[df_all['DISTRICT'] == district].sort_values('Year')
    
    if len(district_data) < 5:
        return None, None
    
    X = district_data['Year'].values.reshape(-1, 1)
    y = district_data[crime_var].values
    
    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(district_data['Year'], y)
    
    # Future years
    future_years = np.array(range(2014, 2014 + forecast_years))
    forecast = slope * future_years + intercept
    
    # Trend label
    if slope > 0.5:
        trend = "Likely Increasing"
    elif slope < -0.5:
        trend = "Likely Decreasing"
    else:
        trend = "Stable"
    
    return forecast, trend

# ────────────────────────────────────────────────
# HELPER: Generate PDF Report
# ────────────────────────────────────────────────
def generate_report_html(year, selected_var, df_year, gdf_merged, hotspot_summary):
    """Generate HTML report for PDF export"""
    
    top3 = df_year.nlargest(3, selected_var)
    bottom3 = df_year.nsmallest(3, selected_var)
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #C41E3A; border-bottom: 3px solid #C41E3A; padding-bottom: 10px; }}
            h2 {{ color: #1E3A8A; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #1E3A8A; color: white; }}
            .metric {{ padding: 15px; margin: 10px 0; border-radius: 5px; border: 1px solid #ccc; }}
            .footer {{ margin-top: 50px; font-size: 12px; color: #666; border-top: 1px solid #ccc; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <h1>🚨 Delhi Crime Analysis Report</h1>
        <p><strong>Analysis Period:</strong> {year}<br>
        <strong>Crime Indicator:</strong> {selected_var}<br>
        <strong>Report Generated:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
        
        <h2>1. Executive Summary</h2>
        <p>This report presents a comprehensive spatial analysis of crime patterns across Delhi's districts for the year {year}. 
        The analysis employs GIS-based methodologies including hotspot identification, spatial distribution analysis, 
        and trend forecasting to support evidence-based policing strategies.</p>
        
        <h2>2. Key Findings</h2>
        <div class="metric">
            <strong>Total IPC Crimes (Delhi):</strong> {df_year['TOTAL IPC CRIMES'].sum():,.0f}<br>
            <strong>Average {selected_var}:</strong> {df_year[selected_var].mean():.2f}<br>
            <strong>Highest District:</strong> {top3.iloc[0]['DISTRICT']} ({top3.iloc[0][selected_var]:.2f})<br>
            <strong>Lowest District:</strong> {bottom3.iloc[0]['DISTRICT']} ({bottom3.iloc[0][selected_var]:.2f})
        </div>
        
        <h2>3. Top 3 High-Crime Districts</h2>
        <table>
            <tr><th>Rank</th><th>District</th><th>{selected_var}</th><th>Population</th></tr>
            <tr><td>1</td><td>{top3.iloc[0]['DISTRICT']}</td><td>{top3.iloc[0][selected_var]:,.2f}</td><td>{top3.iloc[0]['Population']:,.0f}</td></tr>
            <tr><td>2</td><td>{top3.iloc[1]['DISTRICT']}</td><td>{top3.iloc[1][selected_var]:,.2f}</td><td>{top3.iloc[1]['Population']:,.0f}</td></tr>
            <tr><td>3</td><td>{top3.iloc[2]['DISTRICT']}</td><td>{top3.iloc[2][selected_var]:,.2f}</td><td>{top3.iloc[2]['Population']:,.0f}</td></tr>
        </table>
        
        <h2>4. Hotspot Analysis</h2>
        <p>Quantile-based classification was performed to identify crime concentration areas:</p>
        <table>
            <tr><th>Risk Category</th><th>Number of Districts</th></tr>
            {hotspot_summary}
        </table>
        <p><em>Note: District-level hotspot approximation performed due to unavailability of point-level FIR data.</em></p>
        
        <h2>5. Methodology</h2>
        <p><strong>Data Sources:</strong> Delhi Police Crime Records (2001-2013), Census 2011 Population Data</p>
        <p><strong>GIS Techniques Applied:</strong></p>
        <ul>
            <li>Choropleth mapping for spatial visualization</li>
            <li>Quantile classification for hotspot identification</li>
            <li>Temporal trend analysis using linear regression</li>
            <li>Buffer analysis (conceptual demonstration)</li>
        </ul>
        
        <h2>6. Policing Implications</h2>
        <ul>
            <li><strong>Resource Allocation:</strong> High-risk districts require enhanced patrol deployment and community policing initiatives</li>
            <li><strong>Prevention Strategies:</strong> Focus on socio-economic factors (migration, unemployment) in hotspot areas</li>
            <li><strong>Surveillance:</strong> Strategic camera placement in medium-risk transition zones</li>
            <li><strong>Inter-District Coordination:</strong> Border areas between high/low risk zones need attention</li>
        </ul>
        
        <h2>7. Limitations & Future Work</h2>
        <ul>
            <li>Analysis based on district-level aggregated data; point-level crime locations unavailable</li>
            <li>Forecasts are trend-based extrapolations for academic purposes, not operational predictions</li>
            <li>Socio-economic variables (income, education) not included in current analysis</li>
            <li>Future work: Integration of real-time FIR data, machine learning-based risk modeling</li>
        </ul>
        
        <div class="footer">
            <p><strong>Disclaimer:</strong> This report is generated for academic and research purposes as part of a GIS & Crime Mapping learning project. 
            Crime data analysis should be interpreted by domain experts for operational decision-making.</p>
            <p>📊 Data: Delhi Police Crime Records | 🛠️ Tools: Python, GeoPandas, Streamlit, Folium</p>
        </div>
    </body>
    </html>
    """
    return html_content

# ────────────────────────────────────────────────
# Load shapefile once
# ────────────────────────────────────────────────
@st.cache_data
def load_shapefile():
    if not os.path.exists(SHAPE_PATH):
        st.error(f"Shapefile not found: {SHAPE_PATH}")
        st.stop()
    gdf = gpd.read_file(SHAPE_PATH)
    gdf[SHAPE_DISTRICT_COL] = gdf[SHAPE_DISTRICT_COL].str.strip()
    return gdf

@st.cache_data
def load_all_years_data():
    """Load all years for trend analysis"""
    all_data = []
    for year in range(2001, 2014):
        csv_path = f"{CSV_FOLDER}qgis_delhi_crime_{year}_with_pop.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df['DISTRICT'] = df['DISTRICT'].str.strip()
            df['Year'] = year
            
            # Calculate rates if missing
            if "Total_IPC_per_100k" not in df.columns:
                df["Total_IPC_per_100k"] = (df["TOTAL IPC CRIMES"] / df["Population"]) * 100_000
            if "Murder_per_100k" not in df.columns:
                df["Murder_per_100k"] = (df["MURDER"] / df["Population"]) * 100_000
            if "Rape_per_100k" not in df.columns:
                df["Rape_per_100k"] = (df["RAPE"] / df["Population"]) * 100_000
                
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True) if all_data else None

gdf_districts = load_shapefile()
df_all_years = load_all_years_data()

# ────────────────────────────────────────────────
# HEADER
# ────────────────────────────────────────────────
st.title("🚨 Delhi Crime Analytics Dashboard (2001–2013)")
st.markdown("**Interactive GIS-based visualization and analysis of crime patterns across Delhi districts**")

# ────────────────────────────────────────────────
# Sidebar controls
# ────────────────────────────────────────────────
st.sidebar.header("⚙️ Controls")

years_available = list(range(2001, 2014))
selected_year = st.sidebar.selectbox("📅 Select Year", years_available, index=len(years_available)-1)

crime_vars = [
    "TOTAL IPC CRIMES", "MURDER", "RAPE", "KIDNAPPING & ABDUCTION",
    "Total_IPC_per_100k", "Murder_per_100k", "Rape_per_100k"
]

selected_var = st.sidebar.selectbox("📊 Crime Indicator", crime_vars, index=4)

map_style = st.sidebar.selectbox("🗺️ Basemap Style", 
                                 ["CartoDB positron", "CartoDB dark_matter", "OpenStreetMap"],
                                 index=0)

# ────────────────────────────────────────────────
# ANALYSIS OPTIONS
# ────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.header("📈 Analysis Tools")

show_hotspots = st.sidebar.checkbox("Show Hotspot Analysis", value=False)
show_buffer = st.sidebar.checkbox("Show Buffer Zones (Demo)", value=False)
show_trends = st.sidebar.checkbox("Show District Trends", value=False)
show_comparison = st.sidebar.checkbox("Show Year Comparison", value=False)
show_pie = st.sidebar.checkbox("Show Crime Distribution", value=False)
show_correlation = st.sidebar.checkbox("Show Correlation Matrix", value=False)
show_inset = st.sidebar.checkbox("Show Delhi Totals", value=False)
show_forecast = st.sidebar.checkbox("Show Crime Forecasting", value=False)
show_llm = st.sidebar.checkbox("🤖 Enable LLM Insights", value=False)

# ────────────────────────────────────────────────
# Load & prepare data for selected year
# ────────────────────────────────────────────────
@st.cache_data
def load_year_data(year):
    csv_path = f"{CSV_FOLDER}qgis_delhi_crime_{year}_with_pop.csv"
    if not os.path.exists(csv_path):
        st.warning(f"CSV not found for {year}: {csv_path}")
        return None
    df = pd.read_csv(csv_path)
    df['DISTRICT'] = df['DISTRICT'].str.strip()
    return df

df_year = load_year_data(selected_year)

if df_year is None:
    st.stop()

# Calculate rates on-the-fly if missing
if selected_var == "Total_IPC_per_100k" and "Total_IPC_per_100k" not in df_year.columns:
    df_year["Total_IPC_per_100k"] = (df_year["TOTAL IPC CRIMES"] / df_year["Population"]) * 100_000
    df_year["Total_IPC_per_100k"] = df_year["Total_IPC_per_100k"].round(1)

if selected_var == "Murder_per_100k" and "Murder_per_100k" not in df_year.columns:
    df_year["Murder_per_100k"] = (df_year["MURDER"] / df_year["Population"]) * 100_000
    df_year["Murder_per_100k"] = df_year["Murder_per_100k"].round(2)

if selected_var == "Rape_per_100k" and "Rape_per_100k" not in df_year.columns:
    df_year["Rape_per_100k"] = (df_year["RAPE"] / df_year["Population"]) * 100_000
    df_year["Rape_per_100k"] = df_year["Rape_per_100k"].round(3)

# ────────────────────────────────────────────────
# TOP/BOTTOM 3 DISTRICTS CARDS
# ────────────────────────────────────────────────
st.subheader(f"📍 Key Districts for {selected_var} ({selected_year})")

top3 = df_year.nlargest(3, selected_var)
bottom3 = df_year.nsmallest(3, selected_var)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("🔴 Highest", top3.iloc[0]['DISTRICT'], f"{top3.iloc[0][selected_var]:,.1f}")
with col2:
    st.metric("2nd", top3.iloc[1]['DISTRICT'], f"{top3.iloc[1][selected_var]:,.1f}")
with col3:
    st.metric("3rd", top3.iloc[2]['DISTRICT'], f"{top3.iloc[2][selected_var]:,.1f}")

with col4:
    st.metric("🟢 Lowest", bottom3.iloc[0]['DISTRICT'], f"{bottom3.iloc[0][selected_var]:,.1f}")
with col5:
    st.metric("2nd", bottom3.iloc[1]['DISTRICT'], f"{bottom3.iloc[1][selected_var]:,.1f}")
with col6:
    st.metric("3rd", bottom3.iloc[2]['DISTRICT'], f"{bottom3.iloc[2][selected_var]:,.1f}")

# ────────────────────────────────────────────────
# Merge with shapefile & Classify Hotspots
# ────────────────────────────────────────────────
gdf_merged = gdf_districts.merge(
    df_year,
    left_on=SHAPE_DISTRICT_COL,
    right_on="DISTRICT",
    how="left"
)

gdf_merged[selected_var] = gdf_merged[selected_var].fillna(0)

# Classify hotspots
gdf_merged = classify_hotspots(gdf_merged, selected_var)

# ────────────────────────────────────────────────
# Create Folium map with Hotspot Layer
# ────────────────────────────────────────────────
m = folium.Map(
    location=[28.65, 77.23],
    zoom_start=10,
    tiles=map_style
)

# Choropleth layer
folium.Choropleth(
    geo_data=gdf_merged,
    data=gdf_merged,
    columns=["DISTRICT", selected_var],
    key_on="feature.properties.DISTRICT",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.4,
    legend_name=selected_var,
    name="Crime Intensity"
).add_to(m)

# Hotspot overlay (if enabled)
if show_hotspots:
    hotspot_colors = {
        'High Risk': '#DC2626',
        'Medium Risk': '#F59E0B',
        'Low Risk': '#10B981',
        'No Data': '#9CA3AF'
    }
    
    def hotspot_style(feature):
        category = feature['properties'].get('Hotspot_Category', 'No Data')
        return {
            'fillColor': hotspot_colors.get(category, '#9CA3AF'),
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.4
        }
    
    folium.GeoJson(
        gdf_merged,
        style_function=hotspot_style,
        name="Hotspot Zones",
        tooltip=GeoJsonTooltip(
            fields=['DISTRICT', 'Hotspot_Category', selected_var],
            aliases=['District:', 'Risk Level:', f'{selected_var}:']
        )
    ).add_to(m)

# Buffer zones demonstration (if enabled)
if show_buffer:
    # Demo: Create buffers around high-crime district centroids
    high_risk_districts = gdf_merged[gdf_merged['Hotspot_Category'] == 'High Risk']
    
    for idx, row in high_risk_districts.iterrows():
        centroid = row.geometry.centroid
        
        # Create demo buffer (5km radius for visualization)
        folium.Circle(
            location=[centroid.y, centroid.x],
            radius=5000,  # 5km
            color='red',
            fill=True,
            fillColor='red',
            fillOpacity=0.15,
            popup=f"5km Buffer - {row['DISTRICT']}",
            tooltip=f"Enhanced Patrol Zone: {row['DISTRICT']}"
        ).add_to(m)
    
    st.sidebar.info("**Buffer Concept:** 5km patrol zones around high-risk district centers. "
                    "Demonstrates spatial buffer analysis for resource allocation.")

tooltip = GeoJsonTooltip(
    fields=["DISTRICT", selected_var, "Population", "Density", "Hotspot_Category"],
    aliases=["District:", f"{selected_var}:", "Population:", "Density:", "Risk Level:"],
    localize=True,
    sticky=True,
    labels=True,
    style="""
        background-color: #F0EFEF;
        border: 1px solid black;
        border-radius: 3px;
        box-shadow: 3px;
        padding: 6px;
    """
)

folium.GeoJson(
    gdf_merged,
    style_function=lambda x: {"fillColor": "transparent", "color": "black", "weight": 1},
    tooltip=tooltip,
    name="District Labels"
).add_to(m)

folium.LayerControl().add_to(m)

st.subheader(f"🗺️ {selected_var} Spatial Distribution — {selected_year}")
st_folium(m, width=1200, height=600)


# ────────────────────────────────────────────────
# HOTSPOT ANALYSIS SECTION
# ────────────────────────────────────────────────
if show_hotspots:
    st.markdown("---")
    st.subheader("🔥 Hotspot Analysis (Quantile-Based Classification)")
    
    hotspot_counts = gdf_merged['Hotspot_Category'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔴 High Risk Zones", hotspot_counts.get('High Risk', 0))
    with col2:
        st.metric("🟡 Medium Risk Zones", hotspot_counts.get('Medium Risk', 0))
    with col3:
        st.metric("🟢 Low Risk Zones", hotspot_counts.get('Low Risk', 0))
    with col4:
        high_pct = (hotspot_counts.get('High Risk', 0) / len(gdf_merged) * 100)
        st.metric("High Risk %", f"{high_pct:.1f}%")
    
    # Hotspot distribution chart
    hotspot_counts_df = hotspot_counts.reset_index(name='Count')
    fig_hotspot = px.bar(
        hotspot_counts_df,
        x='Hotspot_Category',
        y='Count',
        color='Hotspot_Category',
        labels={'Hotspot_Category': 'Risk Category', 'Count': 'Number of Districts'},
        title=f"Hotspot Distribution - {selected_var} ({selected_year})",
        color_discrete_map={
            'High Risk': '#DC2626',
            'Medium Risk': '#F59E0B',
            'Low Risk': '#10B981'
        }
    )
    st.plotly_chart(fig_hotspot, use_container_width=True)
    
    st.info("**Methodology:** Districts classified using quantile-based thresholds (33rd & 67th percentiles). "
            "This approximates crime concentration areas at district level due to unavailability of point-level FIR data.")


# ────────────────────────────────────────────────
# DISTRICT TRENDS (if enabled)
# ────────────────────────────────────────────────
if show_trends and df_all_years is not None:
    st.markdown("---")
    st.subheader("📈 District-wise Temporal Trends (2001-2013)")
    
    selected_districts = st.multiselect(
        "Select districts to compare",
        options=sorted(df_all_years['DISTRICT'].unique()),
        default=top3['DISTRICT'].tolist()[:2]
    )
    
    if selected_districts:
        trend_data = df_all_years[df_all_years['DISTRICT'].isin(selected_districts)]
        
        fig = px.line(
            trend_data,
            x='Year',
            y=selected_var,
            color='DISTRICT',
            markers=True,
            title=f"{selected_var} Trends Comparison",
            labels={selected_var: selected_var, 'Year': 'Year'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────────
# YEAR-OVER-YEAR COMPARISON (if enabled)
# ────────────────────────────────────────────────
if show_comparison and df_all_years is not None:
    st.markdown("---")
    st.subheader("📊 Year-over-Year Comparison")
    
    col1, col2 = st.columns(2)
    with col1:
        year1 = st.selectbox("First Year", years_available, index=0)
    with col2:
        year2 = st.selectbox("Second Year", years_available, index=len(years_available)-1)
    
    df_y1 = df_all_years[df_all_years['Year'] == year1][['DISTRICT', selected_var]].rename(columns={selected_var: f'{year1}'})
    df_y2 = df_all_years[df_all_years['Year'] == year2][['DISTRICT', selected_var]].rename(columns={selected_var: f'{year2}'})
    
    comparison_df = df_y1.merge(df_y2, on='DISTRICT')
    comparison_df['Change %'] = ((comparison_df[f'{year2}'] - comparison_df[f'{year1}']) / comparison_df[f'{year1}'] * 100).round(1)
    comparison_df = comparison_df.sort_values('Change %', ascending=False)
    
    fig = go.Figure(data=[
        go.Bar(name=str(year1), x=comparison_df['DISTRICT'], y=comparison_df[f'{year1}']),
        go.Bar(name=str(year2), x=comparison_df['DISTRICT'], y=comparison_df[f'{year2}'])
    ])
    fig.update_layout(barmode='group', title=f"District Comparison: {year1} vs {year2}", height=500)
    st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────────
# PIE CHART (if enabled)
# ────────────────────────────────────────────────
if show_pie:
    st.markdown("---")
    st.subheader(f"🥧 Crime Composition Breakdown — {selected_year}")

    crime_types = ["MURDER", "RAPE", "KIDNAPPING & ABDUCTION", "DACOITY", "ROBBERY", 
                   "BURGLARY", "THEFT", "RIOTS", "ARSON", "HURT/GREVIOUS HURT", "DOWRY DEATHS"]

    available_crimes = [c for c in crime_types if c in df_year.columns]
    crime_sums = df_year[available_crimes].sum()

    fig_pie = px.pie(
        values=crime_sums.values,
        names=crime_sums.index,
        title="Proportion of Major IPC Crime Categories",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=True, height=500)

    st.plotly_chart(fig_pie, use_container_width=True)

# ────────────────────────────────────────────────
# CORRELATION MATRIX (if enabled)
# ────────────────────────────────────────────────
if show_correlation:
    st.markdown("---")
    st.subheader("🔗 Correlation Analysis")
    
    corr_vars = ['Population', 'Density', 'TOTAL IPC CRIMES', 'MURDER', 'RAPE', 
                 'Total_IPC_per_100k', 'Murder_per_100k', 'Rape_per_100k']
    
    available_vars = [v for v in corr_vars if v in df_year.columns]
    corr_matrix = df_year[available_vars].corr()
    
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        aspect='auto',
        color_continuous_scale='RdBu_r',
        title=f"Correlation Matrix ({selected_year})"
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────────
# DELHI TOTALS (if enabled)
# ────────────────────────────────────────────────
if show_inset:
    st.markdown("---")
    st.subheader(f"🌆 Delhi Totals — {selected_year}")

    total_row = df_year.sum(numeric_only=True)
    key_totals = {
        "Total IPC Crimes": total_row.get("TOTAL IPC CRIMES", 0),
        "Murder": total_row.get("MURDER", 0),
        "Rape": total_row.get("RAPE", 0),
        "Kidnapping & Abduction": total_row.get("KIDNAPPING & ABDUCTION", 0),
        "Population (2011)": total_row.get("Population", 0),
    }

    cols = st.columns(len(key_totals))
    for i, (label, value) in enumerate(key_totals.items()):
        with cols[i]:
            st.metric(label, f"{value:,.0f}" if "Population" in label else f"{int(value):,}")

    if selected_year > 2001 and df_all_years is not None:
        prev_year = df_all_years[df_all_years['Year'] == selected_year-1]["TOTAL IPC CRIMES"].sum()
        change = total_row["TOTAL IPC CRIMES"] - prev_year
        delta = f"{change:+,.0f} vs {selected_year-1}"
        st.caption(delta)

# ────────────────────────────────────────────────
# CRIME FORECASTING (if enabled)
# ────────────────────────────────────────────────
if show_forecast and df_all_years is not None:
    st.markdown("---")
    st.subheader("📈 Crime Trend Forecasting (2014-2016)")
    
    st.info("**Methodology:** Linear regression-based trend extrapolation for academic demonstration. "
            "These are NOT operational predictions but trend-based forecasts for syllabus compliance.")
    
    forecast_district = st.selectbox(
        "Select District for Forecast",
        options=sorted(df_year['DISTRICT'].unique()),
        index=list(df_year['DISTRICT'].unique()).index(top3.iloc[0]['DISTRICT']) if top3.iloc[0]['DISTRICT'] in df_year['DISTRICT'].unique() else 0
    )
    
    forecast_vals, trend_label = forecast_trend(df_all_years, forecast_district, selected_var)
    
    if forecast_vals is not None:
        # Historical data
        hist_data = df_all_years[df_all_years['DISTRICT'] == forecast_district].sort_values('Year')
        
        # Create forecast dataframe
        future_df = pd.DataFrame({
            'Year': [2014, 2015, 2016],
            selected_var: forecast_vals,
            'Type': 'Forecast'
        })
        
        hist_df = hist_data[['Year', selected_var]].copy()
        hist_df['Type'] = 'Historical'
        
        combined = pd.concat([hist_df, future_df])
        
        fig_forecast = px.line(
            combined,
            x='Year',
            y=selected_var,
            color='Type',
            markers=True,
            title=f"{forecast_district} - {selected_var} Forecast",
            labels={selected_var: selected_var, 'Year': 'Year'},
            color_discrete_map={'Historical': '#3B82F6', 'Forecast': '#EF4444'}
        )
        
        fig_forecast.add_vline(x=2013.5, line_dash="dash", line_color="gray", 
                              annotation_text="Forecast Starts")
        
        st.plotly_chart(fig_forecast, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Trend Direction", trend_label)
        with col2:
            st.metric("2014 Forecast", f"{forecast_vals[0]:.1f}")
        with col3:
            st.metric("2016 Forecast", f"{forecast_vals[2]:.1f}")
        
        # Forecast all districts summary
        st.markdown("#### District-wise Trend Summary")
        
        trends_summary = []
        for dist in df_year['DISTRICT'].unique():
            _, trend = forecast_trend(df_all_years, dist, selected_var)
            if trend:
                trends_summary.append({'District': dist, 'Trend': trend})
        
        trends_df = pd.DataFrame(trends_summary)
        trend_counts = trends_df['Trend'].value_counts()
        
        fig_trend_summary = px.pie(
            values=trend_counts.values,
            names=trend_counts.index,
            title="Overall Trend Distribution Across Districts",
            color=trend_counts.index,
            color_discrete_map={
                'Likely Increasing': '#EF4444',
                'Stable': '#F59E0B',
                'Likely Decreasing': '#10B981'
            }
        )
        st.plotly_chart(fig_trend_summary, use_container_width=True)

# ────────────────────────────────────────────────
# LLM INSIGHTS (if enabled)
# ────────────────────────────────────────────────
if show_llm:
    st.markdown("---")
    st.subheader("🤖 AI-Powered Criminological Insights (Llama 3.2)")

    district_context = """
DELHI DISTRICT SOCIO-SPATIAL PROFILES (2001-2013):

• North East Delhi: Highest density, massive in-migration from UP/Bihar, large unauthorized colonies, poor infrastructure → persistent hotspot
• East Delhi: Trans-Yamuna urbanization, working-class hubs, resettlement colonies → high theft, robbery, riots
• North West Delhi: Explosive growth (+88% 2001-11), Rohini + outer areas → rising crime during urbanization
• West Delhi: Dense middle-class areas, commercial activity, metro connectivity → mainly property crimes
• South West Delhi: Fast-growing (Dwarka, airport), mixed planning → moderate crime, increasing
• South Delhi: Affluent, highly educated, strong security → generally low street crime
• Central Delhi: Commercial heart, crowded markets → property crimes high, violent moderated
• North Delhi: Old Delhi + DU influence, moderate density → balanced profile
• New Delhi: Lutyens' + VIP zone, extreme policing → consistently lowest crime rates

Key trends: Crime followed urbanization & migration westward/northward. Density + low socio-economic status strongest predictors.
"""

    tab1, tab2 = st.tabs(["Pattern Analysis", "Ask Anything"])

    with tab1:
        if st.button("🔍 Explain Current Crime Patterns"):
            with st.spinner("Analyzing spatial-socioeconomic factors..."):
                top_districts = df_year.nlargest(4, selected_var)
                bottom_districts = df_year.nsmallest(2, selected_var)

                prompt = f"""{district_context}

Year: {selected_year}
Indicator: {selected_var}

Top 4 districts:
1. {top_districts.iloc[0]['DISTRICT']} → {top_districts.iloc[0][selected_var]:,.1f}
2. {top_districts.iloc[1]['DISTRICT']} → {top_districts.iloc[1][selected_var]:,.1f}
3. {top_districts.iloc[2]['DISTRICT']} → {top_districts.iloc[2][selected_var]:,.1f}
4. {top_districts.iloc[3]['DISTRICT']} → {top_districts.iloc[3][selected_var]:,.1f}

Lowest 2:
1. {bottom_districts.iloc[0]['DISTRICT']} → {bottom_districts.iloc[0][selected_var]:,.1f}
2. {bottom_districts.iloc[1]['DISTRICT']} → {bottom_districts.iloc[1][selected_var]:,.1f}

Provide 4-6 evidence-based insights explaining the pattern. Focus on migration, density, policing, urbanization, socio-economics. Be concise and spatial."""
                
                response = ask_llm(prompt, model="llama3.2")
                st.markdown("**Llama 3.2 Analysis:**")
                st.info(response)

    with tab2:
        user_question = st.text_input("Ask about Delhi crime patterns, districts, or trends:", 
                                      placeholder="e.g. Why is North East always high? Is West Delhi safer?")

        if user_question and st.button("Get Answer"):
            with st.spinner("Consulting knowledge base..."):
                context = f"""{district_context}

Current: {selected_year}, {selected_var}
Delhi total: {df_year['TOTAL IPC CRIMES'].sum():,} (rate: {df_year['Total_IPC_per_100k'].mean():.1f}/100k)
Highest: {df_year.loc[df_year[selected_var].idxmax(), 'DISTRICT']} ({df_year[selected_var].max():.1f})
Lowest: {df_year.loc[df_year[selected_var].idxmin(), 'DISTRICT']} ({df_year[selected_var].min():.1f})

Question: {user_question}

Answer factually using district profiles and trends."""
                
                response = ask_llm(context, model="llama3.2")
                st.success(response)

# ────────────────────────────────────────────────
# GENERATE CRIME ANALYSIS REPORT (PDF)
# ────────────────────────────────────────────────
st.markdown("---")
st.subheader("📄 Generate Crime Analysis Report")

if st.button("🎯 Generate Comprehensive Crime Report (HTML)"):
    with st.spinner("Generating report..."):
        hotspot_counts = gdf_merged['Hotspot_Category'].value_counts()
        hotspot_summary_html = ""
        for cat, count in hotspot_counts.items():
            hotspot_summary_html += f"<tr><td>{cat}</td><td>{count}</td></tr>"
        
        report_html = generate_report_html(
            selected_year, 
            selected_var, 
            df_year, 
            gdf_merged, 
            hotspot_summary_html
        )
        
        # Offer download
        b64 = base64.b64encode(report_html.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="Delhi_Crime_Report_{selected_year}.html">📥 Download Report (HTML)</a>'
        st.markdown(href, unsafe_allow_html=True)
        
        st.success("✅ Report generated! Click above to download. Open in browser and print to PDF if needed.")
        
        with st.expander("📋 Preview Report"):
            # st.markdown(report_html, unsafe_allow_html=True)
            st.html(report_html, width="stretch", unsafe_allow_javascript=False)

# ────────────────────────────────────────────────
# STATISTICS TABLE
# ────────────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Quick Statistics")

cols_to_show = ["DISTRICT", selected_var, "Population", "TOTAL IPC CRIMES", "Hotspot_Category"]
stats_df = gdf_merged[cols_to_show].copy()
stats_df = stats_df.loc[:, ~stats_df.columns.duplicated()]

if any(col.endswith('_x') or col.endswith('_y') for col in stats_df.columns):
    rename_dict = {}
    for col in stats_df.columns:
        if col.endswith('_x'):
            base = col.replace('_x', '')
            if base in stats_df.columns:
                stats_df = stats_df.drop(columns=base)
            rename_dict[col] = base
        elif col.endswith('_y'):
            rename_dict[col] = col.replace('_y', '_shp')
    stats_df = stats_df.rename(columns=rename_dict)

stats_df = stats_df.sort_values(selected_var, ascending=False)

st.dataframe(
    stats_df.reset_index(drop=True).style.format({
        selected_var: "{:,.1f}",
        "Population": "{:,.0f}",
        "TOTAL IPC CRIMES": "{:,.0f}",
    }),
    use_container_width=True
)

# ────────────────────────────────────────────────
# FOOTER
# ────────────────────────────────────────────────
st.markdown("---")
st.caption("📊 Data: District-wise crime under various sections of Indian Penal Code (IPC) crimes during 2001-2013 | 🛠️ Built with Python, Streamlit, GeoPandas, Folium")