import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            # The frontend is served by Nginx on port 8080
            await page.goto("http://localhost:8080/")

            # Wait for the main content to be visible to ensure the page is loaded
            await page.wait_for_selector("main", timeout=15000)
            print("Page loaded successfully.")

            # Define the file path
            file_path = "test_data.xlsx"

            # Type the command in the chat to open the data source modal
            chat_input = page.get_by_placeholder("Escribe tu mensaje o usa el micrófono...")
            await chat_input.fill("carga un archivo")
            await chat_input.press("Enter")
            print("Message sent to open data source modal.")

            # Wait for the modal to appear. Corrected the title selector.
            await page.wait_for_selector("h2:has-text('Seleccionar Origen de Datos')", timeout=10000)
            print("Data source modal is visible.")

            # The file input is not directly visible, we need to find the button
            # that triggers it. The "Cargar Archivo" button is the one.
            # We'll use a promise to handle the file chooser dialog.
            async with page.expect_file_chooser() as fc_info:
                # Click the "Cargar Archivo" button inside the modal
                await page.get_by_text("Cargar Archivo").first.click()

            file_chooser = await fc_info.value
            await file_chooser.set_files(file_path)
            print(f"File '{file_path}' selected for upload.")

            # After upload, the modal should close and the UI should reflect the loaded data.
            # We will wait for the toast notification confirming the upload.
            await page.wait_for_selector("text=/Archivo 'test_data.xlsx' cargado/i", timeout=15000)
            print("Toast notification found. Upload confirmed.")

            # Take a screenshot to verify the successful upload
            screenshot_path = "/home/jules/verification/e2e_upload_success.png"
            await page.screenshot(path=screenshot_path)
            print(f"Screenshot taken successfully at {screenshot_path}")

        except Exception as e:
            error_screenshot_path = "/home/jules/verification/e2e_upload_error.png"
            await page.screenshot(path=error_screenshot_path)
            print(f"An error occurred: {e}")
            print(f"Error screenshot taken at {error_screenshot_path}")
        finally:
            await browser.close()

if __name__ == "__main__":
    import os
    os.makedirs("/home/jules/verification", exist_ok=True)
    asyncio.run(main())
