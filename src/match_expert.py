import numpy as np
import math
import random

def match(financial_commissioners, user_id, user_data, prod_data, prod_clusters):
	score_list = user_data[user_id]['scores']
	sort_list = np.argsort(np.array(score_list)).tolist()
	client_top5 = []
	for i in range(5):
		client_top5.append(prod_clusters[sort_list[i]]['id'])
	alpha = 0.7;
	beta = 0.3;
	score = [];
	
	for fc_info in financial_commissioners:
		fc_top5 = fc_info['top5'];
		tmp_score = 0;
		for i in range(len(client_top5)):
			if(client_top5[i] in fc_top5):
				tmp_score += (alpha * 1.0/(i+1) + beta * 1.0/(fc_top5.index(client_top5[i]) + 1));
			
		score.append(tmp_score);
	sorted_score = sorted(score, reverse=True);
	sorted_index = sorted(range(len(score)), key=lambda k: score[k], reverse=True);
	top5_fc_index = sorted_index[:5];
	top5_fc_info = {};
	for index in top5_fc_index:
		top5_fc_info[index] = financial_commissioners[index].copy();
	for key in top5_fc_info:
		top5 = top5_fc_info[key]['top5']
		prod_list = []
		for j in range(3):
			prod_id = prod_clusters[top5[j]]['cluster_members'][random.randint(0, len(prod_clusters[top5[j]]['cluster_members'])-1)]
			prod_list.append(prod_data[prod_id])
		top5_fc_info[key]['top5'] = prod_list
	return top5_fc_info;

# match('../data/financial_commissioner.json', [0, 1, 2, 3, 4]);