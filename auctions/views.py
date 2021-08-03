from django.contrib.auth import authenticate, get_user, login, logout
from django.db import IntegrityError
from django.forms.widgets import CheckboxInput, HiddenInput, RadioSelect
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import *

class FormCreateListing(forms.Form):
    title = forms.CharField(max_length=20, min_length=3, required=True)
    description = forms.CharField(min_length=3, max_length=200)
    initial_price = forms.FloatField(required=True)
    url_image = forms.CharField(max_length=200, required=False)
    category = forms.CharField(min_length=3, max_length=20, required=False)

class FormAddWatchlist(forms.Form):
    inwatchlist = forms.BooleanField(label="Add to Watchlist", required=False)

def index(request):
    if "watchlist" not in request.session:
        request.session["watchlist"] = []
    _listing = Auction_Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": _listing,
    })

def listing(request, listingid):
    _listing = Auction_Listing.objects.get(id=listingid)
    _user = get_user(request)
    _comments = _listing.comments.all()
    _currentBid = None
    _uWatchlist = None 
    _errorBid = ""
    try:
        _uWatchlist = _user.watchlistuser.filter(listings=_listing)[0]
    except:
        _uWatchlist = None

    _bids = []
    for _bid in _listing.listings.all():
        if not _currentBid or _bid.price > _currentBid.price:
            _currentBid = _bid
        _bids.append(_bid)

    form = FormAddWatchlist()

    if request.method == "POST":
        if request.POST["type"] == "a":
            if _user is not None:
                try:
                    _price = float(request.POST["price"])
                    if (_currentBid and _price > _currentBid.price) or (not _currentBid and _price > _listing.initial_price):
                        _bid = Auction_Bid(
                            price = _price,
                            user = _user,
                            listing = _listing)
                        _bid.save()
                        return HttpResponseRedirect(reverse("listing", args={_listing.id}))
                    else:
                        _errorBid = "*Your bid must be greater than the current bid."
                except:
                    _errorBid = "*Your bid must be greater than the current bid."
        elif request.POST["type"] == "b":
            try:
                _inwatchlist = request.POST["inwatchlist"]
            except:
                _inwatchlist = "off"
            
            if _uWatchlist is not None:
                if _inwatchlist == "on":
                    form.fields["inwatchlist"].initial = True
                else:
                    form.fields["inwatchlist"].initial = False
                    _uWatchlist.delete()
            else:
                if _inwatchlist == "on":
                    _uWatchlist = User_Watchlist(user = _user, listings = _listing)
                    _uWatchlist.save()
                    form.fields["inwatchlist"].initial = True
                else:
                    form.fields["inwatchlist"].initial = False
            return render(request, "auctions/listing.html", {
                "listing": _listing,
                "formAddWatchlist": form,
                "bidsLen": len(_bids),
                "isMeCurrentBid": _currentBid and _currentBid.user == _user,
                "isMineBid": _listing.user == _user,
                "currentBid": _currentBid,
                "comments": _comments,
                "errorBid": _errorBid
            })
        elif request.POST["type"] == "c":
            if _user is not None:
                _comment = Auction_Comment(listing = _listing, user = _user, comment = request.POST["comment"])
                _comment.save()
                _comments = _listing.comments.all()
        elif request.POST["type"] == "d":
            if _listing.user == _user:
                _listing.is_closed = True
                _listing.save()
   
    print(_uWatchlist)
    if _uWatchlist is not None:
        form.fields["inwatchlist"].initial = True
    else:
        form.fields["inwatchlist"].initial = False

    return render(request, "auctions/listing.html", {
        "listing": _listing,
        "formAddWatchlist": form,
        "bidsLen": len(_bids),
        "isMeCurrentBid": _currentBid and _currentBid.user == _user,
        "isMineBid": _listing.user == _user,
        "currentBid": _currentBid,
        "comments": _comments,
        "errorBid": _errorBid
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            print(request.session["watchlist"])
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def watchlist(request):
    _user = get_user(request)
    _listing = []
    if _user is not None:
        try:
            for wl in _user.watchlistuser.all():
                _listing.append(wl.listings)
        except:
            _listing = []
    return render(request, "auctions/watchlist.html", {
        "listings": _listing,
    })

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def createlisting(request):
    if request.method == "POST":
        form = FormCreateListing(request.POST)

        if form.is_valid():
            _title = request.POST["title"]
            _description = request.POST["description"]
            _initial_price = float(request.POST["initial_price"])
            _is_closed = False
            _url_image = request.POST["url_image"]
            _category = request.POST["category"]
            _listing = Auction_Listing(
                title = _title,
                description = _description,
                is_closed = _is_closed, 
                url_image = _url_image,
                category = _category,
                initial_price = _initial_price,
                user = get_user(request))
            _listing.save()
            return HttpResponseRedirect(reverse("listing", args={_listing.id}))

    form = FormCreateListing()
    return render(request, "auctions/createListing.html", {
        "form": form
    })

def categories(request): 
    _categories = []
    for _listing in Auction_Listing.objects.all():
        if _listing.category and _listing.category != "" and _listing.category not in _categories:
            _categories += [_listing.category]

    return render(request, "auctions/categories.html", {
        "categories": _categories,
    })


def category(request, category):
    _listings = Auction_Listing.objects.filter(category=category)
    print("_listing")
    print(_listings)
    return render(request, "auctions/category.html", {
        "listings": _listings,
    })