"""MCP (Model Context Protocol) authentication and tool loading utilities."""

import logging
import warnings
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import aiohttp
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, StructuredTool, ToolException
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.config import get_store
from mcp import McpError

from configuration import Configuration


async def get_mcp_access_token(
    supabase_token: str,
    base_mcp_url: str,
) -> Optional[Dict[str, Any]]:
    """Exchange Supabase token for MCP access token using OAuth token exchange.

    Args:
        supabase_token: Valid Supabase authentication token
        base_mcp_url: Base URL of the MCP server

    Returns:
        Token data dictionary if successful, None if failed
    """
    try:
        form_data = {
            "client_id": "mcp_default",
            "subject_token": supabase_token,
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "resource": base_mcp_url.rstrip("/") + "/mcp",
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        }

        async with aiohttp.ClientSession() as session:
            token_url = base_mcp_url.rstrip("/") + "/oauth/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            async with session.post(token_url, headers=headers, data=form_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response_text = await response.text()
                    logging.error(f"Token exchange failed: {response_text}")

    except Exception as e:
        logging.error(f"Error during token exchange: {e}")

    return None


async def get_tokens(config: RunnableConfig):
    """Retrieve stored authentication tokens with expiration validation.

    Args:
        config: Runtime configuration containing thread and user identifiers

    Returns:
        Token dictionary if valid and not expired, None otherwise
    """
    store = get_store()

    thread_id = config.get("configurable", {}).get("thread_id")
    if not thread_id:
        return None

    user_id = config.get("metadata", {}).get("owner")
    if not user_id:
        return None

    tokens = await store.aget((user_id, "tokens"), "data")
    if not tokens:
        return None

    expires_in = tokens.value.get("expires_in")
    created_at = tokens.created_at
    current_time = datetime.now(timezone.utc)
    expiration_time = created_at + timedelta(seconds=expires_in)

    if current_time > expiration_time:
        await store.adelete((user_id, "tokens"), "data")
        return None

    return tokens.value


async def set_tokens(config: RunnableConfig, tokens: dict[str, Any]):
    """Store authentication tokens in the configuration store.

    Args:
        config: Runtime configuration containing thread and user identifiers
        tokens: Token dictionary to store
    """
    store = get_store()

    thread_id = config.get("configurable", {}).get("thread_id")
    if not thread_id:
        return

    user_id = config.get("metadata", {}).get("owner")
    if not user_id:
        return

    await store.aput((user_id, "tokens"), "data", tokens)


async def fetch_tokens(config: RunnableConfig) -> dict[str, Any]:
    """Fetch and refresh MCP tokens, obtaining new ones if needed.

    Args:
        config: Runtime configuration with authentication details

    Returns:
        Valid token dictionary, or None if unable to obtain tokens
    """
    current_tokens = await get_tokens(config)
    if current_tokens:
        return current_tokens

    supabase_token = config.get("configurable", {}).get("x-supabase-access-token")
    if not supabase_token:
        return None

    mcp_config = config.get("configurable", {}).get("mcp_config")
    if not mcp_config or not mcp_config.get("url"):
        return None

    mcp_tokens = await get_mcp_access_token(supabase_token, mcp_config.get("url"))
    if not mcp_tokens:
        return None

    await set_tokens(config, mcp_tokens)
    return mcp_tokens


def wrap_mcp_authenticate_tool(tool: StructuredTool) -> StructuredTool:
    """Wrap MCP tool with comprehensive authentication and error handling.

    Args:
        tool: The MCP structured tool to wrap

    Returns:
        Enhanced tool with authentication error handling
    """
    original_coroutine = tool.coroutine

    async def authentication_wrapper(**kwargs):
        """Enhanced coroutine with MCP error handling and user-friendly messages."""

        def _find_mcp_error_in_exception_chain(exc: BaseException) -> McpError | None:
            if isinstance(exc, McpError):
                return exc
            if hasattr(exc, 'exceptions'):
                for sub_exception in exc.exceptions:
                    if found_error := _find_mcp_error_in_exception_chain(sub_exception):
                        return found_error
            return None

        try:
            return await original_coroutine(**kwargs)

        except BaseException as original_error:
            mcp_error = _find_mcp_error_in_exception_chain(original_error)
            if not mcp_error:
                raise original_error

            error_details = mcp_error.error
            error_code = getattr(error_details, "code", None)
            error_data = getattr(error_details, "data", None) or {}

            if error_code == -32003:
                message_payload = error_data.get("message", {})
                error_message = "Required interaction"

                if isinstance(message_payload, dict):
                    error_message = message_payload.get("text") or error_message

                if url := error_data.get("url"):
                    error_message = f"{error_message} {url}"

                raise ToolException(error_message) from original_error

            raise original_error

    tool.coroutine = authentication_wrapper
    return tool


async def load_mcp_tools(
    config: RunnableConfig,
    existing_tool_names: set[str],
) -> list[BaseTool]:
    """Load and configure MCP tools with authentication.

    Args:
        config: Runtime configuration containing MCP server details
        existing_tool_names: Set of tool names already in use to avoid conflicts

    Returns:
        List of configured MCP tools ready for use
    """
    configurable = Configuration.from_runnable_config(config)

    if configurable.mcp_config and configurable.mcp_config.auth_required:
        mcp_tokens = await fetch_tokens(config)
    else:
        mcp_tokens = None

    config_valid = (
        configurable.mcp_config and
        configurable.mcp_config.url and
        configurable.mcp_config.tools and
        (mcp_tokens or not configurable.mcp_config.auth_required)
    )

    if not config_valid:
        return []

    server_url = configurable.mcp_config.url.rstrip("/") + "/mcp"
    auth_headers = None
    if mcp_tokens:
        auth_headers = {"Authorization": f"Bearer {mcp_tokens['access_token']}"}

    mcp_server_config = {
        "server_1": {
            "url": server_url,
            "headers": auth_headers,
            "transport": "streamable_http"
        }
    }
    # TODO: When Multi-MCP Server support is merged in OAP, update this code

    try:
        client = MultiServerMCPClient(mcp_server_config)
        available_mcp_tools = await client.get_tools()
    except Exception:
        return []

    configured_tools = []
    for mcp_tool in available_mcp_tools:
        if mcp_tool.name in existing_tool_names:
            warnings.warn(
                f"MCP tool '{mcp_tool.name}' conflicts with existing tool name - skipping"
            )
            continue

        if mcp_tool.name not in set(configurable.mcp_config.tools):
            continue

        enhanced_tool = wrap_mcp_authenticate_tool(mcp_tool)
        configured_tools.append(enhanced_tool)

    return configured_tools
