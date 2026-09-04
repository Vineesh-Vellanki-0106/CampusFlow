import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key=os.environ["FEATHERLESS_API_KEY"],
)

models = client.models.list()

keywords = ["qwen3", "kimi", "tool", "function", "agent"]

for model in models.data:
    model_id = model.id.lower()

    if any(keyword in model_id for keyword in keywords):
        print(model.id)