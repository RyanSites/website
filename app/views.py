from flask import render_template, flash, redirect, g, request, session, url_for
from wtforms.fields import TextAreaField
from flask.ext.mail import Message
from app import app, db
from forms import LoginForm, ContactForm, TestimonialForm
from models import User, Client, Testimonial, Service, Service_image, Post, Category, Tag, Comment, ContactFormResponse
from datetime import datetime
import blog
from utilities import get_testimonial, navigation, flash_errors, allowed_file, login_required, get_random_slideshow, get_testimonial_by_client, prepare_slideshow
from flask.ext.admin import BaseView, expose, Admin, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
import os.path as op
from flask.ext.mail import Mail
# from flask.ext.images import Images

mail = Mail(app)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", title = 'BR Graphic Design')

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
    return render_template('login.html', title = 'Sign In | BR Graphic Design', form = form)  

@app.route("/logout")
@login_required
def logout():
    session.pop('user_name', None)
    session.pop('user_id', None)
    flash('Successfully logged out')
    return redirect(url_for('index'))

def get_user():
    if 'user_name' in session:
        return session['user_name']    

"""
    ABOUT STUFF
"""

@app.route('/about')    
def about():
    return render_template('about.html', 
        navigation=navigation['about'], 
        title='About Us | BR Graphic Design', 
        testimonial=get_testimonial(), 
        user=get_user(),
        seo_keywords='BR Graphic Design, About Us, Ryan Sites, Brandy Sites', 
        seo_description='The design duo at BR Graphic Design holds over 20 years of experience in programming, graphic design, and marketing')

@app.route('/about/programs')    
def about_programs():
    return render_template('about_programs.html', 
        navigation=navigation['about'], 
        title='Design Tools | BR Graphic Design', 
        testimonial=get_testimonial(), 
        user=get_user(),
        seo_keywords='BR Graphic Design, Design Tools, Open Source, Dayton, Ohio', 
        seo_description='One of the ways we minimize our overhead costs is to utilize open source software whenever possible.')    

@app.route('/about/our-process')    
def about_our_process():
    return render_template('about_our_process.html', 
        title='Our Process | BR Graphic Design', 
        navigation=navigation['about'], 
        testimonial=get_testimonial(), 
        user=get_user(),
        seo_keywords='BR Graphic Design, Design Process, Graphic Design, Web Development, Dayton, Ohio', 
        seo_description='Our carefully designed process is meant to ensure customer satisfaction througout the entire project life cycle')

@app.route('/client-portal', methods=['GET', 'POST'])    
def client_portal():
    form = LoginForm()
    if request.method == 'POST':
        flash('Please come back later.')
        return render_template('login.html', title='Client Portal | BR Graphic Design', form=form)
    return render_template('login.html', title='Client Portal | BR Graphic Design', form=form)

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
        msg = Message("Contact Form Submission",                 sender="contact_form@brgdonline.com",                  recipients=["info@brgdonline.com", 'brandy@brgdonline.com'])
        msg.body = "Name: {!s}\nCompany: {!s}\nPhone: {!s}\nEmail: {!s}\nPreference: {!s}\n Timestamp: {!s}\nBody: {!s}".format(form.name.data, form.company.data, form.phone_number.data, form.email.data, form.preference.data, datetime.utcnow(), form.body.data)
        flash('Thank you for your submission.')        
        mail.send(msg)
    else:
        flash_errors(form)
    return render_template('contact.html', 
        title='Contact | BR Graphic Design', 
        form=form, 
        user=get_user(), 
        seo_keywords='BR Graphic Design, Contact, Quote, Dayton, Ohio', 
        seo_description='Contact form for BR Graphic Design LLC, a full service graphic/web design company in Dayton Ohio')    

"""
    CLIENT STUFF
"""
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
    return render_template('client.html', 
        client=client, 
        title=client.title+' | Clients | BR Graphic Design', 
        testimonial=get_testimonial_by_client(client.id), 
        services=get_services_for_client(client.id), 
        navigation=get_portfolio_navigation(), 
        user=get_user(),
        seo_keywords='BR Graphic Design, '+client.title.replace(',', '')+', Clients, Graphic Design, Web Development', 
        seo_description=client.body)    

"""
    PORTFOLIO STUFF
"""

def get_portfolio_navigation():
    return sorted([(client.slug, client.title) for client in Client.query.all()], key=lambda x:x[1])

@app.route('/portfolio')    
def portfolio():
    return render_template('portfolio.html',
    navigation=get_portfolio_navigation(), 
    title='Portfolio | BR Graphic Design', 
    user=get_user(),
    seo_keywords='BR Graphic Design, Portfolio, Services, Dayton, Ohio', 
    seo_description='The portfolio of BR Graphic Design LLC.')

@app.route('/portfolio/website-design')
def portfolio_website_design(): 
    return render_template('portfolio_derived.html', 
        navigation=get_portfolio_navigation(), 
        services=prepare_slideshow(0), 
        title='Website Design Portfolio | BR Graphic Design', 
        user=get_user(),
        seo_keywords='BR Graphic Design, Website Design Work, Portfolio, Dayton, Ohio', 
        seo_description='The Website design/development portfolio of BR Graphic Design LLC.')

@app.route('/portfolio/corporate-identity')
def portfolio_corporate_identity():
    return render_template('portfolio_derived.html', 
        navigation=get_portfolio_navigation(), 
        services=prepare_slideshow(1), 
        title='Corporate Identity Portfolio | BR Graphic Design', 
        user=get_user(),
        seo_keywords='BR Graphic Design, Corporate Identity, Marketing, Portfolio, Dayton, Ohio', 
        seo_description='The Corporate identity portfolio of BR Graphic Design LLC')

@app.route('/portfolio/print-design')
def portfolio_print_design():
    return render_template('portfolio_derived.html', 
        navigation=get_portfolio_navigation(), 
        services=prepare_slideshow(2), 
        title='Print Design Portfolio | BR Graphic Design', 
        user=get_user(),
        seo_keywords='BR Graphic Design, Print Design, Graphic Design, Dayton, Ohio', 
        seo_description='The Print Design portfolio of BR Graphic Design LLC')

@app.route('/portfolio/other-services')
def portfolio_other_services():
    return render_template('portfolio_derived.html',
     navigation=get_portfolio_navigation(), 
     services=prepare_slideshow(3), 
     title='Other Services Portfolio | BR Graphic Design', 
     user=get_user(),
     seo_keywords='BR Graphic Design, Photography, Portfolio, Dayton, Ohio', 
     seo_description='Portfolio of miscellaneous work that BR Graphic Design LLC performs')    

"""
    SERVICES STUFF
"""

@app.route('/services')
def services():
    return render_template('services.html',
     title='Services | BR Graphic Design',
     navigation=navigation['services'],
     testimonial=get_testimonial(), 
     slideshow = get_random_slideshow(), 
     user=get_user(),
     seo_keywords='BR Graphic Design, Services, Dayton, Ohio', 
     seo_description='The services BR Graphic Design LLC performs for their clients')

@app.route('/services/website-design')
def services_website():
    return render_template('services_website_design.html', 
        title='Website Design Services  | BR Graphic Design',  
        navigation=navigation['services'], 
        testimonial=get_testimonial(), 
        slideshow=get_random_slideshow(0), 
        user=get_user(),
        seo_keywords='BR Graphic Design, Website Design, Website Development, Web Services, Dayton, Ohio', 
        seo_description='Each website by BR Graphic Design LLC is 100% custom designed and carefully crafted to project a unique look and feel for our clients.')    

@app.route('/services/corporate-identity')
def services_corporate_identity():
    return render_template('services_corporate_identity.html', 
        title='Corporate Identity Services  | BR Graphic Design',  
        navigation=navigation['services'], 
        testimonial=get_testimonial(),  
        slideshow=get_random_slideshow(1), 
        user=get_user(),
        seo_keywords='BR Graphic Design, Corporate Identity, Marketing, Services, Dayton, Ohio', 
        seo_description='At BR Graphic Design, we take the time to really get to know your business, competition, and business objectives.')

@app.route('/services/print-design')
def services_print_design():
    return render_template('services_print_design.html', 
        title='Print Design Services  | BR Graphic Design', 
        navigation=navigation['services'],
        testimonial=get_testimonial(), 
        slideshow=get_random_slideshow(2), 
        user=get_user(),
        seo_keywords='BR Graphic Design, Print Design Services, Dayton, Ohio', 
        seo_description='Whether your organization needs a simple sell sheet, or 10,000 trifold brochures, please consider BR Graphic Design for a custom, professional design.')

@app.route('/services/other-services')
def services_other_services():
    return render_template('services_other_services.html', 
        title='Other Services  | BR Graphic Design', 
        navigation=navigation['services'], 
        testimonial=get_testimonial(), 
        slideshow=get_random_slideshow(3), 
        user=get_user(),
        seo_keywords='BR Graphic Design, Photography',
        seo_description='We strive to offer you a full range of service products so that you can rest assured that your entire corporate identity package will be crafted with consistency')    


@app.errorhandler(403)
def internal_error_403(error):
    return render_template('404.html', title='Access Denied  | BR Graphic Design'), 403

@app.errorhandler(404)
def internal_error(error):
    app.logger.warning('404 - '+str(request))
    return render_template('404.html', title='Page Not Found  | BR Graphic Design'), 404


class MyAdminIndexView(AdminIndexView):
    form_overrides = dict(body=TextAreaField)



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
