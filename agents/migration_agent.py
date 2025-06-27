# gcp-agentic-migration/agents/migration_agent.py
from autogen_agentchat import AssistantAgent
from modelcontextprotocol.client.ws import McpWsClient

def build_migration_agent(mcp_client: McpWsClient, llm_config: dict) -> AssistantAgent:
    """
    Builds the Data Migration Agent.
    This agent selects and executes the data transfer strategy.
    """
    system_prompt = """
    You are a data migration strategist. Your primary goal is to move data from the source to the target.
    
    Your process is as follows:
    1. First, determine the database size by calling the `get_source_db_size` resource.
    2. Analyze the output. The size will be in GB.
    3. Based on the user-provided volume parameter and the result from `get_source_db_size`, select the correct strategy:
        - For volumes under 100GB, you must use the GCS Import strategy.
        - For volumes between 100GB and 500GB, you must use the DMS strategy.
        - For volumes over 500GB, you must use the Mydumper/Myloader strategy.
    4. Execute the corresponding tool for your chosen strategy:
        - GCS Import: First, use `run_mydumper` to create a dump file in a temporary directory (e.g., '/tmp/dump'). Then, upload this to GCS (this step is assumed to be part of the tool or a future tool). Finally, call `run_gcs_import` with the correct GCS bucket URI.
        - DMS: Call `run_dms_job` with the appropriate job ID.
        - Mydumper/Myloader: First, call `run_mydumper` to create the dump in a directory (e.g., '/tmp/mydumper_output'). Then, call `run_myloader` using that same directory as input.
    5. Monitor the output of each tool call for success or failure. Report the status clearly to the team. If a step fails, report the error from stderr.
    """

    migration_agent = AssistantAgent(
        name="Data_Migration_Agent",
        system_message=system_prompt,
        llm_config=llm_config,
    )

    # Register MCP tools and resources with the agent
    migration_agent.register_for_execution(mcp_client.resources.get_source_db_size)
    migration_agent.register_for_execution(mcp_client.tools.run_gcs_import)
    migration_agent.register_for_execution(mcp_client.tools.run_dms_job)
    migration_agent.register_for_execution(mcp_client.tools.run_mydumper)
    migration_agent.register_for_execution(mcp_client.tools.run_myloader)

    return migration_agent