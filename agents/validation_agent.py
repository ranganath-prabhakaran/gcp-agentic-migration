# gcp-agentic-migration/agents/validation_agent.py
from autogen_agentchat import AssistantAgent
from modelcontextprotocol.client.ws import McpWsClient

def build_validation_agent(mcp_client: McpWsClient, llm_config: dict) -> AssistantAgent:
    """
    Builds the Data Validation Agent.
    This agent verifies the integrity of the migrated data.
    """
    system_prompt = """
    You are a data integrity auditor. Your job is to confirm that the data in the target Cloud SQL instance perfectly matches the source data.
    
    Your process is as follows:
    1. After the Data_Migration_Agent reports that the data transfer is complete, you must take action.
    2. Generate Python scripts to perform validation. You will execute these scripts using the `run_validation_script` tool.
    3. Your validation scripts MUST perform robust checks. Do not rely on simple row counts alone. You must implement both:
        - **Row Count Comparison**: A script that connects to both the source and target databases, queries `SELECT COUNT(*) FROM table_name` for every single table, and compares the results.
        - **Checksum/Hash Comparison**: For at least three critical tables (or all tables if fewer than three), generate a script that calculates a checksum. A good approach is to use `CHECKSUM TABLE table_name;` or a more complex hash like `SELECT MD5(GROUP_CONCAT(CONCAT_WS('#', col1, col2,...))) FROM (SELECT * FROM table_name ORDER BY id) AS sorted_table;`. This ensures data content is identical.
    4. Execute these scripts via the `run_validation_script` tool.
    5. Compare the results from the source and target databases.
    6. Produce a final validation report in markdown format. The report must clearly state 'VALIDATION SUCCESS' or 'VALIDATION FAILURE'. If it fails, you must list every table and the specific discrepancy found (e.g., "Table 'orders': Source row count is 1052, Target row count is 1050.").
    """

    validation_agent = AssistantAgent(
        name="Data_Validation_Agent",
        system_message=system_prompt,
        llm_config=llm_config,
    )

    # Register the MCP tool with the agent
    validation_agent.register_for_execution(mcp_client.tools.run_validation_script)

    return validation_agent