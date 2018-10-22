from flask import Flask, request,redirect, render_template,session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SECRET_KEY'] = "Your_secret_string"
SECRET_KEY = "Your_secret_string"
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(200))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self,title,content,owner):
        self.title = title
        self.body = content
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog',backref='owner')


    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username


def get_blogs():
    return Blog.query.all()

def get_blogs_for_user(userid):
    return Blog.query.filter_by(owner_id=userid).all()

def get_users():
    return User.query.all()

@app.route("/logout")
def logout():
    del session['username']
    return redirect("/blog")

@app.before_request
def require_login():

    allowed_routes = ['login', 'signup', 'all_posts', 'index']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect("/login")

@app.route("/login", methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        error_msg = ""
        username_in = request.form['username']
        password_in = request.form['password']

        if not (username_in and password_in):
            error_msg = 'Username/Password Required'
        else:
            existing_user = User.query.filter_by(username=username_in).first()

            if not existing_user:
                error_msg = 'Username does not exist'
            else:
                if password_in != existing_user.password:
                    error_msg = 'Password Invalid'

        if error_msg:
            return render_template('login.html', error_p=error_msg,username_p=username_in)
        else:
            session['username'] = username_in
            print(session)
            return redirect ("/newpost")

    return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():

    if request.method == "POST":
        username_in = request.form['username']
        password_in = request.form['password']
        verify_pswd_in = request.form['verify']

        user_name_error_msg = ""
        password_error_msg = ""
        verify_error_msg = ""

        error_flag = False

        if username_in:
            if " " in username_in:
                user_name_error_msg = "User name cannot contain spaces"
                error_flag = True
            else:
                if len(username_in) < 3 or len(username_in) > 20:
                    user_name_error_msg = "User name must be greater than 2 characters and less than 20"
        else:
            user_name_error_msg = "You must enter a user name"
            error_flag = True

        if password_in:
            if " " in password_in:
                password_error_msg = "Password cannot contain spaces"
                error_flag = True
                password_in = ""
            else:
                if len(password_in) < 3 or len(password_in) > 20:
                    password_error_msg = "Password must be greater than 2 characters and less than 20"
                    error_flag = True
                    password_in = ""
        else:
            password_error_msg = "You must enter a password"
            error_flag = True
            password_in = ""

        if verify_pswd_in:
            if verify_pswd_in != password_in:
                verify_error_msg = "Passwords do not match"
                error_flag = True
                verify_pswd_in = ""
        else:
            verify_error_msg = "You must enter the verification password"
            error_flag = True
            verify_pswd_in = ""

        if error_flag:
            return render_template('signup.html', username_p=username_in,
            username_error_p=user_name_error_msg,password_error_p=password_error_msg,
            verify_error_p=verify_error_msg)
        else:
            existing_user = User.query.filter_by(username=username_in).first()

            if existing_user:
                user_name_error_msg = "Username Already In Use"

                return render_template('signup.html', username_p=username_in,
                    username_error_p=user_name_error_msg,password_error_p=password_error_msg,
                    verify_error_p=verify_error_msg)
            else:
                new_user = User(username_in,password_in)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username_in

                return redirect ("/blog")


    return render_template('signup.html')

@app.route("/")
def index():
    return render_template('index.html',users=get_users())

@app.route("/blog")
def all_posts():

    blog_id = request.args.get("blog_id")
    blog_user = request.args.get("userid")

    if blog_user:
        return render_template('main_blog.html',blogs=get_blogs_for_user(blog_user))

    if blog_id:
         blogs = Blog.query.filter_by(id=blog_id).first()
         return render_template('main_blog.html',blogs=blogs)

    else:
        return render_template('main_blog.html',blogs=get_blogs())


@app.route("/newpost", methods=['POST', 'GET'])
def add_blog():


    error_flag = False

    if request.method == 'POST':

        blog_title = request.form['blog_title']
        blog_content = request.form['blog_content']
        title_error_msg = ""
        content_error_msg = ""

        if not blog_title:
            title_error_msg = "Please enter a title"
            error_flag = True

        if not blog_content:
            error_flag = True
            content_error_msg = "Please enter blog content"

        if error_flag == False:
            owner=User.query.filter_by(username=session['username']).first()
            print("owner is", owner)
            new_blog = Blog(blog_title,blog_content,owner)
            db.session.add(new_blog)
            db.session.commit()
        else:
            return render_template('add_blog.html',title_error_p=title_error_msg,
                content_error_p=content_error_msg,blog_title_p=blog_title,blog_content_p=blog_content)


    if request.method == 'GET':
        return render_template('add_blog.html')
    else:
        return redirect ("/blog?blog_id=" + str(new_blog.id))


if __name__ == '__main__':
    app.run()
