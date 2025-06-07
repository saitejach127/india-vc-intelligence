import streamlit as st
from tavily import TavilyClient
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import json

class VCSearchEngine:
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
        
        # Configuration
        self.tier1_vcs = [
            "Peak XV Partners", "Sequoia Capital India", 
            "Accel India", "Matrix Partners India", 
            "Elevation Capital", "Lightspeed India", "Blume Ventures"
        ]
        
        self.priority_sectors = [
            "Consumer", "D2C", "SaaS", "Fintech", "AI SaaS", "Agentic AI"
        ]
        
        # RSS feeds for VC blogs
        self.vc_rss_feeds = {
            "Blume Ventures": "https://blume.vc/feed",
            "Accel": "https://www.accel.com/noteworthy/feed",
            "Matrix Partners": "https://medium.com/feed/@matrixpartnersindia",
            "Lightspeed": "https://medium.com/feed/@lightspeedindiapartners"
        }
        
        # Search domains for better targeting
        self.priority_domains = [
            "techcrunch.com", "inc42.com", "entrackr.com", "yourstory.com",
            "economictimes.indiatimes.com", "business-standard.com",
            "livemint.com", "moneycontrol.com", "blume.vc", "accel.com",
            "peakxv.com", "matrixpartners.in", "elevationcarital.com"
        ]
    
    def search_all_sources(self) -> List[Dict[str, Any]]:
        """Main search function that aggregates from all sources"""
        all_results = []
        
        # 1. Search via Tavily for recent content
        tavily_results = self._search_tavily()
        all_results.extend(tavily_results)
        
        # 2. Check RSS feeds
        rss_results = self._search_rss_feeds()
        all_results.extend(rss_results)
        
        # 3. Search for global sources mentioning India
        global_results = self._search_global_india_content()
        all_results.extend(global_results)
        
        # Deduplicate results
        unique_results = self._deduplicate_results(all_results)
        
        return unique_results
    
    def _search_tavily(self) -> List[Dict[str, Any]]:
        """Search using Tavily API"""
        results = []
        
        try:
            # Generate search queries
            queries = self._generate_search_queries()
            
            for query in queries[:10]:  # Limit to 10 queries per run
                try:
                    response = self.tavily_client.search(
                        query=query,
                        search_depth="advanced",
                        max_results=5,
                        include_domains=self.priority_domains,
                        days=7  # Last 7 days
                    )
                    
                    for result in response.get('results', []):
                        processed_result = {
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'content': result.get('content', ''),
                            'source': self._extract_domain(result.get('url', '')),
                            'date_published': self._parse_date(result.get('published_date')),
                            'search_query': query,
                            'raw_score': result.get('score', 0)
                        }
                        results.append(processed_result)
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    st.warning(f"Query failed: {query} - {str(e)}")
                    continue
        
        except Exception as e:
            st.error(f"Tavily search failed: {str(e)}")
        
        return results
    
    def _search_rss_feeds(self) -> List[Dict[str, Any]]:
        """Search RSS feeds from VC blogs"""
        results = []
        
        for vc_name, feed_url in self.vc_rss_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:5]:  # Last 5 posts per feed
                    # Check if content is relevant to our sectors
                    content = f"{entry.get('title', '')} {entry.get('summary', '')}"
                    if self._is_relevant_content(content):
                        result = {
                            'title': entry.get('title', ''),
                            'url': entry.get('link', ''),
                            'content': entry.get('summary', ''),
                            'source': vc_name,
                            'date_published': self._parse_date(entry.get('published')),
                            'search_query': 'RSS Feed',
                            'raw_score': 0.8  # High score for VC-authored content
                        }
                        results.append(result)
            
            except Exception as e:
                st.warning(f"RSS feed failed for {vc_name}: {str(e)}")
                continue
        
        return results
    
    def _search_global_india_content(self) -> List[Dict[str, Any]]:
        """Search for global sources discussing India"""
        results = []
        
        global_queries = [
            "India startup ecosystem investment thesis 2024",
            "Indian fintech market analysis venture capital",
            "India SaaS companies global expansion funding",
            "Indian unicorns valuation trends 2024",
            "India AI startup funding landscape"
        ]
        
        try:
            for query in global_queries:
                response = self.tavily_client.search(
                    query=query,
                    search_depth="basic",
                    max_results=3,
                    days=14
                )
                
                for result in response.get('results', []):
                    # Ensure it mentions India significantly
                    content = f"{result.get('title', '')} {result.get('content', '')}"
                    if content.lower().count('india') >= 2:
                        processed_result = {
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'content': result.get('content', ''),
                            'source': self._extract_domain(result.get('url', '')),
                            'date_published': self._parse_date(result.get('published_date')),
                            'search_query': query,
                            'raw_score': result.get('score', 0) * 0.8  # Slight discount for global sources
                        }
                        results.append(processed_result)
                
                time.sleep(0.5)
        
        except Exception as e:
            st.warning(f"Global search failed: {str(e)}")
        
        return results
    
    def _generate_search_queries(self) -> List[str]:
        """Generate comprehensive search queries"""
        queries = []
        
        # VC-specific investment thesis queries
        for vc in self.tier1_vcs:
            queries.extend([
                f"{vc} investment thesis India 2024 2025",
                f"{vc} portfolio strategy India market",
                f"{vc} India fund investment focus areas"
            ])
        
        # Sector-specific queries
        for sector in self.priority_sectors:
            queries.extend([
                f"India {sector} startup funding trends 2024",
                f"{sector} venture capital investment India thesis",
                f"Indian {sector} market analysis investment opportunities"
            ])
        
        # Thought leadership queries
        queries.extend([
            "India startup ecosystem investment outlook 2025",
            "Indian venture capital market trends analysis",
            "India unicorn valuation funding landscape",
            "Indian startup regulatory changes impact investment",
            "India vs China startup investment comparison"
        ])
        
        return queries
    
    def _is_relevant_content(self, content: str) -> bool:
        """Check if content is relevant to our focus areas"""
        content_lower = content.lower()
        
        # Check for sector keywords
        sector_keywords = [
            'consumer', 'd2c', 'saas', 'fintech', 'ai', 'artificial intelligence',
            'investment thesis', 'funding', 'venture capital', 'startup',
            'portfolio', 'market analysis', 'trends'
        ]
        
        return any(keyword in content_lower for keyword in sector_keywords)
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles based on URL and title similarity"""
        unique_results = []
        seen_urls = set()
        seen_titles = set()
        
        for result in results:
            url = result.get('url', '')
            title = result.get('title', '').lower().strip()
            
            # Skip if URL already seen
            if url in seen_urls:
                continue
            
            # Skip if very similar title already seen
            if any(self._similarity_ratio(title, seen_title) > 0.8 for seen_title in seen_titles):
                continue
            
            seen_urls.add(url)
            seen_titles.add(title)
            unique_results.append(result)
        
        return unique_results
    
    def _similarity_ratio(self, str1: str, str2: str) -> float:
        """Calculate similarity ratio between two strings"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1, str2).ratio()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return url
    
    def _parse_date(self, date_str) -> datetime:
        """Parse various date formats"""
        if not date_str:
            return datetime.now()
        
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except:
            return datetime.now()
    
    def get_search_stats(self) -> Dict[str, int]:
        """Get statistics about search performance"""
        return {
            'total_queries': len(self._generate_search_queries()),
            'active_rss_feeds': len(self.vc_rss_feeds),
            'priority_domains': len(self.priority_domains),
            'target_vcs': len(self.tier1_vcs)
        }