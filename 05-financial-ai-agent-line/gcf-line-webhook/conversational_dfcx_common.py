from pathlib import Path
from datetime import datetime
import pytz
from dotenv import load_dotenv
from dfcx_scrapi.core.sessions import Sessions
from proto.marshal.collections import maps
from linebot.v3.messaging import ReplyMessageRequest, TextMessage
from flex_builder import (
        build_fund_flex_message,
        build_tax_flex
    )

import os

# Load environment variables
load_dotenv()
creds_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
project_id = os.environ["CONVERSATIONAL_AGENT_PROJECT_ID"]
location_id = os.environ["CONVERSATIONAL_AGENT_LOCATION"]
agent_id = os.environ["CONVERSATIONAL_AGENT_ID"]


def generate_session_path(user_id: str) -> str:
    """Generate a session path with timestamp and user ID."""
    bkk_tz = pytz.timezone("Asia/Bangkok")
    current_time = datetime.now(bkk_tz).strftime("%m%d%H")
    trimmed_user_id = user_id[:20].lower()
    session_id = f"line-{trimmed_user_id}-{current_time}"
    return f"projects/{project_id}/locations/{location_id}/agents/{agent_id}/sessions/{session_id}"


def parse_tool_response(tool_name: str, output_params: dict, input_params: dict) -> list[TextMessage]:
    """Create LINE message(s) from tool response."""
    messages = []

    if tool_name == "loan_calculator":
        max_loan = output_params.get("max_loan", 0)
        monthly_payment = output_params.get("monthly_payment", 0)
        messages.append(
            TextMessage(
                text=f"วงเงินกู้สูงสุด: {max_loan:,.0f} บาท\nยอดผ่อนต่อเดือน: {monthly_payment:,.0f} บาท"
            )
        )
    elif tool_name == "personal_tax_calculator":
       tax_flex = build_tax_flex(output_params)
       messages.append(tax_flex)

    elif tool_name == "vertex_fund_search":
        
        search_results = output_params["200"].get("search_results", None)
        print("search_results", str(search_results))
        if search_results:
            fund_flex = build_fund_flex_message(search_results)
            messages.append(fund_flex)
        
    return messages 


def handle_agent_actions(actions, session: Sessions) -> list[TextMessage]:
    """Process actions from Dialogflow CX and return LINE messages."""
    messages = []

    for action in actions:
        if "tool_use" in action:
            tool_name = action.tool_use.action
            output_params = action.tool_use.output_action_parameters
            input_params = action.tool_use.input_action_parameters

            output_dict = session.recurse_proto_marshal_to_dict(output_params)
            input_dict = session.recurse_proto_marshal_to_dict(input_params)
            print(f"tool_name: {tool_name}")
            print(f"output_dict: {str(output_dict)}")
            print(f"input_dict: {str(input_dict)}")
            messages_from_tools = parse_tool_response(tool_name, output_dict, input_dict)
            messages.extend(messages_from_tools)

        if "agent_utterance" in action:
            agent_utterance = action.agent_utterance.text
            print("agent_utterance", agent_utterance)
            messages.append(TextMessage(text=agent_utterance))

        if "playbook_invocation" in action:
            playbook_name = action.playbook_invocation.display_name
            print(playbook_name)
            playbook_state = action.playbook_invocation.playbook_state
            print(playbook_state)
    return messages


def detect_intent(user_id: str, user_text: str, line_bot_api, reply_token: str) -> None:
    """Main function to detect intent from Dialogflow CX and reply via LINE."""
    try:
        session_path = generate_session_path(user_id)
        agent_session = Sessions(creds_path=creds_path)

        response = agent_session.detect_intent(
            agent_id=f"projects/{project_id}/locations/{location_id}/agents/{agent_id}",
            session_id=session_path,
            text=user_text,
        )

        print(
            "Agent Response:", agent_session.cx_object_to_json(response.generative_info)
        )
        print("="*10)
        print(len(response.generative_info.action_tracing_info.actions))
        line_messages = handle_agent_actions(
            response.generative_info.action_tracing_info.actions, agent_session
        )

        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=line_messages)
        )

    except Exception as e:
        print(f"Error in detect_intent: {str(e)}")
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[
                    TextMessage(text="ขออภัย เกิดข้อผิดพลาดในการประมวลผล กรุณาลองใหม่อีกครั้ง")
                ],
            )
        )
