from flask import Flask, request, redirect, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy 
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:hotdog@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "ads;lkfja"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db. Integer, db.ForeignKey('user.id'))

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
def require_signin():
    allowed = ['signup', 'login', 'blogs', 'index']

    if request.endpoint not in allowed and 'user' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    user_id = request.args.get('id')
    if user_id:
        writer = User.query.filter_by(id=user_id).first()
        posts = Blog.query.filter_by(owner=writer).all()
        return render_template('singleUser.html', posts = posts)

    users = User.query.all()
    
    return render_template('Users.html',users=users)

@app.route('/blogs', methods = ['POST', 'GET'])
def blogs():
    blog_id = request.args.get('id')
    if blog_id:
        blog_id_int = int(blog_id)
        posts = Blog.query.filter_by(id=blog_id_int).first()
        
        return render_template('blog-ID.html', title="Blog Post", posts=posts)

    blogs=Blog.query.all()
    return render_template('blogs.html', blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost(): 
    if request.method == 'POST':   
        title = request.form['title']
        body = request.form['body']
        user = User.query.filter_by(username=session['user']).first()
        # if not user:
        #     flash('Addblog - User not found.')
        #     return redirect('/')

        new_blog = Blog(title, body, user)
        db.session.add(new_blog)
        db.session.commit() 
        
        
        if (title) or (body) == "":
            flash('You have successully posted a blog entry')
            url= "/blogs?id=" + str(new_blog.id)
            return redirect(url)
        else:
            flash('Fields cannot be left empty.')


    else:
        
        return render_template('newpost.html') 

         
 
@app.route('/signup', methods=['POST', 'GET']) 
def signup():

    username_error = ''
    password_error = ''
    verify_password_error = ''
    
   

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']
        
    
    
        if (len(username) < 3 or len(username) > 20) or (" " in username):
            
            username_error = 'Invalid entry.  This field must contain between 3-20 alpha-numeric characters with no spaces.'
            username = ''

        if (len(password) < 3 or len(password) > 20) or (" " in password):
            password_error = 'Invalid entry.  This field must contain between 3-20 alpha-numeric characters with no spaces.'
            password = ''

        if verify_password != password:
            verify_password_error = 'Your passwords do not match.'
            verify_password = ''
    
    
        if not username_error and not password_error and not verify_password_error:
            #user = username

            new_user=User(username, password)
            db.session.add(new_user)
            db.session.commit()
            flash('New user added')
            return redirect('/login')   

#        return render_template('user-signup.html', username_error=username_error,
#            password_error=password_error, verify_password_error=verify_password_error,
#            email_error=email_error, username=username, password=password, verify_password=verify_password, email=email, )        
            


    return render_template('user-signup.html', username_error=username_error,
        password_error=password_error, verify_password_error=verify_password_error, username='', password='', verify_password='')        

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user:
            if user.password == password:
                session['user'] = user.username
                flash('You have sucessfully logged In')
                return redirect('/newpost')
            else:
                flash('Bad Password')
        else:
            flash('user not found')

    return render_template('login.html')

@app.route('/Sign_Out')
def logout():
    session.clear()
    flash('You have successfully logged out')
    return redirect('/')    

if __name__ == '__main__':
    app.run()