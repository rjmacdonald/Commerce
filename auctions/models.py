from django.contrib.auth.models import AbstractUser
from django.db import models


class Bids(models.Model):
    listing = models.ForeignKey(
        'Listings',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        verbose_name="Bidder",
    )
    bid_amount = models.DecimalField(max_digits=8, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        return(f"{self.user}: {self.bid_amount}")

class Categories(models.Model):
    category = models.CharField(max_length=40)

    def __str__(self):
        return(self.category)

class Comments(models.Model):
    listing = models.ForeignKey(
        'Listings',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
    )
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return(f"{self.user} on {self.listing}")

class Listings(models.Model):
    owner = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2)
    image_URL = models.URLField(null=True)
    category = models.ForeignKey(
        'Categories',
        on_delete=models.SET_NULL,
        null=True,
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return(f"{self.owner}: {self.title}")

class User(AbstractUser):
    pass

class Wishlist(models.Model):
    listing = models.ForeignKey(
        'Listings',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return(f"{self.user}: {self.listing}")