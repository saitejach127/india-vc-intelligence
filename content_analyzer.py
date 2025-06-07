import streamlit as st
import openai
from typing import Dict, List, Any
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import pandas as pd

class ContentAnalyzer:
    def __init__(self):
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        
        # Configuration
        self.tier1_vcs = [
            "Peak XV", "Sequoia", "Accel", "Matrix Partners", 
            "Elevation", "Lightspeed", "Blume"
        ]
        
        self.priority_sectors = {
            "Consumer": ["consumer", "retail", "marketplace", "e-commerce"],
            "D2C": ["d2c", "direct-to-consumer", "brand", "digital native"],
            "SaaS": ["saas", "software-as-a-service", "enterprise software", "b2b software"],
            "Fintech": ["fintech", "financial technology", "payments", "banking", "neobank"],
            "AI SaaS": ["ai saas", "artificial intelligence software", "ai platform", "machine learning saas"],
            "Agentic AI": ["agentic ai", "ai agents", "autonomous ai", "ai automation", "intelligent agents"]
        }
        
        self.investment_keywords = [
            "investment thesis", "portfolio strategy", "market analysis", "funding trends",
            "investment focus", "sector outlook", "market opportunity", "venture capital",
            "investment philosophy", "deal flow", "due diligence", "investment criteria"
        ]
    
    def analyze_content(self, content_item: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive content analysis"""
        
        # Basic scoring
        relevance_score = self._calculate_relevance_score(content_item)
        
        # Sector classification
        sectors = self._classify_sectors(content_item)
        
        # VC firm detection
        vc_firm = self._detect_vc_firm(content_item)
        
        # Priority assignment
        priority = self._assign_priority(relevance_score, vc_firm, sectors)
        
        # Extract key insights
        insights = self._extract_insights(content_item)
        
        # Generate summary
        summary = self._generate_summary(content_item)
        
        return {
            **content_item,
            'relevance_score': relevance_score,
            'sectors': ', '.join(sectors),
            'vc_firm': vc_firm,
            'priority': priority,
            'insights': insights,
            'summary': summary,
            'analysis_timestamp': datetime.now().isoformat(),
            'content_type': self._classify_content_type(content_item),
            'sentiment': self._analyze_sentiment(content_item),
            'key_topics': self._extract_key_topics(content_item)
        }
    
    def _calculate_relevance_score(self, content_item: Dict[str, Any]) -> int:
        """Calculate relevance score (0-100)"""
        score = 50  # Base score
        
        title = content_item.get('title', '').lower()
        content = content_item.get('content', '').lower()
        source = content_item.get('source', '').lower()
        
        # Source authority boost
        if any(vc in source for vc in ['blume', 'accel', 'matrix', 'peak', 'sequoia', 'elevation', 'lightspeed']):
            score += 20
        elif any(domain in source for domain in ['techcrunch', 'inc42', 'entrackr']):
            score += 15
        elif any(domain in source for domain in ['economic', 'business-standard', 'livemint']):
            score += 10
        
        # Investment thesis content boost
        investment_terms = sum(1 for term in self.investment_keywords if term in title or term in content)
        score += min(investment_terms * 5, 20)
        
        # Sector relevance boost
        sector_matches = 0
        for sector_keywords in self.priority_sectors.values():
            if any(keyword in title or keyword in content for keyword in sector_keywords):
                sector_matches += 1
        score += min(sector_matches * 5, 15)
        
        # Recency boost
        date_published = content_item.get('date_published', datetime.now())
        if isinstance(date_published, str):
            try:
                date_published = datetime.fromisoformat(date_published.replace('Z', '+00:00'))
            except:
                date_published = datetime.now()
        
        days_old = (datetime.now() - date_published.replace(tzinfo=None)).days
        if days_old <= 1:
            score += 10
        elif days_old <= 7:
            score += 5
        
        # Content quality indicators
        if len(content) > 500:  # Substantial content
            score += 5
        if 'funding' in title or 'investment' in title:
            score += 10
        if ' in content or '₹' in content:  # Contains financial figures
            score += 5
        
        # Penalize irrelevant content
        if any(term in title.lower() for term in ['cricket', 'bollywood', 'politics', 'weather']):
            score -= 20
        
        return max(0, min(100, score))
    
    def _classify_sectors(self, content_item: Dict[str, Any]) -> List[str]:
        """Classify content into relevant sectors"""
        text = f"{content_item.get('title', '')} {content_item.get('content', '')}".lower()
        
        matched_sectors = []
        for sector, keywords in self.priority_sectors.items():
            if any(keyword in text for keyword in keywords):
                matched_sectors.append(sector)
        
        # If no specific sector found, try to infer from context
        if not matched_sectors:
            if any(term in text for term in ['startup', 'investment', 'funding']):
                matched_sectors.append('General')
        
        return matched_sectors
    
    def _detect_vc_firm(self, content_item: Dict[str, Any]) -> str:
        """Detect which VC firm the content is about/from"""
        text = f"{content_item.get('title', '')} {content_item.get('content', '')} {content_item.get('source', '')}".lower()
        
        vc_mapping = {
            'peak xv': 'Peak XV Partners',
            'sequoia': 'Peak XV Partners',
            'accel': 'Accel India',
            'matrix': 'Matrix Partners India',
            'elevation': 'Elevation Capital',
            'lightspeed': 'Lightspeed India',
            'blume': 'Blume Ventures',
            'kalaari': 'Kalaari Capital',
            'nexus': 'Nexus Venture Partners'
        }
        
        for keyword, firm_name in vc_mapping.items():
            if keyword in text:
                return firm_name
        
        return 'Unknown'
    
    def _assign_priority(self, score: int, vc_firm: str, sectors: List[str]) -> str:
        """Assign priority level"""
        # High priority criteria
        if score >= 80 or vc_firm in self.tier1_vcs or any(s in ['AI SaaS', 'Agentic AI'] for s in sectors):
            return 'High'
        elif score >= 60 or len(sectors) >= 2:
            return 'Medium'
        else:
            return 'Low'
    
    def _extract_insights(self, content_item: Dict[str, Any]) -> str:
        """Extract key insights using OpenAI"""
        try:
            text = f"Title: {content_item.get('title', '')}\nContent: {content_item.get('content', '')}"
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert VC analyst. Extract 2-3 key investment insights from this content. Focus on investment thesis, market trends, or strategic implications. Be concise and specific."
                    },
                    {
                        "role": "user",
                        "content": text[:2000]  # Limit to avoid token limits
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Insight extraction failed: {str(e)[:100]}"
    
    def _generate_summary(self, content_item: Dict[str, Any]) -> str:
        """Generate a concise summary"""
        try:
            text = content_item.get('content', '')
            if len(text) < 200:
                return text
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize this VC/startup content in 2-3 sentences. Focus on key facts, figures, and implications."
                    },
                    {
                        "role": "user",
                        "content": text[:1500]
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return content_item.get('content', '')[:200] + "..."
    
    def _classify_content_type(self, content_item: Dict[str, Any]) -> str:
        """Classify the type of content"""
        title = content_item.get('title', '').lower()
        content = content_item.get('content', '').lower()
        
        if any(term in title for term in ['thesis', 'strategy', 'outlook', 'perspective']):
            return 'Investment Thesis'
        elif any(term in title for term in ['funding', 'raises', 'investment', 'series']):
            return 'Funding News'
        elif any(term in title for term in ['trend', 'analysis', 'report', 'insights']):
            return 'Market Analysis'
        elif any(term in title for term in ['interview', 'podcast', 'discussion']):
            return 'Thought Leadership'
        else:
            return 'General'
    
    def _analyze_sentiment(self, content_item: Dict[str, Any]) -> str:
        """Analyze sentiment of the content"""
        text = f"{content_item.get('title', '')} {content_item.get('content', '')}"
        
        positive_words = ['growth', 'opportunity', 'bullish', 'optimistic', 'positive', 'strong', 'robust']
        negative_words = ['decline', 'bearish', 'pessimistic', 'weak', 'challenging', 'difficult', 'winter']
        
        positive_count = sum(1 for word in positive_words if word in text.lower())
        negative_count = sum(1 for word in negative_words if word in text.lower())
        
        if positive_count > negative_count:
            return 'Positive'
        elif negative_count > positive_count:
            return 'Negative'
        else:
            return 'Neutral'
    
    def _extract_key_topics(self, content_item: Dict[str, Any]) -> List[str]:
        """Extract key topics/themes"""
        text = f"{content_item.get('title', '')} {content_item.get('content', '')}".lower()
        
        # Predefined topic keywords
        topics = {
            'AI Revolution': ['ai', 'artificial intelligence', 'machine learning', 'generative ai'],
            'Funding Environment': ['funding winter', 'valuation', 'ipo', 'public markets'],
            'Regulatory Changes': ['regulation', 'policy', 'rbi', 'sebi', 'government'],
            'Market Expansion': ['global', 'international', 'expansion', 'us market'],
            'Technology Trends': ['blockchain', 'web3', 'cloud', 'automation'],
            'Consumer Behavior': ['consumer behavior', 'digital adoption', 'tier 2', 'rural']
        }
        
        matched_topics = []
        for topic, keywords in topics.items():
            if any(keyword in text for keyword in keywords):
                matched_topics.append(topic)
        
        return matched_topics[:3]  # Return top 3 topics
    
    def extract_themes(self, content_list: List[str]) -> Dict[str, List[Dict]]:
        """Extract trending themes from multiple articles"""
        if not content_list:
            return {}
        
        # Simple theme extraction based on keyword frequency
        all_text = ' '.join(content_list).lower()
        
        # Key themes to track
        themes = {
            'ai_revolution': ['ai', 'artificial intelligence', 'generative ai', 'llm'],
            'funding_trends': ['funding', 'investment', 'valuation', 'series'],
            'market_dynamics': ['market', 'growth', 'expansion', 'opportunity'],
            'regulatory_impact': ['regulation', 'policy', 'compliance', 'government'],
            'technology_adoption': ['digital', 'technology', 'platform', 'innovation']
        }
        
        theme_scores = {}
        for theme, keywords in themes.items():
            score = sum(all_text.count(keyword) for keyword in keywords)
            if score > 0:
                theme_scores[theme] = score
        
        # Sort themes by relevance
        sorted_themes = dict(sorted(theme_scores.items(), key=lambda x: x[1], reverse=True))
        
        return {theme: [{'title': 'Sample Article', 'url': '#'}] for theme in list(sorted_themes.keys())[:5]}
    
    def generate_insights(self, df: pd.DataFrame) -> Dict[str, str]:
        """Generate AI insights from the data"""
        if df is None or df.empty:
            return {
                'hot_topics': 'No data available for analysis.',
                'sentiment': 'Neutral - insufficient data.',
                'predictions': 'Cannot make predictions without data.'
            }
        
        try:
            # Prepare data summary
            top_sectors = df['sectors'].value_counts().head(3).to_dict()
            avg_score = df['relevance_score'].mean()
            recent_articles = len(df[df['date_published'] >= datetime.now().date() - timedelta(days=7)])
            
            summary_text = f"""
            Data Summary:
            - Total articles: {len(df)}
            - Recent articles (7 days): {recent_articles}
            - Average relevance score: {avg_score:.1f}
            - Top sectors: {top_sectors}
            - Content types: {df['content_type'].value_counts().to_dict()}
            """
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior VC analyst. Based on this data summary, provide insights on: 1) Hot topics in Indian VC ecosystem, 2) Overall market sentiment, 3) Predictions for next quarter. Be specific and actionable."
                    },
                    {
                        "role": "user",
                        "content": summary_text
                    }
                ],
                max_tokens=300,
                temperature=0.4
            )
            
            full_response = response.choices[0].message.content
            
            # Parse response into sections
            insights = {
                'hot_topics': self._extract_section(full_response, 'hot topics') or 'AI/ML and consumer tech remain dominant themes.',
                'sentiment': self._extract_section(full_response, 'sentiment') or 'Market sentiment appears cautiously optimistic.',
                'predictions': self._extract_section(full_response, 'predictions') or 'Continued focus on profitability and sustainable growth expected.'
            }
            
            return insights
        
        except Exception as e:
            return {
                'hot_topics': f'Analysis error: {str(e)[:100]}',
                'sentiment': 'Unable to determine sentiment.',
                'predictions': 'Prediction generation failed.'
            }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract specific section from AI response"""
        lines = text.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            if section_name.lower() in line.lower():
                in_section = True
                continue
            elif in_section and line.strip() and not any(char.isdigit() for char in line[:3]):
                break
            elif in_section:
                section_lines.append(line.strip())
        
        return ' '.join(section_lines).strip()