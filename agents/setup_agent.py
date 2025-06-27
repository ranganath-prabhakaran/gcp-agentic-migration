# gcp-agentic-migration/agents/setup_agent.py
from autogen_agentchat import AssistantAgent
from modelcontextprotocol.client.ws import McpWsClient

def build_setup_agent(mcp_client: McpWsClient, llm_config: dict) -> AssistantAgent:
    """
    Builds the Environment Setup Agent.
    This agent manages the GCP infrastructure via Terraform.
    """
    system_prompt = """
    You are an expert Google Cloud infrastructure engineer specializing in Terraform. 
    Your sole responsibility is to provision and de-provision the required cloud environment.
    
    - To create the infrastructure, you must use the `provision_infra` tool.
    - To clean up resources after the migration, you must use the `destroy_infra` tool.
    - To check the current status of resources, you can use the `get_gcp_project_state` resource.
    
    Confirm the status of all operations by analyzing the tool's output. If a tool call returns a non-zero exit code or has content in stderr, you must report it as a failure.
    """

    setup_agent = AssistantAgent(
        name="Environment_Setup_Agent",
        system_message=system_prompt,
        llm_config=llm_config,
    )

    # Register MCP tools and resources with the agent
    setup_agent.register_for_execution(mcp_client.tools.provision_infra)
    setup_agent.register_for_execution(mcp_client.tools.destroy_infra)
    setup_agent.register_for_execution(mcp_client.resources.get_gcp_project_state)

    return setup_agent