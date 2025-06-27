# gcp-agentic-migration/mcp_server/server.py

import uvicorn
from fastapi import FastAPI
from modelcontextprotocol.server.fastapi import McpRouter
from.handlers import MigrationToolHandlers

app = FastAPI(
    title="Agentic Migration MCP Server",
    description="Exposes migration utilities as secure tools for AI agents.",
)

# Instantiate handlers
handlers = MigrationToolHandlers()

# Create an MCP router and register the handlers
mcp_router = McpRouter(
    resources={
        "get_source_db_size": handlers.get_source_db_size,
        "get_source_schema": handlers.get_source_schema,
        "get_gcp_project_state": handlers.get_gcp_project_state,
    },
    tools={
        "provision_infra": handlers.provision_infra,
        "destroy_infra": handlers.destroy_infra,
        "run_gcs_import": handlers.run_gcs_import,
        "run_dms_job": handlers.run_dms_job,
        "run_mydumper": handlers.run_mydumper,
        "run_myloader": handlers.run_myloader,
        "run_validation_script": handlers.run_validation_script,
    },
    prompts={
        "get_gcp_encryption_recommendation": handlers.get_gcp_encryption_recommendation,
    },
)

# Include the MCP router in the FastAPI app
app.include_router(mcp_router, prefix="/mcp")

@app.get("/")
async def root():
    return {"message": "MCP Server is running. Use the /mcp endpoint."}

if __name__ == "__main__":
    # This allows running the server directly for testing
    uvicorn.run(app, host="0.0.0.0", port=8000)