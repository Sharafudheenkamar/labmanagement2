# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

@shared_task
def send_booking_notification(user_email, auditorium_name, booking_date, slot_time, purpose):
    subject = f'Reminder: Booking for {auditorium_name}'
    message = (f'Dear User, \n\n'
               f'This is a reminder that you have booked {auditorium_name} on {booking_date} for the purpose of "{purpose}".\n'
               f'The booking time is {slot_time}.\n\n'
               f'Best Regards, \nTeam')
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )
