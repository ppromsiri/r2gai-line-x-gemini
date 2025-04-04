import os
import pytz
from datetime import datetime
from dfcx_scrapi.core.sessions import Sessions
from proto.marshal.collections import maps
from dotenv import load_dotenv

load_dotenv()
creds_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
project_id = os.environ["CONVERSATIONAL_AGENT_PROJECT_ID"]
location_id = os.environ["CONVERSATIONAL_AGENT_LOCATION"]
agent_id = os.environ["CONVERSATIONAL_AGENT_ID"]

def detect_intent(user_id: str, user_text: str, line_bot_api, reply_token: str) -> None:
    """ฟังก์ชันหลักสำหรับตรวจจับ intent และส่งข้อความตอบกลับ"""

    
    try:
        # สร้าง session path
        bkk_tz = pytz.timezone('Asia/Bangkok')
        current_time = datetime.now(bkk_tz).strftime('%m%d%H')
        user_id = user_id[:20]
        session_id=f"line-{user_id}-{current_time}".lower()
        agent_path = f"projects/{project_id}/locations/{location_id}/agents/{agent_id}"
        session_path = f"{agent_path}/sessions/{session_id}"

        agent_session = Sessions(creds_path=creds_path)
        res = agent_session.detect_intent(agent_id=agent_path, session_id=session_path, text=user_text)
        print("Agent Response: ", agent_session.cx_object_to_json(res.generative_info))
        
        line_resp_msgs = []
        for action in res.generative_info.action_tracing_info.actions:
            if "tool_use" in action:
                tool_name = action.tool_use.action
                print(tool_name)
                tools_output = action.tool_use.output_action_parameters

                if isinstance(tools_output, maps.MapComposite):
                    processed_output_params = (
                        agent_session.recurse_proto_marshal_to_dict(tools_output)
                    )
                    output_keys = list(processed_output_params.keys())
                    first_key = output_keys[0] if output_keys else None

                    output_tool_dict = processed_output_params.get(first_key, {})

                    if tool_name == "personal_tax_calculator":
                        pass
                        
                    elif tool_name == "fund_search":
                        pass
                    elif tool_name == "loan_calculator":
                        max_loan = output_tool_dict.get("max_loan", 0)
                        monthly_payment = output_tool_dict.get("monthly_payment", 0)

                        line_resp_msgs.append(TextMessage(text=f"วงเงินกู้สูงสุด: {max_loan:,.0f} บาท\nยอดผ่อนต่อเดือน: {monthly_payment:,.0f} บาท"))
                        
                
            if "agent_utterance" in action:
                    agent_utterance = action.agent_utterance.text
                    print("agent_utterance" ,agent_utterance)
                    line_resp_msgs.append(TextMessage(text=agent_utterance))
                # ส่งข้อความตอบกลับ
        
        
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=line_resp_msgs
            )
        )
    except Exception as e:
        print(f"Error in detect_intent_text: {str(e)}")
        # ส่งข้อความแจ้งเตือนเมื่อเกิดข้อผิดพลาด
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="ขออภัย เกิดข้อผิดพลาดในการประมวลผล กรุณาลองใหม่อีกครั้ง")]
            )
        )

