import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime, timedelta
import random

class BundleCalculator:
    def __init__(self):
        self.bundle_rules = {
            'festival_bundles': {
                'navratri': {
                    'primary_products': ['lehenga', 'saree', 'kurti', 'dress'],
                    'combo_products': ['oxidised_jewellery', 'bangles', 'anklets', 'earrings', 'necklace'],
                    'shopkeeper_categories': ['clothing', 'jewellery', 'accessories'],
                    'bundle_discount': 0.15,
                    'cross_shop_discount': 0.20
                },
                'diwali': {
                    'primary_products': ['ethnic_wear', 'western_wear', 'kids_clothing'],
                    'combo_products': ['home_decor', 'candles', 'rangoli', 'sweets_box'],
                    'shopkeeper_categories': ['clothing', 'home_decor', 'food'],
                    'bundle_discount': 0.12,
                    'cross_shop_discount': 0.18
                },
                'holi': {
                    'primary_products': ['white_clothing', 'traditional_wear'],
                    'combo_products': ['colors', 'water_gun', 'sweets', 'bhang'],
                    'shopkeeper_categories': ['clothing', 'festival_items', 'food'],
                    'bundle_discount': 0.10,
                    'cross_shop_discount': 0.15
                },
                'eid': {
                    'primary_products': ['kurta', 'sherwani', 'abaya', 'hijab'],
                    'combo_products': ['perfume', 'dates', 'sweets', 'prayer_items'],
                    'shopkeeper_categories': ['clothing', 'perfumes', 'food'],
                    'bundle_discount': 0.13,
                    'cross_shop_discount': 0.17
                },
                'christmas': {
                    'primary_products': ['winter_wear', 'party_dress', 'formal_wear'],
                    'combo_products': ['christmas_tree', 'decorations', 'gifts', 'chocolates'],
                    'shopkeeper_categories': ['clothing', 'home_decor', 'gifts'],
                    'bundle_discount': 0.14,
                    'cross_shop_discount': 0.19
                },
                'rakhi': {
                    'primary_products': ['ethnic_wear', 'western_wear'],
                    'combo_products': ['rakhi', 'sweets', 'gifts', 'chocolates'],
                    'shopkeeper_categories': ['clothing', 'festival_items', 'gifts'],
                    'bundle_discount': 0.11,
                    'cross_shop_discount': 0.16
                },
                'ganesh_chaturthi': {
                    'primary_products': ['traditional_wear', 'ethnic_wear'],
                    'combo_products': ['modak', 'prasad', 'decorations', 'flowers'],
                    'shopkeeper_categories': ['clothing', 'food', 'decorations'],
                    'bundle_discount': 0.12,
                    'cross_shop_discount': 0.17
                },
                'karwa_chauth': {
                    'primary_products': ['saree', 'lehenga', 'bridal_wear'],
                    'combo_products': ['mehendi', 'bangles', 'jewellery', 'sweets'],
                    'shopkeeper_categories': ['clothing', 'beauty', 'jewellery'],
                    'bundle_discount': 0.15,
                    'cross_shop_discount': 0.20
                },
                'baisakhi': {
                    'primary_products': ['punjabi_suit', 'kurta', 'traditional_wear'],
                    'combo_products': ['bhangra_items', 'sweets', 'drinks'],
                    'shopkeeper_categories': ['clothing', 'festival_items', 'food'],
                    'bundle_discount': 0.13,
                    'cross_shop_discount': 0.18
                },
                'onam': {
                    'primary_products': ['mundu', 'kasavu_saree', 'traditional_wear'],
                    'combo_products': ['pookalam_items', 'sadya_items', 'decorations'],
                    'shopkeeper_categories': ['clothing', 'decorations', 'food'],
                    'bundle_discount': 0.14,
                    'cross_shop_discount': 0.19
                }
            },
            'seasonal_bundles': {
                'summer': {
                    'primary_products': ['cotton_wear', 'summer_dresses', 'casual_wear'],
                    'combo_products': ['sunglasses', 'hats', 'cooling_items'],
                    'shopkeeper_categories': ['clothing', 'accessories', 'seasonal'],
                    'bundle_discount': 0.10,
                    'cross_shop_discount': 0.15
                },
                'winter': {
                    'primary_products': ['winter_wear', 'sweaters', 'jackets'],
                    'combo_products': ['warmers', 'hot_beverages', 'comfort_items'],
                    'shopkeeper_categories': ['clothing', 'seasonal', 'food'],
                    'bundle_discount': 0.12,
                    'cross_shop_discount': 0.17
                },
                'monsoon': {
                    'primary_products': ['rain_wear', 'quick_dry_clothes'],
                    'combo_products': ['umbrellas', 'rain_boots', 'waterproof_items'],
                    'shopkeeper_categories': ['clothing', 'accessories', 'seasonal'],
                    'bundle_discount': 0.11,
                    'cross_shop_discount': 0.16
                }
            }
        }
        
        self.shopkeeper_profiles = {
            'clothing_store': {
                'name': 'Fashion Hub',
                'category': 'clothing',
                'location': 'mumbai',
                'specialties': ['ethnic_wear', 'western_wear', 'traditional_wear'],
                'collaboration_partners': ['jewellery_store', 'accessories_store']
            },
            'jewellery_store': {
                'name': 'Sparkle & Shine',
                'category': 'jewellery',
                'location': 'mumbai',
                'specialties': ['oxidised_jewellery', 'bangles', 'necklace', 'earrings'],
                'collaboration_partners': ['clothing_store', 'accessories_store']
            },
            'accessories_store': {
                'name': 'Style Accessories',
                'category': 'accessories',
                'location': 'mumbai',
                'specialties': ['bags', 'shoes', 'belts', 'sunglasses'],
                'collaboration_partners': ['clothing_store', 'jewellery_store']
            },
            'home_decor_store': {
                'name': 'Home Beautiful',
                'category': 'home_decor',
                'location': 'mumbai',
                'specialties': ['decorations', 'candles', 'rangoli', 'festival_items'],
                'collaboration_partners': ['clothing_store', 'food_store']
            },
            'food_store': {
                'name': 'Taste of India',
                'category': 'food',
                'location': 'mumbai',
                'specialties': ['sweets', 'snacks', 'festival_food'],
                'collaboration_partners': ['clothing_store', 'home_decor_store']
            }
        }

    def get_available_shopkeepers(self, location: str) -> List[Dict]:
        """Get available shopkeepers for a specific location"""
        available_shopkeepers = []
        for shop_id, profile in self.shopkeeper_profiles.items():
            if profile['location'].lower() == location.lower():
                available_shopkeepers.append({
                    'id': shop_id,
                    'name': profile['name'],
                    'category': profile['category'],
                    'specialties': profile['specialties'],
                    'partners': profile['collaboration_partners']
                })
        return available_shopkeepers

    def get_local_seller_recommendations(self, primary_product: Dict, combo_products: List[Dict], location: str) -> Dict:
        """Get local seller recommendations for bundle creation"""
        
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj

        # Enhanced shopkeeper database with more realistic data
        enhanced_shopkeepers = {
            'mumbai': {
                'clothing': [
                    {'name': 'Fashion Hub Mumbai', 'rating': 4.8, 'specialties': ['ethnic_wear', 'western_wear'], 'contact': '+91-98765-43210'},
                    {'name': 'Style Studio', 'rating': 4.6, 'specialties': ['traditional_wear', 'bridal_wear'], 'contact': '+91-98765-43211'},
                    {'name': 'Urban Fashion', 'rating': 4.5, 'specialties': ['casual_wear', 'party_wear'], 'contact': '+91-98765-43212'}
                ],
                'jewellery': [
                    {'name': 'Sparkle & Shine', 'rating': 4.9, 'specialties': ['oxidised_jewellery', 'bangles'], 'contact': '+91-98765-43213'},
                    {'name': 'Royal Jewellers', 'rating': 4.7, 'specialties': ['necklace', 'earrings'], 'contact': '+91-98765-43214'},
                    {'name': 'Heritage Jewellery', 'rating': 4.6, 'specialties': ['traditional_jewellery', 'anklets'], 'contact': '+91-98765-43215'}
                ],
                'accessories': [
                    {'name': 'Style Accessories', 'rating': 4.5, 'specialties': ['bags', 'shoes'], 'contact': '+91-98765-43216'},
                    {'name': 'Trendy Accessories', 'rating': 4.4, 'specialties': ['belts', 'sunglasses'], 'contact': '+91-98765-43217'}
                ],
                'home_decor': [
                    {'name': 'Home Beautiful', 'rating': 4.6, 'specialties': ['decorations', 'candles'], 'contact': '+91-98765-43218'},
                    {'name': 'Festival Decor', 'rating': 4.5, 'specialties': ['rangoli', 'festival_items'], 'contact': '+91-98765-43219'}
                ]
            },
            'delhi': {
                'clothing': [
                    {'name': 'Delhi Fashion House', 'rating': 4.7, 'specialties': ['ethnic_wear', 'western_wear'], 'contact': '+91-98765-43220'},
                    {'name': 'Chandni Chowk Styles', 'rating': 4.8, 'specialties': ['traditional_wear', 'bridal_wear'], 'contact': '+91-98765-43221'}
                ],
                'jewellery': [
                    {'name': 'Delhi Jewellers', 'rating': 4.8, 'specialties': ['oxidised_jewellery', 'bangles'], 'contact': '+91-98765-43222'},
                    {'name': 'Heritage Jewellery Delhi', 'rating': 4.7, 'specialties': ['necklace', 'earrings'], 'contact': '+91-98765-43223'}
                ]
            },
            'bangalore': {
                'clothing': [
                    {'name': 'Bangalore Fashion Hub', 'rating': 4.6, 'specialties': ['ethnic_wear', 'western_wear'], 'contact': '+91-98765-43224'},
                    {'name': 'Silk City Styles', 'rating': 4.7, 'specialties': ['traditional_wear', 'silk_wear'], 'contact': '+91-98765-43225'}
                ],
                'jewellery': [
                    {'name': 'Bangalore Jewellers', 'rating': 4.7, 'specialties': ['oxidised_jewellery', 'bangles'], 'contact': '+91-98765-43226'}
                ]
            },
            'chennai': {
                'clothing': [
                    {'name': 'Chennai Fashion House', 'rating': 4.6, 'specialties': ['ethnic_wear', 'traditional_wear'], 'contact': '+91-98765-43227'},
                    {'name': 'Tamil Nadu Styles', 'rating': 4.7, 'specialties': ['saree', 'traditional_wear'], 'contact': '+91-98765-43228'}
                ],
                'jewellery': [
                    {'name': 'Chennai Jewellers', 'rating': 4.7, 'specialties': ['traditional_jewellery', 'temple_jewellery'], 'contact': '+91-98765-43229'}
                ]
            },
            'hyderabad': {
                'clothing': [
                    {'name': 'Hyderabad Fashion Hub', 'rating': 4.6, 'specialties': ['ethnic_wear', 'traditional_wear'], 'contact': '+91-98765-43230'},
                    {'name': 'Pearl City Styles', 'rating': 4.7, 'specialties': ['bridal_wear', 'traditional_wear'], 'contact': '+91-98765-43231'}
                ],
                'jewellery': [
                    {'name': 'Hyderabad Jewellers', 'rating': 4.8, 'specialties': ['pearl_jewellery', 'traditional_jewellery'], 'contact': '+91-98765-43232'}
                ]
            },
            'kolkata': {
                'clothing': [
                    {'name': 'Kolkata Fashion House', 'rating': 4.6, 'specialties': ['ethnic_wear', 'traditional_wear'], 'contact': '+91-98765-43233'},
                    {'name': 'City of Joy Styles', 'rating': 4.7, 'specialties': ['saree', 'traditional_wear'], 'contact': '+91-98765-43234'}
                ],
                'jewellery': [
                    {'name': 'Kolkata Jewellers', 'rating': 4.7, 'specialties': ['traditional_jewellery', 'bengali_jewellery'], 'contact': '+91-98765-43235'}
                ]
            },
            'pune': {
                'clothing': [
                    {'name': 'Pune Fashion Hub', 'rating': 4.5, 'specialties': ['ethnic_wear', 'western_wear'], 'contact': '+91-98765-43236'},
                    {'name': 'Oxford of East Styles', 'rating': 4.6, 'specialties': ['traditional_wear', 'casual_wear'], 'contact': '+91-98765-43237'}
                ],
                'jewellery': [
                    {'name': 'Pune Jewellers', 'rating': 4.6, 'specialties': ['oxidised_jewellery', 'traditional_jewellery'], 'contact': '+91-98765-43238'}
                ]
            },
            'ahmedabad': {
                'clothing': [
                    {'name': 'Ahmedabad Fashion House', 'rating': 4.6, 'specialties': ['ethnic_wear', 'traditional_wear'], 'contact': '+91-98765-43239'},
                    {'name': 'Manchester of India Styles', 'rating': 4.7, 'specialties': ['traditional_wear', 'handloom'], 'contact': '+91-98765-43240'}
                ],
                'jewellery': [
                    {'name': 'Ahmedabad Jewellers', 'rating': 4.7, 'specialties': ['traditional_jewellery', 'gujarati_jewellery'], 'contact': '+91-98765-43241'}
                ]
            }
        }

        # Get location-specific shopkeepers
        location_shopkeepers = enhanced_shopkeepers.get(location.lower(), enhanced_shopkeepers.get('mumbai', {}))
        
        # Analyze primary product category
        primary_category = primary_product.get('category', 'clothing').lower()
        primary_name = primary_product.get('name', '').lower()
        
        # Determine complementary categories based on primary product
        complementary_categories = []
        if primary_category in ['clothing', 'ethnic_wear', 'traditional_wear', 'western_wear']:
            complementary_categories = ['jewellery', 'accessories', 'home_decor']
        elif primary_category in ['jewellery', 'accessories']:
            complementary_categories = ['clothing', 'home_decor']
        elif primary_category in ['home_decor', 'festival_items']:
            complementary_categories = ['clothing', 'jewellery', 'accessories']
        else:
            complementary_categories = ['clothing', 'jewellery', 'accessories', 'home_decor']

        # Get recommendations for each complementary category
        recommendations = {}
        for category in complementary_categories:
            if category in location_shopkeepers:
                category_sellers = location_shopkeepers[category]
                # Sort by rating and take top 3
                sorted_sellers = sorted(category_sellers, key=lambda x: x['rating'], reverse=True)[:3]
                recommendations[category] = sorted_sellers

        # Generate collaboration suggestions
        collaboration_suggestions = []
        for category, sellers in recommendations.items():
            for seller in sellers:
                suggestion = {
                    'seller_name': seller['name'],
                    'category': category,
                    'rating': seller['rating'],
                    'specialties': seller['specialties'],
                    'contact': seller['contact'],
                    'collaboration_type': 'cross_promotion',
                    'suggestion_text': f"Partner with {seller['name']} for {category} items to create attractive bundles",
                    'benefits': [
                        f"Access to {seller['rating']}-star rated {category} products",
                        f"Cross-promotion opportunities",
                        f"Shared customer base",
                        f"Enhanced bundle appeal"
                    ]
                }
                collaboration_suggestions.append(suggestion)

        # Sort suggestions by rating
        collaboration_suggestions.sort(key=lambda x: x['rating'], reverse=True)

        return convert_numpy_types({
            'location': location,
            'primary_product': primary_product,
            'combo_products': combo_products,
            'recommendations': recommendations,
            'collaboration_suggestions': collaboration_suggestions[:6],  # Top 6 suggestions
            'total_suggestions': len(collaboration_suggestions),
            'message': f"Found {len(collaboration_suggestions)} potential collaboration partners in {location.title()}"
        })

    def calculate_bundle_recommendations(self, 
                                       product_data: Dict, 
                                       location: str = 'mumbai',
                                       festival: Optional[str] = None,
                                       shopkeeper_id: Optional[str] = None) -> Dict:
        """Calculate bundle recommendations with shopkeeper collaboration"""
        
        # Convert numpy types to native Python types
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj

        product_category = product_data.get('category', 'general').lower()
        product_name = product_data.get('name', '').lower()
        
        # Determine applicable bundles
        applicable_bundles = []
        
        # Festival-based bundles
        if festival and festival in self.bundle_rules['festival_bundles']:
            festival_bundle = self.bundle_rules['festival_bundles'][festival]
            if (product_category in festival_bundle['primary_products'] or 
                any(p in product_name for p in festival_bundle['primary_products'])):
                applicable_bundles.append({
                    'type': 'festival',
                    'festival': festival,
                    'rules': festival_bundle
                })
        
        # Seasonal bundles
        current_month = datetime.now().month
        if current_month in [3, 4, 5]:  # Summer
            season = 'summer'
        elif current_month in [6, 7, 8, 9]:  # Monsoon
            season = 'monsoon'
        else:  # Winter
            season = 'winter'
            
        if season in self.bundle_rules['seasonal_bundles']:
            seasonal_bundle = self.bundle_rules['seasonal_bundles'][season]
            if (product_category in seasonal_bundle['primary_products'] or 
                any(p in product_name for p in seasonal_bundle['primary_products'])):
                applicable_bundles.append({
                    'type': 'seasonal',
                    'season': season,
                    'rules': seasonal_bundle
                })

        # Generate bundle recommendations
        bundle_recommendations = []
        
        for bundle in applicable_bundles:
            rules = bundle['rules']
            
            # Same shop bundles
            same_shop_bundles = []
            for combo_product in rules['combo_products']:
                same_shop_bundles.append({
                    'product': combo_product,
                    'discount': rules['bundle_discount'],
                    'type': 'same_shop',
                    'description': f"Bundle with {combo_product} for {rules['bundle_discount']*100}% off"
                })
            
            # Cross-shop bundles
            cross_shop_bundles = []
            available_shopkeepers = self.get_available_shopkeepers(location)
            
            for shopkeeper in available_shopkeepers:
                if shopkeeper['category'] in rules['shopkeeper_categories']:
                    for specialty in shopkeeper['specialties']:
                        if specialty in rules['combo_products']:
                            cross_shop_bundles.append({
                                'product': specialty,
                                'shopkeeper': shopkeeper['name'],
                                'shopkeeper_id': shopkeeper['id'],
                                'discount': rules['cross_shop_discount'],
                                'type': 'cross_shop',
                                'description': f"Bundle with {specialty} from {shopkeeper['name']} for {rules['cross_shop_discount']*100}% off"
                            })
            
            bundle_recommendations.append({
                'bundle_type': bundle['type'],
                'festival': bundle.get('festival'),
                'season': bundle.get('season'),
                'same_shop_bundles': same_shop_bundles,
                'cross_shop_bundles': cross_shop_bundles,
                'total_bundles': len(same_shop_bundles) + len(cross_shop_bundles)
            })

        # Calculate bundle score
        total_bundles = sum(len(rec['same_shop_bundles']) + len(rec['cross_shop_bundles']) 
                          for rec in bundle_recommendations)
        bundle_score = min(100, total_bundles * 20)  # Score based on number of bundle options

        result = {
            'bundle_score': float(bundle_score),
            'recommendations': bundle_recommendations,
            'available_shopkeepers': self.get_available_shopkeepers(location),
            'total_bundles': total_bundles,
            'location': location,
            'festival': festival
        }
        
        return convert_numpy_types(result)

    def create_custom_bundle(self, 
                           primary_product: Dict, 
                           combo_products: List[Dict],
                           shopkeepers: List[str],
                           location: str) -> Dict:
        """Create a custom bundle with multiple shopkeepers"""
        
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj

        # Calculate bundle pricing
        primary_price = float(primary_product.get('price', 0))
        combo_prices = [float(product.get('price', 0)) for product in combo_products]
        
        total_original_price = primary_price + sum(combo_prices)
        
        # Apply bundle discounts
        if len(combo_products) == 1:
            bundle_discount = 0.15
        elif len(combo_products) == 2:
            bundle_discount = 0.20
        else:
            bundle_discount = 0.25
            
        discounted_price = total_original_price * (1 - bundle_discount)
        savings = total_original_price - discounted_price
        
        # Create bundle details
        bundle_details = {
            'primary_product': {
                'name': primary_product.get('name'),
                'price': primary_price,
                'category': primary_product.get('category')
            },
            'combo_products': [
                {
                    'name': product.get('name'),
                    'price': float(product.get('price', 0)),
                    'category': product.get('category'),
                    'shopkeeper': shopkeepers[i] if i < len(shopkeepers) else 'Unknown'
                }
                for i, product in enumerate(combo_products)
            ],
            'pricing': {
                'original_total': float(total_original_price),
                'discounted_total': float(discounted_price),
                'savings': float(savings),
                'discount_percentage': float(bundle_discount * 100)
            },
            'shopkeepers': shopkeepers,
            'location': location,
            'bundle_id': f"bundle_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'created_at': datetime.now().isoformat()
        }
        
        return convert_numpy_types(bundle_details)

    def get_bundle_analytics(self, location: str) -> Dict:
        """Get analytics for bundle performance in a location"""
        
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj

        # Simulate bundle analytics data
        analytics = {
            'location': location,
            'total_bundles_created': random.randint(50, 200),
            'total_revenue': random.uniform(50000, 150000),
            'average_bundle_value': random.uniform(800, 1500),
            'most_popular_bundles': [
                {'festival': 'navratri', 'count': random.randint(20, 50)},
                {'festival': 'diwali', 'count': random.randint(15, 40)},
                {'festival': 'holi', 'count': random.randint(10, 30)}
            ],
            'shopkeeper_collaborations': [
                {'shopkeeper': 'Fashion Hub', 'bundles': random.randint(30, 80)},
                {'shopkeeper': 'Sparkle & Shine', 'bundles': random.randint(25, 60)},
                {'shopkeeper': 'Style Accessories', 'bundles': random.randint(20, 50)}
            ],
            'monthly_trends': [
                {'month': 'Jan', 'bundles': random.randint(10, 30)},
                {'month': 'Feb', 'bundles': random.randint(15, 35)},
                {'month': 'Mar', 'bundles': random.randint(20, 40)},
                {'month': 'Apr', 'bundles': random.randint(25, 45)},
                {'month': 'May', 'bundles': random.randint(30, 50)},
                {'month': 'Jun', 'bundles': random.randint(35, 55)}
            ]
        }
        
        return convert_numpy_types(analytics) 