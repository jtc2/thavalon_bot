import copy
import os
import random
import shutil
import sys

# get_role_descriptions - this is called when information files are generated.
def get_role_description(role):
	return {
		'Tristan'		: 'You may have a Lover (who is also Good) this game, but you do not know who they are.\nYou and your Lover will be revealed to each other when you go on a mission together.\nBefore you have found your Lover, you will be told after each mission whether they were on that mission or not.',
		'Iseult'		: 'You may have a Lover (who is also Good) this game, but you do not know who they are.\nYou and your Lover will be revealed to each other when you go on a mission together.\nBefore you have found your Lover, you will be told after each mission whether they were on that mission or not.',
		'Merlin' 		: 'You know which people have Evil roles, but not who has any specific role.\nYou do not see Mordred or Morgana.',
		'Percival'		: 'You know which people are either the Assassination target or Morgana, but not specifically who has each.',
		'Lancelot'		: 'You may play Reversal cards while on missions.\nYou are immune to Assassination.',
		'Guinevere'		: 'During each mission for which you are not on the team, you may select one player on the mission team and see the card they played.',
		'Arthur'		: 'You know which Good roles are in the game, but not who has any given role.\nIf two missions have Failed, and less than two missions have Succeeded, you may declare as Arthur.\nAfter declaring, your vote on team proposals is counted twice, but you are unable to be on mission teams until the 5th mission.\nAfter declaring, you are immune to Assassination, as well as any effect that can forcibly change your vote.',
		'Titania'		: 'During each Voting phase, you know how all other players voted prior to submitting your own vote.',
		'Nimue'			: 'You know which Good and Evil roles are in the game, but not who has any given role.',
		'Galahad'		: 'Whenever you Approve (upvote) a mission that Succeeds or Reject (downvote) a mission that Fails, you gain one Virtue.\nOnce you have earned two Virtue, you gain the ability to play a Nullify card on a mission once per game.\nYou are immune to Assassination after you have played your Nullify card.\n(When played, a Nullify card reduces the effective number of Fails played on that mission by one.)',
		'Bedivere'		: 'Once per round (except the first), at any point during the Proposal or Voting phase, you may choose to immediately give a player a mission proposal by typing `!rally <name>`.\nAffected players are moved in the proposal order to their new position.\nOnce you have used this ability on a given player, you may not use it on them again for the rest of the game.',
		'Uther'			: 'Once per round (except the first), at any point during the Proposal or Voting phase, you may choose to immediately give a player a mission proposal by typing `!rally <name>`.\nAffected players are moved in the proposal order to their new position.\nOnce you have used this ability on a given player, you may not use it on them again for the rest of the game.',


		'Mordred' 		: 'Merlin does not know your identity. \nLike other Evil characters, you know who else is Evil (except Colgrevance).',
		'Morgana'		: 'You appear like Merlin to Percival and Merlin does not know your identity.\nLike other Evil characters, you know who else is Evil (except Colgrevance).',
		'Maelagant'		: 'You may play Reversal cards while on missions. \nYou know if there is a Lancelot in the game, but not who they are.\nLike other Evil characters, you know who else is Evil (except Colgrevance).',
		'Agravaine'		: 'You must play Fail cards while on missions. \nIf you are on a mission that Succeeds, you may declare as Agravaine to cause it to Fail instead. \nLike other Evil characters, you know who else is Evil (except Colgrevance).',
		'Colgrevance' 	: 'You know not only who else is Evil, but what role each other Evil player possess. \nEvil players know that there is a Colgrevance, but do not know that it is you.',
		'Oberon' 		: "Once per round (except the first), during a vote on a proposal, you can secretly change one other player's vote to a vote of your choice. (You may not use this ability after two missions have Failed.) \nLike other Evil characters, you know who else is Evil (except Colgrevance).",
		'Maeve' 		: "2/3/4 times per game, during a vote on a proposal, you can secretly choose to obscure how each player voted on the proposal and instead have only the amount of upvotes and downvotes presented. \nLike other Evil characters, you know who else is Evil (except Colgrevance).",
		'Balor'			: 'Once per round (except the first), at any point during the Proposal or Voting phase, you may prevent two players from being on proposals together by typing `!curse <name> <name>`.\nThis effect lasts until the end of the current round.\nOnce you have used this ability on a given player, you may not use it on them again for the rest of the game.\nThis ability cannot be used after two missions have Failed.',
	}.get(role,'ERROR: No description available.')

# get_role_information: this is called to populate information files
# blank roles:
# - Lancelot: no information
# - Arthur: no information?
# - Guinevere: too complicated to generate here
# - Colgrevance: name,role (evil has an update later to inform them about the presence of a Colgrevance)
def get_role_information(my_player,players):
	return {
		'Tristan' 		: [],
		'Iseult' 		: [],
		'Merlin' 		: ['{} is Evil.'.format(player.name) for player in players if (player.team is 'Evil' and (player.role is not 'Mordred') and (player.role is not 'Morgana'))],
		'Percival'		: [],
        'Lancelot'		: [],
		'Arthur'		: ['{}'.format(player.role) for player in players if player.team is 'Good' and player.role is not 'Arthur'],
		'Guinevere'		: [],
		'Titania'		: [],
		'Nimue'			: ['{}'.format(player.role) for player in players if player.role is not 'Nimue'],
		'Galahad'		: [],
		'Bedivere'		: [],

		'Mordred'	 	: ['{} is Evil.'.format(player.name) for player in players if player.team is 'Evil' and player is not my_player and player.role is not 'Colgrevance'],
		'Morgana' 		: ['{} is Evil.'.format(player.name) for player in players if player.team is 'Evil' and player is not my_player and player.role is not 'Colgrevance'],
		'Maelagant' 	: ['{} is Evil.'.format(player.name) for player in players if player.team is 'Evil' and player is not my_player and player.role is not 'Colgrevance'],
		'Agravaine'		: ['{} is Evil.'.format(player.name) for player in players if player.team is 'Evil' and player is not my_player and player.role is not 'Colgrevance'],
		'Colgrevance' 	: ['{} is {}'.format(player.name,player.role) for player in players if player.team is 'Evil' and player is not my_player],
		'Oberon'		: ['{} is Evil.'.format(player.name) for player in players if player.team is 'Evil' and player is not my_player and player.role is not 'Colgrevance'],
		'Maeve'			: ['{} is Evil.'.format(player.name) for player in players if player.team is 'Evil' and player is not my_player and player.role is not 'Colgrevance'],
		'Balor'			: ['{} is Evil.'.format(player.name) for player in players if player.team is 'Evil' and player is not my_player and player.role is not 'Colgrevance'],
	}.get(my_player.role,[])

class Player():
	# players have the following traits
	# name: the name of the player as fed into system arguments
	# role: the role the player possesses
	# team: whether hte player is good or evil
	# type: information or ability
	# seen: a list of what they will see
	# modifier: the random modifier this player has [NOT CURRENTLY UTILIZED]
	def __init__(self,name):
		self.name = name
		self.role = None
		self.team = None
		self.modifier = None
		self.info = []
		self.is_assassin = False

	def set_role(self, role):
		self.role = role

	def set_team(self, team):
		self.team = team

	def add_info(self,info):
		self.info += info

	def generate_info(self,players):
		pass

def get_player_info(player_names):
	num_players = len(player_names)
	if len(player_names) != num_players:
		print('ERROR: Duplicate player names.')
		exit(1)

	# create player objects
	players = []
	for i in range(0,len(player_names)):
		player = Player(player_names[i])
		players.append(player)

	# number of good and evil roles
	if num_players < 7:
		num_evil = 2
	elif num_players < 9:
		num_evil = 3
	else:
		num_evil = 4
	num_good = num_players - num_evil

	# roll a priority target 
	priority_targets = ['Merlin','Lovers'] 

	if num_players > 7: 
		priority_targets = ['Guinevere']

	priority_target = random.sample(priority_targets,1)[0]

	#print(priority_target)




	# establish available roles
	good_roles = ['Merlin','Percival','Tristan','Iseult','Lancelot']
	#good_roles = ['Tristan','Iseult']
	evil_roles = ['Mordred','Morgana','Maeve','Maelagant']

	# additional roles for player-count
	# 5/7 only 
	if num_players < 8: 
		good_roles.append('Nimue')
		#good_roles.append('Lancelot')
		#evil_roles.append('Maelagant')

	# 7 plus
	if num_players > 6:
		#good_roles.append('Bedivere')
		good_roles.append('Titania')
		evil_roles.append('Balor')
		evil_roles.append('Agravaine')
		#good_roles.append('Lancelot')
		#good_roles.append('Galahad')
		#evil_roles.append('Maelagant')

	# 8 plus 
	if num_players > 7:
		good_roles.append('Arthur')
		good_roles.append('Guinevere')
		evil_roles.append('Oberon')

	# 10 only
	if num_players == 10:
		evil_roles.append('Colgrevance')

	
	good_roles_in_game = []
	evil_roles_in_game = [] 

	#print(good_roles)
	#handle various priority targets
	if num_good > 3:

		if priority_target == 'Lovers': 
			good_roles_in_game.append('Tristan') 
			good_roles_in_game.append('Iseult')
			good_roles.remove('Tristan')
			good_roles.remove('Iseult')
			good_roles_in_game_more = random.sample(good_roles,num_good-2)
		else:
			good_roles_in_game.append(priority_target)
			#print(good_roles,priority_target)
			#print(priority_target in good_roles)
			good_roles.remove(priority_target)
			good_roles_in_game_more = random.sample(good_roles,num_good-1)

		good_roles_in_game.extend(good_roles_in_game_more)

	evil_roles_in_game = random.sample(evil_roles,num_evil)


	#code for testing role interaction

	if num_players == 2:
		priority_target = 'Merlin'
		good_roles_in_game = ['Merlin']
		evil_roles_in_game = ['Balor']
		num_good = 1
		num_evil = 1
	
	#good_roles_in_game = random.sample(good_roles,num_good)
	

	# lone lovers are rerolled
	# 50% chance to reroll lone lover
	# 50% chance to reroll another role into a lover
	'''
	if sum(gr in ['Tristan','Iseult'] for gr in good_roles_in_game) == 1 and num_good > 1 and num_players > 7:
		if 'Tristan' in good_roles_in_game:
				good_roles_in_game.remove('Tristan') 
		if 'Iseult' in good_roles_in_game:
				good_roles_in_game.remove('Iseult') 

		if random.choice([True, False]):
			# replacing the lone lover
			available_roles = set(good_roles)-set(good_roles_in_game)-set(['Tristan','Iseult'])
			good_roles_in_game.append(random.sample(set(available_roles),1)[0])
		else: 
			# upgrading to pair of lovers
			rerolled = random.choice(good_roles_in_game)
			good_roles_in_game.remove(rerolled)
			good_roles_in_game.append('Tristan')
			good_roles_in_game.append('Iseult')
	'''

	# roles after validation
	print(good_roles_in_game)
	print(evil_roles_in_game)

	# role assignment
	random.shuffle(players)

	good_players = players[:num_good]
	evil_players = players[num_good:]

	player_of_role = dict()

	for gp in good_players:
		new_role = good_roles_in_game.pop()
		gp.set_role(new_role)
		gp.set_team('Good')
		player_of_role[new_role] = gp

	# if there is at least one evil, first evil player becomes assassin
	if len(evil_players) > 0:
		evil_players[0].is_assassin = True

	for ep in evil_players:
		new_role = evil_roles_in_game.pop()
		ep.set_role(new_role)
		ep.set_team('Evil')
		player_of_role[new_role] = ep

	for p in players:
		p.add_info(get_role_information(p,players))
		random.shuffle(p.info)

	for gp in good_players:
	 	if gp.role is 'Percival': 
	 		percival_info = []
	 		if priority_target == 'Lovers': 
	 			percival_info.append('{} is an Assassination target (or Morgana).'.format(player_of_role.get('Tristan').name))
	 			percival_info.append('{} is an Assassination target (or Morgana).'.format(player_of_role.get('Iseult').name))
	 		else: 
	 			percival_info.append('{} is an Assassination target (or Morgana).'.format(player_of_role.get(priority_target).name))
	 		if player_of_role.get('Morgana'): 
	 			percival_info.append('{} is an Assassination target (or Morgana).'.format(player_of_role.get('Morgana').name))
	 		random.shuffle(percival_info)
	 		gp.add_info(percival_info)

	for ep in evil_players:
		# Informing Maelegant about a Lancelot
		if ep.role is 'Maelegant' and player_of_role.get('Lancelot'):
			ep.add_info(['There is a Lancelot in the game.'])
		elif ep.role is 'Maelegant' and not player_of_role.get('Lancelot'): 
			ep.add_info(['There is not a Lancelot in the game.'])
		# Informing Evil about a Colgrevance
		if ep.role is not 'Colgrevance' and player_of_role.get('Colgrevance'):
			ep.add_info(['Colgrevance lurks in the shadows. (There is another Evil that you do not see.)'])
		#if ep.role is not 'Colgrevance' and player_of_role.get('Titania'):
		#	ep.add_info(['Titania has infiltrated your ranks. (One of the people you see is not Evil.)'])

		# adding an assassin
		if ep.is_assassin:
			ep.add_info(['You are the Assassin. Your assassination target for this game is {}.'.format(priority_target)])

	bar = '----------------------------------------\n'
	for player in players:
		player.string = bar+'You are '+player.role+' ['+player.team+']\n'+bar+get_role_description(player.role)+'\n'+bar+'\n'.join(player.info)+'\n'+bar
		print(player.name,player.role,player.team,player.info)

	return player_of_role, priority_target


if __name__ == "__main__":
	#get_player_info(['A','B','C','D','E','F','G'])
	main()
