# -*- coding: utf-8 -*-
"""
Advanced Scraping Bot - Mercado Livre
Version: 4.0 (Optimized)
Description: Collects product data from Mercado Livre, including affiliate/sharing links.
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pyperclip
import time
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Tuple, Optional


# --- Profile Configuration ---
# 1. This is the path to the PARENT "User Data" folder
#    (Use 'r' before the string to handle backslashes in Windows)
user_data_path = r"C:\Users\spine\AppData\Local\Google\Chrome\User Data"

# 2. This is the specific profile folder you want to use
profile_name = "Profile 3"
# -----------------------------

# 2. Configure Chrome Options to load the profile
chrome_options = Options()

# Add the argument for the user data directory
# This loads all profiles and settings
chrome_options.add_argument(f"user-data-dir={user_data_path}")

# Add the argument to select the specific profile within User Data
chrome_options.add_argument(f"profile-directory={profile_name}")

# ============================================================================
# GLOBAL CONFIGURATION
# ============================================================================

CATEGORY_URLS = [
    "https://www.mercadolivre.com.br/ofertas?category=MLB1367&container_id=MLB1279748-1"
]

# Wait times (in seconds)
WAIT_TIME = 30
SHORT_WAIT_TIME = 15
SCROLL_REPETITIONS = 30
SCROLL_PAUSE = 1.5

# Limits
MAX_SHARE_ATTEMPTS = 3
DESCRIPTION_LIMIT = 500

# ============================================================================
# CSS/XPATH SELECTORS
# ============================================================================

class Selectors:
    """Centralizes all website selectors"""
    
    # Product listing
    PRODUCT_BLOCK = (By.CSS_SELECTOR, "div.andes-card")
    LINK = (By.CSS_SELECTOR, "a.poly-component__title")
    TITLE = (By.CSS_SELECTOR, "a.poly-component__title")
    OLD_PRICE = (By.CSS_SELECTOR, "s.andes-money-amount--previous")
    NEW_PRICE = (By.CSS_SELECTOR, "span.andes-money-amount__fraction")
    INSTALLMENTS = (By.CSS_SELECTOR, "span.poly-price__installments")
    IMAGE_CARD = (By.CSS_SELECTOR, "img.poly-component__picture")
    RATING = (By.CSS_SELECTOR, "span.poly-reviews__rating")
    
    # Detail Page
    DESCRIPTION = (By.CLASS_NAME, "ui-pdp-description__content")
    
    # Share Buttons (multiple strategies)
    SHARE_BUTTON_XPATH = (By.XPATH, "//span[contains(text(), 'Compartilhar')]/ancestor::button")
    SHARE_BUTTON_CSS = (By.CSS_SELECTOR, "button[data-testid='generate_link_button'], button[class*='share'], button[aria-label*='Compartilhar']")
    COPY_BUTTON = (By.CSS_SELECTOR, "button[data-testid='copy-button__label_link'], button[class*='copy']")
    LINK_TEXTAREA = (By.CSS_SELECTOR, "textarea[data-testid='text-field__label_link'], textarea, input[type='text']")


# ============================================================================
# AUXILIARY FUNCTIONS
# ============================================================================

def get_text_or_default(element, by_tuple: Tuple, default: str = "Not Found") -> str:
    """Extracts text from an element or returns a default value"""
    try:
        return element.find_element(*by_tuple).text.strip().replace("\n", " ")
    except Exception:
        return default


def get_attr_or_default(element, by_tuple: Tuple, attr: str = "href", default: str = "Not Found") -> str:
    """Extracts an attribute from an element or returns a default value"""
    try:
        return element.find_element(*by_tuple).get_attribute(attr)
    except Exception:
        return default


def save_error_screenshot(driver, base_name: str) -> str:
    """Saves a screenshot with a timestamp for debugging"""
    timestamp = int(time.time())
    file_name = f"{base_name}_{timestamp}.png"
    try:
        driver.save_screenshot(file_name)
        return file_name
    except Exception:
        return "Could not save screenshot"


# ============================================================================
# DRIVER CONFIGURATION
# ============================================================================

def initialize_driver() -> webdriver.Chrome:
    """
    Initializes the ChromeDriver with optimized and anti-detection settings.
    
    ⚠️ IMPORTANT: Close ALL Chrome windows before running!
    
    Returns:
        webdriver.Chrome: Configured driver instance
        
    Raises:
        Exception: If there is an initialization error
    """
    print("\n" + "="*80)
    print("🔧 INITIALIZING CHROMEDRIVER")
    print("="*80)
    
    global chrome_options # Use the global options defined with the profile config
    options = chrome_options # Start with the options already configured for the profile

    # Anti-detection settings
    print("  → Applying anti-detection settings...")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    
    # Remove automation detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Realistic user agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")

    # Debugging port (tries multiple ports)
    print("  → Configuring debugging port...")
    port_found = False
    for port in [9223, 9224, 9225, 9226, 9227]:
        try:
            options.add_argument(f"--remote-debugging-port={port}")
            print(f"  ✅ Port {port} configured")
            port_found = True
            break
        except Exception:
            continue
    
    if not port_found:
        print("  ⚠️ No debugging port available")

    # Initialization
    try:
        print("  → Installing/Updating ChromeDriver...")
        service = ChromeService(ChromeDriverManager().install())
        
        print("  → Starting browser...")
        driver = webdriver.Chrome(service=service, options=options)
        
        # Remove automation properties via JavaScript
        print("  → Applying anti-detection masks via JavaScript...")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("\n" + "✅"*40)
        print("✅ DRIVER STARTED SUCCESSFULLY!")
        print("✅"*40 + "\n")
        
        return driver
        
    except Exception as e:
        print("\n" + "❌"*40)
        print(f"❌ ERROR STARTING DRIVER")
        print("❌"*40)
        print(f"\n🔴 Error: {str(e)}\n")
        print("💡 POSSIBLE SOLUTIONS:")
        print("  1. Close ALL Chrome windows/processes")
        print("  2. Run the script as Administrator")
        print("  3. Temporarily disable antivirus")
        print("  4. Update Google Chrome to the latest version")
        print("  5. If you are using a Chrome profile, comment out the user-data-dir lines")
        print("  6. Restart the computer")
        print("  7. Check for pending Windows updates")
        print("\n" + "="*80 + "\n")
        raise


# ============================================================================
# NAVIGATION FUNCTIONS
# ============================================================================

def scroll_page(driver, repetitions: int = SCROLL_REPETITIONS) -> None:
    """
    Performs a smooth scroll on the page to dynamically load products.
    
    Args:
        driver: WebDriver instance
        repetitions: Maximum number of scrolls
    """
    print(f"\n  📜 Starting page scroll (max: {repetitions} repetitions)...")
    last_height = 0
    scrolls_without_change = 0
    
    for i in range(repetitions):
        # Scroll to the end
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)
        
        # Check new height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if i % 5 == 0:  # Log every 5 scrolls
            print(f"    → Scroll {i+1}/{repetitions} | Height: {new_height}px")
        
        # Check if the end has been reached
        if new_height == last_height:
            scrolls_without_change += 1
            if scrolls_without_change >= 3:
                print(f"  ✅ End of page reached (scroll {i+1})")
                break
        else:
            scrolls_without_change = 0
            
        last_height = new_height
    
    # Scroll back to the top
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)


# ============================================================================
# DATA COLLECTION FUNCTIONS
# ============================================================================

def collect_basic_data(driver, wait: WebDriverWait, wait_short: WebDriverWait, url: str) -> List[Dict]:
    """
    Collects basic product data from the listing page.
    
    Args:
        driver: WebDriver instance
        wait: Long WebDriverWait
        wait_short: Short WebDriverWait
        url: Category URL
        
    Returns:
        List of dictionaries with product data
    """
    products = []
    
    # Extract category from the URL
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    category = query_params.get('category', query_params.get('container_id', ['unknown_category']))[0]

    print("\n" + "━"*80)
    print(f"📂 CATEGORY: {category}")
    print(f"🔗 URL: {url}")
    print("━"*80)
    
    # Access the page
    print("\n  → Loading page...")
    driver.get(url)

    try:
        # Wait for products to load
        print("  → Waiting for products to load...")
        wait.until(EC.presence_of_element_located(Selectors.PRODUCT_BLOCK))
        time.sleep(2)
        
        # Scroll to load more products
        scroll_page(driver)

        # Find all product blocks
        blocks = driver.find_elements(*Selectors.PRODUCT_BLOCK)
        total_products = len(blocks)
        print(f"\n  ✅ {total_products} products found!")
        print(f"\n  → Extracting basic data...")

        for idx, block in enumerate(blocks, 1):
            if idx % 10 == 0:
                print(f"    → Processing product {idx}/{total_products}...")
                
            product = {
                "ID": idx,
                "Category": category,
                "Title": get_text_or_default(block, Selectors.TITLE),
                "Original_Value": get_text_or_default(block, Selectors.OLD_PRICE),
                "Discount_Value": get_text_or_default(block, Selectors.NEW_PRICE),
                "Installments": get_text_or_default(block, Selectors.INSTALLMENTS),
                "Link": get_attr_or_default(block, Selectors.LINK),
                "Image_Card": get_attr_or_default(block, Selectors.IMAGE_CARD, "src"),
                "Rating": get_text_or_default(block, Selectors.RATING),
                "Description": "Pending",
                "Affiliate_Link": "Pending"
            }
            products.append(product)
        
        print(f"  ✅ Basic data collected: {len(products)} products")
            
    except Exception as e:
        print(f"\n  ❌ ERROR processing category {category}")
        print(f"  🔴 Details: {str(e)}")
        screenshot = save_error_screenshot(driver, f"error_category_{category}")
        print(f"  📸 Screenshot: {screenshot}")

    return products


def try_find_share_button(driver, wait_short: WebDriverWait):
    """
    Attempts to find the share button using multiple strategies.
    
    Returns:
        WebElement or None
    """
    strategies = [
        ("XPath (text)", Selectors.SHARE_BUTTON_XPATH),
        ("CSS Selector", Selectors.SHARE_BUTTON_CSS),
        ("JavaScript (text search)", None),
        ("Button scan", None)
    ]
    
    for strategy_name, selector in strategies:
        print(f"    🔍 Attempt: {strategy_name}...")
        
        try:
            if selector:
                # Strategies with a defined selector
                button = wait_short.until(EC.element_to_be_clickable(selector))
                print(f"    ✅ Button found via {strategy_name}!")
                return button
                
            elif "JavaScript" in strategy_name:
                # Search via JavaScript
                button = driver.execute_script("""
                    return Array.from(document.querySelectorAll('button')).find(btn => 
                        btn.textContent.includes('Compartilhar') || 
                        btn.getAttribute('aria-label')?.includes('Compartilhar') ||
                        btn.getAttribute('data-testid')?.includes('share')
                    );
                """)
                if button:
                    print(f"    ✅ Button found via {strategy_name}!")
                    return button
                    
            else:
                # Scan all buttons
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    try:
                        text = btn.text.lower()
                        if 'compartilhar' in text or 'share' in text:
                            print(f"    ✅ Button found via {strategy_name}!")
                            return btn
                    except Exception:
                        continue
                        
        except Exception:
            print(f"    ⚠️ {strategy_name} failed")
            continue
    
    return None


def get_affiliate_link(driver, wait_short: WebDriverWait, product: Dict) -> str:
    """
    Gets the product's affiliate/sharing link by clicking Share.
    
    Args:
        driver: WebDriver instance
        wait_short: Short WebDriverWait
        product: Dictionary with product data
        
    Returns:
        Affiliate link or original link as a fallback
    """
    try:
        # Scroll to a strategic position
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
        time.sleep(2)
        
        # Try to find the share button
        share_button = try_find_share_button(driver, wait_short)
        
        if not share_button:
            print("    ❌ 'Share' button not found using any strategy")
            return product['Link']
        
        # Scroll to the button and click
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", share_button)
        time.sleep(1)
        
        # Try to click
        try:
            share_button.click()
            print("    ✅ 'Share' button clicked!")
        except Exception:
            driver.execute_script("arguments[0].click();", share_button)
            print("    ✅ Button clicked via JavaScript!")
        
        time.sleep(3)

        # Wait for the modal to appear
        try:
            link_textarea = wait_short.until(EC.presence_of_element_located(Selectors.LINK_TEXTAREA))
            print("    ✅ Share modal opened!")
            time.sleep(2)
            
            # Try to click the copy button
            try:
                copy_button = None
                
                # Try via CSS
                try:
                    copy_button = driver.find_element(*Selectors.COPY_BUTTON)
                except Exception:
                    pass
                
                # Try via JavaScript
                if not copy_button:
                    copy_button = driver.execute_script("""
                        return Array.from(document.querySelectorAll('button')).find(btn => 
                            btn.textContent.includes('Copiar') || 
                            btn.getAttribute('data-testid')?.includes('copy')
                        );
                    """)
                
                if copy_button:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", copy_button)
                    time.sleep(0.5)
                    
                    try:
                        copy_button.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", copy_button)
                    
                    print("    ✅ 'Copy' button clicked!")
                    time.sleep(2)
                    
                    # Check clipboard
                    clipboard_link = pyperclip.paste()
                    if clipboard_link and clipboard_link.startswith("http"):
                        print(f"    🔗 Link captured via clipboard!")
                        return clipboard_link
                
                # Fallback: read from textarea
                textarea_link = link_textarea.get_attribute("value")
                if textarea_link and textarea_link.startswith("http"):
                    print(f"    🔗 Link captured from textarea!")
                    return textarea_link
                    
            except Exception as e:
                print(f"    ⚠️ Error copying: {str(e)}")
                
            # Close modal
            try:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(1)
            except Exception:
                pass
                
        except Exception as e:
            print(f"    ⚠️ Modal not found: {str(e)}")
            
    except Exception as e:
        print(f"    ⚠️ General error: {str(e)}")
    
    return product['Link']


def collect_details(driver, wait: WebDriverWait, wait_short: WebDriverWait, products: List[Dict]) -> List[Dict]:
    """
    Collects individual details for each product (description and affiliate link).
    
    Args:
        driver: WebDriver instance
        wait: Long WebDriverWait
        wait_short: Short WebDriverWait
        products: List of products with basic data
        
    Returns:
        List of products with complete data
    """
    total = len(products)
    print("\n" + "="*80)
    print(f"📋 COLLECTING DETAILS FOR {total} PRODUCTS")
    print("="*80)
    
    
    for i, product in enumerate(products, 1):
        print(f"\n{'─'*80}")
        print(f"📦 PRODUCT {i}/{total}")
        print(f"📝 {product['Title'][:70]}...")
        print(f"{'─'*80}")

        try:
            # Access product page
            print(f"\n  → Accessing product page...")
            driver.get(product['Link'])
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)

            # Collect description
            print(f"  → Collecting description...")
            try:
                description_element = driver.find_element(*Selectors.DESCRIPTION)
                description = description_element.text.strip().replace("\n", " ")
                product["Description"] = description[:DESCRIPTION_LIMIT]
                print(f"    ✅ Description collected ({len(description)} characters)")
            except Exception:
                print(f"    ⚠️ Description not found")
                product["Description"] = "Not available"

            # Collect affiliate link
            print(f"\n  → Getting affiliate link...")
            product["Affiliate_Link"] = get_affiliate_link(driver, wait_short, product)
            
            if product["Affiliate_Link"] != product['Link']:
                print(f"    ✅ Affiliate link obtained successfully!")
            else:
                print(f"    ⚠️ Using original link as fallback")

            print(f"\n  {'✓'*40}")
            print(f"  ✅ PRODUCT {i}/{total} COMPLETED!")
            print(f"  {'✓'*40}")

        except Exception as e:
            print(f"\n  ❌ ERROR processing product {i}")
            print(f"  🔴 Details: {str(e)}")
            screenshot = save_error_screenshot(driver, f"error_product_{i}")
            print(f"  📸 Screenshot: {screenshot}")
            
            # Set default values in case of error
            if product.get("Description") == "Pending":
                product["Description"] = "Error collecting"
            if product.get("Affiliate_Link") == "Pending":
                product["Affiliate_Link"] = product['Link']

    return products


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Main scraper function.
    Orchestrates the entire data collection process.
    """
    print("\n" + "="*80)
    print("🚀 SCRAPING BOT - MERCADO LIVRE v4.0")
    print("="*80)
    print("\n📋 CONFIGURATION:")
    print(f"  • Categories to process: {len(CATEGORY_URLS)}")
    print(f"  • Max wait time: {WAIT_TIME}s")
    print(f"  • Short wait time: {SHORT_WAIT_TIME}s")
    print(f"  • Scroll repetitions: {SCROLL_REPETITIONS}")
    print(f"  • Description limit: {DESCRIPTION_LIMIT} characters")
    print("\n" + "="*80 + "\n")
    
    input("⚠️ IMPORTANT: Close ALL Chrome windows and press ENTER to continue...")
    
    driver = None
    all_products = []
    
    try:
        # Initialize driver
        driver = initialize_driver()
        wait = WebDriverWait(driver, WAIT_TIME)
        wait_short = WebDriverWait(driver, SHORT_WAIT_TIME)

        # Process each category
        for idx, url in enumerate(CATEGORY_URLS, 1):
            print(f"\n{'█'*80}")
            print(f"█ PROCESSING CATEGORY {idx}/{len(CATEGORY_URLS)}")
            print(f"{'█'*80}")
            
            # Collect basic data
            basic_products = collect_basic_data(driver, wait, wait_short, url)
            
            if basic_products:
                # Collect details
                complete_products = collect_details(driver, wait, wait_short, basic_products)
                all_products.extend(complete_products)
                
                print(f"\n{'✅'*40}")
                print(f"✅ Category {idx} COMPLETED! {len(complete_products)} products processed.")
                print(f"{'✅'*40}\n")
            else:
                print(f"\n⚠️ No products found in category {idx}\n")

    except KeyboardInterrupt:
        print("\n\n⚠️ PROCESS INTERRUPTED BY USER (Ctrl+C)")
        
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        if driver:
            screenshot_name = f"fatal_error_{int(time.time())}.png"
            driver.save_screenshot(screenshot_name)
            print(f"📸 Error screenshot: {screenshot_name}")
            
    finally:
        if driver:
            print("\n🛑 Closing browser...")
            driver.quit()
            print("✅ Browser closed.\n")

    # Save results
    print("\n" + "="*80)
    print("💾 SAVING RESULTS")
    print("="*80)
    
    if all_products:
        try:
            df = pd.DataFrame(all_products)
            
            # Reorganize columns
            column_order = [
                "ID", "Category", "Title", 
                "Original_Value", "Discount_Value", "Installments",
                "Rating", "Link", "Affiliate_Link", 
                "Image_Card", "Description"
            ]
            df = df[column_order]
            
            # File name with timestamp
            file_name = f"mercadolivre_products_{time.strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            print(f"\n  → Creating Excel file...")
            df.to_excel(file_name, index=False, engine='openpyxl')
            
            # Statistics
            with_affiliate_link = sum(1 for p in all_products if p['Affiliate_Link'] != p['Link'])
            with_description = sum(1 for p in all_products if p['Description'] not in ['Pending', 'Not available', 'Error collecting'])
            
            print(f"\n{'🎉'*40}")
            print(f"✅ PROCESS COMPLETED SUCCESSFULLY!")
            print(f"{'🎉'*40}")
            print(f"\n📊 STATISTICS:")
            print(f"  • Total products: {len(all_products)}")
            print(f"  • With affiliate link: {with_affiliate_link} ({with_affiliate_link/len(all_products)*100:.1f}%)")
            print(f"  • With description: {with_description} ({with_description/len(all_products)*100:.1f}%)")
            print(f"  • File generated: {file_name}")
            print(f"\n{'='*80}\n")
            
        except Exception as e:
            print(f"\n❌ ERROR saving Excel file: {e}")
            print(f"💡 Data was collected but could not be saved.\n")
            
    else:
        print("\n" + "⚠️"*40)
        print("⚠️ NO PRODUCTS WERE COLLECTED!")
        print("⚠️"*40)
        print("\n💡 VERIFICATION CHECKLIST:")
        print("  ✓ Is the internet connection active?")
        print("  ✓ Are the category URLs correct and accessible?")
        print("  ✓ Is the Mercado Livre site online?")
        print("  ✓ Are the CSS selectors still valid? (site might have changed)")
        print("  ✓ Check saved screenshots for visual analysis")
        print(f"\n{'='*80}\n")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "⚠️"*40)
        print("⚠️ PROCESS INTERRUPTED BY USER (Ctrl+C)")
        print("⚠️"*40 + "\n")
    except Exception as e:
        print("\n\n" + "❌"*40)
        print(f"❌ UNHANDLED FATAL ERROR")
        print("❌"*40)
        print(f"\n🔴 Error: {str(e)}")
        print("\n💡 Contact technical support with this error message.\n")