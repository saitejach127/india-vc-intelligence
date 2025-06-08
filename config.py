# Configuration file for India VC Intelligence Agent

# API Configuration
API_LIMITS = {
    'TAVILY_DAILY_LIMIT': 1000,  # Free tier limit
    'GEMINI_MONTHLY_BUDGET': 20, # USD budget (adjust as needed for Gemini)
    'SEARCH_DELAY': 0.5,  # Seconds between searches
    'MAX_CONTENT_LENGTH': 2000  # Characters for AI analysis
}

# VC Firms Configuration
TIER1_VCS = [
    "Peak XV Partners",
    "Sequoia Capital India", 
    "Accel India",
    "Matrix Partners India",
    "Elevation Capital",
    "Lightspeed India Partners",
    "Blume Ventures"
]

TIER2_VCS = [
    "Kalaari Capital",
    "Nexus Venture Partners",
    "Chiratae Ventures",
    "SAIF Partners",
    "WestBridge Capital",
    "India Quotient",
    "Stellaris Venture Partners"
]

SECTOR_SPECIALISTS = {
    "AgTech": ["Omnivore", "Ankur Capital"],
    "Climate": ["Avaana Capital", "Lightrock India"],
    "Impact": ["Omidyar Network India", "Aavishkaar Capital"],
    "Early Stage": ["Better Capital", "Titan Capital", "3one4 Capital"]
}

# Sector Keywords Configuration
PRIORITY_SECTORS = {
    "Consumer": {
        "keywords": ["consumer", "retail", "marketplace", "e-commerce", "brand"],
        "weight": 1.0
    },
    "D2C": {
        "keywords": ["d2c", "direct-to-consumer", "digital native brands", "dnb"],
        "weight": 1.2
    },
    "SaaS": {
        "keywords": ["saas", "software-as-a-service", "enterprise software", "b2b software", "cloud software"],
        "weight": 1.1
    },
    "Fintech": {
        "keywords": ["fintech", "financial technology", "payments", "neobank", "digital banking", "wealthtech"],
        "weight": 1.0
    },
    "AI SaaS": {
        "keywords": ["ai saas", "artificial intelligence software", "ai platform", "ml platform", "ai tools"],
        "weight": 1.3
    },
    "Agentic AI": {
        "keywords": ["agentic ai", "ai agents", "autonomous ai", "ai automation", "intelligent agents"],
        "weight": 1.4
    }
}

# Content Sources Configuration
PRIORITY_DOMAINS = {
    "vc_blogs": [
        "blume.vc", "accel.com", "peakxv.com", "matrixpartners.in",
        "elevationcapital.com", "lightspeedindiapartners.com"
    ],
    "news_sites": [
        "techcrunch.com", "inc42.com", "entrackr.com", "yourstory.com",
        "economictimes.indiatimes.com", "business-standard.com",
        "livemint.com", "moneycontrol.com"
    ],
    "research_sites": [
        "bain.com", "ey.com", "pwc.com", "mckinsey.com", "bcg.com"
    ]
}

# RSS Feed Sources
RSS_FEEDS = {
    "Blume Ventures": "https://blume.vc/feed",
    "Accel": "https://www.accel.com/noteworthy/feed",
    "Matrix Partners": "https://medium.com/feed/@matrixpartnersindia",
    "Lightspeed India": "https://medium.com/feed/@lightspeedindiapartners",
    "Inc42": "https://inc42.com/feed/",
    "YourStory": "https://yourstory.com/feed",
    "Entrackr": "https://entrackr.com/feed/"
}

# Search Query Templates
SEARCH_TEMPLATES = {
    "vc_thesis": [
        "{vc_firm} investment thesis India 2024 2025",
        "{vc_firm} portfolio strategy {sector} India",
        "{vc_firm} India fund investment focus",
        "{vc_firm} partner interview India market"
    ],
    "sector_analysis": [
        "India {sector} startup funding trends 2024",
        "{sector} venture capital investment India",
        "Indian {sector} market analysis opportunities",
        "{sector} unicorns India ecosystem"
    ],
    "thought_leadership": [
        "India startup ecosystem outlook 2025",
        "Indian venture capital market trends",
        "India vs global startup investment",
        "Indian startup regulatory policy impact"
    ],
    "global_india": [
        "India startup ecosystem global perspective",
        "Indian tech companies international expansion",
        "Global VCs investing India market",
        "India startup valuation global comparison"
    ]
}

# Content Analysis Configuration
INVESTMENT_KEYWORDS = [
    "investment thesis", "portfolio strategy", "market analysis", "funding trends",
    "investment focus", "sector outlook", "market opportunity", "venture capital",
    "investment philosophy", "deal flow", "due diligence", "investment criteria",
    "fund strategy", "capital deployment", "investment pipeline", "market thesis"
]

THOUGHT_LEADERSHIP_KEYWORDS = [
    "outlook", "perspective", "insights", "predictions", "forecast",
    "trends", "analysis", "strategy", "vision", "opinion", "interview",
    "discussion", "keynote", "panel", "fireside chat", "podcast"
]

# Scoring Configuration
SCORING_WEIGHTS = {
    "source_authority": {
        "tier1_vc": 25,
        "tier2_vc": 20,
        "major_news": 15,
        "business_news": 10,
        "other": 5
    },
    "content_type": {
        "investment_thesis": 20,
        "thought_leadership": 18,
        "funding_news": 15,
        "market_analysis": 12,
        "general": 8
    },
    "sector_relevance": {
        "exact_match": 15,
        "related_match": 10,
        "general_tech": 5
    },
    "recency": {
        "same_day": 10,
        "week": 8,
        "month": 5,
        "older": 0
    },
    "content_quality": {
        "substantial_content": 5,
        "financial_figures": 5,
        "expert_quotes": 3
    }
}

# Priority Assignment Rules
PRIORITY_RULES = {
    "high": {
        "min_score": 80,
        "tier1_vc": True,
        "hot_sectors": ["AI SaaS", "Agentic AI"],
        "content_types": ["investment_thesis", "thought_leadership"]
    },
    "medium": {
        "min_score": 60,
        "tier2_vc": True,
        "multiple_sectors": 2,
        "recent_days": 7
    },
    "low": {
        "min_score": 0,
        "default": True
    }
}

# Theme Clustering Configuration
THEME_KEYWORDS = {
    "ai_revolution": [
        "artificial intelligence", "ai", "machine learning", "generative ai",
        "llm", "chatgpt", "automation", "ai agents", "neural networks"
    ],
    "funding_environment": [
        "funding winter", "funding spring", "valuation", "ipo market",
        "public markets", "late stage", "growth capital", "dry powder"
    ],
    "consumer_evolution": [
        "d2c brands", "quick commerce", "tier 2 cities", "rural markets",
        "digital adoption", "consumer behavior", "omnichannel"
    ],
    "enterprise_growth": [
        "b2b saas", "enterprise software", "vertical saas", "workflow automation",
        "digital transformation", "enterprise ai", "api economy"
    ],
    "regulatory_landscape": [
        "rbi guidelines", "sebi regulations", "government policy", "compliance",
        "data protection", "cross border", "fdi policy", "taxation"
    ],
    "exit_opportunities": [
        "ipo", "acquisition", "strategic sale", "secondary transactions",
        "public listing", "exit strategy", "liquidity events"
    ],
    "geographic_expansion": [
        "global expansion", "us market", "southeast asia", "middle east",
        "cross border", "international", "offshore", "gti"
    ],
    "technology_adoption": [
        "digital transformation", "cloud adoption", "mobile first",
        "api integration", "microservices", "devops", "cybersecurity"
    ]
}

# Data Management Configuration
DATABASE_CONFIG = {
    "retention_days": 365,
    "cleanup_frequency": "weekly",
    "backup_frequency": "daily",
    "max_db_size_mb": 500
}

# Performance Monitoring
PERFORMANCE_METRICS = {
    "search_execution_time": {"target": 30, "unit": "seconds"},
    "content_analysis_time": {"target": 5, "unit": "seconds"},
    "relevance_accuracy": {"target": 80, "unit": "percentage"},
    "duplicate_rate": {"target": 5, "unit": "percentage"}
}

# Notification Configuration
ALERTS = {
    "high_priority_threshold": 5,  # Alert if more than 5 high priority articles
    "sentiment_shift": 0.3,  # Alert on significant sentiment changes
    "new_trend_threshold": 10,  # Alert on emerging trends
    "funding_spike_threshold": 50  # Alert on funding activity spikes
}

# Export Configuration
EXPORT_FORMATS = {
    "csv": {"enabled": True, "columns": "all"},
    "json": {"enabled": True, "format": "structured"},
    "pdf": {"enabled": False, "template": "summary"},
    "excel": {"enabled": True, "sheets": ["content", "analytics", "trends"]}
}

# Feedback Learning Configuration
LEARNING_CONFIG = {
    "feedback_weight": 0.2,  # How much user feedback influences scoring
    "adaptation_rate": 0.1,  # How quickly the system adapts
    "minimum_feedback_count": 5,  # Minimum feedback needed for learning
    "confidence_threshold": 0.7  # Confidence threshold for automated decisions
}

# Scheduling Configuration
SCHEDULER_CONFIG = {
    "daily_search_time": "07:00",  # IST
    "evening_update_time": "19:00",  # IST
    "weekly_cleanup_day": "sunday",
    "monthly_report_day": 1
}

# Rate Limiting Configuration
RATE_LIMITS = {
    "tavily_requests_per_minute": 30,
    "openai_requests_per_minute": 60,
    "web_scraping_delay": 1.0,
    "max_concurrent_requests": 5
}

# Error Handling Configuration
ERROR_CONFIG = {
    "max_retries": 3,
    "retry_delay": 2,  # seconds
    "timeout": 30,  # seconds
    "fallback_sources": True
}

# Display Configuration
UI_CONFIG = {
    "items_per_page": 20,
    "summary_length": 200,  # characters
    "max_tags_display": 5,
    "chart_colors": ["#667eea", "#764ba2", "#f093fb", "#f5576c"],
    "refresh_interval": 300  # seconds
}