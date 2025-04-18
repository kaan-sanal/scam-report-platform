import requests
from django.contrib.auth.models import User
from .models import UserProfile
from django.utils import timezone
import json

class UserTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            ip_address = self.get_client_ip(request)
            location = self.get_location_from_ip(ip_address)
            
            try:
                profile = UserProfile.objects.get(user=request.user)
                profile.last_ip = ip_address
                profile.last_location = location
                profile.last_login_time = timezone.now()
                profile.save()
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(
                    user=request.user,
                    last_ip=ip_address,
                    last_location=location
                )

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_location_from_ip(self, ip):
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}')
            data = response.json()
            if data['status'] == 'success':
                return f"{data['city']}, {data['country']} ({data['isp']})"
            return "Konum bilgisi alınamadı"
        except:
            return "Konum bilgisi alınamadı" 