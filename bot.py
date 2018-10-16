# Work with Python 3.6
import discord
from thavalon import THavalon
from tokens import TOKEN

client = discord.Client()
game = THavalon(client)

@client.event
async def on_message(message):
    if not message.content.startswith("!"):
        return

    if message.content == "!newgame" and "admin" in [role.name for role in message.author.roles]:
        await client.send_message(message.channel, "Starting new game!")
        global game
        game = THavalon(client)
        return

    if message.channel.is_private:
        await game.handle_private_message(message)
    else:
        await game.handle_public_message(message)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
