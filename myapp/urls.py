from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('secure/', views.secure_page, name='secure_page'),
    path('submit-report/', views.submit_report, name='submit_report'),
    path('upload-evidence/<int:report_id>/', views.upload_evidence, name='upload_evidence'),
    path('view-report/<int:report_id>/', views.view_report, name='view_report'),
    path('my-reports/', views.my_reports, name='my_reports'),
    path('public-reports/', views.public_reports, name='public_reports'),
    path('scam-websites/', views.scam_websites, name='scam_websites'),
    path('profile/', views.profile, name='profile'),
    path('add-comment/<int:report_id>/', views.add_comment, name='add_comment'),
    path('add-evidence/<int:report_id>/', views.add_evidence, name='add_evidence'),
    path('verify-comment/<int:comment_id>/', views.verify_comment, name='verify_comment'),
    path('verify-evidence/<int:evidence_id>/', views.verify_evidence, name='verify_evidence'),
    path('donate/<int:report_id>/', views.donate, name='donate'),
    path('donate/', views.donate, name='donate_general'),
    
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
] 