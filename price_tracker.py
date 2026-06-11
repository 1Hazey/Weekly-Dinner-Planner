"""
FREE Price Tracker - ACTUALLY FINDS PRICES VERSION
"""

import os
import json
import asyncio
import re
from datetime import datetime
from playwright.async_api import async_playwright

COLES_EMAIL = os.environ.get('COLES_EMAIL', '')
COLES_PASSWORD = os.environ.get('COLES_PASSWORD', '')
WOOLWORTHS_EMAIL = os.environ.get('WOOLWORTHS_EMAIL', '')
WOOLWORTHS_PASSWORD = os.environ.get('WOOLWORTHS_PASSWORD', '')

class PriceTracker:
    
    async def run(self):
        """Main function"""
        print("🚀 Starting price check...")
        
        # Common grocery items
        ingredients = ['milk', 'bread', 'eggs', 'chicken', 'rice', 'pasta', 'cheese']
        
        print(f"\nChecking {len(ingredients)} items...")
        
        # Check Coles
        print("\n📊 COLES")
        coles_prices = await self.check_coles(ingredients)
        
        # Check Woolworths  
        print("\n📊 WOOLWORTHS")
        woolies_prices = await self.check_woolworths(ingredients)
        
        # Show results
        print("\n" + "="*50)
        print("💰 RESULTS")
        print("="*50)
        
        found_any = False
        for item in ingredients:
            coles = coles_prices.get(item)
            woolies = woolies_prices.get(item)
            
            if coles and woolies:
                found_any = True
                if coles < woolies:
                    print(f"• {item}: ${coles} at Coles (cheaper than Woolies ${woolies})")
                else:
                    print(f"• {item}: ${woolies} at Woolworths (cheaper than Coles ${coles})")
            elif coles:
                found_any = True
                print(f"• {item}: ${coles} at Coles only")
            elif woolies:
                found_any = True
                print(f"• {item}: ${woolies} at Woolworths only")
            else:
                print(f"• {item}: NOT FOUND at either store")
        
        if not found_any:
            print("\n⚠️ No prices found! Let me save the webpage so we can debug...")
        
        # Save results
        results = {
            'date': str(datetime.now()),
            'coles': coles_prices,
            'woolworths': woolies_prices
        }
        
        with open('prices.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n✅ Saved to prices.json")
    
    async def check_coles(self, ingredients):
        """Check prices at Coles - IMPROVED VERSION"""
        prices = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            for ingredient in ingredients:
                print(f"  Searching: {ingredient}")
                
                # Search URL
                search_url = f'https://www.coles.com.au/search?search={ingredient.replace(" ", "%20")}'
                await page.goto(search_url)
                
                # Wait for page to load
                await page.wait_for_timeout(3000)
                
                # Save the page HTML to see what's there (for debugging)
                html_content = await page.content()
                with open(f'coles_{ingredient}.html', 'w') as f:
                    f.write(html_content)
                
                # Try multiple ways to find price
                price_found = None
                
                # Method 1: Look for price in specific elements
                price_elements = await page.query_selector_all('.price, .product__price, [data-testid="price"], .ProductCard__price, .price__value')
                
                for elem in price_elements[:3]:  # Check first 3 prices
                    text = await elem.text_content()
                    # Find dollar amount
                    match = re.search(r'\$(\d+\.?\d*)', text)
                    if match:
                        price_found = float(match.group(1))
                        break
                
                # Method 2: If no price found, search the entire page text
                if not price_found:
                    page_text = await page.content()
                    # Look for patterns like "$3.50" or "$5"
                    matches = re.findall(r'\$(\d+\.\d{2})', page_text)
                    if matches:
                        # Take the first reasonable price (not too high or low)
                        for match in matches[:5]:
                            price = float(match)
                            if 0.50 < price < 100:  # Reasonable price range
                                price_found = price
                                break
                
                if price_found:
                    prices[ingredient] = price_found
                    print(f"    Found: ${price_found}")
                else:
                    print(f"    Not found - saved HTML to coles_{ingredient}.html")
                
                # Wait a bit before next search
                await page.wait_for_timeout(2000)
            
            await browser.close()
        
        return prices
    
    async def check_woolworths(self, ingredients):
        """Check prices at Woolworths - IMPROVED VERSION"""
        prices = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            for ingredient in ingredients:
                print(f"  Searching: {ingredient}")
                
                # Search URL
                search_url = f'https://www.woolworths.com.au/shop/search/products?searchTerm={ingredient.replace(" ", "%20")}'
                await page.goto(search_url)
                
                # Wait for page to load
                await page.wait_for_timeout(3000)
                
                # Save HTML for debugging
                html_content = await page.content()
                with open(f'woolies_{ingredient}.html', 'w') as f:
                    f.write(html_content)
                
                # Try multiple ways to find price
                price_found = None
                
                # Method 1: Look for price elements
                price_elements = await page.query_selector_all('.price, .product-price, [data-testid="price"], .shelfProductTile-price')
                
                for elem in price_elements[:3]:
                    text = await elem.text_content()
                    match = re.search(r'\$(\d+\.?\d*)', text)
                    if match:
                        price_found = float(match.group(1))
                        break
                
                # Method 2: Search page text
                if not price_found:
                    page_text = await page.content()
                    matches = re.findall(r'\$(\d+\.\d{2})', page_text)
                    if matches:
                        for match in matches[:5]:
                            price = float(match)
                            if 0.50 < price < 100:
                                price_found = price
                                break
                
                if price_found:
                    prices[ingredient] = price_found
                    print(f"    Found: ${price_found}")
                else:
                    print(f"    Not found - saved HTML to woolies_{ingredient}.html")
                
                await page.wait_for_timeout(2000)
            
            await browser.close()
        
        return prices

async def main():
    tracker = PriceTracker()
    await tracker.run()

if __name__ == '__main__':
    asyncio.run(main())
