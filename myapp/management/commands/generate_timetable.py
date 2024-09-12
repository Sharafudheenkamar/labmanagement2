from django.core.management.base import BaseCommand
from django.utils.timezone import now
from ortools.sat.python import cp_model
from myapp.models import Teacher1, Subject1, Class1, TimetableEntry1

class Command(BaseCommand):
    help = 'Generate a timetable for multiple classes'


    def handle(self, *args, **kwargs):
        model = cp_model.CpModel()

        # Get data from the database
        teachers = list(Teacher1.objects.all())
        subjects = list(Subject1.objects.all())
        classes = list(Class1.objects.all())
        num_periods_per_day = 5
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        # Variables
        timetable = {}
        for cls in classes:
            for day in days_of_week:
                for period in range(num_periods_per_day):
                    timetable[(cls.id, day, period)] = model.NewIntVar(0, len(subjects) - 1, f'timetable_{cls.id}_{day}_{period}')

        # Constraints
        # 1. Ensure subjects are scheduled enough times
        for subj in subjects:
            subject_vars = []
            for cls in classes:
                for day in days_of_week:
                    for period in range(num_periods_per_day):
                        if timetable[(cls.id, day, period)] == subj.id:
                            subject_vars.append(1)
                        else:
                            subject_vars.append(0)
            # Sum the occurrences and ensure the subject is scheduled enough times
            model.Add(cp_model.LinearExpr.Sum(subject_vars) >= subj.contact_hours)

        # 2. Common subjects should come together
        for subj in subjects:
            for day in days_of_week:
                for period in range(num_periods_per_day):
                    common_periods = []
                    for cls in classes:
                        if timetable[(cls.id, day, period)] == subj.id:
                            common_periods.append(1)
                        else:
                            common_periods.append(0)
                    # Ensure common subjects are taught in the same period across multiple classes
                    model.Add(cp_model.LinearExpr.Sum(common_periods) >= len(classes) * 0.8)  # Adjust 0.8 as needed

        # 3. Ensure a teacher doesn't have multiple subjects in the same timeslot
        for teacher in teachers:
            for day in days_of_week:
                for period in range(num_periods_per_day):
                    teacher_periods = []
                    for cls in classes:
                        subject_id = timetable[(cls.id, day, period)]
                        # Assuming each subject has a list of teachers, check if the teacher is assigned to this subject
                        if teacher in Subject1.objects.get(id=subject_id).teachers.all():
                            teacher_periods.append(1)
                        else:
                            teacher_periods.append(0)
                    # Ensure the teacher does not have multiple subjects in the same timeslot
                    model.Add(cp_model.LinearExpr.Sum(teacher_periods) <= 1)

        # Solve the model
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL:
            # Save results to the database
            for cls in classes:
                for day in days_of_week:
                    for period in range(num_periods_per_day):
                        subject_id = solver.Value(timetable[(cls.id, day, period)])
                        subject = Subject1.objects.get(id=subject_id)
                        teacher = subject.teacher
                        TimetableEntry1.objects.create(
                            day=day,
                            period=period,
                            cls=cls,
                            subject=subject,
                            teacher=teacher
                        )
            self.stdout.write(self.style.SUCCESS('Timetable generated successfully!'))
        else:
            self.stdout.write(self.style.ERROR('Failed to generate timetable'))
