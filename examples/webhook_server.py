#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# README: https://help.dartai.com/articles/9024895-webhooks


import json

from flask import Flask, Response, jsonify, request

from dart import Comment, Doc, Task, is_signature_correct

app = Flask(__name__)


@app.route("/", methods=["POST"])
def webhook() -> Response:
    payload = request.data

    # Parse the event
    try:
        event = json.loads(payload)
    except TypeError as ex:
        print(f"Webhook error while parsing event: {ex}")
        return jsonify(success=False)

    # Verify the signature of the event
    signature = request.headers.get("Dart-Signature")
    if not signature or not is_signature_correct(payload, signature):
        print("Webhook signature verification failed")
        return jsonify(success=False)

    # Handle the event
    event_type = event["type"]
    match event_type:
        case "task.created":
            task = Task.from_dict(event["data"]["model"])  # The task that was created
            print(f"Task created:\n{task.to_dict()}")
        case "task.updated":
            data = event["data"]
            task = Task.from_dict(data["model"])  # The new version of the task that was updated
            old_task = Task.from_dict(data["oldModel"])  # The old version of the task that was updated
            print(f"Task updated from:\n{old_task.to_dict()}\nfrom:\n{task.to_dict()}")
        case "task.deleted":
            task = Task.from_dict(event["data"]["model"])  # The task that was deleted
            print(f"Task deleted:\n{task.to_dict()}")
        case "doc.created":
            doc = Doc.from_dict(event["data"]["model"])  # The doc that was created
            print(f"Doc created:\n{doc.to_dict()}")
        case "doc.updated":
            data = event["data"]
            doc = Doc.from_dict(data["model"])  # The new version of the doc that was updated
            old_doc = Doc.from_dict(data["oldModel"])  # The old version of the doc that was updated
            print(f"Doc updated from:\n{old_doc.to_dict()}\nfrom:\n{doc.to_dict()}")
        case "doc.deleted":
            doc = Doc.from_dict(event["data"]["model"])  # The doc that was deleted
            print(f"Doc deleted:\n{doc.to_dict()}")
        case "comment.created":
            comment = Comment.from_dict(event["data"]["model"])  # The comment that was created
            print(f"Comment created:\n{comment.to_dict()}")
        case _:
            # Unexpected event type
            print(f"Unhandled event type: {event_type}")
            return jsonify(success=False)

    return jsonify(success=True)


if __name__ == "__main__":
    app.run(debug=True)
