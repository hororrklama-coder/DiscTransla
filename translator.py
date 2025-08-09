"""Translation service using free cloud API - No local storage needed."""

import asyncio
import aiohttp
import json
from typing import Optional, Tuple
from langdetect import detect, DetectorFactory, LangDetectException
import re
from urllib.parse import quote

# Set seed for consistent language detection
DetectorFactory.seed = 0

class Translator:
    """Handles text translation using free cloud APIs."""
    
    def __init__(self):
        self.session = None
        print("🔧 تم تهيئة المترجم السحابي")
        print("🔧 Cloud translator initialized")
    
    async def get_session(self):
        """Get or create aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect the language of the input text."""
        try:
            # Clean text for better detection
            cleaned_text = re.sub(r'[^\w\s]', ' ', text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            if len(cleaned_text) < 3:
                return None
                
            detected = detect(cleaned_text)
            return detected
        except (LangDetectException, Exception):
            return None
    
    async def translate_with_mymemory(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Translate using MyMemory API (free, no API key required)."""
        try:
            session = await self.get_session()
            
            # MyMemory API endpoint
            url = "https://api.mymemory.translated.net/get"
            
            params = {
                'q': text,
                'langpair': f"{source_lang}|{target_lang}"
            }
            
            async with session.get(url, params=params, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('responseStatus') == 200:
                        translated = data.get('responseData', {}).get('translatedText', '')
                        if translated and translated.lower() != text.lower():
                            print(f"✅ ترجمة MyMemory: {text[:30]}... -> {translated[:30]}...")
                            return translated
                    else:
                        print(f"⚠️ MyMemory responseStatus: {data.get('responseStatus')}")
            
            return None
            
        except Exception as e:
            print(f"❌ خطأ في MyMemory API: {e}")
            return None
    
    async def translate_with_libre(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Translate using LibreTranslate API (backup method)."""
        try:
            session = await self.get_session()
            
            # Use Google Translate alternative API
            url = "https://libretranslate.com/translate"
            
            data = {
                'q': text,
                'source': source_lang,
                'target': target_lang,
                'format': 'text'
            }
            
            async with session.post(url, json=data, timeout=10) as response:
                if response.status == 200:
                    result = await response.json()
                    translated = result.get('translatedText', '')
                    if translated and translated.lower() != text.lower():
                        return translated
            
            return None
            
        except Exception as e:
            print(f"❌ خطأ في LibreTranslate API: {e}")
            return None
    
    async def split_text_smartly(self, text: str, max_length: int = 400) -> list:
        """Split text intelligently by sentences and paragraphs."""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        # Split by paragraphs first
        paragraphs = text.split('\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk + paragraph) <= max_length:
                current_chunk += paragraph + "\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph + "\n"
                else:
                    # If single paragraph is too long, split by sentences
                    sentences = paragraph.split('. ')
                    for sentence in sentences:
                        if len(current_chunk + sentence) <= max_length:
                            current_chunk += sentence + ". "
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    async def translate_text(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> Tuple[Optional[str], str]:
        """
        Translate text to target language using cloud APIs with smart text splitting.
        Returns (translated_text, detected_source_language)
        """
        try:
            # Detect source language if not provided
            if not source_lang:
                source_lang = self.detect_language(text)
                if not source_lang:
                    return None, "unknown"
            
            # Skip translation if source and target are the same
            if source_lang == target_lang:
                return text, source_lang
            
            # Skip if source is Hebrew (not supported by user requirement)
            if source_lang == 'he' or target_lang == 'he':
                return None, source_lang
            
            # Handle long texts by splitting
            if len(text) > 400:
                print(f"📝 نص طويل ({len(text)} حرف) - تقسيم للترجمة...")
                print(f"📝 Long text ({len(text)} chars) - splitting for translation...")
                
                chunks = await self.split_text_smartly(text, 400)
                translated_chunks = []
                
                for i, chunk in enumerate(chunks):
                    print(f"🔄 ترجمة جزء {i+1}/{len(chunks)}: {chunk[:50]}...")
                    
                    # Try MyMemory first
                    translated_chunk = await self.translate_with_mymemory(chunk, source_lang, target_lang)
                    
                    if not translated_chunk:
                        # Try LibreTranslate as backup
                        translated_chunk = await self.translate_with_libre(chunk, source_lang, target_lang)
                    
                    if not translated_chunk:
                        # Try through English
                        if source_lang != 'en' and target_lang != 'en':
                            en_text = await self.translate_with_mymemory(chunk, source_lang, 'en')
                            if en_text:
                                translated_chunk = await self.translate_with_mymemory(en_text, 'en', target_lang)
                    
                    if translated_chunk:
                        translated_chunks.append(translated_chunk)
                    else:
                        # If chunk translation fails, keep original
                        translated_chunks.append(chunk)
                        print(f"⚠️ فشل في ترجمة الجزء {i+1}, استخدام النص الأصلي")
                
                final_translation = "\n".join(translated_chunks)
                print(f"✅ اكتملت ترجمة النص الطويل: {len(final_translation)} حرف")
                return final_translation, source_lang
            
            # Handle short texts normally
            translated = await self.translate_with_mymemory(text, source_lang, target_lang)
            
            if not translated:
                translated = await self.translate_with_libre(text, source_lang, target_lang)
            
            if not translated:
                # Try through English for short texts
                if source_lang != 'en' and target_lang != 'en':
                    en_text = await self.translate_with_mymemory(text, source_lang, 'en')
                    if not en_text:
                        en_text = await self.translate_with_libre(text, source_lang, 'en')
                    
                    if en_text:
                        final_text = await self.translate_with_mymemory(en_text, 'en', target_lang)
                        if not final_text:
                            final_text = await self.translate_with_libre(en_text, 'en', target_lang)
                        
                        if final_text:
                            return final_text, source_lang
            
            if translated:
                return translated, source_lang
            else:
                return None, source_lang
            
        except Exception as e:
            print(f"❌ خطأ في الترجمة: {e}")
            print(f"❌ Translation error: {e}")
            return None, source_lang or "unknown"
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def clear_cache(self):
        """Clear any cached data (no local cache in this implementation)."""
        print("🧹 لا توجد ذاكرة تخزين محلية للتنظيف")
        print("🧹 No local cache to clear")