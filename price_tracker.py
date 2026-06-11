"""
FREE Price Tracker - NO BUTTON CLICKING VERSION
Uses direct URLs only
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
        
        for item in ingredients:
            coles = coles_prices.get(item)
            woolies = woolies_prices.get(item)
            
            if coles and woolies:
                if coles < woolies:
                    print(f"• {item}: ${coles} at Coles (cheaper than Woolies ${woolies})")
                else:
                    print(f"• {item}: ${woolies} at Woolworths (cheaper than Coles ${coles})")
            elif coles:
                print(f"• {item}: ${coles} at Coles only")
            elif woolies:
                print(f"• {item}: ${woolies} at Woolworths only")
        
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
        """Check prices at Coles"""
        prices = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Go directly to Coles
            await page.goto('https://www.coles.com.au')
            await asyncio.sleep(2)
            
            for ingredient in ingredients:
                print(f"  Searching: {ingredient}")
                
                # Go to search
                search_url = f'https://www.coles.com.au/search?search={ingredient}'
                await page.goto(search_url)
                await asyncio.sleep(2)
                
                # Look for price
                content = await page.content()
                price_match = re.search(r'\$(\d+\.\d{2})', content)
                
                if price_match:
                    price = float(price_match.group(1))
                    prices[ingredient] = price
                    print(f"    Found: ${price}")
                else:
                    print(f"    Not found")
                
                await asyncio.sleep(1)
            
            await browser.close()
        
        return prices
    
    async def check_woolworths(self, ingredients):
        """Check prices at Woolworths"""
        prices = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Go directly to Woolworths
            await page.goto('https://www.woolworths.com.au')
            await asyncio.sleep(2)
            
            for ingredient in ingredients:
                print(f"  Searching: {ingredient}")
                
                # Go to search
                search_url = f'https://www.woolworths.com.au/shop/search/products?searchTerm={ingredient}'
                await page.goto(search_url)
                await asyncio.sleep(2)
                
                # Look for price
                content = await page.content()
                price_match = re.search(r'\$(\d+\.\d{2})', content)
                
                if price_match:
                    price = float(price_match.group(1))
                    prices[ingredient] = price
                    print(f"    Found: ${price}")
                else:
                    print(f"    Not found")
                
                await asyncio.sleep(1)
            
            await browser.close()
        
        return prices

async def main():
    tracker = PriceTracker()
    await tracker.run()

if __name__ == '__main__':
    asyncio.run(main())
