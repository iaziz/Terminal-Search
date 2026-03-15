#!/usr/bin/env python3
"""
terminal-search  —  Grok-powered terminal search with streaming, colors & enhanced prompt styling
Local-only – no pip beyond requests

     March 2026     version 1.3-enhanced-colors

Usage:
    python -m terminal_search "latest ai news march 2026"
"""

import os
import sys
import argparse
import json
import re
from datetime import datetime
import requests
import time

# ──────────────────────────────────────────────
#  ANSI COLORS
# ──────────────────────────────────────────────

class Colors:
    HEADER    = '\033[95m'      # magenta
    CYAN      = '\033[96m'      # bright cyan – prompt
    BLUE      = '\033[94m'      # blue – headings
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'      # links / warnings
    RED       = '\033[91m'
    GRAY      = '\033[90m'      # subtle
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    END       = '\033[0m'


# ──────────────────────────────────────────────
#  CONFIG
# ──────────────────────────────────────────────

API_KEY = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")

if not API_KEY:
    print(f"{Colors.RED}{Colors.BOLD}❌ Missing API key{Colors.END}", file=sys.stderr)
    print(f"    export XAI_API_KEY=xai-...", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://api.x.ai/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

MODELS = {
    "default":  "grok-4-0709",
    "think":    "grok-4.20-beta-0309-reasoning",
    "concise":  "grok-4.20-beta-0309-non-reasoning",
    "code":     "grok-4-0709",
}

SYSTEM_PROMPTS = {
    "default": (
        "You are a sharp, factual search/research assistant. "
        "Answer clearly and directly. Use markdown for structure when helpful. "
        f"Current date: {datetime.now():%Y-%m-%d}."
    ),
    "think": (
        "Deep reasoning mode activated. "
        "Think step-by-step. Consider multiple angles. "
        "Use headings, bullets, numbered lists for clarity. "
        "End with the strongest / most likely conclusion."
    ),
    "concise": "Answer briefly and directly. Maximum 3 sentences.",
    "code": (
        "Expert programmer mode. "
        "Return clean, modern, well-formatted code. "
        "Include brief comments only when non-obvious. "
        "Prefer latest language idioms and best practices."
    )
}

TYPE_DELAY = 0.012   # slightly faster for better flow
CHUNK_DELAY = 0.0

# ──────────────────────────────────────────────
#  SIMPLE MARKDOWN COLORING IN STREAM
# ──────────────────────────────────────────────

def colorize_chunk(text: str) -> str:
    """Very basic live coloring for common markdown patterns"""
    # Headings # Heading → bold blue
    text = re.sub(r'^# (.*)$', rf'{Colors.BOLD}{Colors.BLUE}\1{Colors.END}', text, flags=re.M)
    text = re.sub(r'^## (.*)$', rf'{Colors.BOLD}{Colors.BLUE}\1{Colors.END}', text, flags=re.M)

    # Links [text](url) → yellow underlined text
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', rf'{Colors.YELLOW}{Colors.UNDERLINE}\1{Colors.END}', text)

    # Bold **text** → bold
    text = re.sub(r'\*\*([^*]+)\*\*', rf'{Colors.BOLD}\1{Colors.END}', text)

    return text


# ──────────────────────────────────────────────
#  STREAM + TYPE + COLOR ENHANCED PROMPT
# ──────────────────────────────────────────────

def stream_and_type(query: str, mode: str = "default", max_tokens: int = 2200, temperature: float = 0.7):
    model_name = MODELS.get(mode, MODELS["default"])
    system_msg = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])

    payload = {
        "model": model_name,
        "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": query}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    # Enhanced colored header & prompt
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Colors.GRAY}{Colors.UNDERLINE}╭── terminal-search • {model_name} • {ts} ────────{Colors.END}",
          file=sys.stderr)
    print(f"{Colors.BOLD}{Colors.CYAN}   ►►►  {query}  ◄◄◄{Colors.END}", file=sys.stderr)
    print(f"{Colors.GRAY}────────────────────────────────────────────────────────────{Colors.END}\n", file=sys.stderr)

    try:
        with requests.post(
            f"{BASE_URL}/chat/completions",
            headers=HEADERS,
            json=payload,
            timeout=120,
            stream=True
        ) as r:
            r.raise_for_status()

            for line in r.iter_lines():
                if not line:
                    continue
                line = line.decode('utf-8').strip()
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            colored = colorize_chunk(content)

                            for char in colored:
                                sys.stdout.write(char)
                                sys.stdout.flush()
                                time.sleep(TYPE_DELAY)

                            if content.endswith(("\n", ".", "!", "?", ":", "—", " ")):
                                time.sleep(CHUNK_DELAY)

                    except json.JSONDecodeError:
                        pass

            print("\n")  # clean end
            return True

    except requests.RequestException as e:
        print(f"\n{Colors.RED}{Colors.BOLD}┌─ API / Stream error ────────┐{Colors.END}", file=sys.stderr)
        print(f"{Colors.RED}│ {e}{Colors.END}", file=sys.stderr)
        if hasattr(e, "response") and e.response is not None:
            print(f"{Colors.RED}│ → {e.response.text[:240]}...{Colors.END}", file=sys.stderr)
        print(f"{Colors.RED}└─────────────────────────────┘{Colors.END}\n", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(prog="terminal-search", add_help=False)
    parser.add_argument("query", nargs="*", help="question")
    parser.add_argument("-m", "--mode", default="default")
    parser.add_argument("-n", "--maxtokens", type=int, default=2200)
    parser.add_argument("-t", "--temp", type=float, default=0.7)
    parser.add_argument("--list-models", action="store_true")

    args = parser.parse_args()

    if args.list_models:
        # your list function here...
        return

    query = " ".join(args.query).strip()
    if not query:
        print("Usage: terminal-search <query> [-m mode] [-n tokens]")
        return

    stream_and_type(query, args.mode, args.maxtokens, args.temp)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted.{Colors.END}")
        sys.exit(130)
