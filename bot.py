# Work with Python 3.6
import discord
from thavalon import thavalon

TOKEN = 'NTAwNDY5MjczMDg5NjcxMTY4.DqLfOw.7PQdddUEZrs0A6E2bja_qQziB-0'

client = discord.Client()

@client.event
async def on_message(message):
    game_playing = False
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if message.content == '!hello':
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    if message.content == '!agravainemedaddy':
        msg = 'No {0.author.mention}'.format(message)
        await client.send_message(message.author, msg)

    if message.content == '!avalon':
        if game_playing:
            await client.send_message(message.channel, "Game in progress, type !stop to stop the game")
            return

        game_playing = True
        await client.send_message(message.channel, "Starting **THavalon - Discord Edition** in `#" + message.channel.name + "...")
        await thavalon(client, message)
        game_playing = False

    if message.content == "!alert":
        await client.send_message(message.channel, "alert.mp3")
        """
        channel = message.author.voice.voice_channel
        if channel is None:
            await client.send_message(message.channel, "You must be in a voice channel to use this command")
            return
        voice = await client.join_voice_channel(channel)
        player = await voice.create_ytdl_player('https://youtu.be/FTe7XaH_seo')
        player.start()
        voice.disconnect()
        """

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
