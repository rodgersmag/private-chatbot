#!/usr/bin/env python3
"""Interactive terminal chat client for an Ollama server.

Features:
- Interactive REPL chat (streaming) using /api/chat when `requests` is available.
- Fallback single-shot mode when `requests` is not installed.
- Commands: /exit, /reset, /model <name>, /system <text>, /help

Usage:
  python main.py            # start interactive REPL
  python main.py "hello"   # single-shot prompt (prints full JSON/text)

Configure:
  OLLAMA_URL    - set host (default http://localhost:11434)
  OLLAMA_MODEL  - default model (default granite4:micro-h)
"""

import os
import sys
import json
import time

from dotenv import load_dotenv
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
CHAT_ENDPOINT = f"{OLLAMA_URL}/api/chat"
GENERATE_ENDPOINT = f"{OLLAMA_URL}/api/generate"
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "granite4:micro-h")

try:
    import requests
except Exception:
    requests = None


def stream_chat(messages, model=DEFAULT_MODEL, timeout=300):
    """Stream assistant response from /api/chat.

    Returns (assistant_text, stats) where stats contains tokens, duration, tokens_per_second
    """
    payload = {"model": model, "messages": messages, "stream": True}
    headers = {"Content-Type": "application/json"}

    if not requests:
        # fallback: do a blocking generate using /api/generate
        data = {"model": model, "prompt": _messages_to_prompt(messages)}
        return _blocking_generate(data)

    with requests.post(CHAT_ENDPOINT, json=payload, headers=headers, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        assistant = ""
        token_count = 0
        start_ts = None
        last_ts = None
        server_load_ns = None
        server_total_ns = None
        inside_thinking = False
        response_opened = False

        # The server emits newline-delimited JSON chunks. Read them incrementally.
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            line = line.strip()
            try:
                chunk = json.loads(line)
            except Exception:
                # If parsing fails, ignore chunk
                continue

            piece = None
            if isinstance(chunk, dict):
                msg = chunk.get("message")
                if isinstance(msg, dict):
                    piece = msg.get("content")
                if not piece:
                    piece = chunk.get("response") or chunk.get("token") or chunk.get("text")

            if piece:
                s = piece
                # parse markers and emit tagged output
                while s:
                    open_idx = s.find("<think>")
                    close_idx = s.find("</think>")

                    # no markers left
                    if open_idx == -1 and close_idx == -1:
                        text = s
                        s = ""
                        # emit text according to current state
                        if inside_thinking:
                            if not inside_thinking:
                                pass
                            # ensure thinking tag opened
                            if not response_opened and not inside_thinking:
                                pass
                            # print as thinking
                            if not inside_thinking:
                                print("<thinking>", end="", flush=True)
                                inside_thinking = True
                            now = time.time()
                            if start_ts is None:
                                start_ts = now
                            last_ts = now
                            tokens_here = len(text.split()) if text.strip() else 0
                            token_count += tokens_here
                            print(text, end="", flush=True)
                            assistant += text
                        else:
                            # not thinking => response
                            if inside_thinking:
                                # close thinking
                                print("</thinking>", end="", flush=True)
                                inside_thinking = False
                            if not response_opened:
                                print("<response>", end="", flush=True)
                                response_opened = True
                            now = time.time()
                            if start_ts is None:
                                start_ts = now
                            last_ts = now
                            tokens_here = len(text.split()) if text.strip() else 0
                            token_count += tokens_here
                            print(text, end="", flush=True)
                            assistant += text
                        continue

                    # handle open tag before close
                    if open_idx != -1 and (close_idx == -1 or open_idx < close_idx):
                        before = s[:open_idx]
                        if before:
                            # emit 'before' according to current state
                            if inside_thinking:
                                now = time.time()
                                if start_ts is None:
                                    start_ts = now
                                last_ts = now
                                tokens_here = len(before.split()) if before.strip() else 0
                                token_count += tokens_here
                                print(before, end="", flush=True)
                                assistant += before
                            else:
                                if not response_opened:
                                    print("<response>", end="", flush=True)
                                    response_opened = True
                                now = time.time()
                                if start_ts is None:
                                    start_ts = now
                                last_ts = now
                                tokens_here = len(before.split()) if before.strip() else 0
                                token_count += tokens_here
                                print(before, end="", flush=True)
                                assistant += before
                        # consume open tag and switch to thinking
                        s = s[open_idx + len("<think>"):]
                        if not inside_thinking:
                            print("<thinking>", end="", flush=True)
                            inside_thinking = True
                        continue

                    # handle close tag before open
                    if close_idx != -1 and (open_idx == -1 or close_idx < open_idx):
                        before = s[:close_idx]
                        if before:
                            # emit 'before' as thinking
                            now = time.time()
                            if start_ts is None:
                                start_ts = now
                            last_ts = now
                            tokens_here = len(before.split()) if before.strip() else 0
                            token_count += tokens_here
                            print(before, end="", flush=True)
                            assistant += before
                        # close thinking
                        if inside_thinking:
                            print("</thinking>", end="", flush=True)
                            inside_thinking = False
                        s = s[close_idx + len("</think>"):]
                        # ensure response tag opens on subsequent text
                        if not response_opened:
                            print("<response>", end="", flush=True)
                            response_opened = True
                        continue

            if isinstance(chunk, dict):
                if server_load_ns is None and chunk.get("load_duration"):
                    server_load_ns = chunk.get("load_duration")
                if server_total_ns is None and chunk.get("total_duration"):
                    server_total_ns = chunk.get("total_duration")

            if isinstance(chunk, dict) and chunk.get("done"):
                break

        # close any open tags
        if inside_thinking:
            print("</thinking>", end="", flush=True)
            inside_thinking = False
        if response_opened:
            print("</response>", end="", flush=True)
        print("")

        duration = (last_ts - start_ts) if (start_ts is not None and last_ts is not None) else 0.0
        tokens_per_second = token_count / duration if duration > 0 else float(token_count)

        stats = {
            "tokens": token_count,
            "duration": duration,
            "tokens_per_second": tokens_per_second,
            "load_duration_ns": server_load_ns,
            "total_duration_ns": server_total_ns,
        }

        return assistant, stats


def _messages_to_prompt(messages):
    # Convert messages list into a single prompt for non-chat endpoints
    out = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        out.append(f"[{role}] {content}")
    return "\n".join(out)


def _blocking_generate(data):
    # Fallback: call /api/generate without streaming
    t0 = time.time()
    if requests:
        r = requests.post(GENERATE_ENDPOINT, json=data, timeout=120)
        r.raise_for_status()
        t1 = time.time()
        try:
            j = r.json()
            text = j.get("response") or json.dumps(j, ensure_ascii=False)
        except Exception:
            text = r.text
    else:
        # No requests: try urllib for a minimal call
        import urllib.request as _urlreq
        import urllib.error as _urlerr
        headers = {"Content-Type": "application/json"}
        req = _urlreq.Request(GENERATE_ENDPOINT, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        try:
            with _urlreq.urlopen(req, timeout=120) as r:
                raw = r.read().decode("utf-8")
                t1 = time.time()
                try:
                    j = json.loads(raw)
                    text = j.get("response") or raw
                except Exception:
                    text = raw
        except _urlerr.URLError as e:
            raise RuntimeError(f"Request failed: {e}")

    duration = t1 - t0
    token_count = len(text.split()) if text and text.strip() else 0
    stats = {
        "tokens": token_count,
        "duration": duration,
        "tokens_per_second": token_count / duration if duration > 0 else float(token_count),
        "load_duration_ns": None,
        "total_duration_ns": None,
    }
    # wrap blocking responses in <response> tags so thinking/response separation is consistent
    wrapped_text = f"<response>{text}</response>"
    return wrapped_text, stats


def repl():
    print("Interactive Ollama chat — type /help for commands")
    messages = []
    model = DEFAULT_MODEL
    system_prompt = None

    while True:
        try:
            user = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return

        if not user.strip():
            continue

        if user.startswith("/"):
            parts = user.strip().split(" ", 1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            if cmd in ("/exit", "/quit"):
                print("Bye!")
                return
            if cmd == "/reset":
                messages = []
                system_prompt = None
                print("Conversation reset.")
                continue
            if cmd == "/model":
                if arg:
                    model = arg.strip()
                    print(f"Model set to: {model}")
                else:
                    print(f"Current model: {model}")
                continue
            if cmd == "/system":
                system_prompt = arg.strip()
                if system_prompt:
                    print("System message set.")
                else:
                    print("System message cleared.")
                continue
            if cmd == "/help":
                print("Commands:\n  /exit /quit - exit\n  /reset - clear conversation\n  /model <name> - set model\n  /system <text> - set system prompt\n  /help - show this")
                continue
            print("Unknown command. Type /help for list.")
            continue

        # Normal user input
        messages.append({"role": "user", "content": user})
        if system_prompt:
            payload_messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            payload_messages = messages

        print("Assistant:", end=" ", flush=True)
        try:
            assistant_text, stats = stream_chat(payload_messages, model=model)
        except Exception as e:
            print("\nError during chat:", e)
            continue

        # Append assistant message to conversation
        messages.append({"role": "assistant", "content": assistant_text})

        # Print stats summary
        try:
            tks = stats.get("tokens", 0)
            dur = stats.get("duration", 0.0)
            tps = stats.get("tokens_per_second", 0.0)
            print(f"[stats] tokens={tks} duration={dur:.2f}s tokens/s={tps:.2f}")
        except Exception:
            pass


def main():
    if len(sys.argv) > 1:
        # Single-shot prompt
        prompt = " ".join(sys.argv[1:])
        # Prepare a messages list consistent with the chat API
        messages = [{"role": "user", "content": prompt}]
        try:
            print(f"Sending prompt to {CHAT_ENDPOINT} (model={DEFAULT_MODEL})")
            out, stats = stream_chat(messages, model=DEFAULT_MODEL)
            print("\n== RESULT ==")
            print(out)
            try:
                print(f"[stats] tokens={stats.get('tokens',0)} duration={stats.get('duration',0.0):.2f}s tokens/s={stats.get('tokens_per_second',0.0):.2f}")
            except Exception:
                pass
        except Exception as e:
            print("Error:", e)
            sys.exit(2)
    else:
        repl()


if __name__ == "__main__":
    main()
