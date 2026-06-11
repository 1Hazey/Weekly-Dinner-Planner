"""
Price Tracker - WORKS WITH ACTUAL COLES WEBSITE
Based on your screenshot
"""

import asyncio
import re
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def get_coles_price(product_name):
    """Get price for a product from Coles"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Search for the product
        search_url = f'https://www.coles.com.au/search?search={product_name.replace(" ", "%20")}'
        print(f"  Searching: {search_url}")
        
        await page.goto(search_url)
        await asyncio.sleep(3)  # Wait for page to load
        
        # Find the first product result and click it
        # Look for product links
        product_selector = 'a[href*="/product/"]'
        
        try:
            # Wait for products to appear
            await page.wait_for_selector(product_selector, timeout=10000)
            
            # Get the first product link
            first_product = await page.query_selector(product_selector)
            if first_product:
                # Get the product URL
                product_url = await first_product.get_attribute('href')
                full_url = f'https://www.coles.com.au{product_url}'
                print(f"  Opening product page: {full_url}")
                
                # Go to the product page
                await page.goto(full_url)
                await asyncio.sleep(2)
                
                # Now find the price on the product page (like your screenshot)
                # Based on your screenshot, the price is in a specific element
                price_selectors = [
                    '[data-testid="product-price"]',
                    '.product__price',
                    '.price',
                    '.ProductCard__price',
                    'div[class*="price"]'
                ]
                
                for selector in price_selectors:
                    try:
                        price_element = await page.query_selector(selector)
                        if price_element:
                            price_text = await price_element.text_content()
                            print(f"  Found price text: '{price_text}'")
                            
                            # Extract just the number
                            match = re.search(r'\$?(\d+\.\d{2})', price_text)
                            if match:
                                price = float(match.group(1))
                                print(f"  ✅ Price: ${price}")
                                return price
                    except:
                        continue
                
                # If we get here, try looking at the whole page text
                page_text = await page.content()
                # Look for patterns like "$5.15" that are near "milk"
                matches = re.findall(r'\$(\d+\.\d{2})', page_text)
                if matches:
                    # First price is usually the main product
                    price = float(matches[0])
                    print(f"  ✅ Found price in page: ${price}")
                    return price
                    
        except Exception as e:
            print(f"  Error: {e}")
        
        await browser.close()
        return None

async def get_woolworths_price(product_name):
    """Get price for a product from Woolworths"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Search for the product
        search_url = f'https://www.woolworths.com.au/shop/search/products?searchTerm={product_name.replace(" ", "%20")}'
        print(f"  Searching: {search_url}")
        
        await page.goto(search_url)
        await asyncio.sleep(3)
        
        # Find first product and click it
        try:
            # Look for product links
            product_selector = 'a[data-testid="product-tile-link"], a[class*="product"]'
            await page.wait_for_selector(product_selector, timeout=10000)
            
            first_product = await page.query_selector(product_selector)
            if first_product:
                product_url = await first_product.get_attribute('href')
                if product_url:
                    full_url = f'https://www.woolworths.com.au{product_url}' if product_url.startswith('/') else product_url
                    print(f"  Opening product page")
                    
                    await page.goto(full_url)
                    await asyncio.sleep(2)
                    
                    # Find price
                    price_selectors = [
                        '[data-testid="product-price"]',
                        '.price',
                        '.ProductPrice',
                        'span[class*="price"]'
                    ]
                    
                    for selector in price_selectors:
                        try:
                            price_element = await page.query_selector(selector)
                            if price_element:
                                price_text = await price_element.text_content()
                                match = re.search(r'\$?(\d+\.\d{2})', price_text)
                                if match:
                                    price = float(match.group(1))
                                    print(f"  ✅ Price: ${price}")
                                    return price
                        except:
                            continue
        except Exception as e:
            print(f"  Error: {e}")
        
        await browser.close()
        return None

async def main():
    """Main function to check prices"""
    
    products = ['milk', 'bread', 'eggs', 'chicken', 'rice']
    
    print("=" * 50)
    print("🛒 PRICE TRACKER")
    print("=" * 50)
    
    all_prices = {}
    
    for product in products:
        print(f"\n📦 Checking: {product.upper()}")
        print("-" * 30)
        
        # Get Coles price
        print("  🟢 Coles:")
        coles_price = await get_coles_price(product)
        
        # Get Woolworths price
        print("  🔴 Woolworths:")
        woolies_price = await get_woolworths_price(product)
        
        all_prices[product] = {
            'coles': coles_price,
            'woolworths': woolies_price,
            'best_store': 'Coles' if coles_price and (not woolies_price or coles_price < woolies_price) else 'Woolworths' if woolies_price else None,
            'best_price': min(filter(None, [coles_price, woolies_price])) if any([coles_price, woolies_price]) else None
        }
        
        # Show comparison
        if coles_price and woolies_price:
            if coles_price < woolies_price:
                print(f"  💰 Best: Coles (${coles_price} vs ${woolies_price})")
            else:
                print(f"  💰 Best: Woolworths (${woolies_price} vs ${coles_price})")
        elif coles_price:
            print(f"  💰 Best: Coles only (${coles_price})")
        elif woolies_price:
            print(f"  💰 Best: Woolworths only (${woolies_price})")
        else:
            print(f"  ❌ No prices found")
        
        # Wait between products to be nice to websites
        await asyncio.sleep(2)
    
    # Save results
    results = {
        'date': datetime.now().isoformat(),
        'prices': all_prices
    }
    
    with open('prices.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 50)
    print("✅ Results saved to prices.json")
    print("=" * 50)

if __name__ == '__main__':
    asyncio.run(main())
