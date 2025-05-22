#!/usr/bin/env python3
"""
AudioTranscriber - Telegram Audio Files Transcription Tool

This script downloads MP3 files from a Telegram channel, removes duplicates,
renames them chronologically, transcribes them using AssemblyAI, and uploads
the transcriptions to Google Docs.

Author: Your Name
License: MIT
"""

import os
import hashlib
import re
from datetime import datetime
import time
import requests
import json
import asyncio
from telethon import TelegramClient
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('audiotranscriber.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AudioTranscriber:
    def __init__(self, config_file='config.json'):
        """Initialize the AudioTranscriber with configuration."""
        self.config = self.load_config(config_file)
        self.client = None
        self.docs_service = None
        self.drive_service = None
        
        # Create directories
        os.makedirs(self.config['download_dir'], exist_ok=True)
        os.makedirs(self.config['transcription_dir'], exist_ok=True)
        
    def load_config(self, config_file):
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {config_file} not found. Please create it from config.example.json")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {config_file}")
            raise
    
    def calculate_md5(self, file_path):
        """Calculate MD5 hash of a file to detect duplicates."""
        # Using MD5 for file deduplication only, not for security purposes
        hash_md5 = hashlib.md5(usedforsecurity=False)  # nosec B324
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating MD5 for {file_path}: {e}")
            return None
    
    def clean_filename(self, filename):
        """Clean filename by removing invalid characters."""
        return re.sub(r'[\\/*?:"<>|]', "_", filename)
    
    async def setup_telegram_client(self):
        """Setup and authenticate Telegram client."""
        try:
            self.client = TelegramClient(
                'session_name',
                self.config['telegram']['api_id'],
                self.config['telegram']['api_hash']
            )
            await self.client.start(self.config['telegram']['phone'])
            logger.info("Telegram client connected successfully")
        except Exception as e:
            logger.error(f"Failed to setup Telegram client: {e}")
            raise
    
    def setup_google_services(self):
        """Setup Google Docs and Drive services."""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.config['google']['credentials_file'],
                scopes=[
                    'https://www.googleapis.com/auth/documents',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
            
            self.docs_service = build('docs', 'v1', credentials=credentials)
            self.drive_service = build('drive', 'v3', credentials=credentials)
            logger.info("Google services setup successfully")
        except Exception as e:
            logger.error(f"Failed to setup Google services: {e}")
            raise
    
    def transcribe_audio(self, file_path):
        """Transcribe audio file using AssemblyAI."""
        logger.info(f"Starting transcription of {file_path}")
        
        try:
            # Step 1: Upload audio file
            upload_endpoint = "https://api.assemblyai.com/v2/upload"
            headers = {"authorization": self.config['assemblyai']['api_key']}
            
            with open(file_path, "rb") as f:
                response = requests.post(upload_endpoint, headers=headers, data=f, timeout=300)
            
            if response.status_code != 200:
                logger.error(f"Upload failed: {response.text}")
                return None
            
            audio_url = response.json()["upload_url"]
            
            # Step 2: Submit transcription job
            transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
            json_data = {
                "audio_url": audio_url,
                "language_code": self.config['assemblyai'].get('language_code', 'fr')
            }
            
            response = requests.post(transcript_endpoint, json=json_data, headers=headers, timeout=60)
            
            if response.status_code != 200:
                logger.error(f"Transcription submission failed: {response.text}")
                return None
            
            transcript_id = response.json()["id"]
            
            # Step 3: Poll for completion
            polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
            while True:
                response = requests.get(polling_endpoint, headers=headers, timeout=30)
                status = response.json()["status"]
                
                if status == "completed":
                    logger.info(f"Transcription completed for {file_path}")
                    return response.json()["text"]
                elif status == "error":
                    logger.error(f"Transcription error: {response.json()}")
                    return None
                
                logger.info("Transcription in progress...")
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return None
    
    def upload_to_google_docs(self, channel_name, audio_name, transcription_text):
        """Upload transcription to Google Docs."""
        try:
            # Check if document already exists
            query = f"name = '{channel_name} Transcriptions' and mimeType = 'application/vnd.google-apps.document'"
            results = self.drive_service.files().list(q=query).execute()
            items = results.get('files', [])
            
            if not items:
                # Create new document
                doc_metadata = {
                    'name': f'{channel_name} Transcriptions',
                    'mimeType': 'application/vnd.google-apps.document'
                }
                doc = self.drive_service.files().create(body=doc_metadata).execute()
                doc_id = doc['id']
                logger.info(f"New document created with ID: {doc_id}")
            else:
                doc_id = items[0]['id']
                logger.info(f"Using existing document with ID: {doc_id}")
            
            # Add content to document
            requests_body = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': f"## {audio_name} ##\n\n{transcription_text}\n\n{'='*80}\n\n"
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=doc_id, body={'requests': requests_body}
            ).execute()
            
            logger.info(f"Transcription added to Google Doc")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error uploading to Google Docs: {e}")
            return None
    
    async def process_channel(self):
        """Main method to process the Telegram channel."""
        file_hashes = {}
        file_counter = 1
        
        try:
            # Get channel entity
            channel_entity = await self.client.get_entity(self.config['telegram']['channel_id'])
            channel_name = self.clean_filename(channel_entity.title)
            
            logger.info(f"Processing channel: {channel_name}")
            
            # Iterate through messages
            async for message in self.client.iter_messages(channel_entity):
                if message.audio or message.voice or message.document:
                    file = message.audio or message.voice or message.document
                    
                    # Check if it's an audio file
                    if hasattr(file, 'mime_type') and 'audio' in file.mime_type:
                        # Generate filename
                        original_name = getattr(file, 'file_name', f"audio_{message.id}.mp3")
                        if not original_name:
                            original_name = f"audio_{message.id}.mp3"
                        
                        original_name = self.clean_filename(original_name)
                        message_date = message.date.strftime("%Y%m%d")
                        new_filename = f"{channel_name}_{file_counter:03d}_{original_name}_{message_date}.mp3"
                        file_path = os.path.join(self.config['download_dir'], new_filename)
                        
                        # Download file
                        logger.info(f"Downloading {new_filename}")
                        await self.client.download_media(message, file_path)
                        
                        # Check for duplicates
                        file_md5 = self.calculate_md5(file_path)
                        if file_md5 and file_md5 in file_hashes:
                            logger.info(f"Duplicate detected, removing {new_filename}")
                            os.remove(file_path)
                            continue
                        
                        if file_md5:
                            file_hashes[file_md5] = file_path
                        
                        # Transcribe audio
                        transcription = self.transcribe_audio(file_path)
                        if transcription:
                            # Save transcription locally
                            transcription_path = os.path.join(
                                self.config['transcription_dir'],
                                f"{new_filename}.txt"
                            )
                            with open(transcription_path, 'w', encoding='utf-8') as f:
                                f.write(transcription)
                            
                            # Upload to Google Docs
                            self.upload_to_google_docs(channel_name, new_filename, transcription)
                        
                        file_counter += 1
                        
                        # Optional: Add delay to avoid rate limiting
                        await asyncio.sleep(1)
            
            logger.info("Processing completed successfully")
            
        except Exception as e:
            logger.error(f"Error processing channel: {e}")
            raise
    
    async def run(self):
        """Run the complete transcription process."""
        try:
            await self.setup_telegram_client()
            self.setup_google_services()
            await self.process_channel()
        finally:
            if self.client:
                await self.client.disconnect()


async def main():
    """Main entry point."""
    transcriber = AudioTranscriber()
    await transcriber.run()


if __name__ == '__main__':
    asyncio.run(main())