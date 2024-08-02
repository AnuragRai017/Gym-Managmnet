from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Member, Class, ClassAttendance, Attendance, Invoice, Payment, MembershipPlan,Equipment
from .forms import MemberForm, ClassForm, PaymentForm
from datetime import timedelta  # Make sure this import is presen
from .forms import ClassAttendanceForm
import pywhatkit
from django.db.models import Sum
import time

def is_admin(user):
    return user.is_authenticated and user.is_staff

def is_staff(user):
    return user.is_authenticated and user.is_staff

@login_required
def home(request):
    today = timezone.now().date()
    context = {
        'member_count': Member.objects.count(),
        'active_classes': Class.objects.filter(start_time__date=today).count(),
        'pending_invoices': Invoice.objects.filter(paid=False).count(),
        'today_attendance': Attendance.objects.filter(check_in_time__date=today).count(),
        'equipment_count': Equipment.objects.count(),
        'monthly_revenue': Invoice.objects.filter(date_issued__month=today.month, paid=True).aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    return render(request, 'gym_app/home.html', context)

@login_required
@user_passes_test(is_staff)
def member_list(request):
    members = Member.objects.all().order_by('-join_date')  # Order by join date, newest first
    return render(request, 'gym_app/member_list.html', {'members': members})

@login_required
@user_passes_test(lambda u: u.is_staff)
def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'gym_app/member_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    return render(request, 'gym_app/member_detail.html', {'member': member})


@login_required
@user_passes_test(lambda u: u.is_staff)
def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            print("Files in request:", request.FILES)
            print("Profile picture in form:", form.cleaned_data.get('profile_picture'))
            member = form.save()
            print(f"Profile picture saved: {member.profile_picture}")
            return redirect('member_detail', pk=pk)
        else:
            print("Form errors:", form.errors)
    else:
        form = MemberForm(instance=member)
    return render(request, 'gym_app/member_form.html', {'form': form})



@login_required
@user_passes_test(is_admin)
def class_list(request):
    classes = Class.objects.all().order_by('start_time')
    return render(request, 'gym_app/class_list.html', {'classes': classes})

@login_required
@user_passes_test(is_admin)
def class_detail(request, pk):
    gym_class = get_object_or_404(Class, pk=pk)
    attendees = ClassAttendance.objects.filter(gym_class=gym_class)
    return render(request, 'gym_app/class_detail.html', {'gym_class': gym_class, 'attendees': attendees})

@login_required
@user_passes_test(is_admin)
def class_create(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('class_list')
    else:
        form = ClassForm()
    return render(request, 'gym_app/class_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def class_update(request, pk):
    gym_class = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=gym_class)
        if form.is_valid():
            form.save()
            return redirect('class_detail', pk=pk)
    else:
        form = ClassForm(instance=gym_class)
    return render(request, 'gym_app/class_form.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def class_register(request, pk):
    gym_class = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        form = ClassAttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.gym_class = gym_class
            attendance.save()
            messages.success(request, f"{attendance.member.name} has been registered for {gym_class.name}")
            return redirect('class_detail', pk=pk)
    else:
        form = ClassAttendanceForm()
    return render(request, 'gym_app/class_register.html', {'form': form, 'gym_class': gym_class})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    return redirect('login')

@user_passes_test(is_admin)
def staff_dashboard(request):
    classes = Class.objects.all().order_by('start_time')
    members = Member.objects.all()
    return render(request, 'gym_app/staff_dashboard.html', {'classes': classes, 'members': members})

@user_passes_test(is_admin)
def attendance_history(request):
    attendances = Attendance.objects.all().order_by('-check_in_time')
    return render(request, 'gym_app/attendance_history.html', {'attendances': attendances})

@login_required
@user_passes_test(lambda u: u.is_staff)
def billing_dashboard(request):
    invoices = Invoice.objects.all().order_by('-date_issued')
    context = {
        'invoices': invoices,
        'today': timezone.now().date(),
    }
    return render(request, 'gym_app/billing_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def send_invoice_whatsapp(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Prepare the message
    message = f"Dear {invoice.member.name},\n\n"
    message += f"This is regarding your invoice (ID: {invoice.id}).\n"
    message += f"Amount: ${invoice.amount}\n"
    message += f"Due date: {invoice.date_due}\n"
    
    if invoice.paid:
        message += f"Status: Paid\n"
        message += "Thank you for your payment!"
    else:
        message += f"Status: Unpaid\n"
        message += "Please make the payment at your earliest convenience.\n"
    
    message += "\nThank you for your business!"

    try:
        # Send the WhatsApp message
        phone_number = f"+91{invoice.member.phone_number}"  # Adjust country code as needed
        pywhatkit.sendwhatmsg_instantly(
            phone_no=phone_number,
            message=message,
            tab_close=True
        )
        
        # Mark the invoice as sent
        invoice.whatsapp_sent = True
        invoice.save()
        
        messages.success(request, f"Invoice {invoice.id} details sent to {invoice.member.name} via WhatsApp")
    except Exception as e:
        messages.error(request, f"Failed to send WhatsApp message: {str(e)}")
    
    return redirect('billing_dashboard')

@user_passes_test(is_admin)
def pay_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.save()
            invoice.paid = True
            invoice.save()
            return redirect('billing_dashboard')
    else:
        form = PaymentForm(initial={'amount': invoice.amount})
    return render(request, 'gym_app/pay_invoice.html', {'form': form, 'invoice': invoice})

@login_required
@user_passes_test(lambda u: u.is_staff)
def generate_invoice(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == 'POST':
        plan_id = request.POST.get('membership_plan')
        plan = get_object_or_404(MembershipPlan, id=plan_id)
        
        Invoice.objects.create(
            member=member,
            amount=plan.price,
            date_due=timezone.now().date() + timezone.timedelta(days=7)
        )
        messages.success(request, f"Invoice generated for {member.name}")
        return redirect('member_detail', pk=member.id)
    
    plans = MembershipPlan.objects.all()
    return render(request, 'gym_app/generate_invoice.html', {'member': member, 'plans': plans})


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_member(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.delete()
        messages.success(request, f"Member {member.name} has been deleted successfully.")
        return redirect('member_list')
    return render(request, 'gym_app/member_confirm_delete.html', {'member': member})


@login_required
@user_passes_test(lambda u: u.is_staff)
def active_members(request):
    active_members = Member.objects.filter(membership_end_date__gte=timezone.now().date())
    return render(request, 'gym_app/active_members.html', {'members': active_members})

@login_required
@user_passes_test(lambda u: u.is_staff)
def pending_invoices(request):
    pending_invoices = Invoice.objects.filter(paid=False)
    return render(request, 'gym_app/pending_invoices.html', {'invoices': pending_invoices})


@login_required
def home(request):
    today = timezone.now().date()
    context = {
        'member_count': Member.objects.count(),
        'active_classes': Class.objects.filter(start_time__date=today).count(),
        'pending_invoices': Invoice.objects.filter(paid=False).count(),
        'today_attendance': Attendance.objects.filter(check_in_time__date=today).count(),
        'equipment_count': Equipment.objects.count(),
        'monthly_revenue': Invoice.objects.filter(date_issued__month=today.month, paid=True).aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    return render(request, 'gym_app/home.html', context)