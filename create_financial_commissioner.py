import random
import json

CATEGORY_NUM = 20;
COMMISSIONER_NUM = 40;
TOP_NUM = 5;
output_fileName = 'financial_commissioner.json'

res = [];
for i in range(COMMISSIONER_NUM):
	tmp_top5 = random.sample(range(CATEGORY_NUM), TOP_NUM);
	res.append(tmp_top5);

with open(output_fileName, 'w') as f:
	json.dump(res, f);