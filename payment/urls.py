from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('<pk>/', views.book_listing, name='book_listing'),
    path('<pk>/booking_report/', views.booking_report, name='booking_report'),
    path('<pk>/mpesa_callback/', views.mpesa_callback, name='mpesa_callback'),
    path('<pk>/pay_rent/', views.pay_rent, name='pay_rent'),
    path('<pk>/mpesa_rent_callback/', views.mpesa_rent_callback, name='mpesa_rent_callback'),
    path('<pk>/<listing_pk>/tenant_rent_history/',views.tenant_rent_history, name='tenant_rent_history'),
    path('<pk>/landlord_rent_history/',views.landlord_rent_history, name='landlord_rent_history'),
    path('<pk>/download_rent_history/', views.download_rent_history, name='download_rent_history'),
]