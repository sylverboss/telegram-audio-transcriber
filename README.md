# AudioTranscriber

A Python application that automatically downloads, organizes, and transcribes audio files from Telegram channels using AssemblyAI and uploads structured transcriptions to Google Docs.

## Features

- 🎵 Downloads MP3/audio files from Telegram channels
- 🔍 Automatically detects and removes duplicate files
- 📝 Renames files chronologically with structured naming
- 🎤 Transcribes audio using AssemblyAI's powerful speech-to-text API
- 📄 Organizes transcriptions in Google Docs with proper formatting
- 📊 Comprehensive logging and error handling

## Prerequisites

Before you begin, ensure you have:

- Python 3.7 or higher
- A Telegram account and API credentials
- An AssemblyAI account and API key
- Google Cloud project with Docs and Drive API enabled
- Google service account credentials

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sylverboss/telegram-audio-transcriber.git
   cd telegram-audio-transcriber
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### 1. Telegram API Setup

1. Visit [my.telegram.org](https://my.telegram.org/apps)
2. Create a new application with:
   - **App title:** AudioTranscriber Pro
   - **Short name:** audiotrans
   - **URL:** https://github.com/yourusername/telegram-audio-transcriber
   - **Description:** Application for extracting and transcribing audio from Telegram channels
3. Note your `api_id` and `api_hash`

### 2. AssemblyAI Setup

1. Sign up at [AssemblyAI](https://www.assemblyai.com/)
2. Get your API key from the dashboard

### 3. Google Cloud Setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Google Drive API and Google Docs API
3. Create a service account:
   - Go to IAM & Admin > Service Accounts
   - Create a new service account
   - Download the JSON credentials file
   - Grant appropriate permissions (Drive Editor, Docs Editor)

### 4. Configuration File

1. Copy the example configuration:
   ```bash
   cp config.example.json config.json
   ```

2. Edit `config.json` with your credentials and the channel ID you want to transcribe.:
   ```json
   {
     "telegram": {
       "api_id": "your_telegram_api_id",
       "api_hash": "your_telegram_api_hash",
       "phone": "+1234567890",
       "channel_id": -0
     },
     "assemblyai": {
       "api_key": "your_assemblyai_api_key",
       "language_code": "fr"
     },
     "google": {
       "credentials_file": "path/to/google-credentials.json"
     },
     "download_dir": "downloads",
     "transcription_dir": "transcriptions"
   }
   ```

## Usage

1. **Run the application:**
   ```bash
   python audiotranscriber.py
   ```

2. **First-time setup:**
   - You'll be prompted to enter a verification code sent to your Telegram account
   - This creates a session file for future runs

3. **Monitor progress:**
   - Watch the console output for download and transcription progress
   - Check `audiotranscriber.log` for detailed logs
   - Transcriptions will appear in your Google Drive

## File Structure

```
audiotranscriber/
├── audiotranscriber.py          # Main application
├── config.json                  # Your configuration (create from example)
├── config.example.json          # Configuration template
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
├── downloads/                  # Downloaded audio files
├── transcriptions/             # Local transcription backups
└── logs/                       # Application logs
```

## Output Format

### File Naming
Audio files are renamed following this pattern:
```
{ChannelName}_{Number}_{OriginalName}_{Date}.mp3
```
Example: `MyChannel_001_interview_20241201.mp3`

### Google Docs Structure
Each channel gets one Google Doc titled "{ChannelName} Transcriptions" containing:
- Individual sections for each audio file
- Structured headers with file information
- Complete transcription text
- Separator lines between transcriptions

## Logging

The application creates detailed logs in:
- Console output (INFO level)
- `audiotranscriber.log` file (all levels)

## Error Handling

The application handles various error scenarios:
- Network connectivity issues
- API rate limiting
- File permission problems
- Duplicate detection
- Transcription failures

## Troubleshooting

### Common Issues

**ModuleNotFoundError:**
```bash
pip install -r requirements.txt
```

**Telegram Authentication Errors:**
- Verify your API credentials
- Ensure phone number format includes country code
- Check that your account has access to the target channel

**Google API Errors:**
- Verify service account permissions
- Ensure APIs are enabled in Google Cloud Console
- Check credentials file path

**AssemblyAI Errors:**
- Verify API key validity
- Check account usage limits
- Ensure supported audio format

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for personal and educational use. Ensure you have proper permissions to download and transcribe content from Telegram channels. Respect copyright and privacy laws in your jurisdiction.

## Support

If you encounter issues or have questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue on GitHub with detailed information about your problem

## Roadmap

- [ ] Support for additional audio formats
- [ ] Batch processing improvements
- [ ] Web interface
- [ ] Docker containerization
- [ ] Multiple language support
- [ ] Advanced filtering options