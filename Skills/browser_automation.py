from .registry import registry
from Core.logger import logger
import subprocess
import time
import os
import json

# ── Chrome paths (auto-detected for Windows) ──
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_EXE_X86 = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
CHROME_USER_DATA = os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\User Data")
CDP_URL = "http://localhost:9222"

_playwright = None
_browser = None
_context = None
_page = None
_selected_profile_dir = None  # e.g. "Default" or "Profile 1"


def _get_chrome_exe():
    if os.path.exists(CHROME_EXE):
        return CHROME_EXE
    if os.path.exists(CHROME_EXE_X86):
        return CHROME_EXE_X86
    return None


def _scan_chrome_profiles():
    """Scan Chrome User Data dir and return list of (folder_name, display_name, email)."""
    profiles = []
    if not os.path.exists(CHROME_USER_DATA):
        return profiles
    for folder in ["Default"] + [f"Profile {i}" for i in range(1, 20)]:
        profile_path = os.path.join(CHROME_USER_DATA, folder)
        prefs_path = os.path.join(profile_path, "Preferences")
        if not os.path.exists(prefs_path):
            continue
        try:
            with open(prefs_path, "r", encoding="utf-8", errors="ignore") as f:
                prefs = json.load(f)
            name = prefs.get("profile", {}).get("name", folder)
            accounts = prefs.get("account_info", [])
            email = accounts[0].get("email", "") if accounts else ""
            profiles.append((folder, name, email))
        except Exception:
            profiles.append((folder, folder, ""))
    return profiles


def _pick_chrome_profile():
    """Show profile list in terminal and let user choose once per session."""
    global _selected_profile_dir
    if _selected_profile_dir is not None:
        return _selected_profile_dir

    profiles = _scan_chrome_profiles()
    if not profiles:
        _selected_profile_dir = ""
        return None

    print("\n" + "="*52)
    print("🌐  Chrome Profile Picker — Konsa account use karna hai?")
    print("="*52)
    for i, (folder, name, email) in enumerate(profiles, 1):
        line = f"  [{i}] {name}"
        if email:
            line += f"  ({email})"
        print(line)
    print("  [0] Fresh Chrome (no profile / koi nahi)")
    print("="*52)

    while True:
        try:
            choice = input("Profile number enter karo: ").strip()
            idx = int(choice)
            if idx == 0:
                _selected_profile_dir = ""
                print("[Browser] Fresh Chrome use hoga.")
                return None
            if 1 <= idx <= len(profiles):
                _selected_profile_dir = profiles[idx - 1][0]
                name = profiles[idx - 1][1]
                email = profiles[idx - 1][2]
                print(f"[Browser] ✅ Profile: {name}" + (f" ({email})" if email else ""))
                return _selected_profile_dir
            print(f"  0 se {len(profiles)} ke beech number dalo.")
        except (ValueError, KeyboardInterrupt):
            _selected_profile_dir = ""
            print("[Browser] Fresh Chrome use hoga.")
            return None


def _get_page():
    global _playwright, _browser, _context, _page

    if _page:
        return _page

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise Exception("Playwright not installed. Run 'pip install playwright'.")

    if not _playwright:
        _playwright = sync_playwright().start()

    # ── Strategy 1: Connect to existing Chrome via CDP ──
    try:
        logger.info("[Browser] Trying CDP connection to existing Chrome...")
        _browser = _playwright.chromium.connect_over_cdp(CDP_URL)
        contexts = _browser.contexts
        _page = contexts[0].pages[0] if (contexts and contexts[0].pages) else _browser.new_page()
        logger.info("[Browser] ✅ Connected to existing Chrome!")
        return _page
    except Exception:
        logger.info("[Browser] No existing Chrome on port 9222.")

    # ── Strategy 2: Launch Chrome with selected profile ──
    chrome_exe = _get_chrome_exe()
    profile_dir = _pick_chrome_profile()

    if chrome_exe:
        try:
            if profile_dir:
                profile_path = os.path.join(CHROME_USER_DATA, profile_dir)
                logger.info(f"[Browser] Launching Chrome with profile '{profile_dir}'...")
                _context = _playwright.chromium.launch_persistent_context(
                    user_data_dir=profile_path,
                    executable_path=chrome_exe,
                    headless=False,
                    args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
                    no_viewport=True
                )
                _page = _context.pages[0] if _context.pages else _context.new_page()
            else:
                logger.info("[Browser] Launching system Chrome (no profile)...")
                _browser = _playwright.chromium.launch(
                    headless=False, channel="chrome", args=["--start-maximized"]
                )
                _page = _browser.new_page()
            logger.info("[Browser] ✅ Chrome launched!")
            return _page
        except Exception as e:
            logger.warning(f"[Browser] Chrome launch failed: {e}")

    # ── Strategy 3: Playwright Chromium fallback ──
    logger.info("[Browser] Fallback: Playwright Chromium...")
    try:
        _browser = _playwright.chromium.launch(headless=False)
    except Exception as e:
        if "Executable doesn't exist" in str(e) or "playwright install" in str(e):
            subprocess.run(["python", "-m", "playwright", "install", "chromium"], check=True)
            _browser = _playwright.chromium.launch(headless=False)
        else:
            raise e
    _page = _browser.new_page()
    return _page


def _snapshot() -> str:
    """Return compact UI snapshot of visible interactive elements (token-safe)."""
    page = _get_page()
    time.sleep(1)
    script = """
    () => {
        let data = [];
        document.querySelectorAll('button, a, input, select, textarea, [role="button"], [role="link"], [role="textbox"]').forEach((el, idx) => {
            let rect = el.getBoundingClientRect();
            let style = window.getComputedStyle(el);
            if (rect.width > 2 && rect.height > 2 && style.visibility !== 'hidden' && style.display !== 'none') {
                let text = el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || el.name || '';
                text = text.trim().replace(/\n/g, ' ').slice(0, 80);
                if (text.length > 0) {
                    data.push(`[${idx}][${el.tagName.toLowerCase()}] "${text}"`);
                }
            }
        });
        let unique = [...new Set(data)].slice(0, 80);
        return unique.join('\n');
    }
    """
    result = page.evaluate(script)
    title = page.title()
    url = page.url
    if not result:
        return f"Page: {title}\nURL: {url}\n(No interactive elements found — page may still be loading)"
    output = f"Page: {title}\nURL: {url}\n\n[SNAPSHOT — ref IDs for act]\n{result}"
    return output[:3000] + "\n...[truncated]" if len(output) > 3000 else output


# ─────────────────────────────────────────────
# UNIFIED BROWSER TOOL
# ─────────────────────────────────────────────
@registry.register(
    name="browser",
    description=(
        "Unified browser control tool. Use 'action' to pick what to do:\n"
        "  navigate  — go to a URL (requires: url)\n"
        "  snapshot  — read current page UI tree (visible elements with ref IDs)\n"
        "  act       — click/type/press using text or ref ID (requires: action_type, value)\n"
        "  screenshot — describe what is currently visible on screen\n"
        "  status    — check if browser is open and show current URL\n"
        "  close     — close the browser\n\n"
        "action_type for 'act': click | type | press | scroll\n"
        "For 'type': also provide input_text.\n"
        "ALWAYS call snapshot before act to see available elements."
    ),
    parameters={
        "action": {
            "type": "string",
            "description": "What to do: navigate | snapshot | act | screenshot | status | close"
        },
        "url": {
            "type": "string",
            "description": "URL to navigate to (required for navigate action)"
        },
        "action_type": {
            "type": "string",
            "description": "For 'act': click | type | press | scroll"
        },
        "value": {
            "type": "string",
            "description": "For act/click: element text or ref ID. For type: field name/placeholder. For press: key name (e.g. Enter)"
        },
        "input_text": {
            "type": "string",
            "description": "Text to type into a field (used with action_type=type)"
        }
    },
    required=["action"]
)
def browser(
    action: str,
    url: str = None,
    action_type: str = None,
    value: str = None,
    input_text: str = None
) -> str:
    action = action.lower().strip()

    # ── STATUS ──
    if action == "status":
        global _page
        if not _page:
            return "Browser is not open. Use action='navigate' with a URL to start."
        try:
            return f"Browser is open. Current URL: {_page.url} | Title: {_page.title()}"
        except Exception:
            _page = None
            return "Browser was open but appears to have closed."

    # ── CLOSE ──
    if action == "close":
        global _browser, _context, _playwright
        try:
            if _context:
                _context.close()
            if _browser:
                _browser.close()
            if _playwright:
                _playwright.stop()
        except Exception:
            pass
        _page = _browser = _context = _playwright = None
        return "Browser closed successfully."

    # ── NAVIGATE ──
    if action == "navigate":
        if not url:
            return "Error: 'url' is required for navigate action."
        try:
            page = _get_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            return f"Navigated to {url}. Call action='snapshot' to see what's on the page."
        except Exception as e:
            return f"Navigation Error: {e}"

    # ── SNAPSHOT ──
    if action == "snapshot":
        try:
            return _snapshot()
        except Exception as e:
            return f"Snapshot Error: {e}"

    # ── SCREENSHOT ──
    if action == "screenshot":
        try:
            page = _get_page()
            # Return page title + URL as a text description (no actual image bytes)
            title = page.title()
            url_now = page.url
            return f"Current page: '{title}'\nURL: {url_now}\n\nUse action='snapshot' for interactive elements."
        except Exception as e:
            return f"Screenshot Error: {e}"

    # ── ACT ──
    if action == "act":
        if not action_type:
            return "Error: 'action_type' is required for act (click | type | press | scroll)."
        if not value:
            return "Error: 'value' is required for act (element text, ref ID, or key name)."

        try:
            page = _get_page()
            atype = action_type.lower().strip()

            # ── CLICK ──
            if atype == "click":
                locator = page.get_by_text(value, exact=False)
                if locator.count() == 0:
                    locator = page.locator(f"text={value}")
                if locator.count() == 0:
                    # Try ARIA label
                    locator = page.locator(f"[aria-label*='{value}' i]")
                if locator.count() == 0:
                    return f"Element '{value}' not found on page. Call snapshot to see available elements."
                target = locator.first
                target.scroll_into_view_if_needed()
                target.click(timeout=5000)
                time.sleep(2)
                return f"Clicked '{value}'. Call snapshot to see updated page."

            # ── TYPE ──
            elif atype == "type":
                if not input_text:
                    return "Error: 'input_text' is required when action_type is 'type'."
                el = page.get_by_placeholder(value, exact=False)
                if el.count() == 0:
                    el = page.get_by_role("textbox", name=value)
                if el.count() == 0:
                    el = page.locator(f"input[name*='{value}' i], input[aria-label*='{value}' i], textarea[placeholder*='{value}' i]")
                if el.count() == 0:
                    return f"Input field '{value}' not found. Call snapshot to see available fields."
                target = el.first
                target.scroll_into_view_if_needed()
                target.click()
                target.fill("")
                target.type(input_text, delay=30)
                return f"Typed '{input_text}' into '{value}'."

            # ── PRESS ──
            elif atype == "press":
                page.keyboard.press(value)
                time.sleep(1.5)
                return f"Pressed key '{value}'."

            # ── SCROLL ──
            elif atype == "scroll":
                direction = value.lower()
                if "up" in direction:
                    page.mouse.wheel(0, -600)
                elif "down" in direction:
                    page.mouse.wheel(0, 600)
                else:
                    page.mouse.wheel(0, 400)
                time.sleep(1)
                return f"Scrolled {value}."

            else:
                return f"Unknown action_type '{action_type}'. Use: click | type | press | scroll"

        except Exception as e:
            return f"Act Error ({action_type}): {e}"

    return f"Unknown action '{action}'. Use: navigate | snapshot | act | screenshot | status | close"
