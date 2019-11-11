from flask import render_template,flash,url_for,session,redirect,request,g 
from app import app, db,lm
from flask_login import login_user, logout_user, current_user, login_required
from app.models import Post,User
from app.forms import LoginForm,EditForm,PostForm,SignUpForm,ChangeForm
from datetime import datetime

@lm.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated:
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()	

@app.route('/',methods=['GET'])
@app.route('/index', methods = ['GET'])
@app.route('/index/<int:page>', methods = ['GET'])
@login_required
def index(page = 1):
	posts=Post.query.filter_by(user_id = current_user.id).order_by(db.desc(Post.time)).paginate(page,3, False)
	return render_template('index.html',title='Home',posts = posts)

@app.route('/<index>/detail')
@login_required
def detail(index):
	post = Post.query.filter_by(id=index).first()
	return render_template('detail.html',title='Detail',post = post)

@app.route('/write',methods=['GET','POST'])
@login_required
def write():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data,content = form.content.data,user_id = current_user.id)
		db.session.add(post)
		db.session.commit()
		flash('Your post is now live!')
		return redirect(url_for('index'))
	return render_template('write.html',title='Write',form=form)

#在app的根目录下定义一个login目录，允许接受的http请求为GET POST
@app.route('/login',methods=['GET','POST'])
def login():
	#LoginForm为登入表单
	form = LoginForm()
	#判断用户在LoginForm中提交的信息是否符合validators[]列表中对应函数（如DataRequired(),EualTo()）的规定。
	if form.validate_on_submit():
		#将User中的username和password作为对象的参数传递给user
		user = User.login_check(request.form.get('username'),request.form.get('password'))
		#判断刚刚传递过来的对象是否为空
		if user:
			#执行登入操作
			login_user(user)
			#将当前时刻赋值给user对象的数据成员last_seen
			user.last_seen = datetime.now()
			#尝试添加user并提交到数据库
			try:
				db.session.add(user)
				db.session.commit()
			#失败则抛出“The Database error!”并在返回函数redirrect()
			except:
				flash("The Database error!")
				return redirect('/login')
			#将相应参数加入通过flash加入到message处理队列中，后期通过get_flashed_message()来在前端网页显示
			flash('Your name: ' + request.form.get('username'))
			flash('remember me? ' + str(request.form.get('remember_me')))
			return redirect(url_for("index"))
		else:
			flash('Login failed, username or password error!')
			return redirect('/login')
	#返回一个html文件，即在执行这个函数后，在前端上显示返回的html文件。
	return render_template('login.html',form=form)

@app.route('/sign-up',methods=['GET','POST'])
def sign_up():
	form = SignUpForm()
	user = User()
	if form.validate_on_submit():
		user_name = request.form.get('username')
		user_password = request.form.get('password')
		register_check = User.query.filter(db.and_(User.username == user_name, User.password == user_password)).first()
		if register_check:
			return redirect('/sign-up')
		if len(user_name) and len(user_password):
			user.username = user_name
			user.password = user_password
		try:
			db.session.add(user)
			db.session.commit()
		except:
			return redirect('/sign-up')
		return redirect('/index')
	return render_template("sign_up.html",form=form)
		

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/user/<username>')
@login_required
def user(username,page = 1):
	user = User.query.filter_by(username = username).first()
	posts=Post.query.filter_by(user_id = user.id).order_by(db.desc(Post.time)).paginate(page,3, False)
	return render_template('user.html',user = user,posts = posts)

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user.username)
	if form.validate_on_submit():
		g.user.username = form.username.data
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit'))
	form.username.data = g.user.username
	form.about_me.data = g.user.about_me
	return render_template('edit.html',form = form)

@app.route('/delete/<post_id>',methods = ['POST'])
@login_required
def delete(post_id):
	post = Post.query.filter_by(id = post_id).first()
	db.session.delete(post)
	db.session.commit()
	flash("delete post successful!")
	return redirect(url_for('user',username=g.user.username))


@app.route('/edit/<post_id>',methods = ['GET'])
@login_required

def editpost(post_id):
	form = ChangeForm()
	post = Post.query.filter_by(id = post_id).first()
	form.title.data = post.title
	form.content.data = post.content
	return render_template('change.html',form = form,post_id=post.id)

@app.route('/change/<post_id>',methods = ['POST'])
@login_required
def change(post_id):
	form = ChangeForm()
	post = Post.query.filter_by(id = post_id).first()
	if form.validate_on_submit():
		post.title = form.title.data
		print(post.title,post.content)
		post.content = form.content.data
		db.session.add(post)
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('user',username=g.user.username))
