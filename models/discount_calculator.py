import google.generativeai as genai
import os
import json
import re

# Ensure Gemini API is configured (this should also be done in app.py to avoid redundant calls)
# This check is here for self-containation of the model file, but primary configuration
# should happen once at app startup in app.py.
if os.environ.get('GOOGLE_API_KEY'):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
else:
    print("Warning: GOOGLE_API_KEY not found in environment variables. Gemini features in SmartDiscountCalculator may not work.")

class SmartDiscountCalculator:
    """
    Calculates smart discount recommendations and provides detailed reasoning
    and sales strategies using the Gemini AI model.
    """

    def __init__(self):
        # Initialize Gemini model for text generation
        # CORRECTED: Using models/gemini-1.5-flash as requested
        self.gemini_model = genai.GenerativeModel("models/gemini-1.5-flash")

    def calculate_discount(self, product_data, health_score, festival_result):
        """
        Calculates a recommended discount and generates a detailed reasoning
        and 4 sales strategies based on product health, sales data, and festival opportunities.

        Args:
            product_data (dict): Dictionary containing product details like
                                 'name', 'category', 'price', 'stock_quantity',
                                 'days_in_stock', 'sales_velocity'.
            health_score (float): A score (0.0 to 1.0) indicating product health.
                                 Lower score means poorer health (e.g., dead stock).
            festival_result (dict): Dictionary containing festival recommendations,
                                    e.g., {'recommended_festivals': [{'name': 'Diwali'}]}.

        Returns:
            dict: A dictionary containing discount recommendations, AI-generated reasoning,
                  and a list of sales strategies.
        """
        product_name = product_data.get('name', 'product')
        price = product_data.get('price', 0)
        stock_quantity = product_data.get('stock_quantity', 0)
        sales_velocity = product_data.get('sales_velocity', 0)
        days_in_stock = product_data.get('days_in_stock', 0)
        category = product_data.get('category', 'general')

        # Determine health status for context in prompt
        if health_score < 0.3:
            health_status = 'Dead Stock'
        elif health_score < 0.6:
            health_status = 'At Risk'
        else:
            health_status = 'Healthy'

        # Adjust discount based on festival opportunities
        recommended_festivals = [f['name'] for f in festival_result.get('recommended_festivals', [])]
        festival_context = f"Upcoming festival opportunities: {', '.join(recommended_festivals)}." if recommended_festivals else "No specific upcoming festival opportunities."

        # Calculate financial impacts (these will use the AI-determined discount later)
        risk_score = (1 - health_score) * 100 # Convert health score to a risk percentage

        # --- Gemini Integration for Discount, Reasoning and Strategies ---
        # Craft a detailed prompt for Gemini to generate the discount, reasoning, and strategies
        prompt = f"""
        As an expert retail analyst, determine the optimal discount percentage (as an integer from 0 to 70),
        provide a concise and actionable reasoning for this discount,
        and suggest 4 distinct sales strategies for the given product.

        Product Details:
        - Name: '{product_name}'
        - Category: {category}
        - Original Price: ₹{price:.2f}
        - Current Stock: {stock_quantity} units
        - Days in Stock: {days_in_stock} days
        - Sales Velocity (units/day): {sales_velocity}
        - Product Health Score (0-1, lower is worse): {health_score:.2f} ({health_status})
        - {festival_context}

        Generate the response as a JSON object with the following structure:
        {{
            "recommended_discount": 0, // Integer percentage from 0 to 70
            "reasoning_text": "A single, well-structured paragraph (approx. 80-120 words) explaining the discount recommendation, how it addresses product health, and potential benefits.",
            "sales_strategies": [
                {{
                    "name": "Strategy Name 1 (e.g., Flash Sale, Bundle Offer)",
                    "description": "A brief, actionable description of this strategy (1-2 sentences)."
                }},
                {{
                    "name": "Strategy Name 2",
                    "description": "A brief, actionable description of this strategy (1-2 sentences)."
                }},
                {{
                    "name": "Strategy Name 3",
                    "description": "A brief, actionable description of this strategy (1-2 sentences)."
                }},
                {{
                    "name": "Strategy Name 4",
                    "description": "A brief, actionable description of this strategy (1-2 sentences)."
                }}
            ]
        }}
        Ensure the output is ONLY a valid JSON object. No additional text, markdown backticks, or explanations outside the JSON.
        """

        # Default fallbacks if AI call or parsing fails
        recommended_discount = 10 # Default discount
        ai_reasoning = "Could not generate detailed reasoning."
        sales_strategies = []

        try:
            print(f"DEBUG: Sending prompt to Gemini for {product_name}...")
            response = self.gemini_model.generate_content(prompt)
            raw_text = response.text.strip()
            print(f"DEBUG: Raw Gemini response received: {raw_text[:500]}...") # Print first 500 chars
            
            # Attempt to parse the JSON response. Gemini sometimes wraps it in markdown.
            cleaned_text = re.sub(r"^```json|^```|```$", "", raw_text, flags=re.MULTILINE).strip()
            parsed_data = json.loads(cleaned_text)
            print(f"DEBUG: Parsed Gemini data: {json.dumps(parsed_data, indent=2)}")

            # Extract data from AI response
            recommended_discount = int(parsed_data.get("recommended_discount", recommended_discount))
            # Ensure discount is within a reasonable range (0-70%)
            recommended_discount = max(0, min(70, recommended_discount))
            print(f"DEBUG: AI-determined recommended_discount: {recommended_discount}%")


            ai_reasoning = parsed_data.get("reasoning_text", ai_reasoning)
            sales_strategies = parsed_data.get("sales_strategies", sales_strategies)

            # Ensure we always return 4 strategies, even if Gemini provides fewer
            # or if parsing fails partially. Fill with generic if needed.
            while len(sales_strategies) < 4:
                sales_strategies.append({
                    "name": f"Generic Strategy {len(sales_strategies) + 1}",
                    "description": "Consider a general promotional tactic to boost sales."
                })
            sales_strategies = sales_strategies[:4] # Ensure max 4
            print(f"DEBUG: AI-determined sales_strategies count: {len(sales_strategies)}")

        except Exception as e:
            print(f"ERROR: Gemini call failed for discount calculation: {e}")
            print(f"ERROR: Raw Gemini response (if available): {raw_text if 'raw_text' in locals() else 'N/A'}")
            print("DEBUG: Falling back to hardcoded discount logic.")
            # Fallback to simpler, hardcoded reasoning and strategies if AI fails
            recommended_discount = 10 # Fallback discount
            if health_score < 0.3:
                recommended_discount = 40
            elif health_score < 0.6:
                recommended_discount = 20

            ai_reasoning = (
                f"Fallback: Based on the product's {health_status} health status (score: {health_score:.1%}) "
                f"and low sales velocity, a {recommended_discount}% discount is recommended. "
                f"This aims to quickly move existing stock, reduce holding costs, and free up capital. "
                f"Consider leveraging any {', '.join(recommended_festivals) if recommended_festivals else 'general'} promotional periods for maximum impact."
            )
            sales_strategies = [
                {"name": "Clearance Sale", "description": "Aggressively price to clear old stock quickly."},
                {"name": "Limited-Time Offer", "description": "Create urgency with a short-duration discount."},
                {"name": "Bundle with Popular Items", "description": "Pair with fast-moving products to increase perceived value."},
                {"name": "Targeted Promotion", "description": "Offer discount to specific customer segments (e.g., loyal customers)."}
            ]

        # Recalculate financial impacts using the AI-determined (or fallback) discount
        new_price = price * (1 - recommended_discount / 100)
        price_reduction = price * (recommended_discount / 100)
        
        # Determine discount category based on the AI-recommended discount
        discount_category = 'High' if recommended_discount > 30 else 'Medium' if recommended_discount > 15 else 'Low'

        return {
            'recommended_discount': recommended_discount,
            'new_price': new_price,
            'price_reduction': price_reduction,
            'expected_revenue': new_price * stock_quantity, # Ensure expected_revenue is calculated here
            'risk_score': risk_score,
            'health_status': health_status,
            'discount_category': discount_category,
            'reasoning': [ai_reasoning], # Still return as a list for consistency with frontend
            'sales_strategies': sales_strategies # New field
        }
