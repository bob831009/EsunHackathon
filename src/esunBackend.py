from __future__ import print_function

from flask import Flask, render_template, request, url_for, redirect, session
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig

from register_form import RegisterForm

import json
import os

def create_app(configfile=None):
	
	# session.clear()

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
		print (request.method)
		if request.method == 'POST' and form.validate_on_submit():
			# print ('valite on submit = ' + str())
			session['isLogin'] = json.dumps(request.form)
			return redirect(url_for('.mainPage'))
		return render_template('register.html', form=form)

	@app.route('/')
	def mainPage():
		data = {}

		if 'isLogin' not in session:
			data['isLogin'] = False
			print('[INFO]:mainPage --> not login')
			return render_template('index.html', data=data)
		else:
			data['isLogin'] = True
			form = json.loads(session['isLogin'])

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