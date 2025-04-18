import whois
import requests
from bs4 import BeautifulSoup
from PIL import Image
from PIL.ExifTags import TAGS
import os
from datetime import datetime
import json

def analyze_url(url):
    try:
        domain_info = whois.whois(url)
        
        if domain_info.creation_date:
            if isinstance(domain_info.creation_date, list):
                creation_date = domain_info.creation_date[0]
            else:
                creation_date = domain_info.creation_date
            domain_age = (datetime.now() - creation_date).days
        else:
            domain_age = None

        registrar = domain_info.registrar
        country = domain_info.country

        blacklist_check = check_blacklist(url)

        return {
            'domain_age': domain_age,
            'registrar': registrar,
            'country': country,
            'is_blacklisted': blacklist_check['is_blacklisted'],
            'blacklist_details': blacklist_check['details']
        }
    except Exception as e:
        return {
            'error': str(e)
        }

def check_blacklist(url):
    blacklist_services = [
        'https://www.virustotal.com/vtapi/v2/url/report',
        'https://www.google.com/safebrowsing/diagnostic?site='
    ]
    
    is_blacklisted = False
    details = []
    
    for service in blacklist_services:
        try:
            response = requests.get(f"{service}{url}")
            if response.status_code == 200:
                if "malicious" in response.text.lower() or "phishing" in response.text.lower():
                    is_blacklisted = True
                    details.append(f"Found in {service}")
        except:
            continue
    
    return {
        'is_blacklisted': is_blacklisted,
        'details': details
    }

def extract_metadata(file_path):
    metadata = {}
    
    file_type = os.path.splitext(file_path)[1][1:].lower()
    
    if file_type in ['jpg', 'jpeg', 'png', 'tiff']:

        try:
            image = Image.open(file_path)
            exif_data = image._getexif()
            if exif_data:
                for tag_id in exif_data:
                    tag = TAGS.get(tag_id, tag_id)
                    data = exif_data.get(tag_id)
                    if isinstance(data, bytes):
                        data = data.decode()
                    metadata[tag] = data
        except Exception as e:
            metadata['error'] = str(e)
    
    elif file_type == 'pdf':
        try:
            metadata['file_type'] = 'pdf'
            metadata['size'] = os.path.getsize(file_path)
        except Exception as e:
            metadata['error'] = str(e)
    
    return metadata

def analyze_image_metadata(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if exif_data:
            metadata = {}
            for tag_id in exif_data:
                tag = TAGS.get(tag_id, tag_id)
                data = exif_data.get(tag_id)
                if isinstance(data, bytes):
                    data = data.decode()
                metadata[tag] = data
            
            return {
                'success': True,
                'metadata': metadata,
                'message': 'Meta veriler başarıyla analiz edildi'
            }
        else:
            return {
                'success': False,
                'message': 'Resimde EXIF verisi bulunamadı'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Meta veri analizi başarısız: {str(e)}'
        }

def check_scam_database(url):
    try:
        response = requests.get(f'https://api.scam-database.com/check?url={url}')
        data = response.json()
        
        return {
            'success': True,
            'is_scam': data.get('is_scam', False),
            'confidence': data.get('confidence', 0),
            'details': data.get('details', {})
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Scam veritabanı kontrolü başarısız: {str(e)}'
        } 