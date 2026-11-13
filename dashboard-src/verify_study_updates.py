"""Check the rebuilt subjects (Current Affairs, Polity, History, Economy, Geography, Science), their dashboard, links and scripts.

Run after build_dashboard.py. This is static verification, not browser UI testing.
"""
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import subprocess

from bs4 import BeautifulSoup

import build_dashboard as dashboard
import security

ROOT = Path(__file__).resolve().parent.parent
SUBJECTS = [s for s in dashboard.SUBJECTS if s["key"] in {"current", "polity", "history", "economy", "geography", "science"}]


def main():
    files = [ROOT / "study-dashboard.html"]
    for subject in SUBJECTS:
        files.extend(sorted((ROOT / subject["folder"]).glob("*.html")))
    errors, parsed, scripts = [], {}, []
    for path in files:
        text = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(text, "html.parser")
        ids = [tag["id"] for tag in soup.find_all(id=True)]
        duplicate_ids = [key for key, count in Counter(ids).items() if count > 1]
        if duplicate_ids:
            errors.append(f"{path.name}: duplicate IDs {duplicate_ids}")
        parsed[path] = set(ids)
        for script in soup.find_all("script"):
            if script.get("type") in {"application/json", "application/ld+json"}:
                try:
                    json.loads(script.string or "")
                except ValueError as exc:
                    errors.append(f"{path.name}: invalid JSON: {exc}")
            elif not script.get("src"):
                scripts.append({"name": str(path.relative_to(ROOT)), "body": script.string or ""})
        for anchor in soup.find_all("a", href=True):
            href = urlsplit(anchor["href"])
            if href.scheme in {"http", "https"}:
                if anchor.get("target") != "_blank" or not {"noopener", "noreferrer"}.issubset(anchor.get("rel", [])):
                    errors.append(f"{path.name}: unsafe external source link {anchor['href']}")
                continue
            if href.scheme or not href.path and not href.fragment:
                continue
            target = (path.parent / unquote(href.path)).resolve() if href.path else path
            if not target.is_file():
                errors.append(f"{path.name}: missing local target {anchor['href']}")
                continue
            if href.fragment and target.suffix == ".html":
                if target not in parsed:
                    parsed[target] = {tag["id"] for tag in BeautifulSoup(target.read_text(encoding="utf-8"), "html.parser").find_all(id=True)}
                if unquote(href.fragment) not in parsed[target]:
                    errors.append(f"{path.name}: missing anchor {anchor['href']}")
        bank = soup.find("script", id="pqd")
        if bank:
            data = json.loads(bank.string)
            questions = data.values() if isinstance(data, dict) else data
            for q in questions:
                if "full-notes" in path.name and q.get("h") not in parsed[path]:
                    errors.append(f"{path.name}: missing question topic {q.get('h')}")
                if not q.get("s") or not q.get("f"):
                    errors.append(f"{path.name}: question lacks stem or explanation")
                if len(q.get("o", [])) < 2 or not q.get("k") or len(set(q["k"])) != len(q["k"]):
                    errors.append(f"{path.name}: scored question lacks usable options or an unambiguous key")
                if any(not isinstance(key, int) or key < 0 or key >= len(q.get("o", [])) for key in q.get("k", [])):
                    errors.append(f"{path.name}: out-of-range answer key")
        print(f"Checked {path.relative_to(ROOT)}: {len(ids)} unique element IDs")

    node = "const vm=require('node:vm');let s='';process.stdin.setEncoding('utf8');process.stdin.on('data',d=>s+=d);process.stdin.on('end',()=>{for(const x of JSON.parse(s)){new vm.Script(x.body,{filename:x.name});}console.log('Parsed '+JSON.parse(s).length+' executable scripts');});"
    result = subprocess.run(["node", "-e", node], input=json.dumps(scripts), text=True, encoding="utf-8", capture_output=True)
    if result.returncode:
        errors.append(result.stderr)
    else:
        print(result.stdout.strip())
    _, security_errors = security.script_hashes()
    errors.extend(security_errors)
    expected_config, _ = security.build_config()
    if json.loads((ROOT / "vercel.json").read_text(encoding="utf-8")) != expected_config:
        errors.append("vercel.json has stale script hashes; rebuild the dashboard")

    for subject in SUBJECTS:
        folder = subject["folder"]
        full = dashboard.parse_full(dashboard.find_one(folder, ["*-full-notes.html"]))
        quick = dashboard.parse_quick(dashboard.find_one(folder, ["*quick-notes.html"]))
        if [(n, c["title"], c["asked"]) for n, c in full["chapters"].items()] != [(n, c["title"], c["asked"]) for n, c in quick["chapters"].items()]:
            errors.append(f"{folder}: chapter titles or practice totals differ between full and quick notes")
        plan = dashboard.parse_72h(dashboard.find_one(folder, ["*-in-72h.html"]))
        if [n for n, _ in plan["hours"]] != list(range(1, 73)):
            errors.append(f"{folder}: plan does not contain hours 1–72 exactly once")
        print(f"{subject['name']}: {len(full['chapters'])} chapters, {full['bank']} practice entries, 72 hours")
    if errors:
        raise SystemExit("\n".join(dict.fromkeys(errors)))
    print("PASS: links, anchors, data, script syntax, dashboard counts and security hashes. Browser interactions not tested.")


if __name__ == "__main__":
    main()
