// static/js/app.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map
    initMap();
    
    // Set up filters
    document.getElementById('asset-filter').addEventListener('change', updateNewsForCountry);
    document.getElementById('region-filter').addEventListener('change', filterMapByRegion);
});

// Global variables
let worldMap;
let currentCountry = 'us'; // Default to US

async function initMap() {
    // Map dimensions
    const width = document.getElementById('map-container').offsetWidth;
    const height = document.getElementById('map-container').offsetHeight;
    
    // Create SVG
    const svg = d3.select('#map-container').append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Create a group for the map
    worldMap = svg.append('g');
    
    // Define projection
    const projection = d3.geoNaturalEarth1()
        .scale(width / 6)
        .translate([width / 2, height / 2]);
    
    // Create path generator
    const path = d3.geoPath().projection(projection);
    
    // Fetch GeoJSON data
    try {
        const response = await fetch('/api/countries');
        const geojson = await response.json();
        
        // Draw countries
        worldMap.selectAll('path')
            .data(geojson.features)
            .enter()
            .append('path')
            .attr('class', d => `country ${d.properties.iso_a2 ? d.properties.iso_a2.toLowerCase() : ''}`)
            .attr('d', path)
            .attr('data-id', d => d.properties.iso_a2 ? d.properties.iso_a2.toLowerCase() : '')
            .attr('data-name', d => d.properties.name || '')
            .attr('data-region', d => getRegion(d.properties.region))
            .on('click', function(event, d) {
                const countryCode = d.properties.iso_a2 ? d.properties.iso_a2.toLowerCase() : '';
                if (countryCode) {
                    selectCountry(countryCode, d.properties.name);
                }
            });
        
        // Highlight US by default
        selectCountry('us', 'United States');
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([1, 8])
            .on('zoom', (event) => {
                worldMap.attr('transform', event.transform);
            });
        
        svg.call(zoom);
        
    } catch (error) {
        console.error('Error loading map data:', error);
    }
}

function getRegion(regionCode) {
    // Map region codes to our simplified regions
    const regionMap = {
        'Americas': 'americas',
        'Europe': 'europe',
        'Asia': 'asia',
        'Africa': 'africa',
        'Oceania': 'asia', // Group with Asia
    };
    
    return regionMap[regionCode] || 'other';
}

function selectCountry(countryCode, countryName) {
    // Remove active class from all countries
    d3.selectAll('.country').classed('active', false);
    
    // Add active class to selected country
    d3.select(`.country.${countryCode}`).classed('active', true);
    
    // Update current country
    currentCountry = countryCode;
    
    // Update country header
    document.getElementById('selected-country').textContent = countryName || countryCode.toUpperCase();
    
    // Get region from map
    const regionElement = document.querySelector(`.country.${countryCode}`);
    const region = regionElement ? regionElement.getAttribute('data-region') : '';
    
    // Map region code to readable name
    const regionNames = {
        'americas': 'Americas',
        'europe': 'Europe',
        'asia': 'Asia-Pacific',
        'africa': 'Africa',
        'other': 'Other'
    };
    
    document.getElementById('country-region').textContent = regionNames[region] || 'Global';
    
    // Load country data
    loadCountryData(countryCode);
}

async function loadCountryData(countryCode) {
    try {
        // Show loading state
        document.getElementById('market-data-container').innerHTML = `
            <div class="placeholder-glow">
                <p class="placeholder col-12"></p>
                <p class="placeholder col-12"></p>
                <p class="placeholder col-12"></p>
            </div>`;
        
        document.getElementById('news-list').innerHTML = `
            <div class="placeholder-glow">
                <p class="placeholder col-12"></p>
                <p class="placeholder col-12"></p>
                <p class="placeholder col-12"></p>
                <p class="placeholder col-12"></p>
                <p class="placeholder col-12"></p>
            </div>`;
        
        // Fetch country data
        const response = await fetch(`/api/country/${countryCode}`);
        const data = await response.json();
        
        // Update market data section
        updateMarketData(data.market_data);
        
        // Update news section
        updateNews(data.news);
        
    } catch (error) {
        console.error('Error loading country data:', error);
        
        // Show error message
        document.getElementById('market-data-container').innerHTML = `
            <div class="alert alert-danger">
                Error loading market data. Please try again later.
            </div>`;
        
        document.getElementById('news-list').innerHTML = `
            <div class="alert alert-danger">
                Error loading news. Please try again later.
            </div>`;
    }
}

function updateMarketData(marketData) {
    const container = document.getElementById('market-data-container');
    
    if (!marketData || marketData.error) {
        container.innerHTML = `
            <div class="alert alert-warning">
                No market data available for this country.
            </div>`;
        return;
    }
    
    let html = '';
    
    // Add indices
    if (marketData.indices && marketData.indices.length > 0) {
        marketData.indices.forEach(index => {
            const changeClass = index.change_percent > 0 ? 'positive' : index.change_percent < 0 ? 'negative' : '';
            const changeSign = index.change_percent > 0 ? '+' : '';
            
            html += `
                <div class="market-item">
                    <div class="market-name">${index.name}</div>
                    <div class="d-flex justify-content-between">
                        <span>${index.price.toFixed(2)}</span>
                        <span class="${changeClass}">${changeSign}${index.change_percent.toFixed(2)}%</span>
                    </div>
                </div>`;
        });
    }
    
    // Add currency
    if (marketData.currency) {
        const currency = marketData.currency;
        const changeClass = currency.change_percent > 0 ? 'positive' : currency.change_percent < 0 ? 'negative' : '';
        const changeSign = currency.change_percent > 0 ? '+' : '';
        
        html += `
            <div class="market-item">
                <div class="market-name">${currency.name}</div>
                <div class="d-flex justify-content-between">
                    <span>${currency.price.toFixed(4)}</span>
                    <span class="${changeClass}">${changeSign}${currency.change_percent.toFixed(2)}%</span>
                </div>
            </div>`;
    }
    
    // Add bonds
    if (marketData.bonds) {
        const bond = marketData.bonds;
        const changeClass = bond.change_percent > 0 ? 'positive' : bond.change_percent < 0 ? 'negative' : '';
        const changeSign = bond.change_percent > 0 ? '+' : '';
        
        html += `
            <div class="market-item">
                <div class="market-name">${bond.name}</div>
                <div class="d-flex justify-content-between">
                    <span>${bond.price.toFixed(2)}%</span>
                    <span class="${changeClass}">${changeSign}${bond.change_percent.toFixed(2)}%</span>
                </div>
            </div>`;
    }
    
    // Add other metrics (like VIX)
    if (marketData.other && marketData.other.length > 0) {
        marketData.other.forEach(item => {
            const changeClass = item.change_percent > 0 ? 'positive' : item.change_percent < 0 ? 'negative' : '';
            const changeSign = item.change_percent > 0 ? '+' : '';
            
            html += `
                <div class="market-item">
                    <div class="market-name">${item.name}</div>
                    <div class="d-flex justify-content-between">
                        <span>${item.price.toFixed(2)}</span>
                        <span class="${changeClass}">${changeSign}${item.change_percent.toFixed(2)}%</span>
                    </div>
                </div>`;
        });
    }
    
    // If no data, show message
    if (html === '') {
        html = `
            <div class="alert alert-warning">
                No market data available for this country.
            </div>`;
    }
    
    container.innerHTML = html;
}

function updateNews(newsItems) {
    const container = document.getElementById('news-list');
    
    if (!newsItems || newsItems.length === 0) {
        container.innerHTML = `
            <div class="alert alert-warning">
                No news available for this country.
            </div>`;
        return;
    }
    
    // Filter by asset class if selected
    const assetFilter = document.getElementById('asset-filter').value;
    if (assetFilter !== 'all') {
        newsItems = newsItems.filter(item => item.asset_class === assetFilter);
    }
    
    if (newsItems.length === 0) {
        container.innerHTML = `
            <div class="alert alert-warning">
                No news available for the selected asset class.
            </div>`;
        return;
    }
    
    let html = '';
    
    newsItems.forEach(item => {
        html += `
            <div class="news-item">
                <div class="news-source">${item.source} • ${item.asset_class}</div>
                <div class="news-headline">
                    <a href="${item.link}" target="_blank">${item.headline}</a>
                </div>
                <div class="news-time">${item.time}</div>
            </div>`;
    });
    
    container.innerHTML = html;
}

function updateNewsForCountry() {
    // Reload news for current country with filter
    const assetFilter = document.getElementById('asset-filter').value;
    
    fetch(`/api/news?country=${currentCountry}&asset=${assetFilter}`)
        .then(response => response.json())
        .then(data => {
            updateNews(data);
        })
        .catch(error => {
            console.error('Error updating news:', error);
        });
}

function filterMapByRegion() {
    const region = document.getElementById('region-filter').value;
    
    if (region === 'all') {
        // Show all countries
        d3.selectAll('.country').style('opacity', 1);
    } else {
        // Highlight countries in selected region
        d3.selectAll('.country')
            .style('opacity', function() {
                const countryRegion = d3.select(this).attr('data-region');
                return countryRegion === region ? 1 : 0.3;
            });
    }
}