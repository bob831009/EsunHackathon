import json
import numpy
import math

def match(input_fileName, client_top5):
	alpha = 0.7;
	beta = 0.3;
	financial_commissioners = [];
	score = [];
	with open(input_fileName) as f:
		financial_commissioners = json.load(f);
	for fc_top5 in financial_commissioners:
		tmp_score = 0;
		for i in range(len(client_top5)):
			if(client_top5[i] in fc_top5):
				tmp_score += (alpha * 1.0/(i+1) + beta * 1.0/(fc_top5.index(client_top5[i]) + 1));
			
		score.append(tmp_score);
	sorted_score = sorted(score, reverse=True);
	sorted_index = sorted(range(len(score)), key=lambda k: score[k], reverse=True);

match('financial_commissioner.json', [0, 1, 2, 3, 4]);