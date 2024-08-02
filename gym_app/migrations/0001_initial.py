# Generated by Django 5.0.4 on 2024-07-05 14:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

def create_membership_plans(apps, schema_editor):
    MembershipPlan = apps.get_model('gym_app', 'MembershipPlan')
    MembershipPlan.objects.create(name='Basic 1 Month', price='29.99', duration=30)
    MembershipPlan.objects.create(name='Basic 3 Months', price='79.99', duration=90)
    MembershipPlan.objects.create(name='Basic 6 Months', price='149.99', duration=180)
    MembershipPlan.objects.create(name='Basic 12 Months', price='279.99', duration=365)
    MembershipPlan.objects.create(name='Premium 1 Month', price='49.99', duration=30)
    MembershipPlan.objects.create(name='Premium 3 Months', price='129.99', duration=90)
    MembershipPlan.objects.create(name='Premium 6 Months', price='239.99', duration=180)
    MembershipPlan.objects.create(name='Premium 12 Months', price='449.99', duration=365)

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('quantity', models.IntegerField()),
                ('purchase_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='MembershipPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('duration', models.IntegerField(choices=[(30, '1 Month'), (90, '3 Months'), (180, '6 Months'), (365, '12 Months')])),
            ],
        ),
        migrations.RunPython(create_membership_plans),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('join_date', models.DateField(auto_now_add=True)),
                ('membership_end_date', models.DateField(blank=True, null=True)),
                ('barcode', models.ImageField(blank=True, upload_to='barcodes/')),
                ('encrypted_barcode_data', models.BinaryField(blank=True, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('membership_plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='gym_app.membershipplan')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('date_issued', models.DateField(auto_now_add=True)),
                ('date_due', models.DateField()),
                ('paid', models.BooleanField(default=False)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gym_app.member')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in_time', models.DateTimeField(auto_now_add=True)),
                ('check_out_time', models.DateTimeField(blank=True, null=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gym_app.member')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('date_paid', models.DateField(auto_now_add=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gym_app.invoice')),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=50)),
                ('hire_date', models.DateField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('max_capacity', models.IntegerField()),
                ('instructor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='gym_app.staff')),
            ],
        ),
        migrations.CreateModel(
            name='ClassAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attended', models.BooleanField(default=False)),
                ('gym_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gym_app.class')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gym_app.member')),
            ],
            options={
                'unique_together': {('member', 'gym_class')},
            },
        ),
    ]