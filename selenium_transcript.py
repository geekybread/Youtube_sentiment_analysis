from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def get_transcript(video_url, headless=True, timeout=15):
    """
    Extract transcript from a YouTube video URL.
    
    Args:
        video_url (str): YouTube video URL
        headless (bool): Run browser in headless mode (default: True)
        timeout (int): Maximum wait time for elements (default: 15 seconds)
    
    Returns:
        str: Combined transcript text, or None if extraction fails
    """
    driver = None
    try:
        # Setup Chrome options with anti-detection measures
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")  # Use new headless mode
        
        # Essential arguments for headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Faster loading
        
        # Anti-detection measures
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set a realistic user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Set window size for headless mode
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Execute script to hide webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        if not headless:
            driver.maximize_window()
        
        # Load YouTube video
        driver.get(video_url)
        wait = WebDriverWait(driver, timeout)
        
        # Wait longer for page to load in headless mode
        initial_wait = 5 if headless else 3
        time.sleep(initial_wait)
        
        # Click "More" to expand the description
        try:
            # Wait a bit more and try multiple selectors
            more_selectors = [
                'tp-yt-paper-button#expand',
                '#expand',
                'button#expand',
                '[aria-label*="more"]',
                'button[aria-label*="Show more"]'
            ]
            
            more_button = None
            for selector in more_selectors:
                try:
                    more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if more_button:
                # Scroll to element first
                driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                time.sleep(1)
                # Try JavaScript click if regular click fails
                try:
                    more_button.click()
                except:
                    driver.execute_script("arguments[0].click();", more_button)
                print("✅ Clicked 'More'")
                time.sleep(2)
            else:
                print("⚠️  'More' button not found, description might already be expanded")
        except Exception as e:
            print(f"⚠️  Could not click 'More' button: {e}")
            # Continue anyway, sometimes the description is already expanded
        
        # Scroll down to reveal "Show transcript"
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)
        
        # Click "Show transcript"
        try:
            # Try multiple selectors for the transcript button
            transcript_selectors = [
                "//button[.//span[text()='Show transcript']]",
                "//button[contains(@aria-label, 'transcript')]",
                "//button[.//span[contains(text(), 'transcript')]]",
                "//yt-button-renderer[contains(@data-target-id, 'transcript')]",
                "//button[contains(text(), 'Show transcript')]",
                "//*[contains(text(), 'Show transcript')]//ancestor::button[1]"
            ]
            
            transcript_button = None
            for selector in transcript_selectors:
                try:
                    transcript_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if transcript_button:
                # Scroll to element and click
                driver.execute_script("arguments[0].scrollIntoView(true);", transcript_button)
                time.sleep(1)
                try:
                    transcript_button.click()
                except:
                    driver.execute_script("arguments[0].click();", transcript_button)
                print("✅ Clicked 'Show transcript'")
                time.sleep(4 if headless else 3)  # Wait longer in headless mode
            else:
                print("❌ Could not find transcript button")
                return None
                
        except Exception as e:
            print(f"❌ Error clicking 'Show transcript': {e}")
            return None
        
        # Extract transcript segments
        try:
            # Wait for transcript panel to load
            time.sleep(2)
            
            # Try multiple selectors for transcript text
            transcript_selectors = [
                '//*[@id="content"]//yt-formatted-string[contains(@class, "segment-text")]',
                '//div[@id="transcript"]//yt-formatted-string',
                '//ytd-transcript-segment-renderer//yt-formatted-string'
            ]
            
            transcripts = []
            for selector in transcript_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        transcripts = elements
                        break
                except:
                    continue
            
            if not transcripts:
                print("❌ No transcript segments found")
                return None
            
            # Combine all transcript text
            transcript_text = []
            for segment in transcripts:
                text = segment.text.strip()
                if text:
                    transcript_text.append(text)
            
            combined_transcript = ' '.join(transcript_text)
            print(f"✅ Successfully extracted transcript ({len(transcript_text)} segments)")
            return combined_transcript
            
        except Exception as e:
            print(f"❌ Error extracting transcript: {e}")
            return None
    
    except Exception as e:
        print(f"❌ General error: {e}")
        return None
    
    finally:
        # Always close the browser
        if driver:
            driver.quit()

# Example usage
if __name__ == "__main__":
    video_url = "https://youtu.be/2USUfv7klr8?si=7sHCiVI-xS-8Ypg6"
    
    # Get transcript
    transcript = get_transcript(video_url, headless=True)  # Set headless=False to see browser
    
    if transcript:
        print("\n" + "="*50)
        print("TRANSCRIPT:")
        print("="*50)
        print(transcript)
        print("="*50)
        print(f"Total characters: {len(transcript)}")
    else:
        print("❌ Failed to extract transcript")