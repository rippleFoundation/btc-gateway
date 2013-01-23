OVERVIEW

PythonNexus a simple web interface that allows anyone to automatically exchange bitcoins for BTC-denominated Ripple IOUs, and vice-versa. By running this application and opening it to the public, you can thus serve as a "gateway" for Bitcoin users to transfer value in and out of the Ripple network.


REQUIREMENTS AND SETUP

This application is implemented in and requires Django (https://www.djangoproject.com). Additionally, in order for it to run, you must simultaneously be running on your machine an instance of the Bitcoin daemon "bitcoind", which among other ways can be obtained by downloading the Bitcoin-Qt client (http://bitcoin.org/) and locating the "bitcoind" executable in the "daemon" directory.

bitcoind must be configured to accept RPC requests from the local machine. Otherwise, PythonNexus will give you an error resembling:

[Errno socket error] [Errno 10061] No connection could be made because the target machine actively refused it

At the end of pythonnexus/settings.py, five variables are declared for interacting with Bitcoin and Ripple. Make sure to replace them with values appropriate to your own case, as well as the Django-specific paths and keys declared elsewhere in the same file.

In addition to Python, Django, and bitcoind, the following (Python packages) are also required:
* jsonrpc
* ws4py

Before opening your service to the public, you must instruct your Ripple account to reject transactions lacking destination tags. This can be done by submitting the following request to the Ripple server (on the command line, in Python, etc.):

{'command':'submit','tx_json':{'TransactionType':'AccountSet','Flags':65536,'Account':MY_RIPPLE_ADDRESS,},'secret':MY_SECRET_KEY,}

(replacing the address and key as appropriate).


FEATURES

If a user wishes to send you bitcoins in exchange for IOUs, they can enter their Ripple address into the form, and they will receive a Bitcoin address to send to. Once they have sent any number of bitcoins, as many IOUs will be sent to their Ripple address. The Bitcoin address is then considered closed - the user should not send more bitcoins to it.

In order for this to be done, the user has to assign enough trust to you to be able to accept your IOUs. If no or insufficient trust is assigned, PythonNexus will continue trying (and failing) to send the IOUs until trust is assigned.

In the other direction, the user can also enter their Bitcoin address, and will receive a Ripple address to send BTC-denominated IOUs to; PythonNexus will then send as many Bitcoins to that address. (IOUs of other currencies will be bounced back or ignored). If for some reason you don't have enough bitcoins to redeem the IOUs, it will continue trying (and failing) until enough bitcoins are available.


UPDATED

This file was last updated January 23, 2013.