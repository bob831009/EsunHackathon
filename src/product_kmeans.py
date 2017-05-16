#coding=utf-8
from sklearn.cluster import KMeans
import numpy as np
import json
import io
import sys

# sys.setdefaultencoding('UTF8');
def get_unicode_info(dic, key):
	return dic[key.decode('utf-8')];


def remove_shit(a):
	if(len(a) == 0):
		return '0';
	for i in range(len(a)):
		if(not (a[i].isdigit() or a[i] == '.')):
			if(i == 0):
				return '0';
			return a[:i];
	return a;

def hash_invest_region(total_invest_region, region):
	if(not region in total_invest_region):
		total_invest_region.append(region);
	return total_invest_region.index(region);

def check_NA(a):
	if(a == 'N/A'):
		return '0.0';
	else:
		return a;

def handling_scale(currency_conversion, scale):
	scale = scale.strip();
	if(len(scale) == 0):
		return 0.0;
	num = float(remove_shit(scale));
	dollar_catg = scale[scale.index('(') + 1:scale.index(')')];
	num = num * currency_conversion[dollar_catg];
	return num;

def handle_cluster_center(arr):
	res = [];
	for i in range(len(arr)):
		data = arr[i];
		center_info = {
			'id': i,
			'least_buy': data[0],
			'net_worth': data[1],
			'main_invest_region': data[2],
			'risk_beta': data[3],
			'return_on_investment_3month': data[4],
			'return_on_investment_6month': data[5],
			'return_on_investment_1year': data[6],
			'return_on_investment_3year': data[7],
			'risk_return_level': data[8],
			'established_scale': data[9],
			'scale': data[10],
			'risk_standard_deviation': data[11],
			'fee': data[12]
		}
		res.append(center_info);
	return res;



customer_data = []
fund_datas = []
with open('../data/fund.json') as f:
	fund_datas = json.load(f);
	
features = [];
total_invest_region = [];
currency_conversion = {
	'台幣': 1,
	'人民幣': 4.35,
	'美元': 30,
	'南非幣': 2.3,
	'澳幣': 22.3,
	'¥x¹ô': 0,
	'歐元': 33,
	'紐幣': 20.5
}
for fund_info in fund_datas:
	tmp_feature = [];
	
	least_buy = fund_info['單筆最低申購'][:-1].strip().replace(',', '');
	least_buy = int(remove_shit(least_buy));
	
	net_worth = float(check_NA(fund_info['淨值']));
	main_invest_region = hash_invest_region(total_invest_region, fund_info['主要投資區域']);
	risk_beta = float(check_NA(fund_info['風險beta']));
	return_on_investment_3month = float(check_NA(fund_info['報酬率3個月']));
	return_on_investment_6month = float(check_NA(fund_info['報酬率6個月']));
	return_on_investment_1year = float(check_NA(fund_info['報酬率1年']));
	return_on_investment_3year = float(check_NA(fund_info['報酬率3年']));


	risk_return_level = fund_info['風險報酬等級'];
	if(risk_return_level[0]=='R'): risk_return_level = int(risk_return_level[2]);
	else: risk_return_level = 6 + ['低波動度', '中波動度', '高波動度', 'N/A'].index(risk_return_level[:4]);

	established_scale = handling_scale(currency_conversion, fund_info['成立時規模']);
	scale = handling_scale(currency_conversion, fund_info['基金規模']);

	risk_standard_deviation = float(check_NA(fund_info['風險標準差']));
	fee = float(check_NA(fund_info['手續費(%)']));
	
	tmp_feature = [
		least_buy,
		net_worth,
		main_invest_region,
		risk_beta,
		return_on_investment_3month,
		return_on_investment_6month,
		return_on_investment_1year,
		return_on_investment_3year,
		risk_return_level,
		established_scale,
		scale,
		risk_standard_deviation,
		fee
	]
	features.append(tmp_feature);

X = np.array(features);
kmeans = KMeans(n_clusters=20, random_state=0).fit(X);
X_category = kmeans.labels_;
cluster_centers = handle_cluster_center(kmeans.cluster_centers_);

with open('../data/cluster_centers.json', 'w') as f:
	json.dump(cluster_centers, f, indent=1);

new_fund_datas = [];
for i in range(len(fund_datas)):
	fund_info = fund_datas[i];
	fund_info['id'] = i;
	fund_info['cluster_id'] = int(X_category[i]);
	new_fund_datas.append(fund_info);
with open('../data/new_fund.json', 'w') as f:
	json.dump(new_fund_datas, f, indent=1, ensure_ascii=False);

