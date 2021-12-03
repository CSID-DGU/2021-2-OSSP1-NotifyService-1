from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'USER'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = db.Column(db.String(100), primary_key=True)
    college = db.Column(db.String(5))
    department = db.Column(db.String(30))
    phone = db.Column(db.String(15))

    def __init__(self, id, college, department, phone):
        self.id = id
        self.college = college
        self.department = department
        self.phone = phone


class Keywords(db.Model):
    __tablename__ = 'KEYWORDS'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = db.Column(db.String(100), primary_key=True)
    key = db.Column(db.String(10), primary_key=True)
    notified_time = db.Column(db.String(30))

    def __init__(self, id, key, notified_time):
        self.id = id
        self.key = key
        self.notified_time = notified_time


class Crawl(db.Model):
    __tablename__ = 'CRAWL'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    category = db.Column(db.String(30))
    title = db.Column(db.String(200))
    link = db.Column(db.String(250), primary_key=True)
    crawl_time = db.Column(db.String(30))

    def __init__(self, category, title, link, crawl_time):
        self.category = category
        self.title = title
        self.link = link
        self.crawl_time = crawl_time
