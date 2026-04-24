# AudibleSense

AudibleSense is an advanced, end-to-end video and audio translation pipeline with a modern web dashboard. It automates the extraction, transcription, translation, and gender-aware speech synthesis of videos, providing an intuitive interface for seamless dubbing and localization.

## Features

- **Video Input & Preprocessing**: Supports standard local file uploads (`.mp4`, `.avi`, `.mov`, `.mkv`, audio files) as well as direct YouTube URL downloads.
- **Speech Recognition (ASR)**: Uses OpenAI's Whisper model to accurately transcribe audio and generate subtitles (`.vtt`).
- **Subtitle Translation**: Automatically translates generated subtitles into various target languages (e.g., Hindi, Telugu, French, Tamil, Kannada) using Google Translate.
- **Emotion & Gender-Aware Speech Synthesis**: Uses Edge-TTS to synthesize natural-sounding speech mimicry. It automatically detects the speaker's gender from the original audio and applies appropriate pitch-shifting for a lifelike voice reproduction.
- **Video & Audio Merging**: Seamlessly merges the newly synthesized translated audio with the original video, ensuring high-quality audio-video synchronization using FFmpeg.
- **Premium Web Dashboard**: A fully featured Flask-based web interface sporting a modern, dark-mode aesthetic with glassmorphism, micro-animations, and intuitive form controls. 

## Requirements
Make sure you have the following installed:
- Python 3.8+
- [FFmpeg](https://ffmpeg.org/download.html) (must be installed and added to your system PATH)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Gowtham1429/AudibleSense.git
   cd AudibleSense/AudibleSense
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

You can run the web dashboard using Flask:

```bash
python app.py
```

After starting the server, open your web browser and navigate to `http://127.0.0.1:5000/`. From there, you can follow the pipeline step-by-step:
1. **Module 1**: Upload a video, provide a valid YouTube link, or upload an audio file to extract the audio track.
2. **Module 2**: Generate a transcription/subtitle file from the audio.
3. **Module 3**: Translate the transcription to your desired target language.
4. **Module 4**: Synthesize the translated text into speech with automatic gender detection.
5. **Module 5**: Merge the synthesized speech with the original video to produce the final translated video.

## Built With

- **Flask** - Web framework
- **TensorFlow / Keras** - Machine Learning Frameworks
- **OpenAI Whisper** - Speech Recognition
- **Edge-TTS** - Text-to-Speech Synthesis
- **Googletrans** - Translation
- **FFmpeg-python** - Video and Audio Processing

## License

This project is open-source and available under the terms of the MIT License.
