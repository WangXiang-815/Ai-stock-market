import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def explain_signal_with_deepseek(signal_json: dict) -> dict:
    """
    Send model signal JSON to DeepSeek and get explanation JSON.
    """
    system_prompt = """
You are a financial decision-support assistant.
You must return output in json.
Do not invent any market data.
Do not guarantee profit.
Return strictly valid JSON with these fields:
ticker, suggestion, summary, reasoning, risk_warning, confidence_level.
"""

    user_prompt = f"""
Here is the model signal in json:
{json.dumps(signal_json, ensure_ascii=False)}

Generate a user-facing stock suggestion in strict JSON format.
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        max_tokens=500,
        stream=False
    )

    content = response.choices[0].message.content
    return json.loads(content)