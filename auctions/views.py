from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import User, Bid, Category, Comment, Listing, Watchlist
from .utils import get_bid


class CreateListing(forms.Form):
    title = forms.CharField(
        label='Title', 
        max_length=100, 
        help_text="100 characters max", 
        widget=forms.TextInput(attrs={"class":"form-control"})
        )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class":"form-control"})
        )
    starting_bid = forms.DecimalField(
        min_value=0.01, 
        max_digits=8, 
        decimal_places=2, 
        help_text="Provide the minimum starting bid", 
        widget=forms.NumberInput(attrs={"class":"form-control"})
        )
    image_URL = forms.URLField(
        label="Image URL", 
        required=False, 
        help_text="Provide a link to your image", 
        widget=forms.URLInput(attrs={"class":"form-control"})
        )

    # Generates tuple list of categories
    # Note: tuple required as choice field defines name and value
    options = Category.objects.all().order_by("category")
    categories = [(None, "Please select...")]
    for option in options:
        categories.append((option.id, option.category))
    
    category = forms.ChoiceField(
        choices=categories, 
        required=False,
        help_text="Select the most appropriate category for your listing",
        widget=forms.Select(attrs={"class":"form-control"})
        )
    owner = forms.IntegerField(
        widget=forms.HiddenInput
        )


class BidForm(forms.Form):
    current_bid = forms.DecimalField(
        widget=forms.HiddenInput
    )
    listing_id = forms.IntegerField(
        widget=forms.HiddenInput
    )
    user_id = forms.IntegerField(
        widget=forms.HiddenInput
    )
    bid_amount = forms.DecimalField(
        label="Place bid",
        max_digits=8,
        decimal_places=2
    )

    # Validates new bid is greater than current bid
    def clean_bid_amount(self):
        bid_amount = self.cleaned_data["bid_amount"]
        current_bid = self.cleaned_data["current_bid"]

        if bid_amount <= current_bid:
            error = ValidationError(
                _("Error: New bid must be greater than the previous bid of £%(bid)s"),
                code="invalid",
                params={"bid":current_bid})
            self.add_error("bid_amount", error)
        
        return bid_amount

    # Validation for current_bid owner vs current user
    ## TO DO


class CommentForm(forms.Form):
    listing_id = forms.IntegerField(
        label='',
        widget=forms.HiddenInput
    )
    user_id = forms.IntegerField(
        label='',
        widget=forms.HiddenInput
    )
    comment = forms.CharField(
        label="Add comment",
        widget=forms.Textarea(attrs={"class":"comments"})
    )

def index(request):

    # Gets all listings, POST method provides additional filters
    if request.method == "POST":
        category_id = request.POST['category']
        category = Category.objects.filter(id=category_id).get()
        listings = Listing.objects.filter(active=True, category_id=category_id).order_by('title')
    else:
        listings = Listing.objects.filter(active=True).order_by('title')
        category = None

    # Creates dict of highest bid for each listing
    bids = {}
    for listing in listings:
        bids.update(get_bid(listing))

    return render(request, "auctions/index.html", {
        "listings": listings,
        "bids": bids,
        "category": category
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
    # Retrieves category list and counts entries for each
    categories = Category.objects.all().order_by("category")
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

            # Initialises category, sets data if present
            category = None
            if form.cleaned_data["category"]:
                category = form.cleaned_data["category"]
            
            listing = Listing.objects.create(
                title=form.cleaned_data["title"], 
                owner_id=form.cleaned_data["owner"], 
                description=form.cleaned_data["description"], 
                starting_bid=form.cleaned_data["starting_bid"], 
                image_URL=form.cleaned_data["image_URL"], 
                category_id=category)

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
            listing_id = request.POST["watchlist"],
            user_id = user
        )

        # message = "Added to watchlist"

        # If entry exists - deletes
        if created == False:
            Watchlist.objects.filter(id=obj.id).delete()
            # message = "Removed from watchlist"

        return HttpResponseRedirect(reverse("auctions:listing", args=[request.POST["watchlist"]]))

    else:
        user_object = User.objects.filter(id=user).get()
        watchlist = user_object.watchlist.all()

        # Retrieve bids
        bids = {}
        for entry in watchlist:
            bids.update(get_bid(entry.listing))
        
        return render(request, "auctions/watchlist.html", {
            "watchlist": watchlist,
            "bids": bids
        })

def listing(request, listing_id):

    # Initialises variables and forms for use in all routes
    # Initialised in order of requirement
    user = request.user.id
    listing = Listing.objects.filter(id=listing_id).first()
    bid = Bid.objects.filter(listing=listing.id).order_by('-bid_amount').first()
    if bid == None:
        bid = listing.starting_bid
    else:
        bid = bid.bid_amount
    watchlist = Watchlist.objects.filter(user_id=user, listing_id=listing).exists()
    comments = Comment.objects.filter(listing_id=listing.id)
    form_bid = BidForm(initial={"current_bid": bid, "listing_id": listing.id, "user_id": user})
    form_comment = CommentForm(initial={"listing_id": listing.id, "user_id": user})


    if request.method == "POST":

        # New bid path
        if "submit_bid" in request.POST:
            form = BidForm(request.POST)

            if form.is_valid():
                Bid.objects.create(
                    listing_id=form.cleaned_data["listing_id"],
                    user_id=form.cleaned_data["user_id"],
                    bid_amount=form.cleaned_data["bid_amount"]
                )
                return HttpResponseRedirect(reverse("auctions:listing", args=[form.cleaned_data["listing_id"]]))
            else:
                form_bid = BidForm(request.POST)
                return render(request, "auctions/listing.html", {
                    "bid": bid,
                    "comments": comments,
                    "listing": listing,
                    "watchlist": watchlist,
                    "form_bid": form_bid,
                    "form_comment": form_comment
                })
        
        # New comment path
        elif "submit_comment" in request.POST:
            form = CommentForm(request.POST)

            if form.is_valid():
                Comment.objects.create(
                    listing_id=form.cleaned_data["listing_id"],
                    user_id=form.cleaned_data["user_id"],
                    comment=form.cleaned_data["comment"])
                return HttpResponseRedirect(reverse("auctions:listing", args=[form.cleaned_data["listing_id"]]))
            else:
                form_comment = CommentForm(request.POST)
                return render(request, "auctions/listing.html", {
                    "bid": bid,
                    "comments": comments,
                    "listing": listing,
                    "watchlist": watchlist,
                    "form_bid": form_bid,
                    "form_comment": form_comment
                })
        
        # Close listing path
        else:
            if request.user.id != listing.owner_id:
                return HttpResponse("Error: Unauthorised action")

            Listing.objects.filter(id=listing_id).delete()
            return HttpResponseRedirect(reverse("auctions:index"))

    # Get method
    else:
        return render(request, "auctions/listing.html", {
            "bid": bid,
            "comments": comments,
            "listing": listing,
            "watchlist": watchlist,
            "form_bid": form_bid,
            "form_comment": form_comment
        })