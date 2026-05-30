"""Fetch a page using nodriver (Chrome CDP, bypasses bot detection)."""
import argparse, asyncio, pathlib, sys, time, json
from dotenv import load_dotenv

load_dotenv(pathlib.Path(__file__).parent.parent / ".env")

import os
ACADEMY_EMAIL    = os.environ.get("LANGCHAIN_ACADEMY_EMAIL", "")
ACADEMY_PASSWORD = os.environ.get("LANGCHAIN_ACADEMY_PASSWORD", "")

NOTES_ROOT = pathlib.Path(__file__).parent.parent
CACHE_DIR  = NOTES_ROOT / "cache" / "web"
AUTH_FILE  = NOTES_ROOT / "cache" / "auth_state.json"
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def _chrome():
    p = pathlib.Path(CHROME_EXE)
    return str(p) if p.exists() else None


async def _save_auth_async(login_url="https://academy.langchain.com/users/sign_in", email=None, password=None):
    import nodriver as uc
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

    browser = await uc.start(headless=False, browser_executable_path=_chrome())
    page = await browser.get(login_url)
    await asyncio.sleep(3)  # let page settle / Cloudflare clear

    # Auto-fill credentials if provided
    if email and password:
        print("Filling credentials...")
        try:
            email_field = await page.find("input[type='email'], input[name='user[email]'], input[id='user_email']", timeout=10)
            await email_field.click()
            await email_field.send_keys(email)
            await asyncio.sleep(0.5)
            pass_field = await page.find("input[type='password']", timeout=5)
            await pass_field.click()
            await pass_field.send_keys(password)
            await asyncio.sleep(0.5)
            submit = await page.find("input[type='submit'], button[type='submit']", timeout=5)
            await submit.click()
            print("Credentials submitted, waiting for redirect...")
        except Exception as e:
            print(f"Auto-fill failed ({e}), please log in manually in the browser window.")

    print("Waiting for authenticated page...")

    # Poll until we land on an authenticated page (not sign_in / security-check)
    deadline = time.time() + 180
    while time.time() < deadline:
        await asyncio.sleep(2)
        try:
            url   = await page.evaluate("window.location.href")
            title = await page.evaluate("document.title")
            print(f"  url={url[:80]}  title={title[:50]}")
        except Exception as e:
            print(f"  poll error: {e}")
            continue
        if "sign_in" not in url and "just a moment" not in title.lower():
            print(f"Logged-in page detected: {url}")
            break
    else:
        print("WARNING: timed out waiting for login", file=sys.stderr)

    # Collect cookies via CDP
    try:
        raw = await page.send(uc.cdp.network.get_cookies())
        cookies = [c.to_json() for c in raw]
    except Exception as e:
        print(f"Cookie fetch failed: {e}", file=sys.stderr)
        cookies = []

    AUTH_FILE.write_text(json.dumps(cookies, indent=2), encoding="utf-8")
    print(f"Saved {len(cookies)} cookies -> {AUTH_FILE}")
    browser.stop()


async def _fetch_async(url, slug, timeout=60):
    import nodriver as uc
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{slug}.txt"

    browser = await uc.start(headless=False, browser_executable_path=_chrome())
    page = await browser.get("about:blank")

    # Restore cookies
    if AUTH_FILE.exists():
        cookies = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
        for c in cookies:
            try:
                await page.send(uc.cdp.network.set_cookie(
                    name=c["name"], value=c["value"],
                    domain=c.get("domain", ""),
                    path=c.get("path", "/"),
                    secure=c.get("secure", False),
                ))
            except Exception:
                pass

    page = await browser.get(url)

    # Wait past Cloudflare / login redirect
    deadline = time.time() + timeout
    while time.time() < deadline:
        await asyncio.sleep(2)
        try:
            title = await page.evaluate("document.title")
            cur_url = page.url
        except Exception:
            continue
        if "just a moment" in title.lower() or "security verification" in title.lower():
            print(f"  [cf] challenge running ({title})...")
            continue
        if "sign_in" in cur_url or "login" in cur_url:
            print("  [auth] redirected to login — cookies may be stale")
            break
        # Check for lesson content
        try:
            el = await page.find(".fr-view, .lecture-content, .text-block, article", timeout=2)
            if el:
                print("Lesson content found.")
                break
        except Exception:
            pass
        print(f"  waiting... ({title[:60]})")

    await asyncio.sleep(2)

    # Expand accordions
    try:
        for btn in await page.query_selector_all("button[aria-expanded='false']"):
            try: await btn.click(); await asyncio.sleep(0.3)
            except Exception: pass
    except Exception: pass

    text = await page.evaluate("document.body.innerText")
    browser.stop()

    cache_file.write_text(text, encoding="utf-8")
    print(f"Saved {len(text)} chars -> {cache_file}")
    return text


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?", default="")
    ap.add_argument("--slug")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--save-auth", action="store_true")
    ap.add_argument("--email")
    ap.add_argument("--password")
    args = ap.parse_args()

    if args.save_auth:
        asyncio.run(_save_auth_async(
            email=args.email or ACADEMY_EMAIL,
            password=args.password or ACADEMY_PASSWORD,
        ))
    else:
        if not args.url or not args.slug:
            ap.error("url and --slug are required")
        asyncio.run(_fetch_async(args.url, args.slug, args.timeout))
