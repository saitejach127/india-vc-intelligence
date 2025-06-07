# India VC Intelligence Agent 🚀

An AI-powered content monitoring system that tracks investment thesis, thought leadership, and sector strategies from India's top VCs and startup ecosystem.

## Features

- **Multi-source Search**: Tavily API, RSS feeds, and targeted web searches
- **AI-powered Analysis**: OpenAI GPT-4 for content scoring and insights
- **Sector Focus**: Consumer, D2C, SaaS, Fintech, AI SaaS, Agentic AI
- **Tier 1 VC Coverage**: Peak XV, Accel, Matrix, Elevation, Lightspeed, Blume
- **Interactive Dashboard**: Real-time filtering, analytics, and trend detection
- **Learning System**: Adaptive scoring based on user feedback
- **Global + India Sources**: Comprehensive coverage with deduplication

## Quick Deploy to Streamlit Cloud

### Step 1: GitHub Setup
1. Fork this repository or create new repo with these files
2. Make repository public
3. Push all files to your repo

### Step 2: API Keys Setup
1. Get [Tavily API key](https://tavily.com) (1000 free searches/month)
2. Get [OpenAI API key](https://platform.openai.com) ($5 free credits)

### Step 3: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repo
4. Set main file: `streamlit_app.py`
5. Click "Deploy"

### Step 4: Add Secrets
1. In Streamlit Cloud dashboard, go to "Secrets"
2. Add your API keys:
```toml
TAVILY_API_KEY = "your_tavily_key_here"
OPENAI_API_KEY = "your_openai_key_here"
```

## Usage

1. **Dashboard**: View latest VC content with filtering options
2. **Search**: Click "Run Search Now" to fetch latest content
3. **Analytics**: Monitor trends, sentiment, and performance metrics
4. **Feedback**: Use 👍/👎 to train the AI scoring system
5. **Export**: Download data as CSV for further analysis

## Configuration

Key settings in `config.py`:
- **Sectors**: Modify `PRIORITY_SECTORS` to change focus areas
- **VCs**: Update `TIER1_VCS` to track different firms
- **Sources**: Add RSS feeds in `RSS_FEEDS`
- **Scoring**: Adjust weights in `SCORING_WEIGHTS`

## Architecture

```
streamlit_app.py      → Main dashboard and UI
search_engine.py      → Multi-source content discovery
content_analyzer.py   → AI-powered analysis and scoring
data_manager.py       → SQLite database operations
config.py            → Configuration and settings
```

## Cost Estimate

- Tavily API: $0-10/month (1000 searches free)
- OpenAI API: $5-15/month (depends on analysis volume)
- Streamlit Cloud: Free
- **Total: ~$10-20/month**

## Customization

### Adding New VCs
```python
# In config.py
TIER1_VCS.append("New VC Name")
RSS_FEEDS["New VC"] = "https://newvc.com/feed"
```

### Adding New Sectors
```python
# In config.py
PRIORITY_SECTORS["New Sector"] = {
    "keywords": ["keyword1", "keyword2"],
    "weight": 1.2
}
```

### Modifying Search Queries
```python
# In config.py
SEARCH_TEMPLATES["custom"] = [
    "your custom search query template"
]
```

## Troubleshooting

### Common Issues

1. **API Errors**: Check your API keys in Streamlit secrets
2. **No Results**: Verify internet connectivity and API limits
3. **Slow Performance**: Reduce search frequency or content volume
4. **Database Errors**: Check file permissions and disk space

### Debug Mode
Set `debug=True` in the sidebar to see detailed logs.

### Performance Tips
- Limit searches to avoid API rate limits
- Use filters to focus on relevant content
- Regular cleanup of old data (automated)

## Roadmap

- [ ] Email notifications for high-priority content
- [ ] Advanced ML models for better relevance scoring
- [ ] Integration with Slack/Teams for team collaboration
- [ ] Automated daily/weekly reports
- [ ] Social media monitoring (Twitter/LinkedIn)
- [ ] Mobile app version

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Streamlit Cloud logs
3. Verify API key configuration
4. Check API usage limits

## License

MIT License - feel free to modify and distribute.

---

**Built with ❤️ for the Indian startup ecosystem**