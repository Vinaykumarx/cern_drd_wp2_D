from playwright.sync_api import sync_playwright
import time

def run_test():
    print("Initializing Visual Test...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        print("Navigating to http://localhost:3000...")
        page.goto("http://localhost:3000")
        time.sleep(2)
        
        print("Clicking Neural Chat tab...")
        # Find the Neural Chat tab/button. It might be just "chat" or "Neural Chat"
        # We can look for text "Neural Chat"
        try:
            page.get_by_text("Neural Chat").click(timeout=3000)
        except:
            pass # might already be on it
        time.sleep(1)
        
        print("Typing the query...")
        input_box = page.locator("input[type='text'], textarea").first
        input_box.fill("What are the radiation safety parameters mentioned in the CERN-89-12 report?")
        time.sleep(1)
        
        print("Sending query...")
        page.keyboard.press("Enter")
        
        print("Waiting for response...")
        # Wait up to 30 seconds for the response
        page.wait_for_timeout(10000)
        
        print("Checking for citations...")
        try:
            # Look for button that contains "[C"
            citation = page.locator("button:has-text('[C')").first
            if citation.is_visible():
                print("Citation found! Clicking it...")
                citation.click()
                time.sleep(5)
                print("PDF Lightbox opened successfully.")
            else:
                print("No citations generated in the response.")
        except Exception as e:
            print("Failed to click citation:", e)
            
        print("Closing browser in 5 seconds...")
        time.sleep(5)
        browser.close()
        print("Visual Test Complete.")

if __name__ == "__main__":
    run_test()
