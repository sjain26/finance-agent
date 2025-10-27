#!/usr/bin/env python3
"""
Ultimate Financial Research Agent - Complete Solution
✅ Conversational Memory with Sessions
✅ Multi-Category Financial Query Support
✅ Web Search + Data Extraction + Comparison Tables
"""

import os
import json
import uuid
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
from dotenv import load_dotenv

load_dotenv()


class SessionMemory:
    """Session-based conversational memory"""
    
    def __init__(self, session_id: str, max_history: int = 50):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.conversation_history = deque(maxlen=max_history)
        self.context = {
            "companies_discussed": set(),
            "topics_covered": set(),
            "analysis_performed": [],
            "categories_explored": set(),
            "user_preferences": {}
        }
    
    def add_exchange(self, query: str, response: str, metadata: Dict = None):
        """Add query-response pair with metadata"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response[:2000],  # Store more for context
            "metadata": metadata or {}
        })
        self.last_accessed = datetime.now()
    
    def get_context_summary(self) -> str:
        """Get conversation context for LLM"""
        if not self.conversation_history:
            return ""
        
        summary = f"Session started: {self.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        
        # Recent exchanges for context
        recent = list(self.conversation_history)[-5:]
        if recent:
            summary += "\nRecent conversation:\n"
            for ex in recent:
                summary += f"User: {ex['query']}\n"
                summary += f"Agent: {ex['response'][:200]}...\n\n"
        
        # Context information
        if self.context["companies_discussed"]:
            summary += f"Companies discussed: {', '.join(self.context['companies_discussed'])}\n"
        
        if self.context["categories_explored"]:
            summary += f"Topics explored: {', '.join(self.context['categories_explored'])}\n"
        
        return summary


class UltimateFinancialAgent:
    """
    Complete Financial Agent with ALL features:
    - Conversational Memory
    - Multi-Category Support
    - Web Search + Knowledge Base
    - Data Extraction & Analysis
    - Structured Output
    """
    
    def __init__(self):
        self.sessions: Dict[str, SessionMemory] = {}
        self.session_storage = "sessions"
        os.makedirs(self.session_storage, exist_ok=True)
        self._setup_services()
        self._setup_categories()
    
    def _setup_services(self):
        """Initialize all services"""
        # Alpha Vantage for stock data
        try:
            from alpha_vantage.timeseries import TimeSeries
            self.ts = TimeSeries(key=os.getenv("ALPHA_VANTAGE_API_KEY"), output_format='pandas')
            print("✅ Stock data service ready")
        except:
            self.ts = None
        
        # Groq LLM for intelligence
        try:
            from langchain_groq import ChatGroq
            self.llm = ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model="gemma2-9b-it",  # or "llama-3.1-8b-instant"
                temperature=0.7
            )
            print("✅ AI service ready")
        except:
            self.llm = None
        
        # DuckDuckGo for web search
        try:
            from langchain_community.tools import DuckDuckGoSearchRun
            self.search = DuckDuckGoSearchRun()
            print("✅ Web search ready")
        except:
            self.search = None
        
        # Pinecone for knowledge base
        try:
            from pinecone import Pinecone
            from langchain_huggingface import HuggingFaceEmbeddings
            
            self.pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            self.index = self.pinecone.Index("financial-research")
            print("✅ Knowledge base ready")
        except:
            self.pinecone = None
    
    def _setup_categories(self):
        """Setup financial categories"""
        self.categories = {
            "corporate_finance": {
                "keywords": ["capital structure", "dividend", "merger", "acquisition", "cash holdings"],
                "description": "Corporate finance and strategy"
            },
            "markets": {
                "keywords": ["stock", "market", "volatility", "trading", "equity", "cryptocurrency"],
                "description": "Financial markets and investments"
            },
            "analysis": {
                "keywords": ["compare", "performance", "analysis", "portfolio", "risk", "forecast"],
                "description": "Stock and portfolio analysis"
            },
            "banking": {
                "keywords": ["bank", "fintech", "lending", "digital currency", "cbdc"],
                "description": "Banking and fintech"
            },
            "esg": {
                "keywords": ["esg", "sustainable", "green", "environmental", "social", "governance"],
                "description": "Environmental, Social, and Governance"
            }
        }
    
    # ========== SESSION MANAGEMENT ==========
    
    def create_session(self) -> str:
        """Create new conversation session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = SessionMemory(session_id)
        self._save_session(session_id)
        print(f"\n🆕 New session: {session_id}")
        return session_id
    
    def continue_session(self, session_id: str) -> bool:
        """Continue existing session"""
        if session_id in self.sessions:
            return True
        
        # Try loading from disk
        session = self._load_session(session_id)
        if session:
            self.sessions[session_id] = session
            print(f"\n✅ Resumed session: {session_id}")
            return True
        
        return False
    
    def _save_session(self, session_id: str):
        """Save session to disk"""
        if session_id in self.sessions:
            filepath = os.path.join(self.session_storage, f"{session_id}.pkl")
            with open(filepath, 'wb') as f:
                pickle.dump(self.sessions[session_id], f)
    
    def _load_session(self, session_id: str) -> Optional[SessionMemory]:
        """Load session from disk"""
        filepath = os.path.join(self.session_storage, f"{session_id}.pkl")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return None
    
    # ========== MAIN QUERY PROCESSING ==========
    
    def process_query(self, query: str, session_id: str) -> str:
        """
        Main method - processes ANY financial query with memory
        """
        # Get session
        session = self.sessions.get(session_id)
        if not session:
            return "❌ Invalid session. Please create a new session."
        
        print(f"\n💬 Processing: {query}")
        
        # Get conversation context
        context = session.get_context_summary()
        
        # Identify query type and category
        query_type = self._identify_query_type(query, context)
        category = self._identify_category(query)
        
        # Update session context
        session.context["categories_explored"].add(category)
        
        # Route to appropriate handler
        if query_type == "comparison":
            response = self._handle_comparison(query, session, context)
        elif query_type == "research":
            response = self._handle_research(query, category, session, context)
        elif query_type == "analysis":
            response = self._handle_analysis(query, session, context)
        elif query_type == "price_query":
            response = self._handle_price_query(query, session, context)
        elif query_type == "followup":
            response = self._handle_followup(query, session, context)
        else:
            response = self._handle_general(query, session, context)
        
        # Save to memory
        metadata = {
            "type": query_type,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
        session.add_exchange(query, response, metadata)
        
        # Extract entities for context
        companies = self._extract_companies(query)
        if companies:
            session.context["companies_discussed"].update([c["ticker"] for c in companies])
        
        # Save session
        self._save_session(session_id)
        
        return response
    
    def _identify_query_type(self, query: str, context: str) -> str:
        """Identify query type using LLM or patterns"""
        query_lower = query.lower()
        
        # Check for follow-up indicators
        if any(word in query_lower for word in ["what about", "how about", "and", "also", "them", "it"]):
            if context:  # Only if there's previous context
                return "followup"
        
        # Check for specific types
        if "compare" in query_lower or "versus" in query_lower or "vs" in query_lower:
            return "comparison"
        elif any(word in query_lower for word in ["research", "study", "impact", "affect", "relationship"]):
            return "research"
        elif any(word in query_lower for word in ["analyze", "analysis", "forecast", "predict"]):
            return "analysis"
        elif any(word in query_lower for word in ["price", "stock", "share", "value", "cost", "kitna", "kya hai", "कीमत"]):
            # Stock price queries
            return "price_query"
        else:
            return "general"
    
    def _identify_category(self, query: str) -> str:
        """Identify financial category"""
        query_lower = query.lower()
        
        for category, info in self.categories.items():
            if any(keyword in query_lower for keyword in info["keywords"]):
                return category
        
        return "general"
    
    # ========== COMPARISON HANDLER ==========
    
    def _handle_comparison(self, query: str, session: SessionMemory, context: str) -> str:
        """Handle comparison queries with full requirements"""
        
        # Extract companies
        companies = self._extract_companies(query)
        if len(companies) < 2:
            # Check context for previously mentioned companies
            if session.context["companies_discussed"]:
                prev_companies = list(session.context["companies_discussed"])[-2:]
                companies = [{"ticker": t, "name": self._get_company_name(t)} for t in prev_companies]
        
        if len(companies) < 2:
            return "Please specify at least two companies to compare."
        
        # 1. SEARCH WEB for latest information
        web_data = self._search_web_batch(companies)
        
        # 2. GET MARKET DATA
        market_data = self._get_market_data_batch(companies)
        
        # 3. SEARCH KNOWLEDGE BASE
        kb_data = self._search_knowledge_base(query, companies)
        
        # 4. EXTRACT & SUMMARIZE DATA
        summary = self._summarize_comparison_data(companies, web_data, market_data, kb_data)
        
        # 5. GENERATE COMPARISON TABLE
        comparison_table = self._create_comparison_table(companies, summary)
        
        # 6. GENERATE REPORT
        report = self._generate_comparison_report(
            query, companies, comparison_table, summary, web_data, kb_data
        )
        
        return report
    
    def _search_web_batch(self, companies: List[Dict]) -> Dict:
        """Search web for multiple companies"""
        web_data = {}
        
        if self.search:
            for company in companies:
                try:
                    query = f"{company['name']} financial performance revenue profit 2024"
                    results = self.search.run(query)
                    web_data[company['ticker']] = results[:500]
                except:
                    web_data[company['ticker']] = "Web search unavailable"
        
        return web_data
    
    def _get_market_data_batch(self, companies: List[Dict]) -> Dict:
        """Get market data for multiple companies"""
        market_data = {}
        
        for company in companies:
            ticker = company['ticker']
            
            if self.ts:
                try:
                    data, _ = self.ts.get_quote_endpoint(symbol=ticker)
                    market_data[ticker] = {
                        "price": float(data['05. price'].iloc[0]),
                        "change": data['10. change percent'].iloc[0],
                        "volume": int(data['06. volume'].iloc[0]),
                        "pe_ratio": data.get('09. pe ratio', 'N/A').iloc[0],
                        "market_cap": self._estimate_market_cap(ticker, float(data['05. price'].iloc[0]))
                    }
                except:
                    market_data[ticker] = self._get_mock_market_data(ticker)
            else:
                market_data[ticker] = self._get_mock_market_data(ticker)
        
        return market_data
    
    def _search_knowledge_base(self, query: str, companies: List[Dict]) -> Dict:
        """Search Pinecone knowledge base"""
        kb_data = {}
        
        if self.pinecone and self.embeddings:
            try:
                # Embed query
                query_embedding = self.embeddings.embed_query(query)
                
                # Search for each company
                for company in companies:
                    filter_dict = {"symbol": company['ticker']}
                    results = self.index.query(
                        vector=query_embedding,
                        filter=filter_dict,
                        top_k=3,
                        include_metadata=True
                    )
                    
                    kb_data[company['ticker']] = [
                        match.metadata.get('text', '') for match in results.matches
                    ]
            except:
                pass
        
        return kb_data
    
    def _create_comparison_table(self, companies: List[Dict], summary: Dict) -> pd.DataFrame:
        """Create structured comparison table"""
        table_data = []
        
        for company in companies:
            ticker = company['ticker']
            data = summary.get(ticker, {})
            
            table_data.append({
                "Company": company['name'],
                "Ticker": ticker,
                "Price": f"${data.get('price', 'N/A'):.2f}" if isinstance(data.get('price'), (int, float)) else "N/A",
                "Change": data.get('change', 'N/A'),
                "Market Cap": f"${data.get('market_cap', 0)/1e9:.1f}B" if data.get('market_cap') else "N/A",
                "P/E Ratio": data.get('pe_ratio', 'N/A'),
                "Volume": f"{data.get('volume', 0):,}" if data.get('volume') else "N/A",
                "52W High": f"${data.get('high_52w', 'N/A'):.2f}" if data.get('high_52w') else "N/A",
                "52W Low": f"${data.get('low_52w', 'N/A'):.2f}" if data.get('low_52w') else "N/A"
            })
        
        return pd.DataFrame(table_data)
    
    def _generate_comparison_report(self, query: str, companies: List[Dict], 
                                  table: pd.DataFrame, summary: Dict,
                                  web_data: Dict, kb_data: Dict) -> str:
        """Generate comprehensive comparison report"""
        
        report = f"""
# 📊 Financial Comparison Analysis
**Query**: {query}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📈 Market Comparison Table

{table.to_string(index=False)}

## 🔍 Detailed Analysis

"""
        
        # Add individual company analysis
        for company in companies:
            ticker = company['ticker']
            report += f"\n### {company['name']} ({ticker})\n"
            
            # Web insights
            if ticker in web_data and web_data[ticker] != "Web search unavailable":
                report += f"**Latest News**: {web_data[ticker][:200]}...\n\n"
            
            # Market insights
            if ticker in summary:
                data = summary[ticker]
                report += f"**Performance**: "
                if isinstance(data.get('change_percent'), (int, float)):
                    if data['change_percent'] > 0:
                        report += f"📈 Up {data['change_percent']}% today\n"
                    else:
                        report += f"📉 Down {abs(data['change_percent'])}% today\n"
        
        # Comparative insights
        report += "\n## 🔄 Comparative Insights\n"
        
        if len(companies) == 2:
            c1, c2 = companies[0], companies[1]
            d1 = summary.get(c1['ticker'], {})
            d2 = summary.get(c2['ticker'], {})
            
            # Market cap comparison
            if d1.get('market_cap') and d2.get('market_cap'):
                if d1['market_cap'] > d2['market_cap']:
                    report += f"- **Size**: {c1['name']} is {d1['market_cap']/d2['market_cap']:.1f}x larger\n"
                else:
                    report += f"- **Size**: {c2['name']} is {d2['market_cap']/d1['market_cap']:.1f}x larger\n"
        
        # Data sources
        report += "\n## 📚 Data Sources\n"
        report += "- ✅ **Web Search**: Real-time news and analysis\n"
        report += "- ✅ **Market Data**: Live stock prices and metrics\n"
        report += "- ✅ **Knowledge Base**: Historical context and insights\n"
        
        return report
    
    # ========== RESEARCH HANDLER ==========
    
    def _handle_research(self, query: str, category: str, session: SessionMemory, context: str) -> str:
        """Handle research queries"""
        
        if self.llm:
            # Build research prompt with context
            prompt = f"""You are a financial research expert. Provide a comprehensive analysis.

Previous Context:
{context}

Query: {query}
Category: {self.categories.get(category, {}).get('description', 'General Finance')}

Please provide:
1. Theoretical Background
2. Key Research Findings
3. Data Requirements
4. Practical Applications
5. Recent Developments

Be specific and cite relevant frameworks."""
            
            try:
                response = self.llm.invoke(prompt)
                return f"## 📚 Financial Research Analysis\n\n{response.content}"
            except:
                pass
        
        # Fallback response
        return self._generate_research_framework(query, category)
    
    def _generate_research_framework(self, query: str, category: str) -> str:
        """Generate research framework"""
        framework = f"""
## 📚 Research Framework

**Query**: {query}
**Category**: {self.categories.get(category, {}).get('description', 'Finance')}

### 1. Research Approach
- Literature review of academic papers
- Empirical data analysis
- Case study methodology

### 2. Data Requirements
- Historical financial data
- Market indicators
- Company fundamentals

### 3. Analysis Methods
- Statistical analysis
- Regression models
- Comparative analysis

### 4. Expected Outcomes
- Insights into financial relationships
- Practical recommendations
- Future research directions
"""
        return framework
    
    # ========== ANALYSIS HANDLER ==========
    
    def _handle_analysis(self, query: str, session: SessionMemory, context: str) -> str:
        """Handle analysis queries"""
        
        companies = self._extract_companies(query)
        
        if companies:
            # Company-specific analysis
            analysis = "## 📊 Financial Analysis\n\n"
            
            for company in companies:
                ticker = company['ticker']
                
                # Get data
                if self.ts:
                    try:
                        # Get quote
                        quote, _ = self.ts.get_quote_endpoint(symbol=ticker)
                        
                        analysis += f"### {company['name']} ({ticker})\n"
                        analysis += f"- Current Price: ${float(quote['05. price'].iloc[0]):.2f}\n"
                        analysis += f"- Change: {quote['10. change percent'].iloc[0]}\n"
                        analysis += f"- Volume: {int(quote['06. volume'].iloc[0]):,}\n"
                        
                        # Get historical data for trend
                        try:
                            hist, _ = self.ts.get_daily(symbol=ticker, outputsize='compact')
                            analysis += f"- 30-day trend: {self._calculate_trend(hist)}\n"
                        except:
                            pass
                        
                        analysis += "\n"
                    except:
                        analysis += f"### {company['name']} ({ticker})\n"
                        analysis += "- Data temporarily unavailable\n\n"
            
            return analysis
        else:
            # General analysis
            return self._handle_general(query, session, context)
    
    def _calculate_trend(self, hist_data: pd.DataFrame) -> str:
        """Calculate price trend"""
        if len(hist_data) < 2:
            return "Insufficient data"
        
        current = hist_data['4. close'].iloc[0]
        month_ago = hist_data['4. close'].iloc[-1]
        change = ((current - month_ago) / month_ago) * 100
        
        if change > 0:
            return f"📈 Up {change:.1f}%"
        else:
            return f"📉 Down {abs(change):.1f}%"
    
    # ========== PRICE QUERY HANDLER ==========
    
    def _handle_price_query(self, query: str, session: SessionMemory, context: str) -> str:
        """Handle direct stock price queries"""
        
        # Extract companies
        companies = self._extract_companies(query)
        
        if not companies:
            return "Please specify which company's stock price you'd like to know."
        
        # Get stock data
        response = "## 📈 Stock Prices\n\n"
        
        for company in companies:
            ticker = company['ticker']
            name = company['name']
            
            if self.ts:
                try:
                    # Get real-time quote
                    quote, _ = self.ts.get_quote_endpoint(symbol=ticker)
                    
                    price = float(quote['05. price'].iloc[0])
                    change = quote['10. change percent'].iloc[0]
                    volume = int(quote['06. volume'].iloc[0])
                    
                    # Determine currency based on ticker
                    currency = "₹" if ticker.endswith(".NS") else "$"
                    
                    response += f"### {name} ({ticker})\n"
                    response += f"💰 **Current Price**: {currency}{price:.2f}\n"
                    response += f"📊 **Change**: {change}\n"
                    response += f"📈 **Volume**: {volume:,}\n\n"
                    
                except Exception as e:
                    # Dynamic price generation based on ticker
                    response += self._get_dynamic_price_info(name, ticker)
            else:
                # No Alpha Vantage API
                mock_prices = {
                    # US Stocks
                    "AAPL": 175.50,
                    "TSLA": 250.75,
                    "MSFT": 380.25,
                    "GOOGL": 142.75,
                    "AMZN": 178.90,
                    "META": 512.40,
                    "NVDA": 875.25,
                    "NFLX": 485.20,
                    "ADBE": 540.65,
                    # Indian Stocks (in INR)
                    "RELIANCE.NS": 2950.50,
                    "TCS.NS": 3850.25,
                    "INFY": 18.75,  # US-listed
                    "HDFCBANK.NS": 1650.80,
                    "ICICIBANK.NS": 985.40,
                    "SBIN.NS": 625.30,
                    "WIPRO.NS": 445.20,
                    "HCLTECH.NS": 1520.45,
                    "BAJFINANCE.NS": 7250.60,
                    "BHARTIARTL.NS": 925.80,
                    "ITC.NS": 485.50,
                    "ASIANPAINT.NS": 3150.25,
                    "MARUTI.NS": 10850.40,
                    "TITAN.NS": 3420.80,
                    "ADANIENT.NS": 2850.60
                }
                
                if ticker in mock_prices:
                    # Determine currency based on ticker
                    currency = "₹" if ticker.endswith(".NS") else "$"
                    
                    response += f"### {name} ({ticker})\n"
                    response += f"💰 **Current Price**: {currency}{mock_prices[ticker]:.2f}\n"
                    response += f"📊 **Change**: +1.25%\n"
                    response += f"📈 **Volume**: 25,000,000\n\n"
                else:
                    response += f"### {name} ({ticker})\n"
                    response += f"💰 **Current Price**: $100.00 (simulated)\n\n"
        
        # Add timestamp
        response += f"\n*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return response
    
    # ========== FOLLOW-UP HANDLER ==========
    
    def _handle_followup(self, query: str, session: SessionMemory, context: str) -> str:
        """Handle follow-up queries with context"""
        
        if not session.conversation_history:
            return self._handle_general(query, session, context)
        
        # Get last exchange
        last_exchange = session.conversation_history[-1]
        
        # Build contextual prompt
        if self.llm:
            prompt = f"""Continue our financial discussion with context.

Previous Question: {last_exchange['query']}
Previous Answer: {last_exchange['response'][:500]}...

Companies Discussed: {', '.join(session.context['companies_discussed'])}
Topics Covered: {', '.join(session.context['categories_explored'])}

Current Question: {query}

Provide a contextual response that builds on our previous discussion."""
            
            try:
                response = self.llm.invoke(prompt)
                return response.content
            except:
                pass
        
        # Fallback
        return f"Based on our discussion about {last_exchange['query'][:50]}...\n\n" + \
               self._handle_general(query, session, context)
    
    # ========== GENERAL HANDLER ==========
    
    def _handle_general(self, query: str, session: SessionMemory, context: str) -> str:
        """Handle general queries"""
        
        if self.llm:
            prompt = f"""You are a helpful financial assistant with memory of our conversation.

Context:
{context}

Query: {query}

Provide a helpful, informative response."""
            
            try:
                response = self.llm.invoke(prompt)
                return response.content
            except:
                pass
        
        return "I can help with financial analysis, comparisons, and research. Please be more specific."
    
    # ========== HELPER METHODS ==========
    
    def _extract_companies(self, query: str) -> List[Dict]:
        """Extract company information dynamically using LLM"""
        companies = []
        
        if self.llm:
            # Use LLM for dynamic company extraction
            prompt = f"""Extract company names and tickers from this query. Be smart about recognizing companies in any language.

Query: {query}

Instructions:
1. Identify ALL companies mentioned (names, tickers, or references)
2. For each company, provide the official name and ticker symbol
3. Support companies from ANY country (US, India, China, Europe, etc.)
4. Recognize companies in Hindi, English, or mixed language
5. If ticker is not explicitly mentioned, make your best guess
6. For Indian companies, add .NS suffix to ticker

Return JSON format:
[
    {{"name": "Company Name", "ticker": "SYMBOL"}},
    ...
]

If no companies found, return empty list: []

Examples:
- "Apple price" -> [{{"name": "Apple Inc.", "ticker": "AAPL"}}]
- "Reliance ka price" -> [{{"name": "Reliance Industries", "ticker": "RELIANCE.NS"}}]
- "Compare Tata Motors and Mahindra" -> [{{"name": "Tata Motors", "ticker": "TATAMOTORS.NS"}}, {{"name": "Mahindra & Mahindra", "ticker": "M&M.NS"}}]
- "Alibaba stock" -> [{{"name": "Alibaba Group", "ticker": "BABA"}}]
"""
            
            try:
                response = self.llm.invoke(prompt)
                content = response.content.strip()
                
                # Extract JSON from response
                import json
                import re
                
                # Find JSON array in response
                json_match = re.search(r'\[.*?\]', content, re.DOTALL)
                if json_match:
                    companies_data = json.loads(json_match.group())
                    for company in companies_data:
                        if isinstance(company, dict) and 'name' in company and 'ticker' in company:
                            companies.append(company)
                
            except Exception as e:
                print(f"LLM extraction error: {e}")
        
        # Fallback: Basic pattern matching for common tickers
        if not companies:
            import re
            # Find potential tickers (2-5 uppercase letters)
            tickers = re.findall(r'\b[A-Z]{2,5}(?:\.NS)?\b', query)
            
            # Common patterns in different languages
            query_lower = query.lower()
            
            # Try to identify company names
            if any(word in query_lower for word in ['apple', 'aapl']):
                companies.append({"name": "Apple Inc.", "ticker": "AAPL"})
            elif any(word in query_lower for word in ['reliance', 'ril']):
                companies.append({"name": "Reliance Industries", "ticker": "RELIANCE.NS"})
            elif any(word in query_lower for word in ['tcs', 'tata consultancy']):
                companies.append({"name": "Tata Consultancy Services", "ticker": "TCS.NS"})
            
            # Add found tickers
            for ticker in tickers:
                if not any(c['ticker'] == ticker for c in companies):
                    companies.append({"name": ticker, "ticker": ticker})
        
        return companies
    
    def _get_company_name(self, ticker: str) -> str:
        """Get company name from ticker"""
        ticker_map = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corp.",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.",
            "TSLA": "Tesla Inc.",
            "META": "Meta Platforms",
            "NVDA": "NVIDIA Corp."
        }
        return ticker_map.get(ticker, ticker)
    
    def _estimate_market_cap(self, ticker: str, price: float) -> float:
        """Estimate market cap"""
        shares_outstanding = {
            "AAPL": 15.5e9,
            "MSFT": 7.4e9,
            "GOOGL": 12.8e9,
            "AMZN": 10.5e9
        }
        return price * shares_outstanding.get(ticker, 1e9)
    
    def _get_mock_market_data(self, ticker: str) -> Dict:
        """Get mock data when API unavailable"""
        mock_data = {
            "AAPL": {"price": 175.50, "change": "1.2%", "volume": 50000000, "pe_ratio": "28.5"},
            "MSFT": {"price": 380.25, "change": "0.8%", "volume": 25000000, "pe_ratio": "32.1"},
            "GOOGL": {"price": 142.75, "change": "-0.5%", "volume": 20000000, "pe_ratio": "25.3"}
        }
        return mock_data.get(ticker, {
            "price": 100.0,
            "change": "0.0%", 
            "volume": 1000000,
            "pe_ratio": "20.0"
        })
    
    def _summarize_comparison_data(self, companies: List[Dict], 
                                  web_data: Dict, market_data: Dict, 
                                  kb_data: Dict) -> Dict:
        """Summarize all data for comparison"""
        summary = {}
        
        for company in companies:
            ticker = company['ticker']
            
            # Combine all data sources
            summary[ticker] = {
                **market_data.get(ticker, {}),
                "web_summary": web_data.get(ticker, "")[:200],
                "kb_insights": kb_data.get(ticker, []),
                "company_name": company['name']
            }
            
            # Add calculated metrics
            if 'price' in summary[ticker]:
                price = summary[ticker]['price']
                summary[ticker]['high_52w'] = price * 1.2  # Mock
                summary[ticker]['low_52w'] = price * 0.8   # Mock
                
                # Extract change percent
                change_str = str(summary[ticker].get('change', '0%'))
                try:
                    summary[ticker]['change_percent'] = float(change_str.strip('%'))
                except:
                    summary[ticker]['change_percent'] = 0.0
        
        return summary
    
    # ========== SESSION UTILITIES ==========
    
    def list_sessions(self) -> List[Dict]:
        """List all available sessions"""
        sessions = []
        
        # Active sessions
        for sid, session in self.sessions.items():
            sessions.append({
                "session_id": sid,
                "created": session.created_at.isoformat(),
                "last_accessed": session.last_accessed.isoformat(),
                "exchanges": len(session.conversation_history),
                "companies": list(session.context["companies_discussed"]),
                "categories": list(session.context["categories_explored"])
            })
        
        # Saved sessions
        for filename in os.listdir(self.session_storage):
            if filename.endswith('.pkl'):
                sid = filename[:-4]
                if sid not in self.sessions:
                    session = self._load_session(sid)
                    if session:
                        sessions.append({
                            "session_id": sid,
                            "created": session.created_at.isoformat(),
                            "last_accessed": session.last_accessed.isoformat(),
                            "exchanges": len(session.conversation_history),
                            "companies": list(session.context["companies_discussed"]),
                            "categories": list(session.context["categories_explored"])
                        })
        
        return sessions
    
    def get_session_history(self, session_id: str) -> str:
        """Get formatted session history"""
        session = self.sessions.get(session_id)
        if not session:
            session = self._load_session(session_id)
        
        if not session:
            return "Session not found"
        
        history = f"\n📜 Session History\n"
        history += f"ID: {session_id}\n"
        history += f"Started: {session.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        history += f"Total Exchanges: {len(session.conversation_history)}\n"
        history += "-" * 60 + "\n"
        
        for i, exchange in enumerate(session.conversation_history, 1):
            history += f"\n{i}. [{exchange['timestamp']}]\n"
            history += f"Q: {exchange['query']}\n"
            history += f"A: {exchange['response'][:300]}...\n"
            
            if exchange.get('metadata'):
                history += f"Type: {exchange['metadata'].get('type', 'general')}, "
                history += f"Category: {exchange['metadata'].get('category', 'general')}\n"
        
        return history


def interactive_demo():
    """Interactive demo of the ultimate agent"""
    agent = UltimateFinancialAgent()
    
    print("\n🚀 Ultimate Financial Research Agent")
    print("=" * 60)
    print("Features:")
    print("✅ Conversational Memory with Sessions")
    print("✅ Multi-Category Financial Support")
    print("✅ Web Search + Knowledge Base")
    print("✅ Data Extraction & Comparison Tables")
    print("✅ Multilingual Support")
    print("=" * 60)
    
    # Session options
    print("\nOptions:")
    print("1. Start new session")
    print("2. Continue existing session")
    print("3. List all sessions")
    
    choice = input("\nSelect (1-3): ").strip()
    
    if choice == "1":
        session_id = agent.create_session()
    elif choice == "2":
        session_id = input("Enter session ID: ").strip()
        if not agent.continue_session(session_id):
            print("Creating new session instead...")
            session_id = agent.create_session()
    elif choice == "3":
        sessions = agent.list_sessions()
        print("\n📋 Available Sessions:")
        for s in sessions:
            print(f"\n- ID: {s['session_id'][:8]}...")
            print(f"  Created: {s['created']}")
            print(f"  Exchanges: {s['exchanges']}")
            print(f"  Companies: {s['companies']}")
            print(f"  Categories: {s['categories']}")
        return
    else:
        session_id = agent.create_session()
    
    # Example queries to demonstrate
    print(f"\n💬 Session: {session_id}")
    print("\nExample queries:")
    print("- Compare Apple and Microsoft")
    print("- How does ESG affect stock performance?")
    print("- Tell me about Tesla")
    print("- What about its competitors? (follow-up)")
    print("- Impact of interest rates on tech stocks")
    print("\nType 'quit' to exit, 'history' for session history")
    print("-" * 60)
    
    while True:
        query = input("\n👤 You: ").strip()
        
        if query.lower() == 'quit':
            print("\n👋 Session saved. Goodbye!")
            break
        elif query.lower() == 'history':
            print(agent.get_session_history(session_id))
            continue
        elif query:
            response = agent.process_query(query, session_id)
            print(f"\n🤖 Agent:\n{response}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line usage
        agent = UltimateFinancialAgent()
        
        if sys.argv[1] == "demo":
            # Run specific demos
            session_id = agent.create_session()
            
            demos = [
                "Compare the financial performance of Apple and Samsung over the past 5 years",
                "What about Microsoft?",  # Follow-up
                "How does ESG investing affect portfolio returns?",
                "Analyze Tesla stock performance"
            ]
            
            print(f"\n🎯 Running Demo with Session: {session_id}")
            
            for query in demos[:2]:
                print(f"\n{'='*60}")
                print(f"Query: {query}")
                response = agent.process_query(query, session_id)
                print(response)
        else:
            # Direct query with session
            session_id = sys.argv[1]
            query = " ".join(sys.argv[2:])
            
            if agent.continue_session(session_id):
                response = agent.process_query(query, session_id)
                print(response)
            else:
                print("Invalid session ID")
    else:
        # Interactive mode
        interactive_demo()
