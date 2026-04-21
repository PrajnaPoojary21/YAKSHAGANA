from dotenv import load_dotenv
import os
from openai import OpenAI

# 👇 THIS LINE IS MISSING
load_dotenv()

# Optional debug (remove later)
print("API KEY:", os.getenv("OPENAI_API_KEY"))

client = OpenAI()

res = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say OK if working"}]
)

print(res.choices[0].message.content)