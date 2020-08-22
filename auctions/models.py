from django.contrib.auth.models import AbstractUser
from django.db import models


class Bid(models.Model):
    listing = models.ForeignKey(
        'Listing',
        on_delete=models.CASCADE,
        related_name="bids"
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        verbose_name="Bidder",
        related_name="bids"
    )
    bid_amount = models.DecimalField(max_digits=8, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        return(f"{self.user}: {self.bid_amount}")

class Category(models.Model):
    category = models.CharField(max_length=40)

    def __str__(self):
        return(self.category)

class Comment(models.Model):
    listing = models.ForeignKey(
        'Listing',
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name="comments"
    )
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return(f"{self.user} on {self.listing}")

class Listing(models.Model):
    owner = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name="listings"
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2)
    image_URL = models.URLField(blank=True)
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="listings"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return(f"{self.owner}: {self.title}")

class User(AbstractUser):
    pass

class Watchlist(models.Model):
    listing = models.ForeignKey(
        'Listing',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name="watchlist"
    )

    def __str__(self):
        return(f"{self.user}: {self.listing}")