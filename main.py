from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:hotdog4@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
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
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
                        
        if len(username) == 0 or len(username) < 3:
            flash("Invalid username")

        if len(password) == 0 or len(password) < 3:
            flash("Invalid password")
        
        if len(verify) == 0 or verify != password: 
            flash("Passwords don't match")

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash("User already exists")
                
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')
                       
@app.route('/blog')
def blog():
    if request.args.get('user'):
        users = request.args.get('user')
        owner = User.query.filter_by(username=users).first()
        blogs = Blog.query.filter_by(owner=owner).all()
        users = User.query.all()
        return render_template('blog.html', blogs=blogs, users=users)
    else:
        blogs = Blog.query.all()
        users = User.query.all()
        return render_template('blog.html', blogs=blogs, users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
                
    if request.method == 'POST':

        title = request.form['title']
        body = request.form['body']
        if len(title) < 1 or len(body) < 1:
            error = "Please enter a title or body"
            return render_template('newpost.html', error=error) 

        owner = User.query.filter_by(username=session['username']).first()            
        title = request.form['title']
        body = request.form['body']
        id = request.args.get('id')
        newpost = Blog(title, body, owner)
        db.session.add(newpost)
        db.session.commit()
        id = newpost.id
        id = str(id)
                                            
        return redirect("/post?id=" + id)

       
    return render_template('newpost.html')

@app.route('/post', methods=['GET'])
def post():
    users = User.query.all()
    id = request.args.get('id')               
    submitted_blogs = Blog.query.filter_by(id=id).all()
    return render_template('post.html', submitted_blogs=submitted_blogs, users=users)

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


if __name__ == '__main__':
    app.run()