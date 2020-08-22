from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Bid, Category, Comment, Listing, Watchlist
from .utils import get_bid


def index(request):

    # Gets all listings, POST method provides additional filters
    if request.method == "POST":
        category = request.POST['category']
        listings = Listing.objects.filter(active=True, category_id=category).order_by('title')
    else:
        listings = Listing.objects.filter(active=True).order_by('title')

    # Creates dict of highest bid for each listing
    bids = {}
    for listing in listings:
        bids.update(get_bid(listing))

    print(bids)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "bids": bids
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
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


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
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")

def user(request):
    return render(request, "auctions/user.html")

def categories(request):
    categories = Category.objects.all()
    counts = {}
    for category in categories:
        count = Listing.objects.filter(category_id=category.id, active=True).count()
        counts.update({ category.id : count })

    return render(request, "auctions/categories.html", {
        "categories": categories,
        "counts": counts
    })

def create(request):
    return render(request, "auctions/create.html")

def watchlist(request):
    user = request.user.id

    if request.method == "POST":

        # Gets or creates watchlist entry for listing/user combo 
        obj, created = Watchlist.objects.get_or_create(
            listing_id = request.POST["listing"],
            user_id = user
        )

        # message = "Added to watchlist"

        # If entry exists - deletes
        if created == False:
            Watchlist.objects.filter(id=obj.id).delete()
            # message = "Removed from watchlist"

        return HttpResponseRedirect(reverse("auctions:listing", args=[request.POST["listing"]]))

    else:
        user = User.objects.filter(id=user).get()
        watchlist = user.watchlist.all()

        # Retrieve bids
        bids = {}
        for entry in watchlist:
            bids.update(get_bid(entry.listing))
        
        return render(request, "auctions/watchlist.html", {
            "watchlist": watchlist,
            "bids": bids
        })

def listing(request, listing_id):
    listing = Listing.objects.filter(id = listing_id).first()
    bid = Bid.objects.filter(listing=listing.id).order_by('-bid_amount').first()
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid": bid
    })