#!/usr/bin/env python3
"""
Streamlit UI for Financial Research Agent
Deploy on: https://share.streamlit.io
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Financial Research Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .example-button {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize agent
@st.cache_resource
def init_agent():
    try:
        from ultimate_financial_agent import UltimateFinancialAgent
        return UltimateFinancialAgent()
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        return None

# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.title("🤖 AI Financial Research Agent")
    st.markdown("*Compare stocks • Analyze markets • Get insights • Multi-language support*")

# Initialize
agent = init_agent()

if agent:
    # Sidebar
    with st.sidebar:
        st.header("🔧 Controls")
        
        # Session management
        st.subheader("📋 Session")
        if 'session_id' not in st.session_state:
            if st.button("🆕 Start New Session", type="primary"):
                st.session_state.session_id = agent.create_session()
                st.session_state.messages = []
                st.success("Session started!")
                st.rerun()
        else:
            st.info(f"Session: `{st.session_state.session_id[:8]}...`")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 New Session"):
                    st.session_state.session_id = agent.create_session()
                    st.session_state.messages = []
                    st.rerun()
            with col2:
                if st.button("📜 History"):
                    st.session_state.show_history = True
        
        # Features
        st.markdown("---")
        st.subheader("✨ Features")
        st.markdown("""
        - ✅ Real-time stock data
        - ✅ Company comparisons
        - ✅ Financial research
        - ✅ Multi-category support
        - ✅ Conversational memory
        - ✅ Hindi/English
        """)
        
        # API Status
        st.markdown("---")
        st.subheader("🔌 API Status")
        
        # Check services
        services = {
            "Groq AI": bool(os.getenv("GROQ_API_KEY")),
            "Alpha Vantage": bool(os.getenv("ALPHA_VANTAGE_API_KEY")),
            "Pinecone": bool(os.getenv("PINECONE_API_KEY"))
        }
        
        for service, status in services.items():
            if status:
                st.success(f"✅ {service}")
            else:
                st.warning(f"⚠️ {service} - Add key in settings")
    
    # Main area
    if 'session_id' in st.session_state:
        # Initialize chat history
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        # Show history modal
        if hasattr(st.session_state, 'show_history') and st.session_state.show_history:
            with st.expander("📜 Session History", expanded=True):
                history = agent.get_session_history(st.session_state.session_id)
                st.text(history)
            st.session_state.show_history = False
        
        # Example queries
        st.markdown("### 💡 Quick Examples")
        col1, col2, col3 = st.columns(3)
        
        examples = {
            "📊 Compare": "Compare Apple and Microsoft financial performance",
            "📈 Analyze": "Analyze Tesla stock performance and future outlook",
            "🔬 Research": "How does ESG investing affect portfolio returns?",
            "💹 Market": "What's driving cryptocurrency volatility?",
            "🏦 Banking": "Impact of fintech on traditional banking",
            "🌏 Hindi": "Apple aur Samsung ka comparison karo"
        }
        
        example_clicked = None
        for i, (label, query) in enumerate(examples.items()):
            col = [col1, col2, col3][i % 3]
            with col:
                if st.button(label, key=f"ex_{i}", help=query):
                    example_clicked = query
        
        # Chat interface
        st.markdown("---")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input
        if prompt := st.chat_input("Ask anything about finance...") or example_clicked:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    try:
                        response = agent.process_query(prompt, st.session_state.session_id)
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                        # Show context
                        session = agent.sessions[st.session_state.session_id]
                        if session.context['companies_discussed'] or session.context['categories_explored']:
                            with st.expander("📊 Context"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    if session.context['companies_discussed']:
                                        st.markdown("**Companies:**")
                                        for company in session.context['companies_discussed']:
                                            st.markdown(f"- {company}")
                                with col2:
                                    if session.context['categories_explored']:
                                        st.markdown("**Topics:**")
                                        for cat in session.context['categories_explored']:
                                            st.markdown(f"- {cat}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    else:
        # Welcome screen
        st.markdown("## 👋 Welcome!")
        st.info("Click **'Start New Session'** in the sidebar to begin")
        
        # Feature cards
        st.markdown("### What I can do:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### 📊 Stock Comparison
            - Compare multiple companies
            - Real-time market data
            - Historical performance
            - Structured tables
            """)
        
        with col2:
            st.markdown("""
            #### 🔬 Financial Research
            - Market analysis
            - ESG insights
            - Banking trends
            - Academic queries
            """)
        
        with col3:
            st.markdown("""
            #### 🧠 Smart Features
            - Conversational memory
            - Follow-up questions
            - Multi-language (Hindi/English)
            - Context awareness
            """)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.caption("Powered by Groq AI • Alpha Vantage • DuckDuckGo • Pinecone")
        st.caption("Made with ❤️ using Streamlit")

else:
    st.error("Failed to initialize agent. Please check your configuration.")
    
    # Show setup instructions
    with st.expander("🔧 Setup Instructions"):
        st.markdown("""
        ### Required API Keys:
        
        1. **Groq API Key**: [Get it here](https://console.groq.com)
        2. **Alpha Vantage Key**: [Get it here](https://www.alphavantage.co/support/#api-key)
        3. **Pinecone Key**: [Get it here](https://www.pinecone.io)
        
        ### Add to Streamlit Secrets:
        ```toml
        GROQ_API_KEY = "your-groq-key"
        ALPHA_VANTAGE_API_KEY = "your-av-key"
        PINECONE_API_KEY = "your-pinecone-key"
        ```
        """)

# Debug mode (only in development)
if os.getenv("DEBUG"):
    with st.expander("🐛 Debug Info"):
        st.write("Session State:", st.session_state)
        if 'session_id' in st.session_state and agent:
            st.write("Active Sessions:", list(agent.sessions.keys()))
