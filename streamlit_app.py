import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
import openai
import requests
from urllib.parse import urlparse
import time

# Page configuration MUST BE FIRST
st.set_page_config(
    page_title="India VC Intelligence",
    page_icon="🚀",
    layout="wide"
)

# Version check
st.write("🧪 **VERSION: Enhanced Google with AI Filtering v4.0 - PROJECT OMEGA FOUNDATION**")

# Initialize APIs
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    from tavily import TavilyClient
    tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
except:
    st.error("API keys not found in secrets")

# Main title
st.title("🚀 India VC Intelligence Agent")
st.subheader("🧠 Enhanced AI-powered venture capital intelligence with strategic content discovery")

# Enhanced search button
st.markdown("## 🔍 Enhanced Strategic Content Discovery")
st.info("**NEW:** 50+ targeted queries • Social media integration • Investment thesis hunting • 55+ relevance threshold")

if st.button("🧠 **RUN ENHANCED INTELLIGENT SEARCH**", type="primary", use_container_width=True):
    st.write("🧠 **Starting Enhanced Multi-Source Intelligence Discovery**")
    
    # Test APIs
    st.write("### 🔧 Testing Enhanced API Connections")
    
    try:
        st.write("📡 Testing Tavily API...")
        test_response = tavily_client.search(query="venture capital", max_results=1)
        st.success(f"✅ Tavily connected! Enhanced search ready.")
        
        st.write("🧠 Testing OpenAI API...")
        test_completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        st.success("✅ OpenAI connected! Enhanced AI analysis ready.")
        
    except Exception as e:
        st.error(f"❌ API connection failed: {str(e)}")
        st.stop()
    
    # ENHANCED STAGE 1: STRATEGIC MULTI-SOURCE SEARCH
    st.write("### 📡 Enhanced Stage 1: Strategic Multi-Source Discovery")
    st.write("*Deploying 50+ targeted queries across strategic content sources...*")
    
    # MASSIVELY EXPANDED SEARCH QUERIES
    enhanced_queries = [
        # INVESTMENT THESIS & STRATEGY
        "venture capital investment thesis India",
        "VC investment strategy framework",
        "startup investment philosophy India",
        "venture capital market analysis India",
        "VC sector thesis fintech India",
        "investment strategy SaaS India",
        "venture capital outlook India 2025",
        "startup ecosystem trends India",
        
        # THOUGHT LEADERS BY NAME (some examples)
        "Shailendra Singh Sequoia Capital India",
        "Anandan Rajan Peak XV Partners",
        "Prashanth Prakash Accel India",
        "Avnish Bajaj Matrix Partners India",
        "Mukul Arora Elevation Capital",
        "Bejul Somaia Lightspeed India",
        "Karthik Reddy Blume Ventures",
        "Vani Kola Kalaari Capital",
        
        # SECTOR-SPECIFIC INTELLIGENCE
        "fintech investment trends India",
        "SaaS startup scaling India",
        "B2B marketplace strategy India",
        "edtech investment outlook India",
        "healthtech venture capital India",
        "logistics startup funding India",
        "enterprise software VC India",
        "consumer tech investment India",
        
        # SCALING & GROWTH FRAMEWORKS
        "startup scaling playbook India",
        "venture capital growth strategy",
        "startup business model India",
        "product market fit India",
        "go-to-market strategy India",
        "startup hiring strategy India",
        "venture building framework",
        "startup expansion strategy",
        
        # MARKET ANALYSIS & TRENDS
        "Indian startup market size",
        "venture capital market trends",
        "startup valuation trends India",
        "IPO readiness India startups",
        "startup exit strategy India",
        "venture capital LP trends",
        "startup funding winter India",
        "venture capital returns India",
        
        # GLOBAL VC PERSPECTIVES ON INDIA
        "Silicon Valley India venture capital",
        "global VC India investment",
        "international venture capital India",
        "cross-border venture capital India",
        "US VC India strategy",
        
        # OPERATIONAL EXCELLENCE
        "startup operations excellence",
        "venture capital due diligence",
        "startup board management",
        "venture capital portfolio management",
        "startup metrics framework",
        "venture capital value creation",
        
        # CONTRARIAN & EMERGING THEMES
        "contrarian venture capital India",
        "emerging technology VC India",
        "deep tech venture capital India",
        "climate tech investment India",
        "space tech venture capital India"
    ]
    
    st.info(f"🎯 **Enhanced Query Set:** {len(enhanced_queries)} strategic queries (vs 8 basic ones)")
    
    all_enhanced_results = []
    
    try:
        with st.expander("🔍 **Enhanced Stage 1 Progress** (Click to expand)", expanded=True):
            # Show progress in batches
            batch_size = 10
            total_batches = (len(enhanced_queries) + batch_size - 1) // batch_size
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(enhanced_queries))
                batch_queries = enhanced_queries[start_idx:end_idx]
                
                st.write(f"**🔍 Batch {batch_num + 1}/{total_batches}:** Processing {len(batch_queries)} queries...")
                
                batch_progress = st.progress(0)
                
                for i, query in enumerate(batch_queries):
                    batch_progress.progress((i + 1) / len(batch_queries))
                    
                    try:
                        # Enhanced search with more results per query
                        response = tavily_client.search(query=query, max_results=3, days=90)  # Last 90 days
                        results = response.get('results', [])
                        
                        # Enhanced result processing
                        for result in results:
                            # Extract enhanced metadata
                            url = result.get('url', '')
                            domain = urlparse(url).netloc if url else 'Unknown'
                            
                            # Source quality scoring
                            premium_sources = [
                                'techcrunch.com', 'a16z.com', 'sequoiacap.com', 'accel.com',
                                'medium.com', 'substack.com', 'linkedin.com', 'twitter.com',
                                'inc42.com', 'yourstory.com', 'entrackr.com', 'vccircle.com'
                            ]
                            
                            source_quality = 'Premium' if any(ps in domain for ps in premium_sources) else 'Standard'
                            
                            enhanced_result = {
                                'title': result.get('title', 'No title'),
                                'content': result.get('content', 'No content'),
                                'url': url,
                                'domain': domain,
                                'source_quality': source_quality,
                                'published_date': result.get('published_date', datetime.now().isoformat()),
                                'search_query': query,
                                'search_category': classify_query_category(query)
                            }
                            
                            all_enhanced_results.append(enhanced_result)
                            
                    except Exception as e:
                        st.write(f"    ❌ Query '{query[:30]}...' failed: {str(e)[:50]}")
                
                # Small delay between batches to avoid rate limits
                time.sleep(1)
                
                st.write(f"  ✅ Batch {batch_num + 1} complete! Found {len([r for r in all_enhanced_results if r['search_category'] == classify_query_category(batch_queries[0])])} results")
        
        st.success(f"📊 **Enhanced Stage 1 Complete:** Found {len(all_enhanced_results)} total articles")
        
        # Enhanced deduplication with URL and title similarity
        unique_enhanced_results = deduplicate_results(all_enhanced_results)
        
        st.info(f"📋 **After enhanced deduplication:** {len(unique_enhanced_results)} unique articles")
        st.info(f"🏆 **Premium sources:** {len([r for r in unique_enhanced_results if r['source_quality'] == 'Premium'])} articles")
        
        if not unique_enhanced_results:
            st.warning("⚠️ No content found. Check API limits.")
            st.stop()
        
        # Show enhanced sample with categories
        st.write("### 📋 Enhanced Content Discovery Sample:")
        category_samples = {}
        for article in unique_enhanced_results[:6]:
            category = article['search_category']
            if category not in category_samples:
                category_samples[category] = []
            if len(category_samples[category]) < 2:
                category_samples[category].append(article)
        
        for category, articles in category_samples.items():
            st.write(f"**📂 {category.upper()}:**")
            for article in articles:
                quality_icon = "🏆" if article['source_quality'] == 'Premium' else "📄"
                st.write(f"  {quality_icon} {article['title'][:80]}...")
                st.write(f"    Source: {article['domain']}")
            st.write("---")
        
        # ENHANCED STAGE 2: STRATEGIC AI ANALYSIS
        st.write("### 🧠 Enhanced Stage 2: Strategic AI Analysis Engine")
        st.write("*Advanced AI classification for investment thesis and strategic value...*")
        
        def enhanced_ai_classify_content(article):
            """Enhanced AI classification focused on strategic VC intelligence"""
            
            enhanced_prompt = f"""
            STRATEGIC VC INTELLIGENCE ANALYSIS
            
            Analyze this content for strategic value to VCs and startup founders. Use the enhanced scoring criteria:
            
            Title: {article['title']}
            Content: {article['content'][:1000]}
            Source: {article['domain']} ({article['source_quality']})
            Category: {article['search_category']}
            
            ENHANCED SCORING CRITERIA:
            
            EXCEPTIONAL VALUE (80-100 points):
            - Investment thesis documents and frameworks
            - Detailed market analysis with actionable insights
            - Scaling playbooks with specific methodologies
            - Strategic decision-making frameworks
            - Contrarian investment perspectives
            - Deep sector analysis with predictions
            - Founder journey with strategic lessons
            - VC portfolio strategy insights
            
            HIGH VALUE (60-79 points):
            - Business building methodologies
            - Market trend analysis with context
            - Growth strategy frameworks
            - Investment philosophy discussions
            - Sector-specific insights
            - Operational excellence guides
            - Funding strategy insights
            
            MEDIUM VALUE (40-59 points):
            - Company case studies with strategic context
            - Market reports with some insights
            - General business strategy content
            - Industry trend discussions
            
            LOW VALUE (0-39 points):
            - Basic funding announcements
            - Generic startup advice
            - Product launches without strategy
            - Event announcements
            - Superficial company profiles
            
            SCORING MODIFIERS:
            - Premium source (+10 points)
            - Recent content (last 30 days) (+5 points)
            - Thought leader authored (+10 points)
            - Investment thesis category (+15 points)
            - Contrarian perspective (+10 points)
            
            Respond with JSON only:
            {{"score": X, "category": "investment_thesis/scaling_strategy/market_analysis/thought_leadership", "strategic_value": "brief reason", "actionable_insights": "key takeaways"}}
            """
            
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": enhanced_prompt}],
                    max_tokens=300,
                    temperature=0.1
                )
                
                content = response.choices[0].message.content.strip()
                if content.startswith('```json'):
                    content = content[7:-3]
                elif content.startswith('```'):
                    content = content[3:-3]
                
                result = json.loads(content)
                
                # Apply scoring modifiers
                base_score = result.get('score', 0)
                if article['source_quality'] == 'Premium':
                    base_score += 10
                if article['search_category'] == 'investment_thesis':
                    base_score += 15
                
                result['score'] = min(base_score, 100)  # Cap at 100
                return result
                
            except Exception as e:
                st.write(f"    ⚠️ Enhanced AI analysis failed: {str(e)[:50]}")
                # Enhanced fallback
                text = f"{article['title']} {article['content']}".lower()
                strategic_keywords = [
                    'thesis', 'framework', 'strategy', 'scaling', 'investment', 
                    'analysis', 'insights', 'methodology', 'playbook', 'growth'
                ]
                score = min(sum(12 for keyword in strategic_keywords if keyword in text), 75)
                if article['source_quality'] == 'Premium':
                    score += 10
                return {
                    "score": score, 
                    "category": "general", 
                    "strategic_value": "fallback keyword analysis",
                    "actionable_insights": "requires manual review"
                }
        
        # Enhanced processing with higher threshold
        strategic_articles = []
        
        with st.expander("🧠 **Enhanced Stage 2 Progress** (Click to expand)", expanded=True):
            # Process more articles but with higher quality threshold
            test_articles = unique_enhanced_results[:20]  # Increased from 10
            st.info(f"🎯 **Enhanced Analysis:** Processing {len(test_articles)} articles with 55+ threshold")
            
            progress_bar = st.progress(0)
            
            high_value_count = 0
            medium_value_count = 0
            rejected_count = 0
            
            for i, article in enumerate(test_articles):
                progress_bar.progress((i + 1) / len(test_articles))
                
                st.write(f"**Analyzing {i+1}/{len(test_articles)}:** {article['title'][:70]}...")
                
                # Enhanced AI classification
                classification = enhanced_ai_classify_content(article)
                score = classification.get('score', 0)
                strategic_value = classification.get('strategic_value', 'No analysis')
                insights = classification.get('actionable_insights', 'None identified')
                
                quality_icon = "🏆" if article['source_quality'] == 'Premium' else "📄"
                st.write(f"    {quality_icon} **Score: {score}/100**")
                st.write(f"    🎯 **Strategic Value:** {strategic_value}")
                
                # Enhanced threshold: 55+ only
                if score >= 55:
                    priority = 'Exceptional' if score >= 80 else 'High' if score >= 70 else 'Medium'
                    if score >= 70:
                        high_value_count += 1
                        st.write(f"    ✅ **ACCEPTED - {priority.upper()}** ({score}/100)")
                    else:
                        medium_value_count += 1
                        st.write(f"    ✅ **ACCEPTED - {priority.upper()}** ({score}/100)")
                    
                    # Enhanced article data
                    article['relevance_score'] = score
                    article['ai_category'] = classification.get('category', 'general')
                    article['strategic_value'] = strategic_value
                    article['actionable_insights'] = insights
                    article['priority'] = priority
                    
                    strategic_articles.append(article)
                else:
                    rejected_count += 1
                    st.write(f"    ❌ **REJECTED** - Below 55 threshold ({score}/100)")
        
        # Enhanced results summary
        st.success(f"🎯 **Enhanced Stage 2 Complete:** {len(strategic_articles)} strategic articles found!")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("High Value (70+)", high_value_count)
        with col2:
            st.metric("Medium Value (55-69)", medium_value_count)
        with col3:
            st.metric("Rejected (<55)", rejected_count)
        with col4:
            premium_count = len([a for a in strategic_articles if a['source_quality'] == 'Premium'])
            st.metric("Premium Sources", premium_count)
        
        if strategic_articles:
            # Enhanced article display
            st.write("### 📋 Strategic Intelligence Articles:")
            
            # Sort by score (highest first)
            strategic_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            for i, article in enumerate(strategic_articles):
                priority_icon = "🔥" if article['priority'] == 'Exceptional' else "⭐" if article['priority'] == 'High' else "📌"
                quality_icon = "🏆" if article['source_quality'] == 'Premium' else "📄"
                
                st.write(f"**{i+1}.** {priority_icon} {quality_icon} {article['title']} **({article['relevance_score']}/100)**")
                st.write(f"   🎯 **Strategic Value:** {article['strategic_value']}")
                st.write(f"   💡 **Key Insights:** {article['actionable_insights']}")
                st.write(f"   📂 **Category:** {article['ai_category']} | **Source:** {article['domain']}")
                st.write(f"   [🔗 Read Article]({article['url']})")
                st.write("---")
            
            # Enhanced summary analytics
            st.write("### 📊 Enhanced Intelligence Summary")
            
            avg_score = sum(article['relevance_score'] for article in strategic_articles) / len(strategic_articles)
            
            # Category breakdown
            categories = {}
            for article in strategic_articles:
                cat = article['ai_category']
                categories[cat] = categories.get(cat, 0) + 1
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**📂 Content Categories:**")
                for cat, count in categories.items():
                    st.write(f"- {cat.replace('_', ' ').title()}: {count} articles")
            
            with col2:
                st.write("**🎯 Quality Metrics:**")
                st.write(f"- Average Quality Score: {avg_score:.1f}/100")
                st.write(f"- Premium Source Rate: {premium_count}/{len(strategic_articles)} ({premium_count/len(strategic_articles)*100:.0f}%)")
                st.write(f"- Acceptance Rate: {len(strategic_articles)}/{len(test_articles)} ({len(strategic_articles)/len(test_articles)*100:.0f}%)")
                
        else:
            st.warning("⚠️ No strategic articles found meeting 55+ threshold.")
            st.info("**Possible reasons:**")
            st.write("- Search queries need refinement")
            st.write("- AI scoring criteria too strict") 
            st.write("- Limited premium content available")
            st.write("- API rate limits affecting search depth")
            
    except Exception as e:
        st.error(f"❌ **Enhanced search process failed:** {str(e)}")
        st.exception(e)

# Helper functions
def classify_query_category(query):
    """Classify search query into strategic categories"""
    query_lower = query.lower()
    if any(term in query_lower for term in ['thesis', 'philosophy', 'strategy']):
        return 'investment_thesis'
    elif any(term in query_lower for term in ['scaling', 'growth', 'framework']):
        return 'scaling_strategy'
    elif any(term in query_lower for term in ['market', 'trends', 'analysis']):
        return 'market_analysis'
    elif any(term in query_lower for term in ['sequoia', 'accel', 'matrix', 'elevation']):
        return 'thought_leadership'
    else:
        return 'general_intelligence'

def deduplicate_results(results):
    """Enhanced deduplication based on URL and title similarity"""
    unique_results = []
    seen_urls = set()
    seen_titles = set()
    
    for result in results:
        url = result.get('url', '')
        title = result.get('title', '').lower()
        
        # Skip if exact URL match
        if url in seen_urls:
            continue
            
        # Skip if very similar title
        title_words = set(title.split())
        is_similar = False
        for seen_title in seen_titles:
            seen_words = set(seen_title.split())
            if len(title_words & seen_words) / len(title_words | seen_words) > 0.8:
                is_similar = True
                break
        
        if not is_similar:
            unique_results.append(result)
            seen_urls.add(url)
            seen_titles.add(title)
    
    return unique_results

# Enhanced status section
st.markdown("---")
st.write("### 📊 Enhanced System Status")
st.info("**Enhanced Google with AI Filtering ready!** 50+ strategic queries • Investment thesis hunting • 55+ relevance threshold • Premium source prioritization")

# Footer
st.markdown("---")
st.markdown("🧠 **Enhanced VC Intelligence** | Foundation for Project Omega | " + datetime.now().strftime("%Y-%m-%d %H:%M"))
