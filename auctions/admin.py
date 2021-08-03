from django.contrib import admin
from .models import Auction_Bid, Auction_Listing, Auction_Comment, User

admin.site.register(User)
admin.site.register(Auction_Comment)
admin.site.register(Auction_Listing)
admin.site.register(Auction_Bid)