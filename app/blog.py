from flask import render_template, flash, redirect, g, request, session, url_for
from app import app, db
from utilities import  navigation, flash_errors, allowed_file, login_required
from models import User, Post, Tag, Category
from datetime import date
from forms import PostForm
from werkzeug import secure_filename
import os

num_to_month = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
month_to_num = dict(zip(num_to_month.values(), num_to_month.keys()))

def get_all_posts(qty=10):
	return Post.query.limit(qty).all() 

def get_blog_dates(qty=10):
	months = {}
	for post in Post.query.all():		
		my_date = post.timestamp
		if (my_date.year, my_date.month) in months:
			months[(my_date.year, my_date.month)] += 1	
		else:
			months[(my_date.year, my_date.month)] = 1	
	for x in sorted(months, key=lambda x:months[x])[0:qty]:
		yield x, months[x]	

def get_blog_tags(qty=10):
	tags = {}
	for post in Post.query.all():
		for tag in post.tags:
			if (tag.title, tag.slug) in tags:
				tags[(tag.title, tag.slug)] += 1
			else:
				tags[(tag.title, tag.slug)] = 1
	for x in sorted(tags, key=lambda x:tags[x])[0:qty]:
		yield x, tags[x]

def get_blog_categories(qty=10):
	categories = {}
	for post in Post.query.all():
		for category in post.categories:
			if (category.title, category.slug) in categories:
				categories[(category.title, category.slug)] += 1
			else:
				categories[(category.title, category.slug)] = 1
	for x in sorted(categories, key=lambda x:categories[x])[0:qty]:
		yield x, categories[x]

def get_authors(posts):
	authors = []
	for post in posts:
		a = User.query.filter_by(id=post.user_id).first_or_404()		
		authors.append(a)
	return authors

def get_posts_by_timestamp( year, month=None):
	for p in Post.query.all():
		if p.timestamp.year == int(year):
			if not month:
				yield p
			elif month != u'None' and int(month) == p.timestamp.month: 
				yield p

def get_next_previous_post(post):
	next, previous = None, None
	for p in Post.query.all():
		if p != post:
			if post.timestamp > p.timestamp: # if the current post is from a later date
				if next:
					if  (post.timestamp - p.timestamp) < (post.timestamp - next.timestamp):
						next = p
				else:
					next = p
			else:
				if previous:
					if  (p.timestamp - post.timestamp) < (previous.timestamp - post.timestamp):
						previous = p
				else:
					previous = p
	return next, previous

@login_required
@app.route('/add/post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():      	
        s = Post(body=form.body.data, title=form.title.data, slug=form.slug.data, user_id=session['user_id'])        
        for cat in form.category.data:
        	cat = Category.query.filter_by(id=cat).first()
        	if cat:
        		s.categories.append( cat)
        for tag in form.tag.data:
        	tag = Tag.query.filter_by(id=tag).first()
        	if tag:
        		s.tags.append( tag)		
        my_image = form.img.data  
        if allowed_file(my_image.filename):
			filename = secure_filename(my_image.filename)
			save_to = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			my_image.save(save_to)
			db.session.add(s)
			flash('Successfully uploaded '+save_to)
			db.session.commit()
			flash('Successfully added post')
        else:
        	flash('Unable to save file')
        return redirect(url_for('add_post'))
    else:
        flash_errors(form)
    return render_template('add_post.html', form=form, title='Add Post')	

@app.route('/blog')
def blog():
	posts = Post.query.paginate(1, app.config['POSTS_PER_PAGE'], False).items		
	return render_template('blog.html', title='Blog Postings | BR Graphic Design', date_navigation=get_blog_dates(), tag_navigation=get_blog_tags(),  category_navigation=get_blog_categories(), posts=posts, authors=get_authors(posts), all_posts=get_all_posts())

@app.route('/blog/page')
@app.route('/blog/page/<int:page>')
def blog_page(page=1):
	posts = Post.query.paginate(page, app.config['POSTS_PER_PAGE'], False).items		
	title = 'Blog'
	if page != 1:
		title = title + " Page "+str(page)
	return render_template('blog.html', title=title+' | BR Graphic Design', date_navigation=get_blog_dates(), tag_navigation=get_blog_tags(),  category_navigation=get_blog_categories(), posts=posts, authors=get_authors(posts), all_posts=get_all_posts())

@app.route('/blog/posts/<post>')
def blog_post(post):
	post = Post.query.filter_by(slug = post).first_or_404()	
	title = 'Blog Posting'
	next, previous = get_next_previous_post(post)
	return render_template('post.html', post=post, title=title+' | BR Graphic Design', \
		date_navigation=get_blog_dates(), tag_navigation=get_blog_tags(),  category_navigation=get_blog_categories(), \
		author=get_authors([post])[0], all_posts=get_all_posts(), next=next, previous=previous)

# possible TODO: make links to archives, categories, etc. be a word cloud
@app.route('/blog/archives')
@app.route('/blog/archives/<year>')
@app.route('/blog/archives/<year>/<month>')
@app.route('/blog/archives/<year>/<month>/<int:page>')
def blog_archive(year=2013, month=None, page=1):
	posts = [p for p in get_posts_by_timestamp(year, month)]	
	title = 'Blog Archive {} {} {} {} {}'.format('-' if month else '', num_to_month[int(month)] if month else '', year,  'Page ' if page != 1 else '', str(page) if page != 1 else '')		
	return render_template('blog.html', title=title+' | BR Graphic Design', date_navigation=get_blog_dates(), tag_navigation=get_blog_tags(),  category_navigation=get_blog_categories(), posts=posts, authors=get_authors(posts), all_posts=get_all_posts())

@app.route('/blog/categories')
@app.route('/blog/categories/<category>')
def blog_categories(category=None, page=1):
	posts = Post.query.filter(Post.categories.any(slug=category)).paginate(page, app.config['POSTS_PER_PAGE'], False).items
	title = 'Blog Category: '
	if category:
		title = title + category.title()
	if page != 1:
		title = title + " Page "+str(page)	
	return render_template('blog.html', title=title+' | BR Graphic Design', date_navigation=get_blog_dates(), tag_navigation=get_blog_tags(),  category_navigation=get_blog_categories(), posts=posts, authors=get_authors(posts), all_posts=get_all_posts())	

@app.route('/blog/tags')
@app.route('/blog/tags/<tag>')
def blog_tags_tag(tag=None, page=1):
	posts = Post.query.filter(Post.tags.any(slug=tag)).paginate(page, app.config['POSTS_PER_PAGE'], False).items
	title = 'Blog Tag: '
	if tag:
		title = title + tag.title()
	if page != 1:
		title = title + " Page "+str(page)	
	return render_template('blog.html', title=title+' | BR Graphic Design', date_navigation=get_blog_dates(), tag_navigation=get_blog_tags(),  category_navigation=get_blog_categories(), posts=posts, authors=get_authors(posts), all_posts=get_all_posts())	

@app.route('/blog/authors')
@app.route('/blog/authors/<author>')	
def blog_author(author=None, page=1):
	title = 'Blog Authors'
	if not author:
		author = 'ryan'
	author = User.query.filter_by(nickname=author).first_or_404()
	posts = Post.query.filter_by(user_id=author.id).paginate(page, app.config['POSTS_PER_PAGE'], False).items
	if author:
		title = title + " - "+author.nickname
	if page != 1:
		title = title + ' Page '+str(page)
	return render_template('blog.html', title=title+' | BR Graphic Design', date_navigation=get_blog_dates(), tag_navigation=get_blog_tags(),  category_navigation=get_blog_categories(), posts=posts, authors=get_authors(posts), all_posts=get_all_posts())	
