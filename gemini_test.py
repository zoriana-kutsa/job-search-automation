from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

response = client.models.generate_content(
    model="gemini-flash-lite-latest",
    contents="Say hello in Polish in one short sentence.",
)
print(response.text)