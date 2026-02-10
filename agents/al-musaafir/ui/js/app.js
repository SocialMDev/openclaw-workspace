// Al-Musaafir UI Controller
const App = {
    currentView: 'dashboard',
    
    init() {
        this.bindEvents();
        this.loadSavedData();
        console.log('Al-Musaafir UI initialized - Yalla!');
    },
    
    bindEvents() {
        // Form submissions
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        });
        
        // Range slider updates
        const rangeSlider = document.getElementById('max-travel-time');
        if (rangeSlider) {
            rangeSlider.addEventListener('input', (e) => {
                document.querySelector('.range-value').textContent = e.target.value + ' hours';
            });
        }
        
        // Airline tag toggles
        document.querySelectorAll('.tag').forEach(tag => {
            tag.addEventListener('click', function() {
                this.classList.toggle('active');
            });
        });
        
        // Navigation from keyboard
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.currentView !== 'dashboard') {
                this.showDashboard();
            }
        });
    },
    
    handleSubmit(e) {
        e.preventDefault();
        const formId = e.target.id;
        const resultsArea = e.target.nextElementSibling;
        
        // Show loading state
        resultsArea.innerHTML = '<div class="loading"></div><p>Al-Musaafir is searching... (Yalla!)</p>';
        resultsArea.classList.add('has-content');
        
        // Collect form data
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        // Simulate processing (in real implementation, this would call APIs)
        setTimeout(() => {
            this.generateMockResults(formId, resultsArea, data);
        }, 2000);
        
        // Save to localStorage
        this.saveSearch(formId, data);
    },
    
    generateMockResults(formId, container, data) {
        let html = '';
        
        switch(formId) {
            case 'route-form':
                html = this.generateRouteResults(data);
                break;
            case 'timing-form':
                html = this.generateTimingResults(data);
                break;
            case 'hidden-form':
                html = this.generateHiddenResults(data);
                break;
            case 'deals-form':
                html = this.generateDealsResults(data);
                break;
            case 'points-form':
                html = this.generatePointsResults(data);
                break;
            case 'monitor-form':
                html = this.generateMonitorResults(data);
                break;
            case 'audit-form':
                html = this.generateAuditResults(data);
                break;
        }
        
        container.innerHTML = html;
    },
    
    generateRouteResults(data) {
        return `
            <h3 style="color: var(--accent-gold); margin-bottom: 1rem;">🎯 Optimal Routes Found</h3>
            <div style="display: grid; gap: 1rem;">
                <div style="background: var(--bg-card); padding: 1rem; border-radius: 8px; border-left: 3px solid var(--success);">
                    <h4>Best Value: Turkish Airlines</h4>
                    <p>JFK → IST → NRT | $780 | 18h 30m</p>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">✓ Includes lounge access in Istanbul | ✓ 2 free checked bags</p>
                </div>
                <div style="background: var(--bg-card); padding: 1rem; border-radius: 8px; border-left: 3px solid var(--accent-gold);">
                    <h4>Fastest: Direct Flight</h4>
                    <p>JFK → NRT (JAL/ANA) | $1,200 | 14h direct</p>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">✓ No layovers | ✓ Premium service</p>
                </div>
                <div style="background: var(--bg-card); padding: 1rem; border-radius: 8px; border-left: 3px solid var(--warning);">
                    <h4>Budget Option: Split Ticket</h4>
                    <p>JFK → LAX → NRT (Multiple airlines) | $650 | 22h</p>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">⚠ Self-transfer in LAX | Carry-on only recommended</p>
                </div>
            </div>
            <p style="margin-top: 1rem; color: var(--text-muted);">
                <strong>Musaafir's Note:</strong> The Turkish routing saves $420 and gives you a nice break in Istanbul. 
                I've seen this route drop to $650 - shall I set up monitoring?
            </p>
        `;
    },
    
    generateTimingResults(data) {
        return `
            <h3 style="color: var(--accent-gold); margin-bottom: 1rem;">📊 Booking Window Analysis</h3>
            <div style="background: var(--bg-card); padding: 1.5rem; border-radius: 8px;">
                <h4>Optimal Booking Time: 45-60 Days Before</h4>
                <ul style="margin: 1rem 0; padding-left: 1.5rem;">
                    <li>Current day: 52 days out - <strong style="color: var(--success);">BOOK NOW</strong></li>
                    <li>Historical low: $720 (booked 58 days out)</li>
                    <li>Price increase risk: HIGH after 40 days</li>
                    <li>Cheapest day to fly: Tuesday or Wednesday</li>
                </ul>
                <div style="background: rgba(255,215,0,0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <strong>Recommendation:</strong> Book within the next 5 days. 
                    Prices typically spike 30% in the final 3 weeks.
                </div>
            </div>
        `;
    },
    
    generateHiddenResults(data) {
        return `
            <h3 style="color: var(--accent-gold); margin-bottom: 1rem;">💎 Hidden Opportunities</h3>
            
            <div style="background: var(--bg-card); padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid var(--warning);">
                <h4>⚠️ Hidden-City Option Found</h4>
                <p><strong>Route:</strong> NYC → HKG → TYO (Cathay Pacific)</p>
                <p><strong>Price:</strong> $650 (vs $1,200 direct)</p>
                <p><strong>You get off at:</strong> Hong Kong (stopover)</p>
                <br>
                <strong>RISKS:</strong>
                <ul style="color: var(--warning);">
                    <li>Carry-on only (checked bag goes to Tokyo)</li>
                    <li>One-way only - airline cancels return if no-show</li>
                    <li>Don't use frequent flyer number</li>
                    <li>If flight is rerouted, you may be in trouble</li>
                </ul>
                <p style="margin-top: 1rem;"><strong>Savings: $550</strong> - Worth it for one-way, but risky for round-trip.</p>
            </div>
            
            <div style="background: var(--bg-card); padding: 1.5rem; border-radius: 8px; border-left: 3px solid var(--success);">
                <h4>✅ Split-Ticket Opportunity</h4>
                <p><strong>NYC → LAX:</strong> $180 (Southwest, direct)</p>
                <p><strong>LAX → TYO:</strong> $420 (zipair, direct)</p>
                <p><strong>Total:</strong> $600 vs $780 connecting via Istanbul</p>
                <p style="margin-top: 0.5rem; color: var(--success);">✓ Saves $180 ✓ Both direct flights ✓ Can use different airlines</p>
                <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.5rem;">
                    Note: Self-transfer in LAX - allow 3+ hours between flights
                </p>
            </div>
        `;
    },
    
    generateDealsResults(data) {
        return `
            <h3 style="color: var(--accent-gold); margin-bottom: 1rem;">🏷️ Airline Direct Deals</h3>
            <div style="display: grid; gap: 1rem;">
                <div style="background: var(--bg-card); padding: 1rem; border-radius: 8px;">
                    <h4>United.com Exclusive</h4>
                    <p>Member fare: $1,050 (vs $1,200 on OTAs)</p>
                    <p style="color: var(--success);">✓ Free seat selection | ✓ Changes allowed</p>
                </div>
                <div style="background: var(--bg-card); padding: 1rem; border-radius: 8px;">
                    <h4>JAL Direct (Japan Airlines)</h4>
                    <p>New customer promo: $1,100 + 5,000 bonus miles</p>
                    <p style="color: var(--success);">✓ Premium service | ✓ Authentic Japanese experience</p>
                </div>
                <div style="background: rgba(255,215,0,0.1); padding: 1rem; border-radius: 8px; border: 1px solid var(--accent-gold);">
                    <strong>💡 Insider Tip:</strong> ANA (All Nippon) often has unadvertised 
                    discounts for direct bookings from their US website. Check ana.co.jp/us/en/ 
                    and use Google Translate if needed!
                </div>
            </div>
        `;
    },
    
    generatePointsResults(data) {
        return `
            <h3 style="color: var(--accent-gold); margin-bottom: 1rem;">💳 Points Strategy</h3>
            <div style="background: var(--bg-card); padding: 1.5rem; border-radius: 8px;">
                <h4>Best Redemption: Chase UR → Air Canada Aeroplan</h4>
                <ul style="margin: 1rem 0; padding-left: 1.5rem;">
                    <li>Business class: 70,000 points</li>
                    <li>Cash value: $5,000</li>
                    <li><strong>CPP: 7.1¢</strong> (Excellent!)</li>
                    <li>Route: JFK → YVR → NRT (Star Alliance)</li>
                </ul>
                
                <div style="background: rgba(76,175,80,0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <strong>Alternative: Virgin Atlantic (with Amex transfer bonus)</strong>
                    <p>ANA First Class: 90,000 points + $200 taxes</p>
                    <p>Cash value: $15,000+ | <strong>CPP: 16.6¢</strong> (Mashallah!)</p>
                </div>
                
                <p style="margin-top: 1rem; color: var(--text-muted);">
                    <strong>Recommendation:</strong> If you have Amex MR with 30% transfer bonus to Virgin, 
                    the ANA First Class is one of the best redemptions in the world.
                </p>
            </div>
        `;
    },
    
    generateMonitorResults(data) {
        const route = data['monitor-route'] || 'your route';
        const price = data['target-price'] || '800';
        const email = data['alert-email'] || 'your email';
        
        return `
            <h3 style="color: var(--accent-gold); margin-bottom: 1rem;">🔔 Price Monitoring Activated</h3>
            <div style="background: var(--bg-card); padding: 1.5rem; border-radius: 8px;">
                <h4>✅ Monitoring Setup Complete</h4>
                <ul style="margin: 1rem 0; padding-left: 1.5rem;">
                    <li><strong>Route:</strong> ${route}</li>
                    <li><strong>Target Price:</strong> $${price}</li>
                    <li><strong>Alert Email:</strong> ${email}</li>
                    <li><strong>Check Frequency:</strong> Every 6 hours</li>
                    <li><strong>Active Monitors:</strong></li>
                    <ul style="margin-left: 1.5rem;">
                        <li>✓ Google Flights price tracking</li>
                        <li>✓ Secret Flying error fares</li>
                        <li>✓ Award space alerts (United, Aeroplan)</li>
                        <li>✓ Flash sale notifications</li>
                    </ul>
                </ul>
                <p style="color: var(--success);">
                    You'll receive an alert immediately when the price drops below $${price} 
                    or when error fares appear!
                </p>
            </div>
        `;
    },
    
    generateAuditResults(data) {
        return `
            <h3 style="color: var(--accent-gold); margin-bottom: 1rem;">✅ Pre-Booking Audit</h3>
            
            <div style="background: var(--bg-card); padding: 1.5rem; border-radius: 8px;">
                <h4>📋 Audit Checklist</h4>
                
                <div style="margin: 1rem 0;">
                    <h5 style="color: var(--success);">✓ Pricing Verified</h5>
                    <ul style="margin-left: 1.5rem; color: var(--text-muted);">
                        <li>No cheaper alternatives found</li>
                        <li>Direct booking saves $150 vs OTA</li>
                        <li>No hidden fees detected</li>
                    </ul>
                </div>
                
                <div style="margin: 1rem 0;">
                    <h5 style="color: var(--warning);">⚠️ Risks Identified</h5>
                    <ul style="margin-left: 1.5rem; color: var(--warning);">
                        <li>1h 45m layover in Frankfurt - acceptable but tight</li>
                        <li>Terminal change required (T1 → T2)</li>
                        <li>Winter weather possible in January</li>
                    </ul>
                </div>
                
                <div style="margin: 1rem 0;">
                    <h5 style="color: var(--success);">✓ Requirements Met</h5>
                    <ul style="margin-left: 1.5rem; color: var(--text-muted);">
                        <li>Passport validity: 8 months (✓ 6+ required)</li>
                        <li>Japan: 90 days visa-free for US citizens</li>
                        <li>Transit visa not needed for Germany</li>
                    </ul>
                </div>
                
                <div style="background: rgba(76,175,80,0.1); padding: 1rem; border-radius: 8px; margin-top: 1.5rem;">
                    <h4 style="color: var(--success);">🎯 GO/NO-GO Decision: GO</h4>
                    <p>This is a solid booking at a fair price. The layover is manageable, 
                    and you've found a good deal. Book within 24 hours to lock in this price!</p>
                </div>
            </div>
        `;
    },
    
    showDashboard() {
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.getElementById('dashboard').classList.add('active');
        this.currentView = 'dashboard';
        window.scrollTo(0, 0);
    },
    
    showTool(toolId) {
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.getElementById(toolId).classList.add('active');
        this.currentView = toolId;
        window.scrollTo(0, 0);
    },
    
    saveSearch(formId, data) {
        const searches = JSON.parse(localStorage.getItem('alMusaafirSearches') || '[]');
        searches.push({
            id: Date.now(),
            form: formId,
            data: data,
            timestamp: new Date().toISOString()
        });
        // Keep only last 20 searches
        if (searches.length > 20) searches.shift();
        localStorage.setItem('alMusaafirSearches', JSON.stringify(searches));
    },
    
    loadSavedData() {
        // Could restore form data or show recent searches
        const searches = JSON.parse(localStorage.getItem('alMusaafirSearches') || '[]');
        if (searches.length > 0) {
            console.log(`Loaded ${searches.length} recent searches`);
        }
    }
};

// Global functions for HTML onclick handlers
function showDashboard() {
    App.showDashboard();
}

function showTool(toolId) {
    App.showTool(toolId);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// Expose App for debugging
window.AlMusaafir = App;
