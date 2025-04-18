from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import UserProfile, ScamReport, ReportComment, ReportVote, Donation, ReportEvidence, ScamEvidence

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'reputation_score', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('reputation_score', 'join_date', 'last_ip', 'last_location')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'reputation_score', 'is_verified')
        }),
        ('Statistics', {
            'fields': ('total_reports', 'verified_reports', 'flagged_reports', 'warning_count')
        }),
        ('Location Data', {
            'fields': ('last_ip', 'last_location', 'join_date')
        }),
    )

@admin.register(ScamReport)
class ScamReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'reporter', 'report_type', 'status', 'submission_date', 'is_public', 'view_count')
    list_filter = ('status', 'report_type', 'is_public', 'submission_date')
    search_fields = ('title', 'description', 'scam_url')
    readonly_fields = ('submission_date', 'view_count')
    date_hierarchy = 'submission_date'
    fieldsets = (
        ('Report Details', {
            'fields': ('title', 'reporter', 'report_type', 'description', 'scam_url')
        }),
        ('Domain Information', {
            'fields': ('domain_age', 'domain_registrar', 'domain_country', 'is_blacklisted', 'blacklist_details')
        }),
        ('Status', {
            'fields': ('status', 'is_public')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verification_date', 'flagged_by')
        }),
        ('Statistics', {
            'fields': ('view_count', 'submission_date')
        }),
    )
    actions = ['approve_reports', 'flag_reports', 'unflag_reports']

    def approve_reports(self, request, queryset):
        queryset.update(
            status='verified',
            verified_by=request.user,
            verification_date=timezone.now()
        )
    approve_reports.short_description = "Mark selected reports as verified"

    def flag_reports(self, request, queryset):
        queryset.update(
            is_flagged=True,
            flagged_by=request.user
        )
    flag_reports.short_description = "Flag selected reports as suspicious"

    def unflag_reports(self, request, queryset):
        queryset.update(
            is_flagged=False,
            flagged_by=None
        )
    unflag_reports.short_description = "Remove flag from selected reports"

@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'report', 'created_at', 'is_verified', 'verification_status')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('content', 'user__username', 'report__title')
    readonly_fields = ('created_at', 'verification_date')
    fieldsets = (
        ('Comment Details', {
            'fields': ('report', 'user', 'content')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verification_date')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    actions = ['verify_comments', 'unverify_comments']

    def verification_status(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Verified by {}</span>', obj.verified_by.email if obj.verified_by else 'Unknown')
        return format_html('<span style="color: orange;">Pending</span>')
    verification_status.short_description = 'Verification'

    def verify_comments(self, request, queryset):
        queryset.update(
            is_verified=True, 
            verified_by=request.user,
            verification_date=timezone.now()
        )
    verify_comments.short_description = "Mark selected comments as verified"

    def unverify_comments(self, request, queryset):
        queryset.update(
            is_verified=False, 
            verified_by=None,
            verification_date=None
        )
    unverify_comments.short_description = "Mark selected comments as unverified"

@admin.register(ReportEvidence)
class ReportEvidenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'report', 'user_email', 'uploaded_at', 'is_verified', 'verification_status')
    list_filter = ('is_verified', 'uploaded_at')
    search_fields = ('title', 'description', 'report__title', 'user__email')
    readonly_fields = ('uploaded_at', 'verification_date')
    date_hierarchy = 'uploaded_at'
    fieldsets = (
        ('Evidence Details', {
            'fields': ('report', 'user', 'title', 'description', 'file')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verification_date')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at',)
        }),
    )
    actions = ['verify_evidence', 'unverify_evidence']

    def user_email(self, obj):
        return obj.user.email if obj.user else 'Anonymous'
    user_email.short_description = 'Uploaded By'

    def verification_status(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Verified by {}</span>', obj.verified_by.email if obj.verified_by else 'Unknown')
        return format_html('<span style="color: orange;">Pending</span>')
    verification_status.short_description = 'Verification'

    def verify_evidence(self, request, queryset):
        queryset.update(
            is_verified=True,
            verified_by=request.user,
            verification_date=timezone.now()
        )
    verify_evidence.short_description = "Mark selected evidence as verified"

    def unverify_evidence(self, request, queryset):
        queryset.update(
            is_verified=False,
            verified_by=None,
            verification_date=None
        )
    unverify_evidence.short_description = "Mark selected evidence as unverified"

@admin.register(ScamEvidence)
class ScamEvidenceAdmin(admin.ModelAdmin):
    list_display = ('report', 'user_email', 'file_type', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('report__title', 'description')
    readonly_fields = ('uploaded_at', 'file_type', 'metadata')
    date_hierarchy = 'uploaded_at'
    fieldsets = (
        ('Evidence Details', {
            'fields': ('report', 'file', 'description')
        }),
        ('File Information', {
            'fields': ('file_type', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at',)
        }),
    )

    def user_email(self, obj):
        return obj.report.reporter.email if obj.report.reporter else 'Anonymous'
    user_email.short_description = 'Uploaded By'

@admin.register(ReportVote)
class ReportVoteAdmin(admin.ModelAdmin):
    list_display = ('report', 'user', 'vote_type', 'vote_date')
    list_filter = ('vote_type', 'vote_date')
    search_fields = ('report__title', 'user__username')
    readonly_fields = ('vote_date',)
    fieldsets = (
        ('Vote Details', {
            'fields': ('report', 'user', 'vote_type')
        }),
        ('Timestamp', {
            'fields': ('vote_date',)
        }),
    )

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_display', 'payment_status', 'donation_date', 'is_anonymous')
    list_filter = ('payment_status', 'currency', 'donation_date', 'is_anonymous')
    search_fields = ('user__username', 'transaction_id', 'message')
    readonly_fields = ('donation_date', 'last_updated', 'transaction_id')
    fieldsets = (
        ('Donation Details', {
            'fields': ('user', 'amount', 'currency', 'is_anonymous')
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'transaction_id')
        }),
        ('Additional Information', {
            'fields': ('message', 'donation_date', 'last_updated')
        }),
    )

    def amount_display(self, obj):
        return f"{obj.amount} {obj.currency}"
    amount_display.short_description = 'Amount'

# Custom admin site configuration
admin.site.site_header = 'Scam Report Administration'
admin.site.site_title = 'Scam Report Admin Portal'
admin.site.index_title = 'Welcome to Scam Report Management Portal'
