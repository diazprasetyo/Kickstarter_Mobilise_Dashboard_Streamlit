# Mobilise Theory of Change Dashboard

[Launch the Live Dashboard](https://mobilise-dashboard.streamlit.app/)

Welcome! This Streamlit dashboard brings to life the Mobilise Theory of Change, tracking engagement, impact, equity, and progress across all pillars of the Mobilise movement.

## About the Project

This dashboard provides a interactive and equity-focused way to monitor Mobilise’s key outcomes and activities. It is designed for Mobilise team members, partners, and the community to:

- Track core metrics for each Theory of Change pillar
- Grasp insights about impact, engagement, reach, and system change
- Enable equity analysis by demographic group, geography, or time period (soon to come)
- Highlight innovation, stories, and qualitative as well as quantitative outcomes

Data are ingested from Google Sheets, processed, and visualized page-by-page with user-friendly controls and exportable tables.

## Features

- **Modular design**: Each pillar of the Theory of Change is presented on its own dashboard page (10 total), with consistent filters and layouts.
- **Powerful filters**: Date range, metric category, and (per design) demographic or outcome filters available.
- **KPI cards**: Key headline metrics at a glance, per pillar and context.
- **Interactive charts**: Bar, pie, funnel, line, radar, and stacked charts as appropriate for each outcome area.
- **Time series analysis**: Quickly see trends in any metric over time with a dynamic metric dropdown on all pages.
- **Full metrics table**: Export, audit, or deep-dive into all filtered data via details tab.
- **Qualitative placeholders**: Ready for story/quote/word cloud or regional analysis extensions.
- **Auto-refresh and update**: Cached and refreshable data pipeline with Google Sheets integration.

## Dashboard Structure

Every page follows a common, user-friendly template:

1. **Sidebar Filters**  
   Date range, metric category, and (on some pages) demographic filters.

2. **KPI Row**  
   Key metrics for the latest period, updated with current filters.

3. **Tabs**  
   - **Category Overview**: Main summary visuals, equity/bar/pie/funnel charts, and qualitative blocks.
   - **Time Series**: Select any available metric and view its trend over time.
   - **Metric Details**: See and export a full pivoted table of every metric for the current page and filter selections.

### Pages/Pillars

| Page # | Pillar Name                                      | Example Key Metrics                               |
|--------|--------------------------------------------------|---------------------------------------------------|
| 1      | Ignite a Movement                                | Volunteers, Signups, Engagements, Followers, Media|
| 2      | Empower those experiencing homelessness          | Housing Retention, Stable Housing, Wellbeing      |
| 3      | Promote direct participation in the solution     | Volunteer Involvement, Leadership Representation  |
| 4      | Expanded outreach opportunities                  | Outreach Sessions, Individuals Reached, Consistency|
| 5      | Distribution of funds                            | Participants Funded, Use of Funds, Satisfaction   |
| 6      | Engagement of the wider community                | Social Reach, Event Attendance, Donors, Sentiment |
| 7      | A cultural shift in society                      | Empathy, Stigma, Media Tone, Public Support       |
| 8      | People progressing post-homelessness             | Goal Attainment, Housing/Work, Participant Voice  |
| 9      | Homelessness humanised through storytelling      | Story Creation, Engagement, Media/Mentions        |
| 10     | New & innovative responses                       | Pilots Launched, Uptake, Process Efficiency       |

## ⚙️ Setup & Usage

1. **Clone the repo** and install requirements using `pip install -r requirements.txt`.
2. **Update data source** in `streamlit_app.py`:
    - Set your Google Sheet URL.
3. **Launch the dashboard**:
   ```bash
   streamlit run streamlit_app.py
   ```
4. **Navigate** between pages using the sidebar.
5. **Adjust filters** and export data as needed!

## File Structure

- `streamlit_app.py`: Main dashboard app (add/modify visuals/logic here)
- `README.md`: You are here!

## Extending the Dashboard

- Want to add more metrics or break down by new demographics?  
  Just update your Sheet/CSV and the code will handle new fields.
- For maps, word clouds, or text analytics, extend the placeholder panels with your code.
- To further optimise, modularize common chart/table functions and use caching globally.

## Support & Contribution

- **Issues & Questions**: Please open a GitHub Issue for bugs, requests, or clarification.
- **Contributions**: PRs are welcome! See the file structure for entry points.

[Explore the Live Dashboard](https://mobilise-dashboard.streamlit.app/)

**Mobilise AU Dashboard — Ignite Movement, Empower Change, Track Equity.**