"""Flask backend serving the J.A.R.V.I.S web HUD and its JSON API."""

import os
import webbrowser
from datetime import datetime
from pathlib import Path

# Importing config loads the project's .env (if python-dotenv is installed) so
# keys like ANTHROPIC_API_KEY / XTTS_SPEAKER_WAV are available before any request.
from jarvis import config  # noqa: F401

STATIC_DIR = Path(__file__).resolve().parent / "static"


def _stats():
    """Collect live system stats (best-effort; degrades without psutil)."""
    now = datetime.now()
    data = {
        "time": now.strftime("%H:%M:%S"),
        "time12": now.strftime("%I:%M %p").lstrip("0"),
        "date": now.strftime("%d"),
        "month": now.strftime("%B").upper(),
        "weekday": now.strftime("%A").upper(),
        "date_full": now.strftime("%d-%b, %A"),
        "cpu": None, "ram": None, "swap": None,
        "battery": None, "charging": None,
        "cores": [], "disk": [], "net_up": 0, "net_down": 0, "cpu_temp": None,
        "uptime": None,
    }
    try:
        import psutil

        data["cpu"] = psutil.cpu_percent(interval=None)
        data["cores"] = psutil.cpu_percent(interval=None, percpu=True)
        vm = psutil.virtual_memory()
        data["ram"] = vm.percent
        data["ram_used_gb"] = round(vm.used / 1e9, 1)
        data["ram_total_gb"] = round(vm.total / 1e9, 1)
        sm = psutil.swap_memory()
        data["swap"] = sm.percent

        batt = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
        if batt is not None:
            data["battery"] = round(batt.percent)
            data["charging"] = bool(batt.power_plugged)

        for part in psutil.disk_partitions(all=False)[:4]:
            try:
                usage = psutil.disk_usage(part.mountpoint)
                data["disk"].append({
                    "name": part.device,
                    "mount": part.mountpoint,
                    "percent": usage.percent,
                    "used_gb": round(usage.used / 1e9, 1),
                    "total_gb": round(usage.total / 1e9, 1),
                })
            except (PermissionError, OSError):
                continue

        net = psutil.net_io_counters()
        data["net_up"] = net.bytes_sent
        data["net_down"] = net.bytes_recv

        try:
            temps = psutil.sensors_temperatures() if hasattr(psutil, "sensors_temperatures") else {}
            for entries in temps.values():
                if entries:
                    data["cpu_temp"] = round(entries[0].current)
                    break
        except Exception:
            pass

        data["uptime"] = int(datetime.now().timestamp() - psutil.boot_time())
    except ImportError:
        pass
    return data


def create_app():
    """Build and return the Flask application."""
    from flask import Flask, jsonify, request, send_from_directory

    app = Flask(__name__, static_folder=None)

    @app.after_request
    def _no_cache(resp):
        # always serve the latest HUD, never a stale cached copy
        resp.headers["Cache-Control"] = "no-store, max-age=0"
        return resp

    @app.route("/")
    def index():
        return send_from_directory(STATIC_DIR, "index.html")

    @app.route("/static/<path:filename>")
    def static_files(filename):
        return send_from_directory(STATIC_DIR, filename)

    @app.route("/api/health")
    def health():
        from jarvis.web import tts
        return jsonify({
            "ok": True,
            "assistant": os.environ.get("JARVIS_ASSISTANT_NAME", "Jarvis"),
            "tts": tts.provider() is not None,
        })

    @app.route("/api/stats")
    def stats():
        return jsonify(_stats())

    @app.route("/api/voicetest")
    def voicetest():
        """Ground truth for 'why doesn't he sound right': asks ElevenLabs
        which voices this account can use and whether the configured
        voice id is among them."""
        import json as _json
        import urllib.request as _rq
        from jarvis.web.dispatch import _env_ascii, _ssl_context

        key = _env_ascii("ELEVENLABS_API_KEY")
        conf = os.environ.get("ELEVENLABS_VOICE_ID", "(not set — using stock Daniel)")
        if not key:
            return jsonify({"ok": False, "error": "no ELEVENLABS_API_KEY configured"})
        try:
            req = _rq.Request("https://api.elevenlabs.io/v1/voices",
                              headers={"xi-api-key": key})
            with _rq.urlopen(req, timeout=15, context=_ssl_context()) as r:
                voices = _json.loads(r.read()).get("voices", [])
        except Exception as exc:
            return jsonify({"ok": False, "error": str(exc)[:300]})
        mine = {v["voice_id"]: v.get("name", "?") for v in voices}

        # live synthesis check: does a real TTS request with this voice work?
        from jarvis.web import tts as ttsmod
        audio, _mime = ttsmod.synthesize("Good evening, sir. All systems are operational.")
        return jsonify({
            "ok": True,
            "configured_voice_id": conf,
            "configured_voice_is_usable": conf in mine,
            "configured_voice_name": mine.get(conf),
            "synthesis_works": bool(audio),
            "synthesis_error": ttsmod.last_error,
            "hear_exact_backend_audio_at": "/api/voicetest/audio",
            "voices_in_your_account": [{"id": k, "name": n} for k, n in mine.items()],
        })

    @app.route("/api/voicetest/audio")
    def voicetest_audio():
        """Plays the raw audio the backend voice actually produces, with no
        HUD or fallback layers in between."""
        from flask import Response
        from jarvis.web import tts as ttsmod

        audio, mime = ttsmod.synthesize("Good evening, sir. All systems are operational.")
        if not audio:
            return ("Synthesis failed: %s" % (ttsmod.last_error or "unknown"), 500)
        return Response(audio, mimetype=mime)

    @app.route("/api/braintest")
    def braintest():
        """Live check of the reasoning brain so the HUD can report a broken
        key/billing problem instead of JARVIS silently playing dumb."""
        from jarvis.web import dispatch

        p = dispatch.chat_provider()
        if p is None:
            return jsonify({"ok": False, "provider": None,
                            "error": "no ANTHROPIC_API_KEY / OPENAI_API_KEY configured"})
        out = dispatch._chat("Reply with the single word: OK")
        return jsonify({"ok": bool(out), "provider": p,
                        "error": None if out else (dispatch._last_brain_error or "no response")})

    @app.route("/api/command", methods=["POST"])
    def command():
        from jarvis.web.dispatch import handle

        payload = request.get_json(silent=True) or {}
        result = handle(payload.get("text", ""))
        return jsonify(result)

    @app.route("/api/tts", methods=["POST"])
    def tts():
        from flask import Response
        from jarvis.web import tts as ttsmod

        payload = request.get_json(silent=True) or {}
        audio, mime = ttsmod.synthesize(payload.get("text", ""))
        if not audio:
            return ("", 204)  # not configured / failed -> HUD uses the browser voice
        return Response(audio, mimetype=mime)

    @app.route("/api/media/<action>", methods=["POST"])
    def media(action):
        from jarvis.nlp import playmusic

        actions = {
            "play": playmusic.startPlaymusic,
            "pause": playmusic.pauseMusic,
            "unpause": playmusic.unpauseMusic,
            "stop": playmusic.stopMusic,
        }
        fn = actions.get(action)
        if fn is None:
            return jsonify({"ok": False, "error": "unknown action"}), 400
        try:
            fn()
            return jsonify({"ok": True, "action": action})
        except Exception as exc:  # pragma: no cover - hardware dependent
            return jsonify({"ok": False, "error": str(exc)}), 200

    return app


def main():
    """Entry point for ``jarvis-web`` / ``python -m jarvis.web``."""
    host = os.environ.get("JARVIS_WEB_HOST", "127.0.0.1")
    port = int(os.environ.get("JARVIS_WEB_PORT", "8731"))
    url = f"http://{host}:{port}"

    try:
        app = create_app()
    except ImportError:
        raise SystemExit(
            "Flask is required for the web HUD. Install it with:\n"
            '    pip install -e ".[web]"'
        )

    # If a local cloned voice (XTTS) is configured, warm-load the model in the
    # background so the first spoken reply isn't a 20–30s stall.
    from jarvis.web import tts
    if tts.provider() == "xtts":
        import threading

        def _warm():
            try:
                print("  Preloading your cloned voice (XTTS) in the background…")
                tts.synthesize("Systems online.")
                print("  Voice ready.")
            except Exception as exc:  # pragma: no cover
                print(f"  [tts] voice preload failed: {exc}")

        threading.Thread(target=_warm, daemon=True).start()

    # Self-test the reasoning brain at startup and say the verdict out loud in
    # the terminal, so a dead key/billing problem is visible immediately.
    from jarvis.web import dispatch as _dispatch
    _brain = _dispatch.chat_provider()
    if _brain is None:
        print("  Brain: NOT CONFIGURED (set ANTHROPIC_API_KEY in .env for full answers)")
    else:
        import threading as _th

        def _brain_check():
            out = _dispatch._chat("Reply with the single word: OK")
            if out:
                print(f"  Brain: {_brain} — ONLINE")
            else:
                print(f"  Brain: {_brain} — FAILED: {_dispatch._last_brain_error}")

        _th.Thread(target=_brain_check, daemon=True).start()

    print(f"\n  J.A.R.V.I.S HUD online at {url}\n  Press Ctrl-C to shut down.\n")
    if os.environ.get("JARVIS_WEB_NO_BROWSER") != "1":
        try:
            webbrowser.open(url)
        except Exception:
            pass
    # threaded=True so slow speech synthesis never blocks commands/stats.
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
