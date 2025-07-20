import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

class SmartDiscountCalculator:
    """
    Smart Discount & Bundling Engine using Random Forest and Apriori algorithm
    to suggest dynamic discounts and create high-impact product bundles
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.discount_model = None
        self.bundle_model = None
        
        # Discount thresholds
        self.MIN_DISCOUNT = 5  # 5%
        self.MAX_DISCOUNT = 70  # 70%
        
        # Bundle configuration
        self.bundle_categories = {
            'clothing': ['accessories', 'footwear', 'jewelry'],
            'electronics': ['accessories', 'protection', 'storage'],
            'home_decor': ['lighting', 'furniture', 'textiles'],
            'beauty': ['skincare', 'haircare', 'tools']
        }
        
        self.load_or_train_models()
    
    def load_or_train_models(self):
        """Load existing models or train new ones"""
        discount_model_path = 'models/discount_model.pkl'
        bundle_model_path = 'models/bundle_model.pkl'
        
        if os.path.exists(discount_model_path):
            self.discount_model = joblib.load(discount_model_path)
        else:
            self.train_discount_model()
        
        if os.path.exists(bundle_model_path):
            self.bundle_model = joblib.load(bundle_model_path)
        else:
            self.train_bundle_model()
    
    def train_discount_model(self):
        """Train Random Forest model for discount prediction"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 10000
        
        # Generate features
        health_scores = np.random.uniform(0, 1, n_samples)
        days_in_stock = np.random.exponential(30, n_samples)
        demand_trends = np.random.normal(0, 1, n_samples)
        festival_relevance = np.random.uniform(0, 1, n_samples)
        price_levels = np.random.uniform(100, 10000, n_samples)
        quantities = np.random.exponential(50, n_samples)
        
        # Create features
        X = np.column_stack([
            health_scores,
            np.clip(days_in_stock / 365, 0, 1),
            (demand_trends + 1) / 2,  # Normalize to 0-1
            festival_relevance,
            np.log10(price_levels) / 4,  # Normalize price
            np.clip(quantities / 1000, 0, 1)
        ])
        
        # Create target (optimal discount percentage)
        # Higher discounts for unhealthy products, low demand, high quantities
        y = (
            0.4 * (1 - health_scores) +
            0.2 * np.clip(days_in_stock / 365, 0, 1) +
            0.15 * (1 - (demand_trends + 1) / 2) +
            0.1 * festival_relevance +
            0.1 * np.clip(quantities / 1000, 0, 1) +
            np.random.normal(0, 0.05, n_samples)
        )
        
        y = np.clip(y * 100, self.MIN_DISCOUNT, self.MAX_DISCOUNT)
        
        # Train Random Forest model
        self.discount_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.discount_model.fit(X, y)
        
        # Save model
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.discount_model, 'models/discount_model.pkl')
    
    def train_bundle_model(self):
        """Train model for bundle recommendations"""
        # Generate synthetic bundle data
        np.random.seed(42)
        n_samples = 5000
        
        # Generate bundle features
        main_product_value = np.random.uniform(100, 5000, n_samples)
        bundle_size = np.random.randint(2, 6, n_samples)
        category_compatibility = np.random.uniform(0, 1, n_samples)
        seasonal_relevance = np.random.uniform(0, 1, n_samples)
        
        # Create features
        X = np.column_stack([
            np.log10(main_product_value) / 4,
            bundle_size / 5,
            category_compatibility,
            seasonal_relevance
        ])
        
        # Create target (bundle discount percentage)
        y = (
            0.3 * (bundle_size - 2) * 5 +  # More items = higher discount
            0.3 * category_compatibility * 20 +  # Compatible items = higher discount
            0.2 * seasonal_relevance * 15 +  # Seasonal relevance = higher discount
            0.2 * np.random.uniform(5, 25, n_samples)  # Random variation
        )
        
        y = np.clip(y, 10, 50)  # Bundle discounts between 10-50%
        
        # Train model
        self.bundle_model = RandomForestRegressor(
            n_estimators=50,
            max_depth=8,
            random_state=42
        )
        
        self.bundle_model.fit(X, y)
        
        # Save model
        joblib.dump(self.bundle_model, 'models/bundle_model.pkl')
    
    def calculate_discount(self, product_data, health_score, festival_recommendations):
        """
        Calculate optimal discount for a product using risk-based approach
        
        Args:
            product_data (dict): Product information
            health_score (float): Product health score (0-1)
            festival_recommendations (dict): Festival opportunities
            
        Returns:
            dict: Discount recommendations
        """
        # Extract product data
        days_in_stock = product_data.get('days_in_stock', 0)
        stock_quantity = product_data.get('stock_quantity', 0)
        sales_velocity = product_data.get('sales_velocity', 0.1)  # Default to avoid division by zero
        original_price = product_data.get('price', 0)
        
        # Calculate average daily sales (units per day)
        avg_daily_sales = max(sales_velocity, 0.1)  # Minimum 0.1 to avoid division by zero
        
        # Calculate sell-through rate (units sold per day)
        sell_through_rate = avg_daily_sales
        
        # Risk Score Calculation
        # Risk Score = (Stock Age Weight × Days in Inventory) +
        #              (Stock Level Weight × (Stock / Average Daily Sales)) -
        #              (Sell-Through Rate Weight × Units/Day Sold)
        
        # Weights for risk calculation
        stock_age_weight = 0.4
        stock_level_weight = 0.4
        sell_through_weight = 0.2
        
        # Calculate risk score
        stock_age_component = stock_age_weight * days_in_stock
        stock_level_component = stock_level_weight * (stock_quantity / avg_daily_sales)
        sell_through_component = sell_through_weight * sell_through_rate
        
        risk_score = stock_age_component + stock_level_component - sell_through_component
        
        # Normalize risk score to 0-1 range (higher risk = higher discount needed)
        normalized_risk = min(max(risk_score / 100, 0), 1)  # Normalize by 100 days
        
        # Determine health status and base discount
        if health_score >= 0.7:  # Healthy
            base_discount = 5  # 5% base discount
            discount_multiplier = 0.5
        elif health_score >= 0.4:  # At Risk
            base_discount = 15  # 15% base discount
            discount_multiplier = 1.0
        else:  # Danger (Dead stock)
            base_discount = 30  # 30% base discount
            discount_multiplier = 1.5
        
        # Calculate final discount based on risk and health
        risk_based_discount = normalized_risk * 50  # Max 50% from risk
        health_based_discount = base_discount * discount_multiplier
        
        # Combine risk and health factors
        final_discount = min(risk_based_discount + health_based_discount, 70)  # Cap at 70%
        
        # Apply festival adjustments
        if festival_recommendations.get('upcoming_festivals'):
            best_festival = festival_recommendations['upcoming_festivals'][0]
            days_until = best_festival.get('days_until', 90)
            
            if days_until <= 7:
                final_discount *= 1.1  # 10% boost for last-minute rush
            elif days_until <= 30:
                final_discount *= 1.05  # 5% boost for peak shopping period
        
        # Apply quantity adjustments
        if stock_quantity > 100:
            final_discount *= 1.1  # 10% boost for high inventory
        elif stock_quantity < 10:
            final_discount *= 0.9  # 10% reduction for low inventory
        
        # Ensure discount is within reasonable bounds
        final_discount = max(min(final_discount, 70), 5)  # Between 5% and 70%
        
        # Calculate new price and savings
        new_price = original_price * (1 - final_discount / 100)
        total_savings = original_price - new_price
        expected_revenue = new_price * stock_quantity
        
        # Convert to regular Python floats for JSON serialization
        final_discount = float(final_discount)
        new_price = float(new_price)
        total_savings = float(total_savings)
        expected_revenue = float(expected_revenue)
        
        return {
            'recommended_discount': round(final_discount, 1),
            'new_price': round(new_price, 2),
            'price_reduction': round(total_savings, 2),
            'expected_revenue': round(expected_revenue, 2),
            'risk_score': round(float(normalized_risk * 100), 1),
            'health_status': self._get_health_status(health_score),
            'discount_category': self._get_discount_category(final_discount),
            'reasoning': self._get_discount_reasoning(
                final_discount, health_score, festival_recommendations, normalized_risk
            )
        }
    
    def _get_health_status(self, health_score):
        """Get health status based on score"""
        if health_score >= 0.7:
            return 'Healthy'
        elif health_score >= 0.4:
            return 'At Risk'
        else:
            return 'Danger'
    
    def _apply_discount_rules(self, predicted_discount, product_data, health_score, festival_recommendations):
        """Apply business rules to adjust discount"""
        discount = predicted_discount
        
        # Health-based adjustments
        if health_score < 0.3:  # Dead stock
            discount = min(discount * 1.3, self.MAX_DISCOUNT)
        elif health_score < 0.6:  # At risk
            discount = min(discount * 1.1, self.MAX_DISCOUNT)
        
        # Festival-based adjustments
        if festival_recommendations.get('upcoming_festivals'):
            best_festival = festival_recommendations['upcoming_festivals'][0]
            days_until = best_festival.get('days_until', 90)
            
            if days_until <= 7:
                discount *= 1.2  # Last-minute rush
            elif days_until <= 30:
                discount *= 1.1  # Peak shopping period
        
        # Quantity-based adjustments
        quantity = product_data.get('quantity', 0)
        if quantity > 100:
            discount *= 1.15  # High inventory
        elif quantity < 10:
            discount *= 0.9  # Low inventory
        
        return np.clip(discount, self.MIN_DISCOUNT, self.MAX_DISCOUNT)
    
    def _get_discount_category(self, discount):
        """Categorize discount level"""
        if discount >= 50:
            return 'Heavy Discount'
        elif discount >= 30:
            return 'Moderate Discount'
        elif discount >= 15:
            return 'Light Discount'
        else:
            return 'Minimal Discount'
    
    def _get_discount_reasoning(self, discount, health_score, festival_recommendations, risk_score):
        """Generate reasoning for discount recommendation"""
        reasons = []
        
        # Health-based reasoning
        if health_score < 0.4:
            reasons.append("Product is classified as dead stock - urgent action needed")
        elif health_score < 0.7:
            reasons.append("Product is at risk of becoming dead stock")
        else:
            reasons.append("Product is healthy - minimal discount recommended")
        
        # Risk-based reasoning
        if risk_score > 0.7:
            reasons.append("High risk score indicates urgent inventory clearance needed")
        elif risk_score > 0.4:
            reasons.append("Moderate risk score suggests proactive discounting")
        else:
            reasons.append("Low risk score - conservative discount approach")
        
        # Festival-based reasoning
        if festival_recommendations.get('upcoming_festivals'):
            best_festival = festival_recommendations['upcoming_festivals'][0]
            reasons.append(f"Upcoming {best_festival['name']} festival opportunity")
        
        # Discount level reasoning
        if discount >= 50:
            reasons.append("Heavy discount recommended to clear inventory quickly")
        elif discount >= 30:
            reasons.append("Moderate discount to boost sales velocity")
        elif discount >= 15:
            reasons.append("Light discount to maintain competitive pricing")
        else:
            reasons.append("Minimal discount to preserve margins")
        
        return reasons
    
    def generate_bundle_recommendations(self, product_data, inventory_data):
        """
        Generate bundle recommendations using Apriori algorithm
        
        Args:
            product_data (dict): Main product information
            inventory_data (list): Available inventory for bundling
            
        Returns:
            dict: Bundle recommendations
        """
        category = product_data.get('category', '').lower()
        
        # Find compatible products for bundling
        compatible_products = self._find_compatible_products(
            product_data, inventory_data, category
        )
        
        if not compatible_products:
            return {'bundles': [], 'message': 'No compatible products found for bundling'}
        
        # Generate bundle combinations
        bundles = []
        for i, combo in enumerate(self._generate_bundle_combinations(compatible_products)):
            if len(combo) >= 2 and len(combo) <= 4:  # Reasonable bundle size
                bundle_score = self._calculate_bundle_score(combo, product_data)
                bundle_discount = self._calculate_bundle_discount(combo, product_data)
                
                bundles.append({
                    'id': f'bundle_{i}',
                    'products': combo,
                    'total_value': sum(p.get('current_price', 0) for p in combo),
                    'bundle_price': sum(p.get('current_price', 0) for p in combo) * (1 - bundle_discount / 100),
                    'discount_percentage': bundle_discount,
                    'savings': sum(p.get('current_price', 0) for p in combo) * (bundle_discount / 100),
                    'score': bundle_score,
                    'theme': self._generate_bundle_theme(combo)
                })
        
        # Sort by bundle score
        bundles.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'bundles': bundles[:5],  # Top 5 bundles
            'total_bundles': len(bundles)
        }
    
    def _find_compatible_products(self, main_product, inventory_data, category):
        """Find products compatible for bundling with main product"""
        compatible = []
        
        # Get compatible categories
        compatible_categories = self.bundle_categories.get(category, [])
        
        for product in inventory_data:
            if product.get('id') == main_product.get('id'):
                continue  # Skip main product
            
            product_category = product.get('category', '').lower()
            
            # Check if product is in compatible categories
            if product_category in compatible_categories:
                compatible.append(product)
            # Also include products from same category for variety
            elif product_category == category:
                compatible.append(product)
        
        return compatible
    
    def _generate_bundle_combinations(self, products, max_size=4):
        """Generate bundle combinations"""
        from itertools import combinations
        
        combinations_list = []
        for size in range(2, min(max_size + 1, len(products) + 1)):
            combinations_list.extend(list(combinations(products, size)))
        
        return combinations_list
    
    def _calculate_bundle_score(self, bundle_products, main_product):
        """Calculate attractiveness score for a bundle"""
        score = 0
        
        # Value-based scoring
        total_value = sum(p.get('current_price', 0) for p in bundle_products)
        score += min(total_value / 1000, 1) * 30  # Value contribution
        
        # Variety scoring
        categories = set(p.get('category', '').lower() for p in bundle_products)
        score += len(categories) * 10  # More categories = better variety
        
        # Health scoring (prefer healthier products in bundles)
        avg_health = np.mean([p.get('health_score', 0.5) for p in bundle_products])
        score += avg_health * 20
        
        return score
    
    def _calculate_bundle_discount(self, bundle_products, main_product):
        """Calculate optimal discount for bundle"""
        # Prepare features for bundle model
        main_product_value = main_product.get('current_price', 0)
        bundle_size = len(bundle_products)
        
        # Calculate category compatibility
        categories = [p.get('category', '').lower() for p in bundle_products]
        main_category = main_product.get('category', '').lower()
        compatible_categories = self.bundle_categories.get(main_category, [])
        
        compatibility_score = sum(1 for cat in categories if cat in compatible_categories) / len(categories)
        
        # Seasonal relevance (simplified)
        seasonal_relevance = 0.5  # Default value
        
        features = np.array([[
            min(np.log10(max(main_product_value, 100)) / 4, 1),
            bundle_size / 5,
            compatibility_score,
            seasonal_relevance
        ]])
        
        predicted_discount = self.bundle_model.predict(features)[0]
        
        # Convert to regular Python float for JSON serialization
        return float(np.clip(predicted_discount, 10, 50))
    
    def _generate_bundle_theme(self, bundle_products):
        """Generate theme for bundle"""
        categories = [p.get('category', '').lower() for p in bundle_products]
        
        if 'clothing' in categories and 'accessories' in categories:
            return 'Complete Look Bundle'
        elif 'electronics' in categories and 'accessories' in categories:
            return 'Tech Essentials Bundle'
        elif 'home_decor' in categories and 'lighting' in categories:
            return 'Home Makeover Bundle'
        elif 'beauty' in categories and 'skincare' in categories:
            return 'Beauty Ritual Bundle'
        else:
            return 'Value Bundle' 