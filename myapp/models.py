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