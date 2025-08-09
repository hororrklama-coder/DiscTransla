import asyncio
import os

# Simple Discord bot without heavy dependencies
print("🚀 بدء تشغيل البوت المبسط...")
print("🚀 Starting simplified bot...")

try:
    import discord
    from discord.ext import commands
    print("✅ Discord.py متوفر")
    print("✅ Discord.py available")
    DISCORD_AVAILABLE = True
except ImportError:
    print("❌ Discord.py غير متوفر")
    print("❌ Discord.py not available")
    DISCORD_AVAILABLE = False

if DISCORD_AVAILABLE:
    from bot import TranslationBot
    
    async def main():
        """Main entry point for the Discord translation bot."""
        token = os.getenv('DISCORD_BOT_TOKEN')
        
        if not token:
            print("خطأ: لم يتم العثور على DISCORD_BOT_TOKEN في متغيرات البيئة")
            print("Error: DISCORD_BOT_TOKEN not found in environment variables")
            return
        
        bot = TranslationBot()
        
        try:
            print("🤖 بدء تشغيل بوت الترجمة...")
            print("🤖 Starting translation bot...")
            await bot.start(token)
        except KeyboardInterrupt:
            print("🛑 تم إيقاف البوت بواسطة المستخدم")
            print("🛑 Bot stopped by user")
        except discord.LoginFailure:
            print("❌ خطأ في رمز البوت - تحقق من DISCORD_BOT_TOKEN")
            print("❌ Bot token error - check DISCORD_BOT_TOKEN")
        except discord.HTTPException as e:
            print(f"❌ خطأ HTTP: {e}")
            print(f"❌ HTTP error: {e}")
        except Exception as e:
            print(f"❌ خطأ في تشغيل البوت: {e}")
            print(f"❌ Error running bot: {e}")
            print("🔄 محاولة إعادة التشغيل...")
            print("🔄 Attempting restart...")
        finally:
            try:
                await bot.close()
            except:
                pass
else:
    async def main():
        print("❌ لا يمكن تشغيل البوت بدون Discord.py")
        print("❌ Cannot run bot without Discord.py")
        print("يرجى تثبيت المكتبات المطلوبة...")
        print("Please install required libraries...")

if __name__ == "__main__":
    asyncio.run(main())
