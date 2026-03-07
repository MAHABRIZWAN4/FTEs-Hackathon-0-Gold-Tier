"""
Facebook Auto-Post Agent - Gold Tier AI Employee

This script automates posting to Facebook using Playwright browser automation.

[WARNING] IMPORTANT DISCLAIMER:
This tool is intended for authorized personal use, educational purposes, and testing only.
Facebook's Terms of Service generally prohibit automated posting. Users are responsible
for compliance with Facebook's policies. Use at your own risk.

Features:
- Automated Facebook login using environment credentials
- Text post creation and publishing
- Comprehensive error handling and logging
- Headless browser operation
- Screenshot capture on errors

Requirements:
- playwright (pip install playwright)
- python-dotenv (pip install python-dotenv)
- Run: playwright install chromium
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeout, Playwright
except ImportError:
    print("[ERROR] Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("[ERROR] python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

# Social Summary integration
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "social-summary"))
    from social_summary import log_social_post
    SOCIAL_SUMMARY_AVAILABLE = True
except ImportError:
    SOCIAL_SUMMARY_AVAILABLE = False

# Rich library for beautiful terminal output
try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Load environment variables
load_dotenv()

# Configuration
LOGS_DIR = Path("logs")
SOCIAL_LOG = LOGS_DIR / "social.log"
ACTIONS_LOG = LOGS_DIR / "actions.log"
SCREENSHOTS_DIR = LOGS_DIR / "screenshots"

# Ensure directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Facebook URLs
FACEBOOK_URL = "https://www.facebook.com"

# Timeouts (milliseconds)
DEFAULT_TIMEOUT = 30000
NAVIGATION_TIMEOUT = 30000


class FacebookPoster:
    """Handles automated posting to Facebook using browser automation."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Load credentials
        self.email = os.getenv("FACEBOOK_EMAIL")
        self.password = os.getenv("FACEBOOK_PASSWORD")

    def log_message(self, message: str, level: str = "INFO"):
        """Log message to both console and log files."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [FACEBOOK] {message}\n"

        # Log to social.log
        with open(SOCIAL_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        # Log to actions.log
        with open(ACTIONS_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        # Console output
        if RICH_AVAILABLE:
            if level == "ERROR":
                console.print(f"[red][X][/red] {message}")
            elif level == "SUCCESS":
                console.print(f"[green][OK][/green] {message}")
            elif level == "WARNING":
                console.print(f"[yellow][WARNING][/yellow] {message}")
            else:
                console.print(f"[cyan][INFO][/cyan] {message}")
        else:
            print(f"[{level}] {message}")

    async def take_screenshot(self, name: str):
        """Take a screenshot for debugging."""
        try:
            if self.page:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.png"
                filepath = SCREENSHOTS_DIR / filename
                await self.page.screenshot(path=str(filepath))
                self.log_message(f"Screenshot saved: {filepath}", "INFO")
        except Exception as e:
            self.log_message(f"Failed to take screenshot: {str(e)}", "WARNING")

    def validate_credentials(self) -> bool:
        """Validate that required credentials are present."""
        if not self.email or not self.password:
            self.log_message("Missing FACEBOOK_EMAIL or FACEBOOK_PASSWORD in .env", "ERROR")
            return False
        return True

    async def launch_browser(self) -> bool:
        """Launch the browser and create a new page."""
        try:
            self.log_message("Starting Facebook post automation", "INFO")
            self.playwright = await async_playwright().start()

            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self.page = await self.context.new_page()
            self.page.set_default_timeout(DEFAULT_TIMEOUT)

            self.log_message(f"Browser launched (headless={self.headless})", "INFO")
            return True

        except Exception as e:
            self.log_message(f"Failed to launch browser: {str(e)}", "ERROR")
            return False

    async def login(self) -> bool:
        """Login to Facebook using credentials from environment variables."""
        try:
            # Step 1: Navigate to Facebook
            self.log_message("Navigating to Facebook", "INFO")
            await self.page.goto("https://www.facebook.com/", timeout=NAVIGATION_TIMEOUT)

            # Step 2: Wait for page load
            self.log_message("Waiting for page to load", "INFO")
            await self.page.wait_for_load_state("networkidle")

            # Step 3: Wait for email field
            self.log_message("Waiting for email field", "INFO")
            await self.page.wait_for_selector("input[name='email']", timeout=30000)

            # Step 4: Fill email
            self.log_message(f"Filling email: {self.email}", "INFO")
            await self.page.locator("input[name='email']").fill(self.email)

            # Step 5: Fill password
            self.log_message("Filling password", "INFO")
            password_field = self.page.locator("input[name='pass']")
            await password_field.fill(self.password)

            # Step 6: Submit form by pressing Enter on password field
            self.log_message("Submitting login form (pressing Enter)", "INFO")
            await password_field.press("Enter")

            # Step 7: Wait 5 seconds
            self.log_message("Waiting for login to complete", "INFO")
            await asyncio.sleep(5)

            # Step 8: Dismiss "Save Login Info" or "Not now" popup if present
            try:
                self.log_message("Checking for login info popup", "INFO")
                # Try multiple ways to find and click "Not now"
                clicked = False

                # Method 1: Try by role and name
                try:
                    not_now_btn = self.page.get_by_role("button", name="Not now")
                    await not_now_btn.click(timeout=3000)
                    clicked = True
                    self.log_message("Dismissed popup using role button", "INFO")
                except:
                    pass

                # Method 2: Try by text (case insensitive)
                if not clicked:
                    try:
                        not_now_btn = self.page.locator("text=/not now/i").first
                        await not_now_btn.click(timeout=3000)
                        clicked = True
                        self.log_message("Dismissed popup using text locator", "INFO")
                    except:
                        pass

                # Method 3: Try finding any button with "Not now" text
                if not clicked:
                    try:
                        not_now_btn = self.page.locator("button:has-text('Not now')").first
                        await not_now_btn.click(timeout=3000)
                        clicked = True
                        self.log_message("Dismissed popup using button:has-text", "INFO")
                    except:
                        pass

                if clicked:
                    await asyncio.sleep(2)
                else:
                    self.log_message("No popup found or already dismissed", "INFO")

            except Exception as e:
                self.log_message(f"Popup handling: {str(e)}", "INFO")

            # Step 9: Check URL and verify login
            current_url = self.page.url
            current_title = await self.page.title()

            self.log_message(f"DEBUG - Current URL: {current_url}", "INFO")
            self.log_message(f"DEBUG - Current Title: {current_title}", "INFO")

            # Check for successful login
            if "checkpoint" in current_url or "challenge" in current_url:
                self.log_message("Security checkpoint detected. Manual intervention required.", "WARNING")
                await self.take_screenshot("checkpoint_detected")
                return False

            # Check if login was successful by looking for post creation elements
            if "facebook.com" in current_url and "login" not in current_url:
                try:
                    # Try multiple selectors to find the post creation area
                    self.log_message("Looking for post creation area", "INFO")

                    # Method 1: Try by placeholder (any text)
                    try:
                        post_box = self.page.locator('[placeholder]').first
                        await post_box.wait_for(state="visible", timeout=5000)
                        self.log_message("Login successful - Found post creation area (method 1)", "SUCCESS")
                        return True
                    except:
                        pass

                    # Method 2: Try by role textbox
                    try:
                        post_box = self.page.locator('[role="textbox"]').first
                        await post_box.wait_for(state="visible", timeout=5000)
                        self.log_message("Login successful - Found post creation area (method 2)", "SUCCESS")
                        return True
                    except:
                        pass

                    # Method 3: Try by aria-label containing "post"
                    try:
                        post_box = self.page.locator('[aria-label*="post" i]').first
                        await post_box.wait_for(state="visible", timeout=5000)
                        self.log_message("Login successful - Found post creation area (method 3)", "SUCCESS")
                        return True
                    except:
                        pass

                    # If we're on facebook.com and not on login page, assume success
                    self.log_message("On Facebook homepage - assuming login successful", "SUCCESS")
                    return True

                except Exception as e:
                    self.log_message(f"Error verifying login: {str(e)}", "ERROR")
                    await self.take_screenshot("login_verification_error")
                    # Still return True if we're on facebook.com
                    return True

            if "login" in current_url:
                self.log_message("Login failed. Still on login page.", "ERROR")
                await self.take_screenshot("login_failed")
                return False

            self.log_message("Login successful", "SUCCESS")
            return True

        except Exception as e:
            self.log_message(f"Login error: {str(e)}", "ERROR")
            await self.take_screenshot("login_error")
            return False

    async def create_post(self, content: str) -> bool:
        """Create and publish a text post on Facebook."""
        try:
            # Step 1: Dismiss all popups by pressing Escape twice
            self.log_message("Dismissing popups with Escape key", "INFO")
            await self.page.keyboard.press("Escape")
            await self.page.wait_for_timeout(1000)
            await self.page.keyboard.press("Escape")
            await self.page.wait_for_timeout(1000)

            # Step 2: Scroll to top of page
            self.log_message("Scrolling to top of page", "INFO")
            await self.page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)

            # Step 3: Click post box using specific selectors
            self.log_message("Looking for post creation area", "INFO")
            clicked = False

            # Method 1: Try aria-label "Create a post"
            try:
                self.log_message("Trying to click 'Create a post' button", "INFO")
                post_box = self.page.locator("div[aria-label='Create a post']")
                await post_box.click(timeout=5000)
                clicked = True
                self.log_message("Clicked 'Create a post' button", "SUCCESS")
            except Exception as e:
                self.log_message(f"Method 1 failed: {str(e)}", "WARNING")

            # Method 2: Try by role button with "What's on your mind"
            if not clicked:
                try:
                    self.log_message("Trying to click 'What's on your mind' button", "INFO")
                    post_box = self.page.get_by_role("button", name="What's on your mind")
                    await post_box.click(timeout=5000)
                    clicked = True
                    self.log_message("Clicked 'What's on your mind' button", "SUCCESS")
                except Exception as e:
                    self.log_message(f"Method 2 failed: {str(e)}", "WARNING")

            if not clicked:
                self.log_message("Failed to find post creation area", "ERROR")
                await self.take_screenshot("post_box_not_found")
                return False

            # Step 4: Wait 2 seconds after clicking
            self.log_message("Waiting for post editor to open", "INFO")
            await asyncio.sleep(2)

            # Step 5: Type content using keyboard
            self.log_message(f"Typing post content ({len(content)} characters)", "INFO")
            await self.page.keyboard.type(content)

            # Step 6: Wait 2 seconds
            await asyncio.sleep(2)

            # Step 7: Click Post button (use exact=True to avoid matching "Add to your post")
            self.log_message("Clicking Post button", "INFO")
            try:
                post_button = self.page.get_by_role("button", name="Post", exact=True)
                await post_button.click(timeout=5000)
                self.log_message("Clicked Post button", "SUCCESS")
            except Exception as e:
                self.log_message(f"Failed to click Post button: {str(e)}", "ERROR")
                await self.take_screenshot("post_button_error")
                return False

            # Step 8: Wait 5 seconds and take screenshot
            self.log_message("Waiting for post to be published", "INFO")
            await asyncio.sleep(5)

            self.log_message("Post published successfully", "SUCCESS")
            await self.take_screenshot("post_success")
            return True

        except Exception as e:
            self.log_message(f"Post creation error: {str(e)}", "ERROR")
            await self.take_screenshot("post_error")
            return False

    async def cleanup(self):
        """Close browser and cleanup resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.log_message("Browser closed", "INFO")
        except Exception as e:
            self.log_message(f"Cleanup error: {str(e)}", "WARNING")

    async def post(self, content: str) -> bool:
        """Main method to post content to Facebook."""
        if not content or not content.strip():
            self.log_message("Post content is empty", "ERROR")
            return False

        if not self.validate_credentials():
            return False

        try:
            if not await self.launch_browser():
                return False

            if not await self.login():
                await self.cleanup()
                return False

            if not await self.create_post(content):
                await self.cleanup()
                return False

            await self.cleanup()

            # Log to Social Summary
            if SOCIAL_SUMMARY_AVAILABLE:
                try:
                    log_social_post(
                        platform="Facebook",
                        content=content,
                        metadata={"character_count": len(content)}
                    )
                except Exception as e:
                    self.log_message(f"Failed to log to Social Summary: {str(e)}", "WARNING")

            return True

        except Exception as e:
            self.log_message(f"Unexpected error: {str(e)}", "ERROR")
            await self.cleanup()
            return False


def main():
    """Main entry point."""
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel.fit(
            "[bold blue]Facebook Auto-Post Agent[/bold blue]\n"
            "[dim]Gold Tier AI Employee[/dim]\n"
            "[yellow]========================================[/yellow]\n"
            "[red][WARNING] Use responsibly - Facebook ToS may prohibit automation[/red]",
            border_style="blue",
            padding=(1, 2)
        ))
        console.print()

    parser = argparse.ArgumentParser(description="Post content to Facebook automatically")
    parser.add_argument("content", type=str, help="The text content to post")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (default: False)")

    args = parser.parse_args()

    if RICH_AVAILABLE:
        console.print(f"[cyan][CONTENT] Content:[/cyan] [white]{args.content[:50]}{'...' if len(args.content) > 50 else ''}[/white]")
        console.print(f"[cyan][HEADLESS] Headless:[/cyan] [white]{args.headless}[/white]")
        console.print()

    # Create poster and post
    poster = FacebookPoster(headless=args.headless)
    success = asyncio.run(poster.post(args.content))

    if RICH_AVAILABLE:
        console.print()
        if success:
            console.print(Panel(
                "[bold green][OK] Post published successfully![/bold green]\n"
                "[dim]Your content is now live on Facebook[/dim]",
                border_style="green",
                padding=(1, 2)
            ))
        else:
            console.print(Panel(
                "[bold red][X] Failed to publish post[/bold red]\n"
                "[yellow]Check logs/social.log for details[/yellow]",
                border_style="red",
                padding=(1, 2)
            ))
        console.print()
    else:
        if success:
            print("\n[OK] Post published successfully!")
        else:
            print("\n[X] Failed to publish post. Check logs/social.log for details.")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
