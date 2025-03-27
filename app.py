import os
import openai
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import base64

# Load API key from .env or set directly
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def base64_image(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def call_gpt_vision(prompt, image_path=None):
    if image_path:
        with open(image_path, "rb") as image_file:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "넌 장난스럽고 친절한 AI 선생님이야. 학생이 이해할 수 있게 설명해줘."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image(image_path)}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "넌 장난스럽고 친절한 AI 선생님이야. 학생이 이해할 수 있게 설명해줘."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
    return response.choices[0].message.content

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt = request.form['prompt']
        image = request.files.get('image')
        image_path = None

        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

        response = call_gpt_vision(prompt, image_path)
        return render_template('index.html', prompt=prompt, response=response)

    return render_template('index.html', prompt=None, response=None)

if __name__ == '__main__':
    app.run(debug=True)
