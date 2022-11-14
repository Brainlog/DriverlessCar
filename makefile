est:
	python3 drive.py -d -k $(cars) -l $(layout)  -a -i estimator
none:
	python3 drive.py -d -k $(cars) -l $(layout) -a -i none
inti:
	python3 drive.py -m -d -k $(cars) -l $(layout) -a -i estimator -j
con:
	conda activate assign3
# make cars=12 layout=small none 
# dont use gap




