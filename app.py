from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
import re
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io

# Load environment variables from .env file
load_dotenv()

# --- Proxy Configuration (if needed) ---
# Uncomment and configure if you are behind a proxy
os.environ['HTTP_PROXY'] = 'http://172.31.2.4:8080'
os.environ['HTTPS_PROXY'] = 'http://172.31.2.4:8080'

# --- Google Generative AI Configuration ---
api_key_status = "Found" if os.environ.get('GOOGLE_API_KEY') else "Not Found"
print(f"DEBUG: GOOGLE_API_KEY status: {api_key_status}")

if os.environ.get('GOOGLE_API_KEY'):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    try:
        print("\n--- Listing available Gemini models ---")
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(f"Model: {m.name}, Supported Methods: {m.supported_generation_methods}")
        print("--- End model list ---\n")
    except Exception as e:
        print(f"Error listing models: {e}")
else:
    print("Warning: GOOGLE_API_KEY not found. Some AI features may not work.")

# --- Import Custom Modules ---
# Ensure these files (e.g., product_health.py) are in a 'models' directory
# at the same level as your app.py, or adjust the import paths accordingly.
from models.product_health import ProductHealthAnalyzer
from models.festival_engine import FestivalPromotionEngine
from models.discount_calculator import SmartDiscountCalculator
from models.location_service import LocationService
from models.bundle_calculator import BundleCalculator
from models.product_tracker import ProductTracker

# --- Flask App Initialization ---
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-very-secret-key-default') # Use env var for secret key

# Configure app for Vercel deployment (or local 'uploads' and 'processed' folders)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads' if os.environ.get('VERCEL') else 'uploads'
app.config['PROCESSED_FOLDER'] = '/tmp/processed' if os.environ.get('VERCEL') else 'processed'
app.config['EXPORTS_FOLDER'] = '/tmp/exports' if os.environ.get('VERCEL') else 'exports' # For CSV exports

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
os.makedirs(app.config['EXPORTS_FOLDER'], exist_ok=True) # Ensure exports folder exists

# --- Initialize Models/Services ---
health_analyzer = ProductHealthAnalyzer()
discount_calculator = SmartDiscountCalculator()
festival_engine = FestivalPromotionEngine()
location_service = LocationService()
bundle_calculator = BundleCalculator()
product_tracker = ProductTracker()

# --- Demo Data Setup ---
try:
    product_tracker.register_shopkeeper(
        user_id="demo_shopkeeper_001",
        shop_name="Demo Fashion Store",
        password="demo123",
        email="demo@gmail.com",
        phone="9876543210",
        location="Mumbai"
    )
    print("Demo shopkeeper created successfully.")
    
    # Add sample products for demo user
    sample_products = [
        {"sku": "TSHIRT001", "product_name": "Cotton T-Shirt", "category": "clothing", "initial_quantity": 50},
        {"sku": "JEANS002", "product_name": "Blue Denim Jeans", "category": "clothing", "initial_quantity": 30},
        {"sku": "SHOES003", "product_name": "Sports Shoes", "category": "sports", "initial_quantity": 25},
        {"sku": "BAG004", "product_name": "Leather Handbag", "category": "clothing", "initial_quantity": 15}
    ]
    
    for product in sample_products:
        try:
            product_tracker.add_product(
                user_id="demo_shopkeeper_001",
                sku=product["sku"],
                product_name=product["product_name"],
                category=product["category"],
                initial_quantity=product["initial_quantity"]
            )
        except Exception as e:
            print(f"Product {product['sku']} already exists or error adding product: {e}")
    
    # Add sample sale events
    sample_events = [
        {"sku": "TSHIRT001", "event_type": "sale", "quantity_changed": -5, "price_per_unit": 299.99, "notes": "Weekend sale"},
        {"sku": "JEANS002", "event_type": "sale", "quantity_changed": -3, "price_per_unit": 899.99, "notes": "Online order"},
        {"sku": "SHOES003", "event_type": "sale", "quantity_changed": -2, "price_per_unit": 1299.99, "notes": "Store sale"},
        {"sku": "TSHIRT001", "event_type": "restock", "quantity_changed": 10, "price_per_unit": 200.00, "notes": "New stock arrival"},
        {"sku": "BAG004", "event_type": "sale", "quantity_changed": -1, "price_per_unit": 1499.99, "notes": "Premium customer"}
    ]
    
    for event in sample_events:
        try:
            product_tracker.record_sale_event(
                user_id="demo_shopkeeper_001",
                sku=event["sku"],
                event_type=event["event_type"],
                quantity_changed=event["quantity_changed"],
                price_per_unit=event["price_per_unit"],
                notes=event["notes"]
            )
        except Exception as e:
            print(f"Event for {event['sku']} already exists or error recording event: {e}")
            
    print("Demo data added successfully.")
    
except Exception as e:
    print(f"Demo shopkeeper already exists or error during demo setup: {e}")

# --- Frontend Routes ---
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/login')
def login_page(): # Renamed to avoid conflict with login_api
    """Login page"""
    return render_template('login.html')

@app.route('/shopkeeper')
def shopkeeper_dashboard():
    """Shopkeeper dashboard page"""
    # You might want to add a login_required decorator here in a real app
    return render_template('shopkeeper_dashboard.html')

@app.route('/photogenix')
def photogenix():
    return render_template('indexphoto.html')

@app.route('/get-in-touch')
def get_in_touch():
    return render_template('get_in_touch.html')

@app.route('/campaign-generator')
def campaign_generator():
    return render_template('campaign_generator.html')

# --- Static Files Serving ---
@app.route('/static/<path:filename>')
def static_files(filename):
    # Ensure this path matches where your static files are stored
    return send_from_directory('static', filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download exported files"""
    try:
        return send_from_directory(app.config['EXPORTS_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# --- API Endpoints ---

@app.route('/api/health-stats')
def health_stats():
    """Get overall inventory health statistics"""
    # This would typically come from a database, or aggregated from product_tracker
    stats = {
        'total_products': 1250,
        'dead_stock': 180,
        'at_risk': 320,
        'healthy': 750,
        'rescue_potential': 4200000,  # in INR
        'upcoming_opportunities': 15
    }
    return jsonify(stats)

@app.route('/api/analyze-product', methods=['POST'])
def analyze_product():
    """Analyze a single product's health and get recommendations"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract product data
        product_data = {
            'name': data.get('name', ''),
            'category': data.get('category', ''),
            'price': float(data.get('price', 0)),
            'stock_quantity': int(data.get('stock_quantity', 0)),
            'days_in_stock': int(data.get('days_in_stock', 0)),
            'sales_velocity': float(data.get('sales_velocity', 0)),
            'seasonality': data.get('seasonality', 'all_year'),
            'location': data.get('location', 'mumbai')
        }
        
        try:
            # Analyze product health
            health_score = health_analyzer.analyze_health(product_data)
        except Exception as e:
            print(f"Health analysis error: {e}")
            # Fallback health score calculation
            days_in_stock = product_data.get('days_in_stock', 0)
            if days_in_stock < 30:
                health_score = 0.8
            elif days_in_stock < 90:
                health_score = 0.6
            elif days_in_stock < 180:
                health_score = 0.4
            else:
                health_score = 0.2
        
        try:
            # Get location data
            location_data = location_service.get_location_info(product_data['location'])
        except Exception as e:
            print(f"Location service error: {e}")
            location_data = {'name': product_data['location'], 'region': 'India'}
        
        try:
            # Get festival recommendations
            festival_result = festival_engine.get_festival_recommendations(
                product_data, location_data
            )
        except Exception as e:
            print(f"Festival engine error: {e}")
            festival_result = {'upcoming_festivals': [], 'recommended_festivals': []}
        
        try:
            # Get product-specific festival opportunities
            product_opportunities = festival_engine.get_product_festival_opportunities(
                product_data['name'], product_data['location']
            )
        except Exception as e:
            print(f"Product festival opportunities error: {e}")
            product_opportunities = {'opportunities': [], 'total_opportunities': 0}
        
        try:
            # Get discount recommendations
            discount_result = discount_calculator.calculate_discount(
                product_data, health_score, festival_result
            )
        except Exception as e:
            print(f"Discount calculator error: {e}")
            # Fallback discount calculation
            price = product_data.get('price', 0)
            if health_score < 0.3:
                discount_percent = 40
            elif health_score < 0.6:
                discount_percent = 20
            else:
                discount_percent = 10
            
            discount_result = {
                'recommended_discount': discount_percent,
                'new_price': price * (1 - discount_percent / 100),
                'price_reduction': price * (discount_percent / 100),
                'expected_revenue': price * (1 - discount_percent / 100) * product_data.get('stock_quantity', 0),
                'risk_score': (1 - health_score) * 100,
                'health_status': 'At Risk' if health_score < 0.6 else 'Healthy',
                'discount_category': 'High' if discount_percent > 30 else 'Medium' if discount_percent > 15 else 'Low',
                'reasoning': [f'Based on {health_score:.1%} health score, {discount_percent}% discount recommended'],
                'sales_strategies': [] # Ensure fallback includes empty list for sales_strategies
            }
        
        try:
            # Get bundle recommendations
            recommended_festival = festival_result.get('recommended_festival')
            if isinstance(recommended_festival, list) and len(recommended_festival) > 0:
                festival_name = recommended_festival[0].get('name', None)
            elif isinstance(recommended_festival, dict):
                festival_name = recommended_festival.get('name', None)
            else:
                festival_name = None
                
            bundle_result = bundle_calculator.calculate_bundle_recommendations(
                product_data,
                location=product_data['location'],
                festival=festival_name
            )
        except Exception as e:
            print(f"Bundle calculator error: {e}")
            bundle_result = {'bundles': [], 'total_bundles': 0}
        
        try:
            # Calculate rescue score
            rescue_score = health_analyzer.calculate_rescue_score(
                product_data, festival_result, discount_result
            )
        except Exception as e:
            print(f"Rescue score error: {e}")
            rescue_score = health_score * 100
        
        # Combine results
        result = {
            'product': product_data,
            'health_score': health_score,
            'health_status': health_analyzer.get_health_status(health_score), # Use the method from the imported class
            'discount_recommendations': {
                'recommended_discount': discount_result['recommended_discount'],
                'new_price': discount_result['new_price'],
                'price_reduction': discount_result['price_reduction'],
                'expected_revenue': discount_result['expected_revenue'],
                'risk_score': discount_result['risk_score'],
                'health_status': discount_result['health_status'],
                'reasoning': discount_result['reasoning']
            },
            'sales_strategies': discount_result['sales_strategies'], # This is now at the top level
            'festival_recommendations': festival_result,
            'product_festival_opportunities': product_opportunities,
            'bundle_recommendations': bundle_result,
            'rescue_score': rescue_score,
            'location_data': location_data
        }
        
        print(f"Analysis completed successfully. Health score: {health_score}, Discount: {discount_result.get('recommended_discount', 'N/A')}%")
        return jsonify(result)
        
    except Exception as e:
        print(f"General analyze-product error: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/festivals')
def get_festivals():
    """Get all upcoming festivals"""
    location = request.args.get('location', 'mumbai').lower()
    
    # Get all upcoming festivals regardless of location
    festivals = festival_engine.get_upcoming_festivals(location)
    
    return jsonify(festivals)

@app.route('/api/locations')
def get_locations():
    """Get available locations"""
    locations = list(location_service.indian_cities.keys())
    return jsonify(locations)

@app.route('/api/shopkeepers')
def get_shopkeepers():
    """Get available shopkeepers for a location"""
    location = request.args.get('location', 'mumbai').lower()
    shopkeepers = bundle_calculator.get_available_shopkeepers(location)
    return jsonify(shopkeepers)

@app.route('/api/create-bundle', methods=['POST'])
def create_bundle_api(): # Renamed to avoid conflict with create_bundle function
    """Create a custom bundle with multiple shopkeepers"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        primary_product = data.get('primary_product', {})
        combo_products = data.get('combo_products', [])
        shopkeepers = data.get('shopkeepers', [])
        location = data.get('location', 'mumbai')
        
        if not primary_product or not combo_products:
            return jsonify({'error': 'Primary product and combo products are required'}), 400
        
        bundle = bundle_calculator.create_custom_bundle(
            primary_product, 
            combo_products, 
            shopkeepers, 
            location
        )
        
        return jsonify(bundle)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bundle-recommendations', methods=['POST'])
def get_bundle_recommendations():
    """Get bundle recommendations for a product"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        product_data = data.get('product', {})
        location = data.get('location', 'mumbai')
        festival = data.get('festival')
        shopkeeper_id = data.get('shopkeeper_id')
        
        recommendations = bundle_calculator.calculate_bundle_recommendations(
            product_data, 
            location, 
            festival, 
            shopkeeper_id
        )
        
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/all-festivals')
def get_all_festivals_api(): # Renamed to avoid conflict with get_all_festivals function
    """Get all festivals with comprehensive information"""
    try:
        location = request.args.get('location')
        sort_by = request.args.get('sort_by', 'days_until')
        
        festivals = festival_engine.get_all_festivals(location, sort_by)
        
        # Convert numpy types to native Python types
        for festival in festivals:
            if isinstance(festival.get('days_until'), (np.integer, np.floating)):
                festival['days_until'] = int(festival['days_until'])
        
        return jsonify(festivals)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/festival/<festival_key>/insights')
def get_festival_insights_api(festival_key): # Renamed to avoid conflict with get_festival_insights function
    """Get comprehensive insights for a specific festival"""
    try:
        location = request.args.get('location')
        insights = festival_engine.get_festival_insights(festival_key, location)
        
        # Convert numpy types to native Python types
        if isinstance(insights.get('days_until'), (np.integer, np.floating)):
            insights['days_until'] = int(insights['days_until'])
        
        if 'trending_data' in insights and isinstance(insights['trending_data'].get('search_volume'), (np.integer, np.floating)):
            insights['trending_data']['search_volume'] = int(insights['trending_data']['search_volume'])
        
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/festival-countdown')
def get_festival_countdown():
    """Get countdown for all upcoming festivals"""
    try:
        location = request.args.get('location', 'mumbai')
        days_ahead = int(request.args.get('days_ahead', 90))
        
        upcoming_festivals = festival_engine.get_upcoming_festivals(location, days_ahead)
        
        # Convert numpy types to native Python types
        for festival in upcoming_festivals:
            if isinstance(festival.get('days_until'), (np.integer, np.floating)):
                festival['days_until'] = int(festival['days_until'])
        
        return jsonify({
            'location': location,
            'days_ahead': days_ahead,
            'festivals': upcoming_festivals,
            'total_festivals': len(upcoming_festivals)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/festival-categories')
def get_festival_categories_api(): # Renamed to avoid conflict with get_festival_categories function
    """Get all festival categories with counts"""
    try:
        location = request.args.get('location')
        all_festivals = festival_engine.get_all_festivals(location)
        
        categories = {}
        for festival in all_festivals:
            category = festival['category']
            if category not in categories:
                categories[category] = {
                    'name': category.replace('_', ' ').title(),
                    'count': 0,
                    'festivals': []
                }
            categories[category]['count'] += 1
            categories[category]['festivals'].append({
                'name': festival['name'],
                'days_until': int(festival['days_until']) if isinstance(festival['days_until'], (np.integer, np.floating)) else festival['days_until'],
                'urgency_level': festival['urgency_level']
            })
        
        return jsonify(list(categories.values()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/product-festival-opportunities', methods=['POST'])
def get_product_festival_opportunities_api(): # Renamed to avoid conflict with get_product_festival_opportunities function
    """Get specific festival opportunities for a product"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        product_name = data.get('product_name', '')
        location = data.get('location', 'mumbai')
        
        if not product_name:
            return jsonify({'error': 'Product name is required'}), 400
        
        opportunities = festival_engine.get_product_festival_opportunities(product_name, location)
        
        return jsonify(opportunities)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/seller-recommendations', methods=['POST'])
def get_seller_recommendations_api(): # Renamed to avoid conflict with get_seller_recommendations function
    """Get local seller recommendations for bundle creation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        primary_product = data.get('primary_product', {})
        combo_products = data.get('combo_products', [])
        location = data.get('location', 'mumbai')
        
        if not primary_product:
            return jsonify({'error': 'Primary product is required'}), 400
        
        recommendations = bundle_calculator.get_local_seller_recommendations(
            primary_product, 
            combo_products, 
            location
        )
        
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Authentication API Endpoints
@app.route('/api/login', methods=['POST'])
def login_api():
    """Authenticate shopkeeper login"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        password = data.get('password')
        
        if not user_id or not password:
            return jsonify({'error': 'User ID and password are required'}), 400
        
        result = product_tracker.authenticate_shopkeeper(user_id, password)
        
        if result['success']:
            session['shopkeeper_logged_in'] = True
            return jsonify(result)
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Product Tracking API Endpoints
@app.route('/api/register-shopkeeper', methods=['POST'])
def register_shopkeeper():
    """Register a new shopkeeper"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        shop_name = data.get('shop_name')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')
        location = data.get('location')
        
        if not all([user_id, shop_name, password]):
            return jsonify({'error': 'User ID, shop name, and password are required'}), 400
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not phone:
            return jsonify({'error': 'Phone is required'}), 400
            
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        # Validate email format (must be Gmail)
        if not email.endswith('@gmail.com') or '@' not in email:
            return jsonify({'error': 'Email must be a valid Gmail address'}), 400
        
        # Validate phone format (digits only)
        if not phone.isdigit() or len(phone) < 10 or len(phone) > 15:
            return jsonify({'error': 'Phone must contain only digits (10-15 digits)'}), 400
        
        success = product_tracker.register_shopkeeper(user_id, shop_name, password, email, phone, location)
        
        if success:
            return jsonify({'success': True, 'message': 'Shopkeeper registered successfully'})
        else:
            return jsonify({'error': 'Failed to register shopkeeper'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add-product', methods=['POST'])
def add_product():
    """Add a new product to shopkeeper's inventory"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        sku = data.get('sku')
        product_name = data.get('product_name')
        category = data.get('category')
        initial_quantity = data.get('initial_quantity')
        
        if not all([user_id, sku, product_name, category, initial_quantity]):
            return jsonify({'error': 'All fields are required'}), 400
        
        result = product_tracker.add_product(user_id, sku, product_name, category, initial_quantity)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/record-sale-event', methods=['POST'])
def record_sale_event():
    """Record a sale, restock, or adjustment event"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        sku = data.get('sku')
        event_type = data.get('event_type')  # 'sale', 'restock', 'adjustment'
        quantity_changed = data.get('quantity_changed')
        price_per_unit = data.get('price_per_unit')
        notes = data.get('notes')
        
        if not all([user_id, sku, event_type, quantity_changed]):
            return jsonify({'error': 'User ID, SKU, event type, and quantity are required'}), 400
        
        result = product_tracker.record_sale_event(
            user_id, sku, event_type, quantity_changed, price_per_unit, notes
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/shopkeeper-products/<user_id>')
def get_shopkeeper_products_api(user_id): # Renamed to avoid conflict with get_shopkeeper_products function
    """Get all products for a shopkeeper"""
    try:
        products = product_tracker.get_shopkeeper_products(user_id)
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/product-history/<user_id>')
def get_product_history_api(user_id): # Renamed to avoid conflict with get_product_history function
    """Get sale/update history for products"""
    try:
        sku = request.args.get('sku')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        history = product_tracker.get_product_history(user_id, sku or None, start_date or None, end_date or None)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-history/<user_id>')
def export_history_api(user_id): # Renamed to avoid conflict with export_history function
    """Export product history to CSV"""
    try:
        sku = request.args.get('sku')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        filename = product_tracker.export_history_csv(user_id, sku or None, start_date or None, end_date or None)
        
        if filename:
            # Ensure the file is served from the correct EXPORTS_FOLDER
            return send_from_directory(app.config['EXPORTS_FOLDER'], filename, as_attachment=True)
        else:
            return jsonify({'error': 'No data to export'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/shopkeeper-stats/<user_id>')
def get_shopkeeper_stats_api(user_id): # Renamed to avoid conflict with get_shopkeeper_stats function
    """Get summary statistics for a shopkeeper"""
    try:
        stats = product_tracker.get_shopkeeper_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Photogenix Image Processing Routes ---
# Ensure u2net and cv2 (opencv-python) are installed for these routes to work
# pip install u2net_human_seg opencv-python Pillow

@app.route('/process/background_removal', methods=['POST'])
def background_removal_real():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No image uploaded'}), 400
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    try:
        img = Image.open(input_path).convert('RGBA')
        from u2net.infer import run_u2net # Import here to catch ImportError specifically
        mask = run_u2net(img)
        mask = mask.resize(img.size, Image.BILINEAR).convert('L')
        img.putalpha(mask)
        processed_filename = 'bgremoved_' + filename
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        img.save(processed_path, 'PNG')
        return jsonify({'processed_url': f'/processed/{processed_filename}'})
    except ImportError:
        return jsonify({'error': 'U2Net module not found. Please install `u2net_human_seg` to use background removal.'}), 500
    except Exception as e:
        print(f"Error during background removal: {e}")
        return jsonify({'error': f'Background removal failed: {str(e)}'}), 500

@app.route('/process/enhance', methods=['POST'])
def enhance():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No image uploaded'}), 400
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    try:
        img = Image.open(input_path).convert('RGB')
        img = ImageEnhance.Brightness(img).enhance(1.25)
        img = ImageEnhance.Contrast(img).enhance(1.35)
        img = ImageEnhance.Color(img).enhance(1.35)
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        processed_filename = 'enhanced_' + filename.rsplit('.', 1)[0] + '.png'
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        img.save(processed_path, 'PNG')
        return jsonify({'processed_url': f'/processed/{processed_filename}'})
    except Exception as e:
        print(f"Error during image enhancement: {e}")
        return jsonify({'error': f'Image enhancement failed: {str(e)}'}), 500

@app.route('/process/replace_background', methods=['POST'])
def replace_background():
    file = request.files.get('image')
    bg_name = request.form.get('background', 'white.jpg')
    if not file:
        return jsonify({'error': 'No image uploaded'}), 400
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    try:
        img = Image.open(input_path).convert('RGBA')
        from u2net.infer import run_u2net # Import here
        mask = run_u2net(img)
        mask = mask.resize(img.size, Image.BILINEAR).convert('L')
    except ImportError:
        return jsonify({'error': 'U2Net module not found. Please install `u2net_human_seg` to use background replacement.'}), 500
    except Exception as e:
        print(f"Error during background mask generation for replacement: {e}")
        return jsonify({'error': f'Background mask generation failed: {str(e)}'}), 500

    bg_path = os.path.join('static', 'backgrounds', bg_name)
    if not os.path.exists(bg_path):
        bg_path = os.path.join('static', 'backgrounds', 'white.jpg') # Fallback to white
    
    try:
        bg = Image.open(bg_path).convert('RGB').resize(img.size)
        product_rgba = img.copy()
        product_rgba.putalpha(mask)
        composite = Image.alpha_composite(bg.convert('RGBA'), product_rgba)
        
        # Add drop shadow (OpenCV)
        try:
            import cv2 # Import here
            arr = np.array(composite)
            if arr.shape[2] == 4 and np.any(arr[:,:,3]):
                shadow = cv2.GaussianBlur(arr[:,:,3], (21,21), 10)
                arr[:,:,3] = np.maximum(arr[:,:,3], shadow)
            composite = Image.fromarray(arr)
        except ImportError:
            print("Warning: OpenCV not found. Drop shadow not applied for background replacement.")
        except Exception as e:
            print(f"Error applying shadow for background replacement: {e}")

        composite = ImageEnhance.Brightness(composite).enhance(1.08)
        composite = ImageEnhance.Contrast(composite).enhance(1.12)
        composite = ImageEnhance.Color(composite).enhance(1.15)
        processed_filename = 'bgreplace_' + filename.rsplit('.', 1)[0] + '.png'
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        composite.save(processed_path, 'PNG')
        return jsonify({'processed_url': f'/processed/{processed_filename}'})
    except Exception as e:
        print(f"Error during background replacement composite: {e}")
        return jsonify({'error': f'Background replacement failed: {str(e)}'}), 500

@app.route('/process/crop_resize', methods=['POST'])
def crop_resize():
    file = request.files.get('image')
    platform = request.form.get('platform', 'meesho').lower()
    if not file:
        return jsonify({'error': 'No image uploaded'}), 400
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    try:
        img = Image.open(input_path).convert('RGB')
        sizes = {
            'meesho': (1024, 1365),
            'meesho4x4': (1000, 1000),
            'amazon': (1000, 1000),
            'instagram': (1080, 1080),
            'shopify': (2048, 2048),
            'flipkart': (2000, 2000),
        }
        size = sizes.get(platform, sizes['meesho'])
        w, h = img.size
        target_w, target_h = size
        target_ratio = target_w / target_h
        img_ratio = w / h
        if img_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            top = 0
            right = left + new_w
            bottom = h
        else:
            new_h = int(w / target_ratio)
            left = 0
            top = (h - new_h) // 2
            right = w
            bottom = top + new_h
        img_cropped = img.crop((left, top, right, bottom)).resize(size, Image.LANCZOS)
        processed_filename = f'cropped_{platform}_' + filename.rsplit('.', 1)[0] + '.png'
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        img_cropped.save(processed_path, 'PNG')
        return jsonify({'processed_url': f'/processed/{processed_filename}'})
    except Exception as e:
        print(f"Error during crop/resize: {e}")
        return jsonify({'error': f'Crop/resize failed: {str(e)}'}), 500

@app.route('/process/batch', methods=['POST'])
def batch_process():
    # Stub: Replace with real batch processing logic
    return jsonify({'status': 'Batch processing stub'})

def get_dominant_color(img):
    img = img.convert('RGB').resize((64, 64))
    arr = np.array(img)
    arr = arr.reshape((-1, 3))
    arr = arr[(arr < 250).any(axis=1)]  # Ignore near-white
    if len(arr) == 0:
        return (255, 255, 255)
    color = tuple(np.mean(arr, axis=0).astype(int))
    return color

def pick_best_background(product_img, backgrounds_dir='static/backgrounds/'):
    dominant = get_dominant_color(product_img)
    best_bg = None
    best_score = -1
    if not os.path.exists(backgrounds_dir):
        print(f"Warning: Backgrounds directory not found at {backgrounds_dir}")
        return None 

    for bg_name in os.listdir(backgrounds_dir):
        if not (bg_name.endswith('.jpg') or bg_name.endswith('.png') or bg_name.endswith('.jpeg')):
            continue
        bg_path = os.path.join(backgrounds_dir, bg_name)
        try:
            bg_img = Image.open(bg_path).resize(product_img.size)
            bg_color = get_dominant_color(bg_img)
            score = np.linalg.norm(np.array(dominant) - np.array(bg_color))
            if score > best_score:
                best_score = score
                best_bg = bg_path
        except Exception as e:
            print(f"Error processing background image {bg_name}: {e}")
            continue
    return best_bg if best_bg else os.path.join('static', 'backgrounds', 'white.jpg') # Fallback if no suitable background found

@app.route('/process/make_professional', methods=['POST'])
def make_professional():
    file = request.files.get('image')
    preset = request.form.get('preset', 'clean_studio')
    if not file:
        return jsonify({'error': 'No image uploaded'}), 400
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    try:
        img = Image.open(input_path).convert('RGBA')
        from u2net.infer import run_u2net
        mask = run_u2net(img)
        mask = mask.resize(img.size, Image.BILINEAR).convert('L')
    except ImportError:
        return jsonify({'error': 'U2Net module not found. Please install `u2net_human_seg` to use professional processing.'}), 500
    except Exception as e:
        print(f"Error during mask generation for professional processing: {e}")
        return jsonify({'error': f'Mask generation failed: {str(e)}'}), 500

    bg_path = pick_best_background(img)
    if not os.path.exists(bg_path):
        bg_path = os.path.join('static', 'backgrounds', 'white.jpg') # Fallback to white if pick_best_background fails
    
    try:
        bg = Image.open(bg_path).convert('RGB').resize(img.size)
        product_rgba = img.copy()
        product_rgba.putalpha(mask)
        composite = Image.alpha_composite(bg.convert('RGBA'), product_rgba)
        
        # Add drop shadow (OpenCV)
        try:
            import cv2
            arr = np.array(composite)
            if arr.shape[2] == 4 and np.any(arr[:,:,3]):
                shadow = cv2.GaussianBlur(arr[:,:,3], (21,21), 10)
                arr[:,:,3] = np.maximum(arr[:,:,3], shadow)
            composite = Image.fromarray(arr)
        except ImportError:
            print("Warning: OpenCV not found. Drop shadow not applied for professional processing.")
        except Exception as e:
            print(f"Error applying shadow for professional processing: {e}")

        composite = ImageEnhance.Brightness(composite).enhance(1.08)
        composite = ImageEnhance.Contrast(composite).enhance(1.12)
        composite = ImageEnhance.Color(composite).enhance(1.15)
        
        # Style presets
        if preset == 'luxury_matte':
            composite = ImageOps.colorize(composite.convert('L'), black='#222', white='#faf8ff')
        elif preset == 'minimalist_white':
            composite = ImageEnhance.Brightness(composite).enhance(1.15)
            composite = ImageEnhance.Color(composite).enhance(1.05)
        
        processed_filename = 'professional_' + filename.rsplit('.', 1)[0] + '.png'
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        composite.save(processed_path, 'PNG')
        return jsonify({'processed_url': f'/processed/{processed_filename}'})
    except Exception as e:
        print(f"Error during professional processing composite: {e}")
        return jsonify({'error': f'Professional processing failed: {str(e)}'}), 500

@app.route('/process/creative_content', methods=['POST'])
def creative_content():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No image uploaded'}), 400

    try:
        image = Image.open(file.stream).convert('RGB')
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            "Given this product image, respond ONLY with a valid JSON object with the following fields: "
            "title, description, bullets (a list of 3 bullet points), tags (a list), and caption. "
            "Do not include any explanation, markdown, or text outside the JSON. Example:\n"
            "{\n"
            '   \"title\": \"Minimalist White Sneaker for Everyday Comfort\",\n'
            '   \"description\": \"A clean, classic white sneaker...\",\n'
            '   \"bullets\": [\"Lightweight and breathable\", \"All-day comfort\", \"Sleek design\"],\n'
            '   \"tags\": [\"#WhiteSneakers\", \"#ComfortWear\"],\n'
            '   \"caption\": \"Step into style and comfort! #SneakerLove\"\n'
            "}\n"
        )
        response = model.generate_content(
            contents=[prompt, image],
            generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
        )
        
        text = response.text.strip()
        data = json.loads(text) # Directly parse as JSON
        return jsonify(data)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw Gemini response: {text}")
        return jsonify({'error': 'Could not parse Gemini response', 'raw_response': text, 'exception': str(e)}), 500
    except Exception as e:
        print(f"Error during creative content generation: {e}")
        return jsonify({'error': f'Creative content generation failed: {str(e)}'}), 500

@app.route('/api/generate_campaign_content', methods=['POST'])
def generate_campaign_content():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        festival = data.get('festival', 'a special occasion')
        region = data.get('region', 'your area')
        campaign_type = data.get('campaign_type', 'exciting offers')
        shop_name = data.get('shop_name', 'our shop')
        shop_address = data.get('shop_address', '')
        shop_phone = data.get('shop_phone', '')
        valid_till = data.get('valid_till', '')
        shop_insta = data.get('shop_insta', '')
        shop_fb = data.get('shop_fb', '')

        prompt = f"""
        You are a creative marketing assistant. Generate a festive campaign for a shop.
        The campaign should be for {shop_name} (located at {shop_address} if provided).
        It is for the {festival} festival in the {region} region.
        The campaign type is a {campaign_type}.

        Generate the following JSON structure. Ensure the output is ONLY a valid JSON object.
        No additional text, markdown backticks, or explanations outside the JSON.

        {{
            "banner_slogan": "A catchy, festive slogan for the main banner (e.g., 'Diwali Sparkle Sale!'). Include relevant emojis.",
            "main_message": "A compelling, short paragraph for the campaign message, incorporating the festival and region.",
            "offer_details": "A clear and enticing description of the offer, based on '{campaign_type}'. Be specific and highlight benefits.",
            "call_to_action": "A strong and urgent call to action (e.g., 'Shop Now!', 'Grab Yours Today!').",
            "social_media_caption": "A short, engaging caption for social media (e.g., Instagram/Facebook), including relevant hashtags and emojis. Mention the shop name if possible.",
            "additional_tips": [
                "1-2 short, actionable tips for the shopkeeper to promote this specific campaign (e.g., 'Highlight best-selling items related to the offer.')."
            ]
        }}
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            contents=[prompt],
            generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
        )
        raw_text = response.text.strip()

        campaign_data = json.loads(raw_text) # Directly parse as JSON
        return jsonify(campaign_data)

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw Gemini response: {raw_text}")
        return jsonify({'error': 'Failed to parse Gemini response', 'raw_response': raw_text, 'exception': str(e)}), 500
    except Exception as e:
        print(f"Error in generate_campaign_content: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
@app.route('/logout')
def logout():
    session.pop('shopkeeper_logged_in', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Ensure GOOGLE_API_KEY is set in your environment variables for Gemini to work
    # Example: export GOOGLE_API_KEY='your_api_key_here'
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
