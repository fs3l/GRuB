#!/usr/bin/python2.7
import sys

THRESHOLD = 2 		    # the number of consecutive read operations that triggers replication action
cost = [41158, 37324, 40241, 27375] # W, R_OFF_NOREPLICATE, R_OFF_REPLICATE, R_ON
replica={}

# whenever a write is issued, reset the counter to be 0
def reset(_key):
	replica[_key] = False 

# always replicate
def calculate(_key, _write, _total_cost):
	if (_write):
		_total_cost += cost[0] # W
		reset(_key);
	else:
		print "R_OFF"
		_total_cost += cost[2]         #R_OFF

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
scan(log)
