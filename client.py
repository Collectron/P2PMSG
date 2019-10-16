import sys, glob, os, random, datetime, subprocess, pause

# add path with Apache Thrift compiler generated files
sys.path.append('gen-py')
# add path where built Apache Thrift libraries are
sys.path.insert(0, glob.glob('~/thrift-0.10.0/lib/py/build/lib.*'))

from myfirst import AuthorizationService
from myfirst import MainService
from myfirst.ttypes import *
from myfirst.constants import *

from time import sleep, time
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

MIN_NUMBER_OF_NODES = 3 # Min number of noes that the Client needs to know

# Function to notify the Network that a Node is not responding
def Stochastic_not_responding(node_list, non_responding_node):
	tries=0
	while True:
		rand = random.randint(0,len(node_list)-1)
		try:
			transport = TSocket.TSocket(node_list[rand].IPaddress.split(':')[0], node_list[rand].IPaddress.split(':')[1])
			transport = TTransport.TBufferedTransport(transport)
			protocol = TBinaryProtocol.TBinaryProtocol(transport)
			connection = MainService.Client(protocol)
			transport.open()
			response = connection.nodeDidNotRespond(non_responding_node)
			transport.close()
		except:
			tries+=1
			if tries==10: # m>= ln(1/delta)/ln(#Nodes/#Cushed_Nodes)   delta:0.001 , #Nodes/#Crushed_Nodes: 2
				return "Connection Lost"
			else:
				continue
		return response

def StochasticRefreshNetworkNodes(node_list):
	# Clients refreshes his NodeList if it knows to few Nodes of the Network
	while True:
		rand = random.randint(0,len(node_list)-1)
		try:
			transport = TSocket.TSocket(node_list[rand].IPaddress.split(':')[0], node_list[rand].IPaddress.split(':')[1])
			transport = TTransport.TBufferedTransport(transport)
			protocol = TBinaryProtocol.TBinaryProtocol(transport)
			connection = MainService.Client(protocol)
			transport.open()
			node_list = connection.giveNodesInfo()
			transport.close()
		except:
			if Stochastic_not_responding(node_list, node_list[rand]) == "Connection Lost" :
				print("CONNECTION LOST.")
				sys.exit()
			continue
		break
	return node_list

if __name__ == '__main__':

	userName = input("Choose your name : ")
	filename="conversation_"+userName+".txt"

	# # # # # # # # # # # # # AUTH SERVER CODE ADDED HERE # # # # # # # # # # # ## 
	input1 = input("Would you like to register or sign in? {R/S}: ")
	if input1 == "R" or input1 == "r":
		passw = input("Please, enter your password: ")
		transport = TSocket.TSocket("localhost", "1337")
		transport = TTransport.TBufferedTransport(transport)
		protocol = TBinaryProtocol.TBinaryProtocol(transport)
		connection = AuthorizationService.Client(protocol)
		transport.open()
		bool_ans = connection.registerRequest(userName, passw)
		if bool_ans:
			bool_ans2 = connection.loginRequest(userName, passw)
			if bool_ans2:
				print(connection.giveNetworksInfo(userName))
				NetworkNodes = connection.giveNodesInfo(userName, input("Please select the network number: "))
				transport.close()
			else:
				transport.close()
				print("User already logged in")
				sys.exit()	
		else:
			transport.close()
			print("User already registered")
			sys.exit()

	elif input1 == "S" or input1 == "s":
		passw = input("Please, enter your password: ")
		transport = TSocket.TSocket("localhost", "1337")
		transport = TTransport.TBufferedTransport(transport)
		protocol = TBinaryProtocol.TBinaryProtocol(transport)
		connection = AuthorizationService.Client(protocol)
		transport.open()
		bool_ans2 = connection.loginRequest(userName, passw)
		if bool_ans2:
			print(connection.giveNetworksInfo(userName))
			NetworkNodes = connection.giveNodesInfo(userName, input("Please select the network number: "))
			transport.close()
		else:
			transport.close()
			print("User already logged in")
			sys.exit()
	else:
		print("WRONG INPUT!")

	# # # # # # # # # # # # # AUTH SERVER CODE STOPS HERE # # # # # # # # # # # ## 


	# Client connects to the given Node to get the NodeList of the Network
	try:
		transport = TSocket.TSocket(NetworkNodes[0].IPaddress.split(':')[0], NetworkNodes[0].IPaddress.split(':')[1])
		transport = TTransport.TBufferedTransport(transport)
		protocol = TBinaryProtocol.TBinaryProtocol(transport)
		connection = MainService.Client(protocol)
		transport.open()
		NetworkNodes = connection.giveNodesInfo()
		transport.close()
	except:
		print("The is no such Node running right now")
		print("CONNECTION LOST.")
		sys.exit()

	# Subprocess for printing Conversation. (instead of UI) :( 
	pid = subprocess.Popen([sys.executable, "RefreshConversation.py"]+[NetworkNodes[0].IPaddress.split(':')[0],NetworkNodes[0].IPaddress.split(':')[1],userName,filename])

	while True:
		
		# Create a new Message to send to the Network.
		msg = Message()	
		msg.textOfMessage = input(userName+": ")

		# Update your info of the Net
		#NetworkNodes=RefreshNetworkNodes(NetworkNodes)
		NetworkNodes=StochasticRefreshNetworkNodes(NetworkNodes)

		while True:
			# Client sends to the Synchronizer it's message.
			try:
				Panel_ip, Panel_port = NetworkNodes[0].IPaddress.split(':')
				transport = TSocket.TSocket(Panel_ip, Panel_port)
				transport = TTransport.TBufferedTransport(transport)
				protocol = TBinaryProtocol.TBinaryProtocol(transport)
				connection = MainService.Client(protocol)
				transport.open()
				
				msg.IPaddress = userName
				msg.timeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
				pause.until(datetime.datetime(2017,9,19,18,38,0,0))
				Panels_responce = connection.sendMessage(msg)
				transport.close()

			except:
				# in case of no responce
				response = Stochastic_not_responding(NetworkNodes, NetworkNodes[0])
				if response == "Connection Lost":
					print("CONNECTION LOST.")
					sys.exit()
				else:
					if response == "Removed":
						NetworkNodes.remove(NetworkNodes[0])
					#NetworkNodes=RefreshNetworkNodes(NetworkNodes)
					NetworkNodes=StochasticRefreshNetworkNodes(NetworkNodes)
				continue

			# In case the Synchronizer has changed while sending the message. 
			# Higly unlikely, but the thing about fault tolerance is that you can never have to much...
			if Panels_responce != "DO IT":
				#NetworkNodes=RefreshNetworkNodes(NetworkNodes)
				NetworkNodes=StochasticRefreshNetworkNodes(NetworkNodes)
				continue
			break

		# After sending the message to the Synchronizer, the client sends it to everyone else.
		for Node in NetworkNodes:
			if Node.nodeName == NetworkNodes[0].nodeName:
				continue
			try:
				transport = TSocket.TSocket(Node.IPaddress.split(':')[0], Node.IPaddress.split(':')[1])
				transport = TTransport.TBufferedTransport(transport)
				protocol = TBinaryProtocol.TBinaryProtocol(transport)
				connection = MainService.Client(protocol)
				transport.open()
				Panels_responce = connection.sendMessage(msg) # connection.ReceiveMessage(msg)
				transport.close()
			except:
				print("Node "+Node.nodeName+" couldn't receive my the message. The Synchronizer will find it out!")