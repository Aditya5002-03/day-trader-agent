import os
import time
import streamlit as st
import yfinance as yf
from google import genai
from google.genai import types
import skills_engine as skills

st.set_page_config(
    page_title="Universal NSE Day Trader Desk (All Shares)", 
    page_icon="📈", 
    layout="wide"
)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "account_equity" not in st.session_state:
    st.session_state.account_equity = 200000.0  # ₹2,00,000 baseline
if "active_plan" not in st.session_state:
    st.session_state.active_plan = None
if "risk_verdict" not in st.session_state:
    st.session_state.risk_verdict = None
if "paper_positions" not in st.session_state:
    st.session_state.paper_positions = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# Sidebar Controls & Live Portfolio Monitor
# ---------------------------------------------------------
with st.sidebar:
    st.title("NSE Desk Controls")
    api_key = st.text_input(
        "Gemini API Key", 
        type="password", 
        value=os.getenv("GEMINI_API_KEY", "")
    )
    
    st.markdown("---")
    st.subheader("Account Parameters (INR)")
    st.session_state.account_equity = st.number_input(
        "Portfolio Equity (₹)", 
        value=st.session_state.account_equity, 
        step=25000.0
    )
    max_risk_allowed = round(st.session_state.account_equity * 0.01, 2)
    st.caption(f"Risk Rule: Max 1% per trade (₹{max_risk_allowed})")
    
    st.markdown("---")
    st.subheader("Active Trade Plan")
    if st.session_state.active_plan:
        st.json(st.session_state.active_plan)
        st.write(f"**Risk Verdict:** `{st.session_state.risk_verdict}`")
    else:
        st.info("No active trade plan configured yet.")
        
    st.markdown("---")
    st.subheader("Executed Paper Orders")
    if st.session_state.paper_positions:
        st.dataframe(st.session_state.paper_positions, use_container_width=True)
    else:
        st.caption("No executed paper orders.")

# ---------------------------------------------------------
# Main UI Layout
# ---------------------------------------------------------
st.title("Universal NSE Day Trader Desk (India)")
st.caption("Scan entire market indices or input any NSE stock (e.g., ZOMATO, BEL, RELIANCE, SUZLON, TATASTEEL).")

# ---------------------------------------------------------
# Instrument Selection & Price Fetcher
# ---------------------------------------------------------
with st.container():
    st.markdown("### 🔍 Select or Type Any Share")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        ticker_input = st.text_input(
            "Enter Stock Symbol (NSE)", 
            value="TATASTEEL", 
            help="Type any valid symbol: RELIANCE, ZOMATO, BEL, HAL, HDFCBANK, INFY, etc."
        ).strip().upper()
        
    # Auto-fetch live market price to populate default entry/stop
    live_price = 100.0
    try:
        sym_check = skills.format_indian_ticker(ticker_input)
        live_price = float(yf.Ticker(sym_check).fast_info.last_price or 100.0)
    except Exception:
        pass

    with col2:
        custom_entry = st.number_input(
            "Target Entry (₹)", 
            value=round(live_price, 2), 
            step=0.5
        )
    with col3:
        # Default stop 1.5% below entry
        suggested_stop = round(custom_entry * 0.985, 2)
        custom_stop = st.number_input(
            "Stop Loss (₹)", 
            value=suggested_stop, 
            step=0.5
        )

    st.markdown("---")
    st.markdown("### ⚡ Clickable Pipeline")

    # Basket Scanner Selector
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("📊 Scan NIFTY 50", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": "Scan NIFTY 50 (Top 15 Liquid) for 15-minute Opening Range Breakouts."
            })
    with b2:
        if st.button("🏦 Scan NIFTY BANK", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": "Scan NIFTY BANK for 15-minute Opening Range Breakouts."
            })
    with b3:
        if st.button("💻 Scan NIFTY IT", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": "Scan NIFTY IT for 15-minute Opening Range Breakouts."
            })
    with b4:
        if st.button(f"🎯 Scan {ticker_input} Only", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": f"Scan {ticker_input} for 15-minute Opening Range Breakouts."
            })

    # Individual Stock Workflow
    st.write(f"**Actions for {ticker_input}:**")
    row1, row2, row3, row4 = st.columns(4)
    with row1:
        if st.button(f"📰 Check {ticker_input} News", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": f"Check recent news, corporate filings, and catalysts for {ticker_input}."
            })
    with row2:
        if st.button(f"📊 Check Fundamentals", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": f"Check operating margins, revenue growth, and SEBI promoter filings for {ticker_input}."
            })
    with row3:
        if st.button(f"📐 Setup 2:1 Exit Plan", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": f"Plan an exit for {ticker_input}: Entry at {custom_entry}, Stop-Loss at {custom_stop}."
            })
    with row4:
        if st.button(f"⏳ Monte Carlo Simulation", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": f"Run Monte Carlo time machine simulation on {ticker_input} using the active plan."
            })

    row5, row6, row7 = st.columns(3)
    with row5:
        if st.button(f"💰 Size 1% Risk Budget", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": f"Calculate the exact share count for {ticker_input} based on my 1% account risk limit in INR."
            })
    with row6:
        if st.button(f"🛡️ Audit Risk Gate", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": f"Audit the risk for {ticker_input} to determine PASS or BLOCK status."
            })
    with row7:
        if st.button(f"🚀 Paper Execute Trade", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": f"Execute paper trade for {ticker_input} matching my 1% budget sizing, confirmed=True."
            })

st.markdown("---")

# ---------------------------------------------------------
# Multi-Tool Agent Turn Execution
# ---------------------------------------------------------
def run_agent_turn(user_prompt: str, key: str):
    client = genai.Client(api_key=key)

    def tool_scanner(tickers: str = "NIFTY 50"):
        return skills.trader_scanner(tickers)

    def tool_news(ticker: str):
        return skills.trader_news(ticker)

    def tool_entry(ticker: str):
        return skills.trader_entry(ticker)

    def tool_exit(ticker: str, entry_price: float, stop_loss: float):
        return skills.trader_exit(ticker, entry_price, stop_loss, st.session_state)

    def tool_timemachine(ticker: str, simulations: int = 1000):
        return skills.trader_timemachine(ticker, st.session_state, simulations)

    def tool_budget(account_cash: float = None):
        cash = account_cash or st.session_state.account_equity
        return skills.trader_budget(st.session_state, cash)

    def tool_risk(ticker: str, shares: int):
        return skills.trader_risk(ticker, shares, st.session_state)

    def tool_broker(ticker: str, shares: int, confirmed: bool):
        return skills.trader_broker(ticker, shares, confirmed, st.session_state)

    def tool_alerts(ticker: str):
        return skills.trader_alerts(ticker, st.session_state)

    def tool_analyst(ticker: str):
        return skills.trader_analyst(ticker)

    def tool_pelosi(ticker: str):
        return skills.trader_pelosi(ticker)

    desk_tools = [
        tool_scanner, tool_news, tool_entry, tool_exit,
        tool_timemachine, tool_budget, tool_risk,
        tool_broker, tool_alerts, tool_analyst, tool_pelosi
    ]

    system_instruction = """
    You are an institutional intraday equity trading desk agent specialized for the Indian stock market (NSE/BSE).
    The 11 modular skills operate on any Indian stock ticker (e.g., RELIANCE.NS, TATASTEEL.NS, ZOMATO.NS, BEL.NS, HDFCBANK.NS):
    1. trader_scanner: Detect 15-minute Opening Range Breakouts across broad market indices or individual stocks.
    2. trader_news: Pull corporate filings and news.
    3. trader_entry: Require a verified 5-minute candle close confirmation.
    4. trader_exit: Set strict 2:1 targets and stops in INR (₹). Curfew is 15:15 IST (auto square-off).
    5. trader_timemachine: Monte Carlo simulations to assess statistical edge.
    6. trader_budget: Size positions using 1% max account risk in INR (₹).
    7. trader_risk: Enforce strict PASS or BLOCK gating.
    8. trader_broker: Paper execution (requires confirmed=True and PASS status).
    9. trader_alerts: Monitor active levels and the 15:15 IST square-off time.
    10. trader_analyst: Check margins and quarterly results.
    11. trader_pelosi: Track SEBI insider filings and block deals.

    Always run tools to compute figures. Format all monetary values with ₹ (INR).
    Keep responses concise, disciplined, and structured.
    """

    max_retries = 3
    base_delay = 2.0
    candidate_models = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]

    for model_name in candidate_models:
        for attempt in range(max_retries):
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        tools=desk_tools,
                        temperature=0.2
                    )
                )
                return res.text
            except Exception as e:
                err_msg = str(e)
                if ("429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg) and attempt < max_retries - 1:
                    time.sleep(base_delay * (attempt + 1))
                    continue
                if "404" in err_msg or "NOT_FOUND" in err_msg:
                    break
                if attempt == max_retries - 1 and model_name == candidate_models[-1]:
                    raise e

# ---------------------------------------------------------
# Chat Stream & Conversation Processing
# ---------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Or type any query (e.g., 'Scan ZOMATO and plan an entry')...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_user_message = st.session_state.messages[-1]["content"]
    
    if not api_key:
        with st.chat_message("assistant"):
            st.error("Please supply a valid GEMINI_API_KEY in the sidebar to run the desk.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Processing selected step across trading skills..."):
                try:
                    reply = run_agent_turn(last_user_message, api_key)
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error executing agent workflow: {str(e)}")
        st.rerun()