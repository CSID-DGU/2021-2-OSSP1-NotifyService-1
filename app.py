from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')              
def index():                 
    return "Hello world!"   

@app.route('/department', methods=['POST'])
def department():
    req = request.get_json()

    college = req["action"]["detailParams"]["college"]["value"]   #json파일 읽기
    department = req["action"]["detailParams"]["department"]["value"]

    answer = college + "대학\n" + department

    #답변 설정
    res = {
        "version": "2.0",
        "template": {
            "outputs" : [
                {
                    "simpleText": {
                        "text": answer
                    }
                }
            ]
        }
    }
    return jsonify(res)