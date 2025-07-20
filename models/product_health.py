import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import os

class ProductHealthAnalyzer:
    """
    Analyzes product health using multiple factors:
    - Days in stock
    - Price depreciation
    - Demand trends
    - Seasonality
    - Quantity levels
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None
        self.load_or_train_model()
        
        # Health thresholds
        self.HEALTHY_THRESHOLD = 0.7
        self.AT_RISK_THRESHOLD = 0.4
        self.DEAD_THRESHOLD = 0.2
        
    def load_or_train_model(self):
        """Load existing model or train a new one"""
        model_path = 'models/xgboost_health_model.pkl'
        
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            self.train_model()
    
    def train_model(self):
        """Train XGBoost model for health prediction"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 10000
        
        # Generate realistic product data
        days_in_stock = np.random.exponential(30, n_samples)
        price_depreciation = np.random.beta(2, 5, n_samples)
        demand_trend = np.random.normal(0, 1, n_samples)
        quantity_level = np.random.uniform(0, 1, n_samples)
        seasonality_score = np.random.uniform(0, 1, n_samples)
        
        # Create features
        X = np.column_stack([
            days_in_stock,
            price_depreciation,
            demand_trend,
            quantity_level,
            seasonality_score
        ])
        
        # Create target (health scores)
        # Health decreases with days in stock and price depreciation
        # Increases with demand trend and seasonality
        y = (
            0.3 * (1 - np.clip(days_in_stock / 365, 0, 1)) +
            0.2 * (1 - price_depreciation) +
            0.2 * (0.5 + 0.5 * np.tanh(demand_trend)) +
            0.15 * quantity_level +
            0.15 * seasonality_score +
            np.random.normal(0, 0.05, n_samples)
        )
        
        y = np.clip(y, 0, 1)
        
        # Train XGBoost model
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        self.model.fit(X, y)
        
        # Save model
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, 'models/xgboost_health_model.pkl')
    
    def analyze_health(self, product_data):
        """
        Analyze product health and return a score between 0 and 1
        
        Args:
            product_data (dict): Product information
            
        Returns:
            float: Health score (0-1, where 1 is healthy)
        """
        # Extract features
        days_in_stock = product_data.get('days_in_stock', 0)
        original_price = product_data.get('original_price', 0)
        current_price = product_data.get('current_price', 0)
        quantity = product_data.get('quantity', 0)
        demand_trend = product_data.get('demand_trend', 0)
        
        # Calculate derived features
        price_depreciation = 0
        if original_price > 0:
            price_depreciation = (original_price - current_price) / original_price
        
        # Normalize quantity (assuming max quantity is 1000)
        quantity_level = min(quantity / 1000, 1.0)
        
        # Calculate seasonality score based on product category
        seasonality_score = self._calculate_seasonality_score(product_data)
        
        # Prepare features for model
        features = np.array([[
            days_in_stock,
            price_depreciation,
            demand_trend,
            quantity_level,
            seasonality_score
        ]])
        
        # Get prediction from model
        health_score = self.model.predict(features)[0]
        
        # Apply business rules
        health_score = self._apply_business_rules(health_score, product_data)
        
        # Convert to regular Python float for JSON serialization
        return float(np.clip(health_score, 0, 1))
    
    def _calculate_seasonality_score(self, product_data):
        """Calculate seasonality score based on product category and current date"""
        category = product_data.get('category', '').lower()
        current_month = datetime.now().month
        
        # Define seasonal patterns
        seasonal_patterns = {
            'clothing': {
                'summer': [3, 4, 5, 6],  # March-June
                'winter': [11, 12, 1, 2],  # Nov-Feb
                'monsoon': [7, 8, 9],  # July-Sept
                'festival': [10, 11]  # Oct-Nov
            },
            'electronics': {
                'festival': [10, 11, 12],  # Diwali, Christmas
                'back_to_school': [5, 6],  # May-June
                'year_end': [12, 1]  # Dec-Jan
            },
            'home_decor': {
                'festival': [10, 11, 12],  # Diwali, Christmas
                'wedding': [11, 12, 1, 2],  # Wedding season
                'spring': [2, 3, 4]  # Spring cleaning
            }
        }
        
        # Default seasonality score
        seasonality_score = 0.5
        
        if category in seasonal_patterns:
            patterns = seasonal_patterns[category]
            
            # Check if current month is in any seasonal pattern
            for season, months in patterns.items():
                if current_month in months:
                    seasonality_score = 0.8
                    break
        
        return seasonality_score
    
    def _apply_business_rules(self, health_score, product_data):
        """Apply business rules to adjust health score"""
        days_in_stock = product_data.get('days_in_stock', 0)
        quantity = product_data.get('quantity', 0)
        
        # Penalize products that have been in stock too long
        if days_in_stock > 365:  # More than 1 year
            health_score *= 0.5
        elif days_in_stock > 180:  # More than 6 months
            health_score *= 0.8
        
        # Penalize very high quantities
        if quantity > 500:
            health_score *= 0.9
        
        return health_score
    
    def get_health_status(self, health_score):
        """
        Convert health score to status
        
        Args:
            health_score (float): Health score between 0 and 1
            
        Returns:
            str: 'Healthy', 'At Risk', or 'Dead'
        """
        if health_score >= self.HEALTHY_THRESHOLD:
            return 'Healthy'
        elif health_score >= self.AT_RISK_THRESHOLD:
            return 'At Risk'
        else:
            return 'Dead'
    
    def calculate_rescue_score(self, product_data, festival_recommendations, discount_recommendations):
        """
        Calculate rescue score using XGBoost and multiple factors
        
        Args:
            product_data (dict): Product information
            festival_recommendations (dict): Festival opportunities
            discount_recommendations (dict): Discount recommendations
            
        Returns:
            float: Rescue score (0-100)
        """
        # Base health score
        health_score = self.analyze_health(product_data)
        
        # Festival opportunity score
        festival_score = 0
        if festival_recommendations.get('upcoming_festivals'):
            festival_score = min(len(festival_recommendations['upcoming_festivals']) * 10, 30)
        
        # Discount effectiveness score
        discount_score = 0
        recommended_discount = discount_recommendations.get('recommended_discount', 0)
        if recommended_discount > 0:
            discount_score = min(recommended_discount * 0.5, 25)
        
        # Demand trend score
        demand_trend = product_data.get('demand_trend', 0)
        demand_score = max(0, min(demand_trend * 10, 20))
        
        # Seasonality bonus
        seasonality_bonus = 0
        if self._calculate_seasonality_score(product_data) > 0.7:
            seasonality_bonus = 15
        
        # Calculate final rescue score
        rescue_score = (
            (1 - health_score) * 30 +  # Higher score for unhealthy products
            festival_score +
            discount_score +
            demand_score +
            seasonality_bonus
        )
        
        # Convert to regular Python float for JSON serialization
        return float(min(rescue_score, 100))
    
    def get_health_insights(self, product_data, health_score):
        """
        Get detailed insights about product health
        
        Args:
            product_data (dict): Product information
            health_score (float): Calculated health score
            
        Returns:
            dict: Health insights and recommendations
        """
        insights = {
            'primary_factors': [],
            'recommendations': [],
            'risk_level': 'Low'
        }
        
        days_in_stock = product_data.get('days_in_stock', 0)
        quantity = product_data.get('quantity', 0)
        demand_trend = product_data.get('demand_trend', 0)
        
        # Analyze primary factors
        if days_in_stock > 180:
            insights['primary_factors'].append(f"Product has been in stock for {days_in_stock} days")
            insights['recommendations'].append("Consider aggressive discounting or bundling")
        
        if quantity > 100:
            insights['primary_factors'].append(f"High inventory level: {quantity} units")
            insights['recommendations'].append("Implement bulk purchase incentives")
        
        if demand_trend < -0.5:
            insights['primary_factors'].append("Declining demand trend")
            insights['recommendations'].append("Focus on seasonal promotions")
        
        # Set risk level
        if health_score < 0.3:
            insights['risk_level'] = 'High'
        elif health_score < 0.6:
            insights['risk_level'] = 'Medium'
        
        return insights 