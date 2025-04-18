from .models import ScamReport

def user_profile_info(request):
    if request.user.is_authenticated:
        verified_reports_count = ScamReport.objects.filter(
            user=request.user,
            status='verified'
        ).count()
    else:
        verified_reports_count = 0
    
    return {
        'verified_reports_count': verified_reports_count
    } 