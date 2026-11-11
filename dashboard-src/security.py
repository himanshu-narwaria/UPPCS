"""Write vercel.json with the site's security headers.

The Content-Security-Policy allows only the inline scripts that are actually in the pages,
each identified by its SHA-256 hash, and blocks every other script, frame, form target and
outside resource. Because the hashes change whenever a page's script changes, this file is
regenerated on every build (build_dashboard.py calls write_vercel_json()); never edit
vercel.json by hand.

Run on its own:  python security.py
"""
import base64
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "vercel.json")
SKIP_DIRS = {".git", "dashboard-src", "node_modules", ".vercel"}
SCRIPT_RE = re.compile(r"<script(\s[^>]*)?>(.*?)</script>", re.S | re.I)
DATA_TYPES = re.compile(r'type\s*=\s*"application/(?:json|ld\+json)"', re.I)


def pages():
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for f in sorted(files):
            if f.endswith(".html"):
                yield os.path.join(dirpath, f)


def script_hashes():
    hashes, problems = set(), []
    for p in pages():
        with open(p, encoding="utf-8", newline="") as f:
            s = f.read().replace("\r\n", "\n")  # git stores LF; the deployed bytes are LF
        rel = os.path.relpath(p, ROOT)
        for attrs, body in SCRIPT_RE.findall(s):
            attrs = attrs or ""
            if DATA_TYPES.search(attrs):
                continue  # JSON data blocks are never executed
            if re.search(r"\ssrc\s*=", attrs, re.I):
                problems.append(f"{rel}: external script {attrs.strip()}")
                continue
            digest = base64.b64encode(hashlib.sha256(body.encode("utf-8")).digest()).decode()
            hashes.add(f"'sha256-{digest}'")
        if re.search(r"\son[a-z]+\s*=\s*[\"']", re.sub(r"<script.*?</script>", "", s, flags=re.S | re.I)):
            problems.append(f"{rel}: inline event handler (onclick= etc.) would be blocked by the CSP")
        if re.search(r'href\s*=\s*"javascript:', s, re.I):
            problems.append(f"{rel}: javascript: link would be blocked by the CSP")
    return sorted(hashes), problems


def build_config():
    hashes, problems = script_hashes()
    if problems:
        raise SystemExit("security: fix these before deploying:\n  " + "\n  ".join(problems))
    csp = "; ".join([
        "default-src 'none'",
        "script-src " + " ".join(hashes),
        "style-src 'self' 'unsafe-inline'",  # pages use <style> blocks and style="" attributes
        "font-src 'self' data:",             # fonts are embedded as data: URIs
        "img-src 'self' data:",
        "connect-src 'self'",
        "manifest-src 'self'",
        "base-uri 'none'",
        "form-action 'none'",
        "frame-ancestors 'none'",
        "object-src 'none'",
        "upgrade-insecure-requests",
    ])
    headers = [
        {"key": "Content-Security-Policy", "value": csp},
        {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload"},
        {"key": "X-Frame-Options", "value": "DENY"},
        {"key": "X-Content-Type-Options", "value": "nosniff"},
        {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
        {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=()"},
        {"key": "Cross-Origin-Opener-Policy", "value": "same-origin"},
        {"key": "Cross-Origin-Resource-Policy", "value": "same-origin"},
        {"key": "X-Robots-Tag", "value": "noindex, nofollow"},  # private study notes: keep out of search engines
    ]
    return {
        "rewrites": [{"source": "/", "destination": "/study-dashboard.html"}],
        "headers": [{"source": "/(.*)", "headers": headers}],
    }, len(hashes)


def write_vercel_json():
    cfg, n = build_config()
    text = json.dumps(cfg, indent=2) + "\n"
    old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
    if text != old:
        with open(OUT, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print(f"security: vercel.json {'updated' if text != old else 'unchanged'} ({n} allowed inline scripts)")


if __name__ == "__main__":
    write_vercel_json()
