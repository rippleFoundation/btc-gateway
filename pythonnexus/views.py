from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, RequestContext, loader

from pythonnexus.models import BitcoinInEntry, BitcoinOutEntry
import pythonnexus.bitcoinlistener as bitcoinlistener

def index(request):
    template = loader.get_template('pythonnexus/index.html')
    return HttpResponse(template.render(Context({})))
	
	
def deposit(request):
    template = loader.get_template('pythonnexus/deposit.html')
    return HttpResponse(template.render(RequestContext(request,{})))

def redeem(request):
    template = loader.get_template('pythonnexus/redeem.html')
    return HttpResponse(template.render(RequestContext(request,{})))

def bcin(request):
	already = False
	ripple_address=request.POST['ripple_address']
	if ripple_address:
		#For any ripple_address, there should be no more than one entry with that ripple_address and with done_yet=False.
		entries_with_this_ra = BitcoinInEntry.objects.filter(ripple_address=ripple_address).filter(done_yet=False)
		if entries_with_this_ra:
			bitcoin_address = entries_with_this_ra[0].bitcoin_address
			already = True
		else:
			bitcoin_address=bitcoinlistener.generate_bitcoin_address() #Generate a Bitcoin address and add it to our wallet.
			bcinentry = BitcoinInEntry.objects.create(ripple_address=ripple_address, bitcoin_address = bitcoin_address)
		template = loader.get_template('pythonnexus/depositsuccess.html')
		context = RequestContext(request, {
			'bitcoin_address':bitcoin_address,
			'ripple_address':ripple_address,
			'already':already})	
	else:
		context = RequestContext(request, {
			'error_message': 'You have to enter something!'
		})	
		template = loader.get_template('pythonnexus/deposit.html')
	return HttpResponse(template.render(context))
	
def bcout(request):
	bitcoin_address=request.POST['bitcoin_address'] #This is easier, because we can use the primary key (bcoutentry.id) to identify customers.
	if bitcoinlistener.validate_bitcoin_address(bitcoin_address):
		bcoutentry = BitcoinOutEntry.objects.create(bitcoin_address = bitcoin_address)
		template = loader.get_template('pythonnexus/redeemsuccess.html')
		context = RequestContext(request, {
			'bitcoin_address':bitcoin_address,
			'ripple_address':bitcoinlistener.MY_RIPPLE_ADDRESS,
			'id':bcoutentry.id
		})
	else:
		context = RequestContext(request, {
			'error_message': 'This Bitcoin address is not valid. Please try again.'
		})	
		template = loader.get_template('pythonnexus/redeem.html')
	return HttpResponse(template.render(context))