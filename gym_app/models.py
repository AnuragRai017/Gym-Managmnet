from django.db import models
from django.utils import timezone
from datetime import timedelta

class MembershipPlan(models.Model):
    DURATION_CHOICES = [
        (30, '1 Month'),
        (90, '3 Months'),
        (180, '6 Months'),
        (365, '12 Months'),
    ]
    
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.IntegerField(choices=DURATION_CHOICES)

    def __str__(self):
        return f"{self.name} - {self.get_duration_display()} (${self.price})"

class Member(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    email = models.EmailField()
    membership_plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True)
    join_date = models.DateField(auto_now_add=True)
    membership_end_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)



    def __str__(self):
        return self.name

    def is_membership_active(self):
        return self.membership_end_date >= timezone.now().date() if self.membership_end_date else False

    def save(self, *args, **kwargs):
        if self.membership_plan and not self.membership_end_date:
            self.membership_end_date = timezone.now().date() + timedelta(days=self.membership_plan.duration)
        super().save(*args, **kwargs)

class Invoice(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_issued = models.DateField(auto_now_add=True)
    date_due = models.DateField()
    paid = models.BooleanField(default=False)
    whatsapp_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice {self.id} for {self.member.name}"

class Staff(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    hire_date = models.DateField()

    def __str__(self):
        return self.name

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    purchase_date = models.DateField()

class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.member} - {self.check_in_time.date()}"

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date_paid = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Payment of ${self.amount} for Invoice {self.invoice.id}"

class Class(models.Model):
    INSTRUCTOR_CHOICES = [
        ('Dinesh Bhaiya', 'Dinesh Bhaiya'),
        ('Anita Tai', 'Anita Tai'),
        ('Rohit Sir', 'Rohit Sir'),
        ('Priya Madam', 'Priya Madam'),
        ('Vijay Master', 'Vijay Master'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    instructor = models.CharField(max_length=50, choices=INSTRUCTOR_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_capacity = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class ClassAttendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    gym_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ('member', 'gym_class')

    def __str__(self):
        return f"{self.member} - {self.gym_class}"