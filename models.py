from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'USER'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    
    id = db.Column(db.String(100), primary_key=True)
    college = db.Column(db.String(5))
    department = db.Column(db.String(30))
    
    def __init__(self, id, college, department):
        self.id = id
        self.college = college
        self.department = department
    
class Keywords(db.Model):
    __tablename__ = 'KEYWORDS'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    
    id = db.Column(db.String(100), primary_key=True)
    key = db.Column(db.String(10), primary_key=True)
    
    def __init__(self, id, key):
        self.id = id
        self.key = key
    