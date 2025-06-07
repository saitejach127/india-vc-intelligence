import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import openai

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
st.sidebar.subheader("🔍 Intelligent Content Discovery")

if st.sidebar.button("🔍 Run Intelligent Search", type="primary"):
    st.write("🧠 **Starting Intelligent Two-Stage Search Process**")
    
    # Test API connections first
    st.write("### 🔧 Testing API Connections")
    
    try:
        # Test Tavily
        st.write("📡 Testing Tavily API...")
        from tavily import TavilyClient
        tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
        test_response = tavily_client.search(query="startup", max_results=1)
        st.success(f"✅ Tavily working! API responding correctly.")
        
    except Exception as e:
        st.error(f"❌ Tavily failed: {str(e)}")
        st.stop()
    
    try:
        # Test OpenAI
        st.write("🧠 Testing OpenAI API...")
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        st.success("✅ OpenAI configured for intelligent content analysis")
        
    except Exception as e:
        st.error(f"❌ OpenAI failed: {str(e)}")
        st.stop()
    
    # STAGE 1: BROAD SEARCH - Cast a Wide Net
    st.write("### 📡 Stage 1: Broad Content Discovery")
    st.write("*Casting a wide net to find all VC/startup content...*")
    
    # Broad search queries designed to capture maximum relevant content
    broad_queries = [
        # General VC/Startup ecosystem
        "venture capital India",
        "startup funding India", 
        "Indian startup ecosystem",
        "venture capital news India",
        "startup investment India",
        "Indian unicorn startup",
        "startup founder India",
        
        # Business strategy content
        "business strategy India startup",
        "scaling business India",
        "startup growth India",
        "business model India",
        "market expansion India",
        
        # Major VC firms (to capture their thought leadership)
        "Sequoia Capital India blog",
        "Peak XV Partners insights", 
        "Accel India articles",
        "Matrix Partners India",
        "Elevation Capital insights",
        "Lightspeed India blog",
        "Blume Ventures insights",
        "Kalaari Capital"
    ]
    
    all_raw_results = []
    
    try:
        with st.expander("🔍 **Stage 1 Progress** (Click to expand)", expanded=True):
            for i, query in enumerate(broad_queries):
                st.write(f"**Query {i+1}/{len(broad_queries)}:** '{query}'")
                try:
                    response = tavily_client.search(query=query, max_results=8)  # Get more results per query
                    results = response.get('results', [])
                    st.write(f"  📥 Raw results: **{len(results)}**")
                    
                    # Convert to our format
                    for result in results:
                        all_raw_results.append({
                            'title': result.get('title', 'No title'),
                            'content': result.get('content', 'No content'),
                            'url': result.get('url', ''),
                            'source': result.get('url', '').split('/')[2] if result.get('url') else 'Unknown',
                            'date_published': datetime.now().isoformat(),
                            'search_query': query
                        })
                        
                except Exception as e:
                    st.write(f"    ❌ Query failed: {str(e)}")
        
        st.success(f"📊 **Stage 1 Complete:** Found {len(all_raw_results)} total articles")
        
        # Remove duplicates based on URL
        unique_results = []
        seen_urls = set()
        for result in all_raw_results:
            if result['url'] not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result['url'])
        
        st.info(f"📋 **After deduplication:** {len(unique_results)} unique articles")
        
        if not unique_results:
            st.warning("⚠️ No content found in Stage 1. Check API limits or search terms.")
            st.stop()
        
        # STAGE 2: INTELLIGENT AI FILTERING
        st.write("### 🧠 Stage 2: AI-Powered Content Analysis")
        st.write("*Using GPT-4 to analyze each article for VC intelligence value...*")
        
        def ai_classify_content(article):
            """Use OpenAI to intelligently classify content relevance"""
            
            prompt = f"""
            Analyze this article for VC intelligence value. Score 0-100 based on how valuable it would be for a VC or startup founder.
            
            Title: {article['title']}
            Content: {article['content'][:1000]}
            Source: {article['source']}
            
            HIGH VALUE CONTENT (70-100 points):
            - Investment philosophies and strategies
            - Business building frameworks and methodologies
            - Market analysis and sector insights
            - Scaling and growth strategies
            - Founder guidance and lessons learned
            - Venture building approaches
            - Strategic thinking and decision-making
            - Industry predictions and trends
            
            MEDIUM VALUE CONTENT (40-69 points):
            - Company profiles with strategic insights
            - Funding rounds with strategic context
            - Market reports with actionable insights
            - Startup success/failure case studies
            
            LOW VALUE CONTENT (0-39 points):
            - Basic funding announcements without context
            - Product launches without strategic insights
            - Generic business news
            - Unrelated technology news
            - Event announcements
            
            Respond with only a JSON object:
            {{"score": X, "category": "investment_thesis|business_strategy|market_insights|thought_leadership|case_study", "reasoning": "brief explanation", "key_topics": ["topic1", "topic2"]}}
            """
            
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.2
                )
                
                # Parse JSON response
                content = response.choices[0].message.content.strip()
                # Remove any markdown formatting
                if content.startswith('```json'):
                    content = content[7:-3]
                elif content.startswith('```'):
                    content = content[3:-3]
                
                result = json.loads(content)
                return result
                
            except Exception as e:
                st.write(f"    ⚠️ AI analysis failed for article, using fallback: {str(e)[:50]}")
                # Fallback analysis
                text = f"{article['title']} {article['content']}".lower()
                high_value_keywords = [
                    'strategy', 'thesis', 'insights', 'framework', 'scaling', 
                    'growth', 'investment', 'analysis', 'trends', 'outlook'
                ]
                score = min(sum(15 for keyword in high_value_keywords if keyword in text), 85)
                return {"score": score, "category": "general", "reasoning": "fallback keyword analysis", "key_topics": []}
        
        # Process articles with AI analysis
        high_value_articles = []
        
        with st.expander("🧠 **Stage 2 Progress** (Click to expand)", expanded=True):
            progress_bar = st.progress(0)
            
            for i, article in enumerate(unique_results):
                progress_bar.progress((i + 1) / len(unique_results))
                
                st.write(f"**Analyzing {i+1}/{len(unique_results)}:** {article['title'][:60]}...")
                
                # Get AI classification
                classification = ai_classify_content(article)
                score = classification.get('score', 0)
                
                st.write(f"    🎯 **Score: {score}/100** | Category: {classification.get('category', 'unknown')}")
                if score >= 60:  # High-value threshold
                    st.write(f"    ✅ **ACCEPTED** - {classification.get('reasoning', 'No reason')}")
                    
                    # Add classification data to article
                    article['relevance_score'] = score
                    article['ai_category'] = classification.get('category', 'general')
                    article['ai_reasoning'] = classification.get('reasoning', '')
                    article['key_topics'] = classification.get('key_topics', [])
                    article['priority'] = 'High' if score >= 80 else 'Medium'
                    
                    high_value_articles.append(article)
                else:
                    st.write(f"    ❌ **REJECTED** - {classification.get('reasoning', 'Low relevance')}")
        
        st.success(f"🎯 **Stage 2 Complete:** {len(high_value_articles)} high-value articles identified")
        
        if high_value_articles:
            # Show sample of accepted articles
            st.write("### 📋 Sample High-Value Articles Found:")
            for i, article in enumerate(high_value_articles[:3]):
                st.write(f"**{i+1}.** {article['title']} (Score: {article['relevance_score']}/100)")
                st.write(f"   Category: {article['ai_category']} | Reasoning: {article['ai_reasoning']}")
                st.write("---")
            
            # Store in database
            st.write("### 💾 Stage 3: Storing High-Value Content")
            try:
                stored_count = data_manager.store_content(high_value_articles)
                st.success(f"✅ **SUCCESS!** Stored {stored_count} high-value articles in database!")
                
                # Show summary statistics
                categories = [article['ai_category'] for article in high_value_articles]
                avg_score = sum(article['relevance_score'] for article in high_value_articles) / len(high_value_articles)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Articles Stored", stored_count)
                with col2:
                    st.metric("Avg Quality Score", f"{avg_score:.1f}/100")
                with col3:
                    st.metric("Categories Found", len(set(categories)))
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Database storage failed: {str(e)}")
        else:
            st.warning("⚠️ No high-value articles found. Try adjusting the scoring threshold or search terms.")
            
    except Exception as e:
        st.error(f"❌ **Search process failed:** {str(e)}")
        st.exception(e)

# Search stats
search_stats = search_engine.get_search_stats()
st.sidebar.metric("🔍 Total Searches", search_stats.get('total_searches', 0))
st.sidebar.metric("📅 Last Search", search_stats.get('last_search', 'Never'))

# Filters
st.sidebar.subheader("🎯 Intelligent Filters")

# Load data for filters
df = data_manager.get_content_feed()

if df is not None and not df.empty:
    # AI Category filter (new!)
    ai_categories = df['ai_category'].unique() if 'ai_category' in df.columns else []
    selected_categories = st.sidebar.multiselect(
        "🧠 AI Categories",
        options=ai_categories,
        default=ai_categories,
        help="Categories determined by AI analysis"
    )
    
    # Quality Score filter (new!)
    if 'relevance_score' in df.columns:
        min_quality = st.sidebar.slider(
            "🎯 Minimum Quality Score",
            min_value=0,
            max_value=100,
            value=60,
            help="AI-determined content quality score"
        )
    else:
        min_quality = 0
    
    # Date range filter
    min_date = df['date_published'].min().date() if 'date_published' in df.columns else datetime.now().date()
    max_date = df['date_published'].max().date() if 'date_published' in df.columns else datetime.now().date()
    
    date_range = st.sidebar.date_input(
        "📅 Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Priority filter
    priorities = df['priority'].unique() if 'priority' in df.columns else []
    selected_priorities = st.sidebar.multiselect(
        "⭐ Priority",
        options=priorities,
        default=priorities
    )
else:
    selected_categories = []
    min_quality = 60
    date_range = (datetime.now().date(), datetime.now().date())
    selected_priorities = []

# Main content
st.title("🚀 India VC Intelligence Agent")
st.subheader("🧠 AI-powered venture capital intelligence with intelligent content discovery")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📰 Intelligent Feed", "📊 Analytics", "🎯 AI Categories", "💡 Insights"])

with tab1:
    st.header("📰 AI-Curated VC Content")
    
    # Apply filters to dataframe
    if df is not None and not df.empty:
        # Filter by AI categories
        if selected_categories:
            df = df[df['ai_category'].isin(selected_categories)] if 'ai_category' in df.columns else df
        
        # Filter by quality score
        if 'relevance_score' in df.columns:
            df = df[df['relevance_score'] >= min_quality]
        
        # Filter by date
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[df['date_published'].dt.date.between(start_date, end_date)]
        
        # Filter by priority
        if selected_priorities:
            df = df[df['priority'].isin(selected_priorities)]
        
        if not df.empty:
            # Sort by AI relevance score
            df = df.sort_values(['relevance_score', 'date_published'], ascending=[False, False])
            
            # Display content with AI insights
            for idx, row in df.iterrows():
                quality_emoji = "🔥" if row.get('relevance_score', 0) >= 80 else "⭐" if row.get('relevance_score', 0) >= 70 else "📄"
                
                with st.expander(f"{quality_emoji} {row.get('relevance_score', 'N/A')}/100 | {row['title']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if row.get('ai_reasoning'):
                            st.write(f"**🧠 AI Analysis:** {row['ai_reasoning']}")
                        
                        st.write(f"**Content:** {row.get('content', 'No content available')[:300]}...")
                        st.write(f"**Source:** {row['source']} | **Date:** {row['date_published'].strftime('%Y-%m-%d')}")
                        
                        if row.get('key_topics'):
                            topics = ', '.join(row['key_topics']) if isinstance(row['key_topics'], list) else str(row['key_topics'])
                            st.write(f"**🏷️ Key Topics:** {topics}")
                        
                        st.write(f"[📖 Read Full Article]({row['url']})")
                    
                    with col2:
                        st.metric("🎯 AI Quality Score", f"{row.get('relevance_score', 'N/A')}/100")
                        if row.get('ai_category'):
                            st.write(f"**🧠 Category:** {row['ai_category'].replace('_', ' ').title()}")
                        st.write(f"**⭐ Priority:** {row.get('priority', 'N/A')}")
                        
                        # Feedback buttons
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("👍", key=f"up_{idx}"):
                                data_manager.record_feedback(row['url'], 'positive')
                                st.success("👍 Training AI!")
                        with col_b:
                            if st.button("👎", key=f"down_{idx}"):
                                data_manager.record_feedback(row['url'], 'negative')
                                st.success("👎 Training AI!")
        else:
            st.info("No content matches your filters. Try adjusting the quality score or categories.")
    else:
        st.info("No content found. Run an intelligent search to discover high-value VC content.")

with tab2:
    st.header("📊 AI Analytics Dashboard")
    
    if df is not None and not df.empty:
        # Enhanced metrics with AI insights
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Articles", len(df))
        with col2:
            avg_quality = df['relevance_score'].mean() if 'relevance_score' in df.columns else 0
            st.metric("Avg AI Quality", f"{avg_quality:.1f}/100")
        with col3:
            high_quality = len(df[df['relevance_score'] >= 80]) if 'relevance_score' in df.columns else 0
            st.metric("High Quality (80+)", high_quality)
        with col4:
            categories = len(df['ai_category'].unique()) if 'ai_category' in df.columns else 0
            st.metric("AI Categories", categories)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # AI Category distribution
            if 'ai_category' in df.columns:
                category_counts = df['ai_category'].value_counts()
                fig = px.pie(values=category_counts.values, names=category_counts.index, 
                           title="Content by AI Category")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Quality score distribution
            if 'relevance_score' in df.columns:
                fig = px.histogram(df, x='relevance_score', bins=20, 
                                 title="AI Quality Score Distribution")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for analytics. Run an intelligent search to populate data.")

with tab3:
    st.header("🎯 AI Content Categories")
    
    if df is not None and not df.empty and 'ai_category' in df.columns:
        categories = df['ai_category'].unique()
        
        for category in categories:
            category_df = df[df['ai_category'] == category]
            avg_score = category_df['relevance_score'].mean()
            
            st.subheader(f"📁 {category.replace('_', ' ').title()}")
            st.write(f"**Articles:** {len(category_df)} | **Avg Quality:** {avg_score:.1f}/100")
            
            # Show top articles in this category
            top_articles = category_df.nlargest(3, 'relevance_score')
            for _, article in top_articles.iterrows():
                st.write(f"• **{article['title']}** ({article['relevance_score']}/100)")
            st.write("---")
    else:
        st.info("No categorized content available. Run an intelligent search first.")

with tab4:
    st.header("💡 AI-Generated Insights")
    
    if df is not None and not df.empty:
        # Generate insights from high-quality content
        insights = analyzer.generate_insights(df)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🔥 Trending Themes")
            st.write(insights.get('hot_topics', 'No insights available'))
        
        with col2:
            st.subheader("📊 Market Sentiment") 
            st.write(insights.get('sentiment', 'No sentiment data'))
        
        with col3:
            st.subheader("🔮 Strategic Predictions")
            st.write(insights.get('predictions', 'No predictions available'))
        
        # Show quality trend
        if 'relevance_score' in df.columns:
            st.subheader("📈 Content Quality Trends")
            daily_quality = df.groupby(df['date_published'].dt.date)['relevance_score'].mean().reset_index()
            daily_quality.columns = ['date', 'avg_quality']
            fig = px.line(daily_quality, x='date', y='avg_quality', title="Average Content Quality Over Time")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for insights. Run an intelligent search to populate data.")

# Footer
st.markdown("---")
st.markdown("🧠 **Intelligent VC Discovery** | Powered by AI Content Analysis | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
