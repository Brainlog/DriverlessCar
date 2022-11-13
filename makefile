est:
	python3 drive.py -d -k $(cars) -l $(layout) -a -i estimator
none:
	python3 drive.py -d -k $(cars) -l $(layout) -a -i none
int:
	python3 drive.py -d -k $(cars) -l $(layout) -a -i estimator -j
git:
	git add .
	git commit -m "update"
	git push -u origin master
# make cars=12 layout=small none 
# dont use gap




