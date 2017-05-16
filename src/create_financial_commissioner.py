import random
import json

CATEGORY_NUM = 20;
COMMISSIONER_NUM = 20;
TOP_NUM = 5;
output_fileName = '../data/financial_commissioner.json'
total_name = [];
with open('../data/nameList.txt') as f:
	for line in f:
		line = line.strip().split(' ');
		name = line[0];
		total_name.append(name);

res = [];
for i in range(COMMISSIONER_NUM):
	commissioner_info = {};
	tmp_top5 = random.sample(range(CATEGORY_NUM), TOP_NUM);
	commissioner_info['top5'] = tmp_top5;
	commissioner_info['id'] = i;
	commissioner_info['name'] = total_name[i];
	commissioner_info['profile_path'] = '../data/financial_commissioner_image/%d.jpg'%(i);
	commissioner_info['seniority'] = 5;
	res.append(commissioner_info);

with open(output_fileName, 'w') as f:
	json.dump(res, f, indent=4);