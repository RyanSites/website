from app import db
from sqlalchemy.orm import relationship, backref
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key = True)
	nickname = db.Column(db.String(64), unique = True)
	firstname = db.Column(db.String(64))
	lastname = db.Column(db.String(64))
	email = db.Column(db.String(120), unique = True)
	role = db.Column(db.SmallInteger, default = ROLE_USER)
	description = db.Column(db.String(2048))
	image = db.Column(db.String(256))
	pw_hash = db.Column(db.String(1024))

	def __init__(self, nickname, password, firstname=None, lastname=None, email=None):
		self.nickname=nickname
		self.set_password(password)
		self.firstname = firstname
		self.lastname  = lastname
		self.email = email

	def set_password(self, password):
		self.pw_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.pw_hash, password)

	def is_authenticated(self):
	    return True

	def is_active(self):
	    return True

	def is_anonymous(self):
	    return False

	def get_id(self):
	    return unicode(self.id)	

	def __repr__(self):
	    return "User(id={.id!s}, nickname={.nickname}, password={.pw_hash}, firstname={.firstname}, lastname={.lastname}, email={.email}, role={.role})".format(self, self, self, self, self, self, self)

tags = db.Table('tags', db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),    db.Column('post_id', db.Integer, db.ForeignKey('post.id')))
categories = db.Table('categories', db.Column('category_id', db.Integer, db.ForeignKey('category.id')),    db.Column('post_id', db.Integer, db.ForeignKey('post.id')))

class Post(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	title = db.Column(db.String(128))
	img = db.Column(db.String(256))
	slug = db.Column(db.String(128), unique=True)
	categories = relationship('Category', secondary=categories, backref=backref('posts', lazy='dynamic'))
	tags = relationship('Tag', secondary=tags, backref=backref('posts', lazy='dynamic'))
	comment = relationship('Comment', backref='Post', lazy='dynamic')

	def __repr__(self):
	    return "Post(id='%s', title='%s', timestamp='%s', user_id='%s', body='%s', categories='%s', tags='%s')"%(self.id, self.title, self.user_id, self.timestamp, self.body, str(self.categories), str(self.tags))

class Category(db.Model):
	id  = db.Column(db.Integer, primary_key=True)
	slug= db.Column(db.String(128))
	title = db.Column(db.String(128), unique=True)

	def __repr__(self):
		return "Category(id='%s', slug='%s', title='%s')"%(self.id, self.slug, self.title)

class Tag(db.Model):
	id  = db.Column(db.Integer, primary_key=True)
	slug= db.Column(db.String(128))
	title = db.Column(db.String(128), unique=True)	

	def __repr__(self):
		return "Tag(id='%s', slug='%s', title='%s')"%(self.id, self.slug, self.title)

class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String(128))
	body = db.Column(db.String(2048))	
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class Client(db.Model):
	__tablename__ = 'clients'
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(128), unique=True)
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())
	body = db.Column(db.String(1024))
	client_url = db.Column(db.String(128) )
	slug = db.Column(db.String(128))

	def __repr__(self):
		return "Client(id='%s', title='%s', timestamp='%s', body='%s')"%(self.id, self.title, self.timestamp, self.body)

class Service(db.Model):
	__tablename__ = 'services'
	id = db.Column(db.Integer, primary_key = True)
	client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
	title = db.Column(db.String(128), unique=True)
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())
	body = db.Column(db.String(1024))
	service_type = db.Column(db.Integer)
	images = relationship("Service_image", backref="Service", lazy='dynamic')

	def __repr__(self):
		return "Service(id='%s', title='%s', client_id='%s', type='%s', timestamp='%s', body='%s')"%(self.id, self.title, self.client_id, self.service_type, self.timestamp, self.body)

class Service_image(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	uri = db.Column(db.String(128))
	service_id = db.Column(db.Integer, db.ForeignKey('services.id'))

	def __repr__(self):
		return "Service_image(id='%s', service_id='%s', uri='%s')"%(self.id, self.service_id, self.uri)

class Testimonial(db.Model):
	__tablename__ = 'testimonials'
	id = db.Column(db.Integer, primary_key = True)
	client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
	body = db.Column(db.String(2048))
	poc = db.Column(db.String(50))
	poc_title = db.Column(db.String(50))
	poc_company = db.Column(db.String(100))
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())

	def __repr__(self):
		return "Testimonial(id='%s', client_id='%s', poc='%s', poc_title='%s', poc_company='%s', timestamp='%s', body='%s')"%(self.id, self.client_id, self.poc, self.poc_title, self.poc_company, self.timestamp, self.body)

class ContactFormResponse(db.Model):
	__tablename__ = 'contactformresponse'
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(128))
	body = db.Column(db.String(2048))
	phone_number = db.Column(db.String(15))
	company = db.Column(db.String(128))
	email = db.Column(db.String(40))
	preference = db.Column(db.Integer)
	timestamp = db.Column(db.DateTime)

	def __repr__(self):
		return "ContactFormResponse(id='{.id!s}, name='{.name!s}, company='{.company!s}', phone_number='{.phone_number!s}', email='{.email!s}', preference='{.preference!s}', body='{.body!s}', timestamp='{.timestamp!s}')"\
			.format(self, self, self, self, self, self, self, self)

