import openai
from transformers import AutoModelForCausalLM, AutoTokenizer
import google.generativeai as genai
import google.ai.generativelanguage as glm

class OpenAIGenerator:
    def __init__(self, model: str, api_key: str) -> None:
        self.model = model
        self.api_key = api_key
        self.prefix = ""
    
    def load_predix(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            self.prefix = f.read()
        

    def generate(self, user_prompt: str) -> str:
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prefix},
                {"role": "user", "content": "User instruction: {}".format(user_prompt)}
            ],
            temperature=1.0
        )
        return response['choices'][0]['message']['content']


class GeminiGenerator:
    
    def __init__(self, model_name: str, api_key: str) -> None:
        self.model_name = model_name
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        self.messages = []
        self.prefix = ""
        self.error = "Unable to process your request"

    def load_prefix(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            self.prefix = file.read()

    def generate(self, user_prompt: str) -> str:
        if len(self.messages) >= 10:
            self.messages = []

        full_prompt = self.prefix + "\n" + user_prompt
        self.messages.append({'role': 'user', 'parts': [{'text': full_prompt}]})
        response = self.model.generate_content(self.messages)
        reply_text = ""
        for part in response.parts:
            reply_text += part.text 
        self.messages.append({'role': 'model', 'parts': [{'text': reply_text}]})

        return reply_text

            
