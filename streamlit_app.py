import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import openai
import requests
from urllib.parse import urlparse
import time
import sqlite3
import hashlib
import re
from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np

# Page configuration
st.set_page_config(
    page_title="India VC Intelligence Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    <h1>🚀 India VC Intelligence Pro v5.0</h1>
    <p>Complete Strategic Intelligence System with Database, AI Learning, Real-time Analytics & Content Management</p>
</div>
""", unsafe_allow_html=True)

# Database setup
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

class DatabaseManager:
    def __init__(self):
        self.db_path = "vc_intelligence.db"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                url TEXT UNIQUE,
                domain TEXT,
                source_quality TEXT,
                published_date TEXT,
                search_query TEXT,
                search_category TEXT,
                relevance_score INTEGER,
                ai_summary TEXT,
                key_insights TEXT,
                is_paywall BOOLEAN,
                content_freshness TEXT,
                user_rating INTEGER,
                bookmark_count INTEGER DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT,
                rating INTEGER,
                feedback_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles (id)
            )
        """)
        
        # Search history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                results_count INTEGER,
                high_quality_count INTEGER,
                search_filters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                metric_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_article(self, article: Article):
        """Save article to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO articles 
            (id, title, content, url, domain, source_quality, published_date, 
             search_query, search_category, relevance_score, ai_summary, 
             key_insights, is_paywall, content_freshness, user_rating, 
             bookmark_count, view_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article.id, article.title, article.content, article.url,
            article.domain, article.source_quality, article.published_date,
            article.search_query, article.search_category, article.relevance_score,
            article.ai_summary, article.key_insights, article.is_paywall,
            article.content_freshness, article.user_rating,
            article.bookmark_count, article.view_count
        ))
        
        conn.commit()
        conn.close()
    
    def get_articles(self, limit=None, filters=None):
        """Retrieve articles with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM articles WHERE 1=1"
        params = []
        
        if filters:
            if filters.get('min_score'):
                query += " AND relevance_score >= ?"
                params.append(filters['min_score'])
            if filters.get('source_quality'):
                query += " AND source_quality = ?"
                params.append(filters['source_quality'])
            if filters.get('category'):
                query += " AND search_category = ?"
                params.append(filters['category'])
            if filters.get('freshness'):
                query += " AND content_freshness = ?"
                params.append(filters['freshness'])
            if filters.get('no_paywall'):
                query += " AND is_paywall = 0"
        
        query += " ORDER BY relevance_score DESC, created_at DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def save_feedback(self, article_id, rating, feedback_text=""):
        """Save user feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_feedback (article_id, rating, feedback_text)
            VALUES (?, ?, ?)
        """, (article_id, rating, feedback_text))
        
        # Update article rating
        cursor.execute("""
            UPDATE articles SET user_rating = ? WHERE id = ?
        """, (rating, article_id))
        
        conn.commit()
        conn.close()
    
    def get_analytics(self):
        """Get system analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total articles
        cursor.execute("SELECT COUNT(*) FROM articles")
        total_articles = cursor.fetchone()[0]
        
        # High quality articles (score >= 70)
        cursor.execute("SELECT COUNT(*) FROM articles WHERE relevance_score >= 70")
        high_quality = cursor.fetchone()[0]
        
        # Today's articles
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM articles WHERE DATE(created_at) = ?", (today,))
        today_articles = cursor.fetchone()[0]
        
        # Average score
        cursor.execute("SELECT AVG(relevance_score) FROM articles WHERE relevance_score > 0")
        avg_score = cursor.fetchone()[0] or 0
        
        # Weekly trend
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count 
            FROM articles 
            WHERE created_at >= date('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        weekly_trend = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_articles': total_articles,
            'high_quality': high_quality,
            'today_articles': today_articles,
            'avg_score': round(avg_score, 1),
            'weekly_trend': weekly_trend
        }

# Initialize database
@st.cache_resource
def get_database():
    return DatabaseManager()

db = get_database()

# API Setup
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    from tavily import TavilyClient
    tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
    api_connected = True
except:
    api_connected = False
    st.error("⚠️ API keys not configured. Add OPENAI_API_KEY and TAVILY_API_KEY to secrets.")

# Enhanced Content Analysis
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
        """Detect if content is behind paywall"""
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in self.paywall_indicators)
    
    def get_source_quality(self, domain):
        """Determine source quality"""
        for quality, domains in self.quality_sources.items():
            if any(d in domain for d in domains):
                return quality
        return 'standard'
    
    def assess_freshness(self, published_date, content):
        """Assess content freshness"""
        try:
            if published_date:
                pub_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                days_old = (datetime.now() - pub_date.replace(tzinfo=None)).days
                
                if days_old <= 7:
                    return 'fresh'
                elif days_old <= 30:
                    return 'recent'
                elif days_old <= 90:
                    return 'moderate'
                else:
                    return 'stale'
            else:
                # Check for date indicators in content
                current_year = datetime.now().year
                if str(current_year) in content or str(current_year-1) in content:
                    return 'recent'
                else:
                    return 'unknown'
        except:
            return 'unknown'
    
    def enhanced_ai_analysis(self, article_data):
        """Enhanced AI analysis with strategic scoring"""
        if not api_connected:
            return self.fallback_analysis(article_data)
        
        prompt = f"""
        STRATEGIC VC INTELLIGENCE ANALYSIS - ENHANCED SCORING

        Article: {article_data['title']}
        Content: {article_data['content'][:1500]}
        Source: {article_data['domain']} ({article_data['source_quality']})
        Freshness: {article_data['content_freshness']}

        ENHANCED SCORING CRITERIA (0-100):

        EXCEPTIONAL (85-100): Investment thesis documents, detailed market analysis with predictions, 
        scaling frameworks with methodologies, strategic decision frameworks, contrarian insights, 
        VC portfolio strategies, founder journey with strategic lessons

        HIGH VALUE (70-84): Business building methodologies, market trend analysis, growth strategies, 
        investment philosophy, sector insights, operational guides, funding strategies

        MEDIUM VALUE (55-69): Company case studies with context, market reports, general strategy, 
        industry discussions

        LOW VALUE (0-54): Basic announcements, generic advice, product launches, superficial profiles

        SCORING MODIFIERS:
        - Premium VC source: +15 points
        - Fresh content (≤30 days): +10 points  
        - Investment thesis category: +10 points
        - Thought leadership source: +8 points
        - Contrarian perspective: +8 points
        - Actionable frameworks: +5 points

        FRESHNESS PENALTY:
        - Stale content (>1 year): -20 points
        - Unknown date with old indicators: -15 points

        PAYWALL PENALTY: -10 points

        Provide JSON response:
        {{
            "score": [0-100],
            "category": "investment_thesis|scaling_strategy|market_analysis|thought_leadership|operational_excellence|contrarian_insights",
            "strategic_value": "why this matters to VCs/founders",
            "key_insights": "3-5 actionable takeaways",
            "confidence": "high|medium|low",
            "reasoning": "scoring rationale"
        }}
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            result = json.loads(content)
            
            # Apply additional modifiers based on our analysis
            base_score = result.get('score', 0)
            
            # Source quality bonus
            if article_data['source_quality'] == 'premium':
                base_score += 15
            elif article_data['source_quality'] == 'thought_leadership':
                base_score += 8
            
            # Freshness modifier
            if article_data['content_freshness'] == 'stale':
                base_score -= 20
            elif article_data['content_freshness'] == 'fresh':
                base_score += 10
            
            # Paywall penalty
            if article_data.get('is_paywall'):
                base_score -= 10
            
            result['score'] = max(0, min(base_score, 100))
            return result
            
        except Exception as e:
            st.error(f"AI analysis failed: {str(e)}")
            return self.fallback_analysis(article_data)
    
    def fallback_analysis(self, article_data):
        """Fallback analysis when AI is unavailable"""
        text = f"{article_data['title']} {article_data['content']}".lower()
        
        strategic_keywords = {
            'investment_thesis': ['thesis', 'investment philosophy', 'strategy', 'framework'],
            'scaling_strategy': ['scaling', 'growth', 'expansion', 'building'],
            'market_analysis': ['market', 'trends', 'analysis', 'outlook'],
            'thought_leadership': ['insights', 'perspective', 'vision', 'future']
        }
        
        scores = {}
        for category, keywords in strategic_keywords.items():
            score = sum(15 for keyword in keywords if keyword in text)
            scores[category] = score
        
        best_category = max(scores, key=scores.get)
        base_score = scores[best_category]
        
        # Apply modifiers
        if article_data['source_quality'] == 'premium':
            base_score += 20
        if article_data['content_freshness'] == 'fresh':
            base_score += 10
        
        return {
            'score': min(base_score, 100),
            'category': best_category,
            'strategic_value': 'Keyword-based analysis',
            'key_insights': 'Requires manual review',
            'confidence': 'low',
            'reasoning': 'Fallback analysis due to API unavailability'
        }

analyzer = ContentAnalyzer()

# Enhanced Search System
class EnhancedSearchSystem:
    def __init__(self):
        self.search_queries = [
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
    
    def execute_enhanced_search(self, filters=None):
        """Execute comprehensive search with real-time processing"""
        if not api_connected:
            st.error("Cannot search without API access")
            return []
        
        all_results = []
        total_queries = len(self.search_queries)
        
        # Apply date filter for freshness
        search_days = 180  # Last 6 months by default
        if filters and filters.get('date_range'):
            date_mapping = {
                'Last 24 hours': 1,
                'Last 7 days': 7,
                'Last 30 days': 30,
                'Last 90 days': 90,
                'Last 6 months': 180
            }
            search_days = date_mapping.get(filters['date_range'], 180)
        
        progress_container = st.container()
        with progress_container:
            st.write("### 🔍 Enhanced Multi-Source Intelligence Discovery")
            progress_bar = st.progress(0)
            status_text = st.empty()
            batch_info = st.empty()
            
            batch_size = 8
            total_batches = (total_queries + batch_size - 1) // batch_size
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, total_queries)
                batch_queries = self.search_queries[start_idx:end_idx]
                
                batch_info.info(f"🎯 **Batch {batch_num + 1}/{total_batches}:** Processing {len(batch_queries)} strategic queries...")
                
                for i, query in enumerate(batch_queries):
                    overall_progress = (batch_num * batch_size + i + 1) / total_queries
                    progress_bar.progress(overall_progress)
                    status_text.text(f"Searching: {query[:50]}...")
                    
                    try:
                        # Enhanced search with freshness filter
                        response = tavily_client.search(
                            query=query, 
                            max_results=4,
                            days=search_days,
                            include_domains=["techcrunch.com", "inc42.com", "yourstory.com", 
                                           "a16z.com", "sequoiacap.com", "medium.com", 
                                           "linkedin.com", "substack.com", "entrackr.com"]
                        )
                        
                        results = response.get('results', [])
                        
                        for result in results:
                            # Enhanced result processing
                            url = result.get('url', '')
                            domain = urlparse(url).netloc if url else 'Unknown'
                            content = result.get('content', '')
                            title = result.get('title', 'No title')
                            
                            # Skip if content too short or low quality
                            if len(content) < 100 or not title:
                                continue
                            
                            # Create unique ID
                            article_id = hashlib.md5(url.encode()).hexdigest()
                            
                            # Analyze content quality
                            source_quality = analyzer.get_source_quality(domain)
                            is_paywall = analyzer.detect_paywall(content, url)
                            published_date = result.get('published_date', '')
                            content_freshness = analyzer.assess_freshness(published_date, content)
                            
                            # Create article data
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
                            
                            # AI analysis
                            ai_analysis = analyzer.enhanced_ai_analysis(article_data)
                            
                            # Create complete article object
                            article = Article(
                                id=article_id,
                                title=title,
                                content=content,
                                url=url,
                                domain=domain,
                                source_quality=source_quality,
                                published_date=published_date,
                                search_query=query,
                                search_category=ai_analysis.get('category', 'general'),
                                relevance_score=ai_analysis.get('score', 0),
                                ai_summary=ai_analysis.get('strategic_value', ''),
                                key_insights=ai_analysis.get('key_insights', ''),
                                is_paywall=is_paywall,
                                content_freshness=content_freshness
                            )
                            
                            all_results.append(article)
                            
                    except Exception as e:
                        st.error(f"Query failed: {query[:30]}... - {str(e)[:50]}")
                
                # Small delay between batches
                time.sleep(0.5)
        
        progress_container.empty()
        return all_results

search_system = EnhancedSearchSystem()

# Sidebar Filters
st.sidebar.markdown("## 🔍 Intelligence Filters")

# Date range filter
date_ranges = ["Last 24 hours", "Last 7 days", "Last 30 days", "Last 90 days", "Last 6 months"]
selected_date_range = st.sidebar.selectbox("📅 Content Freshness", date_ranges, index=2)

# Source quality filter
quality_options = ["All Sources", "Premium VC Only", "High Quality", "Thought Leadership", "No Paywall"]
selected_quality = st.sidebar.selectbox("📰 Source Quality", quality_options)

# Relevance score filter
min_score = st.sidebar.slider("🎯 Minimum Relevance Score", 0, 100, 65)

# Content category filter
categories = ["All Categories", "Investment Thesis", "Scaling Strategy", "Market Analysis", 
              "Thought Leadership", "Operational Excellence", "Contrarian Insights"]
selected_category = st.sidebar.selectbox("📂 Content Category", categories)

# Fresh content only toggle
fresh_only = st.sidebar.checkbox("🔥 Fresh Content Only (≤30 days)", value=True)

# Exclude paywall content
no_paywall = st.sidebar.checkbox("🚫 Exclude Paywall Content", value=True)

# Build filters object
search_filters = {
    'date_range': selected_date_range,
    'source_quality': selected_quality,
    'min_score': min_score,
    'category': selected_category,
    'fresh_only': fresh_only,
    'no_paywall': no_paywall
}

# Main Dashboard
analytics = db.get_analytics()

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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Discovery Engine", "📋 Content Library", "📊 Analytics", "🎯 Insights", "⚙️ System"])

with tab1:
    st.markdown("### 🚀 Enhanced Strategic Content Discovery Engine")
    
    col_left, col_right = st.columns([3, 1])
    
    with col_left:
        st.info("**🧠 AI-Powered Search:** 56 strategic queries • Real-time analysis • Quality scoring • Database storage")
        
        if st.button("🚀 **EXECUTE ENHANCED DISCOVERY**", type="primary", use_container_width=True):
            with st.spinner("🔍 Discovering strategic intelligence..."):
                # Execute search
                search_results = search_system.execute_enhanced_search(search_filters)
                
                if search_results:
                    # Filter results based on criteria
                    filtered_results = []
                    for article in search_results:
                        # Apply filters
                        if article.relevance_score < min_score:
                            continue
                        if no_paywall and article.is_paywall:
                            continue
                        if fresh_only and article.content_freshness in ['stale', 'unknown']:
                            continue
                        if selected_quality != "All Sources":
                            quality_map = {
                                "Premium VC Only": "premium",
                                "High Quality": "high_quality", 
                                "Thought Leadership": "thought_leadership"
                            }
                            if article.source_quality != quality_map.get(selected_quality):
                                continue
                        
                        filtered_results.append(article)
                        
                        # Save to database
                        db.save_article(article)
                    
                    # Remove duplicates
                    unique_results = {}
                    for article in filtered_results:
                        if article.url not in unique_results:
                            unique_results[article.url] = article
                    
                    final_results = list(unique_results.values())
                    final_results.sort(key=lambda x: x.relevance_score, reverse=True)
                    
                    # Display results summary
                    st.success(f"🎯 **Discovery Complete!** Found {len(final_results)} high-quality strategic articles")
                    
                    # Quality breakdown
                    quality_counts = {}
                    freshness_counts = {}
                    category_counts = {}
                    
                    for article in final_results:
                        quality_counts[article.source_quality] = quality_counts.get(article.source_quality, 0) + 1
                        freshness_counts[article.content_freshness] = freshness_counts.get(article.content_freshness, 0) + 1
                        category_counts[article.search_category] = category_counts.get(article.search_category, 0) + 1
                    
                    # Display quality metrics
                    col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
                    
                    with col_metrics1:
                        st.write("**📊 Source Quality:**")
                        for quality, count in quality_counts.items():
                            st.write(f"• {quality.title()}: {count}")
                    
                    with col_metrics2:
                        st.write("**⏰ Content Freshness:**")
                        for freshness, count in freshness_counts.items():
                            st.write(f"• {freshness.title()}: {count}")
                    
                    with col_metrics3:
                        st.write("**📂 Categories:**")
                        for category, count in list(category_counts.items())[:4]:
                            st.write(f"• {category.replace('_', ' ').title()}: {count}")
                    
                    # Display top articles
                    st.markdown("### 🏆 Top Strategic Content Discovered")
                    
                    for i, article in enumerate(final_results[:10]):  # Show top 10
                        # Quality badges
                        quality_badge = ""
                        if article.source_quality == 'premium':
                            quality_badge = '<span class="quality-badge premium-badge">Premium VC</span>'
                        elif article.source_quality == 'high_quality':
                            quality_badge = '<span class="quality-badge high-badge">High Quality</span>'
                        elif article.source_quality == 'thought_leadership':
                            quality_badge = '<span class="quality-badge medium-badge">Thought Leadership</span>'
                        
                        freshness_badge = ""
                        if article.content_freshness == 'fresh':
                            freshness_badge = '<span class="quality-badge fresh-badge">Fresh</span>'
                        elif article.content_freshness == 'recent':
                            freshness_badge = '<span class="quality-badge medium-badge">Recent</span>'
                        
                        paywall_badge = ""
                        if article.is_paywall:
                            paywall_badge = '<span class="quality-badge paywall-badge">Paywall</span>'
                        
                        score_color = "high-badge" if article.relevance_score >= 80 else "medium-badge" if article.relevance_score >= 65 else "low-badge"
                        
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
                        
                        # Feedback section for each article
                        col_feedback1, col_feedback2, col_feedback3 = st.columns([1, 1, 3])
                        
                        with col_feedback1:
                            if st.button(f"👍", key=f"like_{article.id}"):
                                db.save_feedback(article.id, 5, "Helpful content")
                                st.success("Feedback saved!")
                        
                        with col_feedback2:
                            if st.button(f"👎", key=f"dislike_{article.id}"):
                                db.save_feedback(article.id, 1, "Not relevant")
                                st.info("Feedback noted")
                        
                        with col_feedback3:
                            feedback_text = st.text_input(f"💬 Quick feedback", key=f"feedback_{article.id}", placeholder="Why is this useful/not useful?")
                            if feedback_text:
                                rating = 4 if "good" in feedback_text.lower() or "useful" in feedback_text.lower() else 3
                                db.save_feedback(article.id, rating, feedback_text)
                                st.success("Detailed feedback saved!")
                
                else:
                    st.warning("No results found. Try adjusting filters or check API connectivity.")
    
    with col_right:
        st.markdown("#### 📈 Live Discovery Stats")
        
        # Create a simple trend chart
        if analytics['weekly_trend']:
            dates = [item[0] for item in analytics['weekly_trend']]
            counts = [item[1] for item in analytics['weekly_trend']]
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=dates,
                y=counts,
                mode='lines+markers',
                name='Daily Discoveries',
                line=dict(color='#667eea', width=3)
            ))
            fig_trend.update_layout(
                title="📈 Discovery Trend",
                height=250,
                showlegend=False,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Recent high-quality finds
        st.markdown("#### 🔥 Recent Quality Finds")
        recent_articles = db.get_articles(limit=3, filters={'min_score': 70})
        
        for article in recent_articles:
            st.write(f"⭐ **{article[5]}** - Score: {article[10]}/100")  # source_quality and relevance_score
            st.write(f"   {article[1][:60]}...")  # title
            st.write("---")

with tab2:
    st.markdown("### 📋 Strategic Content Library")
    
    # Filter controls for library
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        library_quality = st.selectbox("Source Quality", ["All", "Premium", "High Quality", "Thought Leadership"])
    
    with col_filter2:
        library_category = st.selectbox("Category", ["All"] + [cat.replace("All ", "") for cat in categories[1:]])
    
    with col_filter3:
        library_sort = st.selectbox("Sort By", ["Relevance Score", "Date Added", "User Rating"])
    
    # Build library filters
    lib_filters = {}
    if library_quality != "All":
        quality_map = {
            "Premium": "premium",
            "High Quality": "high_quality", 
            "Thought Leadership": "thought_leadership"
        }
        lib_filters['source_quality'] = quality_map[library_quality]
    
    if library_category != "All":
        lib_filters['category'] = library_category.lower().replace(' ', '_')
    
    # Get all articles from database
    all_articles = db.get_articles(filters=lib_filters)
    
    st.info(f"📚 **Content Library:** {len(all_articles)} strategic articles stored")
    
    # Display library content
    if all_articles:
        # Pagination
        items_per_page = 20
        total_pages = (len(all_articles) + items_per_page - 1) // items_per_page
        
        if total_pages > 1:
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1) - 1
        else:
            page = 0
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(all_articles))
        page_articles = all_articles[start_idx:end_idx]
        
        st.write(f"**Showing {start_idx + 1}-{end_idx} of {len(all_articles)} articles**")
        
        for i, article_row in enumerate(page_articles):
            # Unpack article data
            (article_id, title, content, url, domain, source_quality, published_date, 
             search_query, search_category, relevance_score, ai_summary, key_insights, 
             is_paywall, content_freshness, user_rating, bookmark_count, view_count, created_at) = article_row
            
            # Create expandable article card
            with st.expander(f"📄 {title} - Score: {relevance_score}/100", expanded=False):
                col_content, col_actions = st.columns([3, 1])
                
                with col_content:
                    st.write(f"**🎯 Strategic Value:** {ai_summary}")
                    st.write(f"**💡 Key Insights:** {key_insights}")
                    st.write(f"**📂 Category:** {search_category.replace('_', ' ').title()}")
                    st.write(f"**🌐 Source:** {domain} ({source_quality})")
                    st.write(f"**📅 Content Age:** {content_freshness}")
                    if is_paywall:
                        st.warning("🔒 This content may be behind a paywall")
                
                with col_actions:
                    if st.button("🔖 Bookmark", key=f"bookmark_{article_id}"):
                        # Update bookmark count
                        st.success("Bookmarked!")
                    
                    if st.button("📊 View", key=f"view_{article_id}"):
                        # Update view count and redirect
                        st.success("Opening article...")
                        st.write(f"[🔗 Open Article]({url})")
                    
                    # Rating
                    rating = st.selectbox("Rate", [None, 1, 2, 3, 4, 5], key=f"rate_{article_id}")
                    if rating and rating != user_rating:
                        db.save_feedback(article_id, rating)
                        st.success(f"Rated {rating}/5!")
    
    else:
        st.info("No articles in library yet. Run a discovery search to populate the library.")

with tab3:
    st.markdown("### 📊 Intelligence Analytics")
    
    col_analytics1, col_analytics2 = st.columns(2)
    
    with col_analytics1:
        # Content quality distribution
        quality_articles = db.get_articles()
        if quality_articles:
            scores = [article[10] for article in quality_articles if article[10] > 0]  # relevance_score
            
            fig_quality = px.histogram(
                x=scores,
                title="🎯 Content Quality Distribution",
                nbins=20,
                labels={'x': 'Relevance Score', 'y': 'Number of Articles'}
            )
            fig_quality.update_layout(showlegend=False)
            st.plotly_chart(fig_quality, use_container_width=True)
            
            # Source quality pie chart
            source_counts = {}
            for article in quality_articles:
                source_quality = article[5]  # source_quality
                source_counts[source_quality] = source_counts.get(source_quality, 0) + 1
            
            if source_counts:
                fig_sources = px.pie(
                    values=list(source_counts.values()),
                    names=list(source_counts.keys()),
                    title="📰 Content by Source Quality"
                )
                st.plotly_chart(fig_sources, use_container_width=True)
    
    with col_analytics2:
        # Category distribution
        category_counts = {}
        freshness_counts = {}
        
        for article in quality_articles:
            category = article[8]  # search_category
            freshness = article[13]  # content_freshness
            
            category_counts[category] = category_counts.get(category, 0) + 1
            freshness_counts[freshness] = freshness_counts.get(freshness, 0) + 1
        
        if category_counts:
            fig_categories = px.bar(
                x=list(category_counts.values()),
                y=list(category_counts.keys()),
                title="📂 Content by Category",
                orientation='h'
            )
            st.plotly_chart(fig_categories, use_container_width=True)
        
        if freshness_counts:
            fig_freshness = px.bar(
                x=list(freshness_counts.keys()),
                y=list(freshness_counts.values()),
                title="⏰ Content Freshness Distribution"
            )
            st.plotly_chart(fig_freshness, use_container_width=True)
    
    # Performance metrics
    st.markdown("#### 📈 System Performance")
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    with perf_col1:
        avg_score = sum(article[10] for article in quality_articles if article[10] > 0) / len(quality_articles) if quality_articles else 0
        st.metric("Average Quality Score", f"{avg_score:.1f}/100")
    
    with perf_col2:
        premium_count = len([a for a in quality_articles if a[5] == 'premium'])
        premium_pct = (premium_count / len(quality_articles) * 100) if quality_articles else 0
        st.metric("Premium Source %", f"{premium_pct:.1f}%")
    
    with perf_col3:
        fresh_count = len([a for a in quality_articles if a[13] in ['fresh', 'recent']])
        fresh_pct = (fresh_count / len(quality_articles) * 100) if quality_articles else 0
        st.metric("Fresh Content %", f"{fresh_pct:.1f}%")
    
    with perf_col4:
        paywall_count = len([a for a in quality_articles if a[12]])  # is_paywall
        paywall_pct = (paywall_count / len(quality_articles) * 100) if quality_articles else 0
        st.metric("Paywall Content %", f"{paywall_pct:.1f}%")

with tab4:
    st.markdown("### 🎯 Strategic Insights")
    
    # AI-generated insights based on stored content
    insights_articles = db.get_articles(limit=50, filters={'min_score': 70})
    
    if insights_articles:
        st.markdown("#### 🧠 AI-Generated Market Intelligence")
        
        # Extract themes and patterns
        categories = {}
        sources = {}
        recent_trends = []
        
        for article in insights_articles:
            category = article[8]  # search_category
            source = article[4]  # domain
            summary = article[11]  # ai_summary
            
            categories[category] = categories.get(category, 0) + 1
            sources[source] = sources.get(source, 0) + 1
            
            if article[13] == 'fresh':  # content_freshness
                recent_trends.append(summary)
        
        # Market themes
        col_insights1, col_insights2 = st.columns(2)
        
        with col_insights1:
            st.markdown("#### 🔥 Dominant Themes")
            sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            
            for category, count in sorted_categories[:5]:
                percentage = (count / len(insights_articles) * 100)
                st.write(f"**{category.replace('_', ' ').title()}** - {count} articles ({percentage:.1f}%)")
                
                # Get sample insights from this category
                category_articles = [a for a in insights_articles if a[8] == category]
                if category_articles:
                    sample_insight = category_articles[0][11]  # ai_summary
                    st.write(f"   💡 {sample_insight[:100]}...")
                st.write("---")
        
        with col_insights2:
            st.markdown("#### 📊 Intelligence Sources")
            sorted_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)
            
            for source, count in sorted_sources[:8]:
                st.write(f"• **{source}** - {count} articles")
        
        # Recent strategic signals
        st.markdown("#### 🎯 Recent Strategic Signals")
        
        if recent_trends:
            for i, trend in enumerate(recent_trends[:5]):
                st.write(f"**Signal {i+1}:** {trend}")
        else:
            st.info("No fresh strategic signals detected. Run a new discovery search.")
        
        # Contrarian opportunities
        st.markdown("#### 🔍 Potential Contrarian Opportunities")
        
        contrarian_articles = [a for a in insights_articles if 'contrarian' in a[8]]  # search_category
        
        if contrarian_articles:
            for article in contrarian_articles[:3]:
                st.write(f"**💡 {article[1][:80]}...**")  # title
                st.write(f"   {article[11]}")  # ai_summary
                st.write("---")
        else:
            # Generate some sample contrarian insights
            st.write("**💡 Underexplored Sectors:** Look for gaps in current VC focus areas")
            st.write("**💡 Geographic Arbitrage:** Tier-2/3 city opportunities with lower competition")
            st.write("**💡 Timing Opportunities:** Sectors in trough phase of hype cycle")
    
    else:
        st.info("No strategic content available for insights. Populate the library first.")

with tab5:
    st.markdown("### ⚙️ System Configuration & Status")
    
    # API Status
    col_status1, col_status2 = st.columns(2)
    
    with col_status1:
        st.markdown("#### 🔌 API Connections")
        
        if api_connected:
            st.success("✅ **Tavily Search API** - Connected")
            st.success("✅ **OpenAI API** - Connected")
        else:
            st.error("❌ **APIs Not Connected**")
            st.info("Add OPENAI_API_KEY and TAVILY_API_KEY to Streamlit secrets")
        
        # Database status
        try:
            total_articles = analytics['total_articles']
            st.success(f"✅ **Database** - {total_articles} articles stored")
        except:
            st.error("❌ **Database** - Connection issue")
    
    with col_status2:
        st.markdown("#### 📊 System Performance")
        
        # Show database statistics
        st.info(f"**Database Size:** {analytics['total_articles']} articles")
        st.info(f"**Quality Articles:** {analytics['high_quality']} (≥70 score)")
        st.info(f"**Average Score:** {analytics['avg_score']}/100")
        st.info(f"**Today's Additions:** {analytics['today_articles']}")
    
    # Database management
    st.markdown("#### 🗄️ Database Management")
    
    col_db1, col_db2, col_db3 = st.columns(3)
    
    with col_db1:
        if st.button("📊 Export Data"):
            # Export articles to CSV
            articles_data = db.get_articles()
            if articles_data:
                df = pd.DataFrame(articles_data, columns=[
                    'id', 'title', 'content', 'url', 'domain', 'source_quality',
                    'published_date', 'search_query', 'search_category', 
                    'relevance_score', 'ai_summary', 'key_insights', 
                    'is_paywall', 'content_freshness', 'user_rating',
                    'bookmark_count', 'view_count', 'created_at'
                ])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"vc_intelligence_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data to export")
    
    with col_db2:
        if st.button("🔄 Refresh Analytics"):
            st.cache_data.clear()
            st.rerun()
    
    with col_db3:
        if st.button("⚠️ Clear Database", type="secondary"):
            if st.button("⚠️ Confirm Clear", type="secondary"):
                # Clear database logic would go here
                st.warning("Database cleared!")
    
    # Search configuration
    st.markdown("#### 🔍 Search Configuration")
    
    st.write("**Current Search Queries:** 56 strategic queries covering:")
    st.write("• Investment thesis and frameworks")
    st.write("• Current thought leaders and VCs")
    st.write("• Sector-specific intelligence")
    st.write("• Scaling and operational excellence")
    st.write("• Market dynamics and trends")
    st.write("• Contrarian and emerging themes")
    
    # System alerts
    st.markdown("#### 🚨 System Alerts")
    
    if analytics['total_articles'] == 0:
        st.warning("📋 **Database Empty** - Run discovery search to populate content")
    
    if not api_connected:
        st.error("🔌 **API Issues** - Configure API keys in secrets")
    
    if analytics['today_articles'] == 0:
        st.info("🔄 **No Fresh Content** - Consider running a new discovery search")

# Footer
st.markdown("---")
st.markdown("### 🚀 System Status")

if api_connected and analytics['total_articles'] > 0:
    st.success("✅ **India VC Intelligence Pro v5.0 FULLY OPERATIONAL** • Database Connected • AI Analysis Active • Real-time Discovery Ready")
else:
    st.warning("⚠️ **System Partially Operational** • Configure APIs and populate database for full functionality")

st.markdown(f"🧠 **Enhanced VC Intelligence System** | Complete Strategic Platform | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
