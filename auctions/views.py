from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Bid, Category, Comment, Listing


def index(request):
    active = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": active
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
    return render(request, "auctions/categories.html")

def create(request):
    return render(request, "auctions/create.html")

def watchlist(request):
    return render(request, "auctions/watchlist.html")

def listing(request, listing_id):
    listing = Listing.objects.filter(id = listing_id).first()
    bid = Bid.objects.filter(listing=listing.id).order_by('-bid_amount').first()
    print(listing)
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid": bid
    })