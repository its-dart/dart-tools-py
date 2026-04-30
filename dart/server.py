"""A small Flask server, optionally tunneled via ngrok.

Handles both:
  * arbitrary requests, returning a configurable JSON body
  * Dart webhook events (signature-verified) — see https://help.dartai.com/articles/9024895-webhooks
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from typing import Any, Union

import httpx
from flask import Flask, Response, jsonify, request
from werkzeug.serving import make_server

from .generated.models import Comment, Doc, Task
from .webhook import is_signature_correct

DEFAULT_PORT = 3350

_NGROK_API_URL = "http://127.0.0.1:4040/api/tunnels"


def _start_ngrok(port: int, timeout: float = 5.0) -> Union[subprocess.Popen, None]:
    if shutil.which("ngrok") is None:
        print("ngrok not found on PATH, skipping tunnel")
        return None

    proc = subprocess.Popen(
        ["ngrok", "http", str(port), "--log=stdout"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            tunnels = httpx.get(_NGROK_API_URL, timeout=1.0).json().get("tunnels") or []
            if tunnels:
                print(f"ngrok tunnel: {tunnels[0]['public_url']} -> http://localhost:{port}")
                return proc
        except (httpx.HTTPError, ValueError, KeyError):
            pass
        time.sleep(0.2)

    print("ngrok did not come up in time, continuing without a tunnel")
    proc.terminate()
    return None


def _handle_webhook(payload: bytes) -> bool:
    try:
        event = json.loads(payload)
    except (TypeError, ValueError) as ex:
        print(f"Webhook error while parsing event: {ex}")
        return False

    signature = request.headers.get("Dart-Signature")
    if not signature or not is_signature_correct(payload, signature):
        print("Webhook signature verification failed")
        return False

    event_type = event.get("type")
    data = event.get("data", {})
    match event_type:
        case "task.created":
            print(f"Task created:\n{Task.from_dict(data['model']).to_dict()}")
        case "task.updated":
            old_task = Task.from_dict(data["oldModel"])
            task = Task.from_dict(data["model"])
            print(f"Task updated from:\n{old_task.to_dict()}\nto:\n{task.to_dict()}")
        case "task.status_updated":
            task = Task.from_dict(data["model"])
            print(f"Task status updated from {data['oldStatus']!r} to {data['newStatus']!r}:\n{task.to_dict()}")
        case "task.assignees_updated":
            task = Task.from_dict(data["model"])
            print(
                f"Task assignees updated from {data['oldAssignees']!r} to {data['newAssignees']!r}:\n{task.to_dict()}"
            )
        case "task.deleted":
            print(f"Task deleted:\n{Task.from_dict(data['model']).to_dict()}")
        case "doc.created":
            print(f"Doc created:\n{Doc.from_dict(data['model']).to_dict()}")
        case "doc.updated":
            old_doc = Doc.from_dict(data["oldModel"])
            doc = Doc.from_dict(data["model"])
            print(f"Doc updated from:\n{old_doc.to_dict()}\nto:\n{doc.to_dict()}")
        case "doc.deleted":
            print(f"Doc deleted:\n{Doc.from_dict(data['model']).to_dict()}")
        case "comment.created":
            print(f"Comment created:\n{Comment.from_dict(data['model']).to_dict()}")
        case _:
            print(f"Unhandled event type: {event_type}")
            return False
    return True


def make_app(response: Any = None) -> Flask:
    """Build a Flask app that returns ``response`` as JSON and verifies Dart webhooks."""
    payload = response if response is not None else {"ok": True}
    app = Flask(__name__)

    @app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
    @app.route("/<path:path>", methods=["GET", "POST"])
    def handle(path: str) -> Response:  # pylint: disable=unused-variable
        body = request.get_data() or b""
        print(f"{request.method} /{path}")
        if body:
            try:
                print(json.dumps(json.loads(body), indent=2))
            except (ValueError, TypeError):
                print(body.decode("utf-8", errors="replace"))

        if request.headers.get("Dart-Signature") is not None:
            ok = _handle_webhook(body)
            return jsonify(success=ok)

        return jsonify(payload)

    return app


def run_server(response: Any = None, port: int = DEFAULT_PORT, no_ngrok: bool = False) -> None:
    """Run the Flask server, optionally with an ngrok tunnel."""
    app = make_app(response)
    print(
        f"Listening on http://localhost:{port} (default response: {json.dumps(response if response is not None else {'ok': True})})"
    )

    ngrok_proc = None if no_ngrok else _start_ngrok(port)
    server = make_server("0.0.0.0", port, app)
    print("Press CTRL+C to quit")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if ngrok_proc is not None:
            ngrok_proc.terminate()
