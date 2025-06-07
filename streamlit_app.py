import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Import our custom modules
try:
    from search_engine import VCSearchEngine
    from content_analyzer import ContentAnalyzer
    from data_manager import DataManager
    from config import SEARCH_QUERIES, VC_FIRMS, PRIORITY_SECTORS
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="India VC Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    """Initialize search engine, analyzer, and data manager"""
    search_engine = VCSearchEngine()
    analyzer = ContentAnalyzer()
    data_manager = DataManager()
    return search_engine, analyzer, data_manager

# Initialize
search_engine, analyzer, data_manager = init_components()

# Sidebar - Control Panel
st.sidebar.title("🎛️ Control Panel")

# Search Controls
st.sidebar.subheader("🔍 Data Collection")

if st.sidebar.button("🔍 Run Search Now", type="primary"):
    st.write("🔍 **Search button clicked!**")
    
    # Test API connections first
    st.write("### 🔧 Testing API Connections")
    
    try:
        # Test Tavily
        st.write("📡 Testing Tavily API...")
        from tavily import TavilyClient
        tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
        test_response = tavily_client.search(query="startup", max_results=1)
        st.success(f"✅ Tavily working! Sample result: {len(test_response.get('results', []))} items")
        
    except Exception as e:
        st.error(f"❌ Tavily failed: {str(e)}")
        st.stop()
    
    try:
        # Test OpenAI
        st.write("🧠 Testing OpenAI API...")
        import openai
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        st.success("✅ OpenAI key configured")
        
    except Exception as e:
        st.error(f"❌ OpenAI failed: {str(e)}")
    
    # Now run the actual search
    st.write("### 🔍 Running Full Search")
    
    try:
        with st.spinner("Searching across sources..."):
            # Manual simple search first
            st.write("📡 **Step 1:** Simple Tavily search...")
            
            simple_queries = [
                "India startup funding 2025",
                "Indian venture capital",
                "startup investment India"
            ]
            
            all_results = []
            for query in simple_queries:
                st.write(f"  🔍 Searching: '{query}'")
                try:
                    response = tavily_client.search(query=query, max_results=5)
                    results = response.get('results', [])
                    st.write(f"    📥 Found: {len(results)} results")
                    
                    # Convert to our format
                    for result in results:
                        all_results.append({
                            'title': result.get('title', 'No title'),
                            'content': result.get('content', 'No content'),
                            'url': result.get('url', ''),
                            'source': result.get('url', '').split('/')[2] if result.get('url') else 'Unknown',
                            'date_published': datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    st.write(f"    ❌ Query failed: {str(e)}")
            
            st.write(f"📊 **Total raw results:** {len(all_results)}")
            
            if all_results:
                # Show first result as example
                st.write("📋 **Sample result:**")
                st.json(all_results[0])
                
                # Try to analyze content
                st.write("🧠 **Step 2:** Analyzing content...")
                
                analyzed_results = []
                for i, result in enumerate(all_results[:3]):  # Just first 3 for testing
                    st.write(f"  🧠 Analyzing {i+1}/{min(3, len(all_results))}: {result['title'][:50]}...")
                    try:
                        analysis = analyzer.analyze_content(result)
                        analyzed_results.append(analysis)
                        st.write(f"    ✅ Score: {analysis.get('relevance_score', 'N/A')}")
                    except Exception as e:
                        st.write(f"    ❌ Analysis failed: {str(e)}")
                
                st.write(f"📊 **Analyzed results:** {len(analyzed_results)}")
                
                # Try to store in database
                st.write("💾 **Step 3:** Storing in database...")
                try:
                    stored_count = data_manager.store_content(analyzed_results)
                    st.success(f"✅ **SUCCESS!** Stored {stored_count} articles in database!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Database storage failed: {str(e)}")
                    
            else:
                st.warning("⚠️ **No results found from any search query!**")
                st.write("**Possible issues:**")
                st.write("- Tavily API rate limits")
                st.write("- Search queries too specific")
                st.write("- Network connectivity issues")
                
    except Exception as e:
        st.error(f"❌ **Overall search failed:** {str(e)}")
        st.write("**Full error details:**")
        st.exception(e)

# Search stats
search_stats = search_engine.get_search_stats()
st.sidebar.metric("🔍 Total Searches", search_stats.get('total_searches', 0))
st.sidebar.metric("📅 Last Search", search_stats.get('last_search', 'Never'))

# Filters
st.sidebar.subheader("🎯 Filters")

# Load data for filters
df = data_manager.get_content_feed()

if df is not None and not df.empty:
    # Date range filter
    min_date = df['date_published'].min().date() if 'date_published' in df.columns else datetime.now().date()
    max_date = df['date_published'].max().date() if 'date_published' in df.columns else datetime.now().date()
    
    date_range = st.sidebar.date_input(
        "📅 Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Sector filter
    sectors = df['sectors'].unique() if 'sectors' in df.columns else []
    selected_sectors = st.sidebar.multiselect(
        "🏢 Sectors",
        options=sectors,
        default=sectors
    )
    
    # VC firm filter
    vc_firms = df['vc_firm'].unique() if 'vc_firm' in df.columns else []
    selected_vcs = st.sidebar.multiselect(
        "💼 VC Firms",
        options=vc_firms,
        default=vc_firms
    )
    
    # Priority filter
    priorities = df['priority'].unique() if 'priority' in df.columns else []
    selected_priorities = st.sidebar.multiselect(
        "⭐ Priority",
        options=priorities,
        default=priorities
    )
    
    # Relevance score filter
    min_score = st.sidebar.slider(
        "📊 Min Relevance Score",
        min_value=0,
        max_value=100,
        value=0
    )
else:
    # Default values when no data
    date_range = (datetime.now().date(), datetime.now().date())
    selected_sectors = []
    selected_vcs = []
    selected_priorities = []
    min_score = 0

# Main content
st.title("🚀 India VC Intelligence Agent")
st.subheader("AI-powered venture capital intelligence for Indian startup ecosystem")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📰 Latest Content", "📊 Analytics", "🎯 Themes", "💡 Insights"])

with tab1:
    st.header("📰 Latest VC Content")
    
    # Apply filters to dataframe
    if df is not None and not df.empty:
        # Filter by date
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[df['date_published'].dt.date.between(start_date, end_date)]
        
        # Filter by sectors
        if selected_sectors:
            df = df[df['sectors'].isin(selected_sectors) | df['sectors'].str.contains('|'.join(selected_sectors), na=False)]
        
        # Filter by VC firms
        if selected_vcs:
            df = df[df['vc_firm'].isin(selected_vcs)]
        
        # Filter by priority
        if selected_priorities:
            df = df[df['priority'].isin(selected_priorities)]
        
        # Filter by relevance score
        df = df[df['relevance_score'] >= min_score]
        
        if not df.empty:
            # Sort by relevance score and date
            df = df.sort_values(['relevance_score', 'date_published'], ascending=[False, False])
            
            # Display content
            for idx, row in df.iterrows():
                with st.expander(f"⭐ {row['relevance_score']}/100 | {row['title']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Summary:** {row.get('summary', 'No summary available')}")
                        st.write(f"**Source:** {row['source']} | **Date:** {row['date_published'].strftime('%Y-%m-%d')}")
                        st.write(f"**Sector:** {row.get('sectors', 'N/A')} | **VC Firm:** {row.get('vc_firm', 'Unknown')}")
                        if row.get('insights'):
                            st.write(f"**Key Insights:** {row['insights']}")
                        st.write(f"[Read Full Article]({row['url']})")
                    
                    with col2:
                        st.metric("Relevance", f"{row['relevance_score']}/100")
                        st.write(f"**Priority:** {row.get('priority', 'N/A')}")
                        
                        # Feedback buttons
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("👍", key=f"up_{idx}"):
                                data_manager.record_feedback(row['url'], 'positive')
                                st.success("👍 Feedback recorded!")
                        with col_b:
                            if st.button("👎", key=f"down_{idx}"):
                                data_manager.record_feedback(row['url'], 'negative')
                                st.success("👎 Feedback recorded!")
        else:
            st.info("No content found. Try adjusting filters or running a search.")
    else:
        st.info("No content found. Try running a search or adjusting filters.")

with tab2:
    st.header("📊 Analytics Dashboard")
    
    if df is not None and not df.empty:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Articles", len(df))
        with col2:
            st.metric("Avg Relevance Score", f"{df['relevance_score'].mean():.1f}")
        with col3:
            st.metric("High Priority", len(df[df['priority'] == 'High']))
        with col4:
            st.metric("This Week", len(df[df['date_published'] >= datetime.now() - timedelta(days=7)]))
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Sector distribution
            if 'sectors' in df.columns:
                sector_counts = df['sectors'].value_counts()
                fig = px.pie(values=sector_counts.values, names=sector_counts.index, 
                           title="Content by Sector")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # VC firm coverage
            if 'vc_firm' in df.columns:
                vc_counts = df['vc_firm'].value_counts().head(10)
                fig = px.bar(x=vc_counts.values, y=vc_counts.index, 
                           orientation='h', title="Coverage by VC Firm")
                st.plotly_chart(fig, use_container_width=True)
        
        # Timeline
        if 'date_published' in df.columns:
            daily_counts = df.groupby(df['date_published'].dt.date).size().reset_index()
            daily_counts.columns = ['date', 'count']
            fig = px.line(daily_counts, x='date', y='count', title="Content Volume Over Time")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for analytics. Run a search to populate data.")

with tab3:
    st.header("🎯 Trending Themes")
    
    if df is not None and not df.empty:
        # Extract themes from content
        themes = analyzer.extract_themes(df['content'].tolist() if 'content' in df.columns else [])
        
        if themes:
            for theme, articles in themes.items():
                st.subheader(f"🔥 {theme.replace('_', ' ').title()}")
                st.write(f"Found in {len(articles)} articles")
                
                # Show sample articles for each theme
                for article in articles[:3]:  # Show top 3
                    st.write(f"• [{article['title']}]({article['url']})")
        else:
            st.info("No trending themes detected. Need more content for analysis.")
    else:
        st.info("No data available for theme analysis. Run a search to populate data.")

with tab4:
    st.header("💡 AI-Generated Insights")
    
    if df is not None and not df.empty:
        # Generate insights
        insights = analyzer.generate_insights(df)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🔥 Hot Topics")
            st.write(insights.get('hot_topics', 'No insights available'))
        
        with col2:
            st.subheader("📊 Market Sentiment")
            st.write(insights.get('sentiment', 'No sentiment data'))
        
        with col3:
            st.subheader("🔮 Predictions")
            st.write(insights.get('predictions', 'No predictions available'))
        
        # Additional analysis
        st.subheader("📈 Trend Analysis")
        
        if 'relevance_score' in df.columns:
            # Score distribution
            fig = px.histogram(df, x='relevance_score', bins=20, 
                             title="Relevance Score Distribution")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for insights. Run a search to populate data.")

# Footer
st.markdown("---")
st.markdown("🚀 **India VC Intelligence Agent** | Powered by AI | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
