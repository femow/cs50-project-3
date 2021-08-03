from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    # User have multiple bids -> Access via user.auction_bid_set.objects.all()
    # User have multiple comments -> Access via user.auction_comment_set.objects.all()
    pass

class Auction_Listing(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    is_closed = models.BooleanField(default=False)
    url_image = models.CharField(blank=True, max_length=200)
    category = models.CharField(blank=True, max_length=20)
    initial_price = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="myListings", default="")
    # Listing have multiple comments -> Access via listing.auction_bid_set.objects.all()
    # Listing have one bid -> Access via listing.auction_bid_set.objects.all()
    
class User_Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlistuser", default="")
    listings = models.ForeignKey(Auction_Listing, on_delete=models.CASCADE, related_name="watchlist", default="")

class Auction_Bid(models.Model):
    price = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", default="")
    listing = models.ForeignKey(Auction_Listing, on_delete=models.CASCADE, related_name="listings", default="")

class Auction_Comment(models.Model):
    listing = models.ForeignKey(Auction_Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentators")
    comment = models.CharField(max_length=100)

