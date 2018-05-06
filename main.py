from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12676712@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'secretkey'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1200))
    content = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, name, content, owner):
        self.name = name
        self.content = content
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['index', 'blog', 'login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect ('/login')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/')
        elif not user:
            flash('You must register to login', 'error')

        elif user and user.password != password:
            flash('You must provide a valid password', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username_error = ''
    password_error = ''
    verify_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            username_error = "Duplicate User"

        if len(username) < 1:
            username_error = "You must add a user name"

        elif len(username) < 3:
            username_error = "Do not use less than 3 characters in your name"

        elif len(username) > 20:
            username_error = "Do not use more than 20 characters"

        if len(password) < 1:
            password_error = "You must add a password"

        elif len(password) < 3:
            password_error = "Password must be greater than 3 characters"
    
        elif len(password) > 20:
            password_error = "Password cannot be greater than 20 characters"

        if len(verify) < 1:
            verify_error = "You must verify your password"

        elif verify != password:
            verify_error = "Verify password must match password"

        if not existing_user and not username_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')


    return render_template('signup.html', username_error = username_error, password_error = password_error, verify_error = verify_error,)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')



@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    blogs = Blog.query.all()
    #owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_name = request.form['blog']
        content_name = request.form['content']

    return render_template('index.html', users=users)


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()
    #owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_name = request.form['blog']
        content_name = request.form['content']

    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title_error = ''
    content_error = ''
    #owner section?
    owner = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        blog_name = request.form['blog']
        content_name = request.form['content']
        
        if len(blog_name) < 1:
            title_error = "You must add a blog title"
            content_error = "You must add blog content"

        if len(content_name) < 1:
            title_error = "You must add a blog title"
            content_error = "You must add blog content"

        if not title_error and not content_error:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_name, content_name, owner)
            db.session.add(new_blog)
            db.session.commit()
            completed_blog = Blog.query.filter_by(name=blog_name,owner=owner).first()
            return redirect('/viewpost/?id=' + str(completed_blog.id))

    
    blogs = Blog.query.all()

    return render_template('newpost.html', blogs=blogs, title_error=title_error, content_error=content_error)


@app.route('/singleUser/', methods=['POST', 'GET'])
def singleUser():

    owner_id = request.args.get('id')
    blogs = Blog.query.filter_by(owner_id=owner_id).all()
    return render_template('singleUser.html', blogs=blogs)


@app.route('/viewpost/', methods=['POST', 'GET'])
def viewpost():

    blog_id = request.args.get('id')
    blog_text = Blog.query.filter_by(id=blog_id).first()

    blog_title = blog_text.name
    blog_body = blog_text.content

    blogs = Blog.query.all()

    return render_template('viewpost.html', blogs=blogs, blog_title=blog_title, blog_body=blog_body, blog=blog_text)



if __name__ == '__main__':
    app.run()