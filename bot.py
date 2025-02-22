import os
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
from collections import defaultdict
import time

from keep_alive import keep_alive

# Track user streaks and timestamps
user_streaks = defaultdict(int)
last_gif_time = defaultdict(float)

keep_alive()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def swap_pronouns(text):
    """Swap pronouns in the given text:
    'i' -> 'you'
    'you' -> 'they'
    """
    words = text.split()
    swapped_words = []
    for word in words:
        lower_word = word.lower()
        if lower_word == "i":
            swapped_words.append("you")
        elif lower_word == "you":
            swapped_words.append("they")
        elif lower_word == "im":
            swapped_words.append("you're")
        elif lower_word == "i'm":
            swapped_words.append("you're")
        elif lower_word == "youre":
            swapped_words.append("they're")
        elif lower_word == "you're":
            swapped_words.append("you're")
        elif lower_word == "your":
            swapped_words.append("their")
        elif lower_word == "ur":
            swapped_words.append("their")
        else:
            swapped_words.append(word)
    return " ".join(swapped_words)

@bot.event
async def on_ready():
    """Event handler for when the bot is ready and connected."""
    logger.info(f'Bot is ready! Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    """Event handler for processing messages."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check for Tenor links from specific user
    if (message.author.id == 991801566271123538 or message.author.id == 974297735559806986) and (message.content.startswith("https://tenor.com") or message.content.startswith("https://giphy.com")):
        content_lower = message.content.lower()
        keywords = ["watashi", "anime", "loli", "kawaii", "hoshino", "senko", "shikimori", "waku", "wataten"]
        
        if any(keyword in content_lower for keyword in keywords):
            current_time = time.time()
            user_id = message.author.id
            
            # Reset streak if more than 5 minutes passed
            if current_time - last_gif_time[user_id] > 300:
                user_streaks[user_id] = 0
                
            # Increment streak and update timestamp
            user_streaks[user_id] += 1
            last_gif_time[user_id] = current_time
            
            # Get appropriate message based on streak
            messages = [
                "# senkiggan activity detected. hush.",
                "# second gif in a row? hush, senkiggan.",
                "# senkiggan activity increasing.",
                "# warning: APPROACHING PEAK SENKIGGRENATE!",
                "# MAXIMUM SENKIGGER ALERT!!!"
            ]
            
            streak_index = min(user_streaks[user_id] - 1, 4)
            await message.reply(messages[streak_index], mention_author=True)
            return

    # Convert message to lowercase for case-insensitive matching
    content = message.content.lower()

    try:
        # Check for "ball" in the message
        if "ball" in content:
            # Find the text before "ball"
            before_ball = content.split("ball")[0].strip()
            if before_ball:
                # Swap pronouns and create response
                swapped_text = swap_pronouns(before_ball)
                response = f"# {swapped_text} what now?"
                await message.reply(response, mention_author=True)
            else:
                # If no text before "ball", use default response
                await message.reply("# what now?", mention_author=True)
            return

    except discord.errors.HTTPException as e:
        logger.error(f"HTTP Exception when sending message: {e}")
    except discord.errors.Forbidden as e:
        logger.error(f"Forbidden action when sending message: {e}")
    except Exception as e:
        logger.error(f"Unexpected error when processing message: {e}")

    # Process commands if any
    await bot.process_commands(message)

@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler for the bot."""
    logger.error(f"Error in {event}: {args} {kwargs}")

async def console_input():
    """Handle console input to send messages through the bot."""
    while True:
        message = input("Enter message to send (or 'quit' to exit): ")
        if message.lower() == 'quit':
            break
        channel_id = input("Enter channel ID to send to: ")
        try:
            channel = bot.get_channel(int(channel_id))
            if channel:
                await channel.send(message)
                print(f"Message sent to channel {channel_id}")
            else:
                print(f"Channel {channel_id} not found")
        except ValueError:
            print("Invalid channel ID")
        except Exception as e:
            print(f"Error sending message: {e}")

def main():
    """Main function to run the bot."""
    try:
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            logger.error("Discord token not found in environment variables!")
            return
            
        import asyncio
        loop = asyncio.get_event_loop()
        loop.create_task(console_input())
        bot.run(token)
    except discord.errors.LoginFailure:
        logger.error("Failed to login. Please check your token.")
    except Exception as e:
        logger.error(f"Unexpected error when starting bot: {e}")

if __name__ == "__main__":
    main()