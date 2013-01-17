from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, RequestContext, loader

from nexus.models import BitcoinInEntry, BitcoinOutEntry

def index(request):
    template = loader.get_template('nexus/index.html')
    context = RequestContext(request, {
        'asdf': 'fdsa',
    })
    return HttpResponse(template.render(context))
	

def redeem(request):
    template = loader.get_template('nexus/redeem.html')
    context = RequestContext(request, {
        'asdf': 'fdsa',
    })
    return HttpResponse(template.render(context))

	
	
import pythonnexus.bitcoinlistener as bitcoinlistener

def bcin(request):
	already = False
	if True: #try:
		ripple_address=request.POST['ripple_address']
		#For any ripple_address, there should be no more than one entry with that ripple_address and with done_yet=False.
		entries_with_this_ra = BitcoinInEntry.objects.filter(ripple_address=ripple_address).filter(done_yet=False)
		if entries_with_this_ra:
			bitcoin_address = entries_with_this_ra[0].bitcoin_address
			already = True
		else:
			bitcoin_address=bitcoinlistener.generate_bitcoin_address() #generate bitcoin address and add it to your wallet.
			bcinentry = BitcoinInEntry.objects.create(ripple_address=ripple_address, bitcoin_address = bitcoin_address)
	else: #except:
		context = RequestContext(request, {
			'message': 'An error occured in submitting. Please try again later.'
		})	
		template = loader.get_template('nexus/index.html')
		return HttpResponse(template.render(context))
	
	template = loader.get_template('nexus/success.html')
	context = RequestContext(request, {'bitcoin_address':bitcoin_address, 'ripple_address':ripple_address, 'already':already})	
	return HttpResponse(template.render(context))

	
	
	
def bcout(request):
	bitcoin_address=request.POST['bitcoin_address'] #This is easier, because we can use the primary key (bcoutentry.id) to identify customers.
	if bitcoinlistener.validate_bitcoin_address(bitcoin_address):
		bcoutentry = BitcoinOutEntry.objects.create(bitcoin_address = bitcoin_address)
		template = loader.get_template('nexus/successredeem.html')
		context = RequestContext(request, {'bitcoin_address':bitcoin_address, 'ripple_address':bitcoinlistener.MY_RIPPLE_ADDRESS, 'id':bcoutentry.id})	
		return HttpResponse(template.render(context))
	else:
		context = RequestContext(request, {
			'message': 'This Bitcoin address is not valid. Please try again.'
		})	
		template = loader.get_template('nexus/redeem.html')
		return HttpResponse(template.render(context))