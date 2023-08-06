from django.shortcuts import get_object_or_404, render, redirect
import urllib
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

from listing.forms import ListingItemForm
from listing.models import ListingItem
from payment.models import Booking, Renting

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.http import HttpResponse
from matplotlib.backends.backend_agg import FigureCanvasAgg
import calendar

import os
from django.conf import settings
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.templatetags.static import static
from django.contrib.staticfiles import finders


@login_required
def add_listing(request):
    if not request.user.is_landlord:
        return redirect('account:tenant' if request.user.is_tenant else 'account:adminpage' if request.user.is_admin else 'account:login')
    
    form = ListingItemForm()
    if request.method == 'POST':
        form = ListingItemForm(request.POST, request.FILES)
        if form.is_valid():
            #set the landlord field to the current user
            form.instance.landlord = request.user
            form.save()
            return redirect('/landlord/')
    context = {
        'form': form
    }
    return render(request, 'listing/add_listing.html', context)
    

@login_required
def view_listing(request, pk):
    listing = ListingItem.objects.get(id=pk)
    if request.user.is_authenticated:
        rent_month = None
        renting = Renting.objects.filter(listing=listing, renting_tenant=request.user.username).first()
        if renting:
            rent_month = renting.transaction_date.strftime('%B')

        context = {
            'listing': listing,
            'rent_month': rent_month,
        }
        if request.user == listing.landlord:
            bookings = Booking.objects.filter(listing=listing)[:2]
            context['bookings'] = bookings
        return render(request,'listing/view_listing.html', context)
    else:
        return redirect('account:login')

@login_required
def edit_listing(request, pk):
    if not request.user.is_landlord:
        return redirect('account:tenant' if request.user.is_tenant else 'account:adminpage' if request.user.is_admin else 'account:login')
    
    listing = ListingItem.objects.get(id=pk)
    form = ListingItemForm(instance=listing)

    if request.method == 'POST':
        form = ListingItemForm(request.POST, instance=listing, files=request.FILES)
        if form.is_valid():
            #set the landlord field to the current user
            form.instance.landlord = request.user
            form.save()
            return redirect('listing:view_listing', pk=listing.id)
    context = {
        'form': form,
        'listing': listing
    }
    return render(request, 'listing/edit_listing.html', context)

@login_required
def listing_bookings(request, pk):
    if not request.user.is_landlord:
        return redirect('account:tenant' if request.user.is_tenant else 'account:adminpage' if request.user.is_admin else 'account:login')
    listing = ListingItem.objects.get(id=pk)

    if request.user == listing.landlord:
        bookings = Booking.objects.filter(listing=listing)
        listing_name = listing.name

        #filtering listings based on transaction date
        if 'transaction_date' in request.GET:
            q = request.GET['transaction_date']
            if q == 'today':
                bookings = bookings.filter(transaction_date__date=datetime.today())
            elif q == 'this_week':
                start_date = datetime.today() - timedelta(days=datetime.today().weekday())
                end_date = start_date + timedelta(days=6)
                bookings = bookings.filter(transaction_date__date__range=[start_date, end_date])
            elif q == 'this_month':
                start_date = datetime.today().replace(day=1)
                end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
                bookings = bookings.filter(transaction_date__date__range=[start_date, end_date])

        #calculate summary statistics
        total_bookings = bookings.count()
        total_revenue = sum(booking.amount_paid for booking in bookings)
        average_revenue = total_revenue / total_bookings if total_bookings > 0 else 0
        context = {
            'bookings': bookings,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'average_revenue': average_revenue,
            'listing_name': listing_name,
            'listing': listing,
        }
    return render(request, 'listing/listing_bookings.html', context)

@login_required
def bookings_chart(request, pk):
    listing = ListingItem.objects.get(id=pk)
    bookings = Booking.objects.filter(listing=listing)
    data = {}
    for booking in bookings:
        month = booking.transaction_date.month
        if month not in data:
            data[month] = 0
        data[month] += 1

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(data.keys(), data.values())
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Bookings')
    ax.set_title(f'Number of Bookings for listing {listing.name} (2023)')
    
    #set y-axis tick labels to integer values
    ax.set_yticks(range(0, int(max(data.values()) + 1)))
    
    #set x-axis tick labels to month names
    month_names = [calendar.month_abbr[i] for i in range(1, 13)]
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names)

    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

@login_required
def listing_bookings_pdf(request, pk):
    listing = ListingItem.objects.get(id=pk)
    bookings = Booking.objects.filter(listing=listing)
    listing_name = listing.name

    # set default value for title
    title = 'All Time'

    #filtering listings based on transaction date
    transaction_date = request.GET.get('transaction_date')
    if transaction_date:
        if transaction_date == 'today':
            bookings = bookings.filter(transaction_date__date=datetime.today())
            title = 'Today'
        elif transaction_date == 'this_week':
            start_date = datetime.today() - timedelta(days=datetime.today().weekday())
            end_date = start_date + timedelta(days=6)
            bookings = bookings.filter(transaction_date__date__range=[start_date, end_date])
            title = 'This Week'
        elif transaction_date == 'this_month':
            start_date = datetime.today().replace(day=1)
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            bookings = bookings.filter(transaction_date__date__range=[start_date, end_date])
            title = 'This Month'

    #calculate summary statistics
    total_bookings = bookings.count()
    total_revenue = sum(booking.amount_paid for booking in bookings)
    average_revenue = total_revenue / total_bookings if total_bookings > 0 else 0
    context = {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'average_revenue': average_revenue,
        'listing_name': listing_name,
        'title': title,
    }

    template = get_template('listing/listing_bookings_pdf.html')
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{listing_name} Bookings.pdf"'

    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=fetch_resources)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def fetch_resources(uri, rel):
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    elif uri.startswith(settings.STATIC_URL):
        path = finders.find(uri.replace(settings.STATIC_URL, ''))
    else:
        path = static(uri)
    return path


#redirecting the user to the whatsapp chat page
@login_required
def whatsapp_chat(request, pk):
    listing = get_object_or_404(ListingItem, id=pk)
    landlord_phone_number = '254' + listing.landlord.phone_number[1:]
    tenant_phone_number = request.user.phone_number
    base_url = 'https://wa.me/'
    url = f'{base_url}{landlord_phone_number}?text={urllib.parse.quote(f"Hello, I am interested in your {listing.name} listing.")}'
    return redirect(url)