from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import update
from models import User

app = Flask(__name__)
Base = declarative_base()
engine = create_engine('postgresql://jrbysnbvqyvmie:4a2d878446a2864c6c7b9b16b965f58756035fea520bf6f682db34769ff6d053@ec2-44-198-236-169.compute-1.amazonaws.com:5432/db0sh1er7k2vqh')
Session = sessionmaker()
Session.configure(bind=engine)
#session.close()

@app.route('/')              
def index():  
    session = Session()    
    msg = str(session.query(User.id, User.college, User.department).all())    
    session.close()
    return msg

@app.route('/department', methods=['POST'])
def department():
    req = request.get_json()
    session = Session()

    id = req["userRequest"]["user"]["id"]
    college = req["action"]["detailParams"]["college"]["value"]   #json파일 읽기
    department = req["action"]["detailParams"]["department"]["value"]

    answer =  str(id) + "\n" + college + "대학\n" + department
    user = session.query(User.id).filter_by(id=id).all();
    if(user == []):
        session.add(User(id=id, college=college, department=department))
        session.commit()
    else:
        conn = engine.connect()
        stmt = update(User).where(User.id == id).values(college=college, department=department)
        conn.execute(stmt)
        conn.close()
    session.close()
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

#if __name__ == '__main__':  
#   app.run('0.0.0.0', port=5000, debug=True)