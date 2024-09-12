# timetable/urls.py
from django.urls import path
from . import views 
from .views import *


urlpatterns = [
    # path('generate/<int:semester_id>/', views.generate_view, name='generate_timetable'),
    path('gen/', views.timetable_view, name='view_timetable'),
    path('gen1/', generate_timetable, name='generate_timetable'),
]
