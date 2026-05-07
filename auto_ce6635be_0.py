#!/usr/bin/env python3
"""
Audio Transcription Script using OpenAI Whisper API

This script transcribes audio files (MP3, WAV, M4A) to text with timestamps
using OpenAI's Whisper API. It handles file upload, API communication, and
formats the response with timestamp markers for easy reading.

Usage: python script.py
Requirements: httpx library (pip install httpx)
"""

import os
import sys
import json
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Error: httpx library is required. Install with: pip install httpx")
    sys.exit(1)


class WhisperTranscriber:
    """Handles audio transcription using OpenAI Whisper API"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable")
        
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        self.supported_formats = {'.mp3', '.wav', '.m4a', '.mp4', '.mpeg', '.mpga', '.webm'}
    
    def validate_file(self, file_path):
        """Validate if file exists and has supported format"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported format: {path.suffix}. Supported: {self.supported_formats}")
        
        # Check file size (Whisper API limit is 25MB)
        file_size = path.stat().st_size
        if file_size > 25 * 1024 * 1024:
            raise ValueError(f"File too large: {file_size / (1024*1024):.1f}MB. Max: 25MB")
        
        return path
    
    def transcribe_file(self, file_path, response_format="verbose_json", language=None):
        """Transcribe audio file using Whisper API"""
        try:
            file_path = self.validate_file(file_path)
            
            with httpx.Client(timeout=300) as client:
                with open(file_path, 'rb') as audio_file:
                    files = {
                        'file': (file_path.name, audio_file, 'audio/mpeg'),
                    }
                    
                    data = {
                        'model': 'whisper-1',
                        'response_format': response_format,
                    }
                    
                    if language:
                        data['language'] = language
                    
                    print(f"Uploading and transcribing: {file_path.name}")
                    print("This may take a few minutes...")
                    
                    response = client.post(
                        f"{self.base_url}/audio/transcriptions",
                        headers=self.headers,
                        files=files,
                        data=data
                    )
                    
                    if response.status_code != 200:
                        raise Exception(f"API Error {response.status_code}: {response.text}")
                    
                    return response.json()
                    
        except httpx.TimeoutException:
            raise Exception("Request timed out. File may be too large or network is slow")
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def format_transcription(self, transcription_data):
        """Format transcription with timestamps"""
        try:
            if isinstance(transcription_data, str):
                return transcription_data
            
            if 'segments' in transcription_data:
                formatted_lines = []
                for segment in transcription_data['segments']:
                    start_time = self.format_timestamp(segment.get('start', 0))
                    end_time = self.format_timestamp(segment.get('end', 0))
                    text = segment.get('text', '').strip()
                    formatted_lines.append(f"[{start_time} - {end_time}] {text}")
                
                return '\n'.join(formatted_lines)
            
            return transcription_data.get('text', 'No transcription available')
            
        except Exception as e:
            return f"Error formatting transcription: {str(e)}"
    
    @staticmethod
    def format_timestamp(seconds):
        """Convert seconds to MM:SS format"""
        try:
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"
        except:
            return "00:00"


def main():
    """Main function to run the transcription script"""
    try:
        # Check for API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Error: Please set your OpenAI API key as environment variable:")
            print("export OPENAI_API_KEY='your-api-key-here'")
            sys.exit(1)
        
        # Get file path from user
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
        else:
            file_path = input("Enter path to audio file (MP3, WAV, M4A): ").strip()
        
        if not file_path:
            print("No file path provided")
            sys.exit(1)
        
        # Initialize transcriber
        transcriber = WhisperTranscriber(api_key)
        
        # Transcribe file
        result = transcriber.transcribe_file(file_path)
        
        # Format and display results
        print("\n" + "="*60)
        print("TRANSCRIPTION RESULTS")
        print("="*60)
        
        formatted_text = transcriber.format_transcription(result)
        print(formatted_text)
        
        # Show additional info if available
        if isinstance(result, dict) and 'language' in result:
            print(f"\nDetected language: {result['language']}")
        
        print("\n" + "="*60)
        print("TRANSCRIPTION COMPLETE")
        
    except KeyboardInterrupt:
        print("\nTranscription cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()