```python
#!/usr/bin/env python3
"""
Bank Statement Parser

This module parses CSV bank statement formats from major US banks (Chase, Bank of America, 
Wells Fargo) and standardizes transaction data into a unified format.

The standardized format includes:
- date: Transaction date in YYYY-MM-DD format
- description: Transaction description/merchant
- amount: Transaction amount as float (negative for debits)
- account: Account identifier/number

Supported formats:
- Chase: Date, Description, Amount, Running Balance
- Bank of America: Date, Description, Amount, Running Balance  
- Wells Fargo: Date, Amount, *, *, Description

Usage: python script.py
"""

import csv
import re
from datetime import datetime
from typing import List, Dict, Optional
import io

class BankStatementParser:
    def __init__(self):
        self.standardized_transactions = []
    
    def parse_date(self, date_str: str) -> str:
        """Parse various date formats and return YYYY-MM-DD format."""
        date_formats = [
            '%m/%d/%Y',    # MM/DD/YYYY
            '%m/%d/%y',    # MM/DD/YY
            '%Y-%m-%d',    # YYYY-MM-DD
            '%m-%d-%Y',    # MM-DD-YYYY
            '%d/%m/%Y',    # DD/MM/YYYY
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def clean_amount(self, amount_str: str) -> float:
        """Clean and convert amount string to float."""
        # Remove currency symbols, commas, spaces
        cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
        
        # Handle parentheses for negative amounts
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            raise ValueError(f"Unable to parse amount: {amount_str}")
    
    def detect_bank_format(self, headers: List[str]) -> str:
        """Detect bank format based on CSV headers."""
        headers_lower = [h.lower().strip() for h in headers]
        
        # Chase format detection
        if any('posting date' in h for h in headers_lower) or \
           (len(headers) >= 3 and 'date' in headers_lower[0] and 'description' in headers_lower[1]):
            return 'chase'
        
        # Bank of America format detection
        elif any('posted date' in h for h in headers_lower) or \
             any('reference number' in h for h in headers_lower):
            return 'bofa'
        
        # Wells Fargo format detection  
        elif len(headers) >= 5 and any('amount' in h for h in headers_lower):
            return 'wells_fargo'
        
        # Default to Chase format if unclear
        return 'chase'
    
    def parse_chase_format(self, rows: List[List[str]], account_id: str = "Chase") -> List[Dict]:
        """Parse Chase bank CSV format."""
        transactions = []
        
        for row in rows:
            if len(row) < 3:
                continue
                
            try:
                date = self.parse_date(row[0])
                description = row[1].strip()
                amount = self.clean_amount(row[2])
                
                transactions.append({
                    'date': date,
                    'description': description,
                    'amount': amount,
                    'account': account_id
                })
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping invalid row {row}: {e}")
                continue
        
        return transactions
    
    def parse_bofa_format(self, rows: List[List[str]], account_id: str = "BofA") -> List[Dict]:
        """Parse Bank of America CSV format."""
        transactions = []
        
        for row in rows:
            if len(row) < 3:
                continue
                
            try:
                date = self.parse_date(row[0])
                description = row[1].strip()
                amount = self.clean_amount(row[2])
                
                transactions.append({
                    'date': date,
                    'description': description,
                    'amount': amount,
                    'account': account_id
                })
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping invalid row {row}: {e}")
                continue
        
        return transactions
    
    def parse_wells_fargo_format(self, rows: List[List[str]], account_id: str = "WellsFargo") -> List[Dict]:
        """Parse Wells Fargo CSV format."""
        transactions = []
        
        for row in rows:
            if len(row) < 5:
                continue
                
            try:
                date = self.parse_date(row[0])
                amount = self.clean_amount(row[1])
                description = row[4].strip()
                
                transactions.append({
                    'date': date,
                    'description': description,
                    'amount': amount,
                    'account': account_id
                })
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping invalid row {row}: {e}")
                continue
        
        return transactions
    
    def parse_csv_content(self, csv_content: str, account_id: Optional[str] = None) -> List[Dict]:
        """Parse CSV content and return standardized transactions."""
        try:
            csv_reader = csv.reader(io.StringIO(csv_content))
            rows = list(csv_reader)
            
            if len(rows) < 2:
                raise ValueError("CSV must have at least header and one data row")
            
            headers = rows[0]
            data_rows = rows[1:]
            
            bank_format = self.detect_bank_format(headers)
            
            if not account_id:
                account_id = bank_format.title()
            
            if bank_format == 'chase':
                return self.parse_chase_format(data_rows, account_id)
            elif bank_format == 'bofa':
                return self.parse_bofa_format(data_rows, account_id)
            elif bank_format == 'wells_fargo':
                return self.parse_wells_fargo_format(data_rows, account_id)
            else:
                raise ValueError(f"Unsupported bank format: {bank_format}")
                
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {e}")
    
    def parse_file(self, filepath: str) -> List[Dict]:
        """Parse CSV file and return standardized transactions."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            return self.parse_csv_content(content)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filepath}")
        except Exception as e:
            raise ValueError(f"Error reading file {filepath}: {e}")

def main():
    """Demonstrate the parser with sample data."""
    parser = BankStatementParser()
    
    # Sample Chase format
    chase_sample = """Date,Description,Amount,Running Balance
01/15/2024,STARBUCKS STORE #12345,-4.95,1245.67
01/16/2024,PAYROLL DEPOSIT,2500.00,3741.72
01/17/2024,ATM WITHDRAWAL,-100.00,3641.72"""
    
    # Sample Bank of America format
    bofa_sample = """Posted Date,Reference Number,Payee,Address,Amount
01/15/2024,1234567890,TARGET STORE T-1234,,-15.67
01/16/2024,1234567891,DIRECT DEPOSIT