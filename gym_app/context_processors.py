from .models import Member
from django.utils import timezone


def debug_info(request):
    context = {}
    if request.user.is_authenticated and request.user.is_staff:
        context['user_id'] = request.user.id
        context['username'] = request.user.username
        context['is_staff'] = True
        try:
            members = Member.objects.all()
            context['total_members'] = members.count()
            context['active_members'] = members.filter(membership_end_date__gte=timezone.now().date()).count()
        except Exception as e:
            context['member_error'] = str(e)
    return context