"""
COVID-19 Interactive Global Dashboard
=====================================

This Streamlit application provides an interactive interface for exploring
global COVID-19 data with user-controlled parameters and real-time visualizations.

Key Features:
- Country and date range selection
- Hospitalization and ICU data analysis  
- Interactive visualizations with Plotly
- Real-time metric calculations
- Professional dashboard layout

To run this application:
1. Save this file as 'covid_dashboard.py'
2. Install requirements: pip install streamlit plotly pandas numpy
3. Run: streamlit run covid_dashboard.py

Author: Senior Data Scientist
Date: 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# PAGE CONFIGURATION AND SETUP
# =============================================================================

# Configure the Streamlit page - this must be the first Streamlit command
st.set_page_config(
    page_title="COVID-19 Global Dashboard",
    page_icon="🦠",
    layout="wide",  # Use full width of the browser
    initial_sidebar_state="expanded"  # Start with sidebar open
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main dashboard styling */
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    /* Metric cards styling */
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f4e79;
        margin: 0.5rem 0;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #fafafa;
    }
    
    /* Warning and info boxes */
    .stAlert > div {
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING AND CACHING
# =============================================================================

@st.cache_data(ttl=3600)  # Cache data for 1 hour to improve performance
def load_covid_data():
    """
    Load and prepare COVID-19 data with caching for performance.
    In a real application, this would load from the Our World in Data CSV.
    For demonstration, we'll create comprehensive sample data.
    """
    
    # Create comprehensive sample dataset with all required fields
    np.random.seed(42)  # For reproducible random data
    
    countries = [
        'United States', 'United Kingdom', 'Germany', 'France', 'Italy', 
        'Spain', 'India', 'Brazil', 'Japan', 'South Korea', 'Australia',
        'Canada', 'Netherlands', 'Sweden', 'Kenya', 'South Africa',
        'Nigeria', 'Egypt', 'Mexico', 'Argentina'
    ]
    
    iso_codes = [
        'USA', 'GBR', 'DEU', 'FRA', 'ITA', 'ESP', 'IND', 'BRA', 'JPN', 
        'KOR', 'AUS', 'CAN', 'NLD', 'SWE', 'KEN', 'ZAF', 'NGA', 'EGY', 
        'MEX', 'ARG'
    ]
    
    continents = [
        'North America', 'Europe', 'Europe', 'Europe', 'Europe', 'Europe',
        'Asia', 'South America', 'Asia', 'Asia', 'Oceania', 'North America',
        'Europe', 'Europe', 'Africa', 'Africa', 'Africa', 'Africa',
        'North America', 'South America'
    ]
    
    # Generate 2+ years of daily data
    date_range = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    
    all_data = []
    
    for i, country in enumerate(countries):
        country_population = np.random.randint(10_000_000, 350_000_000)
        
        for j, current_date in enumerate(date_range):
            # Create realistic progression patterns
            days_since_start = j
            
            # Simulate realistic COVID progression with waves
            base_cases = min(days_since_start * np.random.randint(50, 500), 
                           country_population * 0.3)
            
            # Add wave patterns using sine waves with different periods
            wave1 = np.sin(days_since_start / 100) * base_cases * 0.3
            wave2 = np.sin(days_since_start / 200) * base_cases * 0.2
            wave3 = np.sin(days_since_start / 300) * base_cases * 0.1
            
            total_cases = max(0, int(base_cases + wave1 + wave2 + wave3))
            
            # Calculate other metrics based on total cases
            total_deaths = int(total_cases * np.random.uniform(0.01, 0.05))
            new_cases = max(0, int(total_cases * np.random.uniform(0.001, 0.02)))
            new_deaths = max(0, int(new_cases * np.random.uniform(0.01, 0.03)))
            
            # Hospitalization data (key new feature)
            hosp_patients = max(0, int(new_cases * np.random.uniform(0.05, 0.15)))
            icu_patients = max(0, int(hosp_patients * np.random.uniform(0.1, 0.3)))
            
            # Vaccination data (starts from 2021)
            if current_date >= pd.Timestamp('2021-01-01'):
                days_since_vacc = (current_date - pd.Timestamp('2021-01-01')).days
                total_vaccinations = min(
                    int(country_population * min(days_since_vacc / 365 * 1.8, 2.0)),
                    country_population * 2
                )
                people_vaccinated = min(total_vaccinations, country_population)
                people_fully_vaccinated = max(0, total_vaccinations - country_population)
            else:
                total_vaccinations = 0
                people_vaccinated = 0
                people_fully_vaccinated = 0
            
            all_data.append({
                'iso_code': iso_codes[i],
                'continent': continents[i],
                'location': country,
                'date': current_date,
                'total_cases': total_cases,
                'new_cases': new_cases,
                'total_deaths': total_deaths,
                'new_deaths': new_deaths,
                'hosp_patients': hosp_patients,  # New field
                'icu_patients': icu_patients,    # New field
                'total_vaccinations': total_vaccinations,
                'people_vaccinated': people_vaccinated,
                'people_fully_vaccinated': people_fully_vaccinated,
                'population': country_population
            })
    
    df = pd.DataFrame(all_data)
    
    # Calculate derived metrics
    df['case_fatality_rate'] = (df['total_deaths'] / df['total_cases'].replace(0, np.nan)) * 100
    df['vaccination_rate'] = (df['people_fully_vaccinated'] / df['population']) * 100
    df['hospitalization_rate'] = (df['hosp_patients'] / df['new_cases'].replace(0, np.nan)) * 100
    df['icu_rate'] = (df['icu_patients'] / df['hosp_patients'].replace(0, np.nan)) * 100
    
    return df

@st.cache_data
def get_country_list(df):
    """Get sorted list of available countries for the selector."""
    return sorted(df['location'].unique())

@st.cache_data
def get_date_range(df):
    """Get the available date range from the dataset."""
    return df['date'].min().date(), df['date'].max().date()

# =============================================================================
# USER INTERFACE COMPONENTS
# =============================================================================

def create_sidebar_controls(df):
    """
    Create the sidebar with all user input controls.
    This is where users interact with the dashboard.
    """
    st.sidebar.title("🎛️ Dashboard Controls")
    st.sidebar.markdown("---")
    
    # Country Selection
    st.sidebar.subheader("📍 Country Selection")
    
    # Get available countries
    available_countries = get_country_list(df)
    
    # Multi-select for countries with intelligent defaults
    default_countries = [
        country for country in ['United States', 'United Kingdom', 'Germany', 'India', 'Brazil']
        if country in available_countries
    ][:3]  # Limit to 3 countries for performance
    
    selected_countries = st.sidebar.multiselect(
        "Choose countries to analyze:",
        options=available_countries,
        default=default_countries,
        help="Select 1-5 countries for optimal visualization performance"
    )
    
    # Date Range Selection
    st.sidebar.subheader("📅 Date Range")
    
    min_date, max_date = get_date_range(df)
    
    # Default to last year of data for better performance
    default_start = max(min_date, max_date - timedelta(days=365))
    
    date_range = st.sidebar.date_input(
        "Select date range:",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Choose the time period for your analysis"
    )
    
    # Analysis Options
    st.sidebar.subheader("📊 Analysis Options")
    
    analysis_type = st.sidebar.selectbox(
        "Primary focus:",
        ["Overview", "Cases & Deaths", "Hospitalizations", "Vaccinations"],
        help="Choose the main aspect of COVID-19 data to analyze"
    )
    
    # Advanced options in an expander to save space
    with st.sidebar.expander("🔧 Advanced Options"):
        show_per_capita = st.checkbox("Show per capita metrics", value=True)
        show_moving_average = st.checkbox("Apply 7-day moving average", value=True)
        log_scale = st.checkbox("Use logarithmic scale for large numbers", value=False)
    
    return {
        'countries': selected_countries,
        'date_range': date_range,
        'analysis_type': analysis_type,
        'show_per_capita': show_per_capita,
        'show_moving_average': show_moving_average,
        'log_scale': log_scale
    }

def filter_data(df, controls):
    """
    Filter the dataset based on user selections.
    This is where we apply all the user's choices to the data.
    """
    # Start with the full dataset
    filtered_df = df.copy()
    
    # Filter by countries
    if controls['countries']:
        filtered_df = filtered_df[filtered_df['location'].isin(controls['countries'])]
    else:
        # If no countries selected, show a warning and use default
        st.warning("⚠️ No countries selected. Showing data for United States.")
        filtered_df = filtered_df[filtered_df['location'] == 'United States']
    
    # Filter by date range
    if len(controls['date_range']) == 2:
        start_date, end_date = controls['date_range']
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.Timestamp(start_date)) & 
            (filtered_df['date'] <= pd.Timestamp(end_date))
        ]
    
    # Apply moving averages if requested
    if controls['show_moving_average']:
        for country in filtered_df['location'].unique():
            country_mask = filtered_df['location'] == country
            filtered_df.loc[country_mask, 'new_cases_ma'] = (
                filtered_df.loc[country_mask, 'new_cases'].rolling(window=7, min_periods=1).mean()
            )
            filtered_df.loc[country_mask, 'new_deaths_ma'] = (
                filtered_df.loc[country_mask, 'new_deaths'].rolling(window=7, min_periods=1).mean()
            )
    
    return filtered_df

# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_summary_metrics(df):
    """
    Create key performance indicator cards at the top of the dashboard.
    These provide immediate insights at a glance.
    """
    # Calculate summary statistics
    latest_data = df.groupby('location').last()
    
    total_cases = latest_data['total_cases'].sum()
    total_deaths = latest_data['total_deaths'].sum()
    avg_vaccination = latest_data['vaccination_rate'].mean()
    countries_analyzed = len(latest_data)
    
    # Create four columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Cases",
            value=f"{total_cases:,}",
            delta=f"{latest_data['new_cases'].sum():,} new"
        )
    
    with col2:
        st.metric(
            label="Total Deaths", 
            value=f"{total_deaths:,}",
            delta=f"{(total_deaths/total_cases*100):.2f}% CFR"
        )
    
    with col3:
        st.metric(
            label="Avg Vaccination Rate",
            value=f"{avg_vaccination:.1f}%",
            delta="Fully vaccinated population"
        )
    
    with col4:
        st.metric(
            label="Countries Analyzed",
            value=str(countries_analyzed),
            delta="Selected for comparison"
        )

def create_cases_visualization(df, controls):
    """
    Create visualizations focused on cases and deaths.
    This demonstrates how to build complex, interactive charts with Plotly.
    """
    st.subheader("📈 Cases and Deaths Analysis")
    
    # Create subplot with secondary y-axis for deaths
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Total Cases Over Time', 'Daily New Cases',
            'Total Deaths Over Time', 'Case Fatality Rate'
        ),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    colors = px.colors.qualitative.Set1
    
    for i, country in enumerate(df['location'].unique()):
        country_data = df[df['location'] == country].sort_values('date')
        color = colors[i % len(colors)]
        
        # Total cases
        fig.add_trace(
            go.Scatter(
                x=country_data['date'],
                y=country_data['total_cases'],
                name=f"{country} - Cases",
                line=dict(color=color, width=2),
                hovertemplate=f"<b>{country}</b><br>" +
                             "Date: %{x}<br>" +
                             "Total Cases: %{y:,}<extra></extra>"
            ),
            row=1, col=1
        )
        
        # New cases (with moving average if enabled)
        if controls['show_moving_average'] and 'new_cases_ma' in country_data.columns:
            y_data = country_data['new_cases_ma']
            name_suffix = " (7-day avg)"
        else:
            y_data = country_data['new_cases']
            name_suffix = ""
        
        fig.add_trace(
            go.Scatter(
                x=country_data['date'],
                y=y_data,
                name=f"{country} - New{name_suffix}",
                line=dict(color=color, width=2, dash='dot'),
                hovertemplate=f"<b>{country}</b><br>" +
                             "Date: %{x}<br>" +
                             f"New Cases{name_suffix}: %{{y:,.0f}}<extra></extra>"
            ),
            row=1, col=2
        )
        
        # Total deaths
        fig.add_trace(
            go.Scatter(
                x=country_data['date'],
                y=country_data['total_deaths'],
                name=f"{country} - Deaths",
                line=dict(color=color, width=2, dash='dash'),
                hovertemplate=f"<b>{country}</b><br>" +
                             "Date: %{x}<br>" +
                             "Total Deaths: %{y:,}<extra></extra>"
            ),
            row=2, col=1
        )
        
        # Case fatality rate
        fig.add_trace(
            go.Scatter(
                x=country_data['date'],
                y=country_data['case_fatality_rate'],
                name=f"{country} - CFR",
                line=dict(color=color, width=2, dash='dashdot'),
                hovertemplate=f"<b>{country}</b><br>" +
                             "Date: %{x}<br>" +
                             "Case Fatality Rate: %{y:.2f}%<extra></extra>"
            ),
            row=2, col=2
        )
    
    # Update layout for professional appearance
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text="COVID-19 Cases and Deaths Trends",
        title_x=0.5,
        hovermode='x unified'
    )
    
    # Apply log scale if requested
    if controls['log_scale']:
        fig.update_yaxes(type="log", row=1, col=1)
        fig.update_yaxes(type="log", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)

def create_hospitalization_visualization(df, controls):
    """
    Create visualizations focused on hospitalization and ICU data.
    This is one of the new features requested by the user.
    """
    st.subheader("🏥 Hospitalization and ICU Analysis")
    
    # Check if hospitalization data is available
    if df['hosp_patients'].isna().all():
        st.warning("⚠️ Hospitalization data is not available for the selected period.")
        return
    
    # Create hospitalization dashboard
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Hospital Patients Over Time', 'ICU Patients Over Time',
            'Hospitalization Rate (%)', 'ICU Occupancy Rate (%)'
        )
    )
    
    colors = px.colors.qualitative.Set2
    
    for i, country in enumerate(df['location'].unique()):
        country_data = df[df['location'] == country].sort_values('date')
        color = colors[i % len(colors)]
        
        # Hospital patients
        fig.add_trace(
            go.Scatter(
                x=country_data['date'],
                y=country_data['hosp_patients'],
                name=f"{country} - Hospital",
                line=dict(color=color, width=3),
                hovertemplate=f"<b>{country}</b><br>" +
                             "Date: %{x}<br>" +
                             "Hospital Patients: %{y:,}<extra></extra>"
            ),
            row=1, col=1
        )
        
        # ICU patients
        fig.add_trace(
            go.Scatter(
                x=country_data['date'],
                y=country_data['icu_patients'],
                name=f"{country} - ICU",
                line=dict(color=color, width=3, dash='dot'),
                hovertemplate=f"<b>{country}</b><br>" +
                             "Date: %{x}<br>" +
                             "ICU Patients: %{y:,}<extra></extra>"
            ),
            row=1, col=2
        )
        
        # Hospitalization rate
        fig.add_trace(
            go.Scatter(
                x=country_data['date'],
                y=country_data['hospitalization_rate'],
                name=f"{country} - Hosp Rate",
                line=dict(color=color, width=2),
                hovertemplate=f"<b>{country}</b><br>" +
                             "Date: %{x}<br>" +
                             "Hospitalization Rate: %{y:.1f}%<extra></extra>"
            ),
            row=2, col=1
        )
        
        # ICU rate
        fig.add_trace(
            go.Scatter(
                x=country_data['date'],
                y=country_data['icu_rate'],
                name=f"{country} - ICU Rate",
                line=dict(color=color, width=2, dash='dash'),
                hovertemplate=f"<b>{country}</b><br>" +
                             "Date: %{x}<br>" +
                             "ICU Rate: %{y:.1f}%<extra></extra>"
            ),
            row=2, col=2
        )
    
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text="Healthcare System Capacity and Utilization",
        title_x=0.5
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add explanatory text to help users understand the metrics
    with st.expander("ℹ️ Understanding Hospitalization Metrics"):
        st.markdown("""
        **Hospital Patients**: Current number of COVID-19 patients in hospitals
        
        **ICU Patients**: Current number of COVID-19 patients in intensive care units
        
        **Hospitalization Rate**: Percentage of new cases requiring hospitalization
        
        **ICU Rate**: Percentage of hospitalized patients requiring intensive care
        
        These metrics help understand healthcare system capacity and the severity
        of COVID-19 impact in different countries.
        """)

def create_vaccination_visualization(df, controls):
    """
    Create comprehensive vaccination progress visualizations.
    """
    st.subheader("💉 Vaccination Progress Analysis")
    
    # Filter data to vaccination period (2021 onwards for realistic data)
    vacc_data = df[df['date'] >= '2021-01-01']
    
    if vacc_data.empty:
        st.warning("⚠️ No vaccination data available for the selected period.")
        return
    
    # Create vaccination dashboard
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Cumulative Vaccinations', 'Daily Vaccination Rate',
            'Population Vaccination Coverage', 'Vaccination Pace Comparison'
        )
    )
    
    colors = px.colors.qualitative.Pastel
    
    for i, country in enumerate(vacc_data['location'].unique()):
        country_data = vacc_data[vacc_data['location'] == country].sort_values('date')
        color = colors[i % len(colors)]
        
        # Total vaccinations
        if controls['show_per_capita']:
            y_data = country_data['total_vaccinations'] / country_data['population'] * 100
            y_title = "Vaccinations per 100 people"
        else:
            y_data = country_data['total_vaccinations']
            y_title = "Total vaccinations"
        
        fig.add_trace(
            go.Scatter(
                x=country_data['date'],
                y=y_data,
                name=f"{country}",
                line=dict(color=color, width=3),
                hovertemplate=f"<b>{country}</b><br>" +
                             "Date: %{x}<br>" +
                             f"{y_title}: %{{y:,.1f}}<extra></extra>"
            ),
            row=1, col=1
        )
        
        # Vaccination coverage
        fig.add_trace(
            go.Scatter(
                x=country_data['date'],
                y=country_data['vaccination_rate'],
                name=f"{country} - Coverage",
                line=dict(color=color, width=2, dash='dot'),
                hovertemplate=f"<b>{country}</b><br>" +
                             "Date: %{x}<br>" +
                             "Fully Vaccinated: %{y:.1f}%<extra></extra>"
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        title_text="COVID-19 Vaccination Progress",
        title_x=0.5
    )
    
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# MAIN APPLICATION LOGIC
# =============================================================================

def main():
    """
    Main application function that orchestrates the entire dashboard.
    This is where we tie all the components together.
    """
    
    # Page header
    st.markdown("<h1 class='main-header'>🦠 COVID-19 Global Interactive Dashboard</h1>", 
                unsafe_allow_html=True)
    
    # Load data with progress indicator
    with st.spinner("Loading COVID-19 data... Please wait."):
        df = load_covid_data()
    
    if df is None:
        st.error("❌ Failed to load data. Please check your data source.")
        return
    
    # Success message with data info
    st.success(f"✅ Data loaded successfully! Analyzing {df['location'].nunique()} countries from {df['date'].min().date()} to {df['date'].max().date()}")
    
    # Create sidebar controls
    controls = create_sidebar_controls(df)
    
    # Filter data based on user selections
    filtered_df = filter_data(df, controls)
    
    # Check if we have data after filtering
    if filtered_df.empty:
        st.error("❌ No data available for the selected criteria. Please adjust your selections.")
        return
    
    # Display summary metrics
    create_summary_metrics(filtered_df)
    
    st.markdown("---")
    
    # Create visualizations based on analysis type
    if controls['analysis_type'] == "Overview":
        # Show a combination of key metrics
        col1, col2 = st.columns(2)
        
        with col1:
            create_cases_visualization(filtered_df, controls)
        
        with col2:
            if not filtered_df['hosp_patients'].isna().all():
                create_hospitalization_visualization(filtered_df, controls)
            else:
                create_vaccination_visualization(filtered_df, controls)
    
    elif controls['analysis_type'] == "Cases & Deaths":
        create_cases_visualization(filtered_df, controls)
    
    elif controls['analysis_type'] == "Hospitalizations":
        create_hospitalization_visualization(filtered_df, controls)
    
    elif controls['analysis_type'] == "Vaccinations":
        create_vaccination_visualization(filtered_df, controls)
    
    # Add data export functionality
    st.markdown("---")
    
    with st.expander("📥 Export Data"):
        st.markdown("Download the filtered dataset for your own analysis:")
        
        # Prepare export data
        export_df = filtered_df.copy()
        export_df['date'] = export_df['date'].dt.strftime('%Y-%m-%d')
        
        csv = export_df.to_csv(index=False)
        
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"covid_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        st.info(f"Dataset contains {len(export_df):,} rows and {len(export_df.columns)} columns")

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()

# =============================================================================
# ADDITIONAL NOTES FOR DEPLOYMENT
# =============================================================================

"""
DEPLOYMENT INSTRUCTIONS:
========================

1. Save this file as 'covid_dashboard.py'

2. Create a requirements.txt file with:
   streamlit>=1.28.0
   plotly>=5.15.0
   pandas>=2.0.0
   numpy>=1.24.0

3. Run locally:
   streamlit run covid_dashboard.py

4. Deploy to Streamlit Cloud:
   - Push code to GitHub
   - Connect repository to Streamlit Cloud
   - Deploy automatically

5. For production deployment:
   - Add error logging
   - Implement user authentication if needed
   - Add database connection for real-time data
   - Configure caching strategies
   - Add monitoring and analytics

PERFORMANCE OPTIMIZATION TIPS:
==============================

- Use st.cache_data for expensive computations
- Limit default country selections to 3-5
- Implement data pagination for large datasets
- Use efficient data formats (Parquet instead of CSV)
- Consider using DuckDB for large-scale data processing
- Implement progressive loading for better user experience

EXTENSION IDEAS:
===============

- Add predictive modeling capabilities
- Implement real-time data updates via APIs
- Add geospatial visualizations with country maps
- Include economic impact metrics
- Add email reporting functionality
- Implement user preferences and saved configurations
"""