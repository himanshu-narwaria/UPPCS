import os

dashboard_file = os.path.join("dashboard-src", "build_dashboard.py")
with open(dashboard_file, "r", encoding="utf-8") as f:
    code = f.read()

target = '{"key": "economy", "name": "Economy", "hindi": "अर्थव्यवस्था", "folder": "Economy 2024"},\n]'
replacement = '{"key": "economy", "name": "Economy", "hindi": "अर्थव्यवस्था", "folder": "Economy 2024"},\n    {"key": "geography", "name": "General Geography", "hindi": "सामान्य भूगोल", "folder": "General_Geography_Part_3"},\n]'

if target in code:
    code = code.replace(target, replacement)
elif target.replace('\n', '\r\n') in code:
    code = code.replace(target.replace('\n', '\r\n'), replacement.replace('\n', '\r\n'))
else:
    print("Target not found! Inspecting SUBJECTS block...")
    idx = code.find("SUBJECTS = [")
    print(code[idx:idx+300])

with open(dashboard_file, "w", encoding="utf-8") as f:
    f.write(code)

print("Successfully added Geography to SUBJECTS in build_dashboard.py")
