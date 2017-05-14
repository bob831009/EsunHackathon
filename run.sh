#! /bin/bash


if [ $1 == "demo" ]; 
then
	python src/esunBackend.py
elif [ $1 == "user" ];
then
	python src/createCustomerDB.py 
fi

