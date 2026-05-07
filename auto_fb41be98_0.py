```python
#!/usr/bin/env python3
"""
Password Strength Analyzer

This module analyzes passwords from a text file and evaluates their strength based on:
- Length (minimum 8 characters)
- Complexity (uppercase, lowercase, numbers, symbols)
- Common dictionary words detection
- Sequential patterns detection
- Overall strength score (0-100) with detailed feedback

Usage: python script.py

Expects a 'passwords.txt' file in the same directory with one password per line.
"""

import re
import sys
from typing import List, Dict, Tuple


class PasswordAnalyzer:
    def __init__(self):
        # Common dictionary words (subset for demonstration)
        self.common_words = {
            'password', '123456', 'qwerty', 'abc123', 'admin', 'login',
            'welcome', 'monkey', 'dragon', 'master', 'shadow', 'computer',
            'letmein', 'football', 'baseball', 'superman', 'batman', 'trustno1'
        }
        
        # Sequential patterns
        self.sequences = [
            'abcdefghijklmnopqrstuvwxyz',
            '0123456789',
            'qwertyuiopasdfghjklzxcvbnm'
        ]
    
    def analyze_length(self, password: str) -> Tuple[int, str]:
        """Analyze password length and return score and feedback."""
        length = len(password)
        if length >= 12:
            return 25, f"Excellent length ({length} chars)"
        elif length >= 8:
            return 20, f"Good length ({length} chars)"
        elif length >= 6:
            return 10, f"Fair length ({length} chars) - consider longer"
        else:
            return 0, f"Poor length ({length} chars) - too short"
    
    def analyze_complexity(self, password: str) -> Tuple[int, List[str]]:
        """Analyze character complexity and return score and feedback."""
        score = 0
        feedback = []
        
        if re.search(r'[a-z]', password):
            score += 5
            feedback.append("✓ Contains lowercase letters")
        else:
            feedback.append("✗ Missing lowercase letters")
        
        if re.search(r'[A-Z]', password):
            score += 5
            feedback.append("✓ Contains uppercase letters")
        else:
            feedback.append("✗ Missing uppercase letters")
        
        if re.search(r'\d', password):
            score += 5
            feedback.append("✓ Contains numbers")
        else:
            feedback.append("✗ Missing numbers")
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 10
            feedback.append("✓ Contains special symbols")
        else:
            feedback.append("✗ Missing special symbols")
        
        return score, feedback
    
    def check_dictionary_words(self, password: str) -> Tuple[int, str]:
        """Check for common dictionary words and return score penalty and feedback."""
        password_lower = password.lower()
        found_words = []
        
        for word in self.common_words:
            if word in password_lower:
                found_words.append(word)
        
        if found_words:
            penalty = len(found_words) * 10
            return -penalty, f"✗ Contains common words: {', '.join(found_words)}"
        else:
            return 0, "✓ No common dictionary words detected"
    
    def check_sequential_patterns(self, password: str) -> Tuple[int, List[str]]:
        """Check for sequential patterns and return score penalty and feedback."""
        password_lower = password.lower()
        penalties = 0
        feedback = []
        
        # Check for sequences of 3+ characters
        for sequence in self.sequences:
            for i in range(len(sequence) - 2):
                pattern = sequence[i:i+3]
                if pattern in password_lower:
                    penalties += 5
                    feedback.append(f"✗ Sequential pattern found: {pattern}")
        
        # Check for repeated characters (3+ in a row)
        repeated_pattern = re.search(r'(.)\1{2,}', password)
        if repeated_pattern:
            penalties += 10
            char = repeated_pattern.group(1)
            count = len(repeated_pattern.group(0))
            feedback.append(f"✗ Repeated character pattern: '{char}' repeated {count} times")
        
        if not feedback:
            feedback.append("✓ No sequential patterns detected")
        
        return -penalties, feedback
    
    def calculate_strength_score(self, password: str) -> Dict:
        """Calculate overall password strength score and compile feedback."""
        total_score = 0
        all_feedback = []
        
        # Length analysis
        length_score, length_feedback = self.analyze_length(password)
        total_score += length_score
        all_feedback.append(f"Length: {length_feedback}")
        
        # Complexity analysis
        complexity_score, complexity_feedback = self.analyze_complexity(password)
        total_score += complexity_score
        all_feedback.extend([f"Complexity: {fb}" for fb in complexity_feedback])
        
        # Dictionary words check
        dict_penalty, dict_feedback = self.check_dictionary_words(password)
        total_score += dict_penalty
        all_feedback.append(f"Dictionary: {dict_feedback}")
        
        # Sequential patterns check
        seq_penalty, seq_feedback = self.check_sequential_patterns(password)
        total_score += seq_penalty
        all_feedback.extend([f"Patterns: {fb}" for fb in seq_feedback])
        
        # Ensure score is within 0-100 range
        final_score = max(0, min(100, total_score))
        
        # Determine strength level
        if final_score >= 80:
            strength_level = "Very Strong"
        elif final_score >= 60:
            strength_level = "Strong"
        elif final_score >= 40:
            strength_level = "Moderate"
        elif final_score >= 20:
            strength_level = "Weak"
        else:
            strength_level = "Very Weak"
        
        return {
            'password': password,
            'score': final_score,
            'strength_level': strength_level,
            'feedback': all_feedback
        }
    
    def analyze_passwords_from_file(self, filename: str) -> List[Dict]:
        """Read passwords from file and analyze each one."""
        results = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                passwords = [line.strip() for line in file if line.strip()]
            
            if not passwords:
                print(f"Warning: No passwords found in {filename}")
                return results
            
            for password in passwords:
                result = self.calculate_strength_score(password)
                results.append(result)
            
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            print("Please create a 'passwords.txt' file with one password per line.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file '{filename}': {e}")
            sys.exit(1)
        
        return results
    
    def print_results(self, results: List[Dict]):
        """Print analysis results in a formatted way."""
        print("=" * 80)
        print("PASSWORD STRENGTH ANALYSIS REPORT")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\nPassword #{i}: {'*' * len(result['password'])}")
            print(f"Score: {result['score']}/100")
            print(f"Strength Level: {result['strength_level']}")
            print("-" * 40)
            print("Detailed Analysis:")
            for feedback in result['feedback']:
                print(f"  {feedback}")
            print("-" * 40)
        
        # Summary statistics
        if results