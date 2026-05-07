```python
"""
HTML Email Signature Generator

This module creates professional HTML email signature templates with inline CSS styling.
Users can input their contact information and preferences to generate customized signatures
that work across different email clients.

Features:
- Interactive user input collection
- Multiple signature template styles
- Inline CSS for maximum email client compatibility
- Error handling for user inputs
- Self-contained script with minimal dependencies

Usage:
    python script.py

The script will prompt for user information and generate an HTML signature template
that can be copied and pasted into email client signature settings.
"""

import sys
import re
from typing import Dict, Optional


def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> str:
    """Clean and validate phone number format."""
    # Remove all non-digit characters except + and spaces
    cleaned = re.sub(r'[^\d+\s()-]', '', phone.strip())
    if len(re.sub(r'[^\d]', '', cleaned)) < 10:
        raise ValueError("Phone number must contain at least 10 digits")
    return cleaned


def get_user_input() -> Dict[str, str]:
    """Collect user information for signature generation."""
    print("=== HTML Email Signature Generator ===\n")
    
    user_data = {}
    
    try:
        # Required fields
        user_data['name'] = input("Full Name: ").strip()
        if not user_data['name']:
            raise ValueError("Name cannot be empty")
        
        user_data['title'] = input("Job Title: ").strip()
        if not user_data['title']:
            raise ValueError("Job title cannot be empty")
        
        user_data['company'] = input("Company Name: ").strip()
        if not user_data['company']:
            raise ValueError("Company name cannot be empty")
        
        # Email validation
        email = input("Email Address: ").strip()
        if not validate_email(email):
            raise ValueError("Invalid email format")
        user_data['email'] = email
        
        # Optional fields
        phone = input("Phone Number (optional): ").strip()
        if phone:
            user_data['phone'] = validate_phone(phone)
        
        user_data['website'] = input("Website (optional): ").strip()
        user_data['address'] = input("Address (optional): ").strip()
        
        # Style preferences
        print("\nStyle Options:")
        print("1. Professional Blue")
        print("2. Modern Gray")
        print("3. Classic Black")
        
        style_choice = input("Choose style (1-3, default=1): ").strip()
        if style_choice not in ['1', '2', '3', '']:
            style_choice = '1'
        user_data['style'] = style_choice or '1'
        
        return user_data
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)


def get_style_config(style_choice: str) -> Dict[str, str]:
    """Return CSS styling configuration based on user choice."""
    styles = {
        '1': {  # Professional Blue
            'primary_color': '#2E5BBA',
            'secondary_color': '#666666',
            'accent_color': '#E8F0FF',
            'font_family': 'Arial, sans-serif'
        },
        '2': {  # Modern Gray
            'primary_color': '#333333',
            'secondary_color': '#777777',
            'accent_color': '#F5F5F5',
            'font_family': 'Helvetica, Arial, sans-serif'
        },
        '3': {  # Classic Black
            'primary_color': '#000000',
            'secondary_color': '#555555',
            'accent_color': '#F9F9F9',
            'font_family': 'Times New Roman, serif'
        }
    }
    return styles.get(style_choice, styles['1'])


def generate_signature_html(user_data: Dict[str, str]) -> str:
    """Generate HTML email signature with inline CSS."""
    style_config = get_style_config(user_data['style'])
    
    # Build contact info sections
    contact_parts = []
    
    # Email (always present)
    contact_parts.append(
        f'<a href="mailto:{user_data["email"]}" style="color: {style_config["primary_color"]}; text-decoration: none;">'
        f'{user_data["email"]}</a>'
    )
    
    # Phone (if provided)
    if user_data.get('phone'):
        phone_clean = re.sub(r'[^\d]', '', user_data['phone'])
        contact_parts.append(
            f'<a href="tel:+{phone_clean}" style="color: {style_config["primary_color"]}; text-decoration: none;">'
            f'{user_data["phone"]}</a>'
        )
    
    # Website (if provided)
    if user_data.get('website'):
        website = user_data['website']
        if not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        display_url = user_data['website'].replace('https://', '').replace('http://', '')
        contact_parts.append(
            f'<a href="{website}" style="color: {style_config["primary_color"]}; text-decoration: none;">'
            f'{display_url}</a>'
        )
    
    contact_info = ' | '.join(contact_parts)
    
    # Address section (if provided)
    address_section = ""
    if user_data.get('address'):
        address_section = f'''
        <tr>
            <td colspan="2" style="padding-top: 5px; font-size: 12px; color: {style_config["secondary_color"]}; 
                               font-family: {style_config["font_family"]};">
                {user_data["address"]}
            </td>
        </tr>'''
    
    # Generate complete HTML signature
    html_signature = f'''
<table cellpadding="0" cellspacing="0" border="0" style="font-family: {style_config["font_family"]}; 
                                                        font-size: 14px; line-height: 1.4; color: #333333;">
    <tr>
        <td style="vertical-align: top; padding-right: 15px;">
            <div style="width: 4px; height: 60px; background-color: {style_config["primary_color"]};"></div>
        </td>
        <td style="vertical-align: top;">
            <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td style="font-size: 18px; font-weight: bold; color: {style_config["primary_color"]}; 
                               font-family: {style_config["font_family"]}; padding-bottom: 2px;">
                        {user_data["name"]}
                    </td>
                </tr>
                <tr>
                    <td style="font-size: 14px; color: {style_config["secondary_color"]}; 
                               font-family: {style_config["font_family"]}; padding-bottom: 2px;">
                        {user_data["title"]}
                    </td>
                </tr>
                <tr>
                    <td style="font-size: 14px; font-weight: bold; color: {style_config["primary_color"]}; 
                               font-family: {style_config["font_family"]}; padding-bottom: 8px;">
                        {user_data["company"]}
                    </td>
                </tr>
                <tr>
                    <td style="font-size: 12