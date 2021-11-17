from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'USER'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    
    id = db.Column(db.Integer, primary_key=True)
    college = db.Column(db.String(5))
    department = db.Column(db.String(30))
    
    def __init__(self, id, college, department):
        self.id = id
        self.college = college
        self.department = department
    
    def __repr__(self):
        return "User('{self.id}', '{self.college}', '{self.department}')"
    
    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}
    