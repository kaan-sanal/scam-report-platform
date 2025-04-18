import requests
from bs4 import BeautifulSoup
from PIL import Image
from PIL.ExifTags import TAGS
import os
from datetime import datetime
import json
import dns.resolver
import dns.name
import dns.message
import dns.query
import dns.rdatatype
from urllib.parse import urlparse
import socket
import whois

def get_domain_info(domain):
    """
    Get domain information using multiple methods
    """
    info = {
        'whois_info': None,
        'dns_info': None,
        'error': None
    }
    
    # Try WHOIS lookup first
    try:
        w = whois.whois(domain)
        if w and w.creation_date:
            creation_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
            expiration_date = w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date
            
            info['whois_info'] = {
                'registrar': w.registrar,
                'creation_date': creation_date.strftime('%Y-%m-%d') if creation_date else None,
                'expiration_date': expiration_date.strftime('%Y-%m-%d') if expiration_date else None,
                'name_servers': w.name_servers if hasattr(w, 'name_servers') else None
            }
    except Exception as e:
        info['error'] = f'WHOIS lookup failed: {str(e)}'
        
        # Try DNS lookup as fallback
        try:
            # Create a new resolver
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            # Get NS records
            ns_records = resolver.resolve(domain, 'NS')
            nameservers = [str(ns) for ns in ns_records]
            
            # Get SOA record
            soa_records = resolver.resolve(domain, 'SOA')
            soa = str(soa_records[0]).split()
            
            info['dns_info'] = {
                'nameservers': nameservers,
                'soa': {
                    'primary_ns': soa[0],
                    'responsible_email': soa[1],
                    'serial': soa[2],
                    'refresh': soa[3],
                    'retry': soa[4],
                    'expire': soa[5],
                    'minimum_ttl': soa[6]
                }
            }
        except Exception as dns_error:
            if info['error']:
                info['error'] += f'\nDNS lookup also failed: {str(dns_error)}'
            else:
                info['error'] = f'DNS lookup failed: {str(dns_error)}'
    
    return info

def analyze_url(url):
    """
    Analyze a URL for potential scam indicators
    Returns a dictionary with analysis results
    """
    results = {
        'domain_age': None,
        'whois_info': None,
        'dns_records': None,
        'ip_address': None,
        'is_valid': False,
        'risk_level': 'unknown',
        'warnings': []
    }
    
    try:
        # Parse URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        if not domain:
            results['warnings'].append('Invalid URL format')
            return results
            
        # Get domain information
        domain_info = get_domain_info(domain)
        
        if domain_info['whois_info']:
            results['whois_info'] = domain_info['whois_info']
            
            # Calculate domain age if creation date is available
            if domain_info['whois_info']['creation_date']:
                creation_date = datetime.strptime(domain_info['whois_info']['creation_date'], '%Y-%m-%d')
                domain_age = (datetime.now() - creation_date).days
                results['domain_age'] = domain_age
                
                # Domain age risk assessment
                if domain_age < 30:
                    results['warnings'].append('Domain is less than 30 days old')
                elif domain_age < 90:
                    results['warnings'].append('Domain is less than 90 days old')
        
        elif domain_info['dns_info']:
            results['dns_records'] = domain_info['dns_info']
        
        if domain_info['error']:
            results['warnings'].append(domain_info['error'])
            
        # DNS records
        try:
            dns_records = {}
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            for record_type in ['A', 'MX', 'NS', 'TXT']:
                try:
                    answers = resolver.resolve(domain, record_type)
                    dns_records[record_type] = [str(rdata) for rdata in answers]
                except dns.resolver.NXDOMAIN:
                    dns_records[record_type] = []
                    results['warnings'].append(f'Domain does not exist')
                except Exception:
                    dns_records[record_type] = []
                    
            results['dns_records'] = dns_records
            
            if not dns_records.get('A'):
                results['warnings'].append('No A records found')
            if not dns_records.get('MX'):
                results['warnings'].append('No MX records found')
                
        except Exception as e:
            results['warnings'].append(f'DNS lookup failed: {str(e)}')
            
        # IP address
        try:
            socket.setdefaulttimeout(5)
            ip = socket.gethostbyname(domain)
            results['ip_address'] = ip
        except Exception as e:
            results['warnings'].append(f'Could not resolve IP address: {str(e)}')
            
        # Risk level assessment
        risk_score = 0
        if results['domain_age']:
            if results['domain_age'] < 30:
                risk_score += 3
            elif results['domain_age'] < 90:
                risk_score += 2
            
        if not results.get('dns_records', {}).get('A'):
            risk_score += 2
        if not results.get('dns_records', {}).get('MX'):
            risk_score += 1
            
        if risk_score >= 4:
            results['risk_level'] = 'high'
        elif risk_score >= 2:
            results['risk_level'] = 'medium'
        else:
            results['risk_level'] = 'low'
            
        results['is_valid'] = True
        
    except Exception as e:
        results['warnings'].append(f'Analysis failed: {str(e)}')
        
    return results

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