from . import models

def get_bid(listing):
    all_bids = models.Bid.objects.all()
    bids = {listing.id : all_bids.filter(listing_id = listing.id).order_by('-bid_amount').first()}
    return bids