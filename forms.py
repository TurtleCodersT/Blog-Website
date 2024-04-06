from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL, Email, EqualTo
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    name = StringField(label="Name/Username", validators=[DataRequired()])
    submit = SubmitField("Sign me up!")

# TODO: Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Log me In!")

# TODO: Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    comment = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField(label="Submit My Comment")

class Suggest_Edit(FlaskForm):
    edit_type = SelectField("Please select what type of edit you would like to suggest:", choices=["Error in Article", "New Feature", "Bug fix", "Other"], validators=[DataRequired()])
    edit_text = CKEditorField("Please enter more info in the box below. If the edit is a bug fix or article, please explain exactly where the error is or what article and paragraph the bug/mistake occurs", validators=[DataRequired()])
    other_information = StringField(label="Please type anything else that you want to be changed (Not Required)")
    submit = SubmitField(label="Submit my suggested edit (Suggested Edits are private and your username will not be revealed)")
class Change_Password(FlaskForm):
    email = StringField(label="Please enter your email: ", validators=[DataRequired(), Email()])
    submit = SubmitField(label="Send password reset request. Make sure you're email is correct!")

class Change_Password_Step_2(FlaskForm):
    new_password = PasswordField(label="Enter your new password! Make sure to write it down because you won't be able to reset your password again today: ", validators=[DataRequired()])
    new_password_confirm = PasswordField(label='Confirm your password here: ', validators=[DataRequired(), EqualTo('new_password', message='Passwords are not the same')])
    submit = SubmitField(label="Send password reset request. Make sure you're email is correct!")

class Signup_for_Newletter(FlaskForm):
    interest = StringField(label="What kind of news are you intrested in? Tech, Sports, etc. Enter the exact thing that you are intrested ONLY ONE here: ", validators=[DataRequired()])
    approx_location = StringField(label="Enter your location. It can be as specific or generic as you want. This will be used for telling you the weather. If you do not feel comfortable sharing your exact location you can type your city or state.")
    other_info = StringField(label="Would you like to recieve additional information from me Yes or No?")
    submit = SubmitField(label='Signup!')

