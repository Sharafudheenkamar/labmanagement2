
from django.http import HttpResponse
from django.db.models import Count
from .models import Class1, Subject1, TimetableEntry1
import random
from random import shuffle
from django.views import View
def generate_timetable(request):
    # Get all classes
    classes = Class1.objects.all()
    
    # Define the days and periods
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = [1, 2, 3, 4, 5]  # Assuming 5 periods per day
    
    # Identify common subjects across all classes
    common_subject_ids = Subject1.objects.annotate(class_count=Count('class1')).filter(class_count__gt=1).values_list('id', flat=True)
    common_subjects = Subject1.objects.filter(id__in=common_subject_ids)
    uncommon_subjects = Subject1.objects.exclude(id__in=common_subject_ids)
    

    common_subject_slots = {}

    # Assign common subjects
    for subject in common_subjects:
        # Collect available slots across all classes where the subject is taught
        available_slots = []
        for cls in classes:
            class_subjects = cls.subjects.all()
            if subject in class_subjects:
                for day in days:
                    for period in periods:
                        available_slots.append({
                            'day': day,
                            'period': period,
                            'cls': cls
                        })

        # print(f"Available slots for subject {subject.name}: {len(available_slots)}")

        # Randomly select slots for the subject
        hours_remaining = subject.contact_hours
        # print(f"Hours remaining for subject {subject.name}: {hours_remaining}")

        if available_slots:
            num_slots_to_select = min(len(available_slots), hours_remaining)
                    
            # Randomly select distinct slots
            selected_slots = random.sample(available_slots, num_slots_to_select)
            # print(f"Selected slots for subject {subject.name}: {len(selected_slots)}")

        else:
            print(f"No available slots for subject {subject.name}")
    # print(selected_slots)
    # Save selected slots for the subject
    common_subject_slots[subject.id] = selected_slots
    # Initialize timetable for each class
    for cls in classes:
        # Get subjects for the class
        class_subjects = cls.subjects.all()
        
        # Initialize timetable
        timetable = []
        for day in days:
            for period in periods:
                timetable.append({
                    'day': day,
                    'period': period,
                    'cls': cls,
                    'subject': None
                })
        
        # Assign common subjects
        for subject_id, slots in common_subject_slots.items():
            subject = Subject1.objects.get(id=subject_id)
            if subject in class_subjects:
                for slot in slots:
                    # Ensure that the slot is available
                    while True:
                        if not TimetableEntry1.objects.filter(day=slot['day'], period=slot['period'], cls=cls, subject=subject).exists():
                            TimetableEntry1.objects.create(
                                day=slot['day'],
                                period=slot['period'],
                                cls=cls,
                                subject=subject,
                                teacher=subject.teacher
                            )
                            # print(f"Assigned {subject.name} to {cls.name} on {slot['day']} period {slot['period']}")
                            break  # Exit loop when assignment is successful
                        else:
                            # print(f"Slot already occupied: {slot['day']} period {slot['period']} for {subject.name} in {cls.name}")
                            # Remove the occupied slot and try another one
                            slots.remove(slot)
                            if slots:
                                slot = random.choice(slots)
                            else:
                                print(f"No more available slots for {subject.name} in {cls.name}")
                                break  # Exit loop if no slots are available
        
    empty_slots = []
    # Calculate empty slots by filtering out occupied ones from the timetable
    for cls in classes:
        # Get all periods for this class
        timetable_entries = TimetableEntry1.objects.filter(cls=cls)

        # Initialize a list of all possible slots for this class
        full_slots = []
        for day in days:
            for period in periods:
                full_slots.append({'day': day, 'period': period, 'cls': cls})

        # Filter out the slots already occupied in the timetable
        
        for slot in full_slots:
            if not timetable_entries.filter(
                day=slot['day'], 
                period=slot['period'],
                cls=slot['cls']
            ).exists():
                empty_slots.append(slot)
    print('emptyslots',empty_slots)
 
        # Create a dictionary to store subjects by the same teacher across all classes
    teacher_subjects = {}

    # Loop through all classes
    for cls in Class1.objects.all():
        class_subjects = cls.subjects.all()  # Get all subjects for this class

        for subject in uncommon_subjects:
            teacher = subject.teacher
            
            # Check if this teacher is already in the dictionary
            if teacher not in teacher_subjects:
                teacher_subjects[teacher] = set()  # Initialize an empty set for subjects
            
            # Add the full subject object to the teacher's set of subjects
            teacher_subjects[teacher].add(subject)

    # Filter only teachers who teach multiple subjects
    teacher_multiple_subjects = {teacher: subjects for teacher, subjects in teacher_subjects.items() if len(subjects) > 1}

    # Print final result (optional)
    # print(teacher_multiple_subjects)

    # First Pass: Assign subjects without checking if the teacher is already occupied
    for teacher, subjects in teacher_multiple_subjects.items():
        # Process each subject for the teacher
        for subject in subjects:
            # Only assign the subject if it belongs to the class for the current empty slot
            # print('Subject:', subject)

            # Loop through each class
            for cls in Class1.objects.all():
                # print('Class:', cls.id)
                
                if subject in cls.subjects.all():  # Ensure subject is part of the current class
                    hours_remaining = subject.contact_hours
                    # print('Hours remaining:', hours_remaining)
                    # print('Contact hours:', subject.contact_hours)

                    # Collect available slots for this class
                    available_slots = [entry for entry in empty_slots if entry['cls'].id == cls.id]
                    # print('Available slots:', available_slots)
                    # Shuffle to get a random order
                    shuffle(available_slots)
                    
                    # Assign slots
                    for entry in available_slots:
                        if hours_remaining <= 0:
                            break
                        # Ensure the slot is available and not already occupied
                        if not TimetableEntry1.objects.filter(day=entry['day'], period=entry['period'], cls=cls, subject=subject).exists():
                            # Initially, we skip the check for teacher conflict
                            TimetableEntry1.objects.create(
                                day=entry['day'],
                                period=entry['period'],
                                cls=entry['cls'],
                                subject=subject,
                                teacher=teacher
                            )
                            hours_remaining -= 1
                            # print('Hours remaining after assignment:', hours_remaining)
                            empty_slots.remove(entry)
                            if hours_remaining == 0:
                                break  # Exit loop when all hours are assigned
                        else:
                            print(f"Slot already occupied for subject {subject.name} in class {cls.name} on {entry['day']} period {entry['period']}")
                    
                    # If the subject is not assigned yet and there are no available slots left, print a message
                    if hours_remaining > 0:
                        print(f"No available slots for {subject.name} in class {cls.name}")
    empty_slots = []
    # Calculate empty slots by filtering out occupied ones from the timetable
    for cls in classes:
        # Get all periods for this class
        timetable_entries = TimetableEntry1.objects.filter(cls=cls)

        # Initialize a list of all possible slots for this class
        full_slots = []
        for day in days:
            for period in periods:
                full_slots.append({'day': day, 'period': period, 'cls': cls})

        # Filter out the slots already occupied in the timetable
        
        for slot in full_slots:
            if not timetable_entries.filter(
                day=slot['day'], 
                period=slot['period'],
                cls=slot['cls']
            ).exists():
                empty_slots.append(slot)
    print('emptyslots',empty_slots)
    
    
    # Second Pass: Check for teacher conflicts and reassign if necessary
    for teacher in teacher_multiple_subjects.keys():
        # Find all timetable entries for this teacher
        teacher_entries = TimetableEntry1.objects.filter(teacher=teacher)
        
        # Dictionary to track periods and days where the teacher is already scheduled
        occupied_slots = {}
        
        # Loop through each entry for this teacher
        for entry in teacher_entries:
            slot_key = (entry.day, entry.period)
            
            if slot_key in occupied_slots:
                # Conflict found: Teacher is already assigned in this slot
                conflicting_entry = occupied_slots[slot_key]
                # print(f"Conflict found: Teacher {teacher} is scheduled for both {conflicting_entry.subject.name} and {entry.subject.name} on {entry.day}, period {entry.period}.")
                
                # Try to reassign one of the subjects (you can choose which one to reassign)
                reassign_entry = entry  # For example, reassign the current entry
                reassign_cls = reassign_entry.cls
                reassign_subject = reassign_entry.subject
                
                # Collect available slots for reassignment
                available_slots = [e for e in empty_slots if e['cls'] == reassign_cls]
                shuffle(available_slots)
                
                # Find a new slot for the conflicting subject
                for new_entry in available_slots:
                    if not TimetableEntry1.objects.filter(day=new_entry['day'], period=new_entry['period'], teacher=teacher).exists():
                        # Reassign to a new slot
                        TimetableEntry1.objects.filter(id=reassign_entry.id).update(
                            day=new_entry['day'],
                            period=new_entry['period']
                        )
                        # print(f"Reassigned subject {reassign_subject.name} to {new_entry['day']} period {new_entry['period']} for class {reassign_cls.name}.")
                        empty_slots.remove(new_entry)
                        break
            else:
                # No conflict, mark the slot as occupied by this teacher
                occupied_slots[slot_key] = entry

    # Flatten the list of subjects from teacher_multiple_subjects
    teacher_subject_ids = [subject.id for subjects in teacher_multiple_subjects.values() for subject in subjects]

    # Identify remaining subjects by excluding subjects from teacher_multiple_subjects
    remaining_subjects = uncommon_subjects.exclude(id__in=teacher_subject_ids)
    print('remaining_subjects',remaining_subjects)
    
    empty_slots = []
    # Calculate empty slots by filtering out occupied ones from the timetable
    for cls in classes:
        # Get all periods for this class
        timetable_entries = TimetableEntry1.objects.filter(cls=cls)

        # Initialize a list of all possible slots for this class
        full_slots = []
        for day in days:
            for period in periods:
                full_slots.append({'day': day, 'period': period, 'cls': cls})

        # Filter out the slots already occupied in the timetable
        
        for slot in full_slots:
            if not timetable_entries.filter(
                day=slot['day'], 
                period=slot['period'],
                cls=slot['cls']
            ).exists():
                empty_slots.append(slot)
    print('emptyslots',empty_slots)
    

    for cls in Class1.objects.all():
        class_subjects = cls.subjects.all()  # Get all subjects for this class

        for subject in remaining_subjects:
            if subject in class_subjects:  # Only assign if the subject is in the current class
                hours_remaining = subject.contact_hours

                # Collect available slots for this class
                available_slots = [entry for entry in empty_slots if entry['cls'].id == cls.id]
                shuffle(available_slots)  # Shuffle to ensure random assignment
                
                # Assign slots
                for entry in available_slots:
                    if hours_remaining <= 0:
                        break  # Stop if all hours are assigned
                    
                    # Ensure the slot is available and not already occupied
                    if not TimetableEntry1.objects.filter(day=entry['day'], period=entry['period'], cls=cls, subject=subject).exists():
                        # Check if the teacher is available for this slot
                        if not TimetableEntry1.objects.filter(day=entry['day'], period=entry['period'], teacher=subject.teacher).exists():
                            # Create a new timetable entry
                            TimetableEntry1.objects.create(
                                day=entry['day'],
                                period=entry['period'],
                                cls=entry['cls'],
                                subject=subject,
                                teacher=subject.teacher
                            )
                            hours_remaining -= 1  # Decrease remaining contact hours
                            empty_slots.remove(entry)  # Remove the slot from available slots

                    # Exit loop when all hours for this subject are assigned
                    if hours_remaining == 0:
                        break
    return HttpResponse("Timetable generated successfully!")
        

from django.shortcuts import render
from .models import TimetableEntry1, Class1

def timetable_view(request):
    # Get all classes
    classes = Class1.objects.all()
    
    # Define the days and periods
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = [1, 2, 3, 4, 5]  # Assuming 5 periods per day

    # Initialize a dictionary to hold timetable data
    timetable_data = {cls: {day: {period: None for period in periods} for day in days} for cls in classes}

    # Populate the timetable dictionary with entries
    entries = TimetableEntry1.objects.all()
    for entry in entries:
        timetable_data[entry.cls][entry.day][entry.period] = entry

    # Create a context dictionary for the template
    context = {
        'timetable_data': timetable_data,
        'days': days,
        'periods': periods,
    }
    
    return render(request, 'view_timetable.html', context)

class TimetableView1(View):
    template_name = 'view_timetable1.html'  # Specify your template name here

    def get(self, request, *args, **kwargs):
        # Get all classes
        classes = Class1.objects.all()
        teachers= Teacher1.objects.all()
        
        # Define the days and periods
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        periods = [1, 2, 3, 4, 5]  # Assuming 5 periods per day

        # Initialize a dictionary to hold timetable data
        timetable_data = {cls: {day: {period: None for period in periods} for day in days} for cls in classes}

        # Populate the timetable dictionary with entries
        entries = TimetableEntry1.objects.all()
        for entry in entries:
            timetable_data[entry.cls][entry.day][entry.period] = entry

        # Create a context dictionary for the template
        context = {
            'timetable_data': timetable_data,
            'days': days,
            'periods': periods,
            'teachers':teachers
        }
        
        return render(request, self.template_name, context)
from django.shortcuts import render, redirect
from django.views import View
from .models import Teacher1, Subject1, Class1

# Insert Teacher

class InsertTeacherView(View):
        def get(self,request):
            subjects = Subject1.objects.all() 
            teachers = Teacher1.objects.all()   # Fetch all subjects for the dropdown
            return render(request, 'insert_data.html', {'subjects': subjects,'teachers':teachers})

        def post(self, request):
            teacher_name = request.POST.get('teacher_name')
            if teacher_name:
                Teacher1.objects.create(name=teacher_name)
            return redirect('insert_teacher')


# Insert Subject
class InsertSubjectView(View):
    def get(self, request):
        subjects = Subject1.objects.all() 
        teachers = Teacher1.objects.all()   # Fetch all subjects for the dropdown
        return render(request, 'insert_data.html', {'subjects': subjects,'teachers':teachers})

    def post(self, request):
        subject_name = request.POST.get('subject_name')
        contact_hours = request.POST.get('contact_hours')
        teacher_id = request.POST.get('teacher')
        teacher = Teacher1.objects.get(id=teacher_id)

        if subject_name and contact_hours and teacher:
            Subject1.objects.create(name=subject_name, contact_hours=contact_hours, teacher=teacher)
        return redirect('insert_subject')


# Insert Class
class InsertClassView(View):
    def get(self, request):
        subjects = Subject1.objects.all() 
        teachers = Teacher1.objects.all()   # Fetch all subjects for the dropdown
        return render(request, 'insert_data.html', {'subjects': subjects})

    def post(self, request):
        class_name = request.POST.get('class_name')
        subject_ids = request.POST.getlist('subjects')  # Get multiple subjects
        if class_name and subject_ids:
            class_instance = Class1.objects.create(name=class_name)
            subjects = Subject1.objects.filter(id__in=subject_ids)
            class_instance.subjects.set(subjects)
            class_instance.save()
        return redirect('insert_class')

from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.shortcuts import render
from .models import Teacher1, Subject1, Class1

class Viewclass_subject_teachers(View):
    def get(self,request):
        subjects = Subject1.objects.all() 
        teachers = Teacher1.objects.all() 
        classes= Class1.objects.all() 
        return render(request,'edit_data.html',{'subjects': subjects,'teachers':teachers,'classes':classes})

class EditTeacherView(UpdateView):
    model = Teacher1
    template_name = 'edit_teacher.html'
    fields = ['name']
    success_url = reverse_lazy('view_data')  # Redirect to the list view after successful edit

class EditSubjectView(UpdateView):
    model = Subject1
    template_name = 'edit_subject.html'
    fields = ['name', 'contact_hours', 'teacher']
    success_url = reverse_lazy('view_data')  # Redirect to the list view after successful edit

class EditClassView(UpdateView):
    model = Class1
    template_name = 'edit_class.html'
    fields = ['name', 'subjects']
    success_url = reverse_lazy('view_data')  # Redirect to the list view after successful edit

# Optional: Render the list view in case you want to have a separate view for viewing data
def view_data(request):
    teachers = Teacher1.objects.all()
    subjects = Subject1.objects.all()
    classes = Class1.objects.all()
    return render(request, 'view_data.html', {
        'teachers': teachers,
        'subjects': subjects,
        'classes': classes
    })
from datetime import datetime, timedelta

def generate_time_slots(start_time, end_time, slot_duration_minutes=60):
    """
    Generates time slots for a given start and end time.
    """
    start_time_obj = datetime.combine(datetime.today(), start_time)
    end_time_obj = datetime.combine(datetime.today(), end_time)
    
    time_slots = []
    while start_time_obj + timedelta(minutes=slot_duration_minutes) <= end_time_obj:
        slot_end_time = start_time_obj + timedelta(minutes=slot_duration_minutes)
        time_slots.append((start_time_obj.time(), slot_end_time.time()))
        start_time_obj = slot_end_time

    return time_slots
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.utils import timezone
from calendar import monthrange
from datetime import timedelta, date

from .models import Auditorium, TimeSlot, Booking, WorkingDay


from django.utils import timezone
from django.views import View
from django.shortcuts import get_object_or_404, render
from datetime import date, timedelta
from calendar import monthrange
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.utils import timezone
from calendar import monthrange
from datetime import date, timedelta
from .models import Auditorium, Booking, TimeSlot

class AuditoriumBookingView(View):
    def get(self, request, auditorium_id):
            auditorium = get_object_or_404(Auditorium, id=auditorium_id)

            # Get the current date or use a provided date
            today = timezone.now().date()
            selected_year = int(request.GET.get('year', today.year))
            selected_month = int(request.GET.get('month', today.month))

            selected_date = date(selected_year, selected_month, 1)
            num_days_in_month = monthrange(selected_date.year, selected_date.month)[1]

            first_day_weekday = selected_date.weekday()  # Monday is 0, Sunday is 6

            # Fetch bookings for the selected month
            first_day = selected_date
            last_day = selected_date + timedelta(days=num_days_in_month - 1)
            bookings = Booking.objects.filter(auditorium=auditorium, date__range=[first_day, last_day])

            # Create a dictionary of bookings per day
            bookings_by_date = {day: [] for day in range(1, num_days_in_month + 1)}
            for booking in bookings:
                day = booking.date.day
                bookings_by_date[day].append(booking.time_slot)

            calendar_days = []
            for day in range(1, num_days_in_month + 1):
                current_date = date(selected_date.year, selected_date.month, day)
                day_name = current_date.strftime('%A')  # Get day name like 'Monday', 'Tuesday'
                
                # Fetch the working day for this specific day of the week
                working_day = WorkingDay.objects.filter(auditorium=auditorium, day=day_name).first()
                # print("working_day",working_day)
                slots_with_status = []

                if working_day:
                    # Fetch only time slots that belong to this working day
                    time_slots = TimeSlot.objects.filter(working_day=working_day)
                    day_bookings = bookings_by_date.get(day, [])
                    print("time_slots",time_slots)
                    for slot in time_slots:
                        is_booked = any(booking == slot for booking in day_bookings)
                        slots_with_status.append({
                            'slot': slot,
                            'status': 'occupied' if is_booked else 'vacant'
                        })

                calendar_days.append({
                    'date': current_date,
                    'slots_with_status': slots_with_status
                })

            # Add the range of empty days before the first day of the month
            empty_days_before_first = list(range(first_day_weekday))

            context = {
                'auditorium': auditorium,
                'calendar_days': calendar_days,
                'selected_date': selected_date,
                'selected_year': selected_year,
                'selected_month': selected_month,
                'first_day_weekday': first_day_weekday,
                'empty_days_before_first': empty_days_before_first,
            }
            # print(calendar_days)

            return render(request, 'auditorium_booking.html', context)
    def post(self, request, auditorium_id):
        # Handle booking when the user selects a time slot
        auditorium = get_object_or_404(Auditorium, id=auditorium_id)
        user = request.user
        slot_id = request.POST.get('slot_id')
        selected_date = request.POST.get('selected_date')
        purpose=request.POST.get('purpose')
    

        if slot_id and selected_date:
            time_slot = get_object_or_404(TimeSlot, id=slot_id)
            booking_date = datetime.strptime(selected_date, '%b. %d, %Y').date()
            # booking_date = date.fromisoformat(selected_date)

            # Check if the time slot is already booked
            if not Booking.objects.filter(auditorium=auditorium, date=booking_date, time_slot=time_slot).exists():
                Booking.objects.create(
                    auditorium=auditorium,
                    user=user,
                    date=booking_date,
                    time_slot=time_slot,
                    purpose=purpose
                )
        return self.get(request, auditorium_id)

class BookingConfirmationView(View):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        context = {'booking': booking}
        return render(request, 'booking_confirmation.html', context)
    
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from .models import Booking
from .forms import BookingForm

class EditBookingView(View):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        form = BookingForm(instance=booking)
        return render(request, 'edit_booking.html', {'form': form, 'booking': booking})

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('auditorium_booking', auditorium_id=booking.auditorium.id)
        return render(request, 'edit_booking.html', {'form': form, 'booking': booking})
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from .models import Booking

class DeleteBookingView(View):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        return render(request, 'delete_confirmation.html', {'booking': booking})

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        booking.delete()
        return redirect('adminauditorium_booking', auditorium_id=booking.auditorium.id)
class AdminAuditoriumBookingView(View):
    def get(self, request, auditorium_id):
        auditorium = get_object_or_404(Auditorium, id=auditorium_id)

        # Get the current date or use a provided date
        today = timezone.now().date()
        selected_year = int(request.GET.get('year', today.year))
        selected_month = int(request.GET.get('month', today.month))

        selected_date = date(selected_year, selected_month, 1)
        num_days_in_month = monthrange(selected_date.year, selected_date.month)[1]

        first_day_weekday = selected_date.weekday()  # Monday is 0, Sunday is 6

        # Fetch bookings for the selected month
        first_day = selected_date
        last_day = selected_date + timedelta(days=num_days_in_month - 1)
        bookings = Booking.objects.filter(auditorium=auditorium, date__range=[first_day, last_day])

        # Create a dictionary of bookings per day
        bookings_by_date = {day: [] for day in range(1, num_days_in_month + 1)}
        for booking in bookings:
            day = booking.date.day
            bookings_by_date[day].append(booking)

        calendar_days = []
        for day in range(1, num_days_in_month + 1):
            current_date = date(selected_date.year, selected_date.month, day)
            day_name = current_date.strftime('%A')  # Get day name like 'Monday', 'Tuesday'

            # Fetch the working day for this specific day of the week
            working_day = WorkingDay.objects.filter(auditorium=auditorium, day=day_name).first()
            slots_with_status = []

            if working_day:
                # Fetch only time slots that belong to this working day
                time_slots = TimeSlot.objects.filter(working_day=working_day)
                day_bookings = bookings_by_date.get(day, [])
                for slot in time_slots:
                    # Check if the slot is booked
                    booked_slot = next((b for b in day_bookings if b.time_slot == slot), None)
                    slots_with_status.append({
                        'slot': slot,
                        'status': 'occupied' if booked_slot else 'vacant',
                        'booking': booked_slot,  # Pass the booking object if it's occupied
                    })

            calendar_days.append({
                'date': current_date,
                'slots_with_status': slots_with_status
            })

        empty_days_before_first = list(range(first_day_weekday))

        context = {
            'auditorium': auditorium,
            'calendar_days': calendar_days,
            'selected_date': selected_date,
            'selected_year': selected_year,
            'selected_month': selected_month,
            'first_day_weekday': first_day_weekday,
            'empty_days_before_first': empty_days_before_first,
        }

        return render(request, 'edit_auditorium_booking.html', context)

