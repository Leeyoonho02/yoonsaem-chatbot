import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

# List available models 
models = openai.Model.list()
for m in models.data:
    print(m.id)