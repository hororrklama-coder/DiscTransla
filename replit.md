# Discord Translation Bot

## Overview

This is a Discord bot that provides instant translation capabilities with interactive buttons. Users can translate messages in Discord channels by clicking a translate button that appears with messages. The bot supports over 40 languages and maintains user language preferences. It uses Hugging Face transformer models for accurate translation and includes language detection to automatically identify source languages.

## User Preferences

Preferred communication style: Simple, everyday language.
Bot behavior: Professional translation bot with automatic buttons under all messages, buttons disappear after 5 minutes to reduce clutter.

## System Architecture

### Bot Framework
- **Discord.py Library**: Uses the modern discord.py library with slash commands and UI components
- **Asynchronous Design**: Built on asyncio for handling multiple concurrent translation requests
- **Interactive UI**: Implements Discord's button system for user-friendly translation interactions

### Translation Engine
- **Cloud-Based Translation**: Uses free cloud APIs (MyMemory and LibreTranslate) for translation to save memory
- **No Local Storage**: No model downloads or local caching to minimize storage requirements
- **Language Detection**: Automatic source language detection using the langdetect library
- **Multiple API Fallbacks**: Primary and backup translation services for reliability

### Language Management
- **Multi-language Support**: Supports 40+ languages including Arabic, English, Spanish, French, German, and many others
- **User Preferences**: Persistent storage of user language preferences in JSON format
- **Bilingual Interface**: Bot messages display in both Arabic and English for accessibility

### Data Storage
- **File-based Persistence**: Uses JSON files for storing user language preferences
- **Cloud Translation**: No local model storage, all translation via cloud APIs
- **No Database Dependency**: Lightweight approach without requiring external database setup
- **Memory Optimized**: Minimal local storage usage to work within Replit's memory constraints

### Message Processing
- **Interactive Buttons**: Translation triggered through Discord UI buttons attached to messages
- **Ephemeral Responses**: Private translation responses that only the requesting user can see
- **Message Length Limits**: Configurable maximum message length for translation processing
- **Error Handling**: Comprehensive error handling for translation failures and unsupported content

## External Dependencies

### Core Libraries
- **discord.py**: Discord API wrapper for bot functionality
- **aiohttp**: HTTP client for cloud translation API requests
- **langdetect**: Language detection for automatic source language identification

### Translation Services
- **MyMemory API**: Primary free translation service (no API key required)
- **LibreTranslate API**: Backup free translation service for reliability

### Environment Configuration
- **DISCORD_BOT_TOKEN**: Required environment variable for Discord API authentication
- **User Preferences**: JSON file storage for persistent user language settings