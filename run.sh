#! /bin/bash

root_dir=.
data_dir=${root_dir}/data
src_dir=${root_dir}/src
log_dir=${root_dir}/log

customer_info=${data_dir}/customerDB.pkl
customer_map=${data_dir}/username2customerID.pkl

user_data=${data_dir}/user_data.pkl
user_cluster=${data_dir}/user_clusters.pkl

prod_data=${data_dir}/new_fund.json
prod_cluster=${data_dir}/cluster_centers.json


if [ $1 == "demo" ]; then
	python ${src_dir}/esunBackend.py

elif [ $1 == "data" ]; then
	if [ ! -f $customer_info ] || [ ! -f $customer_map ]; then
		python ${src_dir}/customerDB.py
	fi
	if [ ! -f $user_data ] || [ ! -f $user_cluster ]; then 
		python ${src_dir}/customer_kmeans.py
	fi
	if [ ! -f $prod_data ] || [ ! -f $prod_cluster ]; then
		python ${src_dir}/product_kmeans.py
	fi

elif [ $1 == "clean" ]; then
	rm -rf ${log_dir}/*

fi

