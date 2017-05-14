import csv
import pickle
import os

def readFile(fin):
	with open(fin) as file:
		data = file.read()
	return data.splitlines()

def readPickle(fin):
	with open(fin, 'rb') as file:
		data = pickle.load(file)
	return data

def writePickle(fout, data):
	with open(fout, 'wb') as file:
		pickle.dump(data, file)

def readCSV(fin):
	with open(fin, 'r') as file:
		content = list(csv.reader(file, delimiter=',', quotechar='"'))
	return content

	