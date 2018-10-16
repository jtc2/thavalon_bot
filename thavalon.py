import discord
import random
from player_info import get_player_info

MAX_NUM_PLAYERS = 10
MIN_NUM_PLAYERS = 5
num_players_to_mission = {
    1: [1, 1, 1, 1, 1],
    2: [1, 1, 2, 1, 2],
    3: [2, 2, 2, 2, 2],
    4: [2, 2, 2, 2, 2],
    5: [2, 3, 2, 3, 3],
    6: [2, 3, 4, 3, 4],
    7: [2, 3, 3, 4, 4],
    8: [3, 4, 4, 5, 5],
    9: [3, 4, 4, 5, 5],
    10: [3, 4, 4, 5, 5],
}
num_players_to_num_proposals = {
    1: 2,
    2: 2,
    3: 2,
    4: 2,
    5: 3,
    6: 3,
    7: 4,
    8: 4,
    9: 4,
    10: 5,
}


class THavalon:
    def __init__(self, client):
        self.client = client
        self.name_to_player = {}
        self.player_to_name = {}
        self.order = []
        self.proposer_idx = -2
        self.num_players = 0
        self.mission_num = 0  # 0 indexed
        self.game_running = False
        self.game_state = "CREATE"  # can be either CREATE, PROPOSE, VOTE or PLAY
        self.name_to_info = {}
        self.num_passes = 0
        self.num_failures = 0
        self.game_over = False
        # handle mission 1 proposals separately
        self.first_proposal = []
        self.second_proposal = []
        # handle other proposals
        self.current_proposal = []
        self.num_proposals = 0
        # for mission results
        self.name_to_vote = {}
        # for playing mission
        self.going_proposal = []
        self.num_success = 0
        self.num_fail = 0
        self.num_reverse = 0
        self.num_qb = 0
        self.name_to_play = {}
        self.guin_examinee = None
        self.bewitch_target = ""
        self.bewitch_vote = False
        self.can_bewitch = True

    async def handle_public_message(self, message):
        # handle general messages that can be done anytime
        if message.content == '!agravainemedaddy':
            await self.client.send_message(message.author, "No {0.author.mention}".format(message))
            return
        elif message.content == "!cookiejar":
            await self.client.send_message(message.channel, "The cookie jar is over there Meg.")
            return

        if not self.game_running:
            if message.content == "!thavalon":
                em = discord.Embed(description="A new game has been started!", colour=discord.Color.dark_blue())
                em.add_field(name="!join", value="Join the game", inline=False)
                em.add_field(name="!players", value="List the players who have joined so far", inline=False)
                em.add_field(name="!start", value="Start the game", inline=False)
                await self.client.send_message(message.channel, embed=em)

                self.game_running = True
            else:
                await self.client.send_message(message.channel, "No game running, type !thavalon to start a game")
            return

        if self.game_running:
            if message.content == "!thavalon":
                await self.client.send_message(message.channel, "Game in progress. Type !stop to stop game.")
            elif message.content == "!order" and self.game_state != "CREATE":
                await self.client.send_message(message.channel, "See pinned messages for order.")
            elif self.game_state == "CREATE":
                await self.handle_create_message(message)
            elif self.game_state == "PROPOSE":
                await self.handle_propose_message(message)

    async def handle_private_message(self, message):
        print("MESSAGE RECEIVED: {} from {} in state {}".format(message.content, message.author, self.game_state))
        if self.game_state == "VOTE":
            await self.handle_received_vote(message)
        elif self.game_state == "PLAY":
            await self.handle_received_play(message)

    # handle messages related to game creation
    async def handle_create_message(self, message):
        self.public_channel = message.channel
        if message.content == "!join":
            # check number of players
            if len(self.name_to_player) >= MAX_NUM_PLAYERS:
                await self.client.send_message(message.channel,
                                               "Game already has {} players, unable to add more".format(MAX_NUM_PLAYERS))
                return

            # check is new player
            if message.author.display_name in self.name_to_player:
                await self.client.send_message(message.channel,
                                               embed=discord.Embed(description="{} is already in the game"
                                                                               .format(message.author.display_name),
                                                                   colour=discord.Color.dark_blue()))
                return

            # add new player
            # name_to_player[reply.author.display_name + str(len(name_to_player))] = reply.author
            self.name_to_player[message.author.display_name] = message.author
            self.player_to_name[message.author] = message.author.display_name
            await self.client.send_message(message.channel,
                                           embed=discord.Embed(description="{} has joined the game!"
                                                                           .format(message.author.display_name),
                                                               colour=discord.Color.dark_blue()))
        elif message.content == "!start":
            # check number of players
            if len(self.name_to_player) < 1: # MIN_NUM_PLAYERS:
                await self.client.send_message(message.channel,
                                               discord.Embed(description="Need at least {} players to play"
                                                                         .format(MIN_NUM_PLAYERS),
                                                             colour=discord.Color.dark_blue()))
                return

            # start game if possible
            self.game_state = "PROPOSE"
            self.mission_num = 0

            # clear all previous pins
            pins = await self.client.pins_from(self.public_channel)
            for pin in pins:
                await self.client.unpin_message(pin)

            # update order
            self.order = list(self.name_to_player.keys())
            random.shuffle(self.order)
            order_string = "Player Order:\n{}".format("".join(["\t\t{}) {}\n".format(idx + 1, name) for idx, name in enumerate(self.order)]))
            order_msg = await self.client.send_message(self.public_channel,
                                                       embed=discord.Embed(description=order_string,
                                                                           colour=discord.Color.dark_blue()))
            await self.client.pin_message(order_msg)

            # TODO :remove
            if len(self.order) == 1:
                self.order.append(self.order[0])

            order_string = "Proposal Order:\n"
            order_string += "\n".join(["\t\t{}".format(name) for name in self.order])
            order_pin = await self.client.send_message(self.public_channel,order_string) 
            await self.client.pin_message(order_pin)


            await self.assign_player_info()
            await self.print_game_start_info(message)
            
            
        elif message.content == "!players":
            players_string = "Players in game:\n"
            players_string += "\n".join(["\t{}".format(name) for name in self.name_to_player])
            await self.client.send_message(message.channel, players_string)

    async def assign_player_info(self):
        self.role_to_player = get_player_info(self.order)
        for _, player_info in self.role_to_player.items():
            player = self.name_to_player[player_info.name]
            self.name_to_info[player_info.name] = player_info
            await self.client.send_message(player, player_info.string)

    async def print_game_start_info(self, message):
        game_beginning_message = "The game has begun. Please check your messages for your role info.\n" \
                                "Check pinned messages for player order.\n" \
                                 "Type !order to see the proposal order.\n\n" \
                                 "{} and {} will be proposing teams for the first mission.\n" \
                                 "{}, please make your proposal." \
                                 .format(self.order[-2], self.order[-1], self.order[-2])
        await self.client.send_message(message.channel, game_beginning_message)

    # handle messages during PROPOSE state
    async def handle_propose_message(self, message):
        print("GOT PROPOSAL: {}".format(message.content))
        if message.content.startswith("!propose") and \
           message.author.display_name == self.order[self.proposer_idx]:
            num_on_mission = num_players_to_mission[len(self.order)][self.mission_num]
            proposed_str = message.content.replace("!propose ", "")
            proposed_names = proposed_str.split(" ")
            if len(proposed_names) != num_on_mission:
                await self.client.send_message(message.channel, "Proposal must have exactly {} players. Propose again.".format(num_on_mission))
                return
            for name in proposed_names:
                if name not in self.name_to_player:
                    await self.client.send_message(message.channel, "Invalid players - all players must be in game. Propose again.")
                    return
            if self.proposer_idx == -2:
                # if first proposal
                self.first_proposal = proposed_names
                await self.client.send_message(message.channel,
                                               "{} has proposed:\n{}\n{}, make your proposal."
                                               .format(self.order[-2],
                                                       "".join("\t\t{}\n".format(name) for name in self.first_proposal),
                                                       self.order[-1])
                                               )
                self.proposer_idx = -1
            elif self.proposer_idx == -1:
                self.second_proposal = proposed_names
                await self.client.send_message(message.channel,
                                               "{} has proposed:\n{}\n\nCheck your messages to vote."
                                               .format(self.order[-1],
                                                       "".join("\t\t{}\n".format(name) for name in self.second_proposal),
                                                       )
                                               )
                # don't update proposer idx - it updates after round played
                self.game_state = "VOTE"
                await self.send_vote_requests(message, await self.get_first_mission_vote_string())
            else:  # not in mission 1
                self.current_proposal = proposed_names
                if self.num_proposals == num_players_to_num_proposals[len(self.order)]:
                    # last proposal
                    self.going_proposal = self.current_proposal
                    await self.client.send_message(message.channel,
                                                   "{} has proposed:\n{}\n"
                                                   "This is the final mission of the round, it must go.\n"
                                                   "If you are on the mission, check your messages to play a card.\n"
                                                   .format(self.order[self.proposer_idx],
                                                           "".join("\t\t{}\n".format(name) for name in self.current_proposal),
                                                           ))
                    self.game_state = "PLAY"
                    await self.send_play_requests()
                else:
                    await self.client.send_message(message.channel,
                                               "{} has proposed:\n{}\n\nCheck your messages to vote."
                                               .format(self.order[self.proposer_idx],
                                                       "".join("\t\t{}\n".format(name) for name in self.current_proposal),
                                                       ))
                    self.game_state = "VOTE"
                    await self.send_vote_requests(message, await self.get_mission_vote_string())

    async def get_mission_vote_string(self):
        return "You are voting whether to send {}'s proposal of:\n{}\n" \
               "Type !upvote to approve it.\n" \
               "Type !downvote to reject it.\n" \
               .format(self.order[self.proposer_idx], "".join("\t\t{}\n".format(name) for name in self.current_proposal))

    async def get_first_mission_vote_string(self):
        return "You are voting for which mission 1 proposal to send.\n\n" \
               "Type !upvote to vote for {}'s proposal:\n\t\t{}.\n" \
               "Type !downvote to vote for {}'s proposal of:\n\t\t{}.\n" \
               .format(self.order[-2], ", ".join(self.first_proposal), self.order[-1], ", ".join(self.second_proposal))

    async def send_vote_requests(self, message, request_string):
        for player in self.player_to_name:
            await self.client.send_message(player, request_string)
            if self.name_to_info[self.player_to_name[player]].role == "Oberon" and self.mission_num > 0:
                bewitch_msg = "\nYou may bewitch someone once per round by typing `!bewitch <name> <upvote/downvote>` prior to submitting your own vote. This will cause them to vote as you chose for the current proposal."
                await self.client.send_message(player,bewitch_msg)


    async def handle_received_vote(self, message):
        if message.author not in self.player_to_name:
            return

        if message.author.display_name in self.name_to_vote:
            await self.client.send_message(message.author, "You already voted, unable to change vote")
            return
        elif message.content == "!upvote":
            self.name_to_vote[self.player_to_name[message.author]] = True
            await self.client.send_message(message.author, "You upvoted.")
        elif message.content == "!downvote":
            self.name_to_vote[self.player_to_name[message.author]] = False
            await self.client.send_message(message.author, "You downvoted.")
        elif message.content.startswith("!bewitch") and self.name_to_info[self.player_to_name[message.author]].role == "Oberon":
            if self.mission_num == 0: 
                await self.client.send_message(message.author, "You may not bewitch someone on the first mission. Please submit your vote.")
            elif not self.can_bewitch: 
                await self.client.send_message(message.author, "You have already bewitched someone this round. Please submit your vote.")
            else:
                bewitch_parse = message.content.replace("!bewitch ", "").split(" ")
                self.bewitch_target = bewitch_parse[0]
                bewitch_vote_str = bewitch_parse[1]
                if self.bewitch_target not in self.name_to_player:
                    self.bewitch_target = ""
                    bewitch_vote_str = ""
                    await self.client.send_message(message.author, "The targeted player is not in the game. Please try again.")
                elif bewitch_vote_str != "upvote" and bewitch_vote_str != "downvote":
                    self.bewitch_target = ""
                    bewitch_vote_str = ""
                    await self.client.send_message(message.author, "The selected vote is not valid. The options are 'upvote' and 'downvote'. Please try again.")
                else:
                    if bewitch_vote_str == "upvote":
                        self.bewitch_vote = True
                    else: 
                        self.bewitch_vote = False
                    self.can_bewitch = False
                    await self.client.send_message(message.author, "You have bewitched {} to {} this proposal.\nPlease submit your own vote now.".format(self.bewitch_target,("upvote" if self.bewitch_vote else "downvote")))
        else:
            await self.client.send_message(message.author, "Invalid vote, please vote again.")

        if len(self.name_to_vote) == len(self.order):
            if self.bewitch_target:
                old_vote = self.name_to_vote[self.bewitch_target]
                if self.bewitch_vote != old_vote:
                    self.name_to_vote[self.bewitch_target] = self.bewitch_vote
                    await self.client.send_message(self.name_to_player[self.bewitch_target],"Oberon has changed your vote to {}.".format("**upvote**" if self.bewitch_vote else "**downvote**"))
            self.bewitch_target = ""
            self.bewitch_vote = False
            print("VOTES ARE IN: {}".format(self.name_to_vote))
            await self.determine_vote_result()

    async def determine_vote_result(self):
        accepters = []
        rejecters = []
        for name, vote in self.name_to_vote.items():
            if vote:
                accepters.append(name)
            else:
                rejecters.append(name)
        vote_result_string = "The votes are in!\n" \
                             "Upvote:\n{}" \
                             "Downvote:\n{}" \
                             .format("".join("\t\t{}\n".format(name) for name in accepters),
                                     "".join("\t\t{}\n".format(name) for name in rejecters))
        # reset voters
        self.name_to_vote = {}

        mission_going_string = "\n\n{} are going on the mission! Check your messages to vote"
        if self.mission_num == 0:
            # handle first mission
            if len(accepters) > len(rejecters):
                self.going_proposal = self.first_proposal
                vote_result_string += mission_going_string.format(", ".join(self.first_proposal))
            else:
                self.going_proposal = self.second_proposal
                vote_result_string += mission_going_string.format(", ".join(self.second_proposal))
            self.game_state = "PLAY"

            await self.client.send_message(self.public_channel, vote_result_string)
            await self.send_play_requests()
        else:
            # all other missions
            if len(accepters) > len(rejecters):
                self.going_proposal = self.current_proposal
                vote_result_string += "The mission is approved!\n"
                vote_result_string += mission_going_string.format(", ".join(self.going_proposal))
                self.game_state = "PLAY"

                await self.client.send_message(self.public_channel, vote_result_string)
                await self.send_play_requests()
            else:
                vote_result_string += "The mission is rejected.\n\n"
                self.game_state = "PROPOSE"
                self.proposer_idx = (self.proposer_idx + 1) % len(self.order)
                self.current_proposal = []
                self.num_proposals += 1
                vote_result_string += "{}, please propose a {} player mission. This is proposal {} of {}." \
                                      .format(self.order[self.proposer_idx],
                                              num_players_to_mission[len(self.order)][self.mission_num],
                                              self.num_proposals,
                                              num_players_to_num_proposals[len(self.order)])
                await self.client.send_message(self.public_channel, vote_result_string)

    async def send_play_requests(self):
        print("SENDING PLAY REQUESTS TO: {}".format(self.going_proposal))
        for name in self.going_proposal:
            await self.client.send_message(self.name_to_player[name],
                                           "You are going on a mission! Type !success, !reverse, or !fail to play a card.")
        if 'Guinevere' in self.role_to_player and self.role_to_player['Guinevere'].name not in self.going_proposal:
            await self.send_guinevere_ability_request()

    async def send_guinevere_ability_request(self):
        guin_name = self.role_to_player['Guinevere'].name
        await self.client.send_message(self.name_to_player[guin_name],
                                       "You have the ability to view one played card on the current mission of:\n{}.\n"
                                       "To choose which player, type \"!examine <name>\" where <name> is the player's name.\n"
                                       "You can choose to examine no one by typing \"!decline\".\n"
                                       .format("".join("\t\t{}\n".format(name) for name in self.going_proposal)))

    async def handle_received_play(self, message):
        name = self.player_to_name[message.author]
        print("GOING PROPOSAL: {}".format(self.going_proposal))
        print("NAME: {}".format(name))
        print("{} has sent {}".format(name, message.content))
        print()

        # check guinevere
        if 'Guinevere' in self.role_to_player and self.guin_examinee is None:
            guin_name = self.role_to_player['Guinevere'].name
            if guin_name == name and message.content == "!decline":
                await self.client.send_message(message.author, "You have chosen to examine no one.")
                self.guin_examinee = "none"
            elif guin_name == name and message.content.startswith("!examine "):
                examinee_name = message.content.replace("!examine ", "")
                print("EXAMINEE: {}".format(examinee_name))
                if examinee_name not in self.going_proposal:
                    await self.client.send_message(message.author, "Invalid player to examine, try again.")
                    return
                await self.client.send_message(message.author, "You have chosen to examine {}".format(examinee_name))
                self.guin_examinee = examinee_name
            await self.check_mission_end()

        if name not in self.going_proposal:
            return
        if name in self.name_to_play:
            await self.client.send_message(message.author, "You have already voted.")
            return
        elif message.content == "!success":
            if self.name_to_info[name].role == "Agravaine":
                await self.client.send_message(message.author, "Agravaine must play fails.")
                return
            self.num_success += 1
            await self.client.send_message(message.author, "You have played a success!")
        elif message.content == "!fail":
            if self.name_to_info[name].team == "Good":
                await self.client.send_message(message.author, "You can not play fails, try again.")
                return
            self.num_fail += 1
            await self.client.send_message(message.author, "You have played a fail!")
        elif message.content == "!reverse":
            if self.name_to_info[name].role != "Lancelot" and self.name_to_info[name].role != "Maelegant":
                await self.client.send_message(message.author, "You can not play reverse, try again.")
                return
            self.num_reverse += 1
            await self.client.send_message(message.author, "You have played a reverse!")
        elif message.content == "!qb":
            self.num_qb += 1
            await self.client.send_message(message.author, ":heart: but you still need to vote.")
            return
        else:
            await self.client.send_message(message.author, "Invalid play, try again.")
            return

        self.name_to_play[name] = message.content

        await self.check_mission_end()

    async def check_mission_end(self):
        if len(self.name_to_play) == len(self.going_proposal):
            if 'Guinevere' in self.role_to_player and self.role_to_player['Guinevere'].name not in self.going_proposal and self.guin_examinee is None:
                return
            print("NAME TO PLAY: {}".format(self.name_to_play))
            print("S: {}, F: {}, R: {}, QB: {}".format(self.num_success, self.num_fail, self.num_reverse, self.num_qb))
            if self.guin_examinee and self.guin_examinee != "none":
                await self.inform_guinevere()
            await self.show_played_mission()

    async def inform_guinevere(self):
        guin_player = self.name_to_player[self.role_to_player['Guinevere'].name]
        await self.client.send_message(guin_player,
                                       "{} played {}".format(self.guin_examinee,
                                                             self.name_to_play[self.guin_examinee].replace("!", "")))

    async def show_played_mission(self):
        result_str = "The following team went on a mission:\n{}\nThe cards played were:\n".format("".join("\t\t{}\n".format(name) for name in self.going_proposal))

        cards = []
        for i in range(self.num_fail):
            cards.append("Fail")
        for i in range(self.num_success):
            cards.append("Success")
        for i in range(self.num_reverse):
            cards.append("Reverse")
        for i in range(self.num_qb):
            cards.append("QUESTING BEAST WAS HERE :heart:")

        result = True
        self.saved_reverse = self.num_reverse
        self.num_reverse = self.num_reverse % 2
        if self.mission_num != 3 or len(self.order) < 7:
            if self.num_fail > 0 and self.num_reverse == 0:
                result = False
            if self.num_fail == 0 and self.num_reverse == 1:
                result = False
        elif self.mission_num == 3 and len(self.order) >= 7:
            if self.num_fail >= 2 and self.num_reverse == 0:
                result = False
            if self.num_fail == 1 and self.num_reverse == 1:
                result = False

        random.shuffle(cards)
        for card in cards:
            result_str += "\t\t{}\n".format(card)

        await self.client.send_message(self.public_channel, result_str)

        def agravaine_check(message):
            if message.content != "!declare":
                return False
            if self.name_to_info[message.author.display_name].role != "Agravaine":
                return False
            return True

        if "Agravaine" in self.role_to_player and result and self.num_fail > 0:
            await self.client.send_message(self.public_channel, "If you are Agravaine and would like to declare, type !declare in chat. You have 10 seconds.")
            message = await self.client.wait_for_message(timeout=10, channel=self.public_channel, check=agravaine_check)
            if message is None:
                await self.client.send_message(self.public_channel, "No Agravaine has declared.")
            else:
                await self.client.send_message(self.public_channel, "{} has declared as Agravaine!".format(message.author.display_name))
                result = False

        result_str = "The result of this mission is {}.\n\n".format("PASS" if result else "FAIL")
        await self.client.send_message(self.public_channel, result_str)

        mission_pin = "Mission {}: {}\n\t{}\n\tSuccess: {}, Fail: {}, Reverse: {}".format(str(int(self.mission_num)+1),"PASS" if result else "FAIL","".join("{} ".format(name) for name in self.going_proposal),self.num_success,self.num_fail,self.saved_reverse)
        mission_pin_msg = await self.client.send_message(self.public_channel,mission_pin)

        await self.client.pin_message(mission_pin_msg)
        
        if result:
            self.num_passes += 1
        else:
            self.num_failures += 1

        if self.num_passes == 3:
            await self.client.send_message(self.public_channel, "The game has ended! The \"Good\" team has won!")
            self.game_running = False
            return
        if self.num_failures == 3:
            await self.client.send_message(self.public_channel, "The game has ended! The \"Evil\" team has won!")
            self.game_running = False
            return


        # reset stuff
        self.going_proposal = []
        self.num_fail = 0
        self.num_success = 0
        self.num_reverse = 0
        self.num_qb = 0
        self.name_to_play = {}
        self.mission_num += 1
        self.proposer_idx = (self.proposer_idx + 1) % len(self.order)
        self.current_proposal = []
        self.num_proposals = 1
        self.guin_examinee = None
        self.can_bewitch = True

        # send message starting next round
        if self.mission_num == 5:
            await self.client.send_message(self.public_channel, "The game has ended. Questing beast wins!")
            self.game_running = False
            return
        self.game_state = "PROPOSE"
        await self.client.send_message(self.public_channel,
                                 "Mission {} has {} players.\n{} is proposing first.\nThere are {} proposals this round."
                                 .format(self.mission_num + 1,
                                         num_players_to_mission[len(self.order)][self.mission_num],
                                         self.order[self.proposer_idx],
                                         num_players_to_num_proposals[len(self.order)]))
