# 📐 Financial Research Agent - Architecture Diagrams

## System Components Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                              │
│                         (Streamlit)                               │
└─────────────────────────────┬─────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                              │
│                  ultimate_financial_agent.py                     │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Session   │  │   Query     │  │  Response  │             │
│  │  Manager   │  │   Router    │  │  Generator │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────┬─────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │    Groq     │  │    Alpha    │  │  Pinecone   │
    │    LLM      │  │  Vantage    │  │  Vector DB  │
    │             │  │     API     │  │             │
    └─────────────┘  └─────────────┘  └─────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  DuckDuckGo      │
                    │  Web Search     │
                    └──────────────────┘
```

## Query Processing Flow

```
START
  │
  ├─ User Input → "Compare Apple and Reliance price"
  │
  ▼
┌──────────────────────────────────────────────────┐
│ STEP 1: Query Reception & Session Loading       │
│  • Receive query                                 │
│  • Load session context                          │
│  • Get conversation history                      │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│ STEP 2: AI-Powered Query Classification           │
│                                                    │
│  Using Groq LLM:                                   │
│  ├─ Extract intent: "COMPARISON + PRICE"         │
│  ├─ Extract entities: [AAPL, RELIANCE.NS]         │
│  └─ Determine query_type: "price_query"          │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│ STEP 3: Dynamic Company Extraction               │
│                                                    │
│  LLM-based extraction:                            │
│  [                                                 │
│    {"name": "Apple Inc.", "ticker": "AAPL"},      │
│    {"name": "Reliance Industries",                │
│     "ticker": "RELIANCE.NS"}                       │
│  ]                                                 │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│ STEP 4: Parallel Data Fetching                    │
│                                                    │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐ │
│  │Stock API│      │ Web     │      │KB Search│ │
│  │         │      │ Search  │      │         │ │
│  └────┬────┘      └────┬────┘      └────┬────┘ │
│       │                │                  │      │
│       ▼                ▼                  ▼      │
│  Get price:     Get news:        Get context:   │
│  $175.50        2024 financial    Historical    │
│                  performance      insights       │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│ STEP 5: Data Synthesis                            │
│                                                    │
│  Combine:                                         │
│  ├─ Real prices ($175.50, ₹2,950.50)             │
│  ├─ News context                                   │
│  └─ Historical data                                │
│                                                    │
│  → Pass to LLM for analysis                        │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│ STEP 6: Response Generation                       │
│                                                    │
│  Format:                                           │
│  ## 📈 Stock Prices                                │
│                                                     │
│  ### Apple Inc. (AAPL)                            │
│  💰 Price: $175.50                                │
│  📊 Change: +1.2%                                 │
│  📈 Volume: 38M                                    │
│                                                     │
│  ### Reliance Industries (RELIANCE.NS)           │
│  💰 Price: ₹2,950.50                              │
│  📊 Change: +0.8%                                  │
│  📈 Volume: 25M                                    │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│ STEP 7: Memory Update                             │
│                                                    │
│  Store in SessionMemory:                          │
│  ├─ Query: "Compare Apple and Reliance"           │
│  ├─ Response: Formatted prices                    │
│  ├─ Context: {AAPL, RELIANCE.NS}                 │
│  └─ Topics: {price, comparison}                    │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
                  END
```

## Memory Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 SessionStorage (Disk)                    │
│                                                          │
│  sessions/                                              │
│  ├─ session_abc123.pkl (User 1)                        │
│  ├─ session_def456.pkl (User 2)                        │
│  └─ session_ghi789.pkl (User 3)                         │
└─────────────────────────────────────────────────────────┘
                             ▲
                             │ load/save
                             │
┌─────────────────────────────────────────────────────────┐
│              SessionMemory (In-Memory)                   │
│                                                          │
│  session_id: "abc123"                                   │
│  created_at: 2025-10-27T22:00:00                       │
│  conversation_history:                                  │
│  ├─ Q1: "Tell me about Apple"                          │
│  │   A1: "...Apple info..."                           │
│  │   metadata: {companies: [AAPL]}                      │
│  │                                                     │
│  ├─ Q2: "Compare with Microsoft"                       │
│  │   A2: "...comparison..."                            │
│  │   metadata: {companies: [AAPL, MSFT]}               │
│  │                                                     │
│  └─ Q3: "Which is better?"                             │
│      A3: "...analysis..."                              │
│      metadata: {followup: true}                        │
│                                                          │
│  context:                                               │
│  ├─ companies_discussed: {AAPL, MSFT, TSLA}           │
│  ├─ topics_covered: {comparison, price, analysis}     │
│  └─ categories_explored: {markets, tech}              │
└─────────────────────────────────────────────────────────┘
```

## Tool Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│              UltimateFinancialAgent                       │
│                                                           │
│  def process_query(query, session_id):                   │
│      # 1. Get context                                    │
│      session = self.sessions[session_id]                 │
│      context = session.get_context_summary()             │
│                                                           │
│      # 2. AI Classification                              │
│      query_type = self._identify_query_type(query)      │
│                                                           │
│      # 3. Route to Handler                               │
│      if query_type == "price_query":                     │
│          response = self._handle_price_query(...)        │
│      elif query_type == "comparison":                     │
│          response = self._handle_comparison(...)         │
│      ...                                                  │
│                                                           │
│      # 4. Update Memory                                  │
│      session.add_exchange(query, response)               │
│                                                           │
│      return response                                      │
└──────────────────────────┬───────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────┐
│ Price Handler │  │Comparison    │  │Research      │
│               │  │Handler       │  │Handler      │
│               │  │              │  │             │
│ Uses:         │  │ Uses:        │  │ Uses:       │
│ • Alpha       │  │ • Web Search │  │ • LLM       │
│   Vantage     │  │ • Data API   │  │ • KB Search │
│ • LLM         │  │ • LLM        │  │ • Web       │
└───────────────┘  └──────────────┘  └──────────────┘
```

## Safety Mechanisms

```
┌─────────────────────────────────────────────────────────┐
│                     Input Layer                           │
│                    (Safety Check)                         │
│                                                           │
│  ✓ Validate query length                                 │
│  ✓ Check for malicious patterns                         │
│  ✓ Sanitize input                                        │
└───────────┬───────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│                  Processing Layer                         │
│                                                           │
│  ┌─────────────────────────────────────┐                │
│  │       Retry Mechanism              │                │
│  │                                     │                │
│  │  MAX_ATTEMPTS = 3                  │                │
│  │  attempt = 0                        │                │
│  │                                     │                │
│  │  while attempt < MAX_ATTEMPTS:      │                │
│  │      try:                           │                │
│  │          result = process()         │                │
│  │          break                      │                │
│  │      except:                        │                │
│  │          attempt += 1              │                │
│  │          wait()                     │                │
│  └─────────────────────────────────────┘                │
└───────────┬───────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│                  Output Layer                              │
│                 (Validation)                               │
│                                                           │
│  ✓ Check response completeness                           │
│  ✓ Verify against data sources                           │
│  ✓ Flag hallucinations                                   │
│  ✓ Add source citations                                  │
└───────────────────────────────────────────────────────────┘
```

## Multi-Step Operation Flow

```
┌─────────────────────────────────────────────────────────┐
│              User: "Compare Apple and Tesla"             │
└────────────────────────────┬────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌──────────────────┐   ┌──────────────────┐
        │  STEP 1:        │   │  STEP 2:         │
        │  Get Apple      │   │  Get Tesla       │
        │  Stock Data     │   │  Stock Data      │
        └─────────┬───────┘   └──────────┬──────┘
                  │                      │
                  ▼                      ▼
        ┌──────────────────┐   ┌──────────────────┐
        │  Price: $175.50 │   │  Price: $250.75 │
        │  Change: +1.2%  │   │  Change: +2.5%  │
        └─────────┬───────┘   └──────────┬──────┘
                  │                      │
                  └─────────┬────────────┘
                            │
                            ▼
                ┌──────────────────┐
                │  STEP 3:         │
                │  Combine Data    │
                │  + Analysis      │
                └──────────┬───────┘
                           │
                           ▼
                ┌──────────────────┐
                │  STEP 4:         │
                │  Generate        │
                │  Comparison      │
                │  Table           │
                └──────────┬───────┘
                           │
                           ▼
                ┌──────────────────┐
                │  STEP 5:         │
                │  Return          │
                │  Formatted       │
                │  Response       │
                └──────────────────┘
```

## Data Flow Diagram

```
┌──────────┐
│   User   │
└────┬─────┘
     │ "Compare Apple and Reliance"
     ▼
┌────────────────┐
│   Streamlit    │
│    Frontend    │
└────┬───────────┘
     │ POST query
     ▼
┌────────────────┐
│  Agent Router  │
└────┬───────────┘
     │
     ├─ Check Session
     ├─ Get Context
     ├─ Classify Query
     └─ Route Handler
     │
     ▼
┌────────────────┐
│ Price Handler  │
└────┬───────────┘
     │
     ├─ Extract: AAPL, RELIANCE.NS
     ├─ Call Alpha Vantage
     ├─ Fetch Web Data
     └─ Get KB Context
     │
     ▼
┌────────────────┐
│   Synthesize   │
│   Using LLM    │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│   Format &     │
│   Return       │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│   Update       │
│   Memory       │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│ Display to     │
│   User         │
└────────────────┘
```

## Key Features Diagram

```
┌────────────────────────────────────────────────────────┐
│                  AGENTIC FEATURES                       │
├────────────────────────────────────────────────────────┤
│                                                         │
│  🧠 INTELLIGENT                                        │
│     ├─ LLM-based query understanding                   │
│     ├─ Dynamic entity extraction                        │
│     └─ Context-aware routing                           │
│                                                         │
│  💾 MEMORY                                              │
│     ├─ Session-based storage                           │
│     ├─ Conversation history                            │
│     └─ Context accumulation                            │
│                                                         │
│  🔧 TOOL-ENABLED                                       │
│     ├─ Web search (DuckDuckGo)                         │
│     ├─ Stock API (Alpha Vantage)                       │
│     ├─ Vector DB (Pinecone)                            │
│     └─ AI analysis (Groq LLM)                          │
│                                                         │
│  🛡️ SAFE                                               │
│     ├─ Input validation                                │
│     ├─ Retry limits                                    │
│     ├─ Error handling                                  │
│     └─ Graceful fallbacks                               │
│                                                         │
│  📊 TRACEABLE                                          │
│     ├─ Operation logging                              │
│     ├─ Metadata tracking                              │
│     └─ Source citations                                │
│                                                         │
└────────────────────────────────────────────────────────┘
```

## Summary

This document provides comprehensive flow diagrams showing how the Financial Research Agent:
1. Processes queries autonomously
2. Manages memory across sessions
3. Integrates multiple tools
4. Prevents common issues
5. Provides full traceability

All diagrams are **implementation-ready** and match the actual code in `ultimate_financial_agent.py`! 🚀
