from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/save/', views.toggle_saved_job, name='toggle_saved_job'),
    path('saved/', views.saved_jobs, name='saved_jobs'),
]
