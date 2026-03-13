"""Entry point — starts the uvicorn server."""

import argparse

import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Start the Economic Intelligence MCP Server")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    args = parser.parse_args()

    uvicorn.run(
        "server.app:combined_app",
        host="0.0.0.0",
        port=args.port,
    )
