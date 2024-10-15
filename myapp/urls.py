# timetable/urls.py
from django.urls import path
from . import views 
from .views import *


urlpatterns = [
    # path('generate/<int:semester_id>/', views.generate_view, name='generate_timetable'),
    path('gen/', views.timetable_view, name='view_timetable'),
    path('genclass/', TimetableView1.as_view(), name='TimetableView1'),
    path('gen1/', generate_timetable, name='generate_timetable'),
    path('insert/teacher/', InsertTeacherView.as_view(), name='insert_teacher'),
    path('insert/subject/', InsertSubjectView.as_view(), name='insert_subject'),
    path('insert/class/', InsertClassView.as_view(), name='insert_class'),
    path('edit_teacher/<int:pk>/', EditTeacherView.as_view(), name='edit_teacher'),
    path('edit_subject/<int:pk>/', EditSubjectView.as_view(), name='edit_subject'),
    path('edit_class/<int:pk>/', EditClassView.as_view(), name='edit_class'),
    path('Viewclass_subject_teachers/',Viewclass_subject_teachers.as_view(),name='view_data'),

    path('auditorium/<int:auditorium_id>/book/', AuditoriumBookingView.as_view(), name='auditorium_booking'),
    path('adminauditorium/<int:auditorium_id>/book/', AdminAuditoriumBookingView.as_view(), name='adminauditorium_booking'),
   
    path('booking/<int:booking_id>/confirmation/', BookingConfirmationView.as_view(), name='booking_confirmation'),
    path('booking/<int:booking_id>/edit/', EditBookingView.as_view(), name='edit_booking'),
    path('booking/<int:booking_id>/delete/', DeleteBookingView.as_view(), name='delete_booking'),


]
