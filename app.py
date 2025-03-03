# app.py
from flask import Flask, render_template, jsonify, request
import json
import os
from scrapers.yahoo_finance import YahooFinanceScraper
from data_handlers.market_data import MarketDataHandler

app = Flask(__name__)

# Initialize our data handlers
news_scraper = YahooFinanceScraper()
market_data = MarketDataHandler()

# Load country data (for the map)
with open('static/data/countries.geojson', 'r') as f:
    countries_geojson = json.load(f)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/countries')
def get_countries():
    """Return country GeoJSON data for the map."""
    return jsonify(countries_geojson)

@app.route('/api/country/<country_code>')
def get_country_data(country_code):
    """Get all data for a specific country."""
    # Get market data
    markets = market_data.get_country_market_data(country_code)
    
    # Get news
    news = news_scraper.get_country_news(country_code)
    
    # Combine the data
    result = {
        "country_code": country_code,
        "market_data": markets,
        "news": news
    }
    
    return jsonify(result)

@app.route('/api/news')
def get_news():
    """Get filtered news items."""
    country = request.args.get('country', 'us')
    asset_class = request.args.get('asset', 'all')
    
    news = news_scraper.get_country_news(country)
    
    # Filter by asset class if specified
    if asset_class != 'all':
        news = [item for item in news if item['asset_class'] == asset_class]
    
    return jsonify(news)

@app.route('/api/markets')
def get_markets():
    """Get market data for all major countries."""
    countries = ['us', 'uk', 'jp', 'cn', 'de']
    results = {}
    
    for country in countries:
        results[country] = market_data.get_country_market_data(country)
    
    return jsonify(results)

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('static/data', exist_ok=True)
    
    # Download GeoJSON file for countries if not exists
    if not os.path.exists('static/data/countries.geojson'):
        import requests
        print("Downloading countries GeoJSON file...")
        url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
        response = requests.get(url)
        with open('static/data/countries.geojson', 'w') as f:
            f.write(response.text)
        print("Download complete!")
    
    app.run(debug=True)