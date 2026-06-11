"""
FREE Price Tracker for Coles and Woolworths
Runs every Monday, finds specials, saves to file
"""

import os
import json
import asyncio
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Your email and password come from GitHub Secrets (safe!)
COLES_EMAIL = os.environ.get('COLES_EMAIL', '')
COLES_PASSWORD = os.environ.get('COLES_PASSWORD', '')
WOOLWORTHS_EMAIL = os.environ.get('WOOLWORTHS_EMAIL', '')
WOOLWORTHS_PASSWORD = os.environ.get('WOOLWORTHS_PASSWORD', '')

class SimplePriceTracker:
    """Simple robot that checks prices"""
    
    async def get_prices(self, store, ingredients):
        """Get prices for a list of ingredients"""
        prices = {}
        
        async with async_playwright() as p:
            # Start a hidden browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Go to the store website
            if store == 'coles':
                await page.goto('https://www.coles.com.au')
                # Click sign in
                await page.click('text=Sign In')
                # Type email and password
                await page.fill('input[type="email"]', COLES_EMAIL)
                await page.fill('input[type="password"]', COLES_PASSWORD)
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                
            else:  # woolworths
                await page.goto('https://www.woolworths.com.au')
                await page.click('text=Sign In')
                await page.fill('input[name="email"]', WOOLWORTHS_EMAIL)
                await page.fill('input[name="password"]', WOOLWORTHS_PASSWORD)
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
            
            # Now search for each ingredient
            for ingredient in ingredients:
                print(f"Checking {ingredient} at {store}...")
                
                # Search for the ingredient
                if store == 'coles':
                    await page.goto(f'https://www.coles.com.au/search?search={ingredient}')
                else:
                    await page.goto(f'https://www.woolworths.com.au/shop/search/products?searchTerm={ingredient}')
                
                # Wait a moment for prices to load
                await asyncio.sleep(2)
                
                # Look for the price
                price_element = await page.query_selector('.price, .product__price')
                if price_element:
                    price_text = await price_element.text_content()
                    # Find the dollar amount
                    match = re.search(r'\$(\d+\.?\d*)', price_text)
                    if match:
                        price = float(match.group(1))
                        prices[ingredient] = price
                        print(f"  Found: ${price}")
                
                # Wait a bit before next search (be polite)
                await asyncio.sleep(3)
            
            await browser.close()
        
        return prices
    
    async def find_specials(self):
        """Find specials by comparing with last week"""
        # Get all ingredients from your recipes
        # For now, let's use some common items
        ingredients = [
            'milk', 'bread', 'eggs', 'chicken breast', 'rice',
            'pasta', 'cheese', 'yogurt', 'apples', 'bananas'
        ]
        
        print(f"🛒 Checking prices for {len(ingredients)} items...")
        
        # Get prices from both stores
        coles_prices = await self.get_prices('coles', ingredients)
        woolies_prices = await self.get_prices('woolworths', ingredients)
        
        # Find cheapest store for each item
        print("\n💰 BEST PRICES THIS WEEK 💰")
        for ingredient in ingredients:
            coles_price = coles_prices.get(ingredient)
            woolies_price = woolies_prices.get(ingredient)
            
            if coles_price and woolies_price:
                if coles_price < woolies_price:
                    print(f"• {ingredient}: ${coles_price} at Coles (save ${woolies_price - coles_price:.2f})")
                else:
                    print(f"• {ingredient}: ${woolies_price} at Woolworths (save ${coles_price - woolies_price:.2f})")
            elif coles_price:
                print(f"• {ingredient}: ${coles_price} at Coles")
            elif woolies_price:
                print(f"• {ingredient}: ${woolies_price} at Woolworths")
        
        # Save results to file
        results = {
            'date': datetime.now().isoformat(),
            'coles': coles_prices,
            'woolworths': woolies_prices
        }
        
        with open(f'prices_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Results saved to prices_{datetime.now().strftime('%Y%m%d')}.json")

# This is what runs when we start the robot
async def main():
    tracker = SimplePriceTracker()
    await tracker.find_specials()

if __name__ == '__main__':
    asyncio.run(main())
