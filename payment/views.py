from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from account.models import User
from listing.models import ListingItem
from .models import Booking, Renting
from django.http import HttpResponse, HttpResponseForbidden
from django_daraja.mpesa.core import MpesaClient

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg

from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import io
from reportlab.lib.utils import ImageReader
from django.template.loader import render_to_string
from django.utils.text import slugify
from xhtml2pdf import pisa
import os
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.template.loader import get_template

@csrf_exempt
@login_required
def book_listing(request,pk):
    print("IS THE USER AUTHENTICATED?",request.user.is_authenticated)
    print(request.user.phone_number)
    if request.user.is_tenant:
        print("REQUEST.USER.IS_TENANT",request.user.is_tenant)
        if not request.user.is_tenant:
            return HttpResponseForbidden()
        listing = get_object_or_404(ListingItem, pk=pk)

        cl = MpesaClient()

        phone_number = request.user.phone_number
        amount = listing.booking_fee
        account_reference = 'HouseQuest'
        transaction_desc = 'Payment of booking fee'
        callback_url = f'https://7964-105-166-142-54.ngrok-free.app/payment/{pk}/mpesa_callback/'
        response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)      
        print(response)
    return HttpResponse(response)

@csrf_exempt
def mpesa_callback(request, pk):
    listing = get_object_or_404(ListingItem, pk=pk)

    result = request.body
    cl = MpesaClient()
    data = cl.parse_stk_result(result)

    result_code = data['ResultCode']
    result_desc = data['ResultDesc']
    print(data)

    if result_code == 0:
        print("Transaction was successful")

        amount_paid = data.get('Amount')
        print(f"Booking fee paid: Ksh{amount_paid}")

        transaction_date_str = str(data.get('TransactionDate'))
        transaction_date = datetime.strptime(transaction_date_str, "%Y%m%d%H%M%S")
        transaction_date = timezone.make_aware(transaction_date) #make the datetime object timezone-aware
        iso_date = transaction_date.isoformat()
        print(f"Transaction date string: {transaction_date}")


        tenant_phone_number =  data.get('PhoneNumber')
        print(f"Tenant's Phone number: {tenant_phone_number}")

        transaction_code = data.get('MpesaReceiptNumber')
        print(f"Transaction code: {transaction_code}")

        listing_name = listing.name
        print("Listing booked: ",listing_name)
        
        if tenant_phone_number:
            tenant_phone_number = str(tenant_phone_number)
            if tenant_phone_number.startswith('254'):
                tenant_phone_number = '0' + tenant_phone_number[3:]

        user = User.objects.filter(phone_number=tenant_phone_number).first()
        if user:
            username = user.get_username()
            print(f"Tenant who booked: {username}")
            listing.booked_by.add(user)
            listing.vacancies -= 1
            if listing.vacancies == 0:
                listing.is_available = False
            listing.save()
        else:
            print("User not found")

        #creating Booking object
        booking = Booking(
            listing = listing,
            booking_tenant = username,
            transaction_code = transaction_code,
            tenant_phone_number = tenant_phone_number,
            transaction_date = iso_date,
            amount_paid = amount_paid,
        )
        booking.save()
        print(f"Booking created: {booking}")

    else:
        print("Transaction was UNsuccessful")

    return HttpResponse('Callback handled')

@login_required
def booking_report(request, pk):
    if not request.user.is_landlord:
        return redirect('account:tenant' if request.user.is_tenant else 'account:adminpage' if request.user.is_admin else 'account:login')
    listing = ListingItem.objects.get(id=pk)
    bookings = Booking.objects.filter(listing=listing) #get all bookings for the listing

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    top_margin = 0.75 * inch
    bottom_margin = 0.75 * inch

    #add the logo to each page
    logo_path = "account/static/images/logo.PNG" 
    logo_image = ImageReader(logo_path)
    logo_width, logo_height = logo_image.getSize()
    logo_scale = 0.5 #scale down the logo image
    logo_width *= logo_scale
    logo_height *= logo_scale
    logo_x = (letter[0] - logo_width) / 2
    logo_y = letter[1] - top_margin - (logo_height / 2)
    c.drawImage(logo_image, logo_x, logo_y, width=logo_width, height=logo_height)

    #add the title below the logo
    c.setFont("Helvetica-Bold", 18)
    title_x = inch * 0.5
    title_y = letter[1] - top_margin - inch * 1.5 #adjust the vertical position of the title by increasing the distance from the top margin
    total_bookings = bookings.count()
    title = f"Tenants who have booked {listing.name.upper()} listing"
    c.drawString(title_x, title_y, title)

    # Add the subtitle below the title
    c.setFont("Helvetica", 14)
    subtitle_x = inch * 0.5
    subtitle_y = title_y - 0.2 * inch # adjust the vertical position of the subtitle by increasing the distance from the title
    subtitle = f"Total bookings: {total_bookings}"
    c.drawString(subtitle_x, subtitle_y, subtitle)

    text_y = title_y - 0.5 * inch
    lines = []

    counter = 1 #initialize a counter to number the bookings

    for booking in bookings:
        lines.append(f"{counter}. Tenant: {booking.booking_tenant}")
        lines.append(f"    Phone number: {booking.tenant_phone_number}")
        lines.append(f"    Amount paid: Ksh{booking.amount_paid}")
        lines.append(f"    Transaction code: {booking.transaction_code}")
        lines.append(f"    Transaction date: {booking.transaction_date}")
        lines.append('=' * 65)
        counter += 1 #increment the counter
    
    max_lines_per_page = 25 # reduce the maximum number of lines per page

    page_number = 1
    line_count = 0
    for line in lines:
        if line_count >= max_lines_per_page:
            c.showPage()
            page_number += 1
            line_count = 0
            text_y = letter[1] - top_margin - inch * 1.5 # reset the vertical position of the text on each new page

            #add the logo to each page
            c.drawImage(logo_image, logo_x, logo_y, width=logo_width, height=logo_height)

        c.setFont("Helvetica", 14)
        text_x = inch * 0.5
        c.drawString(text_x, text_y, line)
        text_y -= 0.3 * inch 

        line_count += 1

    c.setFont("Helvetica", 12)
    page_text = f"Page {page_number}"
    c.drawRightString(letter[0] - inch, bottom_margin / 2, page_text)

    c.save()
    buf.seek(0)
    return FileResponse(buf, filename=f'booking_report_{listing.name}.pdf')

@login_required  
@csrf_exempt
def pay_rent(request, pk):
    print("IS THE USER AUTHENTICATED?",request.user.is_authenticated)
    print("REQUEST.USER.IS_TENANT",request.user.is_tenant)

    listing = get_object_or_404(ListingItem, pk=pk)
    if not request.user.is_authenticated or not request.user.is_tenant:
        return HttpResponseForbidden()
    cl = MpesaClient()

    phone_number = request.user.phone_number
    amount = listing.price
    account_reference = 'HouseQuest'
    transaction_desc = 'Payment of rent'
    callback_url = f'https://7964-105-166-142-54.ngrok-free.app/payment/{pk}/mpesa_rent_callback/'
    response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)      
    print("The pay rent view is working")
    print(response)
    return HttpResponse(response)

@csrf_exempt
def mpesa_rent_callback(request, pk):
    listing = get_object_or_404(ListingItem, pk=pk)

    result = request.body
    cl = MpesaClient()
    data = cl.parse_stk_result(result)

    result_code = data['ResultCode']
    result_desc = data['ResultDesc']
    print(data)

    if result_code == 0:
        print("Rent payment was successful")

        amount_paid = data.get('Amount')
        print(f"Rent paid: Ksh{amount_paid}")

        transaction_date_str = str(data.get('TransactionDate'))
        transaction_date = datetime.strptime(transaction_date_str, "%Y%m%d%H%M%S")
        transaction_date = timezone.make_aware(transaction_date) #make the datetime object timezone-aware
        iso_date = transaction_date.isoformat()
        print(f"Transaction date string: {transaction_date}")

        tenant_phone_number =  data.get('PhoneNumber')
        print(f"Tenant's Phone number: {tenant_phone_number}")

        transaction_code = data.get('MpesaReceiptNumber')
        print(f"Transaction code: {transaction_code}")

        listing_name = listing.name
        print("Listing paid for rent: ",listing_name)

        if tenant_phone_number:
            tenant_phone_number = str(tenant_phone_number)
            if tenant_phone_number.startswith('254'):
                tenant_phone_number = '0' + tenant_phone_number[3:]
        
        user = User.objects.filter(phone_number=tenant_phone_number).first()
        if user:
            username = user.get_username()
            print(f"Tenant who paid rent: {username}")
            listing.rented_by.add(user)
            listing.save()
        else:
            print("User not found")

        #creating Renting object
        renting = Renting(
            listing = listing,
            renting_tenant = username,
            transaction_code = transaction_code,
            tenant_phone_number = tenant_phone_number,
            transaction_date = iso_date,
            amount_paid = amount_paid,
        )
        renting.save()
        print(f"Renting created: {renting}")
    
    else:
        print("Rent payment was UNsuccessful")

    return HttpResponse('Callback handled')

@login_required
def tenant_rent_history(request, pk, listing_pk):
    if request.user.is_authenticated:
        user = User.objects.get(id=pk)
        if user == request.user:
            rentings = Renting.objects.filter(renting_tenant=user)
            rented_listings = ListingItem.objects.filter(rented_by=user)
            #get the ListingItem object with the primary key specified in the URL
            listing = ListingItem.objects.get(pk=listing_pk)
            #get the name of the listing
            listing_name = listing.name
            context = {
                'rentings': rentings,
                'rented_listings': rented_listings,
                'listing_name': listing_name,
                'listing': listing,
            }
            return render(request,'payment/tenant_rent_history.html', context)
        else:
            return redirect('account:login')
    else:
        return redirect('account:login')
    
@login_required
def landlord_rent_history(request, pk):
    if not request.user.is_landlord:
        return redirect('account:tenant' if request.user.is_tenant else 'account:adminpage' if request.user.is_admin else 'account:login')
    listing = ListingItem.objects.get(pk=pk)
    if request.user == listing.landlord:
        rentings = Renting.objects.filter(listing=listing)
        listing_name = listing.name
        # Calculate summary statistics
        total_rent_paid = rentings.aggregate(Sum('amount_paid'))['amount_paid__sum']
        average_rent_paid = rentings.aggregate(Avg('amount_paid'))['amount_paid__avg']
        context = {
            'listing': listing,
            'rentings': rentings,
            'listing_name': listing_name,
            'total_rent_paid': total_rent_paid,
            'average_rent_paid': average_rent_paid,
        }
    return render(request, 'payment/landlord_rent_history.html', context)

def download_rent_history(request, pk):
    #retrieve the rent payment history data
    listing = ListingItem.objects.get(pk=pk)
    rentings = Renting.objects.filter(listing=listing)
    listing_name = listing.name
    total_rent_paid = rentings.aggregate(Sum('amount_paid'))['amount_paid__sum']
    average_rent_paid = rentings.aggregate(Avg('amount_paid'))['amount_paid__avg']

    context = {
        'listing_name': listing_name,
        'rentings': rentings,
        'total_rent_paid': total_rent_paid,
        'average_rent_paid': average_rent_paid,
    }

    template = get_template('payment/landlord_rent_history_pdf.html')
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{listing_name}-rent-history.pdf"'

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