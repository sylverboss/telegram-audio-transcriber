#!/usr/bin/env python3
"""
Setup script for AudioTranscriber
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="telegram-audio-transcriber",
    version="1.0.0",
    author="sylverboss",
    author_email="github.com.purely580@passinbox.com",
    description="Telegram audio files transcription tool using AssemblyAI and Google Docs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sylverboss/telegram-audio-transcriber",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "telegram-audio-transcriber=audiotranscriber:main",
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/sylverboss/telegram-audio-transcriber/issues",
        "Documentation": "https://github.com/sylverboss/telegram-audio-transcriber#readme",
        "Source Code": "https://github.com/sylverboss/telegram-audio-transcriber",
    },
)