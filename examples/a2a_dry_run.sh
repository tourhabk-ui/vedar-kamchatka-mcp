#!/usr/bin/env bash
# Dry run of the open A2A agent of Vedar Kamchatka (test: true).
# Nothing is stored; nobody is notified.
# Agent card: https://vedarai.ru/.well-known/agent-card.json
set -euo pipefail

A2A_URL="${A2A_URL:-https://vedarai.ru/api/a2a}"
export MESSAGE_ID="$(python3 -c 'import uuid; print(uuid.uuid4())')"

PAYLOAD="$(python3 - <<'PY'
import json, os
print(json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "message/send",
    "params": {
        "message": {
            "messageId": os.environ["MESSAGE_ID"],
            "role": "user",
            "parts": [{
                "kind": "data",
                "data": {
                    "tool": "create_lead",
                    "arguments": {
                        "name": "Dry Run Example",
                        "phone": "+79990000000",
                        "comment": "Dry-run check of the open A2A agent; not a real request.",
                        "consent": True,
                        "test": True,
                    },
                },
            }],
        },
    },
}, ensure_ascii=False))
PY
)"

curl -sS "$A2A_URL" \
  -H "Content-Type: application/json" \
  -H "A2A-Version: 1.0" \
  -d "$PAYLOAD"
echo
