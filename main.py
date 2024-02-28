from datetime import date
from typing import List
import sqlalchemy.exc
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
import forms
# Import your forms from the forms.py
from forms import CreatePostForm

def admin_only(function):
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        else:
            return function(*args, **kwargs)
    return wrapper_function

def Blog_Writer(function):
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if current_user.permission_status != "Blog-Writer":
            return abort(403)
        else:
            return function(*args, **kwargs)

    return wrapper_function




'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
password = os.environ.get('password')
my_email = os.environ.get('my_email')
ckeditor = CKEditor(app)
Bootstrap5(app)

# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    #Use when database already has at least one user
    # return db.get_or_404(User, user_id)
    #If refactoring database (For example new feature) Use this line and comment out first line until one account is made
    return User.query.get(int(user_id))

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", 'sqlite:///posts.db')
db = SQLAlchemy(model_class=Base)
db.init_app(app)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    comments = relationship('Comment', back_populates='comment_author')
    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    reset_password_token: Mapped[str] = mapped_column(Text, nullable=True)
    permission_status: Mapped[str] = mapped_column(Text, nullable=False)


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")

    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    comments = relationship('Comment', back_populates='parent_post')
    #

class Comment(db.Model):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship('User', back_populates='comments')
    parent_post = relationship('BlogPost', back_populates='comments')
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('blog_posts.id'))
    #Change to string if error occurs

class Suggested_Edits(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    edit_type: Mapped[str] = mapped_column(String(250), nullable=False)
    edit_text: Mapped[str] = mapped_column(Text, nullable=False)
    other_info: Mapped[str] = mapped_column(String(250), nullable=True)


class Reset_Password(db.Model):
    __tablename__ = 'reset_password'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    reset_token: Mapped[str] = mapped_column(String, nullable=True)
    last_reset: Mapped[str] = mapped_column(String, nullable=False)
# TODO: Create a User table for all your registered users.

with app.app_context():
    db.create_all()


# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=["GET", "POST"])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
            permission_status = "Community_Member"
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        import smtplib
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email, to_addrs=form.email.data, msg="Subject: Welcome to my Blog Website!\n\nThank you for signing up for my blog website. I am glad that you were able to sign up for my website. I hope that you enjoy your time on my website. Here is a quick overview of the website. There is a comment section below each post which allows you to type a response to the article. In addition, if you have any feedback you would like to provide please visit the suggest feedback page! Some people who I select will be able to make new blog posts. You will know if you have received this option because there were be a new post button. If you see this feel free to make new posts! I will need to approve each person I want to have the ability to post individually. I am currently working on new features for the website, however I am also learning how to make mobile apps. Due to this, I may start making less updates because I am trying to learn app development. I hope you enjoy my website! If you have any feedback you would like to share, please added a suggested edit to my website. Do not respond to this email. I hope you enjoy visiting my website! In addition to this, you can also look at the about page if you would like to learn more information about me.")
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form, current_user=current_user)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login', methods=['GET', "POST"])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user == None:
            flash('Email Not Found')
        else:
            password = request.form.get('password')
            if check_password_hash(pwhash=user.password, password=password) == True:
                login_user(user)
            else:
                flash("Password Incorrect, please try again.")
                redirect(url_for('login'))
        return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = forms.CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            text = form.comment.data
            comment = Comment(text=text, comment_author=current_user, parent_post=requested_post)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('You need to login in or sign up to continue')
            return redirect(url_for('login'))
    return render_template("post.html", post=requested_post, form=form)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
@Blog_Writer
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@admin_only
@Blog_Writer
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@admin_only
@Blog_Writer
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    if post_id == 1:
        post_to_delete = db.get_or_404(BlogPost, 1)
    else:
        post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/remove-comment/<int:comment_id>/<post_id>")
def remove_comment(comment_id, post_id):
    comment_to_delete = db.get_or_404(Comment, comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect(url_for('show_post', post_id=post_id))

@app.route("/suggest-edit", methods=["GET", "POST"])
def suggest_an_edit():
    form = forms.Suggest_Edit()
    if form.validate_on_submit():
        edit_type = form.edit_type.data
        edit_text = form.edit_text.data
        other_info = form.other_information.data
        New_Edit = Suggested_Edits(edit_type=edit_type, edit_text=edit_text, other_info=other_info)
        db.session.add(New_Edit)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template('suggest_edit.html', form=form)

@admin_only
@app.route('/view_suggested_edits')
def view_edits():
    result = db.session.execute(db.select(Suggested_Edits))
    edits = result.scalars().all()
    return render_template('see_all_edits.html', edits=edits)

@admin_only
@app.route("/remove_suggestion/<suggestion_id>", methods=["GET", "POST"])
def remove_suggestion(suggestion_id):
    suggestion_to_remove = db.get_or_404(Suggested_Edits, suggestion_id)
    db.session.delete(suggestion_to_remove)
    db.session.commit()
    return redirect(url_for('view_edits'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/reset_password", methods=['GET', "POST"])
def reset_pass():
    form = forms.Change_Password()
    if form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            import random
            letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                       't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                       'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            symbols = ['!', '$', '&', '+']
            nr_letters = 17
            nr_symbols = 5
            nr_numbers = 7
            password_list = []
            letters_pass = [random.choice(letters) for char in range(1, nr_letters + 1)]
            symbols_pass = [random.choice(symbols) for char in range(1, nr_symbols + 1)]
            numbers_pass = [random.choice(numbers) for char in range(1, nr_numbers + 1)]
            password_list = letters_pass + symbols_pass + numbers_pass
            random.shuffle(password_list)
            token_reset = ""
            for char in password_list:
                token_reset += char

            result = db.session.execute(db.select(Reset_Password).where(Reset_Password.email == form.email.data))
            user = result.scalar()
            if user:
                # if user.last_reset == date.today().strftime("%B %d, %Y"):
                #     flash("You've reset your password already today! Please submit another request tomorrow.")
                #     return redirect(url_for('reset_pass'))
                result = db.session.execute(db.select(Reset_Password).where(Reset_Password.email == form.email.data)).scalar()
                result.reset_token = token_reset
                user.last_reset = date.today().strftime("%B %d, %Y")
            else:
                new_user_pass = Reset_Password(email=form.email.data, reset_token=token_reset, last_reset=date.today().strftime("%B %d, %Y"))
                db.session.add(new_user_pass)
            db.session.commit()
            print("Test")
            result = db.session.execute(db.select(Reset_Password).where(Reset_Password.email == form.email.data))
            user = result.scalar()
            print(user)
            user_user = db.session.execute(db.select(User).where(User.email == Reset_Password.email)).scalar()
            if user_user == None:
                flash("You do not have a valid account with that email. Create an account or enter a correct email instead")
                return redirect(url_for('register'))
            else:
                user_user.reset_password_token = token_reset
                db.session.commit()
                print(user_user.reset_password_token)
            import smtplib
            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(user=my_email, password=password)
                connection.sendmail(from_addr=my_email, to_addrs=form.email.data,
                                    msg=f"Subject: Reset Password Key\n\nThis message has been automatically sent by the reset password request using your account. If you did not request a password reset, you may reset your password as someone likely knows your password. Here is your token: {user.reset_token}. If you add this in the website address /confirm_reset/{user.reset_token} it will reset your password by filling out the form specified. Thanks, hope this helps!")
            return redirect(url_for('get_all_posts'))

    return render_template('reset_pass_step_1.html', form=form)

@app.route("/confirm_reset/<token>", methods=['GET', "POST"])
def confirm_reset(token):
    # Check if it has been more than one hour
    print(token)
    user = db.session.execute(db.select(User).where(User.reset_password_token == token)).scalar()
    if user == None:
        flash('Invalid Token')
    else:
        form = forms.Change_Password_Step_2()
        if form.validate_on_submit():
            print(user.password)
            print(form.new_password.data)
            hash_and_salted_password = generate_password_hash(
                form.new_password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )
            user.password = hash_and_salted_password
            user.reset_password_token = ""
            db.session.commit()
            print(user.password)
            return redirect(url_for('login'))


        return render_template('Reset_Password_Step2.html', form=form)
    return redirect(url_for('get_all_posts'))

@app.route("/delete_account")
def delete_account():
    if current_user.is_authenticated:
        user = db.session.execute(db.select(User).where(User.email == current_user.email)).scalar()
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('get_all_posts'))
@app.route("/edit_user_permissions")
@admin_only
def edit_user_permissions():
    all_users = User.query.all()
    return render_template('change_users_status.html', all_users=all_users)
@admin_only
@app.route("/become_blog_writer/<id>")
def become_blog_writer(id):
    user = db.session.execute(db.select(User).where(User.id == id)).scalar()
    user.permission_status = "Blog-Writer"
    db.session.commit()
    return redirect(url_for('edit_user_permissions'))

@admin_only
@app.route("/become_community_member/<id>")
def become_community_member(id):
    user = db.session.execute(db.select(User).where(User.id == id)).scalar()
    user.permission_status = "Community_Member"
    db.session.commit()
    return redirect(url_for('edit_user_permissions'))

#Send email thanking people for joining!

if __name__ == "__main__":
    app.run(debug=True, port=5002)
