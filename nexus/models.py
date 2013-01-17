from django.db import models

#When someone gives us a Ripple address, and we wait to receive bitcoins
#from them, and then send Ripple IOUs to them.
class BitcoinInEntry(models.Model):
	done_yet = models.BooleanField(default=False)
	bitcoin_address = models.CharField(max_length=34, unique=True)
	ripple_address = models.CharField(max_length=50)

#When someone gives us a Bitcoin address, and we wait to receive IOUs
#from them, and then send bitcoins to that address.
class BitcoinOutEntry(models.Model):
    done_yet = models.BooleanField(default=False)
    amount_owed = models.FloatField(default=0.0) #How many bitcoins are we supposed to send?
    bitcoin_address = models.CharField(max_length=34)
