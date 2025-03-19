import os
import time
import pickle
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
import pathlib

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get URLs from environment variables
    timewall_url = os.getenv("TIMEWALL_URL", "https://timewall.io/clicks")
    
    if not timewall_url:
        print("Error: URLs not found in .env file")
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
    
    # Add options to help avoid security warnings
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
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })
        
        print("Chrome browser started successfully")
    except Exception as e:
        print(f"Error starting Chrome browser: {e}")
        return
    
    try:
        # Open Timewall URL
        print(f"Opening {timewall_url}...")
        driver.execute_script(f"window.open('{timewall_url}', '_blank');")
        
        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[1])
        
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
        
        # Wait for user to set up Timewall
        input("Please set up Timewall and press Enter to continue...")
        
        print("Setup complete. Ready for automation.")
        
        # Keep the browser open until user decides to close
        input("Press Enter to close the browser...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Save cookies before closing
        try:
            # Save FreeCash cookies
            driver.switch_to.window(driver.window_handles[0])
            freecash_cookies = driver.get_cookies()
            with open(os.path.join(cookies_dir, "freecash_cookies.pkl"), "wb") as f:
                pickle.dump(freecash_cookies, f)
            
            # Also save as JSON for debugging
            with open(os.path.join(cookies_dir, "freecash_cookies.json"), "w") as f:
                json.dump(freecash_cookies, f, indent=2)
            
            # Save Timewall cookies
            driver.switch_to.window(driver.window_handles[1])
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

if __name__ == "__main__":
    main()
