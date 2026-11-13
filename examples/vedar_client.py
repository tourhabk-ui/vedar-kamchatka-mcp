#!/usr/bin/env python3
"""Small client for the open MCP server and open A2A agent of Vedar Kamchatka.

Read-only MCP calls, plus an A2A create_lead dry run (test: true).
Standard library only. Docs: https://vedarai.ru/mcp
"""

from __future__ import annotations

import json
import sys
import uuid
import urllib.error
import urllib.request

MCP_URL = "https://vedarai.ru/api/mcp"
A2A_URL = "https://vedarai.ru/api/a2a"
AGENT_CARD_URL = "https://vedarai.ru/.well-known/agent-card.json"


def post(url: str, payload: dict, headers: dict, timeout: int = 30) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            status = response.status
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8")
        print(f"HTTP {error.code} from {url}", file=sys.stderr)
        print(body[:2000], file=sys.stderr)
        raise SystemExit(1) from error
    print(f"HTTP {status} {url}")
    return json.loads(body)


def get(url: str, timeout: int = 30) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        print(f"HTTP {response.status} {url}")
        return json.loads(response.read().decode("utf-8"))


def mcp(method: str, params: dict, call_id: int) -> dict:
    return post(
        MCP_URL,
        {"jsonrpc": "2.0", "id": call_id, "method": method, "params": params},
        {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )


def preview(obj: object, limit: int = 500) -> str:
    text = json.dumps(obj, ensure_ascii=False)
    return text if len(text) <= limit else text[:limit] + "…"


def main() -> None:
    card = get(AGENT_CARD_URL)
    print(
        "agent card:",
        card.get("name"),
        "version",
        card.get("version"),
        "docs",
        card.get("documentationUrl"),
    )

    init = mcp(
        "initialize",
        {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {
                "name": "vedar-kamchatka-mcp-examples",
                "version": "0.1.0",
            },
        },
        1,
    )
    server = init["result"]["serverInfo"]
    print(
        "MCP initialize:",
        server.get("name"),
        server.get("title"),
        "version",
        server.get("version"),
        "protocol",
        init["result"].get("protocolVersion"),
    )

    listed = mcp("tools/list", {}, 2)
    tools = listed["result"]["tools"]
    print(f"tools/list: {len(tools)} tools")
    print("names:", ", ".join(tool["name"] for tool in tools))

    call = mcp(
        "tools/call",
        {"name": "get_volcano_status", "arguments": {"volcano": "Шивелуч"}},
        3,
    )
    content = call.get("result", {}).get("content") or []
    first = content[0].get("text", "") if content and isinstance(content[0], dict) else preview(call)
    print("get_volcano_status:", first[:400].replace("\n", " / "))

    # Dry run only: test: true stores nothing and notifies no one.
    a2a = post(
        A2A_URL,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "user",
                    "parts": [
                        {
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
                        }
                    ],
                }
            },
        },
        {"Content-Type": "application/json", "A2A-Version": "1.0"},
    )
    task = a2a.get("result", {}).get("task", {})
    status = task.get("status", {})
    parts = (status.get("message") or {}).get("parts") or []
    text_part = next((part.get("text") for part in parts if part.get("text")), "")
    data_part = next((part.get("data") for part in parts if part.get("data")), {})
    result = (data_part or {}).get("result") or {}
    print("A2A task state:", status.get("state"))
    print("create_lead dry run: test=", result.get("test"), "accepted=", result.get("accepted"))
    print(text_part[:500] if text_part else preview(a2a))


if __name__ == "__main__":
    main()
