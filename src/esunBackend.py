from __future__ import print_function

from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from wtforms import BooleanField

from custom_form import RegisterForm, LoginForm, ProductForm
from customerDB import getCustomerDB, getUsername2CustomerIdx
from utils import *

from customer_kmeans import getUserData, getUserClusterData

import ast
import random
import numpy as np
import json
import os

def redirectUrl():
	if request.args['fromUrl'] == 'hotIssue':
		return '.hotIssue'	
	elif request.args['fromUrl'] == 'mainPage':
		return '.mainPage'
	else:
		return '.mainPage'	

def create_recommand_list(user_id, user_data, prod_clusters):
	print (user_id)
	score_list = user_data[user_id]['scores']
	sort_list = np.argsort(np.array(score_list)).tolist()
	prod_list = []
	for i in range(10):
		prod_list.append(prod_clusters[sort_list[i]]['prod_ids'][random.randint(0, len(prod_clusters[sort_list[i]]['prod_ids']) - 1)])
	return prod_list

def like_prod(user_id, prod_id, user_data, user_clusters, prod_data):
	print (user_id, prod_id)
	prod_clu_id = prod_data[prod_id]['cluster_id']
	user_data[user_id]['scores'][prod_clu_id] += 1
	user_clusters[user_data[user_id]['cluster_id']]['scores'][prod_clu_id] += 1
	print ('result : ' + str(user_clusters[user_data[user_id]['cluster_id']]['scores'][prod_clu_id]))

def create_app(configfile=None):
	# myName = [1]
	print ('[INFO]:create_app --> loading customer database and mapping')
	customerDB = getCustomerDB()
	username2customerID = getUsername2CustomerIdx()

	user_data = getUserData()	
	user_clusters = getUserClusterData()
	# user_data = pickle.load('user_data.pkl')
	# user_clusters = pickle.load('user_clusters.pkl')
	prod_data = readPickle(os.path.join('./data', 'prod_data.pkl'))
	prod_clusters = readPickle(os.path.join('./data', 'prod_clusters.pkl'))
	# prod_data = pickle.load('prod_data.pkl')
	# prod_clusters = pickle.load('prod_clusters.pkl')



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
			print (form.checkbox_field.data)
			if form.username.data in username2customerID:
				return redirect(url_for('.register'))

			session['isLogin'] = json.dumps(request.form)
			return redirect(url_for(redirectUrl()))
			
		return render_template('register.html', form=form)

	@app.route('/login', methods=('GET', 'POST'))
	def login():
		form = LoginForm()
		if request.method == 'POST' and form.validate_on_submit():
			username = form.username.data
			password = form.password.data
			print (password + ' , ' + customerDB[username2customerID[username]][2])
			if username in username2customerID and password == customerDB[username2customerID[username] - 1][2]:
				print('[INFO]:login --> username ( ' + form.username.data + ' ) confirmed')
				session['isLogin'] = json.dumps(request.form)
			return redirect(url_for(redirectUrl()))
			
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
	
	@app.route('/hotissue')
	def hotIssue():
		data = {}
		if 'isLogin' not in session:
			data['isLogin'] = False
			print('[INFO]:hotIssue --> not login')
			return render_template('hotissue.html', data=data)
		else:
			data['isLogin'] = True
			# print('[INFO]:hotIssue --> login : ', end=' ')
			# print(form)			
			return render_template('hotissue.html', data=data)
	
	@app.route('/logout')
	def logout():
		# print(request.args['fromUrl'])
		session.pop('isLogin', None)
		return redirect(url_for(redirectUrl()))
	

	@app.route('/click')
	def clickLike():
		print('XDD')
		product = [ProductForm(), ProductForm(), ProductForm()]
		
		return render_template('rankingList.html', products=product)
		
		# pass
		# print request.args['']
	@app.route('/productRank')
	def productRank():
		if 'isRefresh' in request.args and request.args['isRefresh'] == 'no':
			print ('no refresh')
			print (request.args)
			print ('--------------------')
			print (request.args['productDict'])
			print (type(request.args['productDict']))
			print ('idx ====== ' + str(int(request.args['listIdx'])))
			listIdx = int(request.args['listIdx'])
			product_dict = ast.literal_eval(request.args['productDict'])
			
			like_prod(0, product_dict[listIdx]['prod_id'], user_data, user_clusters, prod_data)
			
			# product_dict = dict(request.args['productDict'])
			return render_template('rankingList.html', products=product_dict)
		user_id = 0
		prod_list = create_recommand_list(user_id, user_data, prod_clusters)
		print (prod_list[0])
		print (prod_data[prod_list[0]])
		# product_list = [prod_data[prod_list[idx]] for idx in range(10)]
		product_dict = {}
		for idx in range(10):
			product_dict[idx] = prod_data[prod_list[idx]]
		print (product_dict)
		return render_template('rankingList.html', products=product_dict)
		
	@app.route('/hello')
	def helloWorld():
		print ('hello world')
		# global myName
		# print (myName)
		# myName += 1
		# myName.append(55)
		# customerDB.append(['XDDD'])
		# product = ['AAA', 'BBB', 'CCC', 'DDD']
		# product = [BooleanField('AAA', default=False), BooleanField('BBB', default=False), BooleanField('CCC', default=False)]
		user_id = 0
		prod_list = create_recommand_list(user_id, user_data, prod_clusters)
		print (prod_list[0])
		print (prod_data[prod_list[0]])
		product_list = [prod_data[prod_list[idx]] for idx in range(10)]
		product_list = {}
		for idx in range(10):
			product_list[idx] = prod_data[prod_list[idx]]
		# product = [ProductForm(), ProductForm(), ProductForm()]
		# print (product[0].like_button.data)
		return render_template('rankingList.html', products=product_list)
		# return render_template()
	return app

if __name__ == '__main__':
	create_app().run(debug=True)