import sys, glob, os, random, datetime, subprocess

# add path with Apache Thrift compiler generated files
sys.path.append('gen-py')
# add path where built Apache Thrift libraries are
sys.path.insert(0, glob.glob('~/thrift-0.10.0/lib/py/build/lib.*'))

from myfirst import MainService
from myfirst.ttypes import *
from myfirst.constants import *

from time import sleep, time
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

MIN_NUMBER_OF_NODES = 3

# Function to notify the Network that a Node is not responding
def not_responding(node_list, non_responding_node):
	for node in node_list:
		try:
			transport = TSocket.TSocket(node.IPaddress.split(':')[0], node.IPaddress.split(':')[1])
			transport = TTransport.TBufferedTransport(transport)
			protocol = TBinaryProtocol.TBinaryProtocol(transport)
			connection = MainService.Client(protocol)
			transport.open()
			response = connection.nodeDidNotRespond(non_responding_node)
			transport.close()
			return response
		except:
			continue
	return "Connection Lost"

def RefreshNetworkNodes(node_list):
	# Clients refreshes his NodeList if it knows to few Nodes of the Network
	for Node in node_list:
		try:
			transport = TSocket.TSocket(Node.IPaddress.split(':')[0], Node.IPaddress.split(':')[1])
			transport = TTransport.TBufferedTransport(transport)
			protocol = TBinaryProtocol.TBinaryProtocol(transport)
			connection = MainService.Client(protocol)
			transport.open()
			node_list = connection.giveNodesInfo()
			transport.close()
		except:
			if not_responding(node_list, Node) == "Connection Lost" :
				print("CONNECTION LOST.")
				sys.exit()
			continue
		break
	return node_list

if __name__ == '__main__':

	Polling_frequency=0.1

	try:
		transport = TSocket.TSocket(sys.argv[1], sys.argv[2])
		transport = TTransport.TBufferedTransport(transport)
		protocol = TBinaryProtocol.TBinaryProtocol(transport)
		connection = MainService.Client(protocol)
		transport.open()
		NetworkNodes = connection.giveNodesInfo()
		transport.close()
	except:
		print("CONNECTION LOST.")
		sys.exit()

	line_counter = 0
	while True:
		sleep(Polling_frequency) # Polling rate

		NetworkNodes=RefreshNetworkNodes(NetworkNodes)

		number_of_new_lines = 0
		rand = random.randint(0,len(NetworkNodes)-1)
		try:
			transport = TSocket.TSocket(NetworkNodes[rand].IPaddress.split(':')[0], NetworkNodes[rand].IPaddress.split(':')[1])
			transport = TTransport.TBufferedTransport(transport)
			protocol = TBinaryProtocol.TBinaryProtocol(transport)
			connection = MainService.Client(protocol)
			transport.open()
			temp = connection.updateConversation(line_counter)
			
			number_of_new_lines = len(temp)

			if number_of_new_lines>0:
				line_counter += number_of_new_lines
				file=open(sys.argv[4],'a')
				for line in temp:
					file.write(line)
				file.close()
					
			transport.close()
		except:
			response = not_responding(NetworkNodes, NetworkNodes[rand])	
			if response == "Connection Lost":
				print("CONNECTION LOST.")
				sys.exit()
			else:
				if response == "Removed":
					NetworkNodes.remove(NetworkNodes[rand])
				NetworkNodes=RefreshNetworkNodes(NetworkNodes)

		if number_of_new_lines>0:
			os.system('clear')
			file=open(sys.argv[4],'r')
			print(file.read())
			file.close()
			print("")
			print(sys.argv[3]+": ")
			Polling_frequency=0.1
		else:
			if(Polling_frequency<0.18):
				Polling_frequency+=0.01