import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.tools import get_ip_info
import datetime

def threat_intel_agent(state: dict) -> dict:
    """
    Real Threat Intel Agent: Uses Groq to autonomously trigger tools and analyze data.
    """
    # 1. Grab the IP from the state
    iocs = state.get("iocs", [])
    if not iocs:
        return {"threat_intel_report": "No IOCs provided for analysis."}
    
    # 2. Connect to Groq using Streamlit's secure secrets
    api_key = st.secrets["GROQ_API_KEY"]
    
    # Using Llama-3 8B because it is blazing fast for tool calling
    llm = ChatGroq(
        model="llama3-8b-8192", 
        temperature=0.2, 
        api_key=api_key
    )
    
    # 3. Give the LLM access to our tool
    llm_with_tools = llm.bind_tools([get_ip_info])
    
    # 4. Give the AI its instructions
    sys_msg = SystemMessage(
        content="You are a Senior Cyber Threat Intelligence Analyst. "
                "Use your tools to investigate the provided IP addresses. "
                "Write a brief 2-sentence intelligence report summarizing what you found."
    )
    user_msg = HumanMessage(content=f"Investigate this IP: {iocs[0]}")
    
    # 5. Let the AI think and act
    response = llm_with_tools.invoke([sys_msg, user_msg])
    
    # 6. Check if the AI decided to use the tool
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        
        if tool_call['name'] == 'get_ip_info':
            ip_arg = tool_call['args']['ip_address']
            
            # Execute the python function
            tool_result = get_ip_info.invoke({"ip_address": ip_arg})
            
            # Send the data back to the AI so it can write the final report
            final_msg = HumanMessage(content=f"The tool returned: {tool_result}. Write the final report.")
            final_response = llm.invoke([sys_msg, user_msg, response, final_msg])
            report_text = final_response.content
    else:
        report_text = response.content

    # 7. Update the LangGraph State
    log = {
        "agent": "ThreatIntel (Groq)", 
        "action": "Autonomously queried external API", 
        "timestamp": str(datetime.datetime.now())
    }
    
    return {
        "threat_intel_report": report_text, 
        "explainability_log": [log]
    }
