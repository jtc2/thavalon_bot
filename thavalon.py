import random

MAX_NUM_PLAYERS = 10
MIN_NUM_PLAYERS = 5


async def thavalon(client, message):
    # setup and play game
    name_to_player = {}
    started = await join_game(client, message, name_to_player)
    if not started:
        await client.send_message(message.channel, "Game stopped")
        return

    # TODO: Send role info

    # at this point, game has been started
    await client.send_message(message.channel, "Creating game! Check your messages for role info.")

    # and actually play the game
    await play_game(client, message, name_to_player)

    # finally, print game info
    # TODO: Implement


async def join_game(client, message, name_to_player):
    await client.send_message(message.channel,
                              "A new game has been started. Commands:\n" \
                              "\t!join to join the game\n" \
                              "\t!players to view current players\n"  \
                              "\t!start to begin game\n" \
                              "\t!stop to stop game\n")
    started = False
    while not started:
        reply = await client.wait_for_message(channel=message.channel)
        if reply.content == "!join":
            # check number of players
            if len(name_to_player) >= MAX_NUM_PLAYERS:
                await client.send_message(message.channel, "Game already has {} players, unable to add more".format(MAX_NUM_PLAYERS))
                continue

            # check is new player
            if reply.author.display_name in name_to_player:
                await client.send_message(message.channel, "{} is already in the game!".format(reply.author.display_name))
                continue

            # add new player
            name_to_player[reply.author.display_name] = reply.author
            await client.send_message(message.channel, "{} has joined the game!".format(reply.author.display_name))
        elif reply.content == "!players":
            players_string = "Players in game:\n"
            players_string += "\n".join(["\t{}".format(name) for name in name_to_player])
            await client.send_message(message.channel, players_string)
        elif reply.content == "!start":
            # check number of players
            if len(name_to_player) < MIN_NUM_PLAYERS:
                await client.send_message(message.channel, "Need at least {} players to play".format(MIN_NUM_PLAYERS))
                continue

            # start game if possible
            started = True
            break
        elif reply.content == "!stop":
            break
        elif reply.content == "!test":
            for i in range(5):
                name_to_player["bot{}".format(i)] = "bot{}".format(i)
    return started


async def play_game(client, message, name_to_player):
    player_order = random.shuffle(list(name_to_player.keys()))



    finished = False
    while not finished:
        reply = await client.wait_for_message(channel=message.channel)
        if reply.content == "!stop":
            break