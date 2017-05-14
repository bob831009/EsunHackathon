from __future__ import print_function

from flask import Flask, render_template, request, url_for, redirect, session
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig

from custom_form import RegisterForm, LoginForm
from customerDB import getCustomerDB, getUsername2CustomerIdx

import json
import os

	
def create_app(configfile=None):
	print ('[INFO]:create_app --> loading customer database and mapping')
	customerDB = getCustomerDB()
	username2customerID = getUsername2CustomerIdx()
	
	app = Flask(__name__, static_url_path='/src/static')
	
	app._static_folder = os.path.abspath("src/static/")
	AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
                                # highly recommend =)
                                # https://github.com/mbr/flask-appconfig
	Bootstrap(app)
	app.config['SECRET_KEY'] = 'devkey'
	app.config['RECAPTCHA_PUBLIC_KEY'] = \
		'6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'

	@app.route('/register', methods=('GET', 'POST'))
	def register():
		form = RegisterForm()
		if request.method == 'POST' and form.validate_on_submit():
			# print ('valite on submit = ' + str())
			print (form.radio_field.data)
			if form.username.data in username2customerID:
				return redirect(url_for('.register'))

			session['isLogin'] = json.dumps(request.form)
			return redirect(url_for('.mainPage'))
		return render_template('register.html', form=form)

	@app.route('/login', methods=('GET', 'POST'))
	def login():
		form = LoginForm()
		if request.method == 'POST' and form.validate_on_submit():
			username = form.username.data
			password = form.password.data
			print (password + ' , ' + customerDB[username2customerID[username] - 1][2])
			if username in username2customerID and password == customerDB[username2customerID[username] - 1][2]:
				print('[INFO]:login --> username ( ' + form.username.data + ' ) confirmed')
				session['isLogin'] = json.dumps(request.form)
			return redirect(url_for('.mainPage'))
		return render_template('login.html', form=form)

	@app.route('/')
	def mainPage():
		data = {}
		# user = request.args.get('user')
		if 'isLogin' not in session:
			data['isLogin'] = False
			print('[INFO]:mainPage --> not login')
			return render_template('index.html', data=data)
		else:
			data['isLogin'] = True
			form = json.loads(session['isLogin'])
			# print (user)
			print('[INFO]:mainPage --> login : ', end=' ')
			print(form)
			return render_template('index.html', data=data)
	
	@app.route('/logout')
	def logout():
		session.pop('isLogin', None)
		return redirect(url_for('.mainPage'))
	return app

if __name__ == '__main__':
	create_app().run(debug=True)