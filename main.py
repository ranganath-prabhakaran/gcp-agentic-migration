# gcp-agentic-migration/main.py
import argparse
import asyncio
import autogen_agentchat as ag
from modelcontextprotocol.client.ws import McpWsClient

from agents.setup_agent import build_setup_agent
from agents.schema_agent import build_schema_agent
from agents.migration_agent import build_migration_agent
from agents.validation_agent import build_validation_agent
from agents.anomaly_agent import build_anomaly_agent
from agents.optimization_agent import build_optimization_agent
from utils.gcp_secrets import get_secret
import config

async def main(volume: int, encryption: str):
    # 1. Configure LLM
    if "openai" in config.LLM_PROVIDER:
        api_key = get_secret(config.OPENAI_API_KEY_SECRET)
        model_name = config.LLM_PROVIDER.split('/')[1]
        llm_config = {"model": model_name, "api_key": api_key, "temperature": 0.1}
    elif "google" in config.LLM_PROVIDER:
        api_key = get_secret(config.GEMINI_API_KEY_SECRET)
        model_name = config.LLM_PROVIDER.split('/')[1]
        llm_config = {"model": model_name, "api_key": api_key, "temperature": 0.1}
    else:
        raise ValueError(f"Unsupported LLM provider: {config.LLM_PROVIDER}")

    # 2. Connect to the MCP Server
    # Note: In a real implementation, you'd start the server as a subprocess.
    # For this example, we assume it's running separately.
    mcp_client = McpWsClient(url="ws://localhost:8000/mcp")
    await mcp_client.connect()

    # 3. Build the Agent Team
    user_proxy = ag.UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=config.AUTOGEN_MAX_CONSECUTIVE_AUTO_REPLY,
        is_termination_msg=lambda x: "MIGRATION COMPLETE" in x.get("content", "").upper() or "TASK FAILED" in x.get("content", "").upper(),
        code_execution_config=False,
    )

    setup_agent = build_setup_agent(mcp_client, llm_config)
    schema_agent = build_schema_agent(mcp_client, llm_config)
    migration_agent = build_migration_agent(mcp_client, llm_config)
    validation_agent = build_validation_agent(mcp_client, llm_config)
    anomaly_agent = build_anomaly_agent(llm_config)
    optimization_agent = build_optimization_agent(llm_config)

    # 4. Define the Group Chat
    groupchat = ag.RoundRobinGroupChat(
        agents=[user_proxy, setup_agent, schema_agent, migration_agent, validation_agent, anomaly_agent, optimization_agent],
        messages=[],
    )
    manager = ag.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # 5. Formulate the initial task and start the chat
    initial_task = f"""
    Start the legacy MySQL database migration process.
    The estimated database volume is {volume} GB.
    The user has selected the '{encryption}' encryption strategy.

    Follow this sequence of operations:
    1. The Environment_Setup_Agent must provision the infrastructure.
    2. The Schema_Conversion_Agent must analyze and convert the source schema.
    3. The Data_Migration_Agent must select the correct strategy based on the volume ({volume} GB) and migrate the data.
    4. The Data_Validation_Agent must verify the integrity of the migrated data.
    5. The Performance_Optimization_Agent must provide a final report after the migration is complete.
    6. The Anomaly_Detection_Agent must monitor the entire process for errors.
    7. If all steps are successful, the final message must include the phrase 'MIGRATION COMPLETE'. If any step fails critically, end with 'TASK FAILED'.
    """

    await user_proxy.a_initiate_chat(
        manager,
        message=initial_task,
    )

    await mcp_client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Agentic MySQL to Cloud SQL Migration.")
    parser.add_argument("--volume", type=int, required=True, help="Estimated volume of the database in GB.")
    parser.add_argument("--encryption", type=str, required=True, choices=['legacy', 'gcp-recommended'], help="Encryption strategy to use.")
    args = parser.parse_args()
    
    asyncio.run(main(args.volume, args.encryption))