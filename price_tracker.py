"""
FREE Price Tracker for Coles and Woolworths - FIXED VERSION
Works with current websites
"""

import os
import json
import asyncio
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Your email and password from GitHub Secrets
COLES_EMAIL = os.environ.get('COLES_EMAIL', '')
COLES_PASSWORD = os.environ.get('COLES_PASSWORD', '')
WOOLWORTHS_EMAIL = os.environ.get('WOOLWORTHS_EMAIL', '')
WOOLWORTHS_PASSWORD = os.environ.get('WOOLWORTHS_PASSWORD', '')

class SimplePriceTracker:
    """Simple robot that checks prices"""
    
    async def login_coles(self, page):
        """Log into Coles - works with current website"""
        print("Logging into Coles...")
        
        # Go to Coles homepage
        await page.goto('https://www.coles.com.au')
        await asyncio.sleep(2)
        
        # Try multiple ways to find the login button
        login_selectors = [
            'a:has-text("Sign In")',
            'a:has-text("Sign in")',
            'a:has-text("Log in")',
            'button:has-text("Sign In")',
            '[data-testid="sign-in-link"]',
            '.sign-in-link',
            'a[href*="sign-in"]',
            'a[href*="login"]'
        ]
        
        clicked = False
        for selector in login_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    await page.click(selector)
                    clicked = True
                    print(f"  Found login button: {selector}")
                    break
            except:
                continue
        
        if not clicked:
            # Try going directly to login page
            print("  Going directly to login page")
            await page.goto('https://www.coles.com.au/sign-in')
        
        await asyncio.sleep(2)
        
        # Wait for email field
        await page.wait_for_selector('input[type="email"], input[name="email"]', timeout=10000)
        
        # Type email
        email_input = await page.query_selector('input[type="email"], input[name="email"]')
        await email_input.fill(COLES_EMAIL)
        await asyncio.sleep(1)
        
        # Type password
        password_input = await page.query_selector('input[type="password"]')
        await password_input.fill(COLES_PASSWORD)
        await asyncio.sleep(1)
        
        # Click login button
        login_btn_selectors = [
            'button[type="submit"]',
            'button:has-text("Sign In")',
            'button:has-text("Log in")',
            '[data-testid="login-button"]'
        ]
        
        for selector in login_btn_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    await page.click(selector)
                    print("  Clicked login button")
                    break
            except:
                continue
        
        # Wait for login to complete
        await asyncio.sleep(3)
        print("✅ Logged into Coles")
    
    async def login_woolworths(self, page):
        """Log into Woolworths - works with current website"""
        print("Logging into Woolworths...")
        
        # Go to Woolworths homepage
        await page.goto('https://www.woolworths.com.au')
        await asyncio.sleep(2)
        
        # Try multiple ways to find login button
        login_selectors = [
            'a:has-text("Sign In")',
            'a:has-text("Log in")',
            'button:has-text("Sign In")',
            '[data-testid="sign-in-link"]',
            '.login-link',
            'a[href*="login"]'
        ]
        
        clicked = False
        for selector in login_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    await page.click(selector)
                    clicked = True
                    print(f"  Found login button: {selector}")
                    break
            except:
                continue
        
        if not clicked:
            # Try going directly to login page
            print("  Going directly to login page")
            await page.goto('https://www.woolworths.com.au/shop/login')
        
        await asyncio.sleep(2)
        
        # Wait for email field
        await page.wait_for_selector('input[name="email"], input[type="email"]', timeout=10000)
        
        # Type email
        email_input = await page.query_selector('input[name="email"], input[type="email"]')
        await email_input.fill(WOOLWORTHS_EMAIL)
        await asyncio.sleep(1)
        
        # Type password
        password_input = await page.query_selector('input[name="password"], input[type="password"]')
        await password_input.fill(WOOLWORTHS_PASSWORD)
        await asyncio.sleep(1)
        
        # Click login button
        login_btn_selectors = [
            'button[type="submit"]',
            'button:has-text("Sign In")',
            'button:has-text("Log in")',
            '[data-testid="login-button"]'
        ]
        
        for selector in login_btn_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    await page.click(selector)
                    print("  Clicked login button")
                    break
            except:
                continue
        
        # Wait for login to complete
        await asyncio.sleep(3)
        print("✅ Logged into Woolworths")
    
    async def search_coles(self, page, ingredient):
        """Search for an item on Coles"""
        try:
            # Go to search page
            search_url = f'https://www.coles.com.au/search?search={ingredient.replace(" ", "%20")}'
            await page.goto(search_url)
            await asyncio.sleep(2)
            
            # Try different price selectors
            price_selectors = [
                '.price',
                '.product__price',
                '[data-testid="product-price"]',
                '.price__value',
                '.ProductCard__price'
            ]
            
            for selector in price_selectors:
                try:
                    price_element = await page.query_selector(selector)
                    if price_element:
                        price_text = await price_element.text_content()
                        match = re.search(r'\$(\d+\.?\d*)', price_text)
                        if match:
                            return float(match.group(1))
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"  Error searching Coles: {e}")
            return None
    
    async def search_woolworths(self, page, ingredient):
        """Search for an item on Woolworths"""
        try:
            # Go to search page
            search_url = f'https://www.woolworths.com.au/shop/search/products?searchTerm={ingredient.replace(" ", "%20")}'
            await page.goto(search_url)
            await asyncio.sleep(2)
            
            # Try different price selectors
            price_selectors = [
                '.price',
                '.product-price',
                '[data-testid="price"]',
                '.Price__PriceAmount',
                '.shelfProductTile-price'
            ]
            
            for selector in price_selectors:
                try:
                    price_element = await page.query_selector(selector)
                    if price_element:
                        price_text = await price_element.text_content()
                        match = re.search(r'\$(\d+\.?\d*)', price_text)
                        if match:
                            return float(match.group(1))
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"  Error searching Woolworths: {e}")
            return None
    
    async def get_prices(self, store, ingredients):
        """Get prices for a list of ingredients"""
        prices = {}
        
        async with async_playwright() as p:
            # Start browser
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create context with realistic viewport
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            page = await context.new_page()
            
            # Login
            if store == 'coles':
                await self.login_coles(page)
            else:
                await self.login_woolworths(page)
            
            # Search for each ingredient
            for ingredient in ingredients:
                print(f"  Checking {ingredient}...")
                
                if store == 'coles':
                    price = await self.search_coles(page, ingredient)
                else:
                    price = await self.search_woolworths(page, ingredient)
                
                if price:
                    prices[ingredient] = price
                    print(f"    Found: ${price}")
                else:
                    print(f"    Not found")
                
                # Wait between searches (be polite)
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
        
        print(f"\n🛒 Checking prices for {len(ingredients)} items...")
        print("=" * 50)
        
        # Get prices from both stores
        print("\n📊 Checking Coles...")
        coles_prices = await self.get_prices('coles', ingredients)
        
        print("\n📊 Checking Woolworths...")
        woolies_prices = await self.get_prices('woolworths', ingredients)
        
        # Find cheapest store for each item
        print("\n" + "=" * 50)
        print("💰 BEST PRICES THIS WEEK 💰")
        print("=" * 50)
        
        total_savings = 0
        
        for ingredient in ingredients:
            coles_price = coles_prices.get(ingredient)
            woolies_price = woolies_prices.get(ingredient)
            
            if coles_price and woolies_price:
                if coles_price < woolies_price:
                    saving = woolies_price - coles_price
                    total_savings += saving
                    print(f"• {ingredient:20} ${coles_price:.2f} at Coles     (save ${saving:.2f})")
                else:
                    saving = coles_price - woolies_price
                    total_savings += saving
                    print(f"• {ingredient:20} ${woolies_price:.2f} at Woolworths (save ${saving:.2f})")
            elif coles_price:
                print(f"• {ingredient:20} ${coles_price:.2f} at Coles only")
            elif woolies_price:
                print(f"• {ingredient:20} ${woolies_price:.2f} at Woolworths only")
            else:
                print(f"• {ingredient:20} Not found at either store")
        
        if total_savings > 0:
            print(f"\n💡 Total savings by choosing cheapest store: ${total_savings:.2f}")
        
        # Save results to file
        results = {
            'date': datetime.now().isoformat(),
            'coles': coles_prices,
            'woolworths': woolies_prices,
            'total_savings': total_savings
        }
        
        filename = f'prices_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Results saved to {filename}")
        
        # Also save as latest.json for easy access
        with open('latest_prices.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results

async def main():
    print("🚀 Starting Price Tracker...")
    print(f"📧 Using email: {COLES_EMAIL}")
    
    if not COLES_EMAIL or not COLES_PASSWORD:
        print("\n❌ ERROR: Missing email or password!")
        print("Make sure you've set up GitHub Secrets:")
        print("  - COLES_EMAIL")
        print("  - COLES_PASSWORD")
        print("  - WOOLWORTHS_EMAIL")
        print("  - WOOLWORTHS_PASSWORD")
        return
    
    tracker = SimplePriceTracker()
    await tracker.find_specials()
    print("\n✨ Price check complete!")

if __name__ == '__main__':
    asyncio.run(main())
