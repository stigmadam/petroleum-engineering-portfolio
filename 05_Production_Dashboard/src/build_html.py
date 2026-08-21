"""
build_html.py
--------------
Inlines dashboard_data.json directly into the HTML template as a JS
constant, producing a single self-contained dashboard.html - opens in any
browser via double-click, no server, no fetch()/CORS issues, no build step.
"""

import json
import os

BASE = os.path.dirname(__file__)
with open(os.path.join(BASE, "..", "data", "dashboard_data.json")) as f:
    data = json.load(f)

with open(os.path.join(BASE, "dashboard_template.html")) as f:
    template = f.read()

final_html = template.replace("/*__DASHBOARD_DATA__*/", json.dumps(data))

OUT = os.path.join(BASE, "..", "outputs", "dashboard.html")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    f.write(final_html)

print(f"Built self-contained dashboard -> {OUT}")
print(f"File size: {os.path.getsize(OUT) / 1024:.1f} KB")
