#!/usr/bin/env bash
# Read-only calls to the open MCP server of Vedar Kamchatka.
# Docs: https://vedarai.ru/mcp
set -euo pipefail

MCP_URL="${MCP_URL:-https://vedarai.ru/api/mcp}"
ACCEPT="application/json, text/event-stream"

mcp() {
  local body="$1"
  curl -sS "$MCP_URL" \
    -H "Content-Type: application/json" \
    -H "Accept: ${ACCEPT}" \
    -d "$body"
}

echo "== initialize =="
mcp '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {},
    "clientInfo": { "name": "vedar-kamchatka-mcp-examples", "version": "0.1.0" }
  }
}'
echo

echo "== tools/list =="
mcp '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
echo

echo "== tools/call get_volcano_status (read-only) =="
mcp '{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_volcano_status",
    "arguments": { "volcano": "Шивелуч" }
  }
}'
echo
