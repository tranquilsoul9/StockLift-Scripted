import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json

class FestivalPromotionEngine:
    """
    Festival-Cultural Promotion Engine that maps unsold inventory to upcoming
    regional festivals and recommends culturally relevant promotions
    """
    
    def __init__(self):
        # Indian festivals database (in real implementation, this would come from APIs)
        self.festivals_db = self._load_festivals_database()
        
        # Comprehensive Product-Festival Mapping for Dead Stock Sales
        self.product_festival_mapping = {
            'shirt': {
                'diwali': 'Festive gifting, men\'s wear, party outfits, family looks',
                'rakhi': 'Festive gifting, men\'s wear, party outfits, family looks',
                'eid': 'Festive gifting, men\'s wear, party outfits, family looks',
                'new_year': 'Festive gifting, men\'s wear, party outfits, family looks',
                'friendship_day': 'Festive gifting, men\'s wear, party outfits, family looks'
            },
            'kurti': {
                'rakhi': 'Women\'s festive/casual, ethnic day, gifting',
                'navratri': 'Women\'s festive/casual, ethnic day, gifting',
                'eid': 'Women\'s festive/casual, ethnic day, gifting',
                'diwali': 'Women\'s festive/casual, ethnic day, gifting',
                'teej': 'Women\'s festive/casual, ethnic day, gifting'
            },
            'jeans': {
                'new_year': 'Youth casuals, western day, outings, gifts',
                'christmas': 'Youth casuals, western day, outings, gifts',
                'college_fest': 'Youth casuals, western day, outings, gifts',
                'friendship_day': 'Youth casuals, western day, outings, gifts',
                'valentines_day': 'Youth casuals, western day, outings, gifts'
            },
            'jacket': {
                'christmas': 'Winter season, back to school, party looks',
                'new_year': 'Winter season, back to school, party looks',
                'lohri': 'Winter season, back to school, party looks',
                'makar_sankranti': 'Winter season, back to school, party looks',
                'winter_reopening': 'Winter season, back to school, party looks'
            },
            'dress': {
                'new_year': 'Girls\' party, outings, fusion/western themes',
                'christmas': 'Girls\' party, outings, fusion/western themes',
                'valentines_day': 'Girls\' party, outings, fusion/western themes',
                'birthday_parties': 'Girls\' party, outings, fusion/western themes'
            },
            't_shirts': {
                'friendship_day': 'Group gifting, casual, college/school, summer',
                'college_fest': 'Group gifting, casual, college/school, summer',
                'new_year': 'Group gifting, casual, college/school, summer',
                'sports_events': 'Group gifting, casual, college/school, summer',
                'summer_sales': 'Group gifting, casual, college/school, summer'
            },
            'jeggings': {
                'college_fest': 'Trendy, fusion with ethnic tops, youth, teens',
                'new_year': 'Trendy, fusion with ethnic tops, youth, teens',
                'navratri': 'Trendy, fusion with ethnic tops, youth, teens',
                'diwali': 'Trendy, fusion with ethnic tops, youth, teens'
            },
            'heels': {
                'diwali': 'Party/festive, dance nights, wedding outfits',
                'navratri': 'Party/festive, dance nights, wedding outfits',
                'weddings': 'Party/festive, dance nights, wedding outfits',
                'new_year': 'Party/festive, dance nights, wedding outfits',
                'college_farewells': 'Party/festive, dance nights, wedding outfits'
            },
            'sneakers': {
                'college_fest': 'Outdoor/casual, college fashion, group outings',
                'sports_events': 'Outdoor/casual, college fashion, group outings',
                'friendship_day': 'Outdoor/casual, college fashion, group outings',
                'summer_sales': 'Outdoor/casual, college fashion, group outings',
                'monsoon_sales': 'Outdoor/casual, college fashion, group outings'
            },
            'saree': {
                'durga_puja': 'Festive, regional festivals, ethnic gifting, wedding season',
                'diwali': 'Festive, regional festivals, ethnic gifting, wedding season',
                'karva_chauth': 'Festive, regional festivals, ethnic gifting, wedding season',
                'pongal': 'Festive, regional festivals, ethnic gifting, wedding season',
                'onam': 'Festive, regional festivals, ethnic gifting, wedding season',
                'teej': 'Festive, regional festivals, ethnic gifting, wedding season'
            },
            'salwar_suit': {
                'eid': 'Festive, North Indian traditions, gifting',
                'lohri': 'Festive, North Indian traditions, gifting',
                'diwali': 'Festive, North Indian traditions, gifting',
                'rakhi': 'Festive, North Indian traditions, gifting'
            },
            'leggings': {
                'navratri': 'Pair with kurtis, trendy combos, school/college',
                'diwali': 'Pair with kurtis, trendy combos, school/college',
                'college_fest': 'Pair with kurtis, trendy combos, school/college',
                'rakhi': 'Pair with kurtis, trendy combos, school/college'
            },
            'dupatta': {
                'navratri': 'Pair with ethnic sets, gifts, trending accessory',
                'diwali': 'Pair with ethnic sets, gifts, trending accessory',
                'teej': 'Pair with ethnic sets, gifts, trending accessory',
                'karva_chauth': 'Pair with ethnic sets, gifts, trending accessory'
            },
            'choli': {
                'navratri': 'Essential for saree/lehengas, dance nights, wedding trousseau',
                'diwali': 'Essential for saree/lehengas, dance nights, wedding trousseau',
                'durga_puja': 'Essential for saree/lehengas, dance nights, wedding trousseau',
                'wedding_season': 'Essential for saree/lehengas, dance nights, wedding trousseau'
            },
            'palazzo_pants': {
                'eid': 'Trendy pairings, comfort fashion, Indo-western look',
                'diwali': 'Trendy pairings, comfort fashion, Indo-western look',
                'rakhi': 'Trendy pairings, comfort fashion, Indo-western look',
                'office_parties': 'Trendy pairings, comfort fashion, Indo-western look'
            },
            'lehenga': {
                'navratri': 'Garba/dandiya, weddings, festive combos',
                'diwali': 'Garba/dandiya, weddings, festive combos',
                'wedding_season': 'Garba/dandiya, weddings, festive combos',
                'karva_chauth': 'Garba/dandiya, weddings, festive combos'
            },
            'night_suit': {
                'christmas': 'Gifting, cozy season, back to school/college',
                'new_year': 'Gifting, cozy season, back to school/college',
                'winter': 'Gifting, cozy season, back to school/college',
                'summer_sales': 'Gifting, cozy season, back to school/college'
            },
            'sweater': {
                'christmas': 'Winter essentials, holiday gifts',
                'lohri': 'Winter essentials, holiday gifts',
                'new_year': 'Winter essentials, holiday gifts',
                'winter_sales': 'Winter essentials, holiday gifts'
            },
            'sling_bag': {
                'college_fest': 'Youth/teen accessory, gifting, casual look',
                'friendship_day': 'Youth/teen accessory, gifting, casual look',
                'valentines_day': 'Youth/teen accessory, gifting, casual look',
                'rakhi': 'Youth/teen accessory, gifting, casual look'
            },
            'handbag': {
                'diwali': 'Gifting, festive must-have, trendy looks',
                'rakhi': 'Gifting, festive must-have, trendy looks',
                'eid': 'Gifting, festive must-have, trendy looks',
                'mothers_day': 'Gifting, festive must-have, trendy looks'
            },
            'watch': {
                'new_year': 'Gift for men/women, style upgrade',
                'diwali': 'Gift for men/women, style upgrade',
                'valentines_day': 'Gift for men/women, style upgrade',
                'rakhi': 'Gift for men/women, style upgrade'
            },
            'earrings': {
                'navratri': 'Ethnic wear, party look, matching with kurtis/lehengas',
                'diwali': 'Ethnic wear, party look, matching with kurtis/lehengas',
                'karva_chauth': 'Ethnic wear, party look, matching with kurtis/lehengas',
                'teej': 'Ethnic wear, party look, matching with kurtis/lehengas',
                'rakhi': 'Ethnic wear, party look, matching with kurtis/lehengas'
            },
            'necklace_set': {
                'weddings': 'Bridal/festive, party combos',
                'diwali': 'Bridal/festive, party combos',
                'navratri': 'Bridal/festive, party combos',
                'karva_chauth': 'Bridal/festive, party combos'
            },
            'bangles': {
                'navratri': 'Essential ethnic accessory, gifting',
                'diwali': 'Essential ethnic accessory, gifting',
                'karva_chauth': 'Essential ethnic accessory, gifting',
                'teej': 'Essential ethnic accessory, gifting',
                'rakhi': 'Essential ethnic accessory, gifting'
            },
            'anklet': {
                'teej': 'Ethnic foot accessory, dance, festive wear',
                'karva_chauth': 'Ethnic foot accessory, dance, festive wear',
                'weddings': 'Ethnic foot accessory, dance, festive wear',
                'navratri': 'Ethnic foot accessory, dance, festive wear'
            },
            'hair_accessories': {
                'rakhi': 'Girls\'/women\'s party, ethnic styling, gifting',
                'navratri': 'Girls\'/women\'s party, ethnic styling, gifting',
                'new_year': 'Girls\'/women\'s party, ethnic styling, gifting',
                'college_fest': 'Girls\'/women\'s party, ethnic styling, gifting'
            },
            'kids_dress': {
                'childrens_day': 'Party wear, gifting, festive/seasonal demand',
                'christmas': 'Party wear, gifting, festive/seasonal demand',
                'new_year': 'Party wear, gifting, festive/seasonal demand',
                'birthday_parties': 'Party wear, gifting, festive/seasonal demand',
                'diwali': 'Party wear, gifting, festive/seasonal demand'
            },
            'boys_shirt': {
                'childrens_day': 'Boys\' festive/casual, gifting',
                'diwali': 'Boys\' festive/casual, gifting',
                'new_year': 'Boys\' festive/casual, gifting',
                'rakhi': 'Boys\' festive/casual, gifting'
            },
            'sportswear': {
                'college_fest': 'Sports day, outdoor, activewear demand',
                'sports_events': 'Sports day, outdoor, activewear demand',
                'summer_sales': 'Sports day, outdoor, activewear demand',
                'new_year': 'Sports day, outdoor, activewear demand'
            },
            'saree_shapewear': {
                'durga_puja': 'Essential for saree sales, wedding/festive season',
                'diwali': 'Essential for saree sales, wedding/festive season',
                'wedding_season': 'Essential for saree sales, wedding/festive season',
                'navratri': 'Essential for saree sales, wedding/festive season'
            },
            'blazer': {
                'new_year': 'Party, office, formal outings, winter',
                'christmas': 'Party, office, formal outings, winter',
                'winter_weddings': 'Party, office, formal outings, winter',
                'business_events': 'Party, office, formal outings, winter'
            },
            'scarf': {
                'winter_festivals': 'Pair with western/ethnic, gifting, layering',
                'diwali': 'Pair with western/ethnic, gifting, layering',
                'christmas': 'Pair with western/ethnic, gifting, layering',
                'makar_sankranti': 'Pair with western/ethnic, gifting, layering'
            },
            'tote_bag': {
                'college_fest': 'Trendy, utility, gifting',
                'summer_sales': 'Trendy, utility, gifting',
                'office_parties': 'Trendy, utility, gifting',
                'diwali': 'Trendy, utility, gifting'
            },
            'formal_shoes': {
                'new_year': 'Men\'s festive/office party look',
                'diwali': 'Men\'s festive/office party look',
                'college_farewells': 'Men\'s festive/office party look',
                'office_festivities': 'Men\'s festive/office party look'
            },
            'sandals': {
                'summer_sales': 'Casual, festive, gifting',
                'diwali': 'Casual, festive, gifting',
                'rakhi': 'Casual, festive, gifting',
                'teej': 'Casual, festive, gifting'
            },
            'dupatta_set': {
                'navratri': 'Combo offers with kurtis/suits, gifting',
                'diwali': 'Combo offers with kurtis/suits, gifting',
                'rakhi': 'Combo offers with kurtis/suits, gifting',
                'teej': 'Combo offers with kurtis/suits, gifting'
            },
            
            # National Festival Mappings
            'tricolor_clothing': {
                'independence_day': 'Patriotic wear, national pride, flag colors',
                'republic_day': 'Patriotic wear, national pride, flag colors',
                'gandhi_jayanti': 'Khadi wear, simple clothing, traditional'
            },
            'gift_items': {
                'mothers_day': 'Gifts for mothers, flowers, jewelry, spa items',
                'fathers_day': 'Gifts for fathers, watches, accessories, gadgets',
                'daughters_day': 'Gifts for daughters, toys, dresses, accessories',
                'childrens_day': 'Gifts for children, toys, books, educational items',
                'teachers_day': 'Gifts for teachers, books, stationery, respect items',
                'friendship_day': 'Friendship bands, gifts, cards, accessories',
                'rakhi': 'Rakhi sets, gifts for brothers, sweets, family items'
            },
            'jewelry': {
                'mothers_day': 'Jewelry for mothers, traditional pieces',
                'daughters_day': 'Jewelry for daughters, trendy pieces',
                'karwa_chauth': 'Traditional jewelry, mehendi items',
                'diwali': 'Festive jewelry, traditional pieces',
                'weddings': 'Bridal jewelry, traditional sets'
            },
            'watches': {
                'fathers_day': 'Watches for fathers, premium timepieces',
                'christmas': 'Christmas gifts, luxury items'
            },
            'flowers': {
                'mothers_day': 'Flowers for mothers, bouquets, arrangements',
                'friendship_day': 'Friendship flowers, colorful arrangements'
            },
            'chocolates': {
                'mothers_day': 'Gift chocolates, premium boxes',
                'fathers_day': 'Premium chocolates, gift items',
                'christmas': 'Christmas chocolates, festive boxes'
            },
            'toys': {
                'childrens_day': 'Educational toys, fun items, games',
                'daughters_day': 'Girls toys, dolls, accessories',
                'christmas': 'Christmas toys, festive items'
            },
            'books': {
                'teachers_day': 'Books for teachers, educational materials',
                'childrens_day': 'Educational books, story books',
                'fathers_day': 'Books for fathers, hobby books'
            },
            'stationery': {
                'teachers_day': 'Stationery for teachers, premium items',
                'childrens_day': 'Educational stationery, school items'
            },
            'decorations': {
                'independence_day': 'Tricolor decorations, flag items',
                'diwali': 'Diwali decorations, lights, rangoli items',
                'christmas': 'Christmas decorations, tree ornaments'
            },
            'traditional_clothing': {
                'independence_day': 'Khadi clothing, traditional wear',
                'gandhi_jayanti': 'Khadi clothing, simple traditional wear',
                'diwali': 'Traditional festive wear, ethnic clothing',
                'holi': 'White traditional clothes, colorful items',
                'rakhi': 'Traditional family wear, ethnic clothing'
            },
            'western_clothing': {
                'christmas': 'Party western wear, festive clothing',
                'friendship_day': 'Casual western wear, trendy clothing'
            },
            'accessories': {
                'mothers_day': 'Accessories for mothers, bags, scarves',
                'fathers_day': 'Accessories for fathers, belts, wallets',
                'daughters_day': 'Accessories for daughters, hair items',
                'friendship_day': 'Friendship accessories, trendy items'
            },
            'bags': {
                'mothers_day': 'Bags for mothers, handbags, totes',
                'daughters_day': 'Bags for daughters, school bags, trendy bags'
            },
            'perfumes': {
                'mothers_day': 'Perfumes for mothers, luxury fragrances',
                'fathers_day': 'Perfumes for fathers, masculine fragrances',
                'christmas': 'Christmas perfumes, festive fragrances'
            },
            'cosmetics': {
                'mothers_day': 'Cosmetics for mothers, beauty items',
                'daughters_day': 'Cosmetics for daughters, trendy beauty items',
                'karwa_chauth': 'Mehendi items, traditional cosmetics'
            },
            'electronics': {
                'fathers_day': 'Electronics for fathers, gadgets, tech items',
                'christmas': 'Christmas electronics, tech gifts'
            },
            'home_decor': {
                'mothers_day': 'Home decor for mothers, decorative items',
                'diwali': 'Diwali home decor, traditional items',
                'christmas': 'Christmas home decor, festive items'
            },
            'kitchen_items': {
                'mothers_day': 'Kitchen items for mothers, cooking utensils',
                'diwali': 'Diwali kitchen items, traditional utensils',
                'christmas': 'Christmas kitchen items, festive utensils'
            },
            'sports_items': {
                'fathers_day': 'Sports items for fathers, fitness equipment',
                'childrens_day': 'Sports items for children, outdoor games'
            }
        }

    def _load_festivals_database(self):
       
        return {
            # Maharashtra
            'ganesh_chaturthi': {
                'name': 'Ganesh Chaturthi',
                'date_2025': '2025-08-27',
                'regions': ['maharashtra', 'goa', 'karnataka', 'andhra_pradesh', 'telangana'],
                'duration': 10,
                'category': 'religious',
                'shopping_period': 15,
                'description': 'Birth celebration of Lord Ganesha, Maharashtra\'s biggest festival',
            },

            'dahi_handi': {
                'name': 'Dahi Handi',
                'date_2025': '2025-08-18',
                'regions': ['maharashtra'],
                'duration': 1,
                'category': 'cultural',
                'shopping_period': 5,
                'description': 'Krishna Janmashtami celebrated with human pyramids',
            },
            'maharashtra_day': {
                'name': 'Maharashtra Day',
                'date_2025': '2025-05-01',
                'regions': ['maharashtra'],
                'duration': 1,
                'category': 'cultural',
                'shopping_period': 5,
                'description': 'Formation day of Maharashtra state',
            },

            # Gujarat
            'navratri': {
                'name': 'Navratri (Garba)',
                'date_2025': '2025-09-22',
                'regions': ['gujarat'],
                'duration': 9,
                'category': 'cultural',
                'shopping_period': 15,
                'description': 'Famous Garba and Dandiya festival of Gujarat',
            },

            'gujarat_day': {
                'name': 'Gujarat Day',
                'date_2025': '2025-05-01',
                'regions': ['gujarat'],
                'duration': 1,
                'category': 'cultural',
                'shopping_period': 5,
                'description': 'Formation day of Gujarat state',
            },
            'rath_yatra_ahmedabad': {
                'name': 'Rath Yatra (Ahmedabad)',
                'date_2025': '2025-07-07',
                'regions': ['gujarat'],
                'duration': 1,
                'category': 'religious',
                'shopping_period': 10,
                'description': 'Chariot festival of Lord Jagannath in Ahmedabad',
            },



            # Karnataka

            'karnataka_rajyotsava': {
                'name': 'Karnataka Rajyotsava',
                'date_2025': '2025-11-01',
                'regions': ['karnataka'],
                'duration': 1,
                'category': 'cultural',
                'shopping_period': 5,
                'description': 'Karnataka State Formation Day',
            },
            'mysore_dasara': {
                'name': 'Mysore Dasara',
                'date_2025': '2025-10-05',
                'regions': ['karnataka'],
                'duration': 10,
                'category': 'cultural',
                'shopping_period': 15,
                'description': 'Famous 10-day festival in Mysore',
            },

            # Mizoram


            # Rajasthan


            'marwar_festival': {
                'name': 'Marwar Festival',
                'date_2025': '2025-10-15',
                'regions': ['rajasthan'],
                'duration': 2,
                'category': 'cultural',
                'shopping_period': 10,
                'description': 'Cultural festival in Jodhpur',
            },


            # Kerala
            'onam': {
                'name': 'Onam',
                'date_2025': '2025-08-26',
                'regions': ['kerala'],
                'duration': 10,
                'category': 'harvest',
                'shopping_period': 15,
                'description': 'Harvest festival of Kerala',
            },


            # West Bengal
            'durga_puja': {
                'name': 'Durga Puja',
                'date_2025': '2025-09-28',
                'regions': ['west_bengal'],
                'duration': 5,
                'category': 'religious',
                'shopping_period': 20,
                'description': 'Worship of Goddess Durga, Bengal\'s biggest festival',
            },

            # Punjab



            'gurpurab': {
                'name': 'Gurpurab',
                'date_2025': '2025-11-15',
                'regions': ['punjab'],
                'duration': 1,
                'category': 'religious',
                'shopping_period': 10,
                'description': 'Birth anniversary of Guru Nanak Dev Ji',
            },

            # Odisha
            'rath_yatra_puri': {
                'name': 'Rath Yatra (Puri)',
                'date_2025': '2025-07-07',
                'regions': ['odisha'],
                'duration': 1,
                'category': 'religious',
                'shopping_period': 10,
                'description': 'Chariot festival of Lord Jagannath in Puri',
            },


            # Bihar
            'chhath_puja': {
                'name': 'Chhath Puja',
                'date_2025': '2025-10-27',
                'regions': ['bihar'],
                'duration': 4,
                'category': 'religious',
                'shopping_period': 10,
                'description': 'Ancient Hindu festival dedicated to Sun God',
            },

            # Sikkim



            # Haryana
            'teej': {
                'name': 'Teej',
                'date_2025': '2025-08-22',
                'regions': ['haryana', 'rajasthan'],
                'duration': 1,
                'category': 'cultural',
                'shopping_period': 10,
                'description': 'Monsoon festival celebrated by women',
            },
            'haryana_day': {
                'name': 'Haryana Day',
                'date_2025': '2025-11-01',
                'regions': ['haryana'],
                'duration': 1,
                'category': 'cultural',
                'shopping_period': 5,
                'description': 'Formation day of Haryana state',
            },

            # Tamil Nadu



            # Madhya Pradesh


            # Assam

            'ambubachi_mela': {
                'name': 'Ambubachi Mela',
                'date_2025': '2025-06-12',
                'regions': ['assam'],
                'duration': 4,
                'category': 'religious',
                'shopping_period': 15,
                'description': 'Annual fair at Kamakhya Temple in Assam',
            },

            # Andhra Pradesh



            # Telangana
            'bonalu': {
                'name': 'Bonalu',
                'date_2025': '2025-07-18',
                'regions': ['telangana'],
                'duration': 1,
                'category': 'religious',
                'shopping_period': 10,
                'description': 'Telangana state festival dedicated to Goddess Mahakali',
            },
            'bathukamma': {
                'name': 'Bathukamma',
                'date_2025': '2025-09-30',
                'regions': ['telangana'],
                'duration': 9,
                'category': 'cultural',
                'shopping_period': 15,
                'description': 'Flower festival of Telangana',
            },

            # Goa

            'sao_joao': {
                'name': 'Sao Joao',
                'date_2025': '2025-06-24',
                'regions': ['goa'],
                'duration': 1,
                'category': 'cultural',
                'shopping_period': 10,
                'description': 'Feast of St. John the Baptist in Goa',
            },

            # Himachal Pradesh
            'kullu_dussehra': {
                'name': 'Kullu Dussehra',
                'date_2025': '2025-10-05',
                'regions': ['himachal_pradesh'],
                'duration': 7,
                'category': 'cultural',
                'shopping_period': 15,
                'description': 'Dussehra celebration in Kullu Valley',
            },


            # Tripura
            'kharchi_puja': {
                'name': 'Kharchi Puja',
                'date_2025': '2025-07-15',
                'regions': ['tripura'],
                'duration': 7,
                'category': 'religious',
                'shopping_period': 10,
                'description': 'Traditional festival of Tripura, worship of fourteen deities',
            },
            'ker_puja': {
                'name': 'Ker Puja',
                'date_2025': '2025-08-20',
                'regions': ['tripura'],
                'duration': 1,
                'category': 'religious',
                'shopping_period': 5,
                'description': 'Traditional festival to ward off evil spirits',
            },

            'tripura_sundari_temple_festival': {
                'name': 'Tripura Sundari Temple Festival',
                'date_2025': '2025-10-15',
                'regions': ['tripura'],
                'duration': 5,
                'category': 'religious',
                'shopping_period': 15,
                'description': 'Annual festival at Tripura Sundari Temple',
            },

            # National Festivals and Special Days
            'independence_day': {
                'name': 'Independence Day',
                'date_2025': '2025-08-15',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'national',
                'shopping_period': 10,
                'description': 'India\'s Independence Day celebration',
                'trending_keywords': ['tricolor', 'patriotic', 'indian flag', 'freedom', 'national pride']
            },

            'gandhi_jayanti': {
                'name': 'Gandhi Jayanti',
                'date_2025': '2025-10-02',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'national',
                'shopping_period': 5,
                'description': 'Birth anniversary of Mahatma Gandhi',
                'trending_keywords': ['gandhi', 'peace', 'non-violence', 'khadi', 'freedom fighter']
            },
            'mothers_day': {
                'name': 'Mother\'s Day',
                'date_2025': '2025-05-11',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'national',
                'shopping_period': 15,
                'description': 'Celebration honoring mothers and motherhood',
                'trending_keywords': ['mother', 'mom', 'gift', 'love', 'family', 'flowers', 'jewelry']
            },
            'fathers_day': {
                'name': 'Father\'s Day',
                'date_2025': '2025-06-15',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'national',
                'shopping_period': 15,
                'description': 'Celebration honoring fathers and fatherhood',
                'trending_keywords': ['father', 'dad', 'gift', 'love', 'family', 'watches', 'accessories']
            },
            'daughters_day': {
                'name': 'Daughter\'s Day',
                'date_2025': '2025-09-28',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'national',
                'shopping_period': 10,
                'description': 'Celebration honoring daughters',
                'trending_keywords': ['daughter', 'girl', 'gift', 'love', 'family', 'dress', 'toys']
            },
            'childrens_day': {
                'name': 'Children\'s Day',
                'date_2025': '2025-11-14',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'national',
                'shopping_period': 15,
                'description': 'Birth anniversary of Jawaharlal Nehru, celebrated as Children\'s Day',
                'trending_keywords': ['children', 'kids', 'toys', 'gifts', 'education', 'fun']
            },
            'teachers_day': {
                'name': 'Teacher\'s Day',
                'date_2025': '2025-09-05',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'national',
                'shopping_period': 10,
                'description': 'Birth anniversary of Dr. Sarvepalli Radhakrishnan, celebrated as Teacher\'s Day',
                'trending_keywords': ['teacher', 'education', 'gift', 'respect', 'books', 'stationery']
            },
            'friendship_day': {
                'name': 'Friendship Day',
                'date_2025': '2025-08-03',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'national',
                'shopping_period': 10,
                'description': 'Celebration of friendship and bonds',
                'trending_keywords': ['friend', 'friendship', 'gift', 'love', 'bracelet', 'cards']
            },

            'christmas': {
                'name': 'Christmas',
                'date_2025': '2025-12-25',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'religious',
                'shopping_period': 30,
                'description': 'Christian celebration of the birth of Jesus Christ',
                'trending_keywords': ['christmas', 'gift', 'tree', 'decorations', 'santa', 'winter']
            },

            'diwali': {
                'name': 'Diwali',
                'date_2025': '2025-10-23',
                'regions': ['all_india'],
                'duration': 5,
                'category': 'religious',
                'shopping_period': 25,
                'description': 'Festival of Lights, one of India\'s biggest festivals',
                'trending_keywords': ['diwali', 'lights', 'gift', 'sweets', 'decorations', 'fireworks']
            },
            'holi': {
                'name': 'Holi',
                'date_2025': '2025-03-14',
                'regions': ['all_india'],
                'duration': 2,
                'category': 'religious',
                'shopping_period': 15,
                'description': 'Festival of Colors, celebrating spring and love',
                'trending_keywords': ['holi', 'colors', 'white clothes', 'water guns', 'sweets', 'fun']
            },
            'rakhi': {
                'name': 'Raksha Bandhan',
                'date_2025': '2025-08-03',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'national',
                'shopping_period': 15,
                'description': 'Celebration of the bond between brothers and sisters',
                'trending_keywords': ['rakhi', 'brother', 'sister', 'gift', 'love', 'family']
            },
            'karwa_chauth': {
                'name': 'Karwa Chauth',
                'date_2025': '2025-10-13',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'religious',
                'shopping_period': 15,
                'description': 'Hindu festival where married women fast for their husbands',
                'trending_keywords': ['karwa chauth', 'fasting', 'mehendi', 'sargi', 'jewelry', 'traditional']
            },
            'eid_al_fitr': {
                'name': 'Eid al-Fitr',
                'date_2025': '2025-03-31',
                'regions': ['all_india'],
                'duration': 3,
                'category': 'religious',
                'shopping_period': 20,
                'description': 'Islamic festival marking the end of Ramadan',
                'trending_keywords': ['eid', 'ramadan', 'feast', 'gift', 'traditional', 'family']
            },
            'janmashtami': {
                'name': 'Krishna Janmashtami',
                'date_2025': '2025-08-18',
                'regions': ['all_india'],
                'duration': 2,
                'category': 'religious',
                'shopping_period': 10,
                'description': 'Birth celebration of Lord Krishna',
                'trending_keywords': ['krishna', 'janmashtami', 'dahi handi', 'traditional', 'religious']
            },
            'gurpurab': {
                'name': 'Gurpurab',
                'date_2025': '2025-11-15',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'religious',
                'shopping_period': 10,
                'description': 'Birth anniversary of Guru Nanak Dev Ji',
                'trending_keywords': ['gurpurab', 'sikh', 'guru', 'traditional', 'religious']
            },
            'mahashivratri': {
                'name': 'Maha Shivratri',
                'date_2025': '2025-02-26',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'religious',
                'shopping_period': 10,
                'description': 'Great night of Lord Shiva',
                'trending_keywords': ['shiva', 'shivratri', 'bilva', 'traditional', 'religious']
            },
            'ram_navami': {
                'name': 'Ram Navami',
                'date_2025': '2025-04-06',
                'regions': ['all_india'],
                'duration': 1,
                'category': 'religious',
                'shopping_period': 10,
                'description': 'Birth celebration of Lord Rama',
                'trending_keywords': ['rama', 'ram navami', 'traditional', 'religious', 'hindu']
            }
        }


    def get_upcoming_festivals(self, location, days_ahead=90):
        """
        Get upcoming festivals for the user's region only
        """
        upcoming_festivals = []
        current_date = datetime.now()
        end_date = current_date + timedelta(days=days_ahead)
        region = self._map_location_to_region(location)
        for festival_key, festival_data in self.festivals_db.items():
            festival_date_str = festival_data.get(f'date_{current_date.year}', '')
            if not festival_date_str:
                continue
            festival_date = datetime.strptime(festival_date_str, '%Y-%m-%d')
            # Only include if festival is upcoming and is for this region or all_india
            if current_date <= festival_date <= end_date:
                if region in festival_data.get('regions', []) or 'all_india' in festival_data.get('regions', []):
                    days_until = (festival_date - current_date).days
                    upcoming_festivals.append({
                        'name': festival_data['name'],
                        'key': festival_key,
                        'date': festival_date_str,
                        'days_until': days_until,
                        'duration': festival_data['duration'],
                        'category': festival_data['category'],
                        'shopping_period': festival_data['shopping_period'],
                        'region': region,
                        'description': festival_data.get('description', 'Festival'),
                        'trending_keywords': festival_data.get('trending_keywords', [])
                    })
        upcoming_festivals.sort(key=lambda x: x['days_until'])
        return upcoming_festivals

    def get_all_festivals(self, location=None, sort_by='days_until'):
        """
        Get all festivals for the user's region only
        """
        all_festivals = []
        current_date = datetime.now()
        region = self._map_location_to_region(location) if location else None
        for festival_key, festival_data in self.festivals_db.items():
            festival_date_str = festival_data.get(f'date_{current_date.year}', '')
            if not festival_date_str:
                continue
            festival_date = datetime.strptime(festival_date_str, '%Y-%m-%d')
            days_until = (festival_date - current_date).days
            if days_until < 0:
                next_year = festival_date.year + 1
                next_year_date = datetime.strptime(festival_date_str, '%Y-%m-%d')
                next_year_date = next_year_date.replace(year=next_year)
                days_until = (next_year_date - current_date).days
            # Only include if festival is for this region or all_india
            is_regional = region and (region in festival_data['regions'] or 'all_india' in festival_data['regions'])
            if is_regional:
                festival_info = {
                    'name': festival_data['name'],
                    'key': festival_key,
                    'date': festival_date_str,
                    'days_until': days_until,
                    'duration': festival_data['duration'],
                    'category': festival_data['category'],
                    'shopping_period': festival_data['shopping_period'],
                    'description': festival_data['description'],
                    'trending_keywords': festival_data.get('trending_keywords', []),
                    'is_regional': is_regional,
                    'regions': festival_data['regions'],
                    'urgency_level': self._get_urgency_level(days_until)
                }
                all_festivals.append(festival_info)
        # Sort festivals
        if sort_by == 'days_until':
            all_festivals.sort(key=lambda x: x['days_until'])
        elif sort_by == 'name':
            all_festivals.sort(key=lambda x: x['name'])
        elif sort_by == 'category':
            all_festivals.sort(key=lambda x: (x['category'], x['days_until']))
        return all_festivals
    
    def _map_location_to_region(self, location):
        """Map location to region for festival relevance"""
        location = location.lower()
        
        region_mapping = {
            # Maharashtra
            'mumbai': 'maharashtra',
            'pune': 'maharashtra',
            'nagpur': 'maharashtra',
            'thane': 'maharashtra',
            'nashik': 'maharashtra',
            'aurangabad': 'maharashtra',
            'solapur': 'maharashtra',
            'kolhapur': 'maharashtra',
            
            # North India
            'delhi': 'north_india',
            'gurgaon': 'north_india',
            'noida': 'north_india',
            'faridabad': 'north_india',
            'ghaziabad': 'north_india',
            'lucknow': 'north_india',
            'kanpur': 'north_india',
            'varanasi': 'north_india',
            'allahabad': 'north_india',
            'agra': 'north_india',
            'jaipur': 'north_india',
            'jodhpur': 'north_india',
            'udaipur': 'north_india',
            'bikaner': 'north_india',
            'ajmer': 'north_india',
            'patna': 'north_india',
            'gaya': 'north_india',
            'ranchi': 'north_india',
            'jamshedpur': 'north_india',
            'dhanbad': 'north_india',
            
            # Karnataka
            'bangalore': 'karnataka',
            'mysore': 'karnataka',
            'hubli': 'karnataka',
            'mangalore': 'karnataka',
            'belgaum': 'karnataka',
            'gulbarga': 'karnataka',
            
            # Tamil Nadu
            'chennai': 'tamil_nadu',
            'coimbatore': 'tamil_nadu',
            'madurai': 'tamil_nadu',
            'salem': 'tamil_nadu',
            'tiruchirappalli': 'tamil_nadu',
            'vellore': 'tamil_nadu',
            'erode': 'tamil_nadu',
            'tiruppur': 'tamil_nadu',
            
            # West Bengal
            'kolkata': 'west_bengal',
            'howrah': 'west_bengal',
            'durgapur': 'west_bengal',
            'asansol': 'west_bengal',
            'siliguri': 'west_bengal',
            'bardhaman': 'west_bengal',
            
            # Andhra Pradesh & Telangana
            'hyderabad': 'andhra_pradesh',
            'vijayawada': 'andhra_pradesh',
            'visakhapatnam': 'andhra_pradesh',
            'guntur': 'andhra_pradesh',
            'warangal': 'andhra_pradesh',
            'karimnagar': 'andhra_pradesh',
            'nizamabad': 'andhra_pradesh',
            
            # Gujarat
            'ahmedabad': 'gujarat',
            'surat': 'gujarat',
            'vadodara': 'gujarat',
            'rajkot': 'gujarat',
            'bhavnagar': 'gujarat',
            'jamnagar': 'gujarat',
            'anand': 'gujarat',
            
            # Punjab
            'chandigarh': 'punjab',
            'amritsar': 'punjab',
            'ludhiana': 'punjab',
            'jalandhar': 'punjab',
            'patiala': 'punjab',
            'bathinda': 'punjab',
            'mohali': 'punjab',
            
            # Haryana
            'gurugram': 'north_india',
            'faridabad': 'north_india',
            'rohtak': 'north_india',
            'hisar': 'north_india',
            'panipat': 'north_india',
            'karnal': 'north_india',
            
            # Kerala
            'kochi': 'kerala',
            'thiruvananthapuram': 'kerala',
            'calicut': 'kerala',
            'thrissur': 'kerala',
            'kollam': 'kerala',
            'alappuzha': 'kerala',
            'palakkad': 'kerala',
            
            # Assam
            'guwahati': 'assam',
            'silchar': 'assam',
            'dibrugarh': 'assam',
            'jorhat': 'assam',
            'tezpur': 'assam',
            
            # Odisha
            'bhubaneswar': 'odisha',
            'cuttack': 'odisha',
            'rourkela': 'odisha',
            'berhampur': 'odisha',
            'sambalpur': 'odisha',
            
            # Bihar
            'patna': 'bihar',
            'gaya': 'bihar',
            'bhagalpur': 'bihar',
            'muzaffarpur': 'bihar',
            'purnia': 'bihar',
            
            # Jharkhand
            'ranchi': 'jharkhand',
            'jamshedpur': 'jharkhand',
            'dhanbad': 'jharkhand',
            'bokaro': 'jharkhand',
            'hazaribagh': 'jharkhand',
            
            # Madhya Pradesh
            'bhopal': 'madhya_pradesh',
            'indore': 'madhya_pradesh',
            'jabalpur': 'madhya_pradesh',
            'gwalior': 'madhya_pradesh',
            'ujjain': 'madhya_pradesh',
            
            # Chhattisgarh
            'raipur': 'chhattisgarh',
            'bhilai': 'chhattisgarh',
            'bilaspur': 'chhattisgarh',
            'korba': 'chhattisgarh',
            
            # Uttar Pradesh
            'lucknow': 'uttar_pradesh',
            'kanpur': 'uttar_pradesh',
            'varanasi': 'uttar_pradesh',
            'allahabad': 'uttar_pradesh',
            'agra': 'uttar_pradesh',
            'ghaziabad': 'uttar_pradesh',
            'noida': 'uttar_pradesh',
            'meerut': 'uttar_pradesh',
            'bareilly': 'uttar_pradesh',
            'aligarh': 'uttar_pradesh',
            
            # Rajasthan
            'jaipur': 'rajasthan',
            'jodhpur': 'rajasthan',
            'udaipur': 'rajasthan',
            'bikaner': 'rajasthan',
            'ajmer': 'rajasthan',
            'kota': 'rajasthan',
            'sikar': 'rajasthan',
            
            # Goa
            'panaji': 'goa',
            'margao': 'goa',
            'vasco': 'goa',
            'mapusa': 'goa',
            
            # Himachal Pradesh
            'shimla': 'himachal_pradesh',
            'manali': 'himachal_pradesh',
            'dharamshala': 'himachal_pradesh',
            'solan': 'himachal_pradesh',
            
            # Uttarakhand
            'dehradun': 'north_india',
            'haridwar': 'north_india',
            'rishikesh': 'north_india',
            'nainital': 'north_india',
            
            # Jammu & Kashmir
            'srinagar': 'north_india',
            'jammu': 'north_india',
            'leh': 'north_india',
            
            # North Eastern States
            'imphal': 'northeast',
            'aizawl': 'mizoram',
            'shillong': 'northeast',
            'kohima': 'northeast',
            'itanagar': 'northeast',
            'agartala': 'tripura',
            'gangtok': 'sikkim',
            
            # Additional locations from HTML
            'alappuzha': 'kerala',
            'bardhaman': 'west_bengal',
            'berhampur': 'odisha',
            'bhagalpur': 'bihar',
            'bokaro': 'jharkhand',
            'calicut': 'kerala',
            'coimbatore': 'tamil_nadu',
            'cuttack': 'odisha',
            'dhanbad': 'jharkhand',
            'dibrugarh': 'assam',
            'durgapur': 'west_bengal',
            'erode': 'tamil_nadu',
            'faridabad': 'haryana',
            'gaya': 'bihar',
            'ghaziabad': 'uttar_pradesh',
            'gulbarga': 'karnataka',
            'guntur': 'andhra_pradesh',
            'gurgaon': 'haryana',
            'gurugram': 'haryana',
            'hazaribagh': 'jharkhand',
            'hisar': 'haryana',
            'howrah': 'west_bengal',
            'hubli': 'karnataka',
            'jalandhar': 'punjab',
            'jamnagar': 'gujarat',
            'jamshedpur': 'jharkhand',
            'jorhat': 'assam',
            'karnal': 'haryana',
            'karimnagar': 'telangana',
            'kolhapur': 'maharashtra',
            'kollam': 'kerala',
            'korba': 'chhattisgarh',
            'mangalore': 'karnataka',
            'mohali': 'punjab',
            'muzaffarpur': 'bihar',
            'mysore': 'karnataka',
            'nizamabad': 'telangana',
            'noida': 'uttar_pradesh',
            'palakkad': 'kerala',
            'panaji': 'goa',
            'panipat': 'haryana',
            'patiala': 'punjab',
            'purnia': 'bihar',
            'raipur': 'chhattisgarh',
            'ranchi': 'jharkhand',
            'rohtak': 'haryana',
            'rourkela': 'odisha',
            'sambalpur': 'odisha',
            'salem': 'tamil_nadu',
            'silchar': 'assam',
            'siliguri': 'west_bengal',
            'solapur': 'maharashtra',
            'tezpur': 'assam',
            'thane': 'maharashtra',
            'thiruvananthapuram': 'kerala',
            'thrissur': 'kerala',
            'tiruchirappalli': 'tamil_nadu',
            'tiruppur': 'tamil_nadu',
            'ujjain': 'madhya_pradesh',
            'vadodara': 'gujarat',
            'vellore': 'tamil_nadu',
            'vijayawada': 'andhra_pradesh',
            'visakhapatnam': 'andhra_pradesh',
            'warangal': 'telangana'
        }
        
        return region_mapping.get(location, 'all_india')
    
    def get_festival_recommendations(self, product_data, location_data):
        """
        Get festival-based recommendations for a product
        
        Args:
            product_data (dict): Product information
            location_data (dict): Location information
            
        Returns:
            dict: Festival recommendations
        """
        category = product_data.get('category', '').lower()
        location = product_data.get('location', 'Mumbai')
        
        # Get upcoming festivals
        upcoming_festivals = self.get_upcoming_festivals(location)
        
        # Find relevant festivals for this product
        relevant_festivals = []
        for festival in upcoming_festivals:
            if self._is_product_relevant_to_festival(category, festival['key']):
                relevance_score = self._calculate_festival_relevance(
                    product_data, festival, location_data
                )
                
                relevant_festivals.append({
                    **festival,
                    'relevance_score': relevance_score,
                    'promotion_ideas': self._generate_promotion_ideas(product_data, festival)
                })
        
        # Sort by relevance score
        relevant_festivals.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return {
            'upcoming_festivals': relevant_festivals,
            'total_opportunities': len(relevant_festivals),
            'best_opportunity': relevant_festivals[0] if relevant_festivals else None
        }
    
    def _is_product_relevant_to_festival(self, product_name, festival_key):
        """Check if specific product is relevant to a specific festival"""
        # Normalize product name for matching
        product_name = product_name.lower().replace(' ', '_').replace('-', '_')
        
        # Check if product exists in our mapping
        if product_name in self.product_festival_mapping:
            return festival_key in self.product_festival_mapping[product_name]
        
        # Fallback to category-based matching for products not in specific mapping
        return False
    
    def get_product_festival_opportunities(self, product_name, location):
        """
        Get specific festival opportunities for a product based on the comprehensive mapping
        
        Args:
            product_name (str): Name of the product
            location (str): Location for regional festivals
            
        Returns:
            dict: Product-specific festival opportunities
        """
        # Normalize product name
        product_name = product_name.lower().replace(' ', '_').replace('-', '_')
        
        opportunities = []
        
        if product_name in self.product_festival_mapping:
            product_festivals = self.product_festival_mapping[product_name]
            
            for festival_key, promotion_reason in product_festivals.items():
                # Get festival details from database
                festival_data = self.festivals_db.get(festival_key)
                
                if festival_data:
                    # Calculate days until festival
                    festival_date = datetime.strptime(festival_data['date_2025'], '%Y-%m-%d')
                    days_until = (festival_date - datetime.now()).days
                    
                    # Only include upcoming festivals (within next 6 months)
                    if 0 <= days_until <= 180:
                        # Check if festival is relevant to the location
                        is_regional = location.lower() in [region.lower() for region in festival_data.get('regions', [])]
                        
                        opportunities.append({
                            'festival_name': festival_data['name'],
                            'festival_key': festival_key,
                            'date': festival_data['date_2025'],
                            'days_until': days_until,
                            'duration': festival_data.get('duration', 1),
                            'category': festival_data.get('category', 'cultural'),
                            'promotion_reason': promotion_reason,
                            'is_regional': is_regional,
                            'urgency_level': self._get_urgency_level(days_until),
                            'shopping_period': festival_data.get('shopping_period', 7),
                            'trending_keywords': festival_data.get('trending_keywords', [])
                        })
        
        # Sort by days until festival (closest first)
        opportunities.sort(key=lambda x: x['days_until'])
        
        return {
            'product_name': product_name.replace('_', ' ').title(),
            'total_opportunities': len(opportunities),
            'opportunities': opportunities,
            'best_opportunity': opportunities[0] if opportunities else None,
            'regional_opportunities': [opp for opp in opportunities if opp['is_regional']],
            'national_opportunities': [opp for opp in opportunities if not opp['is_regional']]
        }
    
    def _calculate_festival_relevance(self, product_data, festival, location_data):
        """
        Calculate relevance score between product and festival
        
        Args:
            product_data (dict): Product information
            festival (dict): Festival information
            location_data (dict): Location information
            
        Returns:
            float: Relevance score (0-1)
        """
        base_score = 0.5
        
        # Days until festival (closer festivals get higher score)
        days_until = festival['days_until']
        if days_until <= 30:
            base_score += 0.3
        elif days_until <= 60:
            base_score += 0.2
        elif days_until <= 90:
            base_score += 0.1
        
        # Festival duration (longer festivals get higher score)
        duration_bonus = min(festival['duration'] * 0.02, 0.1)
        base_score += duration_bonus
        
        # Regional relevance
        if location_data.get('region') == festival['region']:
            base_score += 0.2
        
        # Category relevance
        category = product_data.get('category', '').lower()
        if category in self.product_festival_mapping:
            if festival['key'] in self.product_festival_mapping[category]:
                base_score += 0.2
        
        return float(min(base_score, 1.0))
    
    def _generate_promotion_ideas(self, product_data, festival):
        """Generate promotion ideas for product-festival combination"""
        ideas = []
        
        festival_name = festival['name']
        category = product_data.get('category', '').lower()
        
        # Generic promotion ideas
        ideas.append(f"Festival Special: {festival_name} Collection")
        ideas.append(f"Pre-{festival_name} Sale: Up to 40% off")
        ideas.append(f"{festival_name} Gift Bundles")
        
        # Category-specific ideas
        if category == 'clothing':
            ideas.extend([
                f"{festival_name} Ethnic Wear Collection",
                f"Festival Ready: Complete {festival_name} Look",
                f"{festival_name} Family Package Deals"
            ])
        elif category == 'electronics':
            ideas.extend([
                f"{festival_name} Tech Deals",
                f"Festival Gift: Buy 1 Get 1 on Accessories",
                f"{festival_name} EMI Offers"
            ])
        elif category == 'home_decor':
            ideas.extend([
                f"{festival_name} Home Decoration Package",
                f"Festival Lighting Collection",
                f"{festival_name} Religious Items Bundle"
            ])
        
        return ideas
    
    def get_trending_styles(self, festival_key, location):
        """
        Get trending styles for a specific festival and location
        This would typically integrate with Google Trends API
        """
        # Mock trending data (in real implementation, this would come from APIs)
        trending_styles = {
            'diwali': {
                'clothing': ['anarkali_suits', 'silk_sarees', 'kurtas'],
                'colors': ['red', 'gold', 'green', 'purple'],
                'accessories': ['jewelry', 'bindis', 'bangles']
            },
            'holi': {
                'clothing': ['white_kurtas', 'colorful_dresses', 'casual_wear'],
                'colors': ['white', 'bright_colors', 'pastels'],
                'accessories': ['sunglasses', 'hats', 'waterproof_items']
            },
            'christmas': {
                'clothing': ['western_wear', 'party_dresses', 'formal_wear'],
                'colors': ['red', 'green', 'white', 'gold'],
                'accessories': ['gift_items', 'decorations', 'lights']
            }
        }
        
        return trending_styles.get(festival_key, {})
    
    def calculate_festival_demand_boost(self, product_data, festival):
        """
        Calculate expected demand boost during festival period
        
        Args:
            product_data (dict): Product information
            festival (dict): Festival information
            
        Returns:
            float: Expected demand boost multiplier
        """
        base_boost = 1.5  # 50% base increase
        
        # Adjust based on relevance
        relevance_score = festival.get('relevance_score', 0.5)
        base_boost *= (1 + relevance_score)
        
        # Adjust based on days until festival
        days_until = festival['days_until']
        if days_until <= 7:
            base_boost *= 1.5  # Last-minute rush
        elif days_until <= 30:
            base_boost *= 1.3  # Peak shopping period
        
        # Adjust based on festival duration
        duration = festival['duration']
        if duration >= 5:
            base_boost *= 1.2  # Longer festivals have more shopping days
        
        return float(min(base_boost, 3.0))  # Cap at 3x 

    def get_trending_data(self, festival_key, location=None):
        """
        Get trending data for a specific festival and location
        
        Args:
            festival_key (str): Festival identifier
            location (str): Optional location for localized trends
            
        Returns:
            dict: Trending data including keywords, search volume, and suggestions
        """
        festival_data = self.festivals_db.get(festival_key, {})
        if not festival_data:
            return {}
        
        # Mock trending data (in real implementation, this would integrate with Google Trends API)
        trending_keywords = festival_data.get('trending_keywords', [])
        
        # Generate location-specific trends
        location_trends = []
        if location:
            region = self._map_location_to_region(location)
            if region == 'maharashtra':
                location_trends.extend(['maharashtra festival', 'local traditions'])
            elif region == 'punjab':
                location_trends.extend(['punjabi festival', 'traditional items'])
            elif region == 'tamil_nadu':
                location_trends.extend(['tamil festival', 'traditional wear'])
            elif region == 'kerala':
                location_trends.extend(['kerala festival', 'traditional items'])
            elif region == 'west_bengal':
                location_trends.extend(['bengali festival', 'traditional items'])
        
        # Combine general and location-specific trends
        all_trends = trending_keywords + location_trends
        
        return {
            'festival_name': festival_data['name'],
            'trending_keywords': all_trends,
            'search_volume': self._generate_mock_search_volume(festival_key),
            'trending_products': self._get_trending_products(festival_key, location),
            'promotion_suggestions': self._generate_promotion_suggestions(festival_key, location)
        }
    
    def get_festival_insights(self, festival_key, location=None):
        """
        Get comprehensive insights for a specific festival
        
        Args:
            festival_key (str): Festival identifier
            location (str): Optional location for localized insights
            
        Returns:
            dict: Comprehensive festival insights
        """
        festival_data = self.festivals_db.get(festival_key, {})
        if not festival_data:
            return {}
        
        current_date = datetime.now()
        festival_date_str = festival_data.get(f'date_{current_date.year}', '')
        
        if festival_date_str:
            festival_date = datetime.strptime(festival_date_str, '%Y-%m-%d')
            days_until = (festival_date - current_date).days
            
            if days_until < 0:
                next_year = current_date.year + 1
                next_year_date = datetime.strptime(festival_date_str, '%Y-%m-%d')
                next_year_date = next_year_date.replace(year=next_year)
                days_until = (next_year_date - current_date).days
        else:
            days_until = None
        
        region = self._map_location_to_region(location) if location else None
        is_regional = (region and region in festival_data['regions']) or 'all_india' in festival_data['regions']
        
        return {
            'festival_info': festival_data,
            'days_until': days_until,
            'is_regional': is_regional,
            'urgency_level': self._get_urgency_level(days_until) if days_until else 'unknown',
            'trending_data': self.get_trending_data(festival_key, location),
            'marketing_opportunities': self._get_marketing_opportunities(festival_key, days_until),
            'inventory_recommendations': self._get_inventory_recommendations(festival_key, location)
        }
    
    def _get_urgency_level(self, days_until):
        """Get urgency level based on days until festival"""
        if days_until is None:
            return 'unknown'
        elif days_until <= 7:
            return 'critical'
        elif days_until <= 30:
            return 'urgent'
        elif days_until <= 90:
            return 'upcoming'
        else:
            return 'future'
    
    def _generate_mock_search_volume(self, festival_key):
        """Generate mock search volume data"""
        # Mock data - in real implementation, this would come from Google Trends API
        base_volumes = {
            'diwali': 1000000,
            'holi': 800000,
            'christmas': 600000,
            'eid_al_fitr': 500000,
            'navratri': 400000,
            'ganesh_chaturthi': 300000,
            'durga_puja': 350000,
            'rakhi': 200000,
            'karwa_chauth': 150000,
            'onam': 80000,
            'janmashtami': 180000,
            'gurpurab': 90000,
            'mahashivratri': 160000,
            'ram_navami': 140000,
            'independence_day': 300000,
            'republic_day': 250000,
            'gandhi_jayanti': 100000,
            'mothers_day': 400000,
            'fathers_day': 350000,
            'daughters_day': 200000,
            'childrens_day': 300000,
            'teachers_day': 150000,
            'friendship_day': 250000,
            'valentines_day': 500000,
            'new_year': 450000
        }
        
        return base_volumes.get(festival_key, 50000)
    
    def _get_trending_products(self, festival_key, location=None):
        """Get trending products for a festival"""
        # Mock trending products based on festival
        trending_products = {
            'diwali': ['diwali lights', 'sweets', 'gifts', 'decorations', 'clothes'],
            'holi': ['colors', 'white clothes', 'water guns', 'sweets'],
            'christmas': ['christmas tree', 'gifts', 'decorations', 'cake'],
            'eid_al_fitr': ['clothes', 'gifts', 'sweets', 'decorations'],
            'navratri': ['garba clothes', 'dandiya sticks', 'traditional wear'],
            'ganesh_chaturthi': ['ganesh idol', 'modak', 'decorations'],
            'durga_puja': ['durga idol', 'clothes', 'decorations'],
            'rakhi': ['rakhi', 'gifts', 'sweets'],
            'karwa_chauth': ['mehendi', 'sargi items', 'gifts'],
            'onam': ['onam sadya items', 'traditional wear'],
            'janmashtami': ['krishna idol', 'dahi handi items'],
            'gurpurab': ['sikh items', 'traditional wear'],
            'mahashivratri': ['shiva idol', 'bilva leaves'],
            'ram_navami': ['ram idol', 'religious items'],
            'independence_day': ['tricolor clothing', 'flag items', 'patriotic gifts', 'national pride items'],
            'republic_day': ['tricolor clothing', 'flag items', 'patriotic gifts', 'national pride items'],
            'gandhi_jayanti': ['khadi clothing', 'simple traditional wear', 'peace items'],
            'mothers_day': ['flowers', 'jewelry', 'gifts', 'spa items', 'cosmetics'],
            'fathers_day': ['watches', 'accessories', 'gadgets', 'gifts', 'electronics'],
            'daughters_day': ['toys', 'dresses', 'accessories', 'gifts', 'cosmetics'],
            'childrens_day': ['toys', 'books', 'educational items', 'games', 'stationery'],
            'teachers_day': ['books', 'stationery', 'gifts', 'respect items'],
            'friendship_day': ['friendship bands', 'gifts', 'cards', 'accessories'],
            'valentines_day': ['flowers', 'chocolates', 'jewelry', 'romantic gifts', 'couple items'],
            'new_year': ['party wear', 'gifts', 'decorations', 'accessories', 'electronics']
        }
        
        return trending_products.get(festival_key, ['traditional items', 'gifts'])
    
    def _generate_promotion_suggestions(self, festival_key, location=None):
        """Generate promotion suggestions for a festival"""
        suggestions = []
        
        # General suggestions
        suggestions.append(f"Pre-{self.festivals_db[festival_key]['name']} Sale")
        suggestions.append(f"{self.festivals_db[festival_key]['name']} Special Offers")
        suggestions.append(f"Festival Bundle Deals")
        
        # Location-specific suggestions
        if location:
            region = self._map_location_to_region(location)
            if region in ['maharashtra', 'karnataka']:
                suggestions.append("Regional Festival Collection")
            elif region in ['punjab', 'haryana']:
                suggestions.append("Punjabi Festival Special")
            elif region == 'tamil_nadu':
                suggestions.append("Tamil Festival Collection")
            elif region == 'kerala':
                suggestions.append("Kerala Festival Special")
            elif region == 'west_bengal':
                suggestions.append("Bengali Festival Collection")
        
        return suggestions
    
    def _get_marketing_opportunities(self, festival_key, days_until):
        """Get marketing opportunities based on days until festival"""
        opportunities = []
        
        if days_until is None:
            opportunities.append("Plan long-term festival strategy")
        elif days_until <= 7:
            opportunities.extend([
                "Last-minute promotions",
                "Express delivery options",
                "Flash sales",
                "Urgent inventory clearance"
            ])
        elif days_until <= 30:
            opportunities.extend([
                "Pre-festival campaigns",
                "Early bird discounts",
                "Bundle offers",
                "Social media campaigns"
            ])
        elif days_until <= 90:
            opportunities.extend([
                "Festival preparation campaigns",
                "Seasonal collections",
                "Advance booking offers",
                "Loyalty program promotions"
            ])
        else:
            opportunities.extend([
                "Long-term planning",
                "Inventory preparation",
                "Supplier coordination",
                "Marketing strategy development"
            ])
        
        return opportunities
    
    def _get_inventory_recommendations(self, festival_key, location=None):
        """Get inventory recommendations for a festival"""
        recommendations = []
        
        # Category-based recommendations
        if festival_key in ['diwali', 'holi', 'christmas', 'eid_al_fitr']:
            recommendations.extend([
                "Increase stock of traditional clothing",
                "Prepare gift items and accessories",
                "Stock up on decorative items",
                "Plan for sweets and food items"
            ])
        elif festival_key in ['navratri', 'ganesh_chaturthi', 'durga_puja']:
            recommendations.extend([
                "Focus on religious items",
                "Prepare traditional wear",
                "Stock decorative items",
                "Plan for prasad items"
            ])
        elif festival_key in ['rakhi', 'karwa_chauth', 'bhai_dooj']:
            recommendations.extend([
                "Increase gift items",
                "Prepare traditional sweets",
                "Stock jewelry and accessories",
                "Plan for family packages"
            ])
        elif festival_key in ['independence_day', 'republic_day', 'gandhi_jayanti']:
            recommendations.extend([
                "Stock tricolor clothing and accessories",
                "Prepare patriotic gift items",
                "Increase flag and national pride items",
                "Plan for khadi and traditional wear"
            ])
        elif festival_key in ['mothers_day', 'fathers_day', 'daughters_day', 'childrens_day']:
            recommendations.extend([
                "Increase gift items and accessories",
                "Prepare family-oriented products",
                "Stock jewelry and watches",
                "Plan for toys and educational items"
            ])
        elif festival_key in ['friendship_day']:
            recommendations.extend([
                "Increase friendship items",
                "Prepare flowers and gifts",
                "Stock jewelry and accessories",
                "Plan for friendship and gift items"
            ])
        elif festival_key in ['teachers_day', 'childrens_day']:
            recommendations.extend([
                "Increase educational items and books",
                "Prepare stationery and respect items",
                "Stock toys and games",
                "Plan for teacher and student gifts"
            ])

        
        return recommendations 