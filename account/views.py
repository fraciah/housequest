from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from account.models import User

from django.contrib.auth.decorators import login_required

from listing.models import ListingType, ListingItem
from payment.models import Booking, Renting
from .forms import LoginForm, SignUpForm, UpdateProfileForm

from django.http import FileResponse, HttpResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import plotly.graph_objects as go
from django.db.models import Avg

# Create your views here.
def index(request):
    return render(request, 'account/index.html')

def about(request):
    return render(request, 'account/about.html')

def contact_us(request):
    return render(request, 'account/contact_us.html')

def terms(request):
    return render(request, 'account/terms.html')

def register(request):
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # msg = 'user created'
            return redirect('account:login')
        else:
            msg = 'form is not valid'
    else:
        form = SignUpForm()
    return render(request,'account/register.html', {'form': form, 'msg': msg})

@login_required
def update_profile(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        form = UpdateProfileForm(request.POST or None, instance=current_user)
        if form.is_valid():
            form.save()
            login(request, current_user)
            if request.user.is_tenant:
                return redirect(reverse('account:tenant_profile', args=[current_user.pk]))
            elif request.user.is_landlord:
                return redirect('account:landlord')
            else:
                return redirect('account:adminpage')
        return render(request, 'account/update_profile.html', {'form': form})
    else:
        return redirect('account:login')

def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_admin:
                login(request, user)
                return redirect('account:adminpage')
            elif user is not None and user.is_tenant:
                login(request, user)
                return redirect('account:tenant')
            elif user is not None and user.is_landlord:
                login(request, user)
                return redirect('account:landlord')
            else:
                msg= 'invalid credentials'
        else:
            msg = 'error validating form'
    return render(request, 'account/login.html', {'form': form, 'msg': msg})

@login_required
def admin(request):
    if not request.user.is_admin:
        return redirect('account:tenant' if request.user.is_tenant else 'account:landlord' if request.user.is_landlord else 'account:login')
    # total_users = User.objects.exclude(is_admin=True).count()
    total_users = User.objects.exclude(is_admin=True)
    landlords = User.objects.filter(is_landlord=True)
    tenants = User.objects.filter(is_tenant=True)
    listings = ListingItem.objects.all()

    #creating a pie chart to visualize the distribution of rental properties by type
    #retrieve the data from the models
    listing_types = list(ListingType.objects.all())
    listing_type_names = [str(listing_type) for listing_type in listing_types]
    rental_counts = [ListingItem.objects.filter(listing_type=listing_type).count() for listing_type in listing_types]
    #create the pie chart
    fig = go.Figure(data=[go.Pie(labels=listing_type_names, values=rental_counts)])
    #customize the layout
    fig.update_layout(title="Pie chart showing the distribution of HouseQuest rental listings by type")
    #convert the chart to HTML
    chart_div = fig.to_html(full_html=False)
    
    #creating a bar chart to visualize the average rent price for each type of rental property
    avg_rental_prices = []
    for listing_type in listing_types:
        listings_by_type = ListingItem.objects.filter(listing_type=listing_type)
        if listings_by_type.count() > 0:
            avg_price = listings_by_type.aggregate(Avg('price'))['price__avg']
            avg_rental_prices.append(avg_price)
        else:
            avg_rental_prices.append(0)
    
    fig2 = go.Figure(data=[go.Bar(x=listing_type_names, y=avg_rental_prices)])
    fig2.update_layout(title="Average rent price for each type of listing in HouseQuest")
    chart_div2 = fig2.to_html(full_html=False)


    #creating a pie chart to visualize the distribution of tenants by their preferred rental property type
    tenant_preferences = []
    filtered_listing_type_names = []
    for listing_type in listing_types:
        bookings_by_listing_type = Booking.objects.filter(listing__listing_type=listing_type)
        tenant_count = bookings_by_listing_type.values('booking_tenant').distinct().count()
        if tenant_count > 0:
            tenant_preferences.append(tenant_count)
            filtered_listing_type_names.append(str(listing_type))
        
    fig3 = go.Figure(data=[go.Pie(labels=filtered_listing_type_names, values=tenant_preferences)])
    fig3.update_layout(title="Distribution of tenants by their preferred listing(booking data)")
    chart_div3 = fig3.to_html(full_html=False)


    #creating a bar chart to visualize the number of landlords and tenants
    user_counts = [landlords.count(), tenants.count()]
    user_labels = ['Landlords', 'Tenants']
    
    fig4 = go.Figure(data=[go.Bar(x=user_labels, y=user_counts)])
    fig4.update_layout(title="Number of landlords and tenants in HouseQuest")
    chart_div4 = fig4.to_html(full_html=False)

    context = {
        'total_users': total_users,
        'landlords': landlords,
        'tenants': tenants,
        'listings': listings,
        'chart_div': chart_div,
        'chart_div2': chart_div2,
        'chart_div3': chart_div3,
        'chart_div4': chart_div4,
    }
    now = datetime.now()
    hour = now.hour
    if hour < 12:
        message = "morning"
    elif hour < 18:
        message = "afternoon"
    else:
        message = "evening"
    context['message'] = message 
    return render(request,'account/admin.html', context)

@login_required
def tenant(request):
    if not request.user.is_tenant:
        return redirect('account:landlord' if request.user.is_landlord else 'account:adminpage' if request.user.is_admin else 'account:login')
      
    listings = ListingItem.objects.filter(is_available=True)
    
    #filtering listings based on listing type
    if 'Lt' in request.GET:
        q = request.GET['Lt']
        listings &= ListingItem.objects.filter(listing_type__name__icontains=q)
    
    #filtering listings based on location
    if 'location' in request.GET:
        q = request.GET['location']
        listings &= listings.filter(location__icontains=q)
    
    #filtering listings based on price range
    if 'price_range' in request.GET and request.GET['price_range']:
        q = request.GET['price_range']
        if q == '0-5000':
            listings = listings.filter(price__lt=5000)
        elif '-' in q:
            min_price, max_price = q.split('-')
            if min_price:
                listings = listings.filter(price__gte=min_price)
            if max_price:
                listings = listings.filter(price__lte=max_price)
        else:
            min_price = q
            listings = listings.filter(price__gte=min_price)
        
    context = {}

    now = datetime.now()
    hour = now.hour
    if hour < 12:
        message = "morning"
    elif hour < 18:
        message = "afternoon"
    else:
        message = "evening"
    context['message'] = message
    
    if not listings:
        context['no_results'] = True  #if no results are found, display a message(in tenant.html)
    else:
        context['listings'] = listings
    return render(request,'account/tenant.html', context)

@login_required
def tenant_profile(request, pk):
    if request.user.is_authenticated:
        user = User.objects.get(id=pk)
        if user == request.user:
            booked_listings = ListingItem.objects.filter(booked_by=user)
            bookings = Booking.objects.filter(listing__in=booked_listings, booking_tenant=user.username)
            rented_listings = ListingItem.objects.filter(rented_by=user)
            rentings = Renting.objects.filter(listing__in=booked_listings, renting_tenant=user.username)
            context = {
                'user': user,
                'booked_listings': booked_listings,
                'bookings': bookings,
                'rented_listings': rented_listings,
                'rentings': rentings,
            }
            return render(request,'account/tenant_profile.html', context)
        else:
            return redirect('account:login')
    else:
        return redirect('account:login')
    
@login_required
def landlord(request):
    if not request.user.is_landlord:
        return redirect('account:tenant' if request.user.is_tenant else 'account:adminpage' if request.user.is_admin else 'account:login')
    
    context = {}

    now = datetime.now()
    hour = now.hour
    if hour < 12:
        message = "morning"
    elif hour < 18:
        message = "afternoon"
    else:
        message = "evening"
    context['message'] = message
    
    listings = ListingItem.objects.filter(landlord=request.user)
    
    #filtering listings based on listing type  
    if 'Lt-l' in request.GET:
        q = request.GET['Lt-l']
        listings &= listings.filter(listing_type__name__icontains=q)
    
    #filtering listings based on location
    if 'location' in request.GET:
        q = request.GET['location']
        listings &= listings.filter(location__icontains=q)
    
    #filtering listings based on price range
    if 'price_range' in request.GET and request.GET['price_range']:
        q = request.GET['price_range']
        if q == '0-5000':
            listings = listings.filter(price__lt=5000)
        elif '-' in q:
            min_price, max_price = q.split('-')
            if min_price:
                listings = listings.filter(price__gte=min_price)
            if max_price:
                listings = listings.filter(price__lte=max_price)
        else:
            min_price = q
            listings = listings.filter(price__gte=min_price)
    
    if not listings:
        context['no_results'] = True  #if no results are found, display a message(in landlord.html)
    else:
        context['listings'] = listings
    
    return render(request,'account/landlord.html', context)


def logout_view(request):
    logout(request)
    return redirect('account:index')

#generate a pdf file
@login_required
def report(request, *args, **kwargs):
    total_users = User.objects.exclude(is_admin=True)
    landlords = User.objects.filter(is_landlord=True)
    tenants = User.objects.filter(is_tenant=True)
    listings = ListingItem.objects.all()

    report_type = kwargs['report_type']

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

    lines = []
    counter = 1  #initialize the 
    
     #title based on report type
    if report_type == 'users':
        title = "ALL USERS REPORT"
        subtitle = f"Total users: {total_users.count()}"
    elif report_type == 'landlords':
        title = "LANDLORDS REPORT"
        subtitle = f"Total landlords: {landlords.count()}"
    elif report_type == 'tenants':
        title = "TENANTS REPORT"
        subtitle = f"Total tenants: {tenants.count()}"
    elif report_type == 'listings':
        title = "LISTINGS REPORT"
        subtitle = f"Total listings: {listings.count()}"
    elif report_type == 'visualizations':
        current_date = datetime.now().strftime('%Y-%m-%d')
        title = f"Summary visualizations as of {current_date}"
        subtitle =  "."

        # Generate visualizations
        # Pie chart showing distribution of rental listings by type
        listing_types = list(ListingType.objects.all())
        listing_type_names = [str(listing_type) for listing_type in listing_types]
        rental_counts = [ListingItem.objects.filter(listing_type=listing_type).count() for listing_type in listing_types]
        fig = go.Figure(data=[go.Pie(labels=listing_type_names, values=rental_counts)])
        fig.update_layout(title="Pie chart showing distribution of HouseQuest rental listings by type")
        pie_chart_img = fig.to_image(format="png")

        # Bar chart showing average rent price for each type of listing
        avg_rental_prices = []
        for listing_type in listing_types:
            listings_by_type = ListingItem.objects.filter(listing_type=listing_type)
            if listings_by_type.count() > 0:
                avg_price = listings_by_type.aggregate(Avg('price'))['price__avg']
                avg_rental_prices.append(avg_price)
            else:
                avg_rental_prices.append(0)
        fig2 = go.Figure(data=[go.Bar(x=listing_type_names, y=avg_rental_prices)])
        fig2.update_layout(title="Average rent price for each type of listing in HouseQuest")
        bar_chart_img = fig2.to_image(format="png")

        # Pie chart showing distribution of tenants by their preferred rental property type
        tenant_preferences = []
        filtered_listing_type_names = []
        for listing_type in listing_types:
            bookings_by_listing_type = Booking.objects.filter(listing__listing_type=listing_type)
            tenant_count = bookings_by_listing_type.values('booking_tenant').distinct().count()
            if tenant_count > 0:
                tenant_preferences.append(tenant_count)
                filtered_listing_type_names.append(str(listing_type))
        fig3 = go.Figure(data=[go.Pie(labels=filtered_listing_type_names, values=tenant_preferences)])
        fig3.update_layout(title="Distribution of tenants by their preferred listing (booking data)")
        pie_chart2_img = fig3.to_image(format="png")

        # Bar chart showing number of landlords and tenants
        user_counts = [landlords.count(), tenants.count()]
        user_labels = ['Landlords', 'Tenants']
        fig4 = go.Figure(data=[go.Bar(x=user_labels, y=user_counts)])
        fig4.update_layout(title="Number of landlords and tenants in HouseQuest")
        bar_chart2_img = fig4.to_image(format="png")

    else:
        return HttpResponse("Invalid identifier")

    #add the title to the first page
    c.setFont("Helvetica-Bold", 16)
    title_x = inch * 0.5
    title_y = letter[1] - top_margin - inch * 1.0 #adjust the vertical position of the title by increasing the distance from the top margin
    c.drawString(title_x, title_y, title)

    #subtitle below the title
    c.setFont("Helvetica", 14)
    subtitle_x = inch * 0.5
    subtitle_y = title_y - 0.2 * inch 
    c.drawString(subtitle_x, subtitle_y, subtitle)

    text_y = title_y - 0.5 * inch
    
    if report_type == 'users':
        users = User.objects.exclude(is_admin=True).all()
        for user in users:
            lines.append(f"{counter}. Username: {user.username}")
            if user.is_landlord:
                lines.append("    User type: Landlord")
            elif user.is_tenant:
                lines.append("    User type: Tenant")
            else:
                lines.append("   N/A")
            lines.append(f"    Email: {user.email}")
            lines.append(f"    Phone number: {user.phone_number}")
            lines.append(f"    Date joined: {user.date_joined.strftime('%Y-%m-%d %I:%M:%S %p')}")
            if user.last_login is not None:
                lines.append(f"    Last logged in: {user.last_login.strftime('%Y-%m-%d %I:%M:%S %p')}")
            else:
                lines.append("    Last logged in: N/A")
            lines.append('=' * 65)
            counter += 1  #increment the counter

    elif report_type == 'landlords':
        landlords = User.objects.filter(is_landlord=True).all()
        for landlord in landlords:
            lines.append(f"{counter}. Username: {landlord.username}")
            lines.append(f"    Email: {landlord.email}")
            lines.append(f"    Phone number: {landlord.phone_number}")
            lines.append(f"    Date joined: {landlord.date_joined.strftime('%Y-%m-%d %I:%M:%S %p')}")
            if landlord.last_login is not None:
                lines.append(f"    Last logged in: {landlord.last_login.strftime('%Y-%m-%d %I:%M:%S %p')}")
            else:
                lines.append("   Last logged in: N/A")
            lines.append(f"    Number of listings owned: {landlord.listingitem_set.count()}")
            lines.append('=' * 65)
            counter += 1

    elif report_type == 'tenants':
        tenants = User.objects.filter(is_tenant=True).all()
        for tenant in tenants:
            lines.append(f"{counter}. Username: {tenant.username}")
            lines.append(f"    Email: {tenant.email}")
            lines.append(f"    Phone number: {tenant.phone_number}")
            lines.append(f"    Date joined: {tenant.date_joined.strftime('%Y-%m-%d %I:%M:%S %p')}")
            if tenant.last_login is not None:
                lines.append(f"    Last logged in: {tenant.last_login.strftime('%Y-%m-%d %I:%M:%S %p')}")
            else:
                lines.append("    Last logged in: N/A")
            lines.append('=' * 65)
            counter += 1

    elif report_type == 'listings':
        listings = ListingItem.objects.all()
        for listing in listings:
            formatted_price = format(listing.price, ',')
            formatted_booking_fee = format(listing.booking_fee, ',')
            lines.append(f"{counter}. Owner: {listing.landlord.username}")
            lines.append(f"    Name of listing: {listing.name}")
            lines.append(f"    Type of listing: {listing.listing_type.name}")
            lines.append(f"    Date posted: {listing.display_date().strftime('%Y-%m-%d %I:%M:%S %p')}")
            lines.append(f"    Location: {listing.location}")
            lines.append(f"    Price: {formatted_price}")
            lines.append(f"    Booking fee: {formatted_booking_fee}")
            lines.append(f"    Vacancies: {listing.vacancies}")
            lines.append('=' * 65)
            counter += 1

    elif report_type == 'visualizations':
        #add visualizations to PDF report
        image_width = inch * 4
        image_height = inch * 2.5
        image_x = (letter[0] - image_width) / 2

        visualizations = [pie_chart_img, bar_chart_img, pie_chart2_img, bar_chart2_img]
        for visualization in visualizations:
            #check if there is enough space on the current page
            if text_y - inch * 2.5 < bottom_margin:
                c.showPage()
                text_y = letter[1] - top_margin

            c.drawImage(ImageReader(io.BytesIO(visualization)), image_x, text_y - inch * 2.5, width=image_width, height=image_height)
            text_y -= inch * 2.5
            
    else:
        return HttpResponse("Invalid identifier")

    max_lines_per_page = 30

    page_number = 1
    line_count = 0
    for line in lines:
        if line_count >= max_lines_per_page or text_y < bottom_margin:
            c.showPage()
            page_number += 1
            line_count = 0
            text_y = letter[1] - top_margin

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
    return FileResponse(buf, filename='report.pdf')
