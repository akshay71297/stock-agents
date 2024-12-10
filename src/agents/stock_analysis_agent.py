# src/agents/stock_analysis_agent.py
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional

from httpx import AsyncClient
import logfire
from pydantic_ai.models.openai import OpenAIModel

from src.agents.base_agent import BaseAgent
from src.tools.stock_analyzer_tool import FinancialDataFetcher, FinancialAnalyzer, CompetitiveAnalysis

class StockAnalysisAgent(BaseAgent):
    def __init__(self, model: OpenAIModel):
        super().__init__(model)
        
        @self.agent.tool
        async def analyze_stock(
            ctx, 
            symbol: str,
            analysis_type: str = "full"  # full, fundamental, competitive, technical
        ) -> str:
            """Perform comprehensive stock analysis"""
            try:
                import yfinance as yf
                
                # Fetch data
                stock = yf.Ticker(symbol)
                info = stock.info
                
                # Basic validation
                if not info:
                    return f"Could not fetch data for symbol {symbol}"
                
                analysis = {
                    'valuation': {
                        'pe_ratio': info.get('trailingPE', 'N/A'),
                        'forward_pe': info.get('forwardPE', 'N/A'),
                        'peg_ratio': info.get('pegRatio', 'N/A'),
                        'price_to_book': info.get('priceToBook', 'N/A'),
                    },
                    'profitability': {
                        'operating_margin': info.get('operatingMargins', 'N/A'),
                        'profit_margin': info.get('profitMargins', 'N/A'),
                        'roe': info.get('returnOnEquity', 'N/A'),
                        'roa': info.get('returnOnAssets', 'N/A'),
                    },
                    'growth': {
                        'revenue_growth': info.get('revenueGrowth', 'N/A'),
                        'earnings_growth': info.get('earningsGrowth', 'N/A'),
                    },
                    'financial_health': {
                        'current_ratio': info.get('currentRatio', 'N/A'),
                        'debt_to_equity': info.get('debtToEquity', 'N/A'),
                        'free_cash_flow': info.get('freeCashflow', 'N/A'),
                    }
                }
                
                # Store analysis in context for visualization
                if ctx.deps.context is not None:
                    ctx.deps.context['analysis'] = analysis
                    ctx.deps.context['company_info'] = {
                        'name': info.get('longName', symbol),
                        'industry': info.get('industry', 'N/A'),
                        'sector': info.get('sector', 'N/A'),
                        'ticker': symbol,
                        'symbol': symbol
                    }
                
                return self._format_analysis_response(symbol, analysis)
                
            except Exception as e:
                return f"Error analyzing stock: {str(e)}"
    
    def get_system_prompt(self) -> str:
        return (
            f"You are an expert financial analyst specializing in comprehensive stock analysis. "
            f"You help users understand companies through fundamental analysis, competitive positioning, "
            f"and market dynamics. You provide detailed insights while making complex financial "
            f"concepts accessible. The current date is: {datetime.now().strftime('%Y-%m-%d')}"
        )
    
    @dataclass
    class Deps:
        context: Dict[str, Any] | None = None
    
    async def process_query(self, query: str, context: Dict[str, Any] = None):
        """Process a stock analysis query"""
        deps = self.Deps(context=context or {})
        
        with logfire.span('Stock Analysis Agent', query=query):
            result = await self.agent.run(query, deps=deps)
            
            return {
                'response': result.data,
                'analysis_data': deps.context.get('analysis'),
                'company_info': deps.context.get('company_info')
            }

    def _format_analysis_response(self, symbol: str, analysis: Dict[str, Any]) -> str:
        """Format analysis results into a well-structured markdown response"""
        markdown = [f"# Financial Analysis Report: {symbol}\n"]
        
        # Valuation Section
        markdown.extend([
            "## Valuation Metrics\n",
            "| Metric | Value |",
            "|--------|--------|",
            f"| P/E Ratio | {self._format_number(analysis['valuation'].get('pe_ratio'))} |",
            f"| Forward P/E | {self._format_number(analysis['valuation'].get('forward_pe'))} |",
            f"| PEG Ratio | {self._format_number(analysis['valuation'].get('peg_ratio'))} |",
            f"| Price to Book | {self._format_number(analysis['valuation'].get('price_to_book'))} |",
            "\n"
        ])
        
        # Profitability Section
        markdown.extend([
            "## Profitability Metrics\n",
            "| Metric | Value |",
            "|--------|--------|",
            f"| Operating Margin | {self._format_percentage(analysis['profitability'].get('operating_margin'))} |",
            f"| Profit Margin | {self._format_percentage(analysis['profitability'].get('profit_margin'))} |",
            f"| ROE | {self._format_percentage(analysis['profitability'].get('roe'))} |",
            f"| ROA | {self._format_percentage(analysis['profitability'].get('roa'))} |",
            "\n"
        ])
        
        # Growth Section
        markdown.extend([
            "## Growth Metrics\n",
            "| Metric | Value |",
            "|--------|--------|",
            f"| Revenue Growth | {self._format_percentage(analysis['growth'].get('revenue_growth'))} |",
            f"| Earnings Growth | {self._format_percentage(analysis['growth'].get('earnings_growth'))} |",
            "\n"
        ])
        
        # Financial Health Section
        markdown.extend([
            "## Financial Health\n",
            "| Metric | Value |",
            "|--------|--------|",
            f"| Current Ratio | {self._format_number(analysis['financial_health'].get('current_ratio'))} |",
            f"| Debt to Equity | {self._format_number(analysis['financial_health'].get('debt_to_equity'))} |",
            f"| Free Cash Flow | {self._format_currency(analysis['financial_health'].get('free_cash_flow'))} |",
            "\n"
        ])

        # Add disclaimer
        markdown.extend([
            "---",
            "*Disclaimer: This analysis is based on currently available data and should not be considered as financial advice. "
            "Always conduct your own research and consult with financial professionals before making investment decisions.*"
        ])

        return "\n".join(markdown)

    def _format_percentage(self, value: Optional[float]) -> str:
        """Format number as percentage"""
        if value is None or value == 'N/A':
            return "N/A"
        return f"{value*100:.2f}%" if isinstance(value, (int, float)) else "N/A"

    def _format_number(self, value: Optional[float]) -> str:
        """Format number with 2 decimal places"""
        if value is None or value == 'N/A':
            return "N/A"
        return f"{value:.2f}" if isinstance(value, (int, float)) else "N/A"

    def _format_currency(self, value: Optional[float]) -> str:
        """Format number as currency in millions/billions"""
        if value is None or value == 'N/A':
            return "N/A"
        if not isinstance(value, (int, float)):
            return "N/A"
        
        if abs(value) >= 1e9:
            return f"${value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.2f}M"
        else:
            return f"${value:.2f}"