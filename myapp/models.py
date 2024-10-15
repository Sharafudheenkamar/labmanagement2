# from django.db import models

# class Teacher(models.Model):
#     name = models.CharField(max_length=100)

# class Subject(models.Model):
#     name = models.CharField(max_length=100)
#     contact_hours_per_week = models.PositiveIntegerField()

# class Class(models.Model):
#     name = models.CharField(max_length=100)
#     subjects = models.ManyToManyField(Subject, through='ClassSubject')

# class ClassSubject(models.Model):
#     class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
#     teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

# class TimeSlot(models.Model):
#     day = models.CharField(max_length=10)
#     period = models.PositiveIntegerField()  # 1 to 5

# class TimetableEntry(models.Model):
#     class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
#     teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
#     time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
# timetable/models.py
from django.conf import settings
from django.db import models

class Semester(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)

    # def __str__(self):
    #     return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,null=True,blank=True)
    contact_hours = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    subjects = models.ManyToManyField(Subject,null=True,blank=True)

    def __str__(self):
        return self.name

class Timetable(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,null=True,blank=True)
    day = models.IntegerField(null=True,blank=True)
    period = models.IntegerField(null=True,blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,null=True,blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE,null=True,blank=True)

from django.db import models

class Teacher1(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Subject1(models.Model):
    name = models.CharField(max_length=100)
    contact_hours = models.IntegerField()
    teacher = models.ForeignKey(Teacher1, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Class1(models.Model):
    name = models.CharField(max_length=100)
    subjects = models.ManyToManyField(Subject1)

class TimetableEntry1(models.Model):
    day = models.CharField(max_length=10)
    period = models.IntegerField()
    cls = models.ForeignKey(Class1, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject1, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher1, on_delete=models.CASCADE)
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Auditorium Model
class Auditorium(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

# Model for defining working days and slots
class WorkingDay(models.Model):
    auditorium = models.ForeignKey(Auditorium, on_delete=models.CASCADE)
    day = models.CharField(max_length=20)  # Example: 'Monday', 'Tuesday', etc.
    start_time = models.TimeField()  # Example: 09:00 AM
    end_time = models.TimeField()    # Example: 05:00 PM

    def __str__(self):
        return f"{self.day} - {self.start_time} to {self.end_time}"

# Time Slot model
class TimeSlot(models.Model):
    working_day = models.ForeignKey(WorkingDay, on_delete=models.CASCADE)
    slot_start_time = models.TimeField()  # Example: 09:00 AM
    slot_end_time = models.TimeField()    # Example: 10:00 AM

    def __str__(self):
        return f"{self.slot_start_time} to {self.slot_end_time}"

# Booking model for managing reservations
class Booking(models.Model):
    auditorium = models.ForeignKey(Auditorium, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=255, null=True, blank=True)  # Added field for purpose

    def __str__(self):
        return f"{self.auditorium.name} booked by {self.user.username} on {self.date} ({self.time_slot})"
    

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta, datetime  # Import both timedelta and datetime from the standard library
from .tasks import send_booking_notification
from django.core.mail import send_mail

# Convert naive datetime to aware datetime
naive_dt = datetime.now()  # This will now correctly reference datetime.now()
aware_dt = timezone.make_aware(naive_dt)

@receiver(post_save, sender=Booking)
def booking_created_notification(sender, instance, created, **kwargs):
    if created:
        # Combine date and time slot to create booking_time (may be naive)
        booking_time = datetime.combine(instance.date, instance.time_slot.slot_start_time)

        # Ensure booking_time is timezone-aware
        if timezone.is_naive(booking_time):
            booking_time = timezone.make_aware(booking_time)

        # Schedule notification 24 hours before the booking
        notification_time = booking_time - timedelta(seconds=5)

        # Ensure the time is in the future and timezone-aware
        if timezone.now() < notification_time:
            # Schedule Celery task to send an email
            print("hello")
            send_booking_notification.apply_async(
                (
                    instance.user.email, 
                    instance.auditorium.name, 
                    instance.date.strftime("%Y-%m-%d"),  # Pass date as a string
                    instance.time_slot.slot_start_time.strftime("%H:%M"),  # Pass time slot start as a string
                    instance.purpose
                ),
                eta=notification_time  # Execute at notification_time (24 hours before the booking)
            )
@receiver(post_delete, sender=Booking)
def booking_cancelled_notification(sender, instance, **kwargs):
    # Send email for cancellation
    subject = f'Booking Cancelled: {instance.auditorium.name}'
    message = (f'Dear {instance.user.username},\n\n'
               f'Your booking for {instance.auditorium.name} on {instance.date} has been cancelled.\n\n'
               f'Best Regards,\nTeam')

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [instance.user.email],
        fail_silently=False,
    )
