from flask import flash, session, redirect, url_for
from random import choice
from app.models import Testimonial, Service, Client, Service_image
from app import app
from functools import wraps

navigation = {'about':[('/about', 'About Us'), ('/about/programs', 'Design Tools'), ('/about/our-process', 'Our Process')],\
'services':[('/services', 'Services'), ('/services/website-design', 'Website Design'), ('/services/corporate-identity', 'Corporate Identity'),('/services/print-design', 'Print Design'), ('/services/other-services', 'Other Services')],\
'portfolio':[('/portfolio/website-design', 'Website Design'), ('/portfolio/corporate-identity', 'Corporate Identity'), ('/portfolio/print-design', 'Print Design'), ('/portfolio/other-services', 'Other Services')]}

def get_testimonial(ids=None):
    """
        Can optionally take a set of ids to choose from. Otherwise randomly selects one from all testimonials.
    """
    testimonials = {}
    for t in Testimonial.query.all():
    	testimonials[t.id] = t
    if ids:
    	c = choice(testimonials.keys())
        return testimonials[c]
    return choice(testimonials.values())

def get_testimonial_by_client(id):
	t = Testimonial.query.filter_by(client_id=id).first()
	if t:
		return t
	return get_testimonial()

def prepare_slideshow(typ):
	##[(0, 'website'), (1, 'corporate'), (2, 'print'), (3, 'other')]
	result = []
	for service in Service.query.filter_by(service_type=typ):
		client = Client.query.filter_by(id=service.client_id).first()
		images = Service_image.query.filter_by(service_id=service.id)
		if images:
			result.append( (client, service, images) )
	return result

def get_random_slideshow(typ=None):
    if typ == None:
        typ = choice([0, 1, 2, 3])
	try:
		x = choice(prepare_slideshow(typ))
	except IndexError:
		return []
	else:
		return x

def get_client_services(client_id):
	return Service.query.filter_by(client_id=client_id)

def flash_errors(form):    
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))	

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']  

def validate_slug(slug):
	if slug.endswith('/'):
		slug = slug[:-1]
	slug = slug.replace('_', '-')
	return slug


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
    	print ('here')
        if 'user_name' in session:			
			return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap	