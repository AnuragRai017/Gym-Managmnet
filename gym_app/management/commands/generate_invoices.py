from django.core.management.base import BaseCommand
from django.utils import timezone
from gym_app.models import Member, Invoice
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate invoices for members due for renewal'

    def handle(self, *args, **options):
        today = timezone.now().date()
        due_members = Member.objects.filter(membership_end_date__lte=today + timedelta(days=7))
        
        invoices_created = 0
        for member in due_members:
            # Check if an invoice already exists for this renewal period
            existing_invoice = Invoice.objects.filter(
                member=member,
                date_issued__gte=today - timedelta(days=7),
                paid=False
            ).exists()
            
            if not existing_invoice and member.membership_plan:
                Invoice.objects.create(
                    member=member,
                    amount=member.membership_plan.price,
                    date_due=member.membership_end_date
                )
                invoices_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {invoices_created} invoices'))