"""
FastAPI + FastMCP application for the Economic Intelligence MCP Server.

Sets up the FastMCP server, registers tools, and combines MCP routes
with standard FastAPI routes into a single ASGI app served by uvicorn.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastmcp import FastMCP

from .tools import load_tools
from .utils import header_store

# ── MCP server ─────────────────────────────────────────────────────────────────
mcp_server = FastMCP(
    name="economic-intelligence-mcp",
    instructions=(
        "Use this server to fetch live macroeconomic data from public sources "
        "(inflation, GDP growth, interest rates, unemployment) for any country, "
        "and to analyse economic data on public webpages using AI. "
        "Genie spaces for structured internal data are handled by the Supervisor Agent."
    ),
)

STATIC_DIR = Path(__file__).parent / "../static"

# Register all tools
load_tools(mcp_server)

# Streamable HTTP app (MCP protocol over HTTP)
mcp_app = mcp_server.http_app()

# ── FastAPI app ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Economic Intelligence MCP Server",
    description="External macroeconomic data tools for the Databricks Supervisor Agent.",
    version="1.0.0",
    lifespan=mcp_app.lifespan,
)


@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve the status page."""
    if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
        return FileResponse(STATIC_DIR / "index.html")
    return {"message": "Economic Intelligence MCP Server is running", "status": "healthy"}


# ── Combined app (MCP routes + custom routes) ──────────────────────────────────
combined_app = FastAPI(
    title="Economic Intelligence MCP Server",
    routes=[
        *mcp_app.routes,
        *app.routes,
    ],
    lifespan=mcp_app.lifespan,
)


@combined_app.middleware("http")
async def capture_headers(request: Request, call_next):
    """Capture request headers so tools can use the user's OAuth token."""
    header_store.set(dict(request.headers))
    return await call_next(request)
