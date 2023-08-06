from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('terms/', views.terms, name='terms'),
    path('login/', views.login_view, name='login'), 
    path('register/', views.register, name='register'),
    path('adminpage/',views.admin, name='adminpage'),
    path('report/<str:report_type>/',views.report, name='report'),
    path('tenant/',views.tenant, name='tenant'),
    path('<pk>/tenant_profile/',views.tenant_profile, name='tenant_profile'),
    path('update_profile', views.update_profile, name='update_profile'),
    path('landlord/',views.landlord, name='landlord'),
    path('logout/', views.logout_view, name='logout')
]
