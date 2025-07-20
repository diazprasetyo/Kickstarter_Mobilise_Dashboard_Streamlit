import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# Set page config
st.set_page_config(
    page_title="Mobilise AU Dashboard",
    layout="wide"
)

# ----------- LOAD DATA -----------
def get_csv_url(sheets_url, gid=0):
    sheet_id = sheets_url.split('/d/')[1].split('/')[0]
    
    # Auto-extract gid from URL if present
    if 'gid=' in sheets_url:
        gid = sheets_url.split('gid=')[1].split('&')[0].split('#')[0]
    
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data_from_sheets(sheets_url, sheet_tab=0):
    try:
        csv_url = get_csv_url(sheets_url, sheet_tab)
        df = pd.read_csv(csv_url)
        
        # Parse dates more robustly
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        
        # Remove rows with invalid dates
        df = df.dropna(subset=['Date'])
        
        # Create month column for aggregation
        df['Month'] = df['Date'].dt.to_period('M').dt.to_timestamp()
        
        # Add back the Date column (using the month start date)
        df['Date'] = df['Month']
        
        return df, None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=3600)  # Fallback to local CSV
def load_data():
    df = pd.read_csv('data/demo_data.csv')
    
    # Parse dates more robustly
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    
    # Remove rows with invalid dates
    df = df.dropna(subset=['Date'])
    
    # Create month column for aggregation
    df['Month'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    
    # Add back the Date column (using the month start date)
    df['Date'] = df['Month']
    
    return df

# Configuration - UPDATE THIS WITH GOOGLE SHEETS URL
SHEETS_URL = "https://docs.google.com/spreadsheets/d/1nDAi1EsS07YlP8lnLGkbep2Y3xfYDNrMFDpe8vdsqJs/edit?gid=1058530763"
USE_GOOGLE_SHEETS = True  # Set to False to use local CSV

# TTL + Manual + Auto-refresh
# Initialize refresh tracking
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

# Create header with refresh controls
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    last_update = datetime.fromtimestamp(st.session_state.last_refresh)
    st.write(f"Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")

with col2:
    # Show next refresh time
    next_refresh = datetime.fromtimestamp(st.session_state.last_refresh + 3600)
    st.write(f"Next refresh: {next_refresh.strftime('%H:%M')}")

with col3:
    # Manual refresh button
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.session_state.last_refresh = time.time()
        st.rerun()

# Auto-refresh check (every hour)
if time.time() - st.session_state.last_refresh > 3600:
    st.cache_data.clear()
    st.session_state.last_refresh = time.time()
    st.rerun()

# Load data
if USE_GOOGLE_SHEETS and "YOUR_SHEET_ID" not in SHEETS_URL:
    df, error = load_data_from_sheets(SHEETS_URL)
    
    if error:
        st.error(f"Error loading from Google Sheets: {error}")
        st.info("Falling back to local CSV file...")
        df = load_data()
    else:
        st.success("Data loaded from Google Sheets")
else:
    df = load_data()
    if USE_GOOGLE_SHEETS:
        st.warning("Please update SHEETS_URL with your Google Sheets ID")

# # Display data info
# st.write(f"📊 Dataset: {len(df)} rows, {len(df.columns)} columns")
# st.write(f"📅 Date range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")

# clean metric name Function Definition
def clean_metric_name(metric_name):
    """Convert underscores to spaces and title-case for display."""
    return metric_name.replace('_', ' ').title()

# ----------- SIDEBAR NAVIGATION -----------
st.sidebar.title("Mobilise Dashboard")
page = st.sidebar.radio(
    "Go to Page:",
    (
        "1. Ignite a Movement",
        "2. Empower those experiencing homelessness",
        "3. Promote direct participation in the solution",
        "4. Expanded outreach opportunities",
        "5. Distribution of funds",
        "6. Engagement of the wider community",
        "7. A cultural shift in society",
        "8. People progressing post-homelessness",
        "9. Homelessness humanised through storytelling",
        "10. New & innovative responses"
    )
)

st.title("Mobilise Theory of Change Dashboard")

# Page 1
if page == "1. Ignite a Movement":
    st.header("Ignite a Movement")
    df_p1 = df[df["Pillar"] == 1].copy()

    df_p1["Date"] = pd.to_datetime(df_p1["Date"], dayfirst=True)

    # Filters
    st.sidebar.subheader("Filters (Page 1)")
    min_date, max_date = df_p1["Month"].min(), df_p1["Month"].max()
    
    # Handle case where we might have only one date
    if len(df_p1["Month"].unique()) == 1:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date])
    else:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date])
    
    # Ensure we have a range
    if len(selected_range) == 1:
        selected_range = [selected_range[0], selected_range[0]]
    
    categories = df_p1["Metric_Category"].dropna().unique().tolist()
    selected_categories = st.sidebar.multiselect("📂 Metric Category", categories, default=categories)

    # Apply filters
    df_p1_filtered = df_p1[
        (df_p1["Month"] >= pd.to_datetime(selected_range[0])) &
        (df_p1["Month"] <= pd.to_datetime(selected_range[1])) &
        (df_p1["Metric_Category"].isin(selected_categories))
    ]
    col1, col2, col3, col4 = st.columns(4)

    # Get latest values for key metrics
    latest_date = df['Date'].max()
    latest_data = df[df['Date'] == latest_date]

    with col1:
        total_volunteers = latest_data[latest_data['Agg_Metric'] == 'Total_Volunteers']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_Volunteers'].empty else 0
        st.metric("Total Volunteers", total_volunteers)

    with col2:
        total_signups = latest_data[latest_data['Agg_Metric'] == 'Total_Actual_SignUps_Organic']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_Actual_SignUps_Organic'].empty else 0
        st.metric("Organic Sign-ups", total_signups)

    with col3:
        total_followers = latest_data[latest_data['Agg_Metric'].str.contains('Followers', na=False)]['Agg_Value'].sum()
        st.metric("Total Social Media Followers", total_followers)

    with col4:
        total_engagements = latest_data[latest_data['Agg_Metric'].str.contains('Engagements', na=False)]['Agg_Value'].sum()
        st.metric("Total Engagements", total_engagements)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        earned_media = latest_data[latest_data['Agg_Metric'] == 'Total_Mentions_Earned']['Agg_Value'].sum()
        st.metric("Earned Media Mentions", earned_media)

    with col2:
        positive_sentiment = latest_data[latest_data['Agg_Metric'] == 'Total_Positive_Mentions_Earned']['Agg_Value'].sum()
        st.metric("Positive Sentiment Score", f"{positive_sentiment}%")

    # Main visualizations
    st.header("📈 Detailed Analytics")

    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Category Overview", "📈 Time Series", "🔍 Metric Details"])

    with tab1:
        # ========== ROW 1: VOLUNTEER METRICS ==========
        st.header("👥 Volunteer Metrics")
        
        # Volunteers metrics with retention analysis
        volunteers_data = df_p1_filtered[df_p1_filtered['Metric_Category'] == 'Volunteers']
        if not volunteers_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Create volunteer metrics chart
                fig_volunteers = px.bar(
                    volunteers_data.groupby('Agg_Metric')['Agg_Value'].mean().reset_index(),
                    x='Agg_Metric', y='Agg_Value',
                    title="👥 Volunteer Metrics Overview",
                    color='Agg_Metric'
                )
                fig_volunteers.update_layout(showlegend=False)
                st.plotly_chart(fig_volunteers, use_container_width=True)
            
            with col2:
                # Create engagement distribution chart
                # Calculate retention and engagement rates
                latest_volunteers = latest_data[latest_data['Metric_Category'] == 'Volunteers']
                
                total_vols = latest_volunteers[latest_volunteers['Agg_Metric'] == 'Total_Volunteers']['Agg_Value'].iloc[0] if not latest_volunteers[latest_volunteers['Agg_Metric'] == 'Total_Volunteers'].empty else 0
                repeat_vols = latest_volunteers[latest_volunteers['Agg_Metric'] == 'Repeat_Volunteers']['Agg_Value'].iloc[0] if not latest_volunteers[latest_volunteers['Agg_Metric'] == 'Repeat_Volunteers'].empty else 0
                
                active_volunteers = total_vols - repeat_vols if total_vols >= repeat_vols else 0
                
                engagement_dist = pd.DataFrame({
                    'Engagement Level': ['One-time Volunteers', 'Repeat Volunteers'],
                    'Count': [active_volunteers, repeat_vols],
                    'Percentage': [((active_volunteers/total_vols)*100) if total_vols > 0 else 0, 
                                ((repeat_vols/total_vols)*100) if total_vols > 0 else 0]
                })
                
                fig_retention = px.pie(
                    engagement_dist, 
                    values='Count', 
                    names='Engagement Level',
                    title="🎯 Volunteer Engagement Distribution",
                    color_discrete_map={'One-time Volunteers': '#ff7f7f', 'Repeat Volunteers': '#7fbf7f'}
                )
                st.plotly_chart(fig_retention, use_container_width=True)
            
            # Volunteer retention metrics below charts
            st.subheader("🔄 Volunteer Retention & Engagement")
            
            col_a, col_b, col_c = st.columns(3)
            
            total_engagements = latest_volunteers[latest_volunteers['Agg_Metric'] == 'Total_Outreach_Engs_Volunteers']['Agg_Value'].iloc[0] if not latest_volunteers[latest_volunteers['Agg_Metric'] == 'Total_Outreach_Engs_Volunteers'].empty else 0
            
            with col_a:
                retention_rate = (repeat_vols / total_vols * 100) if total_vols > 0 else 0
                st.metric("Retention Rate", f"{retention_rate:.1f}%", help="Percentage of volunteers with ≥2 engagements")
            
            with col_b:
                avg_engagements = (total_engagements / total_vols) if total_vols > 0 else 0
                st.metric("Avg Engagements per Volunteer", f"{avg_engagements:.1f}", help="Average outreach engagements per volunteer")
            
            with col_c:
                st.metric("One-time Volunteers", active_volunteers, help="Volunteers with only 1 engagement")
        
        # ========== ROW 2: AWARENESS METRICS ==========
        st.header("📱 Awareness Metrics")
        
        # Social media followers
        social_followers = df_p1_filtered[df_p1_filtered['Agg_Metric'].str.contains('Followers', na=False)]
        if not social_followers.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Extract platform name from metric
                social_followers['Platform'] = social_followers['Agg_Metric'].str.replace('Total_', '').str.replace('_Followers', '')
                fig_social = px.pie(
                    social_followers.groupby('Platform')['Agg_Value'].mean().reset_index(),
                    values='Agg_Value', names='Platform',
                    title="📱 Social Media Followers Distribution"
                )
                st.plotly_chart(fig_social, use_container_width=True)
            
            with col2:
                # Social media followers bar chart for better comparison
                fig_social_bar = px.bar(
                    social_followers.groupby('Platform')['Agg_Value'].mean().reset_index(),
                    x='Platform', y='Agg_Value',
                    title="📊 Followers by Platform",
                    color='Platform'
                )
                fig_social_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_social_bar, use_container_width=True)
            
            # Awareness metrics summary
            st.subheader("📈 Awareness Summary")
            
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                total_followers = social_followers['Agg_Value'].sum()
                st.metric("Total Social Followers", f"{total_followers:,}")
            
            with col_b:
                visits = latest_data[latest_data['Agg_Metric'] == 'Total_Visits_SignUps_Organic']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_Visits_SignUps_Organic'].empty else 0

                st.metric("Website Visits", f"{visits:,}", help="Visits to sign-up page (awareness driving action)")

            

            with col_c:
                platform_count = len(social_followers['Platform'].unique())
                st.metric("Active Platforms", platform_count)
            
            with col_d:

                # Calculate reach-to-visit rate (visits per follower)

                reach_to_visit_rate = (visits / total_followers * 100) if total_followers > 0 else 0

                st.metric("Reach-to-Visit Rate", f"{reach_to_visit_rate:.1f}%", help="Website visits per social follower")
        
        # ========== ROW 3: ENGAGEMENT METRICS ==========
        st.header("🎯 Engagement Analysis")

        engagement_data = df_p1_filtered[df_p1_filtered['Metric_Category'] == 'Engagement']
        if not engagement_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Engagement by platform
                engagement_platform = engagement_data[engagement_data['Agg_Metric'].str.contains('Engagements', na=False)]
                if not engagement_platform.empty:
                    engagement_platform['Platform'] = engagement_platform['Agg_Metric'].str.replace('Total_', '').str.replace('_Engagements', '')
                    fig_eng = px.bar(
                        engagement_platform.groupby('Platform')['Agg_Value'].mean().reset_index(),
                        x='Platform', y='Agg_Value',
                        title="📊 Engagement by Platform",
                        color='Platform'
                    )
                    st.plotly_chart(fig_eng, use_container_width=True)
            
            with col2:
                # Conversion funnel (visits to sign-ups)
                visits = latest_data[latest_data['Agg_Metric'] == 'Total_Visits_SignUps_Organic']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_Visits_SignUps_Organic'].empty else 0
                signups = latest_data[latest_data['Agg_Metric'] == 'Total_Actual_SignUps_Organic']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_Actual_SignUps_Organic'].empty else 0
                
                if visits > 0:
                    # Simple funnel visualization
                    fig_funnel = go.Figure(go.Funnel(
                        y=["Website Visits", "Sign-ups"],
                        x=[visits, signups],
                        textinfo="value+percent initial"
                    ))
                    fig_funnel.update_layout(title="🔄 Conversion Funnel")
                    st.plotly_chart(fig_funnel, use_container_width=True)
            
            # Engagement metrics summary
            st.subheader("📊 Engagement Summary")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                conversion_rate = (signups / visits * 100) if visits > 0 else 0
                st.metric("Conversion Rate (Visits → Sign-ups)", f"{conversion_rate:.1f}%")
            
            with col_b:
                total_engagements = engagement_platform['Agg_Value'].sum() if not engagement_platform.empty else 0
                st.metric("Total Platform Engagements", f"{total_engagements:,}")
            
            with col_c:
                # Engagement rate (total engagements / total followers)
                total_followers = latest_data[latest_data['Agg_Metric'].str.contains('Followers', na=False)]['Agg_Value'].sum()
                engagement_rate = (total_engagements / total_followers * 100) if total_followers > 0 else 0
                st.metric("Overall Engagement Rate", f"{engagement_rate:.1f}%", help="Total engagements / Total followers")

    with tab2:
        # Time series analysis
        st.subheader("📈 Metrics Over Time")
        
        # Select metric for time series
        available_metrics = df_p1_filtered['Agg_Metric'].unique()
        metric_mapping = {clean_metric_name(metric): metric for metric in available_metrics}
        clean_metric_names = list(metric_mapping.keys())
        
        selected_clean_metric = st.selectbox("Select Metric for Time Series", clean_metric_names)
        selected_metric = metric_mapping[selected_clean_metric]

        metric_data = df_p1_filtered[df_p1_filtered['Agg_Metric'] == selected_metric]
        if not metric_data.empty:
            fig_ts = px.line(
                metric_data, x='Date', y='Agg_Value',
                title=f"{selected_clean_metric} Over Time",
                markers=True
            )
            fig_ts.update_layout(
                xaxis_title="Date",
                yaxis_title="Value"
            )
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No data for this metric.")

    with tab3:
        # Detailed metrics table
        st.subheader("🔍 Detailed Metrics")
        
        # Create a pivot table for better readability
        pivot_data = df_p1_filtered.pivot_table(
            values='Agg_Value', 
            index='Agg_Metric', 
            columns='Date', 
            aggfunc='first'
        ).reset_index()
        
        st.dataframe(pivot_data, use_container_width=True)

# Page 2
elif page == "2. Empower those experiencing homelessness":
    st.header("🏠 Empower those experiencing homelessness")
    # st.markdown("### Tracking progress toward housing stability, financial independence, and wellbeing")
    
    df_p2 = df[df["Pillar"] == 2].copy()

    if df_p2.empty:
        st.warning("No data available for this pillar yet.")
        st.stop()

    df_p2["Date"] = pd.to_datetime(df_p2["Date"], dayfirst=True)

    # Filters - Page 2 specific
    st.sidebar.subheader("Filters (Page 2)")
    min_date, max_date = df_p2["Month"].min(), df_p2["Month"].max()
    
    # Handle case where we might have only one date
    if len(df_p2["Month"].unique()) == 1:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p2_date")
    else:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p2_date")
    
    # Ensure we have a range
    if len(selected_range) == 1:
        selected_range = [selected_range[0], selected_range[0]]
    
    # Time Period Filter (3-month vs 6-month outcomes)
    time_period = st.sidebar.selectbox(
        "📅 Outcome Time Period",
        ["3-month", "6-month", "Both"],
        index=2
    )
    
    # Demographic Filters (for future use when disaggregated data is available)
    st.sidebar.subheader("🎯 Focus Areas")
    
    # Housing Type Focus
    housing_focus = st.sidebar.multiselect(
        "🏠 Housing Types",
        ["Share House/Own Home", "Family/Friends", "Social Housing", "Crisis/Emergency", "Without Housing"],
        default=["Share House/Own Home", "Family/Friends", "Social Housing", "Crisis/Emergency", "Without Housing"]
    )
    
    # Outcome Categories
    outcome_categories = st.sidebar.multiselect(
        "📊 Outcome Categories",
        ["Housing Stability", "Financial Independence", "Safety & Wellbeing", "Housing Retention"],
        default=["Housing Stability", "Financial Independence", "Safety & Wellbeing", "Housing Retention"]
    )

    # Apply filters
    df_p2_filtered = df_p2[
        (df_p2["Month"] >= pd.to_datetime(selected_range[0])) &
        (df_p2["Month"] <= pd.to_datetime(selected_range[1]))
    ]

    # Filter by time period
    if time_period == "3-month":
        df_p2_filtered = df_p2_filtered[df_p2_filtered['Agg_Metric'].str.contains('3mth')]
    elif time_period == "6-month":
        df_p2_filtered = df_p2_filtered[df_p2_filtered['Agg_Metric'].str.contains('6mth')]

    # Get latest data for metrics
    latest_date = df_p2_filtered['Date'].max()
    latest_data_p2 = df_p2_filtered[df_p2_filtered['Date'] == latest_date]
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Housing Stability - Same Property 6 months
        same_property_6m = latest_data_p2[latest_data_p2['Agg_Metric'] == '%_Still_In_Same_Property_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_Still_In_Same_Property_6mth'].empty else 0
        same_property_3m = latest_data_p2[latest_data_p2['Agg_Metric'] == '%_Still_In_Same_Property_3mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_Still_In_Same_Property_3mth'].empty else 0
        delta_same_property = same_property_6m - same_property_3m
        st.metric(
            "Housing Retention (6m)", 
            f"{same_property_6m:.0%}" if same_property_6m <= 1 else f"{same_property_6m:.0f}%",
            delta=f"{delta_same_property:+.0f}pp from 3m" if delta_same_property != 0 else None,
            help="Percentage still in same property after 6 months"
        )

    with col2:
        # Stable Housing (Share House + Own Home)
        stable_6m = latest_data_p2[latest_data_p2['Agg_Metric'] == '%_In_Share_House_or_Own_Home_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_In_Share_House_or_Own_Home_6mth'].empty else 0
        stable_3m = latest_data_p2[latest_data_p2['Agg_Metric'] == '%_In_Share_House_or_Own_Home_3mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_In_Share_House_or_Own_Home_3mth'].empty else 0
        delta_stable = stable_6m - stable_3m
        st.metric(
            "Stable Housing (6m)", 
            f"{stable_6m:.0f}%",
            delta=f"{delta_stable:+.0f}pp from 3m" if delta_stable != 0 else None,
            help="Percentage in share house or own home"
        )

    with col3:
        # Financial Independence (Can pay rent unaided)
        fin_indep_6m = latest_data_p2[latest_data_p2['Agg_Metric'] == '%_Can_Pay_Rent_Unaided_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_Can_Pay_Rent_Unaided_6mth'].empty else 0
        fin_indep_3m = latest_data_p2[latest_data_p2['Agg_Metric'] == '%_Can_Pay_Rent_Unaided_3mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_Can_Pay_Rent_Unaided_3mth'].empty else 0
        delta_fin_indep = fin_indep_6m - fin_indep_3m
        st.metric(
            "Financial Independence", 
            f"{fin_indep_6m:.0f}%",
            delta=f"{delta_fin_indep:+.0f}pp from 3m" if delta_fin_indep != 0 else None,
            help="Can pay rent without assistance"
        )

    with col4:
        # Crisis Support Reduction (inverse of running out of rent money)
        crisis_reduced_6m = 100 - (latest_data_p2[latest_data_p2['Agg_Metric'] == '%_ran_out_of_rent_money_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_ran_out_of_rent_money_6mth'].empty else 0)
        crisis_reduced_3m = 100 - (latest_data_p2[latest_data_p2['Agg_Metric'] == '%_ran_out_of_rent_money_3mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_ran_out_of_rent_money_3mth'].empty else 0)
        delta_crisis = crisis_reduced_6m - crisis_reduced_3m
        st.metric(
            "Financial Stability", 
            f"{crisis_reduced_6m:.0f}%",
            delta=f"{delta_crisis:+.0f}pp improvement" if delta_crisis != 0 else None,
            help="Percentage NOT running out of rent money"
        )

    # ========== MAIN ANALYSIS TABS ==========
    st.header("📈 Detailed Impact Analysis")
    
    tab1, tab2, tab3 = st.tabs([
       "📊 Category Overview",
       "📈 Time Series",
       "🔍 Metric Details"
    ])
    
    with tab1:
        # ========== ROW 1: HOUSING STABILITY ==========
        st.subheader("🏠 Housing Stability & Progress")
        
        # Housing outcomes comparison (3m vs 6m)
        col1, col2 = st.columns(2)
        
        with col1:
            # Housing distribution at 6 months
            housing_metrics_6m = [
                ('%_In_Share_House_or_Own_Home_6mth', 'Share House/Own Home'),
                ('%_Living_With_Family_or_Friends_6mth', 'Family/Friends'),
                ('%_in_social_housing_6mth', 'Social Housing'),
                ('%_in_crisis_or_emergency_accomm_6mth', 'Crisis/Emergency'),
                ('%_without_housing_6mth', 'Without Housing')
            ]
            
            housing_data_6m = []
            for metric, label in housing_metrics_6m:
                value = latest_data_p2[latest_data_p2['Agg_Metric'] == metric]['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == metric].empty else 0
                housing_data_6m.append({'Housing Type': label, 'Percentage': value})
            
            housing_df_6m = pd.DataFrame(housing_data_6m)
            
            fig_housing_pie = px.pie(
                housing_df_6m, 
                values='Percentage', 
                names='Housing Type',
                title="🏠 Housing Distribution (6 months)",
                color_discrete_map={
                    'Share House/Own Home': '#2E8B57',  # Forest green
                    'Family/Friends': '#90EE90',        # Light green
                    'Social Housing': '#FFA500',        # Orange
                    'Crisis/Emergency': '#FF6347',      # Tomato
                    'Without Housing': '#DC143C'        # Crimson
                }
            )
            st.plotly_chart(fig_housing_pie, use_container_width=True)
        
        with col2:
            # Housing progression (3m to 6m comparison)
            housing_metrics_comparison = [
                ('Share House/Own Home', '%_In_Share_House_or_Own_Home_3mth', '%_In_Share_House_or_Own_Home_6mth'),
                ('Family/Friends', '%_Living_With_Family_or_Friends_3mth', '%_Living_With_Family_or_Friends_6mth'),
                ('Social Housing', '%_in_social_housing_3mth', '%_in_social_housing_6mth'),
                ('Crisis/Emergency', '%_in_crisis_or_emergency_accomm_3mth', '%_in_crisis_or_emergency_accomm_6mth'),
                ('Without Housing', '%_without_housing_3mth', '%_without_housing_6mth')
            ]
            
            comparison_data = []
            for housing_type, metric_3m, metric_6m in housing_metrics_comparison:
                val_3m = latest_data_p2[latest_data_p2['Agg_Metric'] == metric_3m]['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == metric_3m].empty else 0
                val_6m = latest_data_p2[latest_data_p2['Agg_Metric'] == metric_6m]['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == metric_6m].empty else 0
                comparison_data.append({'Housing Type': housing_type, 'Period': '3 months', 'Percentage': val_3m})
                comparison_data.append({'Housing Type': housing_type, 'Period': '6 months', 'Percentage': val_6m})
            
            comparison_df = pd.DataFrame(comparison_data)
            
            fig_housing_comparison = px.bar(
                comparison_df,
                x='Housing Type',
                y='Percentage',
                color='Period',
                barmode='group',
                title="📈 Housing Progress: 3m vs 6m Outcomes",
                color_discrete_map={'3 months': '#87CEEB', '6 months': '#4682B4'}
            )
            fig_housing_comparison.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_housing_comparison, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            home_safety_6m = latest_data_p2[latest_data_p2['Agg_Metric'] == 'Avg_Home_Safety_Score_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == 'Avg_Home_Safety_Score_6mth'].empty else 0
            home_safety_3m = latest_data_p2[latest_data_p2['Agg_Metric'] == 'Avg_Home_Safety_Score_3mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == 'Avg_Home_Safety_Score_3mth'].empty else 0
            st.metric(
                "Home Safety Score", 
                f"{home_safety_6m:.1f}/5",
                delta=f"{home_safety_6m - home_safety_3m:+.1f} from 3m" if home_safety_3m != 0 else None
            )
        
        with col2:
            area_safety_6m = latest_data_p2[latest_data_p2['Agg_Metric'] == 'Avg_Area_Safety_Score_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == 'Avg_Area_Safety_Score_6mth'].empty else 0
            area_safety_3m = latest_data_p2[latest_data_p2['Agg_Metric'] == 'Avg_Area_Safety_Score_3mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == 'Avg_Area_Safety_Score_3mth'].empty else 0
            st.metric(
                "Area Safety Score", 
                f"{area_safety_6m:.1f}/5",
                delta=f"{area_safety_6m - area_safety_3m:+.1f} from 3m" if area_safety_3m != 0 else None
            )
        
        with col3:
            housing_indep_6m = latest_data_p2[latest_data_p2['Agg_Metric'] == 'Avg_housing_independence_score_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == 'Avg_housing_independence_score_6mth'].empty else 0
            st.metric(
                "Housing Independence", 
                f"{housing_indep_6m:.1f}/5",
                help="Self-reported housing independence score"
            )

        # ========== ROW 2: FINANCIAL STABILITY ==========
        st.subheader("💰 Financial Stability & Independence")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Financial challenges - what people struggle to pay for
            financial_challenges = [
                ('%_unable_pay_utility_expenses_6mth', 'Utilities'),
                ('%_unable_pay_car_expenses_6mth', 'Car Expenses'),
                ('%_unable_pay_food_expenses_6mth', 'Food'),
                ('%_unable_pay_debts_6mth', 'Debts'),
                ('%_ran_out_of_rent_money_6mth', 'Rent')
            ]
            
            challenges_data = []
            for metric, expense_type in financial_challenges:
                value = latest_data_p2[latest_data_p2['Agg_Metric'] == metric]['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == metric].empty else 0
                challenges_data.append({'Expense Type': expense_type, 'Unable to Pay (%)': value})
            
            challenges_df = pd.DataFrame(challenges_data)
            
            fig_challenges = px.bar(
                challenges_df,
                x='Unable to Pay (%)',
                y='Expense Type',
                orientation='h',
                title="💸 Financial Challenges (6 months)",
                color='Unable to Pay (%)',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_challenges, use_container_width=True)
        
        with col2:
            # Financial stability improvement - Crisis support usage
            crisis_support_data = []
            
            # Current crisis support usage
            crisis_6m = latest_data_p2[latest_data_p2['Agg_Metric'] == '%_ran_out_of_rent_money_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_ran_out_of_rent_money_6mth'].empty else 0
            crisis_3m = latest_data_p2[latest_data_p2['Agg_Metric'] == '%_ran_out_of_rent_money_3mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_ran_out_of_rent_money_3mth'].empty else 0
            
            # Create pie chart for crisis support reliance
            crisis_support_data = [
                {'Category': 'Crisis Support Used', 'Percentage': crisis_6m},
                {'Category': 'Self-Sufficient', 'Percentage': 100 - crisis_6m}
            ]
            
            crisis_df = pd.DataFrame(crisis_support_data)
            
            fig_crisis_pie = px.pie(
                crisis_df,
                values='Percentage',
                names='Category',
                title="🆘 Crisis Support Reliance (6 months)",
                color_discrete_map={
                    'Crisis Support Used': '#FF6B6B',
                    'Self-Sufficient': '#4ECDC4'
                }
            )
            st.plotly_chart(fig_crisis_pie, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Rent payment capacity progression
            rent_payment_data = []
            rent_metrics = [
                ('%_paid_1_3_weeks_rent_3mth', '%_paid_1_3_weeks_rent_6mth', '1-3 weeks'),
                ('%_paid_1_month_rent_3mth', '%_paid_1_month_rent_6mth', '1 month'),
                ('%_paid_most_2_month_rent_3mth', '%_paid_most_2_month_rent_6mth', '1-2 months')
            ]
            
            for metric_3m, metric_6m, period in rent_metrics:
                val_3m = latest_data_p2[latest_data_p2['Agg_Metric'] == metric_3m]['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == metric_3m].empty else 0
                val_6m = latest_data_p2[latest_data_p2['Agg_Metric'] == metric_6m]['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == metric_6m].empty else 0
                rent_payment_data.append({'Rent Period': period, 'Timeline': '3 months', 'Percentage': val_3m})
                rent_payment_data.append({'Rent Period': period, 'Timeline': '6 months', 'Percentage': val_6m})
            
            rent_df = pd.DataFrame(rent_payment_data)
            
            fig_rent = px.bar(
                rent_df,
                x='Rent Period',
                y='Percentage',
                color='Timeline',
                barmode='group',
                title="🏠 Rent Payment Capacity Progress",
                color_discrete_map={'3 months': '#FFB6C1', '6 months': '#FF69B4'}
            )
            st.plotly_chart(fig_rent, use_container_width=True)
        
        with col2:
            # Spending priorities - Long-term vs Crisis needs
            spending_data = []
            
            # Long-term needs (can pay rent in advance)
            long_term_rent = latest_data_p2[latest_data_p2['Agg_Metric'] == '%_paid_most_2_month_rent_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_paid_most_2_month_rent_6mth'].empty else 0
            
            # Crisis needs (running out of rent money)
            crisis_needs = latest_data_p2[latest_data_p2['Agg_Metric'] == '%_ran_out_of_rent_money_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_ran_out_of_rent_money_6mth'].empty else 0
            
            # Medium-term stability (can pay current month)
            medium_term = 100 - long_term_rent - crisis_needs
            
            spending_data = [
                {'Category': 'Long-term Security (1-2 months rent)', 'Percentage': long_term_rent},
                {'Category': 'Medium-term Stability', 'Percentage': medium_term},
                {'Category': 'Crisis Mode (Running out)', 'Percentage': crisis_needs}
            ]
            
            spending_df = pd.DataFrame(spending_data)
            
            fig_spending = px.pie(
                spending_df,
                values='Percentage',
                names='Category',
                title="💰 Financial Capacity Categories (6 months)",
                color_discrete_map={
                    'Long-term Security (1-2 months rent)': '#2E8B57',
                    'Medium-term Stability': '#FFA500',
                    'Crisis Mode (Running out)': '#DC143C'
                }
            )
            st.plotly_chart(fig_spending, use_container_width=True)
        
        # ========== ROW 3: SAFETY & WELLBEING ==========
        st.subheader("🛡️ Safety, Wellbeing & Confidence")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Safety scores radar chart
            safety_data = []
            safety_metrics = [
                ('Home Safety', 'Avg_Home_Safety_Score_6mth', 'Avg_Home_Safety_Score_3mth'),
                ('Area Safety', 'Avg_Area_Safety_Score_6mth', 'Avg_Area_Safety_Score_3mth'),
                ('Home Care', 'Avg_home_care_score_6mth', 'Avg_home_care_score_3mth'),
                ('Financial Sufficiency', 'Avg_fin_suff_Score_6mth', 'Avg_fin_suff_score_3mth'),
                ('Housing Independence', 'Avg_housing_independence_score_6mth', None)
            ]
            
            for dimension, metric_6m, metric_3m in safety_metrics:
                val_6m = latest_data_p2[latest_data_p2['Agg_Metric'] == metric_6m]['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == metric_6m].empty else 0
                val_3m = latest_data_p2[latest_data_p2['Agg_Metric'] == metric_3m]['Agg_Value'].iloc[0] if metric_3m and not latest_data_p2[latest_data_p2['Agg_Metric'] == metric_3m].empty else 0
                
                if val_6m > 0:
                    safety_data.append({'Dimension': dimension, 'Period': '6 months', 'Score': val_6m})
                if val_3m > 0:
                    safety_data.append({'Dimension': dimension, 'Period': '3 months', 'Score': val_3m})
            
            safety_df = pd.DataFrame(safety_data)
            
            if not safety_df.empty:
                fig_radar = px.line_polar(
                    safety_df,
                    r='Score',
                    theta='Dimension',
                    color='Period',
                    line_close=True,
                    title="🛡️ Wellbeing Dimensions (Score out of 5)",
                    range_r=[0, 5]
                )
                st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # Confidence and self-esteem changes
            st.markdown("#### 📈 Self-Reported Confidence & Control")
            
            # Create confidence score changes bar chart
            confidence_metrics = [
                ('Home Safety', 'Avg_Home_Safety_Score_6mth', 'Avg_Home_Safety_Score_3mth'),
                ('Area Safety', 'Avg_Area_Safety_Score_6mth', 'Avg_Area_Safety_Score_3mth'),
                ('Financial Sufficiency', 'Avg_fin_suff_Score_6mth', 'Avg_fin_suff_score_3mth'),
                ('Housing Independence', 'Avg_housing_independence_score_6mth', None)
            ]
            
            confidence_data = []
            for dimension, metric_6m, metric_3m in confidence_metrics:
                val_6m = latest_data_p2[latest_data_p2['Agg_Metric'] == metric_6m]['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == metric_6m].empty else 0
                val_3m = latest_data_p2[latest_data_p2['Agg_Metric'] == metric_3m]['Agg_Value'].iloc[0] if metric_3m and not latest_data_p2[latest_data_p2['Agg_Metric'] == metric_3m].empty else 0
                change = val_6m - val_3m if val_3m > 0 else 0
                
                confidence_data.append({
                    'Dimension': dimension,
                    'Score Change': change,
                    'Direction': 'Improved' if change > 0 else 'Declined' if change < 0 else 'Stable'
                })
            
            confidence_df = pd.DataFrame(confidence_data)
            
            if not confidence_df.empty:
                fig_confidence = px.bar(
                    confidence_df,
                    x='Score Change',
                    y='Dimension',
                    orientation='h',
                    color='Direction',
                    title="🎯 Confidence Score Changes (6m vs 3m)",
                    color_discrete_map={
                        'Improved': '#4ECDC4',
                        'Declined': '#FF6B6B',
                        'Stable': '#95A5A6'
                    }
                )
                st.plotly_chart(fig_confidence, use_container_width=True)

    # ========== ROW 4: GOALS & MILESTONES ==========
        st.subheader("🎯 Goals & Milestones Achievement")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Milestones funnel - Housing progression
            st.markdown("#### 🏠 Housing Milestone Progression")
            # Create funnel data for housing milestones
            housing_milestones = [
                ('Initial Support', 100),
                ('Stable Housing (3m)', latest_data_p2[latest_data_p2['Agg_Metric'] == '%_In_Share_House_or_Own_Home_3mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_In_Share_House_or_Own_Home_3mth'].empty else 0),
                ('Stable Housing (6m)', latest_data_p2[latest_data_p2['Agg_Metric'] == '%_In_Share_House_or_Own_Home_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_In_Share_House_or_Own_Home_6mth'].empty else 0),
                ('Housing Retention', latest_data_p2[latest_data_p2['Agg_Metric'] == '%_Still_In_Same_Property_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == '%_Still_In_Same_Property_6mth'].empty else 0)
            ]
            funnel_df = pd.DataFrame(housing_milestones, columns=['Stage', 'Percentage'])
            import plotly.graph_objects as go
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_df['Stage'],
                x=funnel_df['Percentage'],
                textinfo='value+percent initial',
                marker={"color": ['#2E8B57', '#87CEEB', '#4682B4', '#FF6347']}
            ))
            fig_funnel.update_layout(title_text="🎯 Housing Milestones Funnel")
            st.plotly_chart(fig_funnel, use_container_width=True)
        
        with col2:
            # Bar chart by demographic group (e.g., Gender)
            st.markdown("#### Progress by Demographic: Gender")
            gender_metrics = [
                ('%_Stable_Housing_Female_6mth', 'Female'),
                ('%_Stable_Housing_Male_6mth', 'Male'),
                ('%_Stable_Housing_Other_6mth', 'Other')
            ]
            demographic_data = []
            for metric, group in gender_metrics:
                val = latest_data_p2[latest_data_p2['Agg_Metric'] == metric]['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == metric].empty else 0
                demographic_data.append({'Gender': group, 'Stable Housing %': val})
            demographic_df = pd.DataFrame(demographic_data)
            fig_gender_bar = px.bar(
                demographic_df,
                x='Gender',
                y='Stable Housing %',
                color='Gender',
                title='🏳️‍🌈 Stable Housing by Gender (6 months)',
                color_discrete_map={'Female': '#FF69B4', 'Male': '#4682B4', 'Other': '#9B59B6'}
            )
            st.plotly_chart(fig_gender_bar, use_container_width=True)
        
        # # Scatter plot by goal type
        # st.markdown("#### 🎯 Goals Completion by Type")
        # goal_type_data = []
        # goal_types = ['Housing', 'Employment', 'ID', 'Health']
        # for goal in goal_types:
        #     val = latest_data_p2[latest_data_p2['Agg_Metric'] == f'%_Goals_Completed_{goal}_6mth']['Agg_Value'].iloc[0] if not latest_data_p2[latest_data_p2['Agg_Metric'] == f'%_Goals_Completed_{goal}_6mth'].empty else 0
        #     goal_type_data.append({'Goal Type': goal, 'Completion %': val})
        # goal_df = pd.DataFrame(goal_type_data)
        # fig_goal_scatter = px.scatter(
        #     goal_df,
        #     x='Goal Type',
        #     y='Completion %',
        #     size='Completion %',
        #     color='Goal Type',
        #     title='🎯 Goals Completion by Type',
        #     size_max=60
        # )
        # st.plotly_chart(fig_goal_scatter, use_container_width=True)
    
    with tab2:
        # Time series analysis
        st.subheader("📈 Metrics Over Time")
        
        # Select metric for time series
        # Time series analysis
        st.subheader("📈 Metrics Over Time")
        
        # Select metric for time series
        available_metrics = df_p2_filtered['Agg_Metric'].unique()
        metric_mapping = {clean_metric_name(metric): metric for metric in available_metrics}
        clean_metric_names = list(metric_mapping.keys())
        
        selected_clean_metric = st.selectbox("Select Metric for Time Series", clean_metric_names)
        selected_metric = metric_mapping[selected_clean_metric]

        metric_data = df_p2_filtered[df_p2_filtered['Agg_Metric'] == selected_metric]
        if not metric_data.empty:
            fig_ts = px.line(
                metric_data, x='Date', y='Agg_Value',
                title=f"{selected_clean_metric} Over Time",
                markers=True
            )
            fig_ts.update_layout(
                xaxis_title="Date",
                yaxis_title="Value"
            )
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No data for this metric.")

    with tab3:
        # Detailed metrics table
        st.subheader("🔍 Detailed Metrics")
        
        # Create a pivot table for better readability
        pivot_data = df_p2_filtered.pivot_table(
            values='Agg_Value', 
            index='Agg_Metric', 
            columns='Date', 
            aggfunc='first'
        ).reset_index()
        
        st.dataframe(pivot_data, use_container_width=True)

# Page 3
elif page == "3. Promote direct participation in the solution":
    st.header("🤝 Promote Direct Participation in the Solution")
    df_p3 = df[df["Pillar"] == 3].copy()
    df_p3["Date"] = pd.to_datetime(df_p3["Date"], dayfirst=True)

    # ==== FILTERS ====
    st.sidebar.subheader("Filters (Page 3)")
    min_date, max_date = df_p3["Date"].min(), df_p3["Date"].max()
    
    # Handle single date selection gracefully
    if len(df_p3["Date"].unique()) == 1:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p3_date")
    else:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p3_date")
    if len(selected_range) == 1:
        selected_range = [selected_range[0], selected_range[0]]

    categories = df_p3["Metric_Category"].dropna().unique().tolist()
    selected_categories = st.sidebar.multiselect(
        "📂 Metric Category",
        categories,
        default=categories
    )

    # Apply filters
    df_p3_filtered = df_p3[
        (df_p3["Date"] >= pd.to_datetime(selected_range[0])) &
        (df_p3["Date"] <= pd.to_datetime(selected_range[1])) &
        (df_p3["Metric_Category"].isin(selected_categories))
    ]

    # ==== KPI CARDS ====
    col1, col2, col3, col4 = st.columns(4)
    latest_date = df_p3_filtered["Date"].max()
    latest_data = df_p3_filtered[df_p3_filtered["Date"] == latest_date]

    with col1:
        total_volunteers = latest_data[latest_data['Agg_Metric'] == 'Total_Volunteers']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_Volunteers'].empty else 0
        st.metric("Total Volunteers", total_volunteers)

    with col2:
        repeat_volunteers = latest_data[latest_data['Agg_Metric'] == 'Repeat_Volunteers']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Repeat_Volunteers'].empty else 0
        st.metric("Repeat Volunteers", repeat_volunteers)

    with col3:
        outreach_engs = latest_data[latest_data['Agg_Metric'] == 'Total_Outreach_Engs_Volunteers']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_Outreach_Engs_Volunteers'].empty else 0
        st.metric("Outreach Engagements", outreach_engs)

    with col4:
        part_led = latest_data[latest_data['Agg_Metric'] == 'Total_Participant_led_ Engs']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_Participant_led_ Engs'].empty else 0
        st.metric("Participant-Led Initiatives", part_led)

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        partner_collabs = latest_data[latest_data['Agg_Metric'] == 'Total_partner_events_collabs']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_partner_events_collabs'].empty else 0
        st.metric("Partner Collaborations", partner_collabs)
    
    with col6:
        slt_meetings = latest_data[latest_data['Agg_Metric'] == 'Total_SLT_meetings_participants']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_SLT_meetings_participants'].empty else 0
        st.metric("SLT mtgs w/ lived exp.", slt_meetings)

    with col7:
        int_roles = latest_data[latest_data['Agg_Metric'] == 'Total_participants_int_roles']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_participants_int_roles'].empty else 0
        st.metric("Participants Internal Roles", int_roles)

    # ---- Tabs ----
    tab1, tab2, tab3 = st.tabs(["📂 Category Overview", "📈 Time Series", "📋 Metric Details"])

    with tab1:
        st.subheader("📂 Participation & Collaboration Overview")
        # Volunteer Engagement bar chart
        volunteer_metrics = ["Total_Volunteers", "Repeat_Volunteers", "Total_Outreach_Engs_Volunteers"]
        overview_data = df_p3_filtered[df_p3_filtered["Agg_Metric"].isin(volunteer_metrics)]

        if not overview_data.empty:
            # Calculate period-specific metrics by taking the sum for the filtered period
            period_metrics = overview_data.groupby('Agg_Metric')['Agg_Value'].sum().reset_index()
            
            fig = px.bar(
                period_metrics, 
                x='Agg_Metric', 
                y='Agg_Value',
                text='Agg_Value',
                title=f"Volunteer Engagement Metrics"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No volunteer engagement data available for selected period.")

        # Participant-Led Initiatives
        pli_data = df_p3_filtered[df_p3_filtered["Agg_Metric"] == "Total_Participant_led_ Engs"]
        if not pli_data.empty:
            fig = px.bar(pli_data, x="Date", y="Agg_Value",
                         title="Participant-Led Initiatives")
            st.plotly_chart(fig, use_container_width=True)
        
        # Partner Collaborations
        collab_data = df_p3_filtered[df_p3_filtered["Agg_Metric"] == "Total_partner_events_collabs"]
        if not collab_data.empty:
            fig = px.bar(collab_data, x="Date", y="Agg_Value",
                         title="Partner Collaborations")
            st.plotly_chart(fig, use_container_width=True)

        # Pie Chart: SLT Meetings with/without lived experience
        slt_meetings_part = df_p3_filtered[df_p3_filtered["Agg_Metric"] == "Total_SLT_meetings_participants"]["Agg_Value"].sum()
        slt_meetings_total = slt_meetings_part  # If only this metric, all meetings had lived experience
        if slt_meetings_part>0:
            pie_data = pd.DataFrame({
                "Category": ["With lived experience"],
                "Count": [slt_meetings_part]
            })
            fig = px.pie(pie_data, names="Category", values="Count", title="SLT Meetings with Lived Experience Present")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No SLT meeting data for lived experience inclusion.")
        
    with tab2:
        # Time series analysis
        st.subheader("📈 Metrics Over Time")
        
        # Select metric for time series
        available_metrics = df_p3_filtered['Agg_Metric'].unique()
        metric_mapping = {clean_metric_name(metric): metric for metric in available_metrics}
        clean_metric_names = list(metric_mapping.keys())
        
        selected_clean_metric = st.selectbox("Select Metric for Time Series", clean_metric_names)
        selected_metric = metric_mapping[selected_clean_metric]

        metric_data = df_p3_filtered[df_p3_filtered['Agg_Metric'] == selected_metric]
        if not metric_data.empty:
            fig_ts = px.line(
                metric_data, x='Date', y='Agg_Value',
                title=f"{selected_clean_metric} Over Time",
                markers=True
            )
            fig_ts.update_layout(
                xaxis_title="Date",
                yaxis_title="Value"
            )
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No data for this metric.")

    with tab3:
        # Detailed metrics table
        st.subheader("🔍 Detailed Metrics")
        
        # Create a pivot table for better readability
        pivot_data = df_p3_filtered.pivot_table(
            values='Agg_Value', 
            index='Agg_Metric', 
            columns='Date', 
            aggfunc='first'
        ).reset_index()
        
        st.dataframe(pivot_data, use_container_width=True)
        
# Page 4
elif page == "4. Expanded outreach opportunities":
    st.header("🌐 Expanded Outreach Opportunities")
    df_p4 = df[df["Pillar"] == 4].copy()
    df_p4["Date"] = pd.to_datetime(df_p4["Date"], dayfirst=True)

    # ==== SIDEBAR FILTERS ====
    st.sidebar.subheader("Filters (Page 4)")
    min_date, max_date = df_p4["Date"].min(), df_p4["Date"].max()
    if len(df_p4["Date"].unique()) == 1:
        selected_range = st.sidebar.date_input(
            "Date Range", [min_date, max_date], key="p4_date")
    else:
        selected_range = st.sidebar.date_input(
            "Date Range", [min_date, max_date], key="p4_date")
    if len(selected_range) == 1:
        selected_range = [selected_range[0], selected_range[0]]

    categories = df_p4["Metric_Category"].dropna().unique().tolist()
    selected_categories = st.sidebar.multiselect(
        "📂 Metric Category",
        categories,
        default=categories
    )

    # Apply filters
    df_p4_filtered = df_p4[
        (df_p4["Date"] >= pd.to_datetime(selected_range[0])) &
        (df_p4["Date"] <= pd.to_datetime(selected_range[1])) &
        (df_p4["Metric_Category"].isin(selected_categories))
    ]

    # ==== KPI CARDS ====
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    latest_date = df_p4_filtered["Date"].max()
    latest_data = df_p4_filtered[df_p4_filtered["Date"] == latest_date]

    with col1:
        outreach_sessions = latest_data[latest_data['Agg_Metric'] == 'Total_outreach_Engs']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_outreach_Engs'].empty else 0
        st.metric("Outreach Sessions", outreach_sessions)

    with col2:
        unique_individuals = latest_data[latest_data['Agg_Metric'] == 'Total_outreach_individuals_unique']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_outreach_individuals_unique'].empty else 0
        st.metric("Unique Individuals Engaged", unique_individuals)

    with col3:
        geo_spread = latest_data[latest_data['Agg_Metric'] == 'Total_engs_postcode']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_engs_postcode'].empty else 0
        st.metric("Distinct Outreach Locations", geo_spread)

    with col4:
        avg_impact = latest_data[latest_data['Agg_Metric'] == 'Avg_eng_impact_score']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Avg_eng_impact_score'].empty else 0
        st.metric("Avg Impact Score", avg_impact)

    # ==== TABS ====
    tab1, tab2, tab3 = st.tabs(["📊 Category Overview", "📈 Time Series", "🔍 Metric Details"])

    # === OVERVIEW TAB ===
    with tab1:
        # st.header("📊 Category Overview")

        # 1. Outreach Metrics (bar chart for latest period)
        bar_metrics = [
            ("Total_outreach_Engs", "Outreach Sessions"),
            ("Total_outreach_individuals_unique", "Unique Individuals"),
            ("Total_engs_postcode", "Distinct Locations")
        ]
        vals = []
        for code, label in bar_metrics:
            v = latest_data[latest_data['Agg_Metric'] == code]['Agg_Value'].sum()
            vals.append({'Metric': label, 'Count': v})

        df_bar = pd.DataFrame(vals)
        fig_bar = px.bar(
            df_bar.sort_values("Count"),
            x="Count", y="Metric",
            orientation="h",
            text="Count",
            color="Metric",
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="Outreach Scale at a Glance"
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig_bar, use_container_width=True)

        # 2. Radar chart for quality/consistency
        radar_metrics = [
            ("Avg_eng_impact_score", "Avg Impact", "score"),
            ("%_eng_follow_up_req", "Follow-up Required (%)", "percentage"),
            ("%_eng_referral_sugg", "Referral Suggested (%)", "percentage"),
            ("%_eng_imm_supp_prov", "Immediate Support (%)", "percentage"),
            ("%_eng_na", "No Further Action (%)", "percentage"),
            ("%_eng_declined_withdrawn", "Declined/Withdrawn (%)", "percentage")
        ]

        radar_vals = []
        for code, label, metric_type in radar_metrics:
            raw_value = latest_data[latest_data['Agg_Metric'] == code]['Agg_Value'].sum()
            
            # Normalize based on metric type
            if metric_type == "score":
                # Assuming impact score is 0-5, normalize to 0-100
                max_impact_score = 5  # Adjust this based on your actual scale
                normalized_value = (raw_value / max_impact_score) * 100
                display_label = f"{label} ({raw_value:.1f}/5)"
            else:  # percentage
                normalized_value = raw_value
                display_label = f"{label} ({raw_value:.1f}%)"
            
            radar_vals.append({
                'Dimension': display_label, 
                'Score': normalized_value,
                'Raw_Value': raw_value
            })

        df_radar = pd.DataFrame(radar_vals)

        # Create radar chart with fixed 0-100 scale
        fig_radar_page4 = px.line_polar(
            df_radar, 
            r="Score", 
            theta="Dimension", 
            line_close=True,
            title="Quality & Consistency of Outreach (Normalized 0-100 Scale)",
            range_r=[0, 100]  # Fix scale to 0-100
        )

        fig_radar_page4.update_traces(fill='toself', fillcolor='rgba(135, 206, 235, 0.3)')

        # Improve readability
        fig_radar_page4.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickvals=[0, 25, 50, 75, 100],
                    ticktext=['0', '25', '50', '75', '100'],
                    gridcolor='lightgray'
                ),
                angularaxis=dict(
                    tickfont=dict(size=10)
                )
            ),
            font=dict(size=12),
            height=500
        )

        st.plotly_chart(fig_radar_page4, use_container_width=True, key="radar_page4_normalized")

        # 3. Positive feedback bar chart
        positive_keywords = ["Avg Impact", "Immediate Support", "Referral Suggested"]
        pos_feedback = df_radar[df_radar["Dimension"].str.contains('|'.join(positive_keywords), case=False, na=False)]

        fig_pos = px.bar(
            pos_feedback,
            x="Dimension", y="Score", color="Dimension",
            title="Positive Feedback Metrics",
            text="Score"
        )
        fig_pos.update_traces(textposition="outside")
        fig_pos.update_layout(showlegend=False)
        st.plotly_chart(fig_pos, use_container_width=True)

        # (If location data by lat/lon, add map here)

    # === TIME SERIES TAB ===
    with tab2:
        # Time series analysis
        st.subheader("📈 Metrics Over Time")
        
        # Select metric for time series
        available_metrics = df_p4_filtered['Agg_Metric'].unique()
        metric_mapping = {clean_metric_name(metric): metric for metric in available_metrics}
        clean_metric_names = list(metric_mapping.keys())
        
        selected_clean_metric = st.selectbox("Select Metric for Time Series", clean_metric_names)
        selected_metric = metric_mapping[selected_clean_metric]

        metric_data = df_p4_filtered[df_p4_filtered['Agg_Metric'] == selected_metric]
        if not metric_data.empty:
            fig_ts = px.line(
                metric_data, x='Date', y='Agg_Value',
                title=f"{selected_clean_metric} Over Time",
                markers=True
            )
            fig_ts.update_layout(
                xaxis_title="Date",
                yaxis_title="Value"
            )
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No data for this metric.")

    # === DETAIL TAB ===
    with tab3:
        st.header("🔍 Detailed Metrics")
        if not df_p4_filtered.empty:
            pivot_data = df_p4_filtered.pivot_table(
                values='Agg_Value',
                index='Agg_Metric',
                columns='Date',
                aggfunc='first'
            ).reset_index()
            st.dataframe(pivot_data, use_container_width=True)
        else:
            st.info("No records for selected filters.")
            
# Page 5
elif page == "5. Distribution of funds":
    st.header("💸 Distribution of Funds")
    
    df_p5 = df[df["Pillar"] == 5].copy()
    df_p5["Date"] = pd.to_datetime(df_p5["Date"], dayfirst=True)

    # ==== Filters ====
    st.sidebar.subheader("Filters (Page 5)")
    min_date, max_date = df_p5["Date"].min(), df_p5["Date"].max()
    if len(df_p5["Date"].unique()) == 1:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p5_date")
    else:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p5_date")
    if len(selected_range) == 1:
        selected_range = [selected_range[0], selected_range[0]]

    categories = df_p5["Metric_Category"].dropna().unique().tolist()
    selected_categories = st.sidebar.multiselect(
        "📂 Metric Category",
        categories,
        default=categories
    )

    # Apply filters
    df_p5_filtered = df_p5[
        (df_p5["Date"] >= pd.to_datetime(selected_range[0])) &
        (df_p5["Date"] <= pd.to_datetime(selected_range[1])) &
        (df_p5["Metric_Category"].isin(selected_categories))
    ]

    # ==== KPI CARDS ====
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    latest_date = df_p5_filtered["Date"].max()
    latest_data = df_p5_filtered[df_p5_filtered["Date"] == latest_date]

    with col1:
        n_funded = latest_data[latest_data['Agg_Metric'] == 'Total_unique_participants_received_funds']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_unique_participants_received_funds'].empty else 0
        st.metric("Participants Funded", int(n_funded))
    with col2:
        pct_funded = latest_data[latest_data['Agg_Metric'] == '%_unique_participants_received_funds']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == '%_unique_participants_received_funds'].empty else 0
        st.metric("% of Participants Funded", f"{pct_funded:.1f}%")
    with col3:
        bill_amount = latest_data[latest_data['Agg_Metric'] == 'Total_bill_amount_unique_participants']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_bill_amount_unique_participants'].empty else 0
        st.metric("Total Bill Amount (A$)", f"${bill_amount:,.0f}")
    with col4:
        avg_time_hour = latest_data[latest_data['Agg_Metric'] == 'Avg_time_to_received_funds_hours']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Avg_time_to_received_funds_hours'].empty else 0
        st.metric("Avg Time to Funds (hrs)", f"{avg_time_hour:.1f}")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        rent_ratio = latest_data[latest_data['Agg_Metric'] == 'Avg_rent_income_ratio']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Avg_rent_income_ratio'].empty else 0
        st.metric("Avg Rent/Income Ratio", f"{rent_ratio:.1f}%")
    with col6:
        needs_score = latest_data[latest_data['Agg_Metric'] == 'Avg_intake_needs_score']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Avg_intake_needs_score'].empty else 0
        st.metric("Avg Intake Needs Score", f"{needs_score:.1f}")
    with col7:
        sat_score = latest_data[latest_data['Agg_Metric'] == 'Avg_satisfaction_score_unique_participants']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Avg_satisfaction_score_unique_participants'].empty else 0
        st.metric("Satisfaction Score", f"{sat_score:.1f}/5")
    with col8:
        emerg_calls = latest_data[latest_data['Agg_Metric'] == 'Avg_emergency_callout_unique_participants']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Avg_emergency_callout_unique_participants'].empty else 0
        st.metric("Emergency Callouts", f"{emerg_calls:.1f}")

    # ==== TABS ====
    tab1, tab2, tab3 = st.tabs(["📊 Category Overview", "📈 Time Series", "🔍 Metric Details"])

    # ========== TAB 1: CATEGORY OVERVIEW ==========
    with tab1:
        st.header("📊 Overview: Funds Distribution & Equity")

        # --- 1. Recipients over time (Line Chart) ---
        metric_over_time = df_p5_filtered[df_p5_filtered['Agg_Metric'] == 'Total_unique_participants_received_funds']
        if not metric_over_time.empty:
            fig_line = px.line(
                metric_over_time,
                x="Date",
                y="Agg_Value",
                markers=True,
                title="Number of Funded Participants Over Time"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No data for funded participants over time.")

        # --- 2. Pie chart for spending categories (latest period) ---
        spending_codes = [
            ('%_use_of_funds_rent', 'Rent'),
            ('%_use_of_funds_food', 'Food'),
            ('%_use_of_funds_transport', 'Transport'),
            ('%_use_of_funds_utilities', 'Utilities'),
            ('%_use_of_funds_other', 'Other')
        ]
        spend_vals = []
        for code, label in spending_codes:
            val = latest_data[latest_data['Agg_Metric'] == code]['Agg_Value'].sum()
            spend_vals.append({'Category': label, 'Percent': val})
        df_spend = pd.DataFrame([row for row in spend_vals if row['Percent'] > 0])
        if not df_spend.empty:
            fig_pie = px.pie(
                df_spend,
                values="Percent",
                names="Category",
                title="Use of Funds – Spending Categories",
                color_discrete_sequence=px.colors.sequential.PuBu
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No spending breakdown available for this period.")

        # --- 3. Equity bar chart (filter by group, for example Gender) ---
        st.subheader("Equity Bar Chart (demo: if group columns exist)")
        equity_group = ["Male", "Female", "CALD", "Non-CALD"]  # Example
        equity_bars = []
        for group in equity_group:
            code = f"Total_unique_participants_received_funds_{group}"
            val = latest_data[latest_data['Agg_Metric'] == code]['Agg_Value'].sum()
            if val > 0:
                equity_bars.append({"Group": group, "Count": val})
        df_equity = pd.DataFrame(equity_bars)
        if not df_equity.empty:
            fig_equity = px.bar(
                df_equity,
                x="Group",
                y="Count",
                text="Count",
                title="Participants Receiving Funds by Equity Group"
            )
            fig_equity.update_traces(textposition='outside')
            fig_equity.update_layout(showlegend=False)
            st.plotly_chart(fig_equity, use_container_width=True)
        else:
            st.info("Demographic breakdown not available for this period.")
        
        # Empowerment Impact   
        st.subheader("Empowerment & Crisis Impact")
        trend_codes = [
            ("Financial Sufficiency (3mth)", "Avg_fin_suff_score_3mth"),
            ("Financial Sufficiency (6mth)", "Avg_fin_suff_Score_6mth"),
            ("Satisfaction Score", "Avg_satisfaction_score_unique_participants"),
            ("Crisis Dependency", "Avg_emergency_callout_unique_participants")
        ]

        trend_data = []
        for label, code in trend_codes:
            ts = df_p5_filtered[df_p5_filtered["Agg_Metric"] == code]
            for _, row in ts.iterrows():
                trend_data.append({
                    "Metric": label,
                    "Date": row["Date"],
                    "Value": row["Agg_Value"]
                })
        df_trend = pd.DataFrame(trend_data)

        if not df_trend.empty:
            fig_trend = px.line(
                df_trend, x="Date", y="Value",
                color="Metric",
                markers=True,
                title="Empowerment & Crisis Trend Over Time"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No empowerment/crisis trend data available for selected period.")
            
        # Use latest available period for 'before' and 'after'
        score_3mth = latest_data[latest_data['Agg_Metric'] == "Avg_fin_suff_score_3mth"]['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == "Avg_fin_suff_score_3mth"].empty else None
        score_6mth = latest_data[latest_data['Agg_Metric'] == "Avg_fin_suff_Score_6mth"]['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == "Avg_fin_suff_Score_6mth"].empty else None

        if score_3mth is not None and score_6mth is not None:
            fig_before_after = go.Figure(go.Bar(
                x=["3 Months", "6 Months"],
                y=[score_3mth, score_6mth],
                marker_color=["#90caf9", "#1976d2"]
            ))
            fig_before_after.update_layout(
                title="Financial Sufficiency: Before vs. After",
                xaxis_title="Timepoint",
                yaxis_title="Average Score"
            )
            st.plotly_chart(fig_before_after, use_container_width=True)
        else:
            st.info("No before/after data found for financial sufficiency.")


    with tab2:
        # Time series analysis
        st.subheader("📈 Metrics Over Time")
        
        # Select metric for time series
        available_metrics = df_p5_filtered['Agg_Metric'].unique()
        metric_mapping = {clean_metric_name(metric): metric for metric in available_metrics}
        clean_metric_names = list(metric_mapping.keys())
        
        selected_clean_metric = st.selectbox("Select Metric for Time Series", clean_metric_names)
        selected_metric = metric_mapping[selected_clean_metric]

        metric_data = df_p5_filtered[df_p5_filtered['Agg_Metric'] == selected_metric]
        if not metric_data.empty:
            fig_ts = px.line(
                metric_data, x='Date', y='Agg_Value',
                title=f"{selected_clean_metric} Over Time",
                markers=True
            )
            fig_ts.update_layout(
                xaxis_title="Date",
                yaxis_title="Value"
            )
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No data for this metric.")
            
    # ========== TAB 3: METRIC DETAILS ==========
    with tab3:
        st.header("🔍 Detailed Metrics")
        if not df_p5_filtered.empty:
            pivot_data = df_p5_filtered.pivot_table(
                values='Agg_Value',
                index='Agg_Metric',
                columns='Date',
                aggfunc='first'
            ).reset_index()
            st.dataframe(pivot_data, use_container_width=True)
        else:
            st.info("No records for selected filters.")
            
# Page 6
elif page == "6. Engagement of the wider community":
    st.header("🌍 Engagement of the Wider Community")
    df_p6 = df[df["Pillar"] == 6].copy()
    df_p6["Date"] = pd.to_datetime(df_p6["Date"], dayfirst=True)

    # ==== SIDEBAR FILTERS ====
    st.sidebar.subheader("Filters (Page 6)")
    min_date, max_date = df_p6["Date"].min(), df_p6["Date"].max()
    if len(df_p6["Date"].unique()) == 1:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p6_date")
    else:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p6_date")
    if len(selected_range) == 1:
        selected_range = [selected_range[0], selected_range[0]]

    categories = df_p6["Metric_Category"].dropna().unique().tolist()
    selected_categories = st.sidebar.multiselect(
        "📂 Metric Category",
        categories,
        default=categories
    )

    # Apply filters
    df_p6_filtered = df_p6[
        (df_p6["Date"] >= pd.to_datetime(selected_range[0])) &
        (df_p6["Date"] <= pd.to_datetime(selected_range[1])) &
        (df_p6["Metric_Category"].isin(selected_categories))
    ]

    # ==== KPI CARDS ====
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    latest_date = df_p6_filtered["Date"].max()
    latest_data = df_p6_filtered[df_p6_filtered["Date"] == latest_date]

    with col1:
        total_followers = (
            latest_data[latest_data["Agg_Metric"].str.contains("Followers", na=False)]['Agg_Value'].sum()
            if not latest_data.empty else 0
        )
        st.metric("Total Social Media Followers", int(total_followers))

    with col2:
        total_event_attendees = (
            latest_data[latest_data['Agg_Metric'] == 'Total_event_attendee']['Agg_Value'].iloc[0]
            if not latest_data[latest_data['Agg_Metric'] == 'Total_event_attendee'].empty else 0
        )
        st.metric("Event Attendees", int(total_event_attendees))

    with col3:
        total_volunteers = (
            latest_data[latest_data['Agg_Metric'] == 'Total_Volunteers']['Agg_Value'].iloc[0]
            if not latest_data[latest_data['Agg_Metric'] == 'Total_Volunteers'].empty else 0
        )
        st.metric("Volunteers Recruited", int(total_volunteers))

    with col4:
        unique_donors = (
            latest_data[latest_data['Agg_Metric'] == 'Total_unique_donors']['Agg_Value'].iloc[0]
            if not latest_data[latest_data['Agg_Metric'] == 'Total_unique_donors'].empty else 0
        )
        st.metric("Unique Donors", int(unique_donors))

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        funders = (
            latest_data[latest_data['Agg_Metric'] == 'Total_unique_grant_providers']['Agg_Value'].iloc[0]
            if not latest_data[latest_data['Agg_Metric'] == 'Total_unique_grant_providers'].empty else 0
        )
        st.metric("Grant Funders", int(funders))
    with col6:
        edm_open_rate = (
            latest_data[latest_data['Agg_Metric'] == 'Avg_edm_open_rate']['Agg_Value'].iloc[0]
            if not latest_data[latest_data['Agg_Metric'] == 'Avg_edm_open_rate'].empty else 0
        )
        st.metric("EDM Open Rate (%)", f"{edm_open_rate:.1f}%")
    with col7:
        pulse_responses = (
            latest_data[latest_data['Agg_Metric'] == 'Total_pulse_responses']['Agg_Value'].iloc[0]
            if not latest_data[latest_data['Agg_Metric'] == 'Total_pulse_responses'].empty else 0
        )
        st.metric("Pulse Survey Responses", int(pulse_responses))
    with col8:
        mentions = (
            latest_data[latest_data['Agg_Metric'] == 'Total_Mentions_Earned_Topic']['Agg_Value'].iloc[0]
            if not latest_data[latest_data['Agg_Metric'] == 'Total_Mentions_Earned_Topic'].empty else 0
        )
        st.metric("Mentions in Public Discourse", int(mentions))

    # ==== TABS ====
    tab1, tab2, tab3 = st.tabs([
        "📊 Category Overview", 
        "📈 Time Series", 
        "🔍 Metric Details"
    ])

    # === TAB 1: CATEGORY OVERVIEW ===
    with tab1:
        st.header("📊 Category Overview")

        # 1. Line chart: Social reach growth (sum followers)
        follower_codes = [
            'Total_LinkedIn_Followers', 'Total_Instagram_Followers', 
            'Total_Facebook_Followers', 'Total_TikTok_Followers'
        ]
        df_social = df_p6_filtered[df_p6_filtered['Agg_Metric'].isin(follower_codes)]
        if not df_social.empty:
            platform_labels = {
                'Total_LinkedIn_Followers': 'LinkedIn',
                'Total_Instagram_Followers': 'Instagram',
                'Total_Facebook_Followers': 'Facebook',
                'Total_TikTok_Followers': 'TikTok'
            }
            df_social['Platform'] = df_social['Agg_Metric'].map(platform_labels)
            fig_reach = px.line(
                df_social,
                x="Date", y="Agg_Value", color="Platform",
                title="Social Media Reach Growth", markers=True
            )
            st.plotly_chart(fig_reach, use_container_width=True)

        # 2. Bar chart: Community event attendees
        attendee_data = df_p6_filtered[df_p6_filtered['Agg_Metric'] == 'Total_event_attendee']
        if not attendee_data.empty:
            fig_attendees = px.bar(
                attendee_data, x="Date", y="Agg_Value",
                title="Community Event Attendees", text="Agg_Value"
            )
            st.plotly_chart(fig_attendees, use_container_width=True)

        # 3. Email open rate graph
        edm_data = df_p6_filtered[df_p6_filtered['Agg_Metric'] == 'Avg_edm_open_rate']
        if not edm_data.empty:
            fig_edm = px.line(
                edm_data, x="Date", y="Agg_Value",
                markers=True, title="Email Open Rate Over Time"
            )
            st.plotly_chart(fig_edm, use_container_width=True)

        # 4. New contributors (volunteers, donors, funders)
        contrib_codes = [
            ('Total_Volunteers', 'New Volunteers'),
            ('Total_unique_donors', 'New Donors'),
            ('Total_unique_grant_providers', 'New Funders')
        ]
        contrib_df = []
        for code, label in contrib_codes:
            rows = df_p6_filtered[df_p6_filtered["Agg_Metric"] == code]
            for _, row in rows.iterrows():
                contrib_df.append({"Contributor Type": label, "Date": row["Date"], "Count": row["Agg_Value"]})
        df_contrib = pd.DataFrame(contrib_df)
        if not df_contrib.empty:
            fig_contrib = px.line(
                df_contrib, x="Date", y="Count", color="Contributor Type",
                markers=True, title="New Contributors Over Time"
            )
            st.plotly_chart(fig_contrib, use_container_width=True)

        # 5. Pie chart: Volunteer referral source (if more types available)
        referral_data = df_p6_filtered[df_p6_filtered["Agg_Metric"] == "Total_volunteer_referrals"]
        if not referral_data.empty and referral_data["Agg_Value"].sum() > 0:
            referral_breakdown = [
                {"Source": "Friend/Family Referral", "Count": int(referral_data["Agg_Value"].sum())},
                # Add other sources as you get data
            ]
            df_referral = pd.DataFrame(referral_breakdown)
            fig_referral = px.pie(
                df_referral, values="Count", names="Source",
                title="Volunteer Referral Sources"
            )
            st.plotly_chart(fig_referral, use_container_width=True)

        # 6. Sentiment/Empathy/Understanding bar chart
        pulse_codes = [
            ('Avg_issue_understanding_pulse', 'Issue Understanding (avg 1–5)'),
            ('Complexity_ack_rate_pulse', 'Acknowledgement of Complexity (%)'),
            ('Empathy_act_index_pulse', 'High Empathy Index (%)'),
            ('Structural_cause_rate_pulse', 'Structural Cause Attribution (%)'),
            ('Personal_cause_rate_pulse', 'Personal Cause Attribution (%)')
        ]
        pulse_vals = []
        for code, label in pulse_codes:
            v = latest_data[latest_data['Agg_Metric'] == code]['Agg_Value'].sum()
            pulse_vals.append({'Theme': label, 'Score': v})
        df_pulse = pd.DataFrame([row for row in pulse_vals if row['Score'] > 0])
        if not df_pulse.empty:
            fig_sentiment = px.bar(
                df_pulse, x='Theme', y='Score', color='Theme', text='Score',
                title='Community Pulse: Empathy & Understanding'
            )
            fig_sentiment.update_traces(textposition="outside")
            fig_sentiment.update_layout(showlegend=False)
            st.plotly_chart(fig_sentiment, use_container_width=True)

        # 7. Qualitative: Word cloud & themes (require text/preprocessed input)
        st.info("Word cloud and qualitative themes list will appear here if textual/coded data is provided.")

    # === TAB 2: TIME SERIES ===
    with tab2:
    # Time series analysis
        st.subheader("📈 Metrics Over Time")
        
        # Select metric for time series
        available_metrics = df_p6_filtered['Agg_Metric'].unique()
        metric_mapping = {clean_metric_name(metric): metric for metric in available_metrics}
        clean_metric_names = list(metric_mapping.keys())
        
        selected_clean_metric = st.selectbox("Select Metric for Time Series", clean_metric_names)
        selected_metric = metric_mapping[selected_clean_metric]

        metric_data = df_p6_filtered[df_p6_filtered['Agg_Metric'] == selected_metric]
        if not metric_data.empty:
            fig_ts = px.line(
                metric_data, x='Date', y='Agg_Value',
                title=f"{selected_clean_metric} Over Time",
                markers=True
            )
            fig_ts.update_layout(
                xaxis_title="Date",
                yaxis_title="Value"
            )
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No data for this metric.")

    # === TAB 3: METRIC DETAILS ===
    with tab3:
        st.subheader("🔍 Detailed Metrics")
        if not df_p6_filtered.empty:
            pivot_data = df_p6_filtered.pivot_table(
                values='Agg_Value',
                index='Agg_Metric',
                columns='Date',
                aggfunc='first'
            ).reset_index()
            st.dataframe(pivot_data, use_container_width=True)
        else:
            st.info("No records for selected filters.")
            
# Page 7
if page == "7. A cultural shift in society":
    st.header("🌏 A Cultural Shift in Society")
    df_p7 = df[df["Pillar"] == 7].copy()
    df_p7["Date"] = pd.to_datetime(df_p7["Date"], dayfirst=True)

    # ==== Sidebar Filters ====
    st.sidebar.subheader("Filters (Page 7)")
    min_date, max_date = df_p7["Date"].min(), df_p7["Date"].max()
    if len(df_p7["Date"].unique()) == 1:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p7_date")
    else:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p7_date")
    if len(selected_range) == 1:
        selected_range = [selected_range[0], selected_range[0]]

    categories = df_p7["Metric_Category"].dropna().unique().tolist()
    selected_categories = st.sidebar.multiselect(
        "📂 Metric Category",
        categories,
        default=categories
    )

    # Apply filters
    df_p7_filtered = df_p7[
        (df_p7["Date"] >= pd.to_datetime(selected_range[0])) &
        (df_p7["Date"] <= pd.to_datetime(selected_range[1])) &
        (df_p7["Metric_Category"].isin(selected_categories))
    ]

    # ==== KPI CARDS ====
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    latest_date = df_p7_filtered["Date"].max()
    latest_data = df_p7_filtered[df_p7_filtered["Date"] == latest_date]

    with col1:
        pulse_responses = latest_data[latest_data['Agg_Metric'] == 'Total_pulse_responses']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_pulse_responses'].empty else 0
        st.metric("Pulse Survey Responses", int(pulse_responses))
    with col2:
        avg_awareness_rate = latest_data[latest_data['Agg_Metric'] == 'Avg_mobilise_awareness_rate_pulse']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Avg_mobilise_awareness_rate_pulse'].empty else 0
        st.metric("Awareness Rate (%)", f"{avg_awareness_rate:.1f}%")
    with col3:
        issue_understanding = latest_data[latest_data['Agg_Metric'] == 'Avg_issue_understanding_pulse']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Avg_issue_understanding_pulse'].empty else 0
        st.metric("Issue Understanding (1-5)", f"{issue_understanding:.1f}")
    with col4:
        empathy_index = latest_data[latest_data['Agg_Metric'] == 'Empathy_act_index_pulse']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Empathy_act_index_pulse'].empty else 0
        st.metric("Empathy Index (%)", f"{empathy_index:.1f}%")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        complexity_ack = latest_data[latest_data['Agg_Metric'] == 'Complexity_ack_rate_pulse']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Complexity_ack_rate_pulse'].empty else 0
        st.metric("Complexity Acknowledged (%)", f"{complexity_ack:.1f}%")
    with col6:
        struct_cause = latest_data[latest_data['Agg_Metric'] == 'Structural_cause_rate_pulse']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Structural_cause_rate_pulse'].empty else 0
        st.metric("Structural Cause (%)", f"{struct_cause:.1f}%")
    with col7:
        pers_cause = latest_data[latest_data['Agg_Metric'] == 'Personal_cause_rate_pulse']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Personal_cause_rate_pulse'].empty else 0
        st.metric("Personal Cause (%)", f"{pers_cause:.1f}%")
    with col8:
        media_mentions = latest_data[latest_data['Agg_Metric'] == 'Total_media_mentions_topic']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_media_mentions_topic'].empty else 0
        st.metric("Media Mentions", int(media_mentions))

    # ==== Tabs ====
    tab1, tab2, tab3 = st.tabs([
        "📊 Category Overview",
        "📈 Time Series",
        "🔍 Metric Details"
    ])

    # === Category Overview Tab ===
    with tab1:
        st.header("📊 Societal Change Overview")

        # 1. Sentiment Trend Line (Empathy, Complexity, Structural Cause)
        sentiment_codes = [
            ('Empathy_act_index_pulse', 'Empathy (%)'),
            ('Complexity_ack_rate_pulse', 'Complexity Acknowl. (%)'),
            ('Structural_cause_rate_pulse', 'Structural Cause (%)'),
            ('Personal_cause_rate_pulse', 'Personal Cause (%)')
        ]
        sentiment_vals = []
        for code, label in sentiment_codes:
            v = df_p7_filtered[df_p7_filtered['Agg_Metric'] == code][['Date', 'Agg_Value']].dropna()
            for _, row in v.iterrows():
                sentiment_vals.append({'Metric': label, 'Date': row['Date'], 'Value': row['Agg_Value']})
        df_sentiment = pd.DataFrame(sentiment_vals)
        if not df_sentiment.empty:
            fig_sent = px.line(
                df_sentiment, x="Date", y="Value", color="Metric", markers=True,
                title="Sentiment & Public Attitude Trends"
            )
            st.plotly_chart(fig_sent, use_container_width=True)

        # 2. Comparison Bar Chart (Media Mentions)
        comp_codes = [
            ("Total_media_mentions_topic", "Total Media Mentions"),
            ("Total_media_mentions_constructive_topic", "Constructive Mentions"),
            ("Total_media_mentions_PR_topic", "Mobilise-Generated")
        ]
        comp_vals = []
        for code, label in comp_codes:
            total = latest_data[latest_data['Agg_Metric'] == code]['Agg_Value'].sum()
            comp_vals.append({'Type': label, 'Count': total})
        df_comp = pd.DataFrame([row for row in comp_vals if row['Count'] > 0])
        if not df_comp.empty:
            fig_comp = px.bar(
                df_comp, x="Type", y="Count", color="Type", text="Count",
                title="Media Coverage Breakdown"
            )
            fig_comp.update_traces(textposition="outside")
            fig_comp.update_layout(showlegend=False)
            st.plotly_chart(fig_comp, use_container_width=True)

        # 3. Issue Understanding Breakdown (Pulse)
        pulse_codes = [
            ("Avg_mobilise_awareness_rate_pulse", "Correctly Associate Mobilise (%)"),
            ("Avg_issue_understanding_pulse", "Issue Understanding (1-5)"),
        ]
        pulse_vals = []
        for code, label in pulse_codes:
            pulse_score = latest_data[latest_data['Agg_Metric'] == code]['Agg_Value'].sum()
            pulse_vals.append({'Theme': label, 'Score': pulse_score})
        df_pulse = pd.DataFrame([row for row in pulse_vals if row['Score'] > 0])
        if not df_pulse.empty:
            fig_pulse = px.bar(
                df_pulse, x="Theme", y="Score", color="Theme", text="Score",
                title="Awareness & Understanding Scores"
            )
            fig_pulse.update_traces(textposition="outside")
            fig_pulse.update_layout(showlegend=False)
            st.plotly_chart(fig_pulse, use_container_width=True)

        # 4. Platform Engagements (Comparison Chart)
        platform_codes = [
            ("Total_LinkedIn_Engagements", "LinkedIn"),
            ("Total_Instagram_Engagements", "Instagram"),
            ("Total_Facebook_Engagements", "Facebook"),
            ("Total_TikTok_Engagements", "TikTok")
        ]
        plat_vals = []
        for code, label in platform_codes:
            plat_score = latest_data[latest_data['Agg_Metric'] == code]['Agg_Value'].sum()
            plat_vals.append({'Platform': label, 'Engagements': plat_score})
        df_plat = pd.DataFrame([row for row in plat_vals if row['Engagements'] > 0])
        if not df_plat.empty:
            fig_platform = px.bar(
                df_plat, x="Platform", y="Engagements", color="Platform", text="Engagements",
                title="Social Platform Engagements"
            )
            fig_platform.update_traces(textposition="outside")
            fig_platform.update_layout(showlegend=False)
            st.plotly_chart(fig_platform, use_container_width=True)

        # 5. Info blocks for Qual Themes, Map
        st.info("Word cloud, qualitative themes, and demographic/regional breakdowns will display here when text or coded group data are available.")

    # === Time Series Tab ===
    with tab2:
        # Time series analysis
        st.subheader("📈 Metrics Over Time")
        
        # Select metric for time series
        available_metrics = df_p7_filtered['Agg_Metric'].unique()
        metric_mapping = {clean_metric_name(metric): metric for metric in available_metrics}
        clean_metric_names = list(metric_mapping.keys())
        
        selected_clean_metric = st.selectbox("Select Metric for Time Series", clean_metric_names)
        selected_metric = metric_mapping[selected_clean_metric]

        metric_data = df_p7_filtered[df_p7_filtered['Agg_Metric'] == selected_metric]
        if not metric_data.empty:
            fig_ts = px.line(
                metric_data, x='Date', y='Agg_Value',
                title=f"{selected_clean_metric} Over Time",
                markers=True
            )
            fig_ts.update_layout(
                xaxis_title="Date",
                yaxis_title="Value"
            )
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No data for this metric.")

    # === Metric Details Tab ===
    with tab3:
        st.subheader("🔍 Detailed Metrics")
        if not df_p7_filtered.empty:
            pivot_data = df_p7_filtered.pivot_table(
                values='Agg_Value',
                index='Agg_Metric',
                columns='Date',
                aggfunc='first'
            ).reset_index()
            st.dataframe(pivot_data, use_container_width=True)
        else:
            st.info("No records for selected filters.")
            
# Page 8
if page == "8. People progressing post-homelessness":
    st.header("🏠 People Progressing Post-Homelessness")
    df_p8 = df[df["Pillar"] == 8].copy()
    df_p8["Date"] = pd.to_datetime(df_p8["Date"], dayfirst=True)

    # === Sidebar Filters ===
    st.sidebar.subheader("Filters (Page 8)")
    min_date, max_date = df_p8["Date"].min(), df_p8["Date"].max()
    if len(df_p8["Date"].unique()) == 1:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p8_date")
    else:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p8_date")
    if len(selected_range) == 1:
        selected_range = [selected_range[0], selected_range[0]]

    categories = df_p8["Metric_Category"].dropna().unique().tolist()
    selected_categories = st.sidebar.multiselect(
        "📂 Metric Category",
        categories,
        default=categories
    )

    # Apply filters
    df_p8_filtered = df_p8[
        (df_p8["Date"] >= pd.to_datetime(selected_range[0])) &
        (df_p8["Date"] <= pd.to_datetime(selected_range[1])) &
        (df_p8["Metric_Category"].isin(selected_categories))
    ]

    # === KPI Cards ===
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    latest_date = df_p8_filtered["Date"].max()
    latest_data = df_p8_filtered[df_p8_filtered["Date"] == latest_date]

    with col1:
        pct_goals_set = latest_data[latest_data['Agg_Metric'] == '%_participant_goal_set']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == '%_participant_goal_set'].empty else 0
        st.metric("% with Goals Set", f"{pct_goals_set:.1f}%")
    with col2:
        avg_goals = latest_data[latest_data['Agg_Metric'] == 'Total_goal_per_participant']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_goal_per_participant'].empty else 0
        st.metric("Avg Goals per Participant", f"{avg_goals:.1f}")
    with col3:
        avg_goals_ach = latest_data[latest_data['Agg_Metric'] == 'avg_goals_achieved_per_participant_12mth']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'avg_goals_achieved_per_participant_12mth'].empty else 0
        st.metric("Avg Goals Achieved (12m)", f"{avg_goals_ach:.1f}")
    with col4:
        total_goals_ach = latest_data[latest_data['Agg_Metric'] == 'Total_goals_achieved_all_participants_12mth']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_goals_achieved_all_participants_12mth'].empty else 0
        st.metric("Total Goals Achieved (12m)", int(total_goals_ach))

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        housing_12 = latest_data[latest_data['Agg_Metric'] == 'Total_participants_secure_housing_12mth']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_participants_secure_housing_12mth'].empty else 0
        st.metric("Secure Housing (12m)", int(housing_12))
    with col6:
        housing_24 = latest_data[latest_data['Agg_Metric'] == 'Total_participants_secure_housing_24mth']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_participants_secure_housing_24mth'].empty else 0
        st.metric("Secure Housing (24m)", int(housing_24))
    with col7:
        employed_12 = latest_data[latest_data['Agg_Metric'] == 'Total_participants_employed_12mth']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_participants_employed_12mth'].empty else 0
        st.metric("Employed (12m)", int(employed_12))
    with col8:
        employed_24 = latest_data[latest_data['Agg_Metric'] == 'Total_participants_employed_24mth']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_participants_employed_24mth'].empty else 0
        st.metric("Employed (24m)", int(employed_24))

    # ==== Tabs ====
    tab1, tab2, tab3 = st.tabs([
        "📊 Category Overview",
        "📈 Time Series",
        "🔍 Metric Details"
    ])

    # === Tab 1: Category Overview ===
    with tab1:
        st.header("📊 Goal Attainment & Progress Overview")

        # # Progress Funnel
        # funnel_steps = []
        # if not latest_data.empty:
        #     total_participants = 100  # Use actual total if present in your dataset
        #     pct_goals = pct_goals_set if pct_goals_set else 0
        #     avg_total_goals = avg_goals if avg_goals else 0
        #     avg_ach = avg_goals_ach if avg_goals_ach else 0
        #     total_ach = total_goals_ach if total_goals_ach else 0
        #     funnel_steps = [
        #         ("Participants", total_participants),
        #         ("% with Goals Set", pct_goals),
        #         ("Avg Goals/Participant", avg_total_goals),
        #         ("Avg Goals Achieved", avg_ach),
        #         ("Total Goals Achieved", total_ach)
        #     ]
        # funnel_df = pd.DataFrame(funnel_steps, columns=["Step","Value"])
        # if not funnel_df.empty:
        #     import plotly.graph_objects as go
        #     fig_funnel = go.Figure(go.Funnel(
        #         y=funnel_df["Step"], 
        #         x=funnel_df["Value"],
        #         textinfo="value+percent initial"
        #     ))
        #     fig_funnel.update_layout(title_text="Participant Goal Attainment Funnel")
        #     st.plotly_chart(fig_funnel, use_container_width=True)

        # Bar chart: Housing, Employment, Quality of Life at 12m/24m
        outcome_codes = [
            ("Total_participants_secure_housing_12mth", "Secure Housing", "12 Months"),
            ("Total_participants_secure_housing_24mth", "Secure Housing", "24 Months"),
            ("Total_participants_employed_12mth", "Employed", "12 Months"),
            ("Total_participants_employed_24mth", "Employed", "24 Months"),
            ("Avg_participants_qual_life_12mth", "Quality of Life (avg)", "12 Months"),
            ("Avg_participants_qual_life_24mth", "Quality of Life (avg)", "24 Months"),
        ]
        bar_data = []
        for code, outcome, period in outcome_codes:
            val = latest_data[latest_data["Agg_Metric"] == code]['Agg_Value'].sum()
            bar_data.append({"Outcome": outcome, "Period": period, "Value": val})
        df_bar = pd.DataFrame(bar_data)
        if not df_bar.empty:
            fig_bar = px.bar(
                df_bar, x="Outcome", y="Value",
                color="Period", barmode="group",
                text="Value", title="Key Outcomes at 12 and 24 Months"
            )
            fig_bar.update_traces(textposition="outside")
            st.plotly_chart(fig_bar, use_container_width=True)

        # Participant stories / qualitative (placeholder)
        # Prepare data for both metrics already in df_p8_filtered
        story_ts = df_p8_filtered[df_p8_filtered["Agg_Metric"] == "Total_participant_story_mobilise_mktg"][["Date", "Agg_Value"]].copy()
        story_ts["Metric"] = "Participant Stories in Marketing"

        meetings_ts = df_p8_filtered[df_p8_filtered["Agg_Metric"] == "Total_participant_voice_mobilise_mtgs"][["Date", "Agg_Value"]].copy()
        meetings_ts["Metric"] = "Voice in Leadership Meetings"

        combined_ts = pd.concat([story_ts, meetings_ts], ignore_index=True)

        if not combined_ts.empty:
            fig = px.line(
                combined_ts,
                x="Date",
                y="Agg_Value",
                color="Metric",
                markers=True,
                title="Participant Voice & Representation Over Time"
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Count",
                legend_title="Metric"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for participant stories or leadership voice.")

    # === Tab 2: Time Series ===
    with tab2:
        # Time series analysis
        st.subheader("📈 Metrics Over Time")
        
        # Select metric for time series
        available_metrics = df_p8_filtered['Agg_Metric'].unique()
        metric_mapping = {clean_metric_name(metric): metric for metric in available_metrics}
        clean_metric_names = list(metric_mapping.keys())
        
        selected_clean_metric = st.selectbox("Select Metric for Time Series", clean_metric_names)
        selected_metric = metric_mapping[selected_clean_metric]

        metric_data = df_p8_filtered[df_p8_filtered['Agg_Metric'] == selected_metric]
        if not metric_data.empty:
            fig_ts = px.line(
                metric_data, x='Date', y='Agg_Value',
                title=f"{selected_clean_metric} Over Time",
                markers=True
            )
            fig_ts.update_layout(
                xaxis_title="Date",
                yaxis_title="Value"
            )
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No data for this metric.")

    # === Tab 3: Metric Details ===
    with tab3:
        st.subheader("🔍 Detailed Metrics")
        if not df_p8_filtered.empty:
            pivot_data = df_p8_filtered.pivot_table(
                values='Agg_Value',
                index='Agg_Metric',
                columns='Date',
                aggfunc='first'
            ).reset_index()
            st.dataframe(pivot_data, use_container_width=True)
        else:
            st.info("No records for selected filters.")

# Page 9
if page == "9. Homelessness humanised through storytelling":
    st.header("📖 Homelessness Humanised Through Storytelling")
    df_p9 = df[df["Pillar"] == 9].copy()
    df_p9["Date"] = pd.to_datetime(df_p9["Date"], dayfirst=True)

    # === Sidebar Filters ===
    st.sidebar.subheader("Filters (Page 9)")
    min_date, max_date = df_p9["Date"].min(), df_p9["Date"].max()
    if len(df_p9["Date"].unique()) == 1:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p9_date")
    else:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p9_date")
    if len(selected_range) == 1:
        selected_range = [selected_range[0], selected_range[0]]

    categories = df_p9["Metric_Category"].dropna().unique().tolist()
    selected_categories = st.sidebar.multiselect(
        "📂 Metric Category",
        categories,
        default=categories
    )

    # Apply filters
    df_p9_filtered = df_p9[
        (df_p9["Date"] >= pd.to_datetime(selected_range[0])) &
        (df_p9["Date"] <= pd.to_datetime(selected_range[1])) &
        (df_p9["Metric_Category"].isin(selected_categories))
    ]

    # === KPI CARDS ===
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    latest_date = df_p9_filtered["Date"].max()
    latest_data = df_p9_filtered[df_p9_filtered["Date"] == latest_date]

    with col1:
        n_stories_mktg = latest_data[latest_data['Agg_Metric'] == 'Total_participant_story_mobilise_mktg']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_participant_story_mobilise_mktg'].empty else 0
        st.metric("Stories Used in Marketing", int(n_stories_mktg))
    with col2:
        n_stories_total = latest_data[latest_data['Agg_Metric'] == 'Total_participant_story_mobilise']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_participant_story_mobilise'].empty else 0
        st.metric("Total Participant Stories", int(n_stories_total))
    with col3:
        mentions_media = latest_data[latest_data['Agg_Metric'] == 'Total_Mentions_Earned_participant_story']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_Mentions_Earned_participant_story'].empty else 0
        st.metric('Media Mentions (Stories)', int(mentions_media))
    with col4:
        engagement_sum = (
            latest_data[latest_data['Agg_Metric'] == 'Total_LinkedIn_Engagements_participant_story']['Agg_Value'].sum() +
            latest_data[latest_data['Agg_Metric'] == 'Total_Instagram_Engagements_participant_story']['Agg_Value'].sum() +
            latest_data[latest_data['Agg_Metric'] == 'Total_Facebook_Engagements_participant_story']['Agg_Value'].sum() +
            latest_data[latest_data['Agg_Metric'] == 'Total_TikTok_Engagements_participant_story']['Agg_Value'].sum()
        )
        st.metric("Total Story Engagements", int(engagement_sum))

    # ==== Tabs ====
    tab1, tab2, tab3 = st.tabs([
        "📊 Category Overview",
        "📈 Time Series",
        "🔍 Metric Details"
    ])

    # === Tab 1: Category Overview ===
    with tab1:
        # st.header("📊 Storytelling Impact Overview")

        # 1. Story Source Breakdown (Pie Chart)
        st.subheader("Story Source Breakdown")
        story_vals = [
            dict(Type="Used in Marketing", Value=n_stories_mktg),
            dict(Type="Total Stories Co-Created", Value=n_stories_total)
        ]
        df_story = pd.DataFrame(story_vals)
        if df_story['Value'].sum() > 0:
            fig_story = px.pie(
                df_story, values="Value", names="Type"
                # title="Stories: Co-created vs. Used in Marketing"
            )
            st.plotly_chart(fig_story, use_container_width=True)
        else:
            st.info("No story data for this period.")

        # 2. Stacked Bar Chart: Participant Story Awareness Metrics Over Time
        # st.subheader("Awareness Metrics by Month (Stacked)")
        awareness_codes = [
            ('Total_LinkedIn_Engagements_participant_story', 'LinkedIn'),
            ('Total_Instagram_Engagements_participant_story', 'Instagram'),
            ('Total_Facebook_Engagements_participant_story', 'Facebook'),
            ('Total_TikTok_Engagements_participant_story', 'TikTok'),
            ('Total_Mentions_Earned_participant_story', 'Media Mentions')
        ]
        # Build a tidy DataFrame for plotting
        stack_data = []
        # Get unique months in the filtered data
        for code, label in awareness_codes:
            rows = df_p9_filtered[df_p9_filtered['Agg_Metric'] == code]
            for _, row in rows.iterrows():
                stack_data.append({
                    'Date': row['Date'],
                    'Channel': label,
                    'Value': row['Agg_Value']
                })
        df_stack = pd.DataFrame(stack_data)
        if not df_stack.empty:
            # Group by month if you want month granularity (can also do by exact date)
            df_stack['Month'] = df_stack['Date'].dt.to_period('M').dt.to_timestamp()
            fig_stack = px.bar(
                df_stack,
                x='Month', y='Value', color='Channel',
                title="Monthly Participant Story Awareness Metrics (Stacked Bar)",
                text_auto=True
            )
            fig_stack.update_layout(barmode='stack', xaxis_title="Month", yaxis_title="Engagements / Mentions")
            st.plotly_chart(fig_stack, use_container_width=True)
        else:
            st.info("No awareness data available for the selected period.")

        # 3. Timeline of Releases (Bar chart by date)
        # st.subheader("Participant Stories Released Over Time")
        releases_data = df_p9_filtered[df_p9_filtered["Agg_Metric"] == "Total_participant_story_mobilise"]
        if not releases_data.empty:
            fig_time = px.bar(
                releases_data, x="Date", y="Agg_Value", text="Agg_Value",
                title="Participant Stories Released Over Time"
            )
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("No story release data for selected period.")

        # 4. Qualitative Quotes / Word Cloud Placeholder
        st.info("Word cloud, sentiment analysis and qualitative story quotes will appear here when text data is provided.")


    # === Tab 2: Time Series ===
    with tab2:
        # Time series analysis
        st.subheader("📈 Metrics Over Time")
        
        # Select metric for time series
        available_metrics = df_p9_filtered['Agg_Metric'].unique()
        metric_mapping = {clean_metric_name(metric): metric for metric in available_metrics}
        clean_metric_names = list(metric_mapping.keys())
        
        selected_clean_metric = st.selectbox("Select Metric for Time Series", clean_metric_names)
        selected_metric = metric_mapping[selected_clean_metric]

        metric_data = df_p9_filtered[df_p9_filtered['Agg_Metric'] == selected_metric]
        if not metric_data.empty:
            fig_ts = px.line(
                metric_data, x='Date', y='Agg_Value',
                title=f"{selected_clean_metric} Over Time",
                markers=True
            )
            fig_ts.update_layout(
                xaxis_title="Date",
                yaxis_title="Value"
            )
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No data for this metric.")

    # === Tab 3: Metric Details ===
    with tab3:
        st.subheader("🔍 Detailed Metrics")
        if not df_p9_filtered.empty:
            pivot_data = df_p9_filtered.pivot_table(
                values='Agg_Value',
                index='Agg_Metric',
                columns='Date',
                aggfunc='first'
            ).reset_index()
            st.dataframe(pivot_data, use_container_width=True)
        else:
            st.info("No records for selected filters.")
            
# Page 10
if page == "10. New & innovative responses":
    st.header("💡 New & Innovative Responses")
    df_p10 = df[df["Pillar"] == 10].copy()
    df_p10["Date"] = pd.to_datetime(df_p10["Date"], dayfirst=True)

    # === Sidebar Filters ===
    st.sidebar.subheader("Filters (Page 10)")
    min_date, max_date = df_p10["Date"].min(), df_p10["Date"].max()
    if len(df_p10["Date"].unique()) == 1:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p10_date")
    else:
        selected_range = st.sidebar.date_input("Date Range", [min_date, max_date], key="p10_date")
    if len(selected_range) == 1:
        selected_range = [selected_range[0], selected_range[0]]

    categories = df_p10["Metric_Category"].dropna().unique().tolist()
    selected_categories = st.sidebar.multiselect(
        "📂 Metric Category",
        categories,
        default=categories
    )

    # Apply filters
    df_p10_filtered = df_p10[
        (df_p10["Date"] >= pd.to_datetime(selected_range[0])) &
        (df_p10["Date"] <= pd.to_datetime(selected_range[1])) &
        (df_p10["Metric_Category"].isin(selected_categories))
    ]

    # === KPI CARDS ===
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    latest_date = df_p10_filtered["Date"].max()
    latest_data = df_p10_filtered[df_p10_filtered["Date"] == latest_date]

    with col1:
        pilots_in_dev = latest_data[latest_data['Agg_Metric'] == 'Total_pilot_projects_in_dev']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_pilot_projects_in_dev'].empty else 0
        st.metric("Pilots In Development", int(pilots_in_dev))
    with col2:
        pilots_live = latest_data[latest_data['Agg_Metric'] == 'Total_pilot_projects_live_cumulative']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_pilot_projects_live_cumulative'].empty else 0
        st.metric("Pilots Live (Cumulative)", int(pilots_live))
    with col3:
        sector_mentions = latest_data[latest_data['Agg_Metric'] == 'Total_sector_mentions_reports']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_sector_mentions_reports'].empty else 0
        st.metric("Sector Mentions (Reports)", int(sector_mentions))
    with col4:
        partner_workshops = latest_data[latest_data['Agg_Metric'] == 'Total_partner_workshops_mobilise_hosted']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_partner_workshops_mobilise_hosted'].empty else 0
        st.metric("Partner Workshops Hosted", int(partner_workshops))

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        requests_data = latest_data[latest_data['Agg_Metric'] == 'Total_requests_for_cumulative_data']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_requests_for_cumulative_data'].empty else 0
        st.metric("Requests for Data", int(requests_data))
    with col6:
        avg_hours_intake = latest_data[latest_data['Agg_Metric'] == 'Avg_hours_intake_process_per_person']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Avg_hours_intake_process_per_person'].empty else 0
        st.metric("Avg Intake Hours / Person", f"{avg_hours_intake:.2f}")
    with col7:
        avg_feedback = latest_data[latest_data['Agg_Metric'] == 'Avg_feedback_score_3p']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Avg_feedback_score_3p'].empty else 0
        st.metric("3rd Party Feedback (1-5)", f"{avg_feedback:.2f}")
    with col8:
        part_feedback_sessions = latest_data[latest_data['Agg_Metric'] == 'Total_participant_program_feedback']['Agg_Value'].iloc[0] if not latest_data[latest_data['Agg_Metric'] == 'Total_participant_program_feedback'].empty else 0
        st.metric("Participant Feedback Sessions", int(part_feedback_sessions))

    # ==== Tabs ====
    tab1, tab2, tab3 = st.tabs([
        "📊 Category Overview",
        "📈 Time Series",
        "🔍 Metric Details"
    ])

    # === Tab 1: Category Overview ===
    with tab1:
        st.header("📊 Innovation & Efficiency Overview")

        # 1. Initiative Tracker/Funnel Chart: Pilots in development -> live
        if not latest_data.empty:
            import plotly.graph_objects as go
            funnel_steps = [
                ("Pilot Projects (In Dev)", pilots_in_dev),
                ("Pilots Live (Cumulative)", pilots_live)
            ]
            funnel_df = pd.DataFrame(funnel_steps, columns=["Stage", "Value"])
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_df["Stage"], 
                x=funnel_df["Value"],
                textinfo="value+percent initial"
            ))
            fig_funnel.update_layout(title_text="Innovation Funnel: Idea to Scale")
            st.plotly_chart(fig_funnel, use_container_width=True)

        # # 2. Table of Innovations by Category
        # st.subheader("Innovations Table by Category")
        # innovation_metrics = [
        #     ('Total_pilot_projects_in_dev', 'Pilot Projects in Development'),
        #     ('Total_pilot_projects_live_cumulative', 'Pilot Projects Live'),
        #     ('Total_requests_for_cumulative_data', 'Requests for Data Use'),
        #     ('Total_sector_mentions_reports', 'Sector Mentions'),
        #     ('Total_partner_workshops_mobilise_hosted', 'Workshops Hosted'),
        #     ('Total_participant_program_feedback', 'Participant Feedback Sessions')
        # ]
        # innovation_rows = []
        # for code, label in innovation_metrics:
        #     val = latest_data[latest_data['Agg_Metric'] == code]['Agg_Value'].sum()
        #     innovation_rows.append({'Innovation': label, 'Count': val})
        # df_innov = pd.DataFrame(innovation_rows)
        # st.dataframe(df_innov, use_container_width=True)

        # 3. Partner Uptake Line Chart
        uptake_data = df_p10_filtered[df_p10_filtered["Agg_Metric"] == "Total_requests_for_cumulative_data"]
        if not uptake_data.empty:
            fig_line = px.line(
                uptake_data, x="Date", y="Agg_Value",
                title="Partner Uptake: Requests for Mobilise Tools/Data Over Time",
                markers=True
            )
            st.plotly_chart(fig_line, use_container_width=True)

        # 4. Before/After Bar (Avg. Intake Hours)
        # st.subheader("Efficiency – Before/After Comparison")
        intake_time_data = df_p10_filtered[df_p10_filtered["Agg_Metric"] == "Avg_hours_intake_process_per_person"].sort_values("Date")

        if intake_time_data.shape[0] >= 2:
            before_value = intake_time_data.iloc[0]['Agg_Value']
            after_value = intake_time_data.iloc[-1]['Agg_Value']
            before_month = intake_time_data.iloc[0]['Date'].strftime("%b %Y")
            after_month = intake_time_data.iloc[-1]['Date'].strftime("%b %Y")
            
            fig_bar = px.bar(
                x=[f"Before\n({before_month})", f"After\n({after_month})"],
                y=[before_value, after_value],
                text=[before_value, after_value],
                title="Avg Intake Process Hours – Before/After Change (by Month)"
            )
            fig_bar.update_traces(textposition="outside")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("More than one timepoint needed for before/after comparison.")


        # 5. Feedback Bar Chart
        # st.subheader("Feedback Score Bar Chart (Third Party / Partner)")
        feedback_data = df_p10_filtered[df_p10_filtered["Agg_Metric"] == "Avg_feedback_score_3p"]
        if not feedback_data.empty:
            fig_fb = px.bar(
                feedback_data, x="Date", y="Agg_Value", text="Agg_Value",
                title="Third Party / Partner Feedback Over Time"
            )
            fig_fb.update_traces(textposition="outside")
            st.plotly_chart(fig_fb, use_container_width=True)

        # 6. Co-Design Involvement Tracker
        # st.subheader("Tracker: Participant Feedback Sessions (Co-Design)")
        co_design_data = df_p10_filtered[df_p10_filtered["Agg_Metric"] == "Total_participant_program_feedback"]
        if not co_design_data.empty:
            fig_cod = px.bar(
                co_design_data, x="Date", y="Agg_Value", text="Agg_Value",
                title="Participant Feedback Sessions Over Time"
            )
            fig_cod.update_traces(textposition="outside")
            st.plotly_chart(fig_cod, use_container_width=True)

        # 7. Qual Quotes/Process Updates Section (Placeholder)
        st.info("Qualitative quotes and process update summaries will appear here as data becomes available.")

    # === Tab 2: Time Series ===
    with tab2:
        # Time series analysis
        st.subheader("📈 Metrics Over Time")
        
        # Select metric for time series
        available_metrics = df_p10_filtered['Agg_Metric'].unique()
        metric_mapping = {clean_metric_name(metric): metric for metric in available_metrics}
        clean_metric_names = list(metric_mapping.keys())
        
        selected_clean_metric = st.selectbox("Select Metric for Time Series", clean_metric_names)
        selected_metric = metric_mapping[selected_clean_metric]

        metric_data = df_p10_filtered[df_p10_filtered['Agg_Metric'] == selected_metric]
        if not metric_data.empty:
            fig_ts = px.line(
                metric_data, x='Date', y='Agg_Value',
                title=f"{selected_clean_metric} Over Time",
                markers=True
            )
            fig_ts.update_layout(
                xaxis_title="Date",
                yaxis_title="Value"
            )
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No data for this metric.")

    # === Tab 3: Metric Details ===
    with tab3:
        st.subheader("🔍 Detailed Metrics")
        if not df_p10_filtered.empty:
            pivot_data = df_p10_filtered.pivot_table(
                values='Agg_Value',
                index='Agg_Metric',
                columns='Date',
                aggfunc='first'
            ).reset_index()
            st.dataframe(pivot_data, use_container_width=True)
        else:
            st.info("No records for selected filters.")



st.markdown("---")
st.caption("Use the sidebar to navigate. More features and visualizations coming soon!")