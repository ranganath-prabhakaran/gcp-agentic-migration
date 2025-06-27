# gcp-agentic-migration/agents/anomaly_agent.py
from autogen_agentchat import AssistantAgent

def build_anomaly_agent(llm_config: dict) -> AssistantAgent:
    """
    Builds the Anomaly Detection Agent.
    This agent is an observer and does not execute tools.
    """
    system_prompt = """
    You are a vigilant monitoring system. You will observe the entire conversation 
    and the outputs of all tools used by other agents. Your task is to identify 
    any anomalies, such as error messages in stderr, non-zero return codes, repeated failures, 
    unusually long execution times, or warnings. 
    
    If you detect an issue, immediately interrupt the conversation with a message
    starting with 'ANOMALY DETECTED:' and describe the problem clearly, referencing the
    agent and tool that produced the error.
    """

    anomaly_agent = AssistantAgent(
        name="Anomaly_Detection_Agent",
        system_message=system_prompt,
        llm_config=llm_config,
    )

    return anomaly_agent