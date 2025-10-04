from utils import call_openai

class OpenAIService:
    def generate(self, prompt: str):
        return call_openai(prompt)

openai_service = OpenAIService()
