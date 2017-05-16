from __future__ import print_function

from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from wtforms import BooleanField

from custom_form import RegisterForm, LoginForm, ProductForm
from customerDB import getCustomerDB, getUsername2CustomerIdx
from match_expert import match
from utils import *

import ast
import random
import numpy as np
import json
import os

root_dir = '.'
data_dir = os.path.join(root_dir, 'data')

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
		prod_list.append(prod_clusters[sort_list[i]]['cluster_members'][random.randint(0, len(prod_clusters[sort_list[i]]['cluster_members']) - 1)])
	print (prod_list)
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

	user_data = readPickle(os.path.join(data_dir, 'user_data.pkl'))
	user_clusters = readPickle(os.path.join(data_dir, 'user_clusters.pkl'))
	# prod_data = readPickle(os.path.join(data_dir, 'prod_data.pkl'))
	prod_data = readJson(os.path.join(data_dir, 'new_fund.json'))
	prod_clusters = readJson(os.path.join(data_dir, 'cluster_centers.json'))
	
	expert_data = readJson(os.path.join(data_dir, 'financial_commissioner.json'))
	# prod_data = pickle.load('prod_data.pkl')
	# prod_clusters = pickle.load('prod_clusters.pkl')
	# customer = [None, None]

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
			# print (form.checkbox_field.data)
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
				# customer = [username, username2customerID[username]]

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
		# customer = [None, None]
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
		if 'isLogin' not in session:
			return redirect(url_for('.mainPage'))
		data = {'isLogin' : True, 'listIdx' : 10}
		if json.loads(session['isLogin'])['username'] not in username2customerID:
			user_id = int(json.loads(session['isLogin'])['customer_id'])
		else:
			user_id = username2customerID[json.loads(session['isLogin'])['username']]
		if 'isRefresh' in request.args and request.args['isRefresh'] == 'no':
			if 'listIdx' in request.args:
				print ('idx ====== ' + str(int(request.args['listIdx'])))
				listIdx = int(request.args['listIdx'])
				product_dict = ast.literal_eval(request.args['productDict'])
				like_prod(user_id, product_dict[listIdx]['id'], user_data, user_clusters, prod_data)
				return render_template('productRank.html', products=product_dict, data=data)
			elif 'productIdx' in request.args:
				data['listIdx'] = int(request.args['productIdx'])
				product_dict = ast.literal_eval(request.args['productDict'])
				return render_template('productRank.html', products=product_dict, data=data)
		print('yes refresh')
		prod_list = create_recommand_list(user_id, user_data, prod_clusters)
		product_dict = {}
		for idx in range(10):
			# print (prod_data[prod_list[idx]])
			product_dict[idx] = prod_data[prod_list[idx]]
		# print (product_dict)
		return render_template('productRank.html', products=product_dict, data=data)
	@app.route('/expertRank')
	def expertRank():
		if 'isLogin' not in session:
			return redirect(url_for('.mainPage'))
		data = {'isLogin' : True}
		if json.loads(session['isLogin'])['username'] not in username2customerID:
			user_id = int(json.loads(session['isLogin'])['customer_id'])
		else:
			user_id = username2customerID[json.loads(session['isLogin'])['username']]
		print (expert_data)
		expert_dict = match(expert_data, user_id, user_data, prod_data, prod_clusters)
		return render_templaxte('expertRank.html', experts=expert_dict, data=data)
	return app

if __name__ == '__main__':
	create_app().run(debug=True)