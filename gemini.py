import re
import google.generativeai as genai
import google.ai.generativelanguage as glm

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
        with open(file_path, 'r', encoding='utf-8') as f:
            self.prefix = f.read()

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

    def parse_gemini_reply(self, reply):
        source_prompt_match = re.search(r'Source prompt: \'(.*?)\'', reply)
        target_prompt_match = re.search(r'Target prompt: \'(.*?)\'', reply)
        source_prompt = source_prompt_match.group(1) if source_prompt_match else ""
        target_prompt = target_prompt_match.group(1) if target_prompt_match else ""
        return source_prompt, target_prompt

    def call_gemini(self, instructions):
        reply = self.generate(instructions)
        print(reply)
        source_prompt, target_prompt = self.parse_gemini_reply(reply)
        print(f'Source: {source_prompt}, Target: {target_prompt}')
        return source_prompt, target_prompt
