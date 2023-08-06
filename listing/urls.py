from django.urls import path
from . import views
    
app_name = 'listing'

urlpatterns = [
    path('', views.add_listing, name='add_listing'),
    path('<pk>/', views.view_listing, name='view_listing'),
    path('<pk>/edit/', views.edit_listing, name='edit_listing'),
    path('<pk>/listing_bookings/', views.listing_bookings, name='listing_bookings'),
    path('<pk>/bookings_chart/', views.bookings_chart, name='bookings_chart'),
    path('<pk>/listing_bookings/pdf/', views.listing_bookings_pdf, name='listing_bookings_pdf'),
    path('<pk>/whatsapp/', views.whatsapp_chat, name='whatsapp_chat'),#url for whatsapp chat page
]