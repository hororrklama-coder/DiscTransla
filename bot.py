"""Discord bot for instant translation with interactive buttons."""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from typing import Optional
import re

from translator import Translator
from language_manager import LanguageManager
from config import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, MAX_MESSAGE_LENGTH

class TranslationView(discord.ui.View):
    """View containing translation buttons for messages."""
    
    def __init__(self, original_message: str, author_id: int):
        super().__init__(timeout=300)  # 5 minutes timeout - shorter to reduce clutter
        self.original_message = original_message
        self.author_id = author_id
    
    async def on_timeout(self):
        """Remove buttons when timeout expires."""
        try:
            # Disable all buttons
            for item in self.children:
                item.disabled = True
            
            # Try to edit the message to remove buttons
            if hasattr(self, 'message') and self.message:
                await self.message.edit(view=self)
        except:
            pass  # Ignore errors if message was deleted or we can't edit
    
    @discord.ui.button(label="ترجم", style=discord.ButtonStyle.primary, emoji="🌐")
    async def translate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle translation button click."""
        bot = interaction.client
        
        # Get user's preferred language
        user_lang = bot.language_manager.get_user_language(interaction.user.id)
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Translate the message
            translated_text, source_lang = await bot.translator.translate_text(
                self.original_message, 
                user_lang
            )
            
            if not translated_text:
                embed = discord.Embed(
                    title="❌ خطأ في الترجمة / Translation Error",
                    description="عذراً، لا يمكن ترجمة هذه الرسالة.\nSorry, this message cannot be translated.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Create translation embed
            source_lang_name = bot.language_manager.get_language_name(source_lang)
            target_lang_name = bot.language_manager.get_language_name(user_lang)
            
            embed = discord.Embed(
                title="🌐 ترجمة / Translation",
                color=discord.Color.blue()
            )
            
            # Add fields for source and translation
            embed.add_field(
                name=f"📝 النص الأصلي ({source_lang_name}) / Original ({source_lang_name})",
                value=self.original_message[:1000] + "..." if len(self.original_message) > 1000 else self.original_message,
                inline=False
            )
            
            embed.add_field(
                name=f"🎯 الترجمة ({target_lang_name}) / Translation ({target_lang_name})",
                value=translated_text[:1000] + "..." if len(translated_text) > 1000 else translated_text,
                inline=False
            )
            
            embed.set_footer(text=f"مُترجم بواسطة Cloud APIs • لغتك المفضلة: {target_lang_name}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ / Error",
                description=f"حدث خطأ أثناء الترجمة: {str(e)}\nAn error occurred during translation: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="إعدادات", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def settings_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle settings button click."""
        bot = interaction.client
        current_lang = bot.language_manager.get_user_language(interaction.user.id)
        current_lang_name = bot.language_manager.get_language_name(current_lang)
        
        # Check button visibility setting
        buttons_enabled = bot.user_button_settings.get(interaction.user.id, True)
        button_status = "مفعلة ✅ / Enabled ✅" if buttons_enabled else "معطلة ❌ / Disabled ❌"
        
        embed = discord.Embed(
            title="⚙️ إعدادات الترجمة / Translation Settings",
            description=f"لغتك الحالية: **{current_lang_name}**\nYour current language: **{current_lang_name}**\n\nحالة الأزرار: {button_status}\nButtons status: {button_status}",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="🔧 تغيير اللغة / Change Language",
            value="لتغيير لغتك المفضلة، اكتب:\nTo change your preferred language, type:\n`/set_language [code]`\n\nأمثلة / Examples:\n`/set_language ar` للعربية\n`/set_language en` للإنجليزية\n`/set_language es` للإسبانية",
            inline=False
        )
        
        embed.add_field(
            name="🌍 اللغات المتاحة / Available Languages", 
            value="استخدم الأمر: `/languages`\nUse command: `/languages`",
            inline=False
        )
        
        embed.add_field(
            name="👁️ التحكم في الأزرار / Button Control",
            value="لإخفاء/إظهار أزرار الترجمة:\nTo hide/show translation buttons:\n`/buttons off` - لإخفاء الأزرار\n`/buttons on` - لإظهار الأزرار\n`/translate_old` - ترجمة الرسائل القديمة",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class OldMessagesView(discord.ui.View):
    """View for selecting old messages to translate."""
    
    def __init__(self, messages):
        super().__init__(timeout=60)
        self.messages = messages
        
        # Add buttons for first 5 messages
        for i, msg in enumerate(messages[:5]):
            button = discord.ui.Button(
                label=f"رسالة {i+1}",
                style=discord.ButtonStyle.primary,
                custom_id=f"old_msg_{i}"
            )
            button.callback = self.create_callback(i, msg)
            self.add_item(button)
    
    def create_callback(self, index, message):
        async def callback(interaction):
            # Create translation view for the selected message
            view = TranslationView(message.content, interaction.user.id)
            
            embed = discord.Embed(
                title="📝 الرسالة المحددة / Selected Message",
                description=f"**من / From:** {message.author.display_name}\n**النص / Text:** {message.content[:500]}",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(
                embed=embed,
                view=view,
                ephemeral=True
            )
        
        return callback

class TranslationBot(commands.Bot):
    """Discord bot for translation services."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # Required for reading message content
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.translator = Translator()
        self.language_manager = LanguageManager()
        
        # User preferences for button visibility
        self.user_button_settings = {}  # user_id: True/False (True = show buttons)
    
    async def setup_hook(self):
        """Setup hook called when bot is starting."""
        await self.tree.sync()
        print("🔄 تم مزامنة أوامر البوت")
        print("🔄 Bot commands synced")
    
    async def on_ready(self):
        """Called when bot is ready."""
        print(f"✅ {self.user} متصل ومستعد!")
        print(f"✅ {self.user} is connected and ready!")
        print(f"🌍 يدعم {len(SUPPORTED_LANGUAGES)} لغة")
        print(f"🌍 Supporting {len(SUPPORTED_LANGUAGES)} languages")
        print(f"👥 مُسجل في {len(self.guilds)} خادم")
        print(f"👥 Connected to {len(self.guilds)} servers")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="الرسائل للترجمة | Messages to translate"
            )
        )
    
    async def on_message(self, message):
        """Handle new messages and add translation buttons."""
        print(f"📨 رسالة جديدة من {message.author}: {message.content[:50]}...")
        print(f"📨 New message from {message.author}: {message.content[:50]}...")
        
        # Ignore bot messages
        if message.author.bot:
            print("🤖 تجاهل رسالة البوت")
            return
        
        # Handle button control commands
        content_lower = message.content.lower().strip()
        if content_lower.startswith('/buttons'):
            parts = content_lower.split()
            if len(parts) >= 2:
                if parts[1] == 'off':
                    self.user_button_settings[message.author.id] = False
                    await message.reply("❌ تم إخفاء أزرار الترجمة\n❌ Translation buttons disabled", mention_author=False)
                    return
                elif parts[1] == 'on':
                    self.user_button_settings[message.author.id] = True
                    await message.reply("✅ تم تفعيل أزرار الترجمة\n✅ Translation buttons enabled", mention_author=False)
                    return
        
        # Handle translate old messages command
        if content_lower.startswith('/translate_old'):
            await self.handle_old_messages_translation(message)
            return
        
        # Skip empty messages or very short ones
        if not message.content or len(message.content.strip()) < 3:
            return
        
        # Skip bot commands but allow text commands for debugging
        if message.content.startswith(('!', '$', '%', '&', '*', '+', '=')):
            return
        
        # Skip messages that are mostly emojis or special characters
        text_content = re.sub(r'[^\w\s]', '', message.content)
        if len(text_content.strip()) < 2:
            return
        
        # Check if user has buttons enabled
        if not self.user_button_settings.get(message.author.id, True):
            return  # User has disabled buttons, don't add any
        
        try:
            print("✅ محاولة إضافة زر الترجمة...")
            print("✅ Attempting to add translation button...")
            
            # Add translation button to the message
            view = TranslationView(message.content, message.author.id)
            
            # Don't send button if message is too long
            if len(message.content) > 1500:
                print("⚠️ الرسالة طويلة جداً")
                return
            
            # Handle text commands for debugging - support various formats
            content_clean = message.content.replace(' ', '')  # Remove all spaces
            if content_clean.startswith('/set_language') or content_clean.startswith('/setlanguage'):
                # Extract language code from various formats
                parts = message.content.replace('/', '').replace('set_language', '').replace('setlanguage', '').strip().split()
                if parts and len(parts) > 0:
                    lang_code = parts[0].lower()
                    if self.language_manager.is_language_supported(lang_code):
                        success = self.language_manager.set_user_language(message.author.id, lang_code)
                        if success:
                            lang_name = self.language_manager.get_language_name(lang_code)
                            await message.reply(f"✅ تم تعيين لغتك إلى: **{lang_name}**\nYour language set to: **{lang_name}**", mention_author=False)
                        else:
                            await message.reply("❌ فشل في تحديث اللغة\nFailed to update language", mention_author=False)
                    else:
                        await message.reply(f"❌ لغة غير مدعومة: {lang_code}\nUnsupported language: {lang_code}\n\nاللغات المدعومة: ar, en, es, fr, de, it, pt, ru, zh, ja, ko", mention_author=False)
                else:
                    await message.reply("❌ يرجى كتابة كود اللغة\nPlease provide language code\nمثال/Example: /set_language ar", mention_author=False)
                return
            
            # Send the button as a reply (but don't mention)
            reply_message = await message.reply(
                "🌐 اضغط للترجمة • Click to translate",
                view=view,
                mention_author=False
            )
            # Store reference for timeout handling
            view.message = reply_message
            print("🎯 تم إضافة زر الترجمة بنجاح!")
            print("🎯 Translation button added successfully!")
            
        except discord.HTTPException:
            # Handle rate limits or permission errors silently
            pass
        except Exception as e:
            print(f"❌ خطأ في معالجة الرسالة: {e}")
            print(f"❌ Error processing message: {e}")
    
    async def handle_old_messages_translation(self, message):
        """Handle translation of old messages in the channel."""
        try:
            # Get the channel
            channel = message.channel
            
            # Fetch last 10 messages (excluding bot messages)
            messages = []
            async for msg in channel.history(limit=20):
                if not msg.author.bot and msg.content and len(msg.content.strip()) > 2:
                    messages.append(msg)
                    if len(messages) >= 10:
                        break
            
            if not messages:
                await message.reply("❌ لا توجد رسائل قديمة للترجمة\n❌ No old messages found to translate", mention_author=False)
                return
            
            embed = discord.Embed(
                title="📜 الرسائل القديمة / Old Messages",
                description="اختر رسالة لترجمتها:\nChoose a message to translate:",
                color=discord.Color.blue()
            )
            
            # Create view with buttons for each message
            view = OldMessagesView(messages)
            
            # Add message previews to embed
            for i, msg in enumerate(messages[:5]):  # Show first 5
                preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                embed.add_field(
                    name=f"{i+1}. {msg.author.display_name}",
                    value=f"`{preview}`",
                    inline=False
                )
            
            await message.reply(embed=embed, view=view, mention_author=False)
            
        except Exception as e:
            print(f"❌ خطأ في معالجة الرسائل القديمة: {e}")
            await message.reply("❌ خطأ في الوصول للرسائل القديمة\n❌ Error accessing old messages", mention_author=False)
    
    @app_commands.command(name="set_language", description="اضبط لغتك المفضلة للترجمة / Set your preferred language for translation")
    @app_commands.describe(language="كود اللغة (مثل: ar, en, es) / Language code (e.g: ar, en, es)")
    async def set_language(self, interaction: discord.Interaction, language: str):
        """Set user's preferred language."""
        language = language.lower().strip()
        
        if not self.language_manager.is_language_supported(language):
            embed = discord.Embed(
                title="❌ لغة غير مدعومة / Unsupported Language",
                description=f"اللغة `{language}` غير مدعومة.\nLanguage `{language}` is not supported.",
                color=discord.Color.red()
            )
            
            # Show some supported languages
            embed.add_field(
                name="🌍 بعض اللغات المدعومة / Some Supported Languages",
                value="🇸🇦 `ar` العربية\n🇺🇸 `en` English\n🇪🇸 `es` Español\n🇫🇷 `fr` Français\n🇩🇪 `de` Deutsch\n🇮🇹 `it` Italiano\n🇷🇺 `ru` Русский\n🇨🇳 `zh` 中文\n🇯🇵 `ja` 日本語\n🇰🇷 `ko` 한국어",
                inline=False
            )
            
            embed.add_field(
                name="📋 للحصول على القائمة الكاملة / For complete list",
                value="استخدم الأمر `/languages`\nUse command `/languages`",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Set the language
        success = self.language_manager.set_user_language(interaction.user.id, language)
        
        if success:
            lang_name = self.language_manager.get_language_name(language)
            embed = discord.Embed(
                title="✅ تم تحديث اللغة / Language Updated",
                description=f"تم تعيين لغتك المفضلة إلى: **{lang_name}**\nYour preferred language has been set to: **{lang_name}**",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="💡 كيفية الاستخدام / How to use",
                value="الآن اضغط على أزرار الترجمة تحت أي رسالة لترجمتها إلى لغتك!\nNow click translation buttons under any message to translate to your language!",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ خطأ / Error",
                description="فشل في تحديث اللغة. حاول مرة أخرى.\nFailed to update language. Please try again.",
                color=discord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="languages", description="عرض جميع اللغات المدعومة / Show all supported languages")
    async def languages(self, interaction: discord.Interaction):
        """Show all supported languages."""
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="🌍 اللغات المدعومة / Supported Languages",
            description="يدعم البوت الترجمة إلى ومن اللغات التالية:\nThe bot supports translation to and from the following languages:",
            color=discord.Color.blue()
        )
        
        # Split languages into chunks to fit in embed fields
        languages = list(SUPPORTED_LANGUAGES.items())
        chunk_size = 15
        
        for i in range(0, len(languages), chunk_size):
            chunk = languages[i:i + chunk_size]
            
            field_value = "\n".join([f"`{code}` - {name}" for code, name in chunk])
            field_name = f"اللغات {i//chunk_size + 1} / Languages {i//chunk_size + 1}"
            
            embed.add_field(name=field_name, value=field_value, inline=True)
        
        embed.add_field(
            name="📝 كيفية الاستخدام / How to use",
            value="استخدم `/set_language [كود اللغة]` لتعيين لغتك المفضلة\nUse `/set_language [language_code]` to set your preferred language",
            inline=False
        )
        
        embed.set_footer(text=f"إجمالي اللغات المدعومة: {len(SUPPORTED_LANGUAGES)} | Total supported languages: {len(SUPPORTED_LANGUAGES)}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="my_language", description="عرض لغتك المفضلة الحالية / Show your current preferred language")
    async def my_language(self, interaction: discord.Interaction):
        """Show user's current preferred language."""
        user_lang = self.language_manager.get_user_language(interaction.user.id)
        lang_name = self.language_manager.get_language_name(user_lang)
        
        embed = discord.Embed(
            title="🌐 لغتك المفضلة / Your Preferred Language",
            description=f"لغتك المفضلة الحالية هي: **{lang_name}** (`{user_lang}`)\nYour current preferred language is: **{lang_name}** (`{user_lang}`)",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="💡 تغيير اللغة / Change Language",
            value="لتغيير لغتك استخدم `/set_language`\nTo change your language use `/set_language`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="bot_info", description="معلومات عن البوت / Information about the bot")
    async def bot_info(self, interaction: discord.Interaction):
        """Show bot information."""
        embed = discord.Embed(
            title="🤖 معلومات البوت / Bot Information",
            description="بوت الترجمة الفورية مع أزرار تفاعلية\nInstant Translation Bot with Interactive Buttons",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🌍 اللغات المدعومة / Supported Languages",
            value=f"{len(SUPPORTED_LANGUAGES)} لغة\n{len(SUPPORTED_LANGUAGES)} languages",
            inline=True
        )
        
        embed.add_field(
            name="👥 المستخدمين المسجلين / Registered Users", 
            value=f"{self.language_manager.get_user_count()} مستخدم\n{self.language_manager.get_user_count()} users",
            inline=True
        )
        
        embed.add_field(
            name="🏠 الخوادم / Servers",
            value=f"{len(self.guilds)} خادم\n{len(self.guilds)} servers",
            inline=True
        )
        
        embed.add_field(
            name="🚀 المميزات / Features",
            value="• ترجمة فورية / Instant translation\n• أزرار تفاعلية / Interactive buttons\n• ردود مخفية / Private responses\n• دعم متعدد اللغات / Multi-language support\n• مجاني 100% / 100% Free",
            inline=False
        )
        
        embed.add_field(
            name="⚡ التقنيات المستخدمة / Technologies Used",
            value="• Discord.py\n• Hugging Face Transformers\n• Helsinki-NLP Models\n• Python",
            inline=False
        )
        
        embed.set_footer(text="مُطور باستخدام Hugging Face • Powered by Hugging Face")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Error handlers
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handle application command errors."""
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏰ انتظر قليلاً / Please Wait",
                description=f"يمكنك استخدام هذا الأمر مرة أخرى بعد {error.retry_after:.1f} ثانية\nYou can use this command again in {error.retry_after:.1f} seconds",
                color=discord.Color.orange()
            )
        else:
            embed = discord.Embed(
                title="❌ خطأ / Error",
                description=f"حدث خطأ: {str(error)}\nAn error occurred: {str(error)}",
                color=discord.Color.red()
            )
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            pass
    
    async def close(self):
        """Close the bot and cleanup resources."""
        await self.translator.close()
        await super().close()
