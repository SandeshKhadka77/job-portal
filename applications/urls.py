from django.urls import path

from . import views

urlpatterns = [
    path('apply/<int:pk>/', views.apply_job, name='apply_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
]