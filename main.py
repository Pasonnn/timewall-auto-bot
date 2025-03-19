import os
import time
import pickle
import json
import random
import pathlib
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from controller import click_view, read_timer, exit_tab

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
    
    # Set up undetected Chrome options
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--start-maximized")  # Start with maximized browser
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # Set up undetected Chrome driver
    try:
        driver = uc.Chrome(options=chrome_options)
        print("Undetected Chrome browser started successfully")
    except Exception as e:
        print(f"Error starting undetected Chrome browser: {e}")
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
        
    
        # Wait for user to set up Timewall if needed
        input("Please set up Timewall if needed and press Enter to continue...")
        
        print("Setup complete. Ready for automation.")
        
        # Main automation loop
        while True:
            try:
                # Read initial timer value
                timer_value = read_timer(driver)
                if timer_value == -1:
                    print("Could not read timer, retrying...")
                    time.sleep(5)
                    continue

                # Click view button and wait for timer
                if click_view(driver):
                    print(f"Waiting {timer_value} seconds...")
                    time.sleep(timer_value+1)
                    
                    # Close tab and return to main window
                    if not exit_tab(driver):
                        print("Error closing tab, trying to recover...")
                        # Try to switch back to main window
                        if len(driver.window_handles) > 0:
                            driver.switch_to.window(driver.window_handles[0])
                
                # Add small random delay between iterations
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"Error in automation loop: {e}")
                time.sleep(5)  # Wait before retrying on error
        
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

if __name__ == "__main__":
    main()
