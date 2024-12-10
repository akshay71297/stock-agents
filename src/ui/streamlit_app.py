# src/ui/streamlit_app.py
import streamlit as st
import asyncio
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
from typing import List, Optional, Callable, Any, Dict

# Configure page
st.set_page_config(
    page_title="Stock Analysis Hub",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

class StockPriceTracker:
    @staticmethod
    def get_live_price(symbol: str) -> Dict[str, Any]:
        """Get live stock price data"""
        stock = yf.Ticker(symbol)
        try:
            today_data = stock.history(period='1d', interval='1m')
            if not today_data.empty:
                current_price = today_data['Close'].iloc[-1]
                open_price = today_data['Open'].iloc[0]
                price_change = current_price - open_price
                price_change_pct = (price_change / open_price) * 100
                
                return {
                    'current_price': current_price,
                    'price_change': price_change,
                    'price_change_pct': price_change_pct,
                    'volume': today_data['Volume'].sum(),
                    'high': today_data['High'].max(),
                    'low': today_data['Low'].min(),
                }
        except Exception as e:
            st.error(f"Error fetching live price: {str(e)}")
        return None

class StockChartMaker:
    @staticmethod
    def create_price_chart(symbol: str, period: str = "1y") -> go.Figure:
        """Create an interactive price chart"""
        try:
            # Define appropriate intervals for different periods
            intervals = {
                "1d": "1m",
                "5d": "5m",
                "1mo": "1h",
                "3mo": "1d",
                "6mo": "1d",
                "1y": "1d",
                "2y": "1d",
                "5y": "1wk",
                "max": "1mo"
            }
            
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period, interval=intervals.get(period, "1d"))
            
            if hist.empty:
                st.warning(f"No data available for {symbol} in selected period")
                return None
            
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=('Price', 'Volume')
            )

            # Add candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name='OHLC'
                ),
                row=1, col=1
            )

            # Add moving averages for periods longer than 1 day
            if period not in ["1d", "5d"]:
                ma20 = hist['Close'].rolling(window=20).mean()
                ma50 = hist['Close'].rolling(window=50).mean()
                
                fig.add_trace(
                    go.Scatter(
                        x=hist.index,
                        y=ma20,
                        opacity=0.7,
                        line=dict(color='blue', width=2),
                        name='MA 20'
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=hist.index,
                        y=ma50,
                        opacity=0.7,
                        line=dict(color='orange', width=2),
                        name='MA 50'
                    ),
                    row=1, col=1
                )

            # Add volume bars
            colors = ['red' if row['Open'] > row['Close'] else 'green' 
                     for idx, row in hist.iterrows()]
            fig.add_trace(
                go.Bar(
                    x=hist.index,
                    y=hist['Volume'],
                    marker_color=colors,
                    name='Volume'
                ),
                row=2, col=1
            )

            # Update layout
            fig.update_layout(
                height=600,
                title=f"{symbol} Stock Price ({period})",
                yaxis_title="Price ($)",
                yaxis2_title="Volume",
                template="plotly_dark",
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                margin=dict(l=50, r=50, t=50, b=50)
            )

            fig.update_xaxes(rangeslider_visible=False)
            return fig
            
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")
            return None

class EnhancedUI:
    def __init__(self):
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'last_symbol' not in st.session_state:
            st.session_state.last_symbol = None
        if 'chart_periods' not in st.session_state:
            st.session_state.chart_periods = {}

    def _display_metrics_table(self, metrics: Dict[str, Any], title: str):
        """Display metrics in a formatted table"""
        st.subheader(title)
        
        # Process and format the metrics
        formatted_metrics = {}
        for k, v in metrics.items():
            # Format the key for display
            display_key = k.replace('_', ' ').title()
            
            # Format the value based on type
            if isinstance(v, float):
                if 'ratio' in k.lower() or 'margin' in k.lower():
                    formatted_metrics[display_key] = f"{v:.2f}"
                elif 'growth' in k.lower() or 'return' in k.lower():
                    formatted_metrics[display_key] = f"{v*100:.2f}%"
                else:
                    formatted_metrics[display_key] = f"{v:,.2f}"
            else:
                formatted_metrics[display_key] = str(v)
        
        # Convert to DataFrame for display
        df = pd.DataFrame([
            {'Metric': k, 'Value': v} 
            for k, v in formatted_metrics.items()
        ])
        
        # Display the table
        st.dataframe(
            df.set_index('Metric'),
            use_container_width=True
        )

    def _display_financial_analysis(self, analysis_data: Dict[str, Any], company_info: Optional[Dict[str, Any]]):
        """Display financial analysis in a structured format"""
        try:
            # Check if we have valid data
            if not company_info or not analysis_data:
                st.error("No company information available")
                return

            # Get symbol with proper error handling
            symbol = company_info.get('ticker', '') or company_info.get('symbol', '')
            if symbol:
                st.session_state.last_symbol = symbol
                
                # Create a container for live price and chart
                price_container = st.container()
                self._display_live_price(symbol, price_container)
            
            # Company Header with error handling
            company_name = company_info.get('name', 'Unknown Company')
            industry = company_info.get('industry', 'N/A')
            st.header(f"{company_name} ({industry})")
            st.caption(f"Sector: {company_info.get('sector', 'N/A')}")

            # Create columns for key metrics
            if 'profitability' in analysis_data:
                metrics_container = st.container()
                cols = metrics_container.columns(4)
                
                with cols[0]:
                    operating_margin = analysis_data['profitability'].get('operating_margin', 0)
                    if isinstance(operating_margin, (int, float)):
                        st.metric(
                            "Operating Margin",
                            f"{operating_margin*100:.2f}%"
                        )

                with cols[1]:
                    roe = analysis_data['profitability'].get('roe', 0)
                    if isinstance(roe, (int, float)):
                        st.metric(
                            "ROE",
                            f"{roe*100:.2f}%"
                        )

                with cols[2]:
                    rev_growth = analysis_data['growth'].get('revenue_growth', 0)
                    if isinstance(rev_growth, (int, float)):
                        st.metric(
                            "Revenue Growth",
                            f"{rev_growth*100:.2f}%"
                        )

                with cols[3]:
                    pe_ratio = analysis_data['valuation'].get('pe_ratio', 0)
                    if isinstance(pe_ratio, (int, float)):
                        st.metric(
                            "P/E Ratio",
                            f"{pe_ratio:.2f}"
                        )

                # Create expandable sections for detailed metrics
                with st.expander("📊 Detailed Metrics", expanded=True):
                    tabs = st.tabs(["Valuation", "Profitability", "Growth", "Financial Health"])
                    
                    with tabs[0]:
                        if 'valuation' in analysis_data:
                            self._display_metrics_table(analysis_data['valuation'], "Valuation Metrics")
                    
                    with tabs[1]:
                        if 'profitability' in analysis_data:
                            self._display_metrics_table(analysis_data['profitability'], "Profitability Metrics")
                    
                    with tabs[2]:
                        if 'growth' in analysis_data:
                            self._display_metrics_table(analysis_data['growth'], "Growth Metrics")
                    
                    with tabs[3]:
                        if 'financial_health' in analysis_data:
                            self._display_metrics_table(analysis_data['financial_health'], "Financial Health")
            else:
                st.warning("No financial metrics available")
        
        except Exception as e:
            st.error(f"Error displaying financial analysis: {str(e)}")
            st.write("Analysis Data:", analysis_data)
            st.write("Company Info:", company_info)

    def _display_live_price(self, symbol: str, display_container=None):
        """Display live price information"""
        container = display_container if display_container is not None else st
        
        price_data = StockPriceTracker.get_live_price(symbol)
        if price_data:
            # Create main columns: metrics and period selector
            metric_cols = container.columns([5, 1])
            
            with metric_cols[0]:
                cols = st.columns(5)
                with cols[0]:
                    st.metric(
                        "Current Price",
                        f"${price_data['current_price']:.2f}",
                        f"{price_data['price_change_pct']:.2f}%",
                        delta_color="normal"
                    )
                with cols[1]:
                    st.metric("Daily High", f"${price_data['high']:.2f}")
                with cols[2]:
                    st.metric("Daily Low", f"${price_data['low']:.2f}")
                with cols[3]:
                    st.metric(
                        "Volume",
                        f"{price_data['volume']:,.0f}"
                    )
                with cols[4]:
                    stock = yf.Ticker(symbol)
                    if 'marketCap' in stock.info:
                        market_cap = stock.info['marketCap']
                        market_cap_str = (
                            f"${market_cap/1e12:.2f}T" if market_cap >= 1e12 else
                            f"${market_cap/1e9:.2f}B" if market_cap >= 1e9 else
                            f"${market_cap/1e6:.2f}M"
                        )
                        st.metric("Market Cap", market_cap_str)
            
            with metric_cols[1]:
                if f'period_{symbol}' not in st.session_state:
                    st.session_state[f'period_{symbol}'] = "1y"
                
                period = st.selectbox(
                    "Period",
                    ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
                    index=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"].index(
                        st.session_state[f'period_{symbol}']
                    ),
                    key=f"period_selector_{symbol}"
                )
                
                st.session_state[f'period_{symbol}'] = period

            # Create and display chart
            if period:
                chart = StockChartMaker.create_price_chart(symbol, period)
                if chart:
                    container.plotly_chart(chart, use_container_width=True)

    def render(self, agent: Any, process_message: Callable, model_name: str):
        """Render the chat interface"""
        # Add custom CSS
        st.markdown("""
            <style>
            /* Main container */
            .main {
                width: 100% !important;
                max-width: none !important;
                padding: 0 !important;
            }
            
            /* Chat container */
            [data-testid="stVerticalBlock"] {
                width: 100% !important;
                max-width: none !important;
            }
            
            /* Chat messages */
            .stChatMessage {
                width: 100% !important;
                max-width: none !important;
            }
            
            /* Charts and data displays */
            .element-container, .stDataFrame {
                width: 100% !important;
                max-width: none !important;
            }
            
            /* Plotly charts */
            .js-plotly-plot, .plot-container {
                width: 100% !important;
            }
            
            /* Metrics */
            [data-testid="stMetricValue"] {
                font-size: 1.8rem !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    if isinstance(msg["content"], dict) and "analysis_data" in msg["content"]:
                        self._display_financial_analysis(
                            msg["content"]["analysis_data"],
                            msg["content"]["company_info"]
                        )
                        st.markdown(msg["content"]["response"])
                    else:
                        st.markdown(msg["content"])
                else:
                    st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input("What would you like to know?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                status_container = st.empty()
                
                status_container.status(
                    f"Processing with {model_name}",
                    state="running",
                    expanded=False
                )
                
                try:
                    response = asyncio.run(process_message(agent, prompt))
                    status_container.status("Done!", state="complete", expanded=False)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                    status_container.empty()
                    
                    if isinstance(response, dict) and "analysis_data" in response:
                        self._display_financial_analysis(
                            response["analysis_data"],
                            response["company_info"]
                        )
                        message_placeholder.markdown(response["response"])
                    else:
                        message_placeholder.markdown(response)
                
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    status_container.status("Error occurred", state="error")
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })