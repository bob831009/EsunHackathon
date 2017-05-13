from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig

from register_form import RegisterForm

import os

def create_app(configfile=None):
	app = Flask(__name__, static_url_path='/src/static')
	
	app._static_folder = os.path.abspath("src/static/")
	AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
                                # highly recommend =)
                                # https://github.com/mbr/flask-appconfig
	Bootstrap(app)


	@app.route('/register', methods=('GET', 'POST'))
	def register():
		form = RegisterForm()
		return render_template('register.html', form=form)

	@app.route('/')
	def mainPage():
		return render_template('index.html')


	return app

if __name__ == '__main__':
	create_app().run(debug=True)