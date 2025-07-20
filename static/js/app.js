// Dead Stock Intelligence - Main Application JavaScript

// Global variables
let currentLocation = 'mumbai';

let bundleAnalytics = {};

// Immediately hide dashboard on page load to prevent flash for logged-out users
(function() {
  var dash = document.getElementById('shopkeeperDashboard');
  if (dash) dash.style.display = 'none';
})();

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Always hide dashboard on load
    var dash = document.getElementById('shopkeeperDashboard');
    if (dash) dash.style.display = 'none';

    // Only show dashboard if user is authenticated
    if (checkUserAuth()) {
        showShopkeeperDashboard();
    } else {
        showLoggedOutUser();
    }

    // Load public data (not shopkeeper-specific)
    loadHealthStats();
    loadRegionalFestivals();
    loadFestivalCategories();
    
    // Form event listeners
    document.getElementById('productForm').addEventListener('submit', handleProductAnalysis);
    document.getElementById('bundleForm').addEventListener('submit', handleBundleCreation);
    
    // Shopkeeper dashboard form event listeners
    const addProductForm = document.getElementById('addProductForm');
    const recordEventForm = document.getElementById('recordEventForm');
    
    if (addProductForm) {
        addProductForm.addEventListener('submit', handleAddProduct);
    }
    if (recordEventForm) {
        recordEventForm.addEventListener('submit', handleRecordEvent);
    }
});

// Check user authentication status
function checkUserAuth() {
    const userData = localStorage.getItem('shopkeeper_user');
    console.log('Checking user auth, userData:', userData);
    
    if (userData) {
        try {
            const user = JSON.parse(userData);
            console.log('Parsed user data:', user);
            
            if (user && user.user_id) {
                console.log('User authenticated for:', user.user_id);
                showLoggedInUser(user);
                return true;
            } else {
                console.error('Invalid user data structure:', user);
                logout();
                return false;
            }
        } catch (error) {
            console.error('Error parsing user data:', error);
            logout();
            return false;
        }
    } else {
        console.log('No user data found, showing logged out interface');
        return false;
    }
}

// Show logged in user interface
function showLoggedInUser(user) {
    const loginLink = document.getElementById('loginLink');
    const userInfo = document.getElementById('userInfo');
    const userName = document.getElementById('userName');
    
    if (loginLink) loginLink.style.display = 'none';
    if (userInfo) userInfo.style.display = 'block';
    if (userName) userName.textContent = user.shop_name || user.user_id;
}

// Show logged out user interface
function showLoggedOutUser() {
    const loginLink = document.getElementById('loginLink');
    const userInfo = document.getElementById('userInfo');
    const shopkeeperDashboard = document.getElementById('shopkeeperDashboard');
    
    if (loginLink) loginLink.style.display = 'block';
    if (userInfo) userInfo.style.display = 'none';
    if (shopkeeperDashboard) shopkeeperDashboard.style.display = 'none';
}

// Show shopkeeper dashboard
function showShopkeeperDashboard() {
    const dashboard = document.getElementById('shopkeeperDashboard');
    if (dashboard) {
        dashboard.style.display = 'block';
        console.log('Shopkeeper dashboard displayed');
        
        // Only load data if user is logged in
        const userData = localStorage.getItem('shopkeeper_user');
        if (userData) {
            setTimeout(() => {
                loadShopkeeperStats();
                loadProducts();
                loadHistory();
            }, 100);
        }
    } else {
        console.error('Shopkeeper dashboard element not found');
    }
}

// Logout function
function logout() {
    localStorage.removeItem('shopkeeper_user');
    showLoggedOutUser();
    window.location.href = '/';
}

// Shopkeeper tab functionality
function showShopkeeperTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.shopkeeper-tab-content');
    tabContents.forEach(content => content.classList.remove('active'));
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => button.classList.remove('active'));
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// Load health statistics
async function loadHealthStats() {
    try {
        const response = await fetch('/api/health-stats');
        const data = await response.json();
        
        document.getElementById('totalProducts').textContent = data.total_products?.toLocaleString() || '-';
        document.getElementById('deadStock').textContent = data.dead_stock?.toLocaleString() || '-';
        document.getElementById('atRisk').textContent = data.at_risk?.toLocaleString() || '-';
        document.getElementById('healthy').textContent = data.healthy?.toLocaleString() || '-';
        document.getElementById('rescuePotential').textContent = data.rescue_potential ? 
            `₹${(data.rescue_potential / 100000).toFixed(1)}L` : '-';
    } catch (error) {
        console.error('Error loading health stats:', error);
    }
}

// Load regional festivals based on location
async function loadRegionalFestivals() {
    try {
        const location = document.getElementById('locationSelect').value;
        const sortBy = document.getElementById('festivalSortBy')?.value || 'days_until';
        
        if (!location) {
            document.getElementById('regionalFestivalsList').innerHTML = 
                '<p class="no-data">Please select a location to view regional festivals.</p>';
            return;
        }
        
        const url = `/api/all-festivals?location=${location}&sort_by=${sortBy}`;
        const response = await fetch(url);
        const festivals = await response.json();
        
        displayRegionalFestivals(festivals);
    } catch (error) {
        console.error('Error loading regional festivals:', error);
    }
}

// Display regional festivals
function displayRegionalFestivals(festivals) {
    const container = document.getElementById('regionalFestivalsList');
    
    container.innerHTML = '';
    
    if (!festivals || festivals.length === 0) {
        container.innerHTML = '<p class="no-data">No festivals found for this location. Please select a different location or check back later.</p>';
        return;
    }
    
    // Filter to show festivals within 7 months (210 days) and prioritize regional ones
    const filteredFestivals = festivals.filter(festival => 
        festival.days_until <= 210 && 
        festival.days_until >= 0
    );
    
    // Sort: regional festivals first, then by days until
    const sortedFestivals = filteredFestivals.sort((a, b) => {
        if (a.is_regional && !b.is_regional) return -1;
        if (!a.is_regional && b.is_regional) return 1;
        return a.days_until - b.days_until;
    });
    
    if (sortedFestivals.length === 0) {
        container.innerHTML = '<p class="no-data">No festivals found for this location within the next 7 months. Please select a different location or check back later.</p>';
        return;
    }
    
    sortedFestivals.forEach(festival => {
        const festivalCard = document.createElement('div');
        festivalCard.className = 'festival-card';
        // Add data-category for filtering
        festivalCard.setAttribute('data-category', (festival.category || '').toLowerCase().replace(/\s+/g, '_'));
        
        const daysUntil = festival.days_until;
        const urgencyClass = getUrgencyClass(daysUntil);
        
        // Determine badge type
        let badgeHtml = '';
        if (festival.regions && festival.regions.includes('all_india')) {
            badgeHtml = '<span class="regional-badge national"><i class="fas fa-flag"></i> National</span>';
        } else if (festival.is_regional) {
            badgeHtml = '<span class="regional-badge"><i class="fas fa-map-marker-alt"></i> Regional</span>';
        }
        
        festivalCard.innerHTML = `
            <div class="festival-header ${urgencyClass}">
                <h4>${festival.name}</h4>
                <span class="festival-date">${formatDate(festival.date)}</span>
                ${badgeHtml}
            </div>
            <div class="festival-body">
                <p class="festival-description">${festival.description || 'Festival'}</p>
                <div class="festival-meta">
                    <span class="days-until">${daysUntil === 'N/A' ? 'Date TBD' : `${daysUntil} days away`}</span>
                    <span class="festival-category">${festival.category || 'Cultural'}</span>
                </div>
                <div class="shopping-period">
                    <i class="fas fa-shopping-cart"></i>
                    Shopping period: ${festival.shopping_period || 15} days
                </div>
                <div class="festival-actions">
                    <button onclick="showFestivalInsights('${festival.key}')" class="btn-insights">
                        <i class="fas fa-lightbulb"></i> Insights
                    </button>
                </div>
            </div>
        `;
        
        container.appendChild(festivalCard);
    });
    // Apply filter after rendering
    filterFestivals();
}



// Handle product analysis
async function handleProductAnalysis(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const productData = {
        name: formData.get('name'),
        category: formData.get('category'),
        price: parseFloat(formData.get('price')),
        stock_quantity: parseInt(formData.get('stock_quantity')),
        days_in_stock: parseInt(formData.get('days_in_stock')),
        sales_velocity: parseFloat(formData.get('sales_velocity'))
    };
    
    try {
        const response = await fetch('/api/analyze-product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayResults(result);
        } else {
            alert('Error: ' + (result.error || 'Failed to analyze product'));
        }
    } catch (error) {
        console.error('Error analyzing product:', error);
        alert('Error analyzing product. Please try again.');
    }
}

// Display analysis results
function displayResults(result) {
    document.getElementById('resultsSection').style.display = 'block';
    
    // Display health metrics
    const healthScore = Math.round(result.health_score * 100);
    document.getElementById('healthScoreDisplay').textContent = `${healthScore}%`;
    document.getElementById('healthStatusDisplay').textContent = result.discount_recommendations.health_status || result.health_status;
    document.getElementById('stockAgeDisplay').textContent = `${result.product.days_in_stock} days`;
    document.getElementById('stockQuantityDisplay').textContent = `${result.product.stock_quantity} units`;
    document.getElementById('salesVelocityDisplay').textContent = `${result.product.sales_velocity} units/day`;
    
    // Display discount calculator
    const originalPrice = result.product.price;
    const discountPercentage = result.discount_recommendations.recommended_discount;
    const discountedPrice = result.discount_recommendations.new_price;
    const savings = result.discount_recommendations.price_reduction;
    const expectedRevenue = result.discount_recommendations.expected_revenue;
    const riskScore = result.discount_recommendations.risk_score;
    
    document.getElementById('originalPrice').textContent = `₹${originalPrice.toLocaleString()}`;
    document.getElementById('recommendedDiscount').textContent = `${discountPercentage}%`;
    document.getElementById('discountedPrice').textContent = `₹${discountedPrice.toLocaleString()}`;
    document.getElementById('totalSavings').textContent = `₹${savings.toLocaleString()}`;
    document.getElementById('expectedRevenue').textContent = `₹${expectedRevenue.toLocaleString()}`;
    document.getElementById('riskScoreDisplay').textContent = `${riskScore}`;
    
    // Display discount strategy
    const reasoning = result.discount_recommendations.reasoning || [];
    const strategyText = reasoning.length > 0 ? reasoning.join('. ') : 
        `Based on your product's ${healthScore}% health score and ${riskScore} risk score, a ${discountPercentage}% discount is recommended to move inventory quickly while maintaining profitability.`;
    document.getElementById('discountStrategy').textContent = strategyText;
    
    // Display sales recommendations
    displaySalesRecommendations(result);
    
    // Display festival recommendations
    displayFestivalRecommendations(result.festival_recommendations);
    
    // Display product-specific festival opportunities
    displayProductFestivalOpportunities(result.product_festival_opportunities);
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

// Display sales recommendations
function displaySalesRecommendations(result) {
    const healthScore = Math.round(result.health_score * 100);
    const category = result.product.category;
    const price = result.product.price;
    
    // Target Audience
    let targetAudience = "General customers interested in quality products";
    if (healthScore < 30) {
        targetAudience = "Budget-conscious customers looking for great deals";
    } else if (healthScore < 60) {
        targetAudience = "Value-seeking customers who appreciate quality at reasonable prices";
    } else {
        targetAudience = "Quality-focused customers who value premium products";
    }
    
    // Pricing Strategy
    let pricingStrategy = "Maintain current pricing with occasional promotions";
    if (healthScore < 30) {
        pricingStrategy = "Apply aggressive discounts (40-60%) to clear inventory quickly";
    } else if (healthScore < 60) {
        pricingStrategy = "Use moderate discounts (20-40%) with bundle offers";
    } else {
        pricingStrategy = "Premium pricing with seasonal promotions and loyalty rewards";
    }
    
    // Marketing Approach
    let marketingApproach = "Focus on product benefits and quality";
    if (healthScore < 30) {
        marketingApproach = "Emphasize massive savings and limited-time offers";
    } else if (healthScore < 60) {
        marketingApproach = "Highlight value for money and bundle deals";
    } else {
        marketingApproach = "Showcase premium features and exclusive benefits";
    }
    
    // Timeline
    let timeline = "Expect steady sales over 2-3 months";
    if (healthScore < 30) {
        timeline = "Clear inventory within 2-4 weeks with aggressive pricing";
    } else if (healthScore < 60) {
        timeline = "Move stock in 1-2 months with strategic promotions";
    } else {
        timeline = "Steady sales over 3-6 months with premium positioning";
    }
    
    document.getElementById('targetAudience').textContent = targetAudience;
    document.getElementById('pricingStrategy').textContent = pricingStrategy;
    document.getElementById('marketingApproach').textContent = marketingApproach;
    document.getElementById('salesTimeline').textContent = timeline;
}

// Display festival recommendations
function displayFestivalRecommendations(festivalData) {
    const container = document.getElementById('festivalRecommendations');
    container.innerHTML = '';
    
    if (!festivalData || !festivalData.recommended_festivals) {
        container.innerHTML = '<p class="no-data">No festival opportunities found.</p>';
        return;
    }
    
    festivalData.recommended_festivals.forEach(festival => {
        const festivalItem = document.createElement('div');
        festivalItem.className = 'recommendation-item festival';
        festivalItem.innerHTML = `
            <div class="recommendation-header">
                <h4>${festival.name}</h4>
                <span class="relevance-score">${Math.round(festival.relevance_score * 100)}% relevant</span>
            </div>
            <p>${festival.description || 'Great opportunity for this product category'}</p>
            <div class="festival-details">
                <span class="date">${formatDate(festival.date)}</span>
                <span class="shopping-period">${festival.shopping_period} days shopping period</span>
            </div>
        `;
        container.appendChild(festivalItem);
    });
}

// Display product-specific festival opportunities
function displayProductFestivalOpportunities(opportunitiesData) {
    const container = document.getElementById('festivalRecommendations');
    
    if (!opportunitiesData || !opportunitiesData.opportunities || opportunitiesData.opportunities.length === 0) {
        if (container.innerHTML === '') {
            container.innerHTML = '<p class="no-data">No product-specific festival opportunities found.</p>';
        }
        return;
    }
    
    // Clear existing content
    container.innerHTML = '';
    
    // Add header
    const header = document.createElement('div');
    header.className = 'opportunities-header';
    header.innerHTML = `
        <h4><i class="fas fa-calendar-check"></i> Best Festivals to Sell "${opportunitiesData.product_name}"</h4>
        <p>${opportunitiesData.total_opportunities} opportunities found for your product</p>
    `;
    container.appendChild(header);
    
    // Display opportunities
    opportunitiesData.opportunities.forEach(opportunity => {
        const opportunityItem = document.createElement('div');
        opportunityItem.className = 'recommendation-item festival';
        
        opportunityItem.innerHTML = `
            <div class="recommendation-header">
                <h4>${opportunity.festival_name}</h4>
            </div>
                        <div class="opportunity-details">
                <p class="promotion-reason"><strong>Why/How to Promote:</strong> ${opportunity.promotion_reason}</p>
                <div class="festival-meta">
                    <span class="date"><i class="fas fa-calendar"></i> ${formatDate(opportunity.date)}</span>
                    <span class="days-until"><i class="fas fa-clock"></i> ${opportunity.days_until} days away</span>
                    ${opportunity.is_regional ? '<span class="regional-badge"><i class="fas fa-map-marker-alt"></i> Regional</span>' : ''}
                </div>
                ${opportunity.trending_keywords.length > 0 ? `
                    <div class="trending-keywords">
                        <strong>Trending Keywords:</strong>
                        ${opportunity.trending_keywords.map(keyword => `<span class="keyword">${keyword}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        container.appendChild(opportunityItem);
    });
    
    // Add summary
    if (opportunitiesData.regional_opportunities.length > 0) {
        const summary = document.createElement('div');
        summary.className = 'opportunities-summary';
        summary.innerHTML = `
            <p><strong>Regional Opportunities:</strong> ${opportunitiesData.regional_opportunities.length} festivals specific to your location</p>
            <p><strong>National Opportunities:</strong> ${opportunitiesData.national_opportunities.length} festivals across India</p>
        `;
        container.appendChild(summary);
    }
}

// Display discount recommendations
function displayDiscountRecommendations(discountData) {
    const container = document.getElementById('discountRecommendations');
    container.innerHTML = '';
    
    if (!discountData) {
        container.innerHTML = '<p class="no-data">No discount recommendations available.</p>';
        return;
    }
    
    const discountItem = document.createElement('div');
    discountItem.className = 'recommendation-item discount';
    discountItem.innerHTML = `
        <div class="recommendation-header">
            <h4>Smart Discount Strategy</h4>
            <span class="discount-percentage">${Math.round(discountData.recommended_discount * 100)}%</span>
        </div>
        <p>${discountData.strategy || 'Optimized discount based on product health and market conditions'}</p>
        <div class="discount-details">
            <span class="original-price">Original: ₹${discountData.original_price?.toLocaleString()}</span>
            <span class="discounted-price">Discounted: ₹${discountData.discounted_price?.toLocaleString()}</span>
            <span class="savings">Savings: ₹${discountData.savings?.toLocaleString()}</span>
        </div>
    `;
    container.appendChild(discountItem);
}

// Display bundle recommendations
function displayBundleRecommendations(bundleData) {
    const container = document.getElementById('bundleRecommendations');
    container.innerHTML = '';
    
    if (!bundleData || !bundleData.recommendations || bundleData.recommendations.length === 0) {
        container.innerHTML = '<p class="no-data">No bundle opportunities found.</p>';
        return;
    }
    
    bundleData.recommendations.forEach(bundle => {
        const bundleItem = document.createElement('div');
        bundleItem.className = 'recommendation-item bundle';
        bundleItem.innerHTML = `
            <div class="recommendation-header">
                <h4>${bundle.bundle_type === 'festival' ? bundle.festival : bundle.season} Bundle</h4>
                <span class="bundle-score">${Math.round(bundleData.bundle_score)}% bundle score</span>
            </div>
            <div class="bundle-options">
                <div class="same-shop-bundles">
                    <h5>Same Shop Bundles:</h5>
                    ${bundle.same_shop_bundles.map(item => `
                        <div class="bundle-option">
                            <span class="product">${item.product.replace('_', ' ')}</span>
                            <span class="discount">${Math.round(item.discount * 100)}% off</span>
                        </div>
                    `).join('')}
                </div>
                <div class="cross-shop-bundles">
                    <h5>Cross-Shop Bundles:</h5>
                    ${bundle.cross_shop_bundles.map(item => `
                        <div class="bundle-option">
                            <span class="product">${item.product.replace('_', ' ')}</span>
                            <span class="discount">${Math.round(item.discount * 100)}% off</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        container.appendChild(bundleItem);
    });
}

// Handle bundle creation
async function handleBundleCreation(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const comboProducts = formData.get('combo_products').split(',').map(p => p.trim());
    const location = formData.get('location');
    
    const bundleData = {
        primary_product: {
            name: formData.get('primary_product'),
            price: parseFloat(formData.get('primary_price')),
            category: 'clothing' // Default category
        },
        combo_products: comboProducts.map(product => ({
            name: product,
            price: Math.random() * 1000 + 100, // Random price for demo
            category: 'accessories' // Default category
        })),

        location: location
    };
    
    try {
        // First, get seller recommendations
        const sellerResponse = await fetch('/api/seller-recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                primary_product: bundleData.primary_product,
                combo_products: bundleData.combo_products,
                location: location
            })
        });
        
        if (sellerResponse.ok) {
            const sellerData = await sellerResponse.json();
            displaySellerRecommendations(sellerData);
        }
        
        // Then create the bundle
        const response = await fetch('/api/create-bundle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bundleData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayBundleResult(result);
        } else {
            alert('Error: ' + (result.error || 'Failed to create bundle'));
        }
    } catch (error) {
        console.error('Error creating bundle:', error);
        alert('Error creating bundle. Please try again.');
    }
}

// Display bundle creation result
function displayBundleResult(bundle) {
    document.getElementById('bundleResults').style.display = 'block';
    
    const container = document.getElementById('bundleDetails');
    container.innerHTML = `
        <div class="bundle-summary">
            <div class="primary-product">
                <h4>Primary Product</h4>
                <p>${bundle.primary_product.name} - ₹${bundle.primary_product.price.toLocaleString()}</p>
            </div>
            <div class="combo-products">
                <h4>Combo Products</h4>
                ${bundle.combo_products.map(product => `
                    <p>${product.name} - ₹${product.price.toLocaleString()}</p>
                `).join('')}
            </div>
            <div class="pricing">
                <h4>Bundle Pricing</h4>
                <p><strong>Original Total:</strong> ₹${bundle.pricing.original_total.toLocaleString()}</p>
                <p><strong>Discounted Total:</strong> ₹${bundle.pricing.discounted_total.toLocaleString()}</p>
                <p><strong>Savings:</strong> ₹${bundle.pricing.savings.toLocaleString()} (${bundle.pricing.discount_percentage}% off)</p>
            </div>
            <div class="bundle-id">
                <p><strong>Bundle ID:</strong> ${bundle.bundle_id}</p>
            </div>
        </div>
    `;
    
    // Scroll to bundle results
    document.getElementById('bundleResults').scrollIntoView({ behavior: 'smooth' });
}

// Display seller recommendations
function displaySellerRecommendations(data) {
    const container = document.getElementById('sellerRecommendations');
    const content = document.getElementById('sellerRecommendationsContent');
    
    container.style.display = 'block';
    content.innerHTML = '';
    
    // Add message
    const messageDiv = document.createElement('div');
    messageDiv.className = 'seller-message';
    messageDiv.innerHTML = `
        <i class="fas fa-lightbulb"></i>
        <strong>${data.message}</strong>
        <br>
        <small>Did you know these local sellers offer trending products? Consider reaching out to bundle together or cross-promote!</small>
    `;
    content.appendChild(messageDiv);
    
    // Add seller cards
    if (data.collaboration_suggestions && data.collaboration_suggestions.length > 0) {
        data.collaboration_suggestions.forEach(seller => {
            const sellerCard = document.createElement('div');
            sellerCard.className = 'seller-card';
            sellerCard.innerHTML = `
                <div class="seller-header">
                    <div class="seller-name">${seller.seller_name}</div>
                    <div class="seller-rating">⭐ ${seller.rating}</div>
                </div>
                <div class="seller-category">${seller.category}</div>
                <div class="seller-specialties">
                    <strong>Specialties:</strong> ${seller.specialties.join(', ')}
                </div>
                <div class="seller-contact">
                    <i class="fas fa-phone"></i>
                    ${seller.contact}
                </div>
                <div class="seller-benefits">
                    <h5>Collaboration Benefits:</h5>
                    <ul class="benefits-list">
                        ${seller.benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                    </ul>
                </div>
                <div class="collaboration-actions">
                    <a href="tel:${seller.contact}" class="collab-btn primary">
                        <i class="fas fa-phone"></i> Call Now
                    </a>
                    <a href="https://wa.me/${seller.contact.replace(/[^0-9]/g, '')}" class="collab-btn" target="_blank">
                        <i class="fab fa-whatsapp"></i> WhatsApp
                    </a>
                    <button class="collab-btn" onclick="sendCollaborationMessage('${seller.seller_name}', '${seller.category}')">
                        <i class="fas fa-envelope"></i> Send Message
                    </button>
                </div>
            `;
            content.appendChild(sellerCard);
        });
    } else {
        content.innerHTML += '<p style="text-align: center; opacity: 0.8;">No seller recommendations available for this location.</p>';
    }
    
    // Scroll to recommendations
    container.scrollIntoView({ behavior: 'smooth' });
}

// Send collaboration message (placeholder function)
function sendCollaborationMessage(sellerName, category) {
    const message = `Hi! I'm interested in collaborating with ${sellerName} for ${category} products. Let's discuss bundle opportunities!`;
    
    // For demo purposes, show an alert. In a real app, this would open a messaging interface
    alert(`Message to ${sellerName}:\n\n${message}\n\n(In a real app, this would open a messaging interface)`);
}

// Change location and reload data
function changeLocation() {
    const location = document.getElementById('locationSelect').value;
    currentLocation = location || 'mumbai';
    
    loadRegionalFestivals();
    loadFestivalCategories();
}

// Update gauge visualization
function updateGauge(gaugeId, fillId, textId, percentage) {
    const gauge = document.getElementById(gaugeId);
    const fill = document.getElementById(fillId);
    const text = document.getElementById(textId);
    
    // Update fill
    fill.style.transform = `rotate(${percentage * 1.8}deg)`;
    
    // Update text
    text.textContent = `${Math.round(percentage)}%`;
    
    // Update color based on percentage
    if (percentage >= 70) {
        gauge.className = 'gauge healthy';
    } else if (percentage >= 40) {
        gauge.className = 'gauge at-risk';
    } else {
        gauge.className = 'gauge dead';
    }
}

// Enhanced calculateDaysUntil function with better error handling
function calculateDaysUntil(dateString) {
    if (!dateString || dateString === 'Invalid Date' || dateString === 'NaN') {
        return 'N/A';
    }
    
    const targetDate = new Date(dateString);
    const today = new Date();
    
    // Check if date is valid
    if (isNaN(targetDate.getTime())) {
        return 'N/A';
    }
    
    // Reset time to start of day for accurate calculation
    today.setHours(0, 0, 0, 0);
    targetDate.setHours(0, 0, 0, 0);
    
    const diffTime = targetDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    // If festival has passed this year, calculate for next year
    if (diffDays < 0) {
        const nextYear = targetDate.getFullYear() + 1;
        const nextYearDate = new Date(dateString);
        nextYearDate.setFullYear(nextYear);
        const nextYearDiff = nextYearDate - today;
        const nextYearDays = Math.ceil(nextYearDiff / (1000 * 60 * 60 * 24));
        return nextYearDays >= 0 ? nextYearDays : 'N/A';
    }
    
    return diffDays;
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
} 



// Load festival categories
async function loadFestivalCategories() {
    try {
        const location = document.getElementById('locationSelect').value;
        const url = `/api/festival-categories?location=${location}`;
        
        const response = await fetch(url);
        const categories = await response.json();
        
        displayFestivalCategories(categories);
    } catch (error) {
        console.error('Error loading festival categories:', error);
    }
}

// Display festival categories
function displayFestivalCategories(categories) {
    const container = document.getElementById('festivalCategories');
    container.innerHTML = '';
    
    if (!categories || categories.length === 0) {
        container.innerHTML = '<p class="no-data">No categories found.</p>';
        return;
    }
    
    categories.forEach(category => {
        const categoryCard = document.createElement('div');
        categoryCard.className = 'category-card';
        categoryCard.onclick = () => showCategoryFestivals(category);
        
        const urgentFestivals = category.festivals.filter(f => f.urgency_level === 'urgent' || f.urgency_level === 'critical');
        
        categoryCard.innerHTML = `
            <h4>${category.name}</h4>
            <div class="category-count">${category.count}</div>
            <div class="category-festivals">
                ${urgentFestivals.length > 0 ? 
                    `<strong>${urgentFestivals.length} urgent</strong><br>` : ''}
                ${category.festivals.slice(0, 3).map(f => f.name).join(', ')}
                ${category.festivals.length > 3 ? '...' : ''}
            </div>
        `;
        
        container.appendChild(categoryCard);
    });
}

// Show all festivals in a specific category
async function showCategoryFestivals(category) {
    try {
        const location = document.getElementById('locationSelect').value;
        const url = `/api/all-festivals?location=${location}&sort_by=days_until`;
        
        const response = await fetch(url);
        const allFestivals = await response.json();
        
        // Filter festivals by category (these are already regional due to backend filtering)
        const categoryFestivals = allFestivals.filter(festival => 
            festival.category.toLowerCase() === category.name.toLowerCase().replace(' ', '_')
        );
        
        // Create a modal or expand the festivals list to show category festivals
        displayCategoryFestivalsModal(category, categoryFestivals);
        
    } catch (error) {
        console.error('Error loading category festivals:', error);
    }
}

// Display category festivals in a modal-like view
function displayCategoryFestivalsModal(category, festivals) {
    // Create modal container
    let modal = document.getElementById('categoryFestivalsModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'categoryFestivalsModal';
        modal.className = 'category-modal';
        document.body.appendChild(modal);
        
        // Add click outside to close functionality
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeCategoryModal();
            }
        });
        
        // Add keyboard event listener for Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display === 'flex') {
                closeCategoryModal();
            }
        });
    }
    
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>${category.name} Festivals (${festivals.length})</h3>
                <button class="close-btn" onclick="closeCategoryModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="category-festivals-grid">
                    ${festivals.map(festival => `
                        <div class="festival-card-comprehensive ${festival.is_regional ? 'regional' : ''} ${festival.urgency_level}" onclick="showFestivalInsights('${festival.key}')">
                            <div class="festival-header-comprehensive">
                                <div>
                                    <div class="festival-name-comprehensive">${festival.name}</div>
                                    <div class="festival-date-comprehensive">${formatDate(festival.date)}</div>
                                </div>
                                <div class="festival-days-comprehensive ${getUrgencyClass(festival.days_until)}">
                                    ${festival.days_until === 'N/A' ? 'TBD' : `${festival.days_until} days`}
                                </div>
                            </div>
                            <div class="festival-description-comprehensive">${festival.description}</div>
                            <div class="festival-meta-comprehensive">
                                <span class="festival-category-badge">${festival.category}</span>
                                <span>${festival.duration} day${festival.duration > 1 ? 's' : ''}</span>
                            </div>
                            <div class="festival-trending-keywords">
                                ${festival.trending_keywords.slice(0, 3).map(keyword => 
                                    `<span class="trending-keyword">${keyword}</span>`
                                ).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    modal.style.display = 'flex';
    
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
}

// Close category modal
function closeCategoryModal() {
    const modal = document.getElementById('categoryFestivalsModal');
    if (modal) {
        modal.style.display = 'none';
        // Restore body scroll
        document.body.style.overflow = 'auto';
    }
}

// Get urgency class for days until
function getUrgencyClass(daysUntil) {
    if (daysUntil === 'N/A' || daysUntil === null || daysUntil === undefined) return '';
    if (daysUntil <= 7) return 'critical';
    if (daysUntil <= 30) return 'urgent';
    return '';
}

// Show festival insights
async function showFestivalInsights(festivalKey) {
    try {
        const location = document.getElementById('locationSelect').value;
        const url = `/api/festival/${festivalKey}/insights?location=${location}`;
        
        const response = await fetch(url);
        const insights = await response.json();
        
        displayFestivalInsights(insights);
        
        // Show insights panel
        document.getElementById('festivalInsightsPanel').style.display = 'block';
        document.getElementById('festivalInsightsPanel').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Error loading festival insights:', error);
    }
}

// Display festival insights
function displayFestivalInsights(insights) {
    const container = document.getElementById('festivalInsights');
    
    container.innerHTML = `
        <div class="insights-content">
            <div class="insight-section">
                <h4>Festival Information</h4>
                <ul class="insight-list">
                    <li><strong>Name:</strong> ${insights.festival_info.name}</li>
                    <li><strong>Category:</strong> ${insights.festival_info.category}</li>
                    <li><strong>Duration:</strong> ${insights.festival_info.duration} days</li>
                    <li><strong>Shopping Period:</strong> ${insights.festival_info.shopping_period} days</li>
                    <li><strong>Days Until:</strong> ${insights.days_until || 'TBD'}</li>
                    <li><strong>Urgency Level:</strong> ${insights.urgency_level}</li>
                </ul>
            </div>
            
            <div class="insight-section">
                <h4>Marketing Opportunities</h4>
                <ul class="insight-list">
                    ${insights.marketing_opportunities.map(opportunity => 
                        `<li>${opportunity}</li>`
                    ).join('')}
                </ul>
            </div>
            
            <div class="insight-section">
                <h4>Inventory Recommendations</h4>
                <ul class="insight-list">
                    ${insights.inventory_recommendations.map(recommendation => 
                        `<li>${recommendation}</li>`
                    ).join('')}
                </ul>
            </div>
            
            <div class="insight-section">
                <h4>Trending Data</h4>
                <div class="trending-data-item">
                    <h4>Trending Products</h4>
                    <div class="trending-products-list">
                        ${insights.trending_data.trending_products.map(product => 
                            `<span class="trending-product">${product}</span>`
                        ).join('')}
                    </div>
                </div>
                <div class="trending-data-item">
                    <h4>Promotion Suggestions</h4>
                    <ul class="insight-list">
                        ${insights.trending_data.promotion_suggestions.map(suggestion => 
                            `<li>${suggestion}</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>
        </div>
    `;
}

// Filter festivals by category
function filterFestivals() {
    const filterValue = document.getElementById('festivalFilter').value;
    // Main dashboard cards
    const festivalCards = document.querySelectorAll('.festival-card');
    festivalCards.forEach(card => {
        const category = card.getAttribute('data-category') || '';
        if (filterValue === 'all' || category.includes(filterValue)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
    // Modal cards (if modal is open)
    const modalCards = document.querySelectorAll('.festival-card-comprehensive');
    modalCards.forEach(card => {
        const categoryBadge = card.querySelector('.festival-category-badge');
        const category = categoryBadge ? categoryBadge.textContent.toLowerCase() : '';
        if (filterValue === 'all' || category.includes(filterValue)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Filter by specific category
function filterByCategory(category) {
    document.getElementById('festivalFilter').value = category;
    filterFestivals();
}

// ===== SHOPKEEPER DASHBOARD FUNCTIONS =====

// Load shopkeeper statistics
async function loadShopkeeperStats() {
    try {
        const userData = localStorage.getItem('shopkeeper_user');
        console.log('Loading shopkeeper stats, userData:', userData);
        
        if (!userData) {
            console.log('No user data found for shopkeeper stats');
            return;
        }
        
        const user = JSON.parse(userData);
        console.log('Loading stats for user:', user.user_id);
        
        if (!user.user_id) {
            console.error('Invalid user ID in user data:', user);
            return;
        }
        
        const response = await fetch(`/api/shopkeeper-stats/${user.user_id}`);
        const stats = await response.json();
        
        const totalProductsEl = document.getElementById('shopkeeperTotalProducts');
        const totalSalesValueEl = document.getElementById('shopkeeperTotalSalesValue');
        const totalItemsSoldEl = document.getElementById('shopkeeperTotalItemsSold');
        const currentInventoryEl = document.getElementById('shopkeeperCurrentInventory');
        
        if (totalProductsEl) totalProductsEl.textContent = stats.total_products || 0;
        if (totalSalesValueEl) totalSalesValueEl.textContent = `₹${(stats.total_sales_value || 0).toLocaleString()}`;
        if (totalItemsSoldEl) totalItemsSoldEl.textContent = stats.total_items_sold || 0;
        if (currentInventoryEl) currentInventoryEl.textContent = stats.current_inventory || 0;
        
    } catch (error) {
        console.error('Error loading shopkeeper stats:', error);
    }
}

// Load shopkeeper products
async function loadProducts() {
    try {
        const userData = localStorage.getItem('shopkeeper_user');
        console.log('Loading products, userData:', userData);
        
        if (!userData) {
            console.log('No user data found for products');
            return;
        }
        
        const user = JSON.parse(userData);
        console.log('Loading products for user:', user.user_id);
        
        if (!user.user_id) {
            console.error('Invalid user ID in user data:', user);
            return;
        }
        
        const response = await fetch(`/api/shopkeeper-products/${user.user_id}`);
        const products = await response.json();
        
        displayProducts(products);
        
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// Display products
function displayProducts(products) {
    const container = document.getElementById('productsList');
    
    if (!products || products.length === 0) {
        container.innerHTML = '<div class="no-data">No products found. Add your first product to get started!</div>';
        return;
    }
    
    container.innerHTML = `
        <div class="products-table">
            <table>
                <thead>
                    <tr>
                        <th>SKU</th>
                        <th>Product Name</th>
                        <th>Category</th>
                        <th>Current Quantity</th>
                        <th>Date Added</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${products.map(product => `
                        <tr>
                            <td>${product.sku}</td>
                            <td>${product.product_name}</td>
                            <td>${product.category}</td>
                            <td>${product.current_quantity}</td>
                            <td>${product.date_added ? new Date(product.date_added).toLocaleDateString() : 'N/A'}</td>
                            <td>
                                <button onclick="recordEventForProduct('${product.sku}')" class="btn-small">
                                    <i class="fas fa-edit"></i> Record Event
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Record event for specific product
function recordEventForProduct(sku) {
    document.getElementById('eventSku').value = sku;
    showShopkeeperTab('record-event');
}

// Load shopkeeper history
async function loadHistory() {
    try {
        const userData = localStorage.getItem('shopkeeper_user');
        console.log('Loading history, userData:', userData);
        
        if (!userData) {
            console.log('No user data found for history');
            return;
        }
        
        const user = JSON.parse(userData);
        console.log('Loading history for user:', user.user_id);
        
        if (!user.user_id) {
            console.error('Invalid user ID in user data:', user);
            return;
        }
        
        // Get filter values
        const skuFilter = document.getElementById('filterSku')?.value || '';
        const startDate = document.getElementById('startDate')?.value || '';
        const endDate = document.getElementById('endDate')?.value || '';
        
        let url = `/api/product-history/${user.user_id}`;
        const params = new URLSearchParams();
        
        if (skuFilter) params.append('sku', skuFilter);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        const history = await response.json();
        
        displayHistory(history);
        
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Display history
function displayHistory(history) {
    const container = document.getElementById('historyList');
    
    if (!history || history.length === 0) {
        container.innerHTML = '<div class="no-data">No history found for the selected filters.</div>';
        return;
    }
    
    container.innerHTML = `
        <div class="history-table">
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>SKU</th>
                        <th>Event Type</th>
                        <th>Quantity Changed</th>
                        <th>Price per Unit</th>
                        <th>Total Value</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    ${history.map(event => `
                        <tr>
                            <td>${new Date(event.event_date).toLocaleDateString()}</td>
                            <td>${event.sku}</td>
                            <td><span class="event-type ${event.event_type}">${event.event_type}</span></td>
                            <td>${event.quantity_changed > 0 ? '+' : ''}${event.quantity_changed}</td>
                            <td>₹${event.price_per_unit || 0}</td>
                            <td>₹${Math.abs(event.quantity_changed * (event.price_per_unit || 0)).toLocaleString()}</td>
                            <td>${event.notes || '-'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Export history to CSV
async function exportHistory() {
    try {
        const userData = localStorage.getItem('shopkeeper_user');
        if (!userData) return;
        
        const user = JSON.parse(userData);
        
        if (!user.user_id) {
            console.error('Invalid user ID in user data:', user);
            return;
        }
        
        // Get filter values
        const skuFilter = document.getElementById('filterSku')?.value || '';
        const startDate = document.getElementById('startDate')?.value || '';
        const endDate = document.getElementById('endDate')?.value || '';
        
        let url = `/api/export-history/${user.user_id}`;
        const params = new URLSearchParams();
        
        if (skuFilter) params.append('sku', skuFilter);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        const blob = await response.blob();
        
        // Create download link
        const url2 = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url2;
        a.download = `product_history_${user.user_id}_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url2);
        
    } catch (error) {
        console.error('Error exporting history:', error);
    }
}

// Handle add product form submission
async function handleAddProduct(event) {
    event.preventDefault();
    
    const userData = localStorage.getItem('shopkeeper_user');
    if (!userData) {
        alert('Please login first');
        return;
    }
    
    const user = JSON.parse(userData);
    if (!user.user_id) {
        alert('Invalid user data');
        return;
    }
    
    const formData = new FormData(event.target);
    const productData = {
        user_id: user.user_id,
        sku: formData.get('sku'),
        product_name: formData.get('product_name'),
        category: formData.get('category'),
        initial_quantity: parseInt(formData.get('initial_quantity'))
    };
    
    try {
        const response = await fetch('/api/add-product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Product added successfully!');
            event.target.reset();
            loadProducts();
            loadShopkeeperStats();
        } else {
            alert(result.error || 'Failed to add product');
        }
    } catch (error) {
        console.error('Error adding product:', error);
        alert('Error adding product. Please try again.');
    }
}

// Handle record event form submission
async function handleRecordEvent(event) {
    event.preventDefault();
    
    const userData = localStorage.getItem('shopkeeper_user');
    if (!userData) {
        alert('Please login first');
        return;
    }
    
    const user = JSON.parse(userData);
    if (!user.user_id) {
        alert('Invalid user data');
        return;
    }
    
    const formData = new FormData(event.target);
    const eventData = {
        user_id: user.user_id,
        sku: formData.get('sku'),
        event_type: formData.get('event_type'),
        quantity_changed: parseInt(formData.get('quantity_changed')),
        price_per_unit: formData.get('price_per_unit') ? parseFloat(formData.get('price_per_unit')) : null,
        notes: formData.get('notes')
    };
    
    try {
        const response = await fetch('/api/record-sale-event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(eventData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`${eventData.event_type} recorded successfully! New quantity: ${result.new_quantity}`);
            event.target.reset();
            loadProducts();
            loadHistory();
            loadShopkeeperStats();
        } else {
            alert(result.error || 'Failed to record event');
        }
    } catch (error) {
        console.error('Error recording event:', error);
        alert('Error recording event. Please try again.');
    }
}

// Add event listeners for shopkeeper forms
document.addEventListener('DOMContentLoaded', function() {
    // Add Product Form
    const addProductForm = document.getElementById('addProductForm');
    if (addProductForm) {
        addProductForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const productData = {
                sku: formData.get('sku'),
                product_name: formData.get('product_name'),
                category: formData.get('category'),
                initial_quantity: parseInt(formData.get('initial_quantity'))
            };
            
            try {
                const userData = localStorage.getItem('shopkeeper_user');
                if (!userData) {
                    alert('Please log in to add products.');
                    return;
                }
                
                const user = JSON.parse(userData);
                const response = await fetch(`/api/add-product/${user.user_id}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(productData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert('Product added successfully!');
                    e.target.reset();
                    loadProducts();
                    loadShopkeeperStats();
                } else {
                    alert('Error: ' + (result.error || 'Failed to add product'));
                }
            } catch (error) {
                console.error('Error adding product:', error);
                alert('Error adding product. Please try again.');
            }
        });
    }
    
    // Record Event Form
    const recordEventForm = document.getElementById('recordEventForm');
    if (recordEventForm) {
        recordEventForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const eventData = {
                sku: formData.get('sku'),
                event_type: formData.get('event_type'),
                quantity_changed: parseInt(formData.get('quantity_changed')),
                price_per_unit: parseFloat(formData.get('price_per_unit')) || 0,
                notes: formData.get('notes')
            };
            
            try {
                const userData = localStorage.getItem('shopkeeper_user');
                if (!userData) {
                    alert('Please log in to record events.');
                    return;
                }
                
                const user = JSON.parse(userData);
                const response = await fetch(`/api/record-event/${user.user_id}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(eventData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert('Event recorded successfully!');
                    e.target.reset();
                    loadProducts();
                    loadShopkeeperStats();
                    loadHistory();
                } else {
                    alert('Error: ' + (result.error || 'Failed to record event'));
                }
            } catch (error) {
                console.error('Error recording event:', error);
                alert('Error recording event. Please try again.');
            }
        });
    }
});

 
