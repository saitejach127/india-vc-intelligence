import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import streamlit as st

class DataManager:
    def __init__(self, db_path: str = "vc_intelligence.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main content table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                content TEXT,
                source TEXT,
                author TEXT,
                date_published DATETIME,
                date_scraped DATETIME DEFAULT CURRENT_TIMESTAMP,
                search_query TEXT,
                raw_score REAL,
                relevance_score INTEGER,
                sectors TEXT,
                vc_firm TEXT,
                priority TEXT,
                insights TEXT,
                summary TEXT,
                content_type TEXT,
                sentiment TEXT,
                key_topics TEXT,
                analysis_timestamp DATETIME,
                user_feedback INTEGER DEFAULT 0
            )
        """)
        
        # User feedback table for learning
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER,
                feedback_type TEXT,
                feedback_value INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
        """)
        
        # Search performance metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_date DATE,
                total_results INTEGER,
                high_priority_count INTEGER,
                avg_relevance_score REAL,
                sources_searched TEXT,
                execution_time REAL
            )
        """)
        
        # Trending themes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS themes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme_name TEXT,
                frequency INTEGER,
                relevance_score REAL,
                first_seen DATE,
                last_seen DATE,
                related_articles TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_content(self, content_list: List[Dict[str, Any]]) -> int:
        """Store analyzed content in database"""
        if not content_list:
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stored_count = 0
        
        for content in content_list:
            try:
                # Check if URL already exists
                cursor.execute("SELECT id FROM content WHERE url = ?", (content.get('url'),))
                if cursor.fetchone():
                    continue  # Skip duplicates
                
                # Prepare data for insertion
                insert_data = (
                    content.get('title', ''),
                    content.get('url', ''),
                    content.get('content', ''),
                    content.get('source', ''),
                    content.get('author', ''),
                    content.get('date_published'),
                    content.get('search_query', ''),
                    content.get('raw_score', 0),
                    content.get('relevance_score', 0),
                    content.get('sectors', ''),
                    content.get('vc_firm', ''),
                    content.get('priority', ''),
                    content.get('insights', ''),
                    content.get('summary', ''),
                    content.get('content_type', ''),
                    content.get('sentiment', ''),
                    json.dumps(content.get('key_topics', [])),
                    content.get('analysis_timestamp')
                )
                
                cursor.execute("""
                    INSERT INTO content (
                        title, url, content, source, author, date_published,
                        search_query, raw_score, relevance_score, sectors,
                        vc_firm, priority, insights, summary, content_type,
                        sentiment, key_topics, analysis_timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, insert_data)
                
                stored_count += 1
                
            except Exception as e:
                st.warning(f"Failed to store content: {content.get('title', 'Unknown')} - {str(e)}")
                continue
        
        conn.commit()
        conn.close()
        
        return stored_count
    
    def get_filtered_content(self, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           sector: Optional[str] = None,
                           vc_firm: Optional[str] = None,
                           priority: Optional[str] = None,
                           limit: int = 100) -> pd.DataFrame:
        """Retrieve filtered content from database"""
        
        conn = sqlite3.connect(self.db_path)
        
        # Build dynamic query
        query = "SELECT * FROM content WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date_published >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date_published <= ?"
            params.append(end_date)
        
        if sector and sector != "All":
            query += " AND sectors LIKE ?"
            params.append(f"%{sector}%")
        
        if vc_firm and vc_firm != "All":
            query += " AND vc_firm LIKE ?"
            params.append(f"%{vc_firm}%")
        
        if priority and priority != "All":
            query += " AND priority = ?"
            params.append(priority)
        
        query += " ORDER BY relevance_score DESC, date_published DESC"
        query += f" LIMIT {limit}"
        
        try:
            df = pd.read_sql_query(query, conn, params=params)
            
            # Convert date columns
            if 'date_published' in df.columns:
                df['date_published'] = pd.to_datetime(df['date_published'])
            
            conn.close()
            return df
        
        except Exception as e:
            conn.close()
            st.error(f"Database query failed: {str(e)}")
            return pd.DataFrame()
    
    def get_all_content(self) -> pd.DataFrame:
        """Get all content for export"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            df = pd.read_sql_query("SELECT * FROM content ORDER BY date_published DESC", conn)
            conn.close()
            return df
        except Exception as e:
            conn.close()
            st.error(f"Failed to retrieve all content: {str(e)}")
            return pd.DataFrame()
    
    def store_user_feedback(self, content_id: int, feedback_value: int):
        """Store user feedback for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Store feedback
            cursor.execute("""
                INSERT INTO feedback (content_id, feedback_type, feedback_value)
                VALUES (?, 'relevance', ?)
            """, (content_id, feedback_value))
            
            # Update content user_feedback score
            cursor.execute("""
                UPDATE content 
                SET user_feedback = user_feedback + ?
                WHERE id = ?
            """, (feedback_value, content_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            conn.close()
            st.error(f"Failed to store feedback: {str(e)}")
    
    def get_trending_themes(self, days: int = 7) -> Dict[str, Any]:
        """Get trending themes from recent content"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Get recent content
            query = """
                SELECT sectors, key_topics, content_type, priority
                FROM content 
                WHERE date_published >= date('now', '-{} days')
            """.format(days)
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return {}
            
            # Analyze trends
            trends = {
                'top_sectors': df['sectors'].value_counts().head(5).to_dict(),
                'content_types': df['content_type'].value_counts().to_dict(),
                'priority_distribution': df['priority'].value_counts().to_dict(),
                'total_articles': len(df)
            }
            
            return trends
            
        except Exception as e:
            conn.close()
            st.error(f"Failed to get trending themes: {str(e)}")
            return {}
    
    def get_search_performance_stats(self) -> Dict[str, Any]:
        """Get search performance statistics"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Recent performance
            recent_stats = pd.read_sql_query("""
                SELECT 
                    COUNT(*) as total_articles,
                    AVG(relevance_score) as avg_score,
                    COUNT(CASE WHEN priority = 'High' THEN 1 END) as high_priority,
                    COUNT(DISTINCT source) as unique_sources,
                    COUNT(DISTINCT vc_firm) as unique_vcs
                FROM content 
                WHERE date_scraped >= date('now', '-7 days')
            """, conn)
            
            # Daily trend
            daily_trend = pd.read_sql_query("""
                SELECT 
                    DATE(date_scraped) as date,
                    COUNT(*) as count,
                    AVG(relevance_score) as avg_score
                FROM content 
                WHERE date_scraped >= date('now', '-30 days')
                GROUP BY DATE(date_scraped)
                ORDER BY date
            """, conn)
            
            conn.close()
            
            return {
                'recent_stats': recent_stats.iloc[0].to_dict() if not recent_stats.empty else {},
                'daily_trend': daily_trend.to_dict('records')
            }
            
        except Exception as e:
            conn.close()
            st.error(f"Failed to get performance stats: {str(e)}")
            return {}
    
    def cleanup_old_data(self, days: int = 365):
        """Remove data older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete old content
            cursor.execute("""
                DELETE FROM content 
                WHERE date_scraped < date('now', '-{} days')
            """.format(days))
            
            # Delete old feedback
            cursor.execute("""
                DELETE FROM feedback 
                WHERE timestamp < date('now', '-{} days')
            """.format(days))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
            
        except Exception as e:
            conn.close()
            st.error(f"Cleanup failed: {str(e)}")
            return 0
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Analyze user feedback patterns for learning"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Get feedback patterns
            feedback_analysis = pd.read_sql_query("""
                SELECT 
                    c.source,
                    c.vc_firm,
                    c.sectors,
                    c.content_type,
                    AVG(c.user_feedback) as avg_feedback,
                    COUNT(f.id) as feedback_count
                FROM content c
                LEFT JOIN feedback f ON c.id = f.content_id
                WHERE c.user_feedback != 0
                GROUP BY c.source, c.vc_firm, c.sectors, c.content_type
                HAVING feedback_count > 0
                ORDER BY avg_feedback DESC
            """, conn)
            
            conn.close()
            
            if feedback_analysis.empty:
                return {'message': 'No feedback data available yet'}
            
            insights = {
                'top_sources': feedback_analysis.nlargest(5, 'avg_feedback')[['source', 'avg_feedback']].to_dict('records'),
                'top_vcs': feedback_analysis.nlargest(5, 'avg_feedback')[['vc_firm', 'avg_feedback']].to_dict('records'),
                'preferred_content_types': feedback_analysis.groupby('content_type')['avg_feedback'].mean().to_dict(),
                'total_feedback_items': len(feedback_analysis)
            }
            
            return insights
            
        except Exception as e:
            conn.close()
            st.error(f"Failed to analyze feedback: {str(e)}")
            return {}
    
    def update_relevance_scoring_model(self):
        """Update the relevance scoring based on user feedback"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Get articles with feedback
            feedback_data = pd.read_sql_query("""
                SELECT 
                    c.id,
                    c.source,
                    c.vc_firm,
                    c.sectors,
                    c.content_type,
                    c.relevance_score,
                    AVG(f.feedback_value) as user_score
                FROM content c
                JOIN feedback f ON c.id = f.content_id
                GROUP BY c.id
            """, conn)
            
            if not feedback_data.empty:
                # Calculate adjustment factors
                for _, row in feedback_data.iterrows():
                    # Simple learning: adjust future scoring based on feedback
                    adjustment = (row['user_score'] - row['relevance_score']) * 0.1
                    
                    # Store adjustment logic (this is a simplified version)
                    # In production, you'd implement more sophisticated ML here
                    pass
            
            conn.close()
            return True
            
        except Exception as e:
            conn.close()
            st.error(f"Model update failed: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get overall database statistics"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            stats = {}
            
            # Basic counts
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM content")
            stats['total_articles'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM feedback")
            stats['total_feedback'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT source) FROM content")
            stats['unique_sources'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT vc_firm) FROM content WHERE vc_firm != 'Unknown'")
            stats['tracked_vcs'] = cursor.fetchone()[0]
            
            # Date range
            cursor.execute("SELECT MIN(date_published), MAX(date_published) FROM content")
            date_range = cursor.fetchone()
            stats['date_range'] = {
                'earliest': date_range[0],
                'latest': date_range[1]
            }
            
            conn.close()
            return stats
            
        except Exception as e:
            conn.close()
            st.error(f"Failed to get database stats: {str(e)}")
            return {}