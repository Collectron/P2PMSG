// namespaces are used in resulting packages
namespace py myfirst
namespace java myfirst

const double PI = 3.1415926
const double e = 2.718281828459

typedef i32 int
// typedef map<string,list<string>> Dict

struct Node {
    1: string IPaddress,
    2: string nodeName
}

exception MyError {
    1: int error_code,
    2: string error_description
}

struct Message {
    1: string textOfMessage,
    2: string IPaddress,
    3: string timeStamp
}


typedef list<Node> NodeList
typedef list<Message> MessageList

// here starts the service definition
service MainService {

    // The client calls this method from the Synchronizer, to send a message to the Network
    string sendMessage(1:Message Msg) throws (1:MyError error),

    // giving info of User
    //map<string, User> giveUsersInfo() throws (1:MyError error),
    NodeList giveNodesInfo() throws (1:MyError error),

    string updateNodes(1:int action, 2:Node node) throws (1:MyError error),

    oneway void printNodes(),
	
    // Message confirmation, send by nodes to panel
    oneway void AcceptedMessage(1:string MessageId),

    // removing a node from the nertwork
    int removeNode(1:Node node) throws (1:MyError error),

    // The subprocess of the Synchronizer validates the message
    string ValidateMessage(1:string key) throws (1:MyError error),

    // Send message/transaction to node 
    int ReceiveMessage(1:Message Msg) throws (1:MyError error),

    // The name says it all
    string sendConversation() throws (1:MyError error),

    // The name says it all
    list<string> updateConversation(1: int currentMessageLine) throws (1:MyError error),

    // Checking if a Node is up and running
    string checkIfNodeIsUp() throws (1:MyError error),

    // Refresh the conversation of the Node 
    string refreshYourConversation() throws (1:MyError error),

    // called by subprocess of Synchronizer for message Queuing
    string sendMessageToProcess(1:string key, 2:NodeList NdLst) throws (1:MyError error),

    // called from client when someone does not respond to fix their nodeList
    string nodeDidNotRespond(1:Node nodeThatWentWrong) throws(1:MyError error),

    // append key of Message to list of Node
    int AppendToListNode(1:string key) throws(1:MyError error),

    // request connection
    oneway void pingMe(1:Message msg),
    
    // send NodeList
    int sendListNodes(1:NodeList lst) throws(1:MyError error),

    // make someone replace their conversation with what you gave them
    oneway void getConversation(1:string conv),

    // ask new panelist to open his subprocess,
    oneway void popen(),

    // the next synchronizer sends the critical message to all 
    int getLastMessage(1:Message msg) throws(1:MyError error),

    int flushYourList() throws(1:MyError error)
}

// here starts the service definition
service AuthorizationService {
	
	// register request from client
	bool registerRequest(1:string Username, 2:string Password) throws (1:MyError error),

	// login request from client
	bool loginRequest(1:string Username, 2:string Password) throws (1:MyError error),

	// logout request from client
	bool logoutRequest(1:string Username) throws (1:MyError error),

	// give Nodes Info about the chosen network
    NodeList giveNodesInfo(1:string Username, 2:string choice) throws (1:MyError error),

    // give me the networks that are available to me
    string giveNetworksInfo(1:string Username) throws (1:MyError error),

    // register request from network
    int registerNetwork(1:NodeList nodeList) throws (1:MyError error),

    // network nodes update
    bool updateNetwork(1:int networkID, 2:NodeList nodeList) throws (1:MyError error)

}
