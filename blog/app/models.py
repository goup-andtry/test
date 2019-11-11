from app import db
from datetime import datetime
ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), unique = True)
	password = db.Column(db.String(64))
	role = db.Column(db.SmallInteger, default = ROLE_USER)
	posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)

	def is_authenticated(self):
		return True
	def is_active(self):
		return True
	def is_anonymous(self):
		return False
	def get_id(self):
		return self.id
	def __repr__(self):
		return '<User %r>' % (self.username)

	@classmethod
	def login_check(cls,username,password):
		user = cls.query.filter(db.and_(User.username == username, User.password == password)).first()
		if not user:
			return None
		return user

#定义Post()表单类，继承了db.Model。用于存放永固提交的信息
class Post(db.Model):
	# 为表定义了一个叫id的列，是整数类型且为主键
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(100))
	content = db.Column(db.String(140))
	# 定义了一个叫time的列，即获取当前时间，并转化为标准时间后赋值给time
	time = db.Column(db.DateTime,default=datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S'))
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

	# 为了方便的看到对象输出的内容__repr__, 如果是普通类__str__
	def __repr__(self):
		return '<Post %r>' % (self.body)
