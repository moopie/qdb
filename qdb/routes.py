from qdb import app
from datetime import datetime
from flask import (url_for, render_template, jsonify,
	redirect, abort, flash, request, session)
from qdb.models import Quote
from qdb.database import db_session
from qdb.utils import Paginator
from sqlalchemy.sql.expression import func


@app.route('/')
def home():
	search = request.args.get('s')
	page = int(request.args.get('p', 1))

	query = db_session.query(Quote) \
		.filter(Quote.approved == True) \
		.order_by(Quote.submitted_at.desc())

	if search:
		query = query.filter(Quote.body.like('%'+search+'%'))

	if page > 0:
		paginator = Paginator(query, page, request.url)
		quotes = paginator.items

		if request.headers.get('Accept') == 'application/json':
			return jsonify(quotes=paginator)
	else:
		paginator = None
		quotes = query.all()

		if request.headers.get('Accept') == 'application/json':
			return jsonify(quotes=quotes)

	return render_template('list.html.jinja', quotes=quotes, paginator=paginator)


@app.route('/random')
def random():
	query = db_session.query(Quote) \
		.filter(Quote.approved == True) \
		.order_by(func.random()) \
		.limit(10)

	quotes = query.all()

	return render_template('list.html.jinja', quotes=quotes)


@app.route('/submit', methods=['GET', 'POST'])
def submit():
	if request.method == 'GET':
		return render_template('form.html.jinja', form_action=url_for('submit'))

	body = Quote.prepare(request.form['body'])
	quote = Quote(body, datetime.now())
	db_session.add(quote)
	db_session.commit()

	flash('Quote added!')
	return redirect(url_for('home'))


@app.route('/pending')
def pending():
	if not session.get('logged_in'):
		flash('You must be logged in to do that!')
		return redirect(url_for('home'))

	query = db_session.query(Quote) \
		.filter(Quote.approved == False) \
		.order_by(Quote.submitted_at.desc())

	quotes = query.all()

	if request.headers.get('Accept') == 'application/json':
		return jsonify(quotes=quotes)

	return render_template('list.html.jinja', quotes=quotes)


@app.route('/login')
def login():
	if request.args.get('password') == app.config.get('PASSWORD'):
		session['logged_in'] = True
		flash('You are now logged in!')
	else:
		flash('Incorrect password!')

	return redirect(url_for('home'))


@app.route('/<int:quote_id>', methods=['GET', 'POST', 'DELETE'])
def show(quote_id):
	quote = db_session.query(Quote) \
		.filter(Quote.id == quote_id) \
		.first()

	if not quote:
		return abort(404)

	if request.method == 'GET':
		if request.headers.get('Accept') == 'application/json':
			return jsonify(quote=quote)

		return render_template('show.html.jinja', quote=quote)
	elif request.method == 'DELETE':
		db_session.delete(quote)
		db_session.commit()
		return 'OK'
	else:
		return 'not yet implemented'


@app.route('/<int:quote_id>/vote', methods=['POST'])
def vote(quote_id):
	quote = db_session.query(Quote) \
		.filter(Quote.id == quote_id) \
		.first()

	if not quote:
		return abort(404)

	return 'not yet implemented'


@app.route('/<int:quote_id>/approve', methods=['POST'])
def approve(quote_id):
	quote = db_session.query(Quote) \
		.filter(Quote.id == quote_id) \
		.first()

	if not quote:
		return abort(404)

	quote.approved = True
	db_session.add(quote)
	db_session.commit()
	return 'OK'