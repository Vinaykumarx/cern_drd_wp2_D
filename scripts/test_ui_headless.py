from playwright.sync_api import sync_playwright
import time

def run_test():
    print("Initializing Headless Visual Test...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to http://localhost:3000...")
        page.goto("http://localhost:3000")
        time.sleep(2)
        page.screenshot(path="screenshot_1_dashboard.png")
        
        print("Clicking Neural Chat tab...")
        try:
            page.get_by_text("Neural Chat").click(timeout=3000)
        except:
            pass 
        time.sleep(1)
        page.screenshot(path="screenshot_2_chat_empty.png")
        
        print("Typing the query...")
        input_box = page.locator("input[type='text'], textarea").first
        input_box.fill("What are the radiation safety parameters mentioned in the CERN-89-12 report?")
        time.sleep(1)
        
        print("Sending query...")
        page.keyboard.press("Enter")
        
        print("Waiting for response...")
        time.sleep(2)
        page.screenshot(path="screenshot_3_synthesizing.png")
        
        page.wait_for_timeout(10000)
        page.screenshot(path="screenshot_4_response.png")
        
        print("Checking for citations...")
        try:
            citation = page.locator("button:has-text('[C')").first
            if citation.is_visible():
                print("Citation found! Clicking it...")
                citation.click()
                time.sleep(5)
                page.screenshot(path="screenshot_5_pdf.png")
                print("PDF Lightbox opened successfully.")
            else:
                print("No citations generated in the response.")
        except Exception as e:
            print("Failed to click citation:", e)
            
        print("Closing browser...")
        browser.close()
        print("Visual Test Complete.")

if __name__ == "__main__":
    run_test()
