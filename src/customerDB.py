from utils import *
import os

customer_size = 200000

root_dir = './'
data_dir = os.path.join(root_dir, 'data')

nameFile = os.path.join(data_dir, 'nameList.txt')
infoFile = os.path.join(data_dir, 'customers.csv')
foutInfo = os.path.join(data_dir, 'customerDB.pkl')
foutMap = os.path.join(data_dir, 'username2customerID.pkl')

def createDB():
	
	nameList = readFile(nameFile)
	infoList = readCSV(infoFile)[1:]
	
	customerData = [None] * customer_size
	username2customerID = {}
	
	for i in range(customer_size):
		username = nameList[i % 4275].split(' ')[0].lower() + str(i / 4275 + 1)
		password = '123'
		email = username + '@gmail.com'
		customerID = int(infoList[i][0])
		feature = infoList[i][1:]
		username2customerID[username] = customerID
		customerData[i] = [customerID, username, password, email, feature]
	writePickle(foutInfo, customerData)
	writePickle(foutMap, username2customerID)
	#	username2customerID['mary1'] = 1
	#	customerData[0] = [1, 'mary1', 123, 'mary1@gmail.com', ['F', 'N', 'N', 'N', 'Y', 'N', 'Y', 'N', 'N', '9', '1']]
def getCustomerDB():
	if not os.path.exists(foutMap) or not os.path.exists(foutInfo):
		print('[INFO]:getCustomerDB --> create map and info')
		createDB()
	return readPickle(foutInfo)	

def getUsername2CustomerIdx():
	if not os.path.exists(foutMap) or not os.path.exists(foutInfo):
		print('[INFO]:getUsername2CustomerIdx --> create map and info')
		createDB()
	return readPickle(foutMap)	



if __name__ == '__main__':
	createDB()