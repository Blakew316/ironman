"""Web-friendly command dispatcher.

Maps free-text (typed or spoken) to a J.A.R.V.I.S skill and returns a
spoken-style reply. Matching is keyword-based so natural phrasing from speech
recognition works ("what's the time", "check my battery please", ...), not just
exact phrases. If ``OPENAI_API_KEY`` is set, anything not handled locally is
answered conversationally by the model, so J.A.R.V.I.S can respond to almost
anything. Destructive actions (shutdown/restart) are gated behind
``JARVIS_WEB_ALLOW_POWER=1``.
"""

import json
import os
import random
import re
import unicodedata
import urllib.error
import urllib.request

from jarvis.nlp import action_phrases as ap
from jarvis.skills import (
    greet_startup,  # noqa: F401 (kept for parity / future use)
    datetime_info,
    get_weather,
    tell_joke,
    check_hardware,
    wikipedia_search,
    wolfram,
)
from jarvis import config

_wolfram_ready = False


def _ensure_wolfram():
    global _wolfram_ready
    if not _wolfram_ready:
        wolfram.setupWolfram()
        _wolfram_ready = True


def _r(items):
    return items[random.randint(0, len(items) - 1)]


def _norm(t):
    """Lowercase, drop punctuation, collapse whitespace."""
    t = (t or "").lower().strip()
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


_SYSTEM = (
    "You are J.A.R.V.I.S, a calm, warm, dry-witted British AI assistant in the "
    "spirit of Tony Stark's assistant. You are genuinely personable: greet "
    "warmly, match the user's mood, offer a touch of dry humour when it fits, "
    "and never sound clipped, robotic, or like a report. "
    "Your replies are SPOKEN ALOUD by a "
    "text-to-speech voice, so write exactly the way a person talks: flowing "
    "natural sentences with contractions, an even relaxed pace, and nothing that "
    "cannot be read aloud — never use bullet points, numbered lists, headings, "
    "markdown, symbols, URLs, or code. Round numbers the way people say them. "
    "Keep replies to one to three short sentences unless the user asks for "
    "detail, address the user as 'sir', and answer the question directly before "
    "adding anything extra. When a question needs current or real-time "
    "information (news, prices, weather, live facts), use web search to look it "
    "up before answering, and weave the result into one conversational answer."
)


def chat_provider():
    """Which reasoning 'brain' is configured: 'anthropic', 'openai', or None."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return None


def _env_ascii(name):
    """Read an env var as a clean ASCII credential.

    Keys pasted through chat apps / rich-text fields arrive as unicode
    lookalike characters that HTTP headers reject ('latin-1' codec errors).
    NFKC-normalize back to plain characters and drop anything non-ASCII.
    """
    v = os.environ.get(name, "")
    v = unicodedata.normalize("NFKC", v).strip()
    return "".join(ch for ch in v if 0x21 <= ord(ch) <= 0x7E)


def _ssl_context():
    """Use certifi's CA bundle when available — macOS Pythons often can't
    verify TLS with the system default, which kills every API call."""
    try:
        import ssl
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return None


def _post_json(url, headers, payload, timeout=25):
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        # surface the API's own explanation (invalid key, no credits, ...)
        try:
            detail = json.loads(exc.read().decode("utf-8", "replace"))
            msg = detail.get("error", {}).get("message", "") or str(detail)
        except Exception:
            msg = exc.reason or ""
        raise RuntimeError("HTTP %s: %s" % (exc.code, str(msg)[:200])) from exc


# Last reason the reasoning brain failed, so the HUD can say WHY instead of
# silently playing dumb.
_last_brain_error = None


def _chat(prompt):
    """Conversational 'brain'. Claude (ANTHROPIC_API_KEY) if set, else OpenAI.

    Returns a reply string, or None when no key is configured / the call fails.
    The spoken voice is handled separately, so the brain and voice are
    independent — you can pair any brain with your cloned voice.
    """
    global _last_brain_error
    provider = chat_provider()
    if provider is None:
        return None
    try:
        if provider == "anthropic":
            model = os.environ.get("JARVIS_CHAT_MODEL", "claude-haiku-4-5-20251001")
            headers = {"x-api-key": _env_ascii("ANTHROPIC_API_KEY"),
                       "anthropic-version": "2023-06-01", "content-type": "application/json"}
            base = {"model": model, "max_tokens": 400, "system": _SYSTEM,
                    "messages": [{"role": "user", "content": prompt}]}
            # Try with live web search first; if the tool isn't available on the
            # account/model, retry the same request without it.
            attempts = []
            if os.environ.get("JARVIS_WEB_SEARCH", "1") != "0":
                with_tool = dict(base)
                # max_uses kept low so a chained search can't stall the reply
                with_tool["tools"] = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 2}]
                attempts.append(with_tool)
            attempts.append(base)
            for payload in attempts:
                try:
                    data = _post_json("https://api.anthropic.com/v1/messages", headers, payload)
                except Exception as exc:
                    print("[dispatch] claude call failed: %s" % exc)
                    _last_brain_error = str(exc)
                    continue
                parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
                txt = ("".join(parts)).strip()
                if txt:
                    _last_brain_error = None
                    return txt
            return None

        model = os.environ.get("JARVIS_CHAT_MODEL", "gpt-4o-mini")
        data = _post_json(
            "https://api.openai.com/v1/chat/completions",
            {"Authorization": "Bearer %s" % _env_ascii("OPENAI_API_KEY"),
             "Content-Type": "application/json"},
            {"model": model, "temperature": 0.6, "max_tokens": 220,
             "messages": [{"role": "system", "content": _SYSTEM},
                          {"role": "user", "content": prompt}]},
        )
        reply = data["choices"][0]["message"]["content"].strip()
        _last_brain_error = None
        return reply
    except Exception as exc:
        print("[dispatch] chat brain (%s) failed: %s" % (provider, exc))
        _last_brain_error = str(exc)
        return None


def handle(text):
    """Return ``{"reply": str, "intent": str}`` for a free-text command."""
    raw = (text or "").strip()
    cmd = _norm(raw)
    if not cmd:
        return {"reply": "I'm listening, sir.", "intent": "idle"}

    # strip the wake word wherever it appears
    stripped = re.sub(r"\bjarvis\b", " ", cmd).strip()
    if stripped:
        cmd = re.sub(r"\s+", " ", stripped)
    else:
        return {"reply": _r(ap.check_r), "intent": "status"}

    def has(*kws):
        return any(k in cmd for k in kws)

    # --- status / identity ---
    if has("are you there", "you awake", "you up", "you alive", "you dead", "wake up", "daddy s home"):
        return {"reply": _r(ap.check_r), "intent": "status"}
    if has("who are you", "what are you", "your name", "introduce yourself"):
        return {"reply": "I am %s, sir — just a rather very intelligent system, at your service." % config.ASSISTANT_NAME,
                "intent": "identity"}

    # --- greetings ---
    if cmd in ("hi", "hey", "hello", "yo", "hiya", "howdy", "hola", "sup") or \
            has("good morning", "good afternoon", "good evening", "how are you", "what s up", "whats up"):
        return {"reply": _r(ap.greet_r), "intent": "greet"}

    # --- time / date ---
    if has("time"):
        return {"reply": datetime_info.tell_time(), "intent": "time"}
    if has("date", "what day", "today s date", "day is it"):
        return {"reply": datetime_info.tell_date(), "intent": "date"}

    # --- jokes ---
    if has("joke", "make me laugh", "amuse me", "something funny"):
        return {"reply": tell_joke.startJoke(), "intent": "joke"}

    # --- weather ---
    # Only use the built-in OpenWeatherMap skill when it can actually work;
    # otherwise let the reasoning brain (with live web search) answer instead
    # of parroting "no API key configured".
    if has("weather", "forecast", "umbrella", "temperature", "how hot", "how cold", "is it raining", "how s the sky"):
        if os.environ.get("OWM_API_KEY") or chat_provider() is None:
            m = re.search(r"(?:weather|forecast|temperature)\s+(?:in|for|at)\s+(.+)", cmd)
            city = m.group(1).strip() if m else config.CITY
            return {"reply": get_weather.weather(city), "intent": "weather"}

    # --- power (gated) ---
    if has("shut down", "shutdown", "power off", "turn off the computer"):
        if os.environ.get("JARVIS_WEB_ALLOW_POWER") == "1":
            from jarvis.skills import power_options
            power_options.shutdown()
            return {"reply": "Shutting down the system, sir.", "intent": "power"}
        return {"reply": "Power controls are disabled from the web interface, sir.", "intent": "denied"}

    # --- system status ---
    if has("battery", "power level", "battery level", "charge"):
        return {"reply": check_hardware.getbattery(), "intent": "battery"}
    if has("ram", "memory", "virtual memory"):
        return {"reply": check_hardware.getram(), "intent": "ram"}
    if has("cpu", "processor", "cores"):
        return {"reply": check_hardware.getcpuper(False), "intent": "cpu"}

    # --- explicit wikipedia lookups ---
    # With a reasoning brain configured, only an explicit "wikipedia" request
    # goes to the encyclopedia; everything else deserves the smarter answer.
    _wiki_triggers = ("search wikipedia for", "wikipedia") if chat_provider() else \
        ("search wikipedia for", "wikipedia", "look up", "search for", "tell me about")
    for trigger in _wiki_triggers:
        if cmd.startswith(trigger):
            topic = cmd[len(trigger):].strip()
            if topic:
                return {"reply": wikipedia_search.search(topic), "intent": "wikipedia"}

    # --- conversational fallback (any question/statement) via the brain ---
    answer = _chat(raw)
    if answer:
        return {"reply": answer, "intent": "chat"}
    if chat_provider() is not None:
        # A brain IS configured but the call failed — say WHY instead of
        # pretending not to know. This turns a silent outage into a fix.
        err = _last_brain_error or "no response from the API"
        low = err.lower()
        if "credit" in low or "billing" in low or "purchase" in low:
            hint = " The API account is out of credits — add credits at console.anthropic.com under Billing."
        elif "401" in err or "authentication" in low or "invalid x-api-key" in low:
            hint = " The API key was rejected — it may be mistyped, expired, or revoked."
        elif "overloaded" in low or "529" in err or "rate" in low:
            hint = " The service is briefly overloaded — try again in a moment."
        else:
            hint = ""
        return {"reply": "My reasoning core hit an error, sir: %s.%s" % (err, hint),
                "intent": "brain-error"}

    # --- informational questions -> Wikipedia best-effort ---
    if has("who is", "who was", "what is", "what are", "where is", "who are"):
        topic = re.sub(r"^(who is|who was|what is|what are|where is|who are)\s+", "", cmd).strip()
        if topic:
            return {"reply": wikipedia_search.search(topic), "intent": "wikipedia"}

    # --- computational fallback -> Wolfram Alpha ---
    _ensure_wolfram()
    a = wolfram.startWolfram(cmd)
    if a:
        return {"reply": a, "intent": "wolfram"}

    return {
        "reply": "I'm not sure how to help with that yet, sir. Try the time, the weather, "
                 "a joke, your system stats, or ask me a question.",
        "intent": "unknown",
    }
