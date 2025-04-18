from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

def scam_evidence_path(instance, filename):
    return f'scam_evidence/{instance.id}/{filename}'

class ScamReport(models.Model):
    REPORT_TYPES = [
        ('investment', 'Investment Scam'),
        ('shopping', 'Shopping Scam'),
        ('banking', 'Banking Scam'),
        ('social', 'Social Media Scam'),
        ('other', 'Other')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ]

    reporter = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='submitted_reports',
        help_text='User who submitted this report'
    )
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    scam_url = models.URLField(blank=True, null=True)
    domain_age = models.CharField(max_length=100, blank=True, null=True)
    domain_registrar = models.CharField(max_length=200, blank=True, null=True)
    domain_country = models.CharField(max_length=100, blank=True, null=True)
    is_blacklisted = models.BooleanField(default=False)
    blacklist_details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_public = models.BooleanField(default=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True, null=True)
    flagged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='flagged_reports')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_reports')
    verification_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == 'verified' and not self.verification_date:
            self.verification_date = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-submission_date']
        verbose_name = 'Scam Report'
        verbose_name_plural = 'Scam Reports'

class ScamEvidence(models.Model):
    report = models.ForeignKey(ScamReport, on_delete=models.CASCADE, related_name='scam_evidence')
    file = models.FileField(upload_to=scam_evidence_path)
    description = models.TextField()
    file_type = models.CharField(max_length=50)
    metadata = models.JSONField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidence for {self.report.title}"

    def save(self, *args, **kwargs):
        if not self.file_type:
            self.file_type = os.path.splitext(self.file.name)[1][1:].lower()
        super().save(*args, **kwargs)

class ReportComment(models.Model):
    report = models.ForeignKey(ScamReport, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_comments'
    )
    verification_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.report.title}"

    class Meta:
        ordering = ['-created_at']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reputation_score = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True, null=True)
    last_ip = models.GenericIPAddressField(null=True, blank=True)
    last_location = models.CharField(max_length=255, null=True, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    total_reports = models.IntegerField(default=0)
    verified_reports = models.IntegerField(default=0)
    flagged_reports = models.IntegerField(default=0)
    warning_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def update_reputation(self):
        verified_reports = self.user.submitted_reports.filter(status='verified').count()
        total_upvotes = sum(report.reportvote_set.filter(vote_type='upvote').count() 
                           for report in self.user.submitted_reports.all())
        total_downvotes = sum(report.reportvote_set.filter(vote_type='downvote').count() 
                            for report in self.user.submitted_reports.all())
        

        self.reputation_score = (verified_reports * 10) + (total_upvotes * 2) - (total_downvotes * 1)
        self.save()

class ReportVote(models.Model):
    VOTE_CHOICES = [
        ('upvote', 'Upvote'),
        ('downvote', 'Downvote')
    ]
    
    report = models.ForeignKey(ScamReport, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=8, choices=VOTE_CHOICES)
    vote_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['report', 'user']

    def __str__(self):
        return f"{self.user.username} {self.vote_type}d {self.report.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.report.reporter.userprofile.update_reputation()

class ReportEvidence(models.Model):
    report = models.ForeignKey(ScamReport, on_delete=models.CASCADE, related_name='evidence')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='evidence/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_evidence'
    )
    verification_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.report.title}"

    class Meta:
        ordering = ['-uploaded_at']

class Donation(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('TRY', 'Turkish Lira'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='TRY')
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    donation_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_anonymous = models.BooleanField(default=False)
    message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.amount} {self.currency} donation by {self.user.username if not self.is_anonymous else 'Anonymous'}"

    class Meta:
        ordering = ['-donation_date']
