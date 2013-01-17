from django.contrib import admin
from nexus.models import BitcoinInEntry, BitcoinOutEntry
admin.site.register(BitcoinInEntry)
admin.site.register(BitcoinOutEntry)
