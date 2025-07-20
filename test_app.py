#!/usr/bin/env python3
"""
Test script for Dead Stock Intelligence System
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        from models.product_health import ProductHealthAnalyzer
        print("✅ ProductHealthAnalyzer imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ProductHealthAnalyzer: {e}")
        return False
    
    try:
        from models.festival_engine import FestivalPromotionEngine
        print("✅ FestivalPromotionEngine imported successfully")
    except Exception as e:
        print(f"❌ Failed to import FestivalPromotionEngine: {e}")
        return False
    
    try:
        from models.discount_calculator import SmartDiscountCalculator
        print("✅ SmartDiscountCalculator imported successfully")
    except Exception as e:
        print(f"❌ Failed to import SmartDiscountCalculator: {e}")
        return False
    
    try:
        from models.location_service import LocationService
        print("✅ LocationService imported successfully")
    except Exception as e:
        print(f"❌ Failed to import LocationService: {e}")
        return False
    
    return True

def test_product_health():
    """Test product health analysis"""
    print("\nTesting Product Health Analysis...")
    
    try:
        from models.product_health import ProductHealthAnalyzer
        
        analyzer = ProductHealthAnalyzer()
        
        # Test product data
        product_data = {
            'name': 'Test Product',
            'category': 'clothing',
            'days_in_stock': 150,
            'original_price': 2000,
            'current_price': 1500,
            'quantity': 50,
            'seasonality': 'festival',
            'location': 'mumbai',
            'last_sale_date': '2024-01-01',
            'demand_trend': -0.3
        }
        
        health_score = analyzer.analyze_health(product_data)
        health_status = analyzer.get_health_status(health_score)
        
        print(f"✅ Health Score: {health_score:.2f}")
        print(f"✅ Health Status: {health_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Product health test failed: {e}")
        return False

def test_festival_engine():
    """Test festival recommendations"""
    print("\nTesting Festival Engine...")
    
    try:
        from models.festival_engine import FestivalPromotionEngine
        
        engine = FestivalPromotionEngine()
        
        # Test festival recommendations
        product_data = {
            'name': 'Test Product',
            'category': 'clothing',
            'location': 'mumbai'
        }
        
        location_data = {
            'region': 'maharashtra',
            'city': 'Mumbai'
        }
        
        recommendations = engine.get_festival_recommendations(product_data, location_data)
        
        print(f"✅ Found {len(recommendations.get('upcoming_festivals', []))} festival opportunities")
        
        return True
        
    except Exception as e:
        print(f"❌ Festival engine test failed: {e}")
        return False

def test_discount_calculator():
    """Test discount calculations"""
    print("\nTesting Discount Calculator...")
    
    try:
        from models.discount_calculator import SmartDiscountCalculator
        
        calculator = SmartDiscountCalculator()
        
        # Test discount calculation
        product_data = {
            'name': 'Test Product',
            'category': 'clothing',
            'days_in_stock': 150,
            'original_price': 2000,
            'current_price': 1500,
            'quantity': 50,
            'demand_trend': -0.3
        }
        
        health_score = 0.4  # At risk
        festival_recommendations = {
            'upcoming_festivals': [{
                'name': 'Diwali',
                'relevance_score': 0.8,
                'days_until': 30
            }]
        }
        
        discount_result = calculator.calculate_discount(
            product_data, health_score, festival_recommendations
        )
        
        print(f"✅ Recommended Discount: {discount_result.get('recommended_discount', 0)}%")
        print(f"✅ New Price: ₹{discount_result.get('new_price', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Discount calculator test failed: {e}")
        return False

def test_location_service():
    """Test location service"""
    print("\nTesting Location Service...")
    
    try:
        from models.location_service import LocationService
        
        service = LocationService()
        
        # Test location info
        location_info = service.get_location_info('mumbai')
        
        print(f"✅ Location: {location_info.get('city', 'Unknown')}")
        print(f"✅ Region: {location_info.get('region', 'Unknown')}")
        print(f"✅ Economic Zone: {location_info.get('economic_zone', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Location service test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Dead Stock Intelligence - System Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_product_health,
        test_festival_engine,
        test_discount_calculator,
        test_location_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 To start the application:")
        print("   python app.py")
        print("   Then open http://localhost:5000 in your browser")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 