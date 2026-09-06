"""
MCP Server for genpark-agent-dag-parallel-branch-fanout-join-skill
Standard JSON-RPC 2.0 protocol over stdio.
"""

import sys
import json
from client import ParallelBranchFanoutJoinClient

coordinator = ParallelBranchFanoutJoinClient()

def handle_request(req):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "fanout_tasks",
                        "description": "Initialize a parallel branch fanout barrier for subtasks.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "batch_id": {"type": "string"},
                                "tasks": {"type": "array", "items": {"type": "object"}}
                            },
                            "required": ["batch_id", "tasks"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "fanout_tasks":
            res = coordinator.fanout(args["batch_id"], args["tasks"])
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res)}]
                }
            }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_res = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
