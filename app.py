from flask import Flask

app = Flask(__name__)

@app.route('/')              # <-- 추가된 3줄
def index():                 # <
    return "Hello world!"    # <