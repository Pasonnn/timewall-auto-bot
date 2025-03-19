import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


def click_view(driver, timeout=10):
    """
    Find and click the View button on the Timewall page.
    
    Args:
        driver: The WebDriver instance
        timeout: Maximum time to wait for the button in seconds
    
    Returns:
        bool: True if button was clicked successfully, False otherwise
    """
    try:
        print("Looking for View button...")
        
        # Wait for the View button to be clickable
        view_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.clickBtn[ad-timer]"))
        )
        
        # Get button attributes for logging
        ad_id = view_button.get_attribute("ad-id")
        ad_timer = view_button.get_attribute("ad-timer")
        print(f"Found View button with timer: {ad_timer}s, ID: {ad_id}")
        
        # Add some random delay before clicking to appear more human-like
        time.sleep(random.uniform(0.5, 2.0))
        
        # Click the button
        view_button.click()
        print("Successfully clicked View button")
        
        # Switch to the new tab that opened
        time.sleep(1)  # Wait for new tab to open
        driver.switch_to.window(driver.window_handles[-1])
        print("Switched to new tab")
        
        return True
    except Exception as e:
        print(f"Error clicking View button: {e}")
        return False

def read_timer(driver, timeout=5):
    """
    Read the timer value from the Timewall page.
    
    Args:
        driver: The WebDriver instance
        timeout: Maximum time to wait for the timer in seconds
    
    Returns:
        int: The timer value in seconds, or -1 if not found
    """
    try:
        # Wait for the timer element to be present
        timer_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.clickTimer"))
        )
        
        # Get the timer value
        timer_value = int(timer_element.text.strip())
        print(f"Current timer value: {timer_value}s")
        return timer_value
    except Exception as e:
        print(f"Error reading timer: {e}")
        return -1

def exit_tab(driver):
    """
    Close the current tab and switch back to the previous tab.
    
    Args:
        driver: The WebDriver instance
    
    Returns:
        bool: True if tab was closed successfully, False otherwise
    """
    try:
        # Store the current window handle
        current_handle = driver.current_window_handle
        
        # Store all window handles
        handles = driver.window_handles
        
        # Send Ctrl+W to close the current tab
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('w').key_up(Keys.CONTROL).perform()
        print("Sent Ctrl+W to close current tab")
        
        # Wait for the tab to close
        time.sleep(1)
        
        # Check if the tab was closed
        if len(driver.window_handles) < len(handles):
            # Switch back to the previous tab
            driver.switch_to.window(driver.window_handles[0])
            print("Switched back to main tab")
            return True
        else:
            # Try alternative method to close tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            print("Used driver.close() to close tab")
            return True
    except Exception as e:
        print(f"Error closing tab: {e}")
        
        # Try to recover by switching to the first tab if available
        try:
            if len(driver.window_handles) > 0:
                driver.switch_to.window(driver.window_handles[0])
                print("Recovered by switching to first available tab")
                return True
        except:
            pass
            
        return False