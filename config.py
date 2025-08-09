"""Configuration settings for the Discord translation bot."""

# Supported languages with their codes and names
SUPPORTED_LANGUAGES = {
    'ar': 'العربية (Arabic)',
    'en': 'English',
    'es': 'Español (Spanish)', 
    'fr': 'Français (French)',
    'de': 'Deutsch (German)',
    'it': 'Italiano (Italian)',
    'pt': 'Português (Portuguese)',
    'ru': 'Русский (Russian)',
    'zh': '中文 (Chinese)',
    'ja': '日本語 (Japanese)',
    'ko': '한국어 (Korean)',
    'tr': 'Türkçe (Turkish)',
    'nl': 'Nederlands (Dutch)',
    'pl': 'Polski (Polish)',
    'sv': 'Svenska (Swedish)',
    'da': 'Dansk (Danish)',
    'no': 'Norsk (Norwegian)',
    'fi': 'Suomi (Finnish)',
    'cs': 'Čeština (Czech)',
    'hu': 'Magyar (Hungarian)',
    'ro': 'Română (Romanian)',
    'bg': 'Български (Bulgarian)',
    'hr': 'Hrvatski (Croatian)',
    'sk': 'Slovenčina (Slovak)',
    'sl': 'Slovenščina (Slovenian)',
    'et': 'Eesti (Estonian)',
    'lv': 'Latviešu (Latvian)',
    'lt': 'Lietuvių (Lithuanian)',
    'mt': 'Malti (Maltese)',
    'ga': 'Gaeilge (Irish)',
    'cy': 'Cymraeg (Welsh)',
    'is': 'Íslenska (Icelandic)',
    'mk': 'Македонски (Macedonian)',
    'sq': 'Shqip (Albanian)',
    'eu': 'Euskera (Basque)',
    'ca': 'Català (Catalan)',
    'gl': 'Galego (Galician)',
    'hi': 'हिन्दी (Hindi)',
    'th': 'ไทย (Thai)',
    'vi': 'Tiếng Việt (Vietnamese)',
    'id': 'Bahasa Indonesia',
    'ms': 'Bahasa Melayu (Malay)',
    'tl': 'Filipino (Tagalog)',
    'sw': 'Kiswahili (Swahili)',
    'af': 'Afrikaans',
    'am': 'አማርኛ (Amharic)',
    'be': 'Беларуская (Belarusian)',
    'bn': 'বাংলা (Bengali)',
    'bs': 'Bosanski (Bosnian)',
    'el': 'Ελληνικά (Greek)',
    'fa': 'فارسی (Persian)',
    'gu': 'ગુજરાતી (Gujarati)',
    'kn': 'ಕನ್ನಡ (Kannada)',
    'ml': 'മലയാളം (Malayalam)',
    'mr': 'मराठी (Marathi)',
    'ne': 'नेपाली (Nepali)',
    'pa': 'ਪੰਜਾਬੀ (Punjabi)',
    'si': 'සිංහල (Sinhala)',
    'ta': 'தமிழ் (Tamil)',
    'te': 'తెలుగు (Telugu)',
    'ur': 'اردو (Urdu)',
    'uz': "O'zbek (Uzbek)",
    'kk': 'Қазақша (Kazakh)',
    'ky': 'Кыргызча (Kyrgyz)',
    'mn': 'Монгол (Mongolian)',
    'my': 'မြန်မာ (Myanmar)',
    'km': 'ខ្មែរ (Khmer)',
    'lo': 'ລາວ (Lao)',
    'ka': 'ქართული (Georgian)',
    'hy': 'Հայերեն (Armenian)',
    'az': 'Azərbaycan (Azerbaijani)',
}

# Language code mappings for different translation services
LANGUAGE_MAPPINGS = {
    'zh': 'zh-cn',  # Chinese Simplified
    'pt': 'pt-br',  # Portuguese (Brazil)
}

# Default language
DEFAULT_LANGUAGE = 'en'

# Bot settings
BOT_PREFIX = '!'
MAX_MESSAGE_LENGTH = 2000
TRANSLATION_TIMEOUT = 30  # seconds

# Translation model settings
MODEL_CACHE_DIR = "./models"
MAX_TRANSLATION_LENGTH = 1000  # characters
