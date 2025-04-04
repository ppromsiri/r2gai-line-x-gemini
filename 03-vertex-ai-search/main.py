import os
import functions_framework
from dotenv import load_dotenv
import base64

from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3 import WebhookHandler
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    StickerMessageContent,
    LocationMessageContent,
    ImageMessageContent,
    VideoMessageContent,
    AudioMessageContent,
    FileMessageContent,
)

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
    ShowLoadingAnimationRequest,
    FlexContainer,
    FlexMessage,
    FlexCarousel,
)

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]


configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
line_bot_blob_api = MessagingApiBlob(api_client)

from vertext_ai_search import search_ai


@functions_framework.http
def callback(request):
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    line_bot_api.show_loading_animation(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )
    gemini_summary_text, search_results = search_ai(event.message.text)
    funds_flex_message = make_flex_message(search_results)

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=gemini_summary_text), funds_flex_message],
        )
    )


def make_flex_message(search_results):
    result_products_list = []
    for idx, result in enumerate(search_results):
        fund_data = result["document"]["structData"]
        return1D_color = "#FF5555" if fund_data["return1D"] < 0 else "#00AA00"
        returnYTD_color = "#FF5555" if fund_data["returnYTD"] < 0 else "#00AA00"

        flex_bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": fund_data["fundCode"],
                        "weight": "bold",
                        "size": "lg",
                        "wrap": True,
                    },
                    {
                        "type": "text",
                        "text": fund_data["fundNameThai"],
                        "size": "sm",
                        "color": "#666666",
                        "wrap": True,
                    },
                    {"type": "separator", "margin": "md"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "NAV",
                                        "size": "sm",
                                        "color": "#555555",
                                        "flex": 2,
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{fund_data['NAV']} บาท",
                                        "size": "sm",
                                        "color": "#111111",
                                        "align": "end",
                                        "flex": 3,
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "เปลี่ยนแปลง (1D)",
                                        "size": "sm",
                                        "color": "#555555",
                                        "flex": 2,
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{fund_data['return1D']}%",
                                        "size": "sm",
                                        "color": return1D_color,
                                        "align": "end",
                                        "flex": 3,
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "ผลตอบแทน YTD",
                                        "size": "sm",
                                        "color": "#555555",
                                        "flex": 2,
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{fund_data['returnYTD']}%",
                                        "size": "sm",
                                        "color": returnYTD_color,
                                        "align": "end",
                                        "flex": 3,
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Risk Level",
                                        "size": "sm",
                                        "color": "#555555",
                                        "flex": 2,
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{fund_data['riskSpectrum']} ({'สูง' if fund_data['riskSpectrum'] >= 7 else 'ปานกลาง' if fund_data['riskSpectrum'] >= 4 else 'ต่ำ'})",
                                        "size": "sm",
                                        "color": "#111111",
                                        "align": "end",
                                        "flex": 3,
                                    },
                                ],
                            },
                        ],
                    },
                    {"type": "separator", "margin": "md"},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"ข้อมูล ณ วันที่ {str(fund_data['NAVDate'])[:4]}-{str(fund_data['NAVDate'])[4:6]}-{str(fund_data['NAVDate'])[6:]}",
                                "size": "xs",
                                "color": "#999999",
                                "flex": 1,
                                "align": "start",
                            }
                        ],
                    },
                ],
            },
        }

        result_products_list.append(FlexContainer.from_dict(flex_bubble))

    carousel_flex_message = FlexMessage(
        alt_text=f"ผลการค้นหากองทุน",
        contents=FlexCarousel(
            type="carousel",
            contents=result_products_list,
        ),
    )

    return carousel_flex_message
