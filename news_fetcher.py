"""
News & Earnings Fetcher
Fetches real news and earnings data to enhance IV analysis
"""

import requests
from datetime import datetime, timedelta
import os
from ddgs import DDGS
import time

ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')


def get_earnings_info(ticker):
    """
    Get earnings information from Alpha Vantage
    Returns: dict with earnings date, results, etc.
    """
    if not ALPHA_VANTAGE_KEY:
        return None

    url = f"https://www.alphavantage.co/query"
    params = {
        'function': 'EARNINGS_CALENDAR',
        'symbol': ticker,
        'apikey': ALPHA_VANTAGE_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return None

        # Parse CSV response
        lines = response.text.strip().split('\n')
        if len(lines) < 2:
            return None

        # Get most recent earnings (first data row)
        headers = lines[0].split(',')
        data = lines[1].split(',')

        if len(data) < len(headers):
            return None

        earnings_data = dict(zip(headers, data))

        return {
            'date': earnings_data.get('reportDate', 'N/A'),
            'estimate': earnings_data.get('estimate', 'N/A'),
            'actual': earnings_data.get('actual', 'N/A'),
            'surprise': earnings_data.get('surprise', 'N/A')
        }

    except Exception as e:
        print(f"   ⚠️  Earnings API error for {ticker}: {str(e)}")
        return None


def get_company_news_av(ticker):
    """
    Get company news from Alpha Vantage
    """
    if not ALPHA_VANTAGE_KEY:
        return []

    url = f"https://www.alphavantage.co/query"
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': ticker,
        'limit': 5,
        'apikey': ALPHA_VANTAGE_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return []

        data = response.json()

        if 'feed' not in data:
            return []

        news_items = []
        for item in data['feed'][:3]:  # Top 3 articles
            news_items.append({
                'title': item.get('title', ''),
                'date': item.get('time_published', '')[:10],  # YYYY-MM-DD
                'summary': item.get('summary', '')[:150],
                'source': item.get('source', '')
            })

        return news_items

    except Exception as e:
        print(f"   ⚠️  News API error for {ticker}: {str(e)}")
        return []


def search_recent_news(ticker, days=7):
    """
    Search recent news using DuckDuckGo (no API key needed!)
    """
    try:
        # Search query
        query = f"{ticker} stock news last {days} days"

        # Use DuckDuckGo search
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return []

        news_items = []
        for result in results[:3]:  # Top 3
            news_items.append({
                'title': result.get('title', ''),
                'url': result.get('link', ''),
                'snippet': result.get('body', '')[:150]
            })

        return news_items

    except Exception as e:
        print(f"   ⚠️  Web search error for {ticker}: {str(e)}")
        return []


def get_comprehensive_context(ticker, iv_change_pct, iv_current):
    """
    Get comprehensive context combining earnings + news
    """
    context = {
        'ticker': ticker,
        'iv_change': iv_change_pct,
        'iv_current': iv_current,
        'earnings': None,
        'alpha_news': [],
        'web_news': [],
        'summary': ''
    }

    print(f"   🔍 Fetching news for {ticker}...")

    # Get earnings info
    earnings = get_earnings_info(ticker)
    if earnings:
        context['earnings'] = earnings
        print(f"   ✅ Found earnings data")

    # Get news from Alpha Vantage
    time.sleep(0.5)  # Rate limiting
    alpha_news = get_company_news_av(ticker)
    if alpha_news:
        context['alpha_news'] = alpha_news
        print(f"   ✅ Found {len(alpha_news)} news articles (Alpha Vantage)")

    # Get news from web search
    time.sleep(0.5)  # Rate limiting
    web_news = search_recent_news(ticker)
    if web_news:
        context['web_news'] = web_news
        print(f"   ✅ Found {len(web_news)} news articles (web search)")

    # Build summary text for GPT
    summary_parts = []

    if earnings:
        summary_parts.append(f"Earnings: Date={earnings['date']}, Est={earnings['estimate']}, Act={earnings['actual']}")

    if alpha_news:
        summary_parts.append("Recent headlines (Alpha Vantage):")
        for news in alpha_news:
            summary_parts.append(f"- {news['title']} ({news['date']})")

    if web_news:
        summary_parts.append("Recent headlines (web):")
        for news in web_news:
            summary_parts.append(f"- {news['title']}")

    context['summary'] = '\n'.join(summary_parts)

    return context


def format_enhanced_prompt(ticker, iv_change_pct, iv_current, context):
    """
    Create enhanced GPT prompt with actual news context
    """

    prompt = f"""Analyze this IV change with ACTUAL context:

Ticker: {ticker}
IV Change (7 days): {iv_change_pct:+.1f}%
Current IV: {iv_current:.1f}%

ACTUAL CONTEXT:
{context['summary'] if context['summary'] else 'No specific news found.'}

Provide 2-3 sentences:
1. What ACTUALLY happened (cite specific events/dates if available)
2. Why IV moved (specific reason, not speculation)
3. ONE actionable trade idea with specific strikes/timeframes

Be specific and factual. If no news, say "No specific catalyst identified" and focus on technical IV analysis.
"""

    return prompt


if __name__ == "__main__":
    # Test the module
    test_ticker = "AAPL"

    print(f"\nTesting news fetcher for {test_ticker}...\n")

    context = get_comprehensive_context(test_ticker, 25.0, 35.5)

    print(f"\n{'=' * 70}")
    print("CONTEXT SUMMARY:")
    print(f"{'=' * 70}")
    print(context['summary'])
    print(f"{'=' * 70}\n")
