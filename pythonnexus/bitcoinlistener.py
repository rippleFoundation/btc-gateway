import time
import json

from nexus import models
import config

from jsonrpc import ServiceProxy, JSONRPCException #Use this to communicate with the locally-running bitcoind instance.
from ws4py.client.threadedclient import WebSocketClient		

rpcuser=config.rpcuser
rpcpassword=config.rpcpassword
RIPPLE_WEBSOCKET_URL=config.RIPPLE_WEBSOCKET_URL
MY_RIPPLE_ADDRESS=config.MY_RIPPLE_ADDRESS
MY_SECRET_KEY=config.MY_SECRET_KEY


## INTERACTING WITH BITCOIN

bitcoin_connection = ServiceProxy("http://" + rpcuser + ":" + rpcpassword + "@127.0.0.1:8332")

def validate_bitcoin_address(address):
	return bitcoin_connection.validateaddress(address)["isvalid"]

def generate_bitcoin_address():
	while True:
		address = bitcoin_connection.getnewaddress()
		if models.BitcoinInEntry.objects.filter(bitcoin_address=address):
			print "Address already used; trying again" #Practically speaking, this will never happen.
		else:
			break
	return address

def amount_received_at_address(bitcoin_address):
	amount = bitcoin_connection.getreceivedbyaddress(bitcoin_address)
	print "Bitcoin address:", bitcoin_address
	print "Received:", amount
	return amount

def send_bitcoins_to(bitcoin_address, amount):
	try:
		x = bitcoin_connection.sendtoaddress(bitcoin_address, float(amount))
		print "Sent bitcoins"
	except JSONRPCException, e:
		raise Exception(repr(e.error))

		
## INTERACTING WITH RIPPLE
 
class IouClientConnector(WebSocketClient):
	connected = False
	
	def opened(self):
		self.connected = True
		print "Subscribe to messages about receiving Ripple IOUs."
		request = {
			'command'      : 'subscribe',
			'accounts'     : [ MY_RIPPLE_ADDRESS ],
			'username'     : rpcuser,
			'password'     : rpcpassword,
		}
		self.send(json.dumps(request))
		print "Tell the server to reject payments without a destination tag."
		request = {
			'command' : 'submit',
			'tx_json' : {
				'TransactionType' : 'AccountSet',
				'Flags'           : 65536,
				'Account'         : MY_RIPPLE_ADDRESS,
			},
			'secret'  : MY_SECRET_KEY,
		}
		self.send(json.dumps(request))

	def received_message(self, m):
		#Process message m, to see if we've received or sent Ripple IOUs.
		print m
		message = json.loads(str(m))
		if message["status"] == "error":
			if "error" in message                              \
			 and message["error"] == "dstActMalformed"         \
			 and "request" in message                          \
			 and "tx_json" in message["request"]               \
			 and "Destination" in message["request"]["tx_json"]:
				malformed_address = message["request"]["tx_json"]["Destination"]
				print "Error: Destination address is malformed. We will no longer try to send to this address.",\
				 "Whoever sent us Bitcoins and asked for IOUs to be sent to this Ripple address is out of luck."
				mark_as_done(malformed_address)
			else:
				print "Error: another kind of error occurred."
		elif message["status"] == "success":
			print "The message had a status of success, but we'll wait for the closing of the ledger to figure out what to do."
		elif message["status"] == "closed":
			if message["engine_result"]=="tesSUCCESS"                  \
			 and message["type"] == "account"                          \
			 and "transaction" in message                              \
			 and "Destination" in message["transaction"]               \
			 and "TransactionType" in message["transaction"]           \
			 and message["transaction"]["TransactionType"] == "Payment"\
			 and "Amount" in message["transaction"]                    \
			 and "currency" in message["transaction"]["Amount"]        \
			 and message["transaction"]["Amount"]["currency"] == "BTC":
				destination = message["transaction"]["Destination"]
				if destination == MY_RIPPLE_ADDRESS:
					if "DestinationTag" in message["transaction"]:
						#This means that someone just sent us IOUs, and we're supposed to send them bitcoins.
						amount = message["transaction"]["Amount"]["value"]
						try:
							transaction_code = message["transaction"]["DestinationTag"]
							entry = models.BitcoinOutEntry.objects.get(pk=transaction_code)
							entry.amount_owed = amount
							entry.save()
							print "On the next execution of the 'Listening!' loop, we will attempt to send",\
							 amount, "bitcoins to", entry.bitcoin_address
						except:
							print "Could not find this DestinationTag in the database. We'll send the IOUs back."
							self.send_ious_to(amount, message["transaction"]["Account"])
					else:
						print "Someone just sent us IOUs, but they lacked a DestinationTag."
				else: 	
					print "The ledger just closed on an IOU payment from us to someone else that has succeeded."
					mark_as_done(destination)
			else:
				print "The message received had a status of 'closed', but we don't know what for."
		else:
			print "The message status was not error, success, or closed, and was not recognized as any other kind of transaction."
	
	def send_ious_to(self, amount, ripple_address):
		request = {
			'command' : 'submit',
			'tx_json' : {
				'TransactionType' : 'Payment',
				'Account'         : MY_RIPPLE_ADDRESS,
				'Destination'     : ripple_address,
				'Amount'          : {
					'currency' : 'BTC',
					'value'    : str(amount),
					'issuer'   : MY_RIPPLE_ADDRESS,
				}
			},
			'secret'  : MY_SECRET_KEY,
		}
		self.send(json.dumps(request))
		
	def closed(self, code="", reason=""):
		if not self.connected:
			print "Closed down: Could not open connection."
		else:
			print "Closed down", code, reason
			
			
def mark_as_done(ripple_address):
	print "Marking as done:", ripple_address
	entries = models.BitcoinInEntry.objects.filter(done_yet=False).filter(ripple_address=ripple_address)
	if len(entries) > 1:
		print "ERROR! There is more than one entry in the database with that ripple_address!"        ,\
		 "Having received bitcoins at one of the associated bitcoin_address-es, and having received" ,\
		 "notification that our payment of IOUs to this ripple_address was successful, we don't know",\
		 "which entry to mark_as_done!"
		raise
	if len(entries) == 0:
		print "WARNING! Attempting to mark_as_done a ripple_address which exists nowhere among the",\
		 "BitcoinInEntrys that have not been done_yet. Nothing will happen as a result of this."
	else:
		for entry in entries:
			entry.done_yet = True
			entry.save()
		print "Marked ripple_address", ripple_address, "as done."


def listen():
	ws = IouClientConnector(RIPPLE_WEBSOCKET_URL, protocols=['http-only', 'chat'])
	ws.connect()
	#print "Testing!"
	#test(ws)
	while True:
		time.sleep(20)
		print "Listening!"
		btc_in_list = models.BitcoinInEntry.objects.filter(done_yet=False)
		btc_out_list = models.BitcoinOutEntry.objects.filter(done_yet=False).filter(amount_owed__gt=0)
		try:
			for entry in btc_in_list:
				bitcoin_address = entry.bitcoin_address
				ripple_address = entry.ripple_address
				print "BCA", bitcoin_address
				print "RA", ripple_address
				amount_received = amount_received_at_address(bitcoin_address)
				amount_received = 0.012345 #For testing only.
				print "AMOUNT", amount_received
				if amount_received > 0:
					ws.send_ious_to(amount_received, ripple_address)
		except Exception, e:
			print "An error occurred in traversing btc_in_list:", e
		try:
			for entry in btc_out_list:
				bitcoin_address = entry.bitcoin_address
				amount_owed = entry.amount_owed
				print "We need to send", amount_owed, "bitcoins to", bitcoin_address
				try:
					send_bitcoins_to(bitcoin_address, amount_owed)
					entry.done_yet = True
					entry.save()
					print "Marked bitcoin_address", bitcoin_address, "as done."
				except Exception, ee:
					print "send_bitcoins_to failed:", ex, "this will be attempted next time."
		except Exception, e:
			print "An error occurred in traversing btc_out_list:", e
		print "Finished the loop. Waiting..."
		
		
		
#For testing only.

	
def test_trust_me(ws):
	request = {
		'command' : 'submit',
		'tx_json' : {
			'TransactionType' : 'TrustSet',
			'Account'         : "rJENEwJWyFve99YNedcxw1zVZKLdQ1w3fS", 
			#'Destination'     : MY_RIPPLE_ADDRESS,
			'LimitAmount'          : {
				'currency' : 'BTC',
				'value'    : "8",
				'issuer'   : MY_RIPPLE_ADDRESS,
			}
			
		},
		'secret'  : "sh6PM1oVNGppr116fqf22pnGjwJnc",
	}
	ws.send(json.dumps(request))

def test_send_them_ious(ws, amount):
	ws.send_ious_to(amount, "rJENEwJWyFve99YNedcxw1zVZKLdQ1w3fS")
	
def test(ws):
	print "Waiting..."
	time.sleep(10)
	test_send_them_ious(ws, 0.01002)
	time.sleep(0.1)
	test_trust_me(ws)