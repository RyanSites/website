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

class ClientForm(Form):
	client_name = TextField('client_name', validators=[Required()])
	body = TextAreaField('body', validators=[Required()])
	client_url = TextField('client_url')
	slug = TextField('slug', validators=[Required()])

class TestimonialForm(Form):
	body = TextAreaField('body', validators=[Required()])
	poc = TextField('poc', validators=[Required()])
	poc_title = TextField('poc_title')
	poc_company = TextField('poc_company', validators=[Required()])
	clients = []
	for client in models.Client.query.all():
		clients.append( (client.id, client.title))
	client = SelectField('client', choices=clients, coerce=int)

class ServiceForm(Form):
	body = TextAreaField('body', validators=[Required()])
	service_name = TextField('service_name', validators=[Required()])
	service_types = [(0, 'website'), (1, 'corporate'), (2, 'print'), (3, 'other')]
	service_type = SelectField('service_type', choices=service_types, coerce=int)
	clients = []
	for client in models.Client.query.all():
		clients.append( (client.id, client.title))
	client = SelectField('client', choices=clients, coerce=int)

class PostForm(Form):
	body = TextAreaField('body', validators=[Required()])
	title = TextField('title', validators=[Required()])				
	slug = TextField('slug', validators=[Required()])				
	categories = [(0, 'None')]+[(category.id, category.title) for category in models.Category.query.all()]
	tags = [(0, 'None')]+[(tag.id, tag.title) for tag in models.Tag.query.all()]	
	category = SelectMultipleField('category', choices=categories, coerce=int)
	tag = SelectMultipleField('tag', choices=tags, coerce=int)
	img = FileField(validators=[Required()])