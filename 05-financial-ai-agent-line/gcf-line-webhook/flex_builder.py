
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



def build_fund_flex_message(search_results):
    result_products_list = []
    for idx, fund_data in enumerate(search_results):
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


def build_tax_flex(tools_data):
    template="""{
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://storage.googleapis.com/financial-ai-agent-src/fund_agent.png",
                "size": "full",
                "aspectRatio": "20:5",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "คำณวนภาษีบุคคล",
                    "weight": "bold",
                    "size": "lg"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "text",
                            "text": "รายได้รวมต่อปี",
                            "color": "#aaaaaa",
                            "size": "sm",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": "<gross_income>",
                            "wrap": true,
                            "color": "#666666",
                            "size": "sm",
                            "flex": 5
                        }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "text",
                            "text": "ค่าลดหย่อน",
                            "color": "#aaaaaa",
                            "size": "sm",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": "<tax_to_pay>",
                            "wrap": true,
                            "color": "#666666",
                            "size": "sm",
                            "flex": 5
                        }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "text",
                            "color": "#aaaaaa",
                            "size": "sm",
                            "flex": 1,
                            "text": "ภาษีที่ต้องจ่ายเพิ่ม"
                        },
                        {
                            "type": "text",
                            "text": "<total_deductions>",
                            "wrap": true,
                            "color": "#666666",
                            "size": "sm",
                            "flex": 5
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                    "type": "message",
                    "label": "Search Fund",
                    "text": "ค้นหากองทุนลดหย่อนภาษี"
                    },
                    "color": "#73282f"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "margin": "sm"
                }
                ],
                "flex": 0
            }
            }
            """
    tools_data = tools_data["200"]
    tax_to_pay = str(tools_data.get("tax_to_pay",0))
    gross_income = str(tools_data.get("gross_income",0))
    total_deductions = str(tools_data.get("total_deductions",0))
    flex_text = (
        template.replace("<tax_to_pay>", tax_to_pay),
        template.replace("<gross_income>", gross_income),
        template.replace("<total_deductions>", total_deductions),
    )
    detail_message = FlexMessage(
        alt_text="Personal Tax",
        contents=FlexContainer.from_json(flex_text),
    )
    return detail_message