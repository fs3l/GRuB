#!/usr/bin/python2.7
import sys

THRESHOLD = 2 		    # the number of consecutive read operations that triggers replication action
cost = [41158, 37324, 40241, 27375] # W, R_OFF_NOREPLICATE, R_OFF_REPLICATE, R_ON
content=[]
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

	if counter[_key] > THRESHOLD:
		print "R_OFF_R"
		replica[_key] = True
		return True
	else:
		print "R_OFF_NR"
		replica[_key] = False 
		return False

def _calculate(_key, _write, _total_cost):
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

def forward_search(_key, _i, _length, _consecutive_read):
	for j in range(_i+1, _length, 1):
		next_record = content[j].strip('\n').split('\t')
		key = next_record[0]
		value = next_record[1]
		if next_record[4]=="W":
			return False
		else:
			_consecutive_read += 1
			if _consecutive_read >= THRESHOLD: 
				_consecutive_read=0
				return True
	return False

def calculate(_FILE):
	total_cost = 0
	FILE = open(_FILE, 'r')
	for line in FILE:
		content.append(line);
	length = len(content)
	last_decision=False;
	consecutive_read = 0
        for i in range(length):
        	record = content[i].strip('\n').split('\t')
		key = record[0]
		value = record[1]
		if record[4]=="W":
			print "W"
			total_cost += cost[0] # W
			write = True
			last_decision = False
			consecutive_read=0
		else:
			write = False
			consecutive_read += 1
			if last_decision:
				print 'R: consecutive read, no need to forward search'
				total_cost += cost[3]         #R_ON
			else:
				last_decision = forward_search(key, i, length, consecutive_read)
				if last_decision:
					print 'R: should be replicated'
					total_cost += cost[2] #R_OFF_REPLICATE
				else:
					print 'R: #successor reads is less than THRESHOLD'
					total_cost += cost[1] #R_OFF_NOREPLICATE
	print total_cost
        FILE.close()

##################
####   main   ####
##################

if (len(sys.argv) < 2 ):
	print "Usage: ./scan.py logfile"
	exit()
log =sys.argv[1]

calculate(log);
