# Scam Report & Verification Platform

Hey there! Welcome to our Scam Report & Verification Platform. This is a Django-based web application that helps people report and verify scam websites, protecting others from falling victim to fraud.

## What This Platform Does 

- **Report Scams**: Users can submit detailed reports about scam websites they've encountered
- **Share Evidence**: Upload screenshots, documents, or other proof of scams
- **Community Verification**: Admins verify reports and evidence to ensure accuracy
- **Stay Informed**: Browse verified scam reports to protect yourself
- **Support Victims**: Make donations to help scam victims

## Features 

### For Users
- Create an account and build your reputation
- Submit scam reports with detailed information
- Upload evidence (screenshots, documents, etc.)
- Comment on reports and share experiences
- Make anonymous donations to support victims
- Track your reporting history

### For Admins
- Verify scam reports and evidence
- Manage user accounts and permissions
- Monitor user reputation scores
- Track donation transactions
- Moderate comments and content

## Tech Stack 

- **Backend**: Django 5.2
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Django's built-in auth system
- **File Storage**: Local storage (development), AWS S3 (production)

## Getting Started 

1. Clone the repository:
```bash
git clone https://github.com/yourusername/scam-report-platform.git
cd scam-report-platform
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate 
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser!

## Project Structure 

```
scam-report-platform/
├── myapp/
│   ├── templates/          # HTML templates
│   ├── static/            # CSS, JS, images
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── forms.py           # Form definitions
│   └── urls.py            # URL patterns
├── mysite/                # Project settings
├── manage.py
└── requirements.txt       # Python dependencies
```

## Contributing 

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Security 

- All user data is encrypted
- Passwords are hashed using Django's security features
- File uploads are validated and sanitized
- CSRF protection enabled
- XSS prevention implemented


## Support 

If you need help or have questions:
- Open an issue
- Email us at support@scamreport.com
- Join our Discord community

## Acknowledgments 

Thanks to all contributors and the Django community for making this project possible!

---
# scam-report-platform
