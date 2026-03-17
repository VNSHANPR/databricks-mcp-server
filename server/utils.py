import contextvars
import os

from databricks.sdk import WorkspaceClient

header_store = contextvars.ContextVar("header_store")


def get_workspace_client() -> WorkspaceClient:
    """Return a service-principal authenticated workspace client."""
    return WorkspaceClient()


def get_user_authenticated_workspace_client() -> WorkspaceClient:
    """
    Return an authenticated workspace client.

    Auth resolution order:
      1. Interactive user session (browser): uses x-forwarded-access-token injected
         by the Databricks Apps proxy — acts on behalf of the end user.
      2. Agent / M2M call (Supervisor Agent via UC connection): no forwarded token
         is present, so falls back to the app's own service principal credentials,
         which the Databricks Apps runtime injects automatically via environment
         variables (DATABRICKS_HOST, DATABRICKS_CLIENT_ID, DATABRICKS_CLIENT_SECRET).
      3. Local development: uses default SDK auth (~/.databrickscfg or env vars).
    """
    headers = header_store.get({})
    token = headers.get("x-forwarded-access-token")

    if token:
        # Interactive user session — act on behalf of the user
        return WorkspaceClient(token=token, auth_type="pat")

    # Agent/M2M call or local dev — use app SP credentials (auto-injected by runtime)
    return WorkspaceClient()
