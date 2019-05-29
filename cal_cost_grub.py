#!/usr/bin/python2.7
import sys

THRESHOLD = 2 		    # the number of consecutive read operations that triggers replication action
cost = [41158, 37324, 40241, 27375] # W, R_OFF_NOREPLICATE, R_OFF_REPLICATE, R_ON
counter={}
replica={}

# whenever a write is issued, reset the counter to be 0
def reset(_key):
	counter[_key] = 0
	replica[_key] = False 

def read_offchain(_key):
	return not replica[_key]

# whenever a read is issued, increase the counter by 1
def replicate_decision(_key):
	if _key in counter:
		counter[_key] += 1
	else:
		counter[_key] = 0

	if counter[_key] >= THRESHOLD:
		print "R_OFF_R"
		replica[_key] = True
		return True
	else:
		print "R_OFF_NR"
		replica[_key] = False 
		return False

def calculate(_key, _write, _total_cost):
	if (_write):
		_total_cost += cost[0] # W
		reset(_key);
	else:
		if read_offchain(_key):
			if not replicate_decision(_key):
				_total_cost += cost[1] #R_OFF_NOREPLICATE
			else:
				_total_cost += cost[2] #R_OFF_REPLICATE
		else:
			print "R_ON"
			_total_cost += cost[3]         #R_ON
	return _total_cost

def scan(_FILE):
	FILE = open(_FILE, 'r')
	total_cost = 0
	for line in FILE:
        	record = line.strip('\n').split('\t')
		key = record[0]
		value = record[1]
		if record[4]=="W":
			print "W"
			write = True
		else:
			write = False
		total_cost = calculate(key, write, total_cost)
	print total_cost
        FILE.close()

##################
####   main   ####
##################

if (len(sys.argv) < 2 ):
	print "Usage: ./scan.py logfile"
	exit()
log =sys.argv[1]
scan(log);
