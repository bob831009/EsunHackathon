import tensorflow as tf
import csv
import random
import numpy as np
import json

gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.1)
sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))

# data features
customer_data = []
with open('../data/customers.csv', 'r') as f:
	data = csv.reader(f)
	for d in data:
		customer_data.append(d)

customer_data = customer_data[1:]

print len(customer_data)

for c in customer_data:
	#c[0] = int(c[0])
	if c[1] == 'F':
		c[1] = 0.
	elif c[1] == 'M':
		c[1] = 1.
	for j in range(2, 10):
		if c[j] == 'N':
			c[j] = 0.
		elif c[j] == 'Y':
			c[j] = 1.
	c[10] = float(c[10])
	c[11] = float(c[11])
	# id = index+1
	c.pop(0)

data_vectors = customer_data
init_n = 50000
init_users = data_vectors[:init_n]
follow_users = data_vectors[init_n:]

# data structure
num_prod_clusters = 20

num_vectors = 200000
num_clusters = 20
num_steps = 100
num_dims = 11

user_data = []
for i in range(num_vectors):
	user_tmp = dict()
	user_tmp['user_id'] = i
	user_tmp['features'] = data_vectors[i]
	if (i < init_n):
		user_tmp['scores'] = [round(random.uniform(0, 10), 3) for j in range(num_prod_clusters)]
	else:
		user_tmp['scores'] = [0. for j in range(num_prod_clusters)]
	user_tmp['cluster_id'] = -1
	user_data.append(user_tmp)

user_clusters = []
for i in range(num_clusters):
	cluster_tmp = dict()
	cluster_tmp['cluster_id'] = i
	cluster_tmp['user_ids'] = []
	cluster_tmp['scores'] = [0. for j in range(num_prod_clusters)]
	user_clusters.append(cluster_tmp)

# k-means
#vectors = tf.constant(init_users)
#random_indices = tf.random_shuffle(tf.range(0, num_vectors))
#centroid_indices = tf.slice(random_indices, [0,], [num_clusters,])
#init_centroids = tf.Variable(tf.gather(data_vectors, centroid_indices))
init_centroids = tf.Variable(init_users[:num_clusters])

centroids = tf.placeholder('float32', [num_clusters, num_dims])
vectors = tf.placeholder('float32', [None, num_dims])

expanded_vectors = tf.expand_dims(vectors, 0)
expanded_centroids = tf.expand_dims(centroids, 1)

vectors_sub = tf.subtract(expanded_vectors, expanded_centroids)
distances = tf.reduce_sum(tf.square(vectors_sub), 2)
assignments = tf.to_int32(tf.argmin(distances, 0))

partitions = tf.dynamic_partition(vectors, assignments, num_clusters)
update_centroids = tf.concat([tf.expand_dims(tf.reduce_mean(partition, 0), 0) for partition in partitions], 0)

# session
init = tf.initialize_all_variables()
sess = tf.Session()
sess.run(init)

new_centroids = sess.run(init_centroids)
for step in xrange(num_steps):
	print step
	#tmp = sess.run(update_centroids)
	#print tmp
	new_centroids, assignment_values = sess.run([update_centroids, assignments], feed_dict={centroids: new_centroids, vectors: init_users})
	#print new_centroids
	#print len(assignment_values)

# updata data
current_centroids = new_centroids

for i in range(len(assignment_values)):
	user_data[i]['cluster_id'] = assignment_values[i]
	user_clusters[assignment_values[i]]['user_ids'].append(i)

for i in range(len(user_clusters)):
	for j in user_clusters[i]['user_ids']:
		user_clusters[i]['scores'] = np.add(user_clusters[i]['scores'], user_data[j]['scores'])

new_centroids, assignment_values = sess.run([update_centroids, assignments], feed_dict={centroids: current_centroids, vectors: follow_users})
#print len(assignment_values)

for i in range(len(assignment_values)):
	user_data[init_n + i]['cluster_id'] = assignment_values[i]
	user_clusters[assignment_values[i]]['user_ids'].append(init_n + i)

#print user_data[100000]
for i in range(num_clusters):
	print user_clusters[i]['scores'], len(user_clusters[i]['user_ids'])

with open('user_data.txt', 'w') as f_user:
	#json.dumps(user_data, f_user)
	for user in user_data:
		f_user.write(str(user))

with open('user_clusters.txt', 'w') as f_cluster:
	#json.dumps(user_clusters, f_cluster)
	for cluster in user_clusters:
		f_cluster.write(str(cluster))


