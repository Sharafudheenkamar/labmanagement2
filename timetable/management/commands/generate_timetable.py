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
        # 1. Subjects should be distributed across the week
        for cls in classes:
            for subj in subjects:
                subject_periods = []
                for day in days_of_week:
                    for period in range(num_periods_per_day):
                        subject_periods.append(timetable[(cls.id, day, period)] == subj.id)
                # Create a linear expression for the constraint
                expr = cp_model.LinearExpr.Sum(subject_periods)
                model.Add(expr >= subj.contact_hours)

        # 2. Common subjects of multiple classes should come together
        for subj in subjects:
            common_subject_periods = []
            for day in days_of_week:
                for period in range(num_periods_per_day):
                    common_periods = []
                    for cls in classes:
                        common_periods.append(timetable[(cls.id, day, period)] == subj.id)
                    # Create a linear expression for the constraint
                    expr = cp_model.LinearExpr.Sum(common_periods)
                    model.Add(expr >= len(classes) * 0.8)  # Adjust 0.8 as needed

        # 3. Multiple subjects taken by a teacher shouldn’t come in the same timeslot
        for teacher in teachers:
            for day in days_of_week:
                for period in range(num_periods_per_day):
                    teacher_periods = []
                    for cls in classes:
                        subject_id = timetable[(cls.id, day, period)]
                        subject = Subject1.objects.get(id=subject_id)
                        if subject.teacher == teacher:
                            teacher_periods.append(1)
                    # Create a linear expression for the constraint
                    expr = cp_model.LinearExpr.Sum(teacher_periods)
                    model.Add(expr <= 1)

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