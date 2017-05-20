#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

from flask import Flask, jsonify, render_template, request, url_for, redirect, session, flash
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from wtforms import BooleanField

from custom_form import RegisterForm, LoginForm, ProductForm
from customerDB import getCustomerDB, getUsername2CustomerIdx
from match_expert import match
from utils import *

import chartkick
import logging
from logging.handlers import RotatingFileHandler
import ast
import random
import numpy as np
import json
import os
import time

root_dir = '.'
data_dir = os.path.join(root_dir, 'data')
log_dir = os.path.join(root_dir, 'log')

LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(funcName)11s - %(levelname)s - %(message)s'
LOGGING_MAXBYTES = 10000
LOGGING_BACKUPCOUNT = 5

logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)

werkzeugLogger = logging.getLogger('werkzeug')
werkzeugLogger.setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
fileHandler = RotatingFileHandler(os.path.join(log_dir, 'esunBackend.log') , maxBytes=LOGGING_MAXBYTES, backupCount=LOGGING_BACKUPCOUNT)
fileHandler.setLevel(LOGGING_LEVEL)
formatter = logging.Formatter(LOGGING_FORMAT)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

# consoleHandler = logging.StreamHandler()
# consoleHandler.setFormatter(formatter)
# logger.addHandler(consoleHandler)

def strTimeProp(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def randomDate(start, end, prop):
    return strTimeProp(start, end, '%m/%d/%Y', prop)


def getClusterDist(prod_clusters):
	prod_features = ["least_buy", "net_worth", "main_invest_region", "risk_beta", "return_on_investment_3month", "return_on_investment_6month", "return_on_investment_1year", "return_on_investment_3year", "risk_return_level", "established_scale", "scale", "risk_standard_deviation", "fee"]
	prod_clu_centers= []
	for i in range(20):
		prod_clu_centers.append([prod_clusters[i][prod_features[j]] for j in range(len(prod_features))])

	clusters_dis = []
	for i in range(20):
		tmp = []
		for j in range(20):
			if (i == j):
				tmp.append(10.)
			else:
				sub = np.subtract(prod_clu_centers[i], prod_clu_centers[j])
				dis = 0.
				for k in range(len(sub)):
					dis += (sub[k]**2)
				tmp.append(dis**0.5)
		clusters_dis.append(np.log10(tmp))
	return clusters_dis

def redirectUrl():
	logger.debug('redirect to the url: ' + request.args['fromUrl'])
	if request.args['fromUrl'] == 'hotIssue':
		return '.hotIssue'	
	elif request.args['fromUrl'] == 'mainPage':
		return '.mainPage'
	else:
		return '.mainPage'	

def updateCustomer(form, customerDB, username2customerID):
	logger.debug(type(form['username']))
	logger.debug(type(username2customerID[form['username']]))
	logger.debug(username2customerID[form['username']])
	username2customerID[str(form['username'])] = int(form['add1'])
	customerDB[int(username2customerID[str(form['username'])])][0] = username2customerID[str(form['username'])]
	customerDB[int(username2customerID[str(form['username'])])][1] = str(form['username'])		
	customerDB[int(username2customerID[str(form['username'])])][2] = str(form['password'])
	customerDB[int(username2customerID[str(form['username'])])][3] = str(request.form['username']) + '@gmail.com'	
	logger.info('Create user [ ' + str(form['username']) + ' ]')
	return

def create_recommand_list(user_id, user_data, prod_clusters):
	# print (user_id)
	score_list = user_data[user_id]['scores']
	sort_list = np.argsort(np.array(score_list)).tolist()
	prod_list = []
	for i in range(10):
		prod_list.append(prod_clusters[sort_list[i]]['cluster_members'][random.randint(0, len(prod_clusters[sort_list[i]]['cluster_members']) - 1)])
	return prod_list

def like_prod(user_id, prod_id, user_data, user_clusters, prod_data, clusters_dis):
	# print (user_id, prod_id)
	prod_clu_id = prod_data[prod_id]['cluster_id']
	for idx in range(20):
		user_data[user_id]['scores'][idx] += (1 / clusters_dis[prod_clu_id][idx])
		user_clusters[user_data[user_id]['cluster_id']]['scores'][idx] += (1 / clusters_dis[prod_clu_id][idx])
	# print ('result : ' + str(user_clusters[user_data[user_id]['cluster_id']]['scores'][prod_clu_id]))

def create_app(configfile=None):
	logger.info('Loading user data...')
	
	customerDB = readPickle(os.path.join(data_dir, 'customerDB.pkl'))
	username2customerID = readPickle(os.path.join(data_dir, 'username2customerID.pkl'))
	user_data = readPickle(os.path.join(data_dir, 'user_data.pkl'))
	user_clusters = readPickle(os.path.join(data_dir, 'user_clusters.pkl'))

	logger.info('Loading product data...')
	prod_data = readJson(os.path.join(data_dir, 'new_fund.json'))
	prod_clusters = readJson(os.path.join(data_dir, 'cluster_centers.json'))
	clusters_dis = getClusterDist(prod_clusters)

	logger.info('Loading expert data...')
	expert_data = readJson(os.path.join(data_dir, 'financial_commissioner.json'))
	
	logger.info('Loading finished')
	
	app = Flask(__name__, static_url_path='/src/static')
	app.jinja_env.add_extension("chartkick.ext.charts")
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
		if request.method == 'POST':
			logger.debug(request.form)

			if str(request.form['username']) in username2customerID:
				return render_template('registerForm.html', fromUrl=request.args['fromUrl'])
			updateCustomer(request.form, customerDB, username2customerID)
			session['isLogin'] = json.dumps(request.form)
			return redirect(url_for(redirectUrl()))
		return render_template('registerForm.html', fromUrl=request.args['fromUrl'])

	@app.route('/login', methods=('GET', 'POST'))
	def login():
		form = LoginForm()
		if request.method == 'POST' and form.validate_on_submit():
			username = str(form.username.data)
			password = str(form.password.data)
			logger.debug(username in username2customerID)
			if username in username2customerID and password == str(customerDB[int(username2customerID[username])][2]):
				logger.debug(customerDB[username2customerID[username]])
				# print('[INFO]:login --> username ( ' + form.username.data + ' ) confirmed')
				logger.info('Username [ ' + username + ' ] login')
				session['isLogin'] = json.dumps(request.form)
				# customer = [username, username2customerID[username]]
			return redirect(url_for(redirectUrl()))
			
		return render_template('login.html', form=form)
	@app.route('/personalStatus')
	def personalStatus():
		data = {'isLogin' : True if 'isLogin' in session else False}
		if 'isLogin' not in session:
			return redirect(url_for('.mainPage'))
		return render_template('personalStatus.html', data=data)
	
	@app.route('/history')
	def history():
		if 'isLogin' not in session:
			return redirect(url_for('.mainPage'))
		data = {'isLogin' : True, 'listIdx' : 10}
		if json.loads(session['isLogin'])['username'] not in username2customerID:
			user_id = int(json.loads(session['isLogin'])['customer_id'])
		else:
			user_id = username2customerID[json.loads(session['isLogin'])['username']]
		logger.info('Username : ' + json.loads(session['isLogin'])['username'] + ' , ID : ' + str(user_id))
		prod_list = create_recommand_list(user_id, user_data, prod_clusters)[:5]
		logger.info('Generate history product ID:')
		logger.info(prod_list)
		product_dict = {}
		for idx in range(5):
			fromData = randomDate(str(idx + 1) + '/1/200' + str(idx + 1), str(idx + 3) + '/1/200' + str(idx + 1), random.random())
			toData = randomDate(str(idx + 3) + '/1/200' + str(idx + 1), str(idx + 7) + '/1/200' + str(idx + 1), random.random())
			product_dict[idx] = prod_data[prod_list[idx]]
			product_dict[idx]['from'] = fromData
			product_dict[idx]['end'] = toData
			product_dict[idx]['revenue'] = float((random.randint(0, 400) - 200)) / 10 
			
		return render_template('history.html', data=data, products=product_dict)

	@app.route('/')
	def mainPage():
		data = {'isLogin' : True if 'isLogin' in session else False}
		logger.info('Login status : ' + 'Login' if data['isLogin'] else 'Not login')
		logger.info('Switch to main page')
		return render_template('index.html', data=data)
	
	@app.route('/hotissue')
	def hotIssue():
		data = {'isLogin' : True if 'isLogin' in session else False}
		logger.info('Login status : ' + 'Login' if data['isLogin'] else 'Not login')
		logger.info('Switch to hot issue page')
		return render_template('hotissue.html', data=data)
	
	@app.route('/logout')
	def logout():
		logger.info('Username [ ' + json.loads(session['isLogin'])['username'] + ' ] logout')
		session.pop('isLogin', None)
		return redirect(url_for(redirectUrl()))

	@app.route('/productRank')
	def productRank():
		if 'isLogin' not in session:
			return redirect(url_for('.mainPage'))
		logger.info('Switch to product rank page')
		data = {'isLogin' : True, 'listIdx' : 10}
		if json.loads(session['isLogin'])['username'] not in username2customerID:
			user_id = int(json.loads(session['isLogin'])['customer_id'])
		else:
			user_id = username2customerID[json.loads(session['isLogin'])['username']]
		if 'isRefresh' in request.args and request.args['isRefresh'] == 'no':
			if 'listIdx' in request.args:
				listIdx = int(request.args['listIdx'])
				product_dict = ast.literal_eval(request.args['productDict'])
				like_prod(user_id, product_dict[listIdx]['id'], user_data, user_clusters, prod_data, clusters_dis)
				logger.info('User ID [ ' + str(user_id) + ' ] likes product ID [ ' + str(product_dict[listIdx]['id']) + ' ] from cluster [ ' + str(product_dict[listIdx]['cluster_id']) + ' ]')
				logger.info('Product cluster scores:')
				logger.info(user_data[user_id]['scores'])
				return render_template('productRank.html', products=product_dict, data=data)
			elif 'productIdx' in request.args:
				data['listIdx'] = int(request.args['productIdx'])
				product_dict = ast.literal_eval(request.args['productDict'])
				logger.info('Product ID [ ' + str(product_dict[data['listIdx']]['id']) + ' ] selected.')
				return render_template('productRank.html', products=product_dict, data=data)
		logger.info('Username : ' + json.loads(session['isLogin'])['username'] + ' , ID : ' + str(user_id))
		prod_list = create_recommand_list(user_id, user_data, prod_clusters)
		logger.info('Generate recommended product ID:')
		logger.info(prod_list)
		product_dict = {}
		for idx in range(10):
			product_dict[idx] = prod_data[prod_list[idx]]
		return render_template('productRank.html', products=product_dict, data=data)
	
	@app.route('/expertRank')
	def expertRank():
		if 'isLogin' not in session:
			return redirect(url_for('.mainPage'))
		logger.info('Switch to expert rank page')
		data = {'isLogin' : True}
		if json.loads(session['isLogin'])['username'] not in username2customerID:
			user_id = int(json.loads(session['isLogin'])['customer_id'])
		else:
			user_id = username2customerID[json.loads(session['isLogin'])['username']]
		expert_dict = match(expert_data, user_id, user_data, prod_data, prod_clusters)
		logger.info('Username : ' + json.loads(session['isLogin'])['username'] + ' , ID : ' + str(user_id))
		logger.info('Generate recommended financial commissioner ID:')
		logger.info([key for key in expert_dict])
		logger.info('Successful experience with product ID:')
		logger.info([[item['id'] for item in expert_dict[key]['top5']] for key in expert_dict])
		return render_template('expertRank.html', experts=expert_dict, data=data)
	return app

if __name__ == '__main__':
	logger.info('Start the server')
	create_app().run(debug=True)
