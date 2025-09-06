from playwright.sync_api import sync_playwright, expect
import uuid
import os

# --- Test Setup ---
base_url = 'http://127.0.0.1:5000'
unique_id = str(uuid.uuid4())[:8]
username = f"design_user_{unique_id}"
email = f"design_{unique_id}@example.com"
password = "password"

def register_and_login(page):
    """Registers and logs in a new user."""
    page.goto(f"{base_url}/auth/register")
    page.get_by_label("Username").fill(username)
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_label("Repeat Password").fill(password)
    page.get_by_role("button", name="Register").click()
    expect(page).to_have_url(f"{base_url}/auth/login")

    page.get_by_label("Username").fill(username)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Sign In").click()
    expect(page).to_have_url(f"{base_url}/index")
    print("User registered and logged in.")

def create_sample_with_image(page):
    """Creates a sample, uploads an image, and returns the sample page URL."""
    # Create sample
    sample_name = f"SampleForDesignTest_{str(uuid.uuid4())[:4]}"
    page.get_by_role("link", name="Create a New Sample").click()
    expect(page).to_have_url(f"{base_url}/create_sample")
    page.get_by_label("Sample Name").fill(sample_name)
    page.get_by_role("button", name="Create Sample").click()
    expect(page).to_have_url(f"{base_url}/index")
    print(f"Created sample '{sample_name}'")

    # Go to the sample page
    page.get_by_role("link", name=sample_name).click()

    # Upload image
    image_path = 'test_image.png'
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Test image '{image_path}' not found.")

    page.get_by_label("Image").set_input_files(image_path)
    page.get_by_role("button", name="Upload").click()
    print("Image uploaded.")
    return page.url

def test_responsive_design():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        register_and_login(page)
        sample_page_url = create_sample_with_image(page)

        # Navigate back to the sample page to ensure we have the final state
        page.goto(sample_page_url)
        expect(page.get_by_role("heading", name=f"Sample: SampleForDesignTest_")).to_be_visible()

        # Take a screenshot of the desktop view
        screenshot_path = "jules-scratch/verification/desktop_view.png"
        page.screenshot(path=screenshot_path)
        print(f"Desktop screenshot saved to {screenshot_path}")

        # Emulate a mobile device and take another screenshot
        page.set_viewport_size({"width": 375, "height": 667}) # iPhone 6/7/8 size
        mobile_screenshot_path = "jules-scratch/verification/mobile_view.png"
        page.screenshot(path=mobile_screenshot_path)
        print(f"Mobile screenshot saved to {mobile_screenshot_path}")

        browser.close()

if __name__ == "__main__":
    # We need the test image for this script
    if not os.path.exists('test_image.png'):
        print("Generating test image...")
        import numpy as np
        import cv2
        image = np.zeros((100, 100, 3), np.uint8)
        cv2.circle(image, (50, 50), 10, (255, 255, 255), -1)
        cv2.imwrite("test_image.png", image)
    test_responsive_design()
