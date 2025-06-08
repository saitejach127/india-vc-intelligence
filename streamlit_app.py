import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import requests
from urllib.parse import urlparse
import time
import sqlite3
import hashlib
import re
import os
import tempfile
from dataclasses import dataclass
from typing import List, Dict, Optional

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="India VC Intelligence Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Version check
st.success("✅ VERSION: Enhanced Google with AI Filtering v4.0 - FIXED DEPLOYMENT")

# Handle API imports with error checking
api_connected = False
openai = None
tavily_client = None

try:
    import openai
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    
    from tavily import TavilyClient
    tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
    api_connected = True
    st.success("✅ APIs Connected Successfully")
except ImportError as e:
    st.error(f"❌ Missing library: {e}. Install required packages.")
except KeyError as e:
    st.error(f"❌ Missing API key: {e}. Add to Streamlit secrets.")
except Exception as e:
    st.error(f"❌ API connection failed: {e}")

# Custom CSS for premium look
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
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
    .content-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .quality-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    .premium-badge { background: #FFD700; color: #000; }
    .high-badge { background: #28a745; color: white; }
    .medium-badge { background: #ffc107; color: #000; }
    .low-badge { background: #6c757d; color: white; }
    .paywall-badge { background: #dc3545; color: white; }
    .fresh-badge { background: #17a2b8; color: white; }
</style>
""", unsafe_allow_html=True)

# Version header
st.markdown("""
<div class="main-header">
    <h1>🚀 India VC Intelligence Pro v4.0</h1>
    <p>Enhanced Strategic Intelligence System - Google with AI Filtering Foundation</p>
</div>
""", unsafe_allow_html=True)

# Simple Article dataclass
@dataclass
class Article:
    id: str
    title: str
    content: str
    url: str
    domain: str
    source_quality: str
    published_date: str
    search_query: str
    search_category: str
    relevance_score: int
    ai_summary: str
    key_insights: str
    is_paywall: bool
    content_freshness: str
    user_rating: Optional[int] = None
    bookmark_count: int = 0
    view_count: int = 0
    created_at: str = None

# Simplified Database Manager
class DatabaseManager:
    def __init__(self):
        # Use a simple file in temp directory for Streamlit
        self.db_path = os.path.join(tempfile.gettempdir(), "vc_intelligence.db")
        self.init_database()
    
    def init_database(self):
        """Initialize simple SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple articles table - all TEXT fields to avoid type issues
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    url TEXT,
                    domain TEXT,
                    source_quality TEXT,
                    published_date TEXT,
                    search_query TEXT,
                    search_category TEXT,
                    relevance_score TEXT,
                    ai_summary TEXT,
                    key_insights TEXT,
                    is_paywall TEXT,
                    content_freshness TEXT,
                    user_rating TEXT,
                    bookmark_count TEXT,
                    view_count TEXT,
                    created_at TEXT
                )
            """)
            
            # Simple feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id TEXT,
                    rating TEXT,
                    feedback_text TEXT,
                    created_at TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"❌ Database initialization failed: {e}")
            return False
    
    def save_article(self, article: Article):
        """Save article with simple error handling"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert all values to strings to avoid type issues
            cursor.execute("""
                INSERT OR REPLACE INTO articles 
                (id, title, content, url, domain, source_quality, published_date,
                 search_query, search_category, relevance_score, ai_summary,
                 key_insights, is_paywall, content_freshness, user_rating,
                 bookmark_count, view_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(article.id),
                str(article.title)[:500],  # Limit length
                str(article.content)[:2000],  # Limit length
                str(article.url),
                str(article.domain),
                str(article.source_quality),
                str(article.published_date or ""),
                str(article.search_query)[:200],
                str(article.search_category),
                str(article.relevance_score),
                str(article.ai_summary or "")[:500],
                str(article.key_insights or "")[:500],
                str(article.is_paywall),
                str(article.content_freshness),
                str(article.user_rating or ""),
                str(article.bookmark_count),
                str(article.view_count),
                str(datetime.now().isoformat())
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"❌ Failed to save article: {e}")
            return False
    
    def get_articles(self, limit=None, filters=None):
        """Get articles with simple filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM articles ORDER BY relevance_score DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            return results
            
        except Exception as e:
            st.error(f"❌ Failed to get articles: {e}")
            return []
    
    def save_feedback(self, article_id, rating, feedback_text=""):
        """Save user feedback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO feedback (article_id, rating, feedback_text, created_at)
                VALUES (?, ?, ?, ?)
            """, (str(article_id), str(rating), str(feedback_text), str(datetime.now().isoformat())))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"❌ Failed to save feedback: {e}")
            return False
    
    def get_analytics(self):
        """Get basic analytics"""
        try:
            articles = self.get_articles()
            
            total_articles = len(articles)
            
            # Calculate high quality (score >= 70)
            high_quality = 0
            total_score = 0
            
            for article in articles:
                try:
                    score = int(article[9]) if article[9] and str(article[9]).isdigit() else 0
                    if score >= 70:
                        high_quality += 1
                    total_score += score
                except:
                    pass
            
            avg_score = (total_score / total_articles) if total_articles > 0 else 0
            
            # Today's articles (simplified)
            today_articles = min(total_articles, 3)  # Simplified for demo
            
            return {
                'total_articles': total_articles,
                'high_quality': high_quality,
                'today_articles': today_articles,
                'avg_score': round(avg_score, 1),
                'weekly_trend': [(datetime.now().strftime('%Y-%m-%d'), total_articles)]
            }
            
        except Exception as e:
            st.error(f"❌ Analytics error: {e}")
            return {
                'total_articles': 0,
                'high_quality': 0,
                'today_articles': 0,
                'avg_score': 0,
                'weekly_trend': []
            }

# Deduplication function
def deduplicate_results(results):
    """Remove duplicate articles based on URL"""
    seen_urls = set()
    unique_results = []
    
    for article in results:
        if article.url not in seen_urls:
            seen_urls.add(article.url)
            unique_results.append(article)
    
    return unique_results

# Content Analysis System
class ContentAnalyzer:
    def __init__(self):
        self.paywall_indicators = [
            'subscribe', 'premium', 'paid', 'membership', 'unlock',
            'register to read', 'sign up', 'free trial', 'paywall'
        ]
        
        self.quality_sources = {
            'premium': [
                'a16z.com', 'sequoiacap.com', 'accel.com', 'matrix.co.in',
                'elevationcapital.com', 'lightspeedindiapartners.com',
                'kalaari.com', 'nexusventurepartners.com', 'blume.vc'
            ],
            'high_quality': [
                'techcrunch.com', 'venturebeat.com', 'thenextweb.com',
                'inc42.com', 'yourstory.com', 'entrackr.com', 'vccircle.com',
                'forbes.com', 'bloomberg.com', 'reuters.com'
            ],
            'thought_leadership': [
                'medium.com', 'substack.com', 'linkedin.com', 'firstround.com',
                'nfx.com', 'greylock.com', 'bessemer.com'
            ]
        }
    
    def detect_paywall(self, content, url):
        """Simple paywall detection"""
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in self.paywall_indicators)
    
    def get_source_quality(self, domain):
        """Determine source quality"""
        for quality, domains in self.quality_sources.items():
            if any(d in domain for d in domains):
                return quality
        return 'standard'
    
    def assess_freshness(self, published_date, content):
        """Simple freshness assessment"""
        try:
            if published_date:
                # Try to parse date
                if '2024' in str(published_date) or '2025' in str(published_date):
                    return 'fresh'
                elif '2023' in str(published_date):
                    return 'recent'
                else:
                    return 'stale'
            else:
                # Check content for year indicators
                current_year = datetime.now().year
                if str(current_year) in content or str(current_year-1) in content:
                    return 'recent'
                else:
                    return 'unknown'
        except:
            return 'unknown'
    
    def simple_scoring(self, article_data):
        """Simple scoring when AI is not available"""
        text = f"{article_data['title']} {article_data['content']}".lower()
        
        score = 0
        
        # Strategic keywords scoring
        strategic_keywords = {
            'investment': 10, 'thesis': 15, 'strategy': 12, 'framework': 10,
            'scaling': 12, 'growth': 8, 'market': 8, 'venture': 8,
            'startup': 5, 'founder': 5, 'portfolio': 10, 'due diligence': 15
        }
        
        for keyword, points in strategic_keywords.items():
            if keyword in text:
                score += points
        
        # Source quality bonus
        if article_data['source_quality'] == 'premium':
            score += 25
        elif article_data['source_quality'] == 'high_quality':
            score += 15
        elif article_data['source_quality'] == 'thought_leadership':
            score += 10
        
        # Freshness modifier
        if article_data['content_freshness'] == 'fresh':
            score += 15
        elif article_data['content_freshness'] == 'recent':
            score += 10
        elif article_data['content_freshness'] == 'stale':
            score -= 20
        
        # Paywall penalty
        if article_data.get('is_paywall'):
            score -= 10
        
        return {
            'score': max(0, min(score, 100)),
            'category': 'general_intelligence',
            'strategic_value': 'Keyword-based analysis - review manually for strategic value',
            'key_insights': 'Manual review recommended for detailed insights',
            'confidence': 'medium',
            'reasoning': f'Score based on strategic keywords and source quality'
        }
    
    def enhanced_ai_analysis(self, article_data):
        """Enhanced AI analysis with fallback"""
        if not api_connected or not openai:
            return self.simple_scoring(article_data)
        
        prompt = f"""
        STRATEGIC VC INTELLIGENCE ANALYSIS

        Article: {article_data['title']}
        Content: {article_data['content'][:1000]}
        Source: {article_data['domain']} ({article_data['source_quality']})
        Freshness: {article_data['content_freshness']}

        Score this content 0-100 for strategic VC value:
        - 85-100: Investment thesis, strategic frameworks, market predictions
        - 70-84: Business methodologies, growth strategies, sector insights  
        - 55-69: Case studies, market reports, general strategy
        - 0-54: Basic news, generic advice, product launches

        Provide JSON response:
        {{
            "score": [0-100],
            "category": "investment_thesis|scaling_strategy|market_analysis|thought_leadership",
            "strategic_value": "why this matters to VCs/founders",
            "key_insights": "3-5 actionable takeaways",
            "confidence": "high|medium|low"
        }}
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            result = json.loads(content)
            
            # Apply source and freshness modifiers
            base_score = result.get('score', 0)
            
            if article_data['source_quality'] == 'premium':
                base_score += 15
            elif article_data['source_quality'] == 'thought_leadership':
                base_score += 8
            
            if article_data['content_freshness'] == 'stale':
                base_score -= 20
            elif article_data['content_freshness'] == 'fresh':
                base_score += 10
            
            if article_data.get('is_paywall'):
                base_score -= 10
            
            result['score'] = max(0, min(base_score, 100))
            return result
            
        except Exception as e:
            st.warning(f"AI analysis failed: {str(e)}, using fallback scoring")
            return self.simple_scoring(article_data)

# Search System
class EnhancedSearchSystem:
    def __init__(self):
        self.strategic_queries = [
            # INVESTMENT THESIS & FRAMEWORKS
            "venture capital investment thesis India 2024",
            "VC investment framework methodology",
            "startup investment philosophy India",
            "venture capital decision making process",
            "VC due diligence framework India",
            "investment strategy fintech India 2024",
            "SaaS investment thesis India",
            "B2B investment framework India",
            
            # CURRENT THOUGHT LEADERS & VCs
            "Shailendra Singh Sequoia India insights 2024",
            "Ravi Adusumalli Elevation Capital strategy",
            "Prashanth Prakash Accel Partners India",
            "Avnish Bajaj Matrix Partners insights",
            "Bejul Somaia Lightspeed Venture Partners",
            "Vani Kola Kalaari Capital portfolio strategy",
            "Karthik Reddy Blume Ventures thesis",
            "Mukul Arora Elevation Capital insights",
            
            # SECTOR-SPECIFIC INTELLIGENCE (2024 FOCUS)
            "fintech investment trends India 2024",
            "SaaS startup scaling India 2024", 
            "B2B marketplace strategy India 2024",
            "edtech investment outlook India 2024",
            "healthtech venture capital India 2024",
            "enterprise software VC India 2024",
            "AI startup investment India 2024",
            "climate tech VC India 2024",
            
            # SCALING & OPERATIONAL EXCELLENCE
            "startup scaling playbook India 2024",
            "venture capital operational support",
            "startup go-to-market strategy India",
            "product market fit framework India",
            "startup hiring strategy India 2024",
            "venture building methodology",
            "startup unit economics framework",
            "customer acquisition strategy India",
            
            # MARKET DYNAMICS & TRENDS
            "Indian startup ecosystem 2024",
            "venture capital market trends India",
            "startup valuation trends India 2024",
            "IPO readiness Indian startups",
            "venture capital exits India 2024",
            "startup funding patterns India 2024",
            "growth stage investing India",
            "late stage VC India 2024",
            
            # CONTRARIAN & EMERGING THEMES
            "contrarian venture capital views India",
            "emerging technology VC India 2024",
            "deep tech venture capital India",
            "space tech investment India",
            "Web3 crypto VC India 2024",
            "sustainable technology VC India",
            "rural market VC India 2024",
            "tier 2 city startups India"
        ]
    
    def execute_search(self, max_queries=20):
        """Execute enhanced search with progress tracking"""
        if not api_connected or not tavily_client:
            st.error("❌ Search requires API access")
            return []
        
        all_results = []
        queries_to_run = self.strategic_queries[:max_queries]
        
        progress_container = st.container()
        with progress_container:
            st.write("### 🔍 Enhanced Strategic Intelligence Discovery")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, query in enumerate(queries_to_run):
                progress = (i + 1) / len(queries_to_run)
                progress_bar.progress(progress)
                status_text.text(f"Searching: {query[:50]}...")
                
                try:
                    # Search with Tavily
                    response = tavily_client.search(
                        query=query,
                        max_results=3,
                        days=180  # Last 6 months
                    )
                    
                    results = response.get('results', [])
                    
                    for result in results:
                        url = result.get('url', '')
                        domain = urlparse(url).netloc if url else 'Unknown'
                        content = result.get('content', '')
                        title = result.get('title', 'No title')
                        
                        # Skip if content too short
                        if len(content) < 100 or not title:
                            continue
                        
                        # Create unique ID
                        article_id = hashlib.md5(url.encode()).hexdigest()
                        
                        # Analyze content
                        source_quality = analyzer.get_source_quality(domain)
                        is_paywall = analyzer.detect_paywall(content, url)
                        published_date = result.get('published_date', '')
                        content_freshness = analyzer.assess_freshness(published_date, content)
                        
                        # Create article data for analysis
                        article_data = {
                            'id': article_id,
                            'title': title,
                            'content': content,
                            'url': url,
                            'domain': domain,
                            'source_quality': source_quality,
                            'published_date': published_date,
                            'search_query': query,
                            'content_freshness': content_freshness,
                            'is_paywall': is_paywall
                        }
                        
                        # Get AI analysis
                        ai_analysis = analyzer.enhanced_ai_analysis(article_data)
                        
                        # Create article object
                        article = Article(
                            id=article_id,
                            title=title,
                            content=content,
                            url=url,
                            domain=domain,
                            source_quality=source_quality,
                            published_date=published_date or "",
                            search_query=query,
                            search_category=ai_analysis.get('category', 'general'),
                            relevance_score=ai_analysis.get('score', 0),
                            ai_summary=ai_analysis.get('strategic_value', '') or "",
                            key_insights=ai_analysis.get('key_insights', '') or "",
                            is_paywall=is_paywall,
                            content_freshness=content_freshness,
                            user_rating=None,
                            bookmark_count=0,
                            view_count=0,
                            created_at=datetime.now().isoformat()
                        )
                        
                        all_results.append(article)
                        
                except Exception as e:
                    st.error(f"Query failed: {query[:30]}... - {str(e)}")
                
                # Small delay to avoid rate limits
                time.sleep(0.5)
        
        progress_container.empty()
        return all_results

# Initialize database
@st.cache_resource
def get_database():
    return DatabaseManager()

# Initialize components
try:
    db = get_database()
    analyzer = ContentAnalyzer()
    search_system = EnhancedSearchSystem()
    st.success("✅ All systems initialized successfully")
except Exception as e:
    st.error(f"❌ System initialization failed: {e}")
    db = None

# Sidebar Filters
st.sidebar.markdown("## 🔍 Intelligence Filters")

# Basic filters
min_score = st.sidebar.slider("🎯 Minimum Relevance Score", 0, 100, 55)
fresh_only = st.sidebar.checkbox("🔥 Fresh Content Only", value=False)
no_paywall = st.sidebar.checkbox("🚫 Exclude Paywall Content", value=True)

# Main Dashboard
if db:
    analytics = db.get_analytics()
else:
    analytics = {'total_articles': 0, 'high_quality': 0, 'today_articles': 0, 'avg_score': 0, 'weekly_trend': []}

# Metrics Dashboard
st.markdown("## 📊 Real-time Intelligence Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>📄 Total Articles</h3>
        <h2>{analytics['total_articles']:,}</h2>
        <p>Strategic content database</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🎯 High Quality</h3>
        <h2>{analytics['high_quality']}</h2>
        <p>Score ≥70 articles</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🔥 Today</h3>
        <h2>{analytics['today_articles']}</h2>
        <p>New discoveries</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>⭐ Avg Score</h3>
        <h2>{analytics['avg_score']}/100</h2>
        <p>Content quality</p>
    </div>
    """, unsafe_allow_html=True)

# Main Interface Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Discovery Engine", "📋 Content Library", "⚙️ System Status"])

with tab1:
    st.markdown("### 🚀 Strategic Content Discovery Engine")
    
    st.info("**🧠 Enhanced Search:** 48 strategic queries • AI analysis • Quality scoring • Database storage")
    
    if st.button("🚀 **EXECUTE ENHANCED DISCOVERY**", type="primary", use_container_width=True):
        if not api_connected:
            st.error("❌ Cannot search without API access. Please configure API keys.")
        else:
            with st.spinner("🔍 Discovering strategic intelligence..."):
                # Execute search
                search_results = search_system.execute_search(max_queries=15)  # Limited for testing
                
                if search_results:
                    # Filter results
                    filtered_results = []
                    for article in search_results:
                        # Apply filters
                        if article.relevance_score < min_score:
                            continue
                        if no_paywall and article.is_paywall:
                            continue
                        if fresh_only and article.content_freshness in ['stale', 'unknown']:
                            continue
                        
                        filtered_results.append(article)
                    
                    # Remove duplicates by URL
                    final_results = deduplicate_results(filtered_results)
                    final_results.sort(key=lambda x: x.relevance_score, reverse=True)
                    
                    # Save to database
                    saved_count = 0
                    if db:
                        for article in final_results:
                            if db.save_article(article):
                                saved_count += 1
                    
                    # Display results
                    st.success(f"🎯 **Discovery Complete!** Found {len(final_results)} strategic articles, saved {saved_count} to database")
                    
                    # Show results
                    st.markdown("### 🏆 Strategic Content Discovered")
                    
                    for i, article in enumerate(final_results[:10]):  # Show top 10
                        # Quality badges
                        quality_badge = ""
                        if article.source_quality == 'premium':
                            quality_badge = '<span class="quality-badge premium-badge">Premium VC</span>'
                        elif article.source_quality == 'high_quality':
                            quality_badge = '<span class="quality-badge high-badge">High Quality</span>'
                        
                        freshness_badge = ""
                        if article.content_freshness == 'fresh':
                            freshness_badge = '<span class="quality-badge fresh-badge">Fresh</span>'
                        
                        paywall_badge = ""
                        if article.is_paywall:
                            paywall_badge = '<span class="quality-badge paywall-badge">Paywall</span>'
                        
                        score_color = "high-badge" if article.relevance_score >= 70 else "medium-badge"
                        
                        st.markdown(f"""
                        <div class="content-card">
                            <h4>{i+1}. {article.title}</h4>
                            <p><strong>🎯 Strategic Value:</strong> {article.ai_summary}</p>
                            <p><strong>💡 Key Insights:</strong> {article.key_insights}</p>
                            <p>
                                <span class="quality-badge {score_color}">Score: {article.relevance_score}/100</span>
                                {quality_badge}
                                {freshness_badge}
                                {paywall_badge}
                            </p>
                            <p><strong>📂 Category:</strong> {article.search_category.replace('_', ' ').title()} | <strong>🌐 Source:</strong> {article.domain}</p>
                            <p><a href="{article.url}" target="_blank">🔗 Read Full Article</a></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Simple feedback
                        col_fb1, col_fb2 = st.columns(2)
                        
                        with col_fb1:
                            if st.button(f"👍 Helpful", key=f"like_{article.id}"):
                                if db and db.save_feedback(article.id, 5, "Helpful content"):
                                    st.success("✅ Feedback saved!")
                        
                        with col_
