"""
Convert the opencode session JSON into a readable transcript.

The lab deliverable asks for the chat history as a doc/pdf; the raw export is
JSON. This renders it to Markdown and to a printable HTML file (open the HTML
in a browser and use Print > Save as PDF).

Usage:  python make_chat_doc.py [chat-history.json]
"""

import html
import json
import os
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "chat-history.json"
OUT_DIR = os.path.dirname(os.path.abspath(SRC)) or "."

with open(SRC, encoding="utf-8-sig") as fh:
    data = json.load(fh)

info = data["info"]
messages = data["messages"]


def stamp(ms):
    t = (ms.get("time") or {}).get("created")
    if not t:
        return ""
    import datetime
    return datetime.datetime.fromtimestamp(t / 1000).strftime("%Y-%m-%d %H:%M:%S")


def summarise_tool(part):
    state = part.get("state") or {}
    name = part.get("tool", "tool")
    status = state.get("status", "?")
    title = (state.get("title") or state.get("output") or "").strip()
    title = " ".join(title.split())
    if len(title) > 300:
        title = title[:300] + "..."
    return f"{name} [{status}] {title}".strip()


def walk(md, fh, msg):
    role = (msg.get("info") or {}).get("role", "?")
    when = stamp(msg.get("info") or {})

    for part in msg.get("parts", []):
        kind = part.get("type")

        if kind == "text" and part.get("text", "").strip():
            text = part["text"].rstrip()
            if role == "user":
                md.append(f"\n### 👤 User · {when}\n\n{text}\n")
                fh.append(f'<div class="msg user"><div class="who">👤 User · {html.escape(when)}</div>'
                          f'<pre>{html.escape(text)}</pre></div>')
            else:
                md.append(f"\n### 🤖 Assistant\n\n{text}\n")
                fh.append(f'<div class="msg bot"><div class="who">🤖 Assistant</div>'
                          f'<pre>{html.escape(text)}</pre></div>')

        elif kind == "tool":
            line = summarise_tool(part)
            md.append(f"\n> 🔧 `{line}`\n")
            fh.append(f'<div class="tool">🔧 {html.escape(line)}</div>')

        elif kind == "reasoning":
            body = " ".join((part.get("text") or "").split())
            if body:
                md.append(f"\n> 💭 _reasoning: {body[:400]}_\n")


md = [
    f"# Chat history — {info.get('title', 'opencode session')}",
    "",
    f"- Session: `{info.get('id')}`",
    f"- Model: `{info.get('model', {}).get('modelID', 'n/a') if isinstance(info.get('model'), dict) else info.get('model', 'n/a')}`",
    f"- Directory: `{info.get('directory', '')}`",
    f"- Messages: {len(messages)}",
    "",
    "Lab 4 (VibeCoding) — Frogger. Tool calls are shown inline as `🔧` lines;",
    "internal reasoning is omitted.",
    "",
]

fh = [
    "<!doctype html><html><head><meta charset='utf-8'>",
    "<title>Chat history — Lab 4</title><style>",
    "body{font:14px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;max-width:900px;"
    "margin:32px auto;padding:0 20px;color:#1a1a1a;background:#fff}",
    "h1{font-size:22px;border-bottom:2px solid #333;padding-bottom:8px}",
    ".meta{color:#666;font-size:13px;margin-bottom:24px}",
    ".msg{border-radius:8px;padding:12px 14px;margin:14px 0;border:1px solid #ddd}",
    ".user{background:#eef4ff;border-color:#c3d5f5}",
    ".bot{background:#f7f7f7;border-color:#e0e0e0}",
    ".who{font-weight:700;font-size:12px;text-transform:uppercase;"
    "letter-spacing:.04em;margin-bottom:6px;color:#444}",
    "pre{white-space:pre-wrap;word-wrap:break-word;margin:0;font:13px/1.5 ui-monospace,"
    "Consolas,monospace}",
    ".tool{font:12px/1.4 Consolas,monospace;color:#5a5a5a;background:#fafafa;"
    "border-left:3px solid #ccc;padding:6px 10px;margin:6px 0;white-space:pre-wrap}",
    "@media print{body{margin:0;max-width:none}.msg{break-inside:avoid}}",
    "</style></head><body>",
    f"<h1>Chat history — {html.escape(info.get('title', 'opencode session'))}</h1>",
    f"<div class='meta'>Session <code>{html.escape(info.get('id', ''))}</code> &middot; "
    f"{len(messages)} messages &middot; Lab 4 (VibeCoding) — Frogger</div>",
]

for m in messages:
    walk(md, fh, m)

md_path = os.path.join(OUT_DIR, "chat-history.md")
html_path = os.path.join(OUT_DIR, "chat-history.html")

with open(md_path, "w", encoding="utf-8") as fh2:
    fh2.write("\n".join(md))
with open(html_path, "w", encoding="utf-8") as fh2:
    fh2.write("\n".join(fh) + "\n</body></html>")

print(f"wrote {md_path}  ({os.path.getsize(md_path)} bytes)")
print(f"wrote {html_path} ({os.path.getsize(html_path)} bytes)")
print("Open the HTML in a browser and use Print > Save as PDF for the PDF copy.")
