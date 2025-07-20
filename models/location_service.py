import requests
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

class LocationService:
    """
    Location-Aware Service that provides GeoIP-based location detection
    and regional insights for personalized clearance strategies
    """
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="dead_stock_intelligence")
        
        # Indian cities and their regional data
        self.indian_cities = {
            # Metro Cities
            'mumbai': {
                'state': 'Maharashtra',
                'region': 'maharashtra',
                'population': 20411274,
                'avg_income': 450000,
                'shopping_preferences': ['ethnic_wear', 'electronics', 'luxury_items'],
                'festival_importance': ['diwali', 'ganesh_chaturthi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'metro'
            },
            'delhi': {
                'state': 'Delhi',
                'region': 'north_india',
                'population': 16787941,
                'avg_income': 480000,
                'shopping_preferences': ['western_wear', 'electronics', 'home_decor'],
                'festival_importance': ['diwali', 'holi', 'christmas'],
                'climate': 'semi_arid',
                'economic_zone': 'metro'
            },
            'bangalore': {
                'state': 'Karnataka',
                'region': 'karnataka',
                'population': 12425304,
                'avg_income': 520000,
                'shopping_preferences': ['western_wear', 'electronics', 'casual_wear'],
                'festival_importance': ['diwali', 'ganesh_chaturthi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'metro'
            },
            'chennai': {
                'state': 'Tamil Nadu',
                'region': 'tamil_nadu',
                'population': 7088000,
                'avg_income': 380000,
                'shopping_preferences': ['traditional_wear', 'electronics', 'home_decor'],
                'festival_importance': ['diwali', 'pongal', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'metro'
            },
            'kolkata': {
                'state': 'West Bengal',
                'region': 'west_bengal',
                'population': 14850000,
                'avg_income': 350000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'books'],
                'festival_importance': ['diwali', 'durga_puja', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'metro'
            },
            'hyderabad': {
                'state': 'Telangana',
                'region': 'andhra_pradesh',
                'population': 6993262,
                'avg_income': 420000,
                'shopping_preferences': ['ethnic_wear', 'electronics', 'jewelry'],
                'festival_importance': ['diwali', 'ganesh_chaturthi', 'eid'],
                'climate': 'tropical',
                'economic_zone': 'metro'
            },
            'ahmedabad': {
                'state': 'Gujarat',
                'region': 'gujarat',
                'population': 5570585,
                'avg_income': 400000,
                'shopping_preferences': ['ethnic_wear', 'textiles', 'jewelry'],
                'festival_importance': ['diwali', 'holi', 'navratri'],
                'climate': 'semi_arid',
                'economic_zone': 'tier1'
            },
            'pune': {
                'state': 'Maharashtra',
                'region': 'maharashtra',
                'population': 3115431,
                'avg_income': 450000,
                'shopping_preferences': ['western_wear', 'electronics', 'sports_items'],
                'festival_importance': ['diwali', 'ganesh_chaturthi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier1'
            },
            'surat': {
                'state': 'Gujarat',
                'region': 'gujarat',
                'population': 4467797,
                'avg_income': 380000,
                'shopping_preferences': ['textiles', 'jewelry', 'ethnic_wear'],
                'festival_importance': ['diwali', 'holi', 'navratri'],
                'climate': 'tropical',
                'economic_zone': 'tier1'
            },
            'jaipur': {
                'state': 'Rajasthan',
                'region': 'north_india',
                'population': 3073350,
                'avg_income': 320000,
                'shopping_preferences': ['ethnic_wear', 'jewelry', 'handicrafts'],
                'festival_importance': ['diwali', 'holi', 'teej'],
                'climate': 'semi_arid',
                'economic_zone': 'tier1'
            },
            # North India
            'lucknow': {
                'state': 'Uttar Pradesh',
                'region': 'north_india',
                'population': 2817100,
                'avg_income': 280000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'jewelry'],
                'festival_importance': ['diwali', 'holi', 'eid'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'kanpur': {
                'state': 'Uttar Pradesh',
                'region': 'north_india',
                'population': 2767031,
                'avg_income': 250000,
                'shopping_preferences': ['ethnic_wear', 'textiles', 'footwear'],
                'festival_importance': ['diwali', 'holi', 'eid'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'varanasi': {
                'state': 'Uttar Pradesh',
                'region': 'north_india',
                'population': 1198491,
                'avg_income': 200000,
                'shopping_preferences': ['religious_items', 'traditional_wear', 'handicrafts'],
                'festival_importance': ['diwali', 'holi', 'dev_deepawali'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'agra': {
                'state': 'Uttar Pradesh',
                'region': 'north_india',
                'population': 1585704,
                'avg_income': 220000,
                'shopping_preferences': ['handicrafts', 'traditional_wear', 'tourist_items'],
                'festival_importance': ['diwali', 'holi', 'taj_mahotsav'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'jodhpur': {
                'state': 'Rajasthan',
                'region': 'north_india',
                'population': 1033754,
                'avg_income': 280000,
                'shopping_preferences': ['ethnic_wear', 'handicrafts', 'jewelry'],
                'festival_importance': ['diwali', 'holi', 'marwar_festival'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'udaipur': {
                'state': 'Rajasthan',
                'region': 'north_india',
                'population': 658339,
                'avg_income': 300000,
                'shopping_preferences': ['ethnic_wear', 'handicrafts', 'tourist_items'],
                'festival_importance': ['diwali', 'holi', 'mewar_festival'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'patna': {
                'state': 'Bihar',
                'region': 'bihar',
                'population': 2046652,
                'avg_income': 180000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'books'],
                'festival_importance': ['diwali', 'holi', 'chhath_puja'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'chandigarh': {
                'state': 'Chandigarh',
                'region': 'north_india',
                'population': 1055450,
                'avg_income': 450000,
                'shopping_preferences': ['western_wear', 'electronics', 'lifestyle'],
                'festival_importance': ['diwali', 'holi', 'christmas'],
                'climate': 'semi_arid',
                'economic_zone': 'tier1'
            },
            'amritsar': {
                'state': 'Punjab',
                'region': 'north_india',
                'population': 1132383,
                'avg_income': 320000,
                'shopping_preferences': ['ethnic_wear', 'religious_items', 'traditional_wear'],
                'festival_importance': ['diwali', 'holi', 'baisakhi'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'ludhiana': {
                'state': 'Punjab',
                'region': 'north_india',
                'population': 1618879,
                'avg_income': 350000,
                'shopping_preferences': ['western_wear', 'textiles', 'sports_items'],
                'festival_importance': ['diwali', 'holi', 'baisakhi'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'dehradun': {
                'state': 'Uttarakhand',
                'region': 'north_india',
                'population': 578420,
                'avg_income': 380000,
                'shopping_preferences': ['western_wear', 'outdoor_gear', 'traditional_items'],
                'festival_importance': ['diwali', 'holi', 'kedarnath_yatra'],
                'climate': 'temperate',
                'economic_zone': 'tier2'
            },
            'shimla': {
                'state': 'Himachal Pradesh',
                'region': 'north_india',
                'population': 169578,
                'avg_income': 350000,
                'shopping_preferences': ['winter_wear', 'handicrafts', 'tourist_items'],
                'festival_importance': ['diwali', 'holi', 'summer_festival'],
                'climate': 'temperate',
                'economic_zone': 'tier3'
            },
            # South India
            'mysore': {
                'state': 'Karnataka',
                'region': 'karnataka',
                'population': 920550,
                'avg_income': 320000,
                'shopping_preferences': ['ethnic_wear', 'handicrafts', 'traditional_items'],
                'festival_importance': ['diwali', 'dussehra', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'mangalore': {
                'state': 'Karnataka',
                'region': 'karnataka',
                'population': 623841,
                'avg_income': 300000,
                'shopping_preferences': ['ethnic_wear', 'seafood', 'traditional_items'],
                'festival_importance': ['diwali', 'ganesh_chaturthi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'madurai': {
                'state': 'Tamil Nadu',
                'region': 'tamil_nadu',
                'population': 1017865,
                'avg_income': 250000,
                'shopping_preferences': ['traditional_wear', 'religious_items', 'handicrafts'],
                'festival_importance': ['diwali', 'pongal', 'meenakshi_festival'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'coimbatore': {
                'state': 'Tamil Nadu',
                'region': 'tamil_nadu',
                'population': 1050721,
                'avg_income': 320000,
                'shopping_preferences': ['western_wear', 'textiles', 'electronics'],
                'festival_importance': ['diwali', 'pongal', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'visakhapatnam': {
                'state': 'Andhra Pradesh',
                'region': 'andhra_pradesh',
                'population': 2035922,
                'avg_income': 280000,
                'shopping_preferences': ['ethnic_wear', 'seafood', 'traditional_items'],
                'festival_importance': ['diwali', 'ganesh_chaturthi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'vijayawada': {
                'state': 'Andhra Pradesh',
                'region': 'andhra_pradesh',
                'population': 1034358,
                'avg_income': 250000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'textiles'],
                'festival_importance': ['diwali', 'ganesh_chaturthi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'kochi': {
                'state': 'Kerala',
                'region': 'kerala',
                'population': 677381,
                'avg_income': 350000,
                'shopping_preferences': ['ethnic_wear', 'spices', 'traditional_items'],
                'festival_importance': ['diwali', 'onam', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'thiruvananthapuram': {
                'state': 'Kerala',
                'region': 'kerala',
                'population': 743691,
                'avg_income': 320000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'onam', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'calicut': {
                'state': 'Kerala',
                'region': 'kerala',
                'population': 431560,
                'avg_income': 300000,
                'shopping_preferences': ['ethnic_wear', 'spices', 'traditional_items'],
                'festival_importance': ['diwali', 'onam', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            # East India
            'howrah': {
                'state': 'West Bengal',
                'region': 'west_bengal',
                'population': 1077075,
                'avg_income': 220000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'industrial_goods'],
                'festival_importance': ['diwali', 'durga_puja', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'durgapur': {
                'state': 'West Bengal',
                'region': 'west_bengal',
                'population': 566517,
                'avg_income': 280000,
                'shopping_preferences': ['western_wear', 'industrial_goods', 'electronics'],
                'festival_importance': ['diwali', 'durga_puja', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'asansol': {
                'state': 'West Bengal',
                'region': 'west_bengal',
                'population': 563917,
                'avg_income': 250000,
                'shopping_preferences': ['western_wear', 'industrial_goods', 'traditional_items'],
                'festival_importance': ['diwali', 'durga_puja', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'siliguri': {
                'state': 'West Bengal',
                'region': 'west_bengal',
                'population': 513264,
                'avg_income': 220000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'tea_products'],
                'festival_importance': ['diwali', 'durga_puja', 'christmas'],
                'climate': 'temperate',
                'economic_zone': 'tier2'
            },
            'bhubaneswar': {
                'state': 'Odisha',
                'region': 'odisha',
                'population': 837737,
                'avg_income': 280000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'rath_yatra', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'cuttack': {
                'state': 'Odisha',
                'region': 'odisha',
                'population': 606007,
                'avg_income': 220000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'rath_yatra', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'guwahati': {
                'state': 'Assam',
                'region': 'assam',
                'population': 957352,
                'avg_income': 250000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'tea_products'],
                'festival_importance': ['diwali', 'bihu', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'silchar': {
                'state': 'Assam',
                'region': 'assam',
                'population': 172709,
                'avg_income': 200000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'tea_products'],
                'festival_importance': ['diwali', 'bihu', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier3'
            },
            'dibrugarh': {
                'state': 'Assam',
                'region': 'assam',
                'population': 154019,
                'avg_income': 220000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'tea_products'],
                'festival_importance': ['diwali', 'bihu', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier3'
            },
            # West India
            'vadodara': {
                'state': 'Gujarat',
                'region': 'gujarat',
                'population': 1670806,
                'avg_income': 350000,
                'shopping_preferences': ['ethnic_wear', 'textiles', 'jewelry'],
                'festival_importance': ['diwali', 'holi', 'navratri'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'rajkot': {
                'state': 'Gujarat',
                'region': 'gujarat',
                'population': 1286678,
                'avg_income': 320000,
                'shopping_preferences': ['ethnic_wear', 'textiles', 'traditional_items'],
                'festival_importance': ['diwali', 'holi', 'navratri'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'bhavnagar': {
                'state': 'Gujarat',
                'region': 'gujarat',
                'population': 593768,
                'avg_income': 280000,
                'shopping_preferences': ['ethnic_wear', 'textiles', 'traditional_items'],
                'festival_importance': ['diwali', 'holi', 'navratri'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'nashik': {
                'state': 'Maharashtra',
                'region': 'maharashtra',
                'population': 1486053,
                'avg_income': 320000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'wine_products'],
                'festival_importance': ['diwali', 'ganesh_chaturthi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'nagpur': {
                'state': 'Maharashtra',
                'region': 'maharashtra',
                'population': 2405665,
                'avg_income': 300000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'oranges'],
                'festival_importance': ['diwali', 'ganesh_chaturthi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'thane': {
                'state': 'Maharashtra',
                'region': 'maharashtra',
                'population': 1841488,
                'avg_income': 400000,
                'shopping_preferences': ['western_wear', 'electronics', 'lifestyle'],
                'festival_importance': ['diwali', 'ganesh_chaturthi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier1'
            },
            'aurangabad': {
                'state': 'Maharashtra',
                'region': 'maharashtra',
                'population': 1175116,
                'avg_income': 280000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'tourist_items'],
                'festival_importance': ['diwali', 'ganesh_chaturthi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'panaji': {
                'state': 'Goa',
                'region': 'goa',
                'population': 114405,
                'avg_income': 350000,
                'shopping_preferences': ['western_wear', 'tourist_items', 'seafood'],
                'festival_importance': ['diwali', 'christmas', 'carnival'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            # Central India
            'bhopal': {
                'state': 'Madhya Pradesh',
                'region': 'madhya_pradesh',
                'population': 1798218,
                'avg_income': 280000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'holi', 'christmas'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'indore': {
                'state': 'Madhya Pradesh',
                'region': 'madhya_pradesh',
                'population': 1994397,
                'avg_income': 320000,
                'shopping_preferences': ['western_wear', 'electronics', 'traditional_items'],
                'festival_importance': ['diwali', 'holi', 'christmas'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'jabalpur': {
                'state': 'Madhya Pradesh',
                'region': 'madhya_pradesh',
                'population': 1055525,
                'avg_income': 250000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'holi', 'christmas'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'gwalior': {
                'state': 'Madhya Pradesh',
                'region': 'madhya_pradesh',
                'population': 1068826,
                'avg_income': 250000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'holi', 'christmas'],
                'climate': 'semi_arid',
                'economic_zone': 'tier2'
            },
            'raipur': {
                'state': 'Chhattisgarh',
                'region': 'chhattisgarh',
                'population': 1010087,
                'avg_income': 250000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'holi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'bhilai': {
                'state': 'Chhattisgarh',
                'region': 'chhattisgarh',
                'population': 625138,
                'avg_income': 280000,
                'shopping_preferences': ['western_wear', 'industrial_goods', 'traditional_items'],
                'festival_importance': ['diwali', 'holi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier2'
            },
            'bilaspur': {
                'state': 'Chhattisgarh',
                'region': 'chhattisgarh',
                'population': 330106,
                'avg_income': 220000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'rice_products'],
                'festival_importance': ['diwali', 'holi', 'christmas'],
                'climate': 'tropical',
                'economic_zone': 'tier3'
            },
            # North East
            'imphal': {
                'state': 'Manipur',
                'region': 'north_east',
                'population': 264986,
                'avg_income': 200000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'christmas', 'sangai_festival'],
                'climate': 'temperate',
                'economic_zone': 'tier3'
            },
            'aizawl': {
                'state': 'Mizoram',
                'region': 'north_east',
                'population': 293416,
                'avg_income': 220000,
                'shopping_preferences': ['western_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'christmas', 'chapchar_kut'],
                'climate': 'temperate',
                'economic_zone': 'tier3'
            },
            'shillong': {
                'state': 'Meghalaya',
                'region': 'north_east',
                'population': 143229,
                'avg_income': 250000,
                'shopping_preferences': ['western_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'christmas', 'wangala_festival'],
                'climate': 'temperate',
                'economic_zone': 'tier3'
            },
            'kohima': {
                'state': 'Nagaland',
                'region': 'north_east',
                'population': 99039,
                'avg_income': 220000,
                'shopping_preferences': ['western_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'christmas', 'hornbill_festival'],
                'climate': 'temperate',
                'economic_zone': 'tier3'
            },
            'itanagar': {
                'state': 'Arunachal Pradesh',
                'region': 'north_east',
                'population': 59490,
                'avg_income': 200000,
                'shopping_preferences': ['western_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'christmas', 'losar_festival'],
                'climate': 'temperate',
                'economic_zone': 'tier3'
            },
            'agartala': {
                'state': 'Tripura',
                'region': 'north_east',
                'population': 399688,
                'avg_income': 200000,
                'shopping_preferences': ['ethnic_wear', 'traditional_items', 'handicrafts'],
                'festival_importance': ['diwali', 'christmas', 'kharchi_festival'],
                'climate': 'tropical',
                'economic_zone': 'tier3'
            },
            'gangtok': {
                'state': 'Sikkim',
                'region': 'north_east',
                'population': 100286,
                'avg_income': 250000,
                'shopping_preferences': ['western_wear', 'traditional_items', 'tourist_items'],
                'festival_importance': ['diwali', 'christmas', 'losar_festival'],
                'climate': 'temperate',
                'economic_zone': 'tier3'
            }
        }
        
        # Regional economic data
        self.regional_data = {
            'maharashtra': {
                'gdp_per_capita': 180000,
                'consumer_spending': 'high',
                'festival_culture': 'strong',
                'shopping_seasons': ['diwali', 'ganesh_chaturthi', 'christmas', 'wedding_season']
            },
            'north_india': {
                'gdp_per_capita': 160000,
                'consumer_spending': 'high',
                'festival_culture': 'very_strong',
                'shopping_seasons': ['diwali', 'holi', 'rakhi', 'christmas']
            },
            'karnataka': {
                'gdp_per_capita': 170000,
                'consumer_spending': 'high',
                'festival_culture': 'moderate',
                'shopping_seasons': ['diwali', 'ganesh_chaturthi', 'christmas']
            },
            'tamil_nadu': {
                'gdp_per_capita': 150000,
                'consumer_spending': 'moderate',
                'festival_culture': 'strong',
                'shopping_seasons': ['diwali', 'pongal', 'christmas']
            },
            'west_bengal': {
                'gdp_per_capita': 120000,
                'consumer_spending': 'moderate',
                'festival_culture': 'very_strong',
                'shopping_seasons': ['diwali', 'durga_puja', 'christmas']
            },
            'andhra_pradesh': {
                'gdp_per_capita': 140000,
                'consumer_spending': 'moderate',
                'festival_culture': 'strong',
                'shopping_seasons': ['diwali', 'ganesh_chaturthi', 'eid']
            },
            'gujarat': {
                'gdp_per_capita': 160000,
                'consumer_spending': 'high',
                'festival_culture': 'strong',
                'shopping_seasons': ['diwali', 'holi', 'navratri']
            },
            'bihar': {
                'gdp_per_capita': 80000,
                'consumer_spending': 'low',
                'festival_culture': 'very_strong',
                'shopping_seasons': ['diwali', 'holi', 'chhath_puja']
            },
            'odisha': {
                'gdp_per_capita': 110000,
                'consumer_spending': 'moderate',
                'festival_culture': 'strong',
                'shopping_seasons': ['diwali', 'rath_yatra', 'christmas']
            },
            'assam': {
                'gdp_per_capita': 100000,
                'consumer_spending': 'moderate',
                'festival_culture': 'strong',
                'shopping_seasons': ['diwali', 'bihu', 'christmas']
            },
            'kerala': {
                'gdp_per_capita': 140000,
                'consumer_spending': 'high',
                'festival_culture': 'strong',
                'shopping_seasons': ['diwali', 'onam', 'christmas']
            },
            'goa': {
                'gdp_per_capita': 180000,
                'consumer_spending': 'high',
                'festival_culture': 'moderate',
                'shopping_seasons': ['diwali', 'christmas', 'carnival']
            },
            'madhya_pradesh': {
                'gdp_per_capita': 100000,
                'consumer_spending': 'moderate',
                'festival_culture': 'strong',
                'shopping_seasons': ['diwali', 'holi', 'christmas']
            },
            'chhattisgarh': {
                'gdp_per_capita': 90000,
                'consumer_spending': 'low',
                'festival_culture': 'strong',
                'shopping_seasons': ['diwali', 'holi', 'christmas']
            },
            'north_east': {
                'gdp_per_capita': 120000,
                'consumer_spending': 'moderate',
                'festival_culture': 'strong',
                'shopping_seasons': ['diwali', 'christmas', 'local_festivals']
            }
        }
    
    def get_location_info(self, location_name):
        """
        Get comprehensive location information
        
        Args:
            location_name (str): City name
            
        Returns:
            dict: Location information
        """
        location_name = location_name.lower().strip()
        
        # Get basic city data
        city_data = self.indian_cities.get(location_name, self._get_default_city_data())
        
        # Get regional data
        region = city_data['region']
        regional_data = self.regional_data.get(region, {})
        
        # Combine city and regional data
        location_info = {
            'city': location_name.title(),
            'state': city_data['state'],
            'region': region,
            'population': city_data['population'],
            'avg_income': city_data['avg_income'],
            'economic_zone': city_data['economic_zone'],
            'climate': city_data['climate'],
            'shopping_preferences': city_data['shopping_preferences'],
            'festival_importance': city_data['festival_importance'],
            'regional_gdp': regional_data.get('gdp_per_capita', 150000),
            'consumer_spending': regional_data.get('consumer_spending', 'moderate'),
            'festival_culture': regional_data.get('festival_culture', 'moderate'),
            'shopping_seasons': regional_data.get('shopping_seasons', ['diwali', 'christmas'])
        }
        
        # Add calculated insights
        location_info.update(self._calculate_location_insights(location_info))
        
        return location_info
    
    def _get_default_city_data(self):
        """Get default city data for unknown locations"""
        return {
            'state': 'Unknown',
            'region': 'all_india',
            'population': 1000000,
            'avg_income': 300000,
            'shopping_preferences': ['general_items'],
            'festival_importance': ['diwali', 'christmas'],
            'climate': 'tropical',
            'economic_zone': 'tier2'
        }
    
    def _calculate_location_insights(self, location_info):
        """Calculate additional insights based on location data"""
        insights = {}
        
        # Spending power index
        income = location_info['avg_income']
        if income >= 450000:
            spending_power = 'high'
        elif income >= 350000:
            spending_power = 'moderate'
        else:
            spending_power = 'low'
        
        insights['spending_power'] = spending_power
        
        # Festival shopping potential
        festival_culture = location_info['festival_culture']
        if festival_culture == 'very_strong':
            festival_potential = 'very_high'
        elif festival_culture == 'strong':
            festival_potential = 'high'
        else:
            festival_potential = 'moderate'
        
        insights['festival_shopping_potential'] = festival_potential
        
        # Seasonal discount effectiveness
        climate = location_info['climate']
        if climate == 'tropical':
            seasonal_impact = 'moderate'
        elif climate == 'semi_arid':
            seasonal_impact = 'high'
        else:
            seasonal_impact = 'low'
        
        insights['seasonal_discount_effectiveness'] = seasonal_impact
        
        # Market maturity
        economic_zone = location_info['economic_zone']
        if economic_zone == 'metro':
            market_maturity = 'mature'
        elif economic_zone == 'tier1':
            market_maturity = 'developing'
        else:
            market_maturity = 'emerging'
        
        insights['market_maturity'] = market_maturity
        
        return insights
    
    def get_nearby_cities(self, location_name, radius_km=100):
        """
        Get nearby cities within specified radius
        
        Args:
            location_name (str): Base city name
            radius_km (int): Search radius in kilometers
            
        Returns:
            list: Nearby cities with distance information
        """
        try:
            # Get coordinates of base city
            base_location = self.geolocator.geocode(f"{location_name}, India")
            if not base_location:
                return []
            
            base_coords = (base_location.latitude, base_location.longitude)
            
            nearby_cities = []
            
            for city_name, city_data in self.indian_cities.items():
                if city_name == location_name.lower():
                    continue
                
                # Get coordinates for comparison city
                try:
                    comp_location = self.geolocator.geocode(f"{city_name}, India")
                    if comp_location:
                        comp_coords = (comp_location.latitude, comp_location.longitude)
                        distance = geodesic(base_coords, comp_coords).kilometers
                        
                        if distance <= radius_km:
                            nearby_cities.append({
                                'city': city_name.title(),
                                'distance_km': round(distance, 1),
                                'region': city_data['region'],
                                'population': city_data['population']
                            })
                        
                        # Rate limiting to avoid API issues
                        time.sleep(0.1)
                        
                except Exception:
                    continue
            
            # Sort by distance
            nearby_cities.sort(key=lambda x: x['distance_km'])
            
            return nearby_cities[:10]  # Return top 10 nearby cities
            
        except Exception as e:
            print(f"Error getting nearby cities: {e}")
            return []
    
    def get_regional_market_insights(self, region):
        """
        Get market insights for a specific region
        
        Args:
            region (str): Region name
            
        Returns:
            dict: Regional market insights
        """
        regional_data = self.regional_data.get(region, {})
        
        insights = {
            'region': region,
            'market_size': self._estimate_market_size(region),
            'consumer_behavior': self._analyze_consumer_behavior(region),
            'competitive_landscape': self._analyze_competition(region),
            'opportunity_areas': self._identify_opportunities(region)
        }
        
        return insights
    
    def _estimate_market_size(self, region):
        """Estimate market size for region"""
        # This would typically come from market research data
        # For demo purposes, using simplified estimates
        
        market_sizes = {
            'maharashtra': 'large',
            'north_india': 'very_large',
            'karnataka': 'large',
            'tamil_nadu': 'medium',
            'west_bengal': 'medium',
            'andhra_pradesh': 'medium',
            'gujarat': 'large'
        }
        
        return market_sizes.get(region, 'medium')
    
    def _analyze_consumer_behavior(self, region):
        """Analyze consumer behavior patterns for region"""
        behaviors = {
            'maharashtra': {
                'price_sensitivity': 'moderate',
                'brand_consciousness': 'high',
                'online_shopping': 'high',
                'festival_spending': 'high'
            },
            'north_india': {
                'price_sensitivity': 'low',
                'brand_consciousness': 'very_high',
                'online_shopping': 'high',
                'festival_spending': 'very_high'
            },
            'karnataka': {
                'price_sensitivity': 'moderate',
                'brand_consciousness': 'high',
                'online_shopping': 'very_high',
                'festival_spending': 'moderate'
            }
        }
        
        return behaviors.get(region, {
            'price_sensitivity': 'moderate',
            'brand_consciousness': 'moderate',
            'online_shopping': 'moderate',
            'festival_spending': 'moderate'
        })
    
    def _analyze_competition(self, region):
        """Analyze competitive landscape for region"""
        competition_levels = {
            'maharashtra': 'high',
            'north_india': 'very_high',
            'karnataka': 'high',
            'tamil_nadu': 'moderate',
            'west_bengal': 'moderate',
            'andhra_pradesh': 'moderate',
            'gujarat': 'high'
        }
        
        return {
            'competition_level': competition_levels.get(region, 'moderate'),
            'key_competitors': self._get_key_competitors(region),
            'market_gaps': self._identify_market_gaps(region)
        }
    
    def _get_key_competitors(self, region):
        """Get key competitors for region"""
        # This would typically come from market research
        return ['Local Retailers', 'E-commerce Platforms', 'Regional Chains']
    
    def _identify_market_gaps(self, region):
        """Identify market gaps and opportunities"""
        gaps = {
            'maharashtra': ['Premium Ethnic Wear', 'Tech Accessories', 'Home Decor'],
            'north_india': ['Western Fashion', 'Electronics', 'Luxury Items'],
            'karnataka': ['Traditional Items', 'Festival Collections', 'Gift Items']
        }
        
        return gaps.get(region, ['General Items'])
    
    def _identify_opportunities(self, region):
        """Identify business opportunities for region"""
        opportunities = {
            'maharashtra': ['Festival Bundles', 'Tech + Fashion Combos', 'Premium Collections'],
            'north_india': ['Wedding Collections', 'Festival Specials', 'Luxury Bundles'],
            'karnataka': ['Traditional + Modern Mix', 'Tech Accessories', 'Festival Items']
        }
        
        return opportunities.get(region, ['General Promotions']) 