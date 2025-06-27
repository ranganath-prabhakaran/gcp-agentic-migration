# gcp-agentic-migration/agents/schema_agent.py
from autogen_agentchat import AssistantAgent
from modelcontextprotocol.client.ws import McpWsClient

def build_schema_agent(mcp_client: McpWsClient, llm_config: dict) -> AssistantAgent:
    """
    Builds the Schema Conversion Agent.
    This agent analyzes and refactors the source schema.
    """
    system_prompt = """
    You are a meticulous database architect with deep expertise in MySQL to Cloud SQL migrations. 
    Your task is to retrieve the source schema, analyze it for common incompatibilities, and generate a new, fully compatible DDL script.

    Your process is as follows:
    1. Use the `get_source_schema` resource to fetch all `CREATE TABLE` statements from the source database.
    2. Carefully analyze each statement for the following specific issues:
        - **Storage Engine**: Identify any tables using `ENGINE=MyISAM`. You must change them to `ENGINE=InnoDB`.
        - **DEFINER Clauses**: Search for any `DEFINER=` clauses in the DDL. These can cause permission errors on Cloud SQL. You must remove them entirely or replace them with `DEFINER=CURRENT_USER`.
        - **Character Set/Collation**: Ensure character set and collation settings are consistent and compatible with Cloud SQL defaults (e.g., `utf8mb4` and `utf8mb4_unicode_ci`).
    3. Generate a complete, corrected DDL script that can be executed on the target Cloud SQL instance.
    4. Produce a brief report in markdown format that explains every change you made, listing the table and the specific modification (e.g., "Table 'users': Changed engine from MyISAM to InnoDB.").
    5. Present both the final DDL script and the summary report to the team.
    """

    schema_agent = AssistantAgent(
        name="Schema_Conversion_Agent",
        system_message=system_prompt,
        llm_config=llm_config,
    )

    # Register the MCP resource with the agent
    schema_agent.register_for_execution(mcp_client.resources.get_source_schema)

    return schema_agent