from flask import render_template, flash, redirect, g, request, session, url_for
from app import app, db
from forms import LoginForm, ContactForm, TestimonialForm
from models import User, Client, Testimonial, Service, Service_image, Post, Category, Tag, Comment, ContactFormResponse
from datetime import datetime
import blog
from utilities import get_testimonial, navigation, flash_errors, allowed_file, login_required
from flask.ext.admin import BaseView, expose, Admin, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
import os.path as op

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", title = 'BR Graphic Design | Dayton, Ohio | Custom Website Design | Corporate Identity | Print Design | Consulting')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':        
        if form.validate():        
            user = User.query.filter_by(nickname=form.user_name.data).first()
            flash('Successfully logged in')
            session['user_name'] = user.nickname
            session['user_id'] = user.id
            return redirect(request.args.get("next") or url_for("blog"))
        else:
            flash('Unsuccessful')
            return render_template('login.html', title='Sign In', form=form)
    return render_template('login.html', title = 'Sign In', form = form)  

@app.route("/logout")
@login_required
def logout():
    session.pop('user_name', None)
    session.pop('user_id', None)
    flash('Successfully logged out')
    return redirect(url_for('index'))


@app.route('/add/testimonial', methods=['GET', 'POST'])
@login_required
def add_testimonial():
    form = TestimonialForm()
    if form.validate_on_submit():                
        s = Testimonial(body=form.body.data, timestamp=datetime.now(), poc=form.poc.data, poc_title=form.poc_title.data, poc_company=form.poc_company.data, client_id=form.client.data)
        db.session.add(s)
        db.session.commit()
        flash('Successfully added testimonial')
        return redirect(url_for('add_testimonial'))
    else:
        flash_errors(form)
        flash(form.client.data)
    return render_template('add_testimonial.html', form=form, title='Add Testimonial')   

"""
    ABOUT STUFF
"""

@app.route('/about')    
def about():
    return render_template('about.html', navigation=navigation['about'], title='About Us', testimonial=get_testimonial())

@app.route('/about/programs')    
def about_programs():
    return render_template('about_programs.html', navigation=navigation['about'], title='Design Tools', testimonial=get_testimonial())    

@app.route('/about/our-process')    
def about_our_process():
    return render_template('about_our_process.html', title='Our Process', navigation=navigation['about'], testimonial=get_testimonial())

@app.route('/client-portal')    
def client_portal():
    return render_template('client_portal.html', title='Client Portal')

"""
    CONTACT STUFF
"""

@app.route('/contact', methods=['POST', 'GET'])    
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        c = ContactFormResponse(name=form.name.data, company=form.company.data, phone_number=form.phone_number.data, body=form.body.data, email=form.email.data, preference=form.preference.data, timestamp=datetime.utcnow())
        db.session.add(c)
        db.session.commit()        
        flash('Thank you for your submission.')        
    else:
        flash_errors(form)
    return render_template('contact.html', title='Contact', form=form)    

"""
    CLIENT STUFF
"""
def get_portfolio_navigation():
    return sorted([(client.slug, client.title) for client in Client.query.all()], key=lambda x:x[1])

def get_services_for_client(client_id):
    for service in Service.query.filter_by(client_id=client_id):        
        images = [i for i in Service_image.query.filter_by(service_id=service.id)]
        yield service, images

@app.route('/clients')
@app.route('/clients/<client_slug>')
def client(client_slug):    
    client = Client.query.filter_by(slug=client_slug).first()
    if client == None:
        return redirect(url_for('404'))   
    return render_template('client.html', client=client, title=client.title, testimonial=get_testimonial_by_client(client.id), services=get_services_for_client(client.id), navigation=get_portfolio_navigation())    


"""
    PORTFOLIO STUFF
"""

def get_portfolio_navigation():
    return sorted([(client.slug, client.title) for client in Client.query.all()], key=lambda x:x[1])

@app.route('/portfolio')    
def portfolio():
    # title = 
    return render_template('portfolio.html', navigation=get_portfolio_navigation(), title=app.config['TITLE']+" | "+'Portfolio')

@app.route('/portfolio/website-design')
def portfolio_website_design(): 
    return render_template('portfolio_derived.html', navigation=get_portfolio_navigation(), services=prepare_slideshow(0), title='Website Design')

@app.route('/portfolio/corporate-identity')
def portfolio_corporate_identity():
    return render_template('portfolio_derived.html', navigation=get_portfolio_navigation(), services=prepare_slideshow(1), title='Corporate Identity')

@app.route('/portfolio/print-design')
def portfolio_print_design():
    return render_template('portfolio_derived.html', navigation=get_portfolio_navigation(), services=prepare_slideshow(2), title='Print Design')

@app.route('/portfolio/other-services')
def portfolio_other_services():
    return render_template('portfolio_derived.html', navigation=get_portfolio_navigation(), services=prepare_slideshow(3), title='Other Services')    

"""
    SERVICES STUFF
"""

@app.route('/services')
def services():
    if 'user_name' in session:
        user = session['user_name']
    return render_template('services.html', title='Services', navigation=navigation['services'],testimonial=get_testimonial(), user=user)

@app.route('/services/website-design')
def services_website():
    return render_template('services_website_design.html', title='Website Design',  navigation=navigation['services'], testimonial=get_testimonial(), slideshow=get_random_slideshow(0))    

@app.route('/services/corporate-identity')
def services_corporate_identity():
    return render_template('services_corporate_identity.html', title='Corporate Identity',  navigation=navigation['services'], testimonial=get_testimonial(),  slideshow=get_random_slideshow(1))

@app.route('/services/print-design')
def services_print_design():
    return render_template('services_print_design.html', title='Print Design', navigation=navigation['services'],testimonial=get_testimonial(), slideshow=get_random_slideshow(2))

@app.route('/services/other-services')
def services_other_services():
    return render_template('services_other_services.html', title='Other Services', navigation=navigation['services'], testimonial=get_testimonial(), slideshow=get_random_slideshow(3))    


@app.errorhandler(403)
def internal_error_403(error):
    return render_template('404.html', title='403'), 403

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html', title='404'), 404


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return 'user_name' in session


admin = Admin(app, 'BRGD', index_view=MyAdminIndexView())
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Client, db.session))
admin.add_view(ModelView(Service, db.session))
admin.add_view(ModelView(Testimonial, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ModelView(Comment, db.session))
admin.add_view(ModelView(ContactFormResponse, db.session))
path = op.join(op.dirname(__file__), 'static')
admin.add_view(FileAdmin(path, '/static/', name='Static Files'))        