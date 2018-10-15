# Work with Python 3.6
import discord
from thavalon import THavalon

TOKEN = ''

client = discord.Client()
game = THavalon(client)

@client.event
async def on_message(message):
    if not message.content.startswith("!"):
        return

    if message.content == "!newgame" and "@admin" in [role.name for role in message.author.roles]:
        client.send_message(message.channel, "Starting new game!")
        global game
        game = THavalon(client)
        return

    if message.channel.is_private:
        await game.handle_private_message(message)
    else:
        await game.handle_public_message(message)
    # game_playing = False
    # # we do not want the bot to reply to itself
    # if message.author == client.user:
    #     return
    # if message.content == '!hello':
    #     msg = 'Hello {0.author.mention}'.format(message)
    #     await client.send_message(message.channel, msg)
    #
    # if message.content == '!agravainemedaddy':
    #     msg = 'No {0.author.mention}'.format(message)
    #     await client.send_message(message.author, msg)
    #
    # if message.content == '!avalon':
    #     if game_playing:
    #         await client.send_message(message.channel, "Game in progress, type !stop to stop the game")
    #         return
    #
    #     game_playing = True
    #     await client.send_message(message.channel, "Starting **THavalon - Discord Edition** in `#" + message.channel.name + "...")
    #     await thavalon(client, message)
    #     game_playing = False
    #
    # if message.content.startswith("!help"):
    #     help_command = message.content.replace("!help ", "")
    #     if help_command == "":
    #         await client.send_message(message.channel, "Help topics: propose, vote, play, declare")
    #     elif help_command == "propose":
    #         await client.send_message(message.channel,
    #                                   "To propose, please type \"!propose <player1> <player2> ...\""
    #                                   ", using the names of the actual players.\n"
    #                                   "**IMPORTANT:** This must exactly match the discord display name of "
    #                                   "the player, and all names must be separated by a single space.")
    #     else:
    #         await client.send_message(message.channel, "Invalid help command. Type !help to see options.")
    #
    # if message.content == "!alert":
    #     await client.send_message(message.channel, "alert.mp3")
    #     """
    #     channel = message.author.voice.voice_channel
    #     if channel is None:
    #         await client.send_message(message.channel, "You must be in a voice channel to use this command")
    #         return
    #     voice = await client.join_voice_channel(channel)
    #     player = await voice.create_ytdl_player('https://youtu.be/FTe7XaH_seo')
    #     player.start()
    #     voice.disconnect()
    #     """

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
