import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
import openai

# Add version check to confirm deployment
st.write("🧪 **VERSION: Intelligent Search System v3.0 - FRESH DEPLOYMENT**")

# Page configuration
st.set_page_config(
    page_title="India VC Intelligence",
    page_icon="🚀",
    layout="wide"
)

# Initialize OpenAI (simple approach)
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("OpenAI API key not found in secrets")

# Main title
st.title("🚀 India VC Intelligence Agent")
st.subheader("🧠 AI-powered venture capital intelligence with intelligent content discovery")

# Big prominent search button on main page
st.markdown("## 🔍 Intelligent Content Discovery")

if st.button("🧠 **RUN INTELLIGENT SEARCH**", type="primary", use_container_width=True):
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
        test_completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
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
        "Sequoia Capital India",
        "Peak XV Partners", 
        "Accel India",
        "Matrix Partners India",
        "Elevation Capital",
        "Lightspeed India",
        "Blume Ventures",
        "Kalaari Capital"
    ]
    
    all_raw_results = []
    
    try:
        with st.expander("🔍 **Stage 1 Progress** (Click to expand)", expanded=True):
            for i, query in enumerate(broad_queries):
                st.write(f"**Query {i+1}/{len(broad_queries)}:** '{query}'")
                try:
                    response = tavily_client.search(query=query, max_results=5)
                    results = response.get('results', [])
                    st.write(f"  📥 Raw results: **{len(results)}**")
                    
                    # Show sample titles for verification
                    if results:
                        st.write(f"    Sample: {results[0].get('title', 'No title')[:60]}...")
                    
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
        
        # Show first few articles found
        st.write("### 📋 Sample Articles Found:")
        for i, article in enumerate(unique_results[:3]):
            st.write(f"**{i+1}.** {article['title']}")
            st.write(f"   Source: {article['source']}")
            st.write("---")
        
        # STAGE 2: INTELLIGENT AI FILTERING
        st.write("### 🧠 Stage 2: AI-Powered Content Analysis")
        st.write("*Using GPT-4 to analyze each article for VC intelligence value...*")
        
        def ai_classify_content(article):
            """Use OpenAI to intelligently classify content relevance"""
            
            prompt = f"""
            Analyze this article for VC intelligence value. Score 0-100 based on how valuable it would be for a VC or startup founder.
            
            Title: {article['title']}
            Content: {article['content'][:800]}
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
            {{"score": X, "category": "investment_thesis", "reasoning": "brief explanation"}}
            """
            
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
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
                st.write(f"    ⚠️ AI analysis failed: {str(e)[:50]}")
                # Fallback analysis
                text = f"{article['title']} {article['content']}".lower()
                high_value_keywords = [
                    'strategy', 'thesis', 'insights', 'framework', 'scaling', 
                    'growth', 'investment', 'analysis', 'trends', 'outlook'
                ]
                score = min(sum(15 for keyword in high_value_keywords if keyword in text), 85)
                return {"score": score, "category": "general", "reasoning": "fallback keyword analysis"}
        
        # Process articles with AI analysis
        high_value_articles = []
        
        with st.expander("🧠 **Stage 2 Progress** (Click to expand)", expanded=True):
            progress_bar = st.progress(0)
            
            # Limit to first 10 articles for testing to avoid API limits
            test_articles = unique_results[:10]
            st.info(f"Testing AI analysis on first {len(test_articles)} articles to avoid API limits")
            
            for i, article in enumerate(test_articles):
                progress_bar.progress((i + 1) / len(test_articles))
                
                st.write(f"**Analyzing {i+1}/{len(test_articles)}:** {article['title'][:60]}...")
                
                # Get AI classification
                classification = ai_classify_content(article)
                score = classification.get('score', 0)
                reasoning = classification.get('reasoning', 'No reasoning')
                
                st.write(f"    🎯 **Score: {score}/100**")
                st.write(f"    📝 **AI Reasoning:** {reasoning}")
                
                if score >= 40:  # Lower threshold for testing
                    st.write(f"    ✅ **ACCEPTED** - High enough value")
                    
                    # Add classification data to article
                    article['relevance_score'] = score
                    article['ai_category'] = classification.get('category', 'general')
                    article['ai_reasoning'] = reasoning
                    article['priority'] = 'High' if score >= 70 else 'Medium'
                    
                    high_value_articles.append(article)
                else:
                    st.write(f"    ❌ **REJECTED** - Score too low")
        
        st.success(f"🎯 **Stage 2 Complete:** {len(high_value_articles)} high-value articles identified")
        
        if high_value_articles:
            # Show accepted articles
            st.write("### 📋 High-Value Articles Found:")
            for i, article in enumerate(high_value_articles):
                st.write(f"**{i+1}.** {article['title']} (Score: {article['relevance_score']}/100)")
                st.write(f"   Reasoning: {article['ai_reasoning']}")
                st.write(f"   [Read Article]({article['url']})")
                st.write("---")
            
            # For now, just show the results instead of storing in database
            st.write("### 💾 Stage 3: Results Summary")
            st.success(f"✅ **SUCCESS!** Found {len(high_value_articles)} high-value articles!")
            
            # Show summary statistics
            avg_score = sum(article['relevance_score'] for article in high_value_articles) / len(high_value_articles)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("High-Value Articles", len(high_value_articles))
            with col2:
                st.metric("Avg Quality Score", f"{avg_score:.1f}/100")
            with col3:
                st.metric("Total Analyzed", len(test_articles))
                
        else:
            st.warning("⚠️ No high-value articles found. All articles scored below threshold.")
            st.info("This might mean:")
            st.write("- The articles found were mostly basic news")
            st.write("- AI threshold is too high") 
            st.write("- Need different search terms")
            
    except Exception as e:
        st.error(f"❌ **Search process failed:** {str(e)}")
        st.exception(e)

# Rest of the interface
st.markdown("---")
st.write("### 📊 System Status")
st.info("Database integration temporarily disabled for testing. Using in-memory results only.")

# Footer
st.markdown("---")
st.markdown("🧠 **Intelligent VC Discovery** | Testing Mode | " + datetime.now().strftime("%Y-%m-%d %H:%M"))
