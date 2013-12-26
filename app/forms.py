from flask.ext.wtf import Form
from wtforms.fields.html5 import TelField, EmailField
from wtforms import TextField, BooleanField, PasswordField, TextAreaField, RadioField, FileField, SelectField, SelectMultipleField
from wtforms.validators import Required, Email
from werkzeug import secure_filename
import models
from app import app
from app.models import User

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def ShouldBeEmpty(form, field):
	if field.data:
		return False
	return True

class LoginForm(Form):
    user_name = TextField('user_name', validators = [Required('Please enter a username')])
    password = PasswordField('password', validators =[Required('Please enter a password')])
    hidden = TextField('hidden',validators=[ShouldBeEmpty])
    remember_me = BooleanField('remember_me', default = False)

    def __init__(self, *args, **kwargs):
    	Form.__init__(self, *args, **kwargs)

    def validate(self):
	    if not Form.validate(self):
	      return False	     	      
	    user = User.query.filter_by(nickname = self.user_name.data.lower()).first()	    
	    if user and user.check_password(self.password.data):
	      return True
	    else:
	      self.user_name.errors.append("Invalid e-mail or password")
	      return False

class ContactForm(Form):
	name = TextField('name', validators=[Required('Please enter your name.')])
	company = TextField('company')
	phone_number = TelField('phone')
	email = EmailField('email', validators=[Required('Please enter a valid email address.'), Email('Please enter a valid email address.')])
	preference = RadioField('preference', choices=[('phone', 'Phone'), ('email', 'Email')])
	body = TextAreaField('body', validators=[Required('Please leave us a message.')])
	hidden = TextField('hidden',validators=[ShouldBeEmpty])

