import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import json

# Import our custom modules
from search_engine import VCSearchEngine
from content_analyzer import ContentAnalyzer
from data_manager import DataManager

# Page config
st.set_page_config(
    page_title="India VC Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .sector-tag {
        background-color: #e1f5fe;
        color: #01579b;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.1rem;
        display: inline-block;
    }
    
    .priority-high { background-color: #ffebee; color: #c62828; }
    .priority-medium { background-color: #fff8e1; color: #ef6c00; }
    .priority-low { background-color: #e8f5e8; color: #2e7d32; }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize components
    @st.cache_resource
    def init_components():
        search_engine = VCSearchEngine()
        analyzer = ContentAnalyzer()
        data_manager = DataManager()
        return search_engine, analyzer, data_manager
    
    search_engine, analyzer, data_manager = init_components()
    
    # Header
    st.markdown('<h1 class="main-header">🚀 India VC Intelligence Agent</h1>', unsafe_allow_html=True)
    st.markdown("**Real-time Investment Thesis & Thought Leadership Monitoring**")
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Control Panel")
        
        # Manual search trigger
        if st.button("🔍 Run Search Now", type="primary"):
            with st.spinner("Searching across sources..."):
                run_search(search_engine, analyzer, data_manager)
        
        st.divider()
        
        # Filters
        st.subheader("📊 Filters")
        
        # Date range
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=7), datetime.now()),
            max_value=datetime.now()
        )
        
        # Sector filter
        sectors = ["All", "Consumer", "D2C", "SaaS", "Fintech", "AI SaaS", "Agentic AI"]
        selected_sector = st.selectbox("Sector", sectors)
        
        # VC filter
        vcs = ["All", "Peak XV (Sequoia)", "Accel", "Matrix Partners", "Elevation", "Lightspeed", "Blume Ventures"]
        selected_vc = st.selectbox("VC Firm", vcs)
        
        # Priority filter
        priorities = ["All", "High", "Medium", "Low"]
        selected_priority = st.selectbox("Priority", priorities)
        
        st.divider()
        
        # Data management
        st.subheader("🗄️ Data Management")
        if st.button("📊 Export Data"):
            export_data(data_manager)
        
        if st.button("🗑️ Clear Old Data"):
            data_manager.cleanup_old_data(days=90)
            st.success("Old data cleared!")
    
    # Main content area
    col1, col2, col3, col4 = st.columns(4)
    
    # Get filtered data
    df = data_manager.get_filtered_content(
        start_date=date_range[0] if len(date_range) == 2 else None,
        end_date=date_range[1] if len(date_range) == 2 else None,
        sector=selected_sector if selected_sector != "All" else None,
        vc_firm=selected_vc if selected_vc != "All" else None,
        priority=selected_priority if selected_priority != "All" else None
    )
    
    # Metrics
    with col1:
        total_articles = len(df) if df is not None else 0
        st.markdown(f'<div class="metric-card"><h3>{total_articles}</h3><p>Total Articles</p></div>', unsafe_allow_html=True)
    
    with col2:
        high_priority = len(df[df['priority'] == 'High']) if df is not None and not df.empty else 0
        st.markdown(f'<div class="metric-card"><h3>{high_priority}</h3><p>High Priority</p></div>', unsafe_allow_html=True)
    
    with col3:
        today_articles = len(df[df['date_published'] >= datetime.now().date()]) if df is not None and not df.empty else 0
        st.markdown(f'<div class="metric-card"><h3>{today_articles}</h3><p>Today</p></div>', unsafe_allow_html=True)
    
    with col4:
        avg_score = round(df['relevance_score'].mean(), 1) if df is not None and not df.empty else 0
        st.markdown(f'<div class="metric-card"><h3>{avg_score}</h3><p>Avg Score</p></div>', unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📰 Latest Content", "📈 Analytics", "🎯 Themes", "💡 Insights"])
    
    with tab1:
        display_content_feed(df)
    
    with tab2:
        display_analytics(df)
    
    with tab3:
        display_themes(df, analyzer)
    
    with tab4:
        display_insights(df, analyzer)

def run_search(search_engine, analyzer, data_manager):
    """Execute the search and analysis pipeline"""
    try:
        # Search for content
        results = search_engine.search_all_sources()
        
        # Analyze and score content
        analyzed_results = []
        for result in results:
            analysis = analyzer.analyze_content(result)
            analyzed_results.append(analysis)
        
        # Store in database
        data_manager.store_content(analyzed_results)
        
        st.success(f"✅ Found and analyzed {len(analyzed_results)} new articles!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Search failed: {str(e)}")

def display_content_feed(df):
    """Display the main content feed"""
    if df is None or df.empty:
        st.info("No content found. Try running a search or adjusting filters.")
        return
    
    # Sort by relevance score and date
    df_sorted = df.sort_values(['relevance_score', 'date_published'], ascending=[False, False])
    
    for idx, row in df_sorted.iterrows():
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Title and source
                st.markdown(f"**[{row['title']}]({row['url']})**")
                st.markdown(f"*{row['source']} • {row['author']} • {row['date_published']}*")
                
                # Summary
                if pd.notna(row['summary']):
                    st.markdown(row['summary'])
                
                # Tags
                if pd.notna(row['sectors']):
                    sectors = row['sectors'].split(',')
                    tags_html = ''.join([f'<span class="sector-tag">{sector.strip()}</span>' for sector in sectors])
                    st.markdown(tags_html, unsafe_allow_html=True)
            
            with col2:
                # Score and priority
                score_color = "🟢" if row['relevance_score'] >= 80 else "🟡" if row['relevance_score'] >= 60 else "🔴"
                st.markdown(f"{score_color} **{row['relevance_score']}/100**")
                
                priority_class = f"priority-{row['priority'].lower()}"
                st.markdown(f'<span class="{priority_class}">{row["priority"]} Priority</span>', unsafe_allow_html=True)
                
                # Feedback buttons
                col_up, col_down = st.columns(2)
                with col_up:
                    if st.button("👍", key=f"up_{idx}"):
                        update_feedback(idx, 1)
                with col_down:
                    if st.button("👎", key=f"down_{idx}"):
                        update_feedback(idx, -1)
            
            st.divider()

def display_analytics(df):
    """Display analytics dashboard"""
    if df is None or df.empty:
        st.info("No data available for analytics.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Content by sector
        sector_counts = df['sectors'].str.split(',').explode().value_counts().head(10)
        fig_sectors = px.bar(
            x=sector_counts.values,
            y=sector_counts.index,
            orientation='h',
            title="Content by Sector",
            color=sector_counts.values,
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_sectors, use_container_width=True)
    
    with col2:
        # Content by VC firm
        vc_counts = df['vc_firm'].value_counts().head(10)
        fig_vcs = px.pie(
            values=vc_counts.values,
            names=vc_counts.index,
            title="Content by VC Firm"
        )
        st.plotly_chart(fig_vcs, use_container_width=True)
    
    # Timeline
    df['date_published'] = pd.to_datetime(df['date_published'])
    daily_counts = df.groupby(df['date_published'].dt.date).size().reset_index()
    daily_counts.columns = ['date', 'count']
    
    fig_timeline = px.line(
        daily_counts,
        x='date',
        y='count',
        title="Content Volume Over Time",
        markers=True
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

def display_themes(df, analyzer):
    """Display theme analysis"""
    if df is None or df.empty:
        st.info("No data available for theme analysis.")
        return
    
    # Get themes from analyzer
    themes = analyzer.extract_themes(df['content'].tolist())
    
    # Display top themes
    st.subheader("🎯 Trending Themes")
    for theme, articles in themes.items():
        with st.expander(f"**{theme.title()}** ({len(articles)} articles)"):
            for article in articles[:5]:  # Show top 5 articles per theme
                st.markdown(f"• [{article['title']}]({article['url']})")

def display_insights(df, analyzer):
    """Display AI-generated insights"""
    if df is None or df.empty:
        st.info("No data available for insights.")
        return
    
    with st.spinner("Generating insights..."):
        insights = analyzer.generate_insights(df)
    
    st.subheader("💡 AI-Generated Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔥 Hot Topics**")
        st.markdown(insights.get('hot_topics', 'No hot topics identified.'))
    
    with col2:
        st.markdown("**📊 Market Sentiment**")
        st.markdown(insights.get('sentiment', 'Sentiment analysis not available.'))
    
    st.markdown("**🔮 Predictions**")
    st.markdown(insights.get('predictions', 'No predictions available.'))

def update_feedback(article_id, feedback):
    """Update user feedback for learning"""
    # This will be implemented in the data_manager
    st.success("Feedback recorded! 🙏")

def export_data(data_manager):
    """Export data to CSV"""
    df = data_manager.get_all_content()
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"vc_intelligence_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()