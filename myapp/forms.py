from django import forms
from .models import ScamReport, ScamEvidence, ReportComment, ReportEvidence, Donation
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Fieldset, ButtonHolder
import re
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class ScamReportForm(forms.ModelForm):
    class Meta:
        model = ScamReport
        fields = ['title', 'description', 'scam_url', 'report_type', 'is_public']
        labels = {
            'title': 'Title',
            'description': 'Description',
            'scam_url': 'Scam URL',
            'report_type': 'Type of Scam',
            'is_public': 'Make Public'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'scam_url': forms.URLInput(attrs={'class': 'form-control'}),
            'report_type': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Scam Report Details',
                'report_type',
                'title',
                'description',
                'scam_url',
            ),
            ButtonHolder(
                Submit('submit', 'Submit Report', css_class='btn-primary')
            )
        )

class ScamEvidenceForm(forms.ModelForm):
    class Meta:
        model = ScamEvidence
        fields = ['file', 'description']
        widgets = {
            'file': forms.FileInput(),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'file': 'Evidence File',
            'description': 'Evidence Description'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Upload Evidence',
                'file',
                'description',
            ),
            ButtonHolder(
                Submit('submit', 'Upload Evidence', css_class='btn-primary')
            )
        )

class CommentForm(forms.ModelForm):
    class Meta:
        model = ReportComment
        fields = ['content']
        labels = {
            'content': 'Comment'
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('content'),
            ButtonHolder(
                Submit('submit', 'Post Comment', css_class='btn-primary')
            )
        )

class EvidenceForm(forms.ModelForm):
    class Meta:
        model = ReportEvidence
        fields = ['title', 'description', 'file']
        labels = {
            'title': 'Title',
            'description': 'Description',
            'file': 'File'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Submit Evidence',
                'title',
                'description',
                'file',
            ),
            ButtonHolder(
                Submit('submit', 'Submit Evidence', css_class='btn-primary')
            )
        )

class DonationForm(forms.ModelForm):
    card_number = forms.CharField(max_length=16, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card Number'}))
    expiry_date = forms.CharField(max_length=5, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'}))
    cvc = forms.CharField(max_length=3, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CVC'}))
    is_anonymous = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Your message (optional)'}))

    class Meta:
        model = Donation
        fields = ['amount', 'currency']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '1'}),
            'currency': forms.Select(attrs={'class': 'form-control'})
        }

    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')
        if not card_number.isdigit() or len(card_number) != 16:
            raise forms.ValidationError("Please enter a valid 16-digit card number.")
        return card_number

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        if not re.match(r'^\d{2}/\d{2}$', expiry_date):
            raise forms.ValidationError("Please enter a valid expiry date in MM/YY format.")
        return expiry_date

    def clean_cvc(self):
        cvc = self.cleaned_data.get('cvc')
        if not cvc.isdigit() or len(cvc) != 3:
            raise forms.ValidationError("Please enter a valid 3-digit CVC.")
        return cvc

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'payment-form'
        self.helper.layout = Layout(
            Row(
                Column('amount', css_class='col-md-6'),
                Column('currency', css_class='col-md-6'),
                css_class='mb-3'
            ),
            Fieldset(
                'Card Information',
                Row(
                    Column('card_number', css_class='col-12 mb-3'),
                ),
                Row(
                    Column('expiry_date', css_class='col-md-6'),
                    Column('cvc', css_class='col-md-6'),
                ),
                css_class='card bg-light mb-3 p-3'
            ),
            'is_anonymous',
            'message',
            ButtonHolder(
                Submit('submit', 'Make Donation', css_class='btn-primary'),
                css_class='mt-3'
            )
        )

class CustomLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class CustomSignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already in use.')
        return email

class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('No user found with this email address.')
        return email 