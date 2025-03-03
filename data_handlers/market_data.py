# data_handlers/market_data.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class MarketDataHandler:
    def __init__(self):
        # Map country codes to major indices, currencies, and bonds
        self.country_assets = {
            'us': {
                'indices': ['^GSPC', '^DJI', '^IXIC'],  # S&P 500, Dow Jones, NASDAQ
                'currency': 'USDEUR=X',  # USD to EUR
                'bonds': '^TNX',  # 10-year Treasury yield
                'vix': '^VIX'  # Volatility index
            },
            'uk': {
                'indices': ['^FTSE'],  # FTSE 100
                'currency': 'GBPUSD=X',  # GBP to USD
                'bonds': '^TMBMKGB-10Y'  # UK 10-year Gilt
            },
            'jp': {
                'indices': ['^N225'],  # Nikkei 225
                'currency': 'JPYUSD=X',  # JPY to USD
                'bonds': '^JGBS10Y'  # Japan 10-year Gov Bond
            },
            'cn': {
                'indices': ['^SSEC', '000300.SS'],  # Shanghai Composite, CSI 300
                'currency': 'CNYUSD=X',  # CNY to USD
            },
            'de': {
                'indices': ['^GDAXI'],  # DAX
                'currency': 'EURUSD=X',  # EUR to USD
                'bonds': '^TMBMKDE-10Y'  # German 10-year Bund
            },
            # Add more countries as needed
        }
        
        # Cache to minimize API calls
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 3600  # Cache for 1 hour
    
    def get_country_market_data(self, country_code):
        """Get market data for a specific country."""
        # Check cache first
        cache_key = f"market_{country_code}"
        current_time = datetime.now().timestamp()
        
        if cache_key in self.cache and self.cache_expiry.get(cache_key, 0) > current_time:
            return self.cache[cache_key]
        
        # If not in cache or expired, fetch new data
        country_assets = self.country_assets.get(country_code)
        if not country_assets:
            return {"error": f"No market data configured for {country_code}"}
        
        result = {
            "indices": [],
            "currency": None,
            "bonds": None,
            "other": []
        }
        
        # Get data for indices
        if 'indices' in country_assets:
            for ticker in country_assets['indices']:
                try:
                    index_data = self._get_ticker_data(ticker)
                    if index_data:
                        result["indices"].append(index_data)
                except Exception as e:
                    print(f"Error fetching index {ticker}: {e}")
        
        # Get currency data
        if 'currency' in country_assets:
            try:
                currency_data = self._get_ticker_data(country_assets['currency'])
                if currency_data:
                    result["currency"] = currency_data
            except Exception as e:
                print(f"Error fetching currency {country_assets['currency']}: {e}")
        
        # Get bond data
        if 'bonds' in country_assets:
            try:
                bond_data = self._get_ticker_data(country_assets['bonds'])
                if bond_data:
                    result["bonds"] = bond_data
            except Exception as e:
                print(f"Error fetching bond {country_assets['bonds']}: {e}")
        
        # Get other data (like VIX)
        if 'vix' in country_assets:
            try:
                vix_data = self._get_ticker_data(country_assets['vix'])
                if vix_data:
                    result["other"].append(vix_data)
            except Exception as e:
                print(f"Error fetching VIX {country_assets['vix']}: {e}")
        
        # Cache the result
        self.cache[cache_key] = result
        self.cache_expiry[cache_key] = current_time + self.cache_duration
        
        return result
    
    def _get_ticker_data(self, ticker):
        """Get data for a specific ticker."""
        try:
            # Check individual ticker cache
            cache_key = f"ticker_{ticker}"
            current_time = datetime.now().timestamp()
            
            if cache_key in self.cache and self.cache_expiry.get(cache_key, 0) > current_time:
                return self.cache[cache_key]
            
            # Get ticker info
            ticker_obj = yf.Ticker(ticker)
            
            # Get recent history
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)
            history = ticker_obj.history(start=start_date, end=end_date)
            
            if history.empty:
                return None
            
            # Calculate change
            if len(history) >= 2:
                latest = history.iloc[-1]
                previous = history.iloc[-2]
                change_pct = ((latest['Close'] - previous['Close']) / previous['Close']) * 100
            else:
                change_pct = 0
            
            # Basic info
            info = {
                "ticker": ticker,
                "name": ticker_obj.info.get('shortName', ticker),
                "price": history.iloc[-1]['Close'],
                "change_percent": change_pct,
                "currency": ticker_obj.info.get('currency', 'USD')
            }
            
            # Cache this ticker's data
            self.cache[cache_key] = info
            self.cache_expiry[cache_key] = current_time + self.cache_duration
            
            return info
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None