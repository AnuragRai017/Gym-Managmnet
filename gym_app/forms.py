from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Member, Class, Payment, MembershipPlan
from .models import Member, Class, ClassAttendance

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    name = forms.CharField(max_length=100)  # Add this line
    phone_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    membership_plan = forms.ModelChoiceField(
        queryset=MembershipPlan.objects.all(),
        empty_label=None,
        widget=forms.RadioSelect
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'name', 'phone_number', 'address', 'membership_plan']  # Update this line



class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'description', 'instructor', 'start_time', 'end_time', 'max_capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instructor': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'max_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instructor'].choices = Class.INSTRUCTOR_CHOICES

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'phone_number', 'address', 'membership_plan', 'profile_picture']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'membership_plan': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control-file', 
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({
            'class': 'custom-file-input',
            'id': 'customFile'
        })
        self.fields['profile_picture'].widget.attrs.update({'accept': 'image/*'})

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if profile_picture.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file too large ( > 5MB )")
        return profile_picture

class ClassAttendanceForm(forms.ModelForm):
    class Meta:
        model = ClassAttendance
        fields = ['member']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-control'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount']