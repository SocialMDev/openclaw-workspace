// Al-Musaafir Pricing Engine - Dynamic Results Based on Route Data

const PricingEngine = {
    // Route distance estimates (approximate flight miles)
    distances: {
        'NYC-LON': 3450, 'NYC-PAR': 3630, 'NYC-TYO': 6730, 'NYC-DXB': 6830,
        'NYC-SIN': 9530, 'NYC-SYD': 9950, 'NYC-LAX': 2450, 'NYC-CHI': 730,
        'LAX-TYO': 5470, 'LAX-SYD': 7490, 'LAX-LON': 5450, 'LAX-PAR': 5680,
        'LAX-SFO': 340, 'LAX-SEA': 960, 'LAX-MIA': 2340, 'LAX-DFW': 1240,
        'LON-TYO': 5940, 'LON-DXB': 3400, 'LON-SIN': 6740, 'LON-SYD': 10560,
        'LON-PAR': 210, 'LON-AMS': 220, 'LON-FRA': 410, 'LON-IST': 1560,
        'PAR-TYO': 6040, 'PAR-DXB': 3260, 'PAR-SIN': 6660, 'TYO-SIN': 3300,
        'TYO-SYD': 4840, 'DXB-SIN': 3630, 'DXB-SYD': 7480, 'SIN-SYD': 3910,
        'CHI-LON': 3950, 'CHI-PAR': 4150, 'CHI-TYO': 6300, 'SFO-TYO': 5120,
        'SFO-SYD': 7420, 'MIA-LON': 4430, 'MIA-PAR': 4620, 'SEA-LON': 4780
    },

    // Base price per mile by route popularity (cents per mile)
    routeMultipliers: {
        // High volume routes - lower CPM
        'NYC-LON': 0.12, 'NYC-PAR': 0.12, 'LON-PAR': 0.25, 'LAX-SFO': 0.28,
        'NYC-LAX': 0.10, 'LON-AMS': 0.22, 'LON-FRA': 0.20, 'LAX-SEA': 0.15,
        
        // Medium volume - standard CPM
        'NYC-TYO': 0.14, 'LAX-TYO': 0.13, 'LON-TYO': 0.13, 'PAR-TYO': 0.13,
        'NYC-SYD': 0.11, 'LAX-SYD': 0.10, 'LON-SYD': 0.10,
        
        // Premium routes - higher CPM
        'NYC-DXB': 0.15, 'NYC-SIN': 0.13, 'LON-DXB': 0.14, 'LON-SIN': 0.12,
        'TYO-SIN': 0.18, 'DXB-SIN': 0.16, 'DXB-SYD': 0.11,
        
        // Default for unlisted routes
        'default': 0.14
    },

    // Airline pricing tiers
    airlines: {
        'turkish': { name: 'Turkish Airlines', multiplier: 0.65, quality: 'high', layover: 'IST' },
        'qatar': { name: 'Qatar Airways', multiplier: 0.75, quality: 'luxury', layover: 'DOH' },
        'emirates': { name: 'Emirates', multiplier: 0.80, quality: 'luxury', layover: 'DXB' },
        'singapore': { name: 'Singapore Airlines', multiplier: 0.85, quality: 'luxury', layover: 'SIN' },
        'ana': { name: 'ANA (All Nippon)', multiplier: 0.90, quality: 'premium', layover: null },
        'jal': { name: 'Japan Airlines', multiplier: 0.90, quality: 'premium', layover: null },
        'lufthansa': { name: 'Lufthansa', multiplier: 0.88, quality: 'premium', layover: 'FRA' },
        'ba': { name: 'British Airways', multiplier: 0.92, quality: 'premium', layover: 'LHR' },
        'airfrance': { name: 'Air France', multiplier: 0.90, quality: 'premium', layover: 'CDG' },
        'united': { name: 'United Airlines', multiplier: 0.85, quality: 'standard', layover: null },
        'delta': { name: 'Delta Airlines', multiplier: 0.87, quality: 'standard', layover: null },
        'american': { name: 'American Airlines', multiplier: 0.85, quality: 'standard', layover: null },
        'norwegian': { name: 'Norwegian', multiplier: 0.45, quality: 'budget', layover: null },
        'level': { name: 'Level', multiplier: 0.42, quality: 'budget', layover: null },
        'zipair': { name: 'Zipair', multiplier: 0.40, quality: 'budget', layover: null }
    },

    // Calculate distance between two cities
    getDistance(from, to) {
        const key1 = `${from}-${to}`;
        const key2 = `${to}-${from}`;
        return this.distances[key1] || this.distances[key2] || 4000; // Default to 4000 miles
    },

    // Get route multiplier
    getRouteMultiplier(from, to) {
        const key1 = `${from}-${to}`;
        const key2 = `${to}-${from}`;
        return this.routeMultipliers[key1] || this.routeMultipliers[key2] || this.routeMultipliers.default;
    },

    // Calculate base price for a route
    calculateBasePrice(from, to) {
        const distance = this.getDistance(from, to);
        const multiplier = this.getRouteMultiplier(from, to);
        return Math.round(distance * multiplier);
    },

    // Get seasonal factor (simplified - in reality would use actual date)
    getSeasonalFactor(date) {
        if (!date) return 1.0;
        const month = new Date(date).getMonth(); // 0-11
        
        // Peak summer (June-August)
        if (month >= 5 && month <= 7) return 1.35;
        // Christmas/New Year (December)
        if (month === 11) return 1.40;
        // Thanksgiving (November)
        if (month === 10) return 1.25;
        // Spring break (March-April)
        if (month >= 2 && month <= 3) return 1.20;
        // Shoulder season (May, September-October)
        if (month === 4 || month === 8 || month === 9) return 1.0;
        // Off-peak (January-February)
        return 0.85;
    },

    // Get random variation (±10%)
    getVariation() {
        return 0.9 + (Math.random() * 0.2);
    },

    // Generate realistic route results
    generateRouteResults(from, to, date) {
        const basePrice = this.calculateBasePrice(from, to);
        const seasonalFactor = this.getSeasonalFactor(date);
        
        // Select appropriate airlines based on route
        const routeAirlines = this.selectAirlinesForRoute(from, to);
        
        // Generate 3 options with different characteristics
        const options = [];
        
        // Option 1: Best Value (1-stop, good airline)
        const valueAirline = routeAirlines.value;
        const valuePrice = Math.round(basePrice * valueAirline.multiplier * seasonalFactor * this.getVariation());
        const valueDuration = this.calculateDuration(from, to, 1);
        options.push({
            type: 'Best Value',
            airline: valueAirline.name,
            route: from === 'NYC' && to === 'TYO' ? `${from} → IST → ${to}` : `${from} → ${valueAirline.layover || 'Connection'} → ${to}`,
            price: valuePrice,
            duration: valueDuration,
            stops: 1,
            perks: this.getPerks(valueAirline),
            color: 'success'
        });
        
        // Option 2: Direct/ fastest
        const directAirline = routeAirlines.direct;
        const directPrice = Math.round(basePrice * directAirline.multiplier * seasonalFactor * 1.15 * this.getVariation());
        const directDuration = this.calculateDuration(from, to, 0);
        options.push({
            type: 'Fastest',
            airline: directAirline.name,
            route: `${from} → ${to}`,
            price: directPrice,
            duration: directDuration,
            stops: 0,
            perks: ['No layovers', 'Premium service', 'Direct baggage'],
            color: 'gold'
        });
        
        // Option 3: Budget (ultra-low cost or split)
        const budgetPrice = Math.round(basePrice * 0.50 * seasonalFactor * this.getVariation());
        const budgetDuration = this.calculateDuration(from, to, 1) + 4; // Longer
        options.push({
            type: 'Budget Option',
            airline: 'Split Ticket / Budget Airlines',
            route: `${from} → Connection → ${to}`,
            price: budgetPrice,
            duration: budgetDuration,
            stops: 1,
            perks: ['Lowest price', 'Self-transfer required', 'Carry-on only'],
            warning: true,
            color: 'warning'
        });
        
        return options;
    },

    // Select appropriate airlines based on route
    selectAirlinesForRoute(from, to) {
        const isUS = ['NYC', 'LAX', 'CHI', 'SFO', 'MIA', 'DFW', 'SEA', 'BOS'].includes(from) || 
                     ['NYC', 'LAX', 'CHI', 'SFO', 'MIA', 'DFW', 'SEA', 'BOS'].includes(to);
        const isEurope = ['LON', 'PAR', 'BER', 'AMS', 'FRA', 'IST'].includes(from) || 
                         ['LON', 'PAR', 'BER', 'AMS', 'FRA', 'IST'].includes(to);
        const isAsia = ['TYO', 'SIN', 'HKG', 'ICN'].includes(from) || 
                       ['TYO', 'SIN', 'HKG', 'ICN'].includes(to);
        
        // Transatlantic (US-Europe)
        if ((isUS && isEurope) || (isEurope && isUS)) {
            return {
                value: this.airlines.turkish,
                direct: this.airlines.united
            };
        }
        
        // US-Asia
        if ((isUS && isAsia) || (isAsia && isUS)) {
            return {
                value: this.airlines.turkish,
                direct: this.airlines.ana
            };
        }
        
        // Europe-Asia
        if ((isEurope && isAsia) || (isAsia && isEurope)) {
            return {
                value: this.airlines.qatar,
                direct: this.airlines.singapore
            };
        }
        
        // Domestic US
        if (isUS) {
            return {
                value: this.airlines.united,
                direct: this.airlines.delta
            };
        }
        
        // Default
        return {
            value: this.airlines.turkish,
            direct: this.airlines.emirates
        };
    },

    // Calculate flight duration
    calculateDuration(from, to, stops) {
        const distance = this.getDistance(from, to);
        const flightSpeed = 550; // mph average
        const flightTime = (distance / flightSpeed);
        const stopTime = stops * 3; // 3 hours per stop
        const totalHours = Math.ceil(flightTime + stopTime);
        const hours = Math.floor(totalHours);
        const mins = Math.round((totalHours - hours) * 60);
        return `${hours}h ${mins > 0 ? mins + 'm' : ''}`;
    },

    // Get perks for an airline
    getPerks(airline) {
        const perksByQuality = {
            'luxury': ['Lie-flat seats', 'Gourmet dining', 'Premium lounge access', 'Spa access'],
            'premium': ['Extra legroom', 'Priority boarding', 'Enhanced meal service'],
            'high': ['Complimentary meals', 'Free checked bag', 'Seat selection included'],
            'standard': ['Standard seat', 'Buy-on-board meals', 'Free carry-on'],
            'budget': ['Lowest price guarantee', 'Pay for extras', 'Point-to-point']
        };
        return perksByQuality[airline.quality] || perksByQuality.standard;
    },

    // Generate HTML for route results
    renderRouteResults(from, to, date, fromCity, toCity) {
        const options = this.generateRouteResults(from, to, date);
        
        let html = `
            <h3 style="color: var(--accent-gold); margin-bottom: 1rem;">🎯 Optimal Routes: ${fromCity} → ${toCity}</h3>
            <p style="color: var(--text-muted); margin-bottom: 1rem;">Departure: ${date || 'Flexible dates'}</p>
            <div style="display: grid; gap: 1rem;">
        `;
        
        options.forEach(opt => {
            const borderColor = opt.color === 'success' ? 'var(--success)' : 
                               opt.color === 'warning' ? 'var(--warning)' : 'var(--accent-gold)';
            const warningText = opt.warning ? '<p style="color: var(--warning); font-size: 0.9rem;">⚠️ Self-transfer | Carry-on only recommended</p>' : '';
            
            html += `
                <div style="background: var(--bg-card); padding: 1rem; border-radius: 8px; border-left: 3px solid ${borderColor};">
                    <h4>${opt.type}: ${opt.airline}</h4>
                    <p><strong>${opt.route}</strong> | <span style="color: var(--accent-gold); font-size: 1.2em;">$${opt.price}</span> | ${opt.duration}</p>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">✓ ${opt.perks.join(' | ✓ ')}</p>
                    ${warningText}
                </div>
            `;
        });
        
        const savings = options[1].price - options[0].price;
        html += `
            </div>
            <p style="margin-top: 1rem; color: var(--text-muted);">
                <strong>Musaafir's Note:</strong> The ${options[0].airline.split(' ')[0]} routing saves $${savings} vs direct on your ${fromCity} to ${toCity} trip.
                ${savings > 300 ? " That's a significant saving - Mashallah!" : ''}
                I've seen this route drop to $${Math.round(options[0].price * 0.85)} - shall I set up monitoring?
            </p>
        `;
        
        return html;
    }
};

// Make available globally
window.PricingEngine = PricingEngine;
