from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

from .models import User, Bid, Category, Comment, Listing, Watchlist
from .utils import get_bid


class CreateListing(forms.Form):
    title = forms.CharField(
        label='Title', 
        max_length=100, 
        help_text="100 characters max", 
        widget=forms.TextInput(attrs={"class":"form-control"}))
    description = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control"}))
    starting_bid = forms.DecimalField(
        min_value=0.01, 
        max_digits=8, 
        decimal_places=2, 
        help_text="Provide the minimum starting bid", 
        widget=forms.NumberInput(attrs={"class":"form-control"}))
    image_URL = forms.URLField(
        label="Image URL", 
        required=False, 
        help_text="Provide a link to your image", 
        widget=forms.URLInput(attrs={"class":"form-control"}))

    # Generates tuple list of categories
    # Note: tuple required as choice field defines name and value
    options = Category.objects.values("category").order_by("category")
    categories = [(None, "Please select...")]
    for option in options:
        category = option.items()
        for key, value in category:
            categories.append((value, value))
    category = forms.ChoiceField(
        choices=categories, 
        required=False,
        help_text="Select the most appropriate category for your listing",
        widget=forms.Select(attrs={"class":"form-control"}))

    owner = forms.IntegerField(
        label='', 
        widget=forms.HiddenInput)

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
    if request.method == "POST":
        form = CreateListing(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image_URL = form.cleaned_data["image_URL"]
            category = None
            if form.cleaned_data["category"]:
                category = form.cleaned_data["category"]
            owner = form.cleaned_data["owner"]

            listing = Listing.objects.create(
                title=title, owner_id=owner, description=description, starting_bid=starting_bid, 
                image_URL=image_URL, category=category)

            return HttpResponseRedirect(reverse("auctions:listing", args=[listing.id]))
        else:
            return render(request, "auctions/create.html", {
                "form": form,
                "message": "Error: Invalid submission"
            })
    else:
        form = CreateListing(initial={"owner": request.user.id})
        return render(request, "auctions/create.html", {
            "form": form
        })

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
    user = request.user.id
    listing = Listing.objects.filter(id = listing_id).first()
    bid = Bid.objects.filter(listing=listing.id).order_by('-bid_amount').first()
    watchlist = Watchlist.objects.filter(user_id=user, listing_id=listing).exists()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid": bid,
        "watchlist": watchlist
    })