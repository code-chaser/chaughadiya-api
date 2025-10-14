from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://localhost:8080/")
    page.get_by_role("button", name="Get Chaughadiya").click()
    page.wait_for_timeout(2000)  # Wait for results to load
    page.screenshot(path="jules-scratch/verification/verification.png")
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
