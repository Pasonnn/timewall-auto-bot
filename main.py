import os
import time
import pickle
import json
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
import pathlib

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get URLs from environment variables
    timewall_url = os.getenv("TIMEWALL_URL", "https://timewall.io/clicks")
    
    if not timewall_url:
        print("Error: URL not found in .env file")
        return
    
    # Create directories to store browser data and cookies
    user_data_dir = os.path.join(pathlib.Path.home(), "timewall-bot-chrome-data")
    cookies_dir = os.path.join(pathlib.Path.home(), "timewall-bot-cookies")
    os.makedirs(user_data_dir, exist_ok=True)
    os.makedirs(cookies_dir, exist_ok=True)
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Start with maximized browser
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # Add options to help avoid security warnings and detection
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Set a realistic user agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Uncomment the line below if you want to run in headless mode later
    # chrome_options.add_argument("--headless=new")
    
    # Set up Chrome driver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute CDP commands to prevent detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                // Overwrite the 'navigator.webdriver' property to prevent detection
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Overwrite the 'navigator.plugins' to make it look more realistic
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Overwrite the 'navigator.languages' property
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en', 'es']
                });
                
                // Prevent detection via permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({state: Notification.permission}) :
                        originalQuery(parameters)
                );
            """
        })
        
        print("Chrome browser started successfully")
    except Exception as e:
        print(f"Error starting Chrome browser: {e}")
        return
    
    try:
        # Open Timewall URL directly in the first tab
        print(f"Opening {timewall_url}...")
        driver.get(timewall_url)
        
        # Load Timewall cookies if they exist
        timewall_cookies_path = os.path.join(cookies_dir, "timewall_cookies.pkl")
        if os.path.exists(timewall_cookies_path):
            try:
                with open(timewall_cookies_path, "rb") as f:
                    cookies = pickle.load(f)
                    for cookie in cookies:
                        try:
                            driver.add_cookie(cookie)
                        except Exception:
                            pass
                driver.refresh()  # Refresh to apply cookies
                print("Loaded saved Timewall session")
            except Exception as e:
                print(f"Error loading cookies: {e}")
        
        # Wait for page to load and handle Cloudflare if needed
        handle_cloudflare(driver)
        
        # Wait for user to set up Timewall if needed
        input("Please set up Timewall if needed and press Enter to continue...")
        
        print("Setup complete. Ready for automation.")
        
        # Keep the browser open until user decides to close
        input("Press Enter to close the browser...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Save cookies before closing
        try:
            # Save Timewall cookies
            timewall_cookies = driver.get_cookies()
            with open(os.path.join(cookies_dir, "timewall_cookies.pkl"), "wb") as f:
                pickle.dump(timewall_cookies, f)
            
            # Also save as JSON for debugging
            with open(os.path.join(cookies_dir, "timewall_cookies.json"), "w") as f:
                json.dump(timewall_cookies, f, indent=2)
                
            print("Browser session saved successfully")
        except Exception as e:
            print(f"Error saving browser session: {e}")
        
        # Close the browser
        driver.quit()
        print("Browser closed.")

def handle_cloudflare(driver, timeout=30):
    """Handle Cloudflare challenges by waiting and helping with checkbox if needed."""
    try:
        print("Checking for Cloudflare challenge...")
        
        # Wait for Cloudflare to load
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "challenge-form"))
        )
        
        print("Cloudflare challenge detected. Waiting for it to process...")
        
        # Check for checkbox challenge
        try:
            checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='checkbox']"))
            )
            print("Cloudflare checkbox found. Please click it manually.")
            input("Press Enter after clicking the checkbox...")
        except TimeoutException:
            # No checkbox found, might be automatic challenge
            print("No checkbox found. Waiting for automatic verification...")
        
        # Wait for the challenge to complete
        WebDriverWait(driver, timeout).until_not(
            EC.presence_of_element_located((By.ID, "challenge-form"))
        )
        
        print("Cloudflare challenge completed successfully.")
        
    except TimeoutException:
        # No Cloudflare challenge detected or it timed out
        print("No Cloudflare challenge detected or it timed out.")
    except Exception as e:
        print(f"Error handling Cloudflare: {e}")

if __name__ == "__main__":
    main()
