"""Extract Chrome cookies for LangChain Academy and save as Playwright auth state."""
import json, pathlib
import rookiepy

AUTH_FILE = pathlib.Path(r"C:\opt\learn\langchain\notes\cache\auth_state.json")
AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

cookies = rookiepy.chrome(domains=["academy.langchain.com", "langchain.com"])
print(f"Found {len(cookies)} cookies")

pl_cookies = []
for c in cookies:
    pl_cookies.append({
        "name": c["name"],
        "value": c["value"],
        "domain": c["host"],
        "path": c.get("path", "/"),
        "expires": c.get("expires", -1),
        "httpOnly": bool(c.get("httpOnly", False)),
        "secure": bool(c.get("secure", False)),
        "sameSite": "None",
    })

state = {"cookies": pl_cookies, "origins": []}
AUTH_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
print(f"Saved {len(pl_cookies)} cookies -> {AUTH_FILE}")
for c in pl_cookies[:8]:
    print(f"  {c['name']}: {c['value'][:40]}")
