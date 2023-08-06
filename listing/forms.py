from django.forms import ModelForm
from .models import ListingItem

class ListingItemForm(ModelForm):
    class Meta:
        model = ListingItem
        fields = ['listing_type','name', 'price', 'location', 'description','vacancies', 'is_available','image','booking_fee','features']

    #for styling the form
    def __init__(self, *args, **kwargs):
        super(ListingItemForm, self).__init__(*args, **kwargs)
        self.fields['listing_type'].widget.attrs.update({'class': 'myfieldclass'})
        self.fields['price'].widget.attrs.update({'class': 'myfieldclass'})
        self.fields['description'].widget.attrs.update({'class': 'myfieldclass-description'})
        self.fields['vacancies'].widget.attrs.update({'class': 'myfieldclass'})
        self.fields['booking_fee'].widget.attrs.update({'class': 'myfieldclass'})
        self.fields['features'].widget.attrs.update({'class': 'myfieldclass-features'})