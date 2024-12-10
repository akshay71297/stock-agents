from typing import Optional, Dict, Any, List
from httpx import AsyncClient
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import pandas_ta as ta
from bs4 import BeautifulSoup
import json

class FinancialDataFetcher:
    """Fetches financial data from multiple sources"""
    
    @staticmethod
    async def get_yahoo_data(symbol: str) -> Dict[str, Any]:
        """Fetch comprehensive data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            
            # Get all available data
            info = stock.info
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            earnings = stock.earnings
            institutional_holders = stock.institutional_holders
            recommendations = stock.recommendations
            
            return {
                'info': info,
                'financials': financials.to_dict() if not financials.empty else {},
                'balance_sheet': balance_sheet.to_dict() if not balance_sheet.empty else {},
                'cash_flow': cash_flow.to_dict() if not cash_flow.empty else {},
                'earnings': earnings.to_dict() if not earnings.empty else {},
                'institutional_holders': institutional_holders.to_dict() if institutional_holders is not None and not institutional_holders.empty else {},
                'recommendations': recommendations.to_dict() if recommendations is not None and not recommendations.empty else {},
                'status': 'success'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    @staticmethod
    async def get_news_sentiment(client: AsyncClient, symbol: str) -> Dict[str, Any]:
        """Fetch and analyze news sentiment using FinBERT"""
        # Note: Implement news fetching from free sources and sentiment analysis
        pass

class FinancialAnalyzer:
    """Analyzes financial data and calculates metrics"""
    
    @staticmethod
    def analyze_fundamentals(data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive fundamental analysis"""
        analysis = {}
        
        try:
            # Profitability Metrics
            analysis['profitability'] = {
                'gross_margin': data['info'].get('grossMargins'),
                'operating_margin': data['info'].get('operatingMargins'),
                'profit_margin': data['info'].get('profitMargins'),
                'roe': data['info'].get('returnOnEquity'),
                'roa': data['info'].get('returnOnAssets'),
                'roic': data['info'].get('returnOnCapital')
            }
            
            # Valuation Metrics
            analysis['valuation'] = {
                'pe_ratio': data['info'].get('trailingPE'),
                'forward_pe': data['info'].get('forwardPE'),
                'peg_ratio': data['info'].get('pegRatio'),
                'price_to_book': data['info'].get('priceToBook'),
                'price_to_sales': data['info'].get('priceToSalesTrailing12Months'),
                'enterprise_value': data['info'].get('enterpriseValue'),
                'ev_to_ebitda': data['info'].get('enterpriseToEbitda'),
                'ev_to_revenue': data['info'].get('enterpriseToRevenue')
            }
            
            # Growth Metrics
            analysis['growth'] = {
                'revenue_growth': data['info'].get('revenueGrowth'),
                'earnings_growth': data['info'].get('earningsGrowth'),
                'earnings_quarterly_growth': data['info'].get('earningsQuarterlyGrowth')
            }
            
            # Financial Health
            analysis['financial_health'] = {
                'current_ratio': data['info'].get('currentRatio'),
                'debt_to_equity': data['info'].get('debtToEquity'),
                'quick_ratio': data['info'].get('quickRatio'),
                'total_debt': data['info'].get('totalDebt'),
                'total_cash': data['info'].get('totalCash'),
                'free_cash_flow': data['info'].get('freeCashflow')
            }
            
            # Dividend Analysis
            analysis['dividend'] = {
                'dividend_rate': data['info'].get('dividendRate'),
                'dividend_yield': data['info'].get('dividendYield'),
                'payout_ratio': data['info'].get('payoutRatio'),
                'five_year_avg_dividend_yield': data['info'].get('fiveYearAvgDividendYield')
            }
            
            # Efficiency Metrics
            analysis['efficiency'] = {
                'inventory_turnover': data['info'].get('inventoryTurnover'),
                'asset_turnover': data['info'].get('assetTurnover'),
                'revenue_per_employee': data['info'].get('revenuePerEmployee')
            }
            
            # Market Position
            analysis['market_position'] = {
                'market_cap': data['info'].get('marketCap'),
                'enterprise_value': data['info'].get('enterpriseValue'),
                'beta': data['info'].get('beta'),
                'float_shares': data['info'].get('floatShares'),
                'shares_outstanding': data['info'].get('sharesOutstanding'),
                'shares_short': data['info'].get('sharesShort'),
                'short_ratio': data['info'].get('shortRatio')
            }

            return analysis
            
        except Exception as e:
            return {'error': f"Error in fundamental analysis: {str(e)}"}

class CompetitiveAnalysis:
    """Analyzes competitive position and industry comparisons"""
    
    @staticmethod
    def analyze_competitive_position(data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive position in the industry"""
        try:
            industry = data['info'].get('industry')
            sector = data['info'].get('sector')
            
            analysis = {
                'industry': industry,
                'sector': sector,
                'market_position': {
                    'market_cap_category': CompetitiveAnalysis._categorize_market_cap(
                        data['info'].get('marketCap')
                    ),
                    'industry_rank': data['info'].get('industryRank'),
                    'sector_rank': data['info'].get('sectorRank')
                },
                'competitive_advantages': CompetitiveAnalysis._analyze_competitive_advantages(data)
            }
            
            return analysis
        except Exception as e:
            return {'error': f"Error in competitive analysis: {str(e)}"}
    
    @staticmethod
    def _categorize_market_cap(market_cap: float) -> str:
        if market_cap is None:
            return "Unknown"
        elif market_cap >= 200e9:
            return "Mega Cap"
        elif market_cap >= 10e9:
            return "Large Cap"
        elif market_cap >= 2e9:
            return "Mid Cap"
        elif market_cap >= 300e6:
            return "Small Cap"
        else:
            return "Micro Cap"
    
    @staticmethod
    def _analyze_competitive_advantages(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential competitive advantages"""
        advantages = []
        
        info = data['info']
        
        # Profitability advantage
        if info.get('operatingMargins', 0) > 0.20:  # 20% operating margin
            advantages.append({
                'type': 'High Profitability',
                'description': 'Company shows strong operational efficiency'
            })
        
        # Market leader advantage
        if info.get('marketPosition') == 1:
            advantages.append({
                'type': 'Market Leadership',
                'description': 'Company is a market leader in its industry'
            })
        
        return advantages