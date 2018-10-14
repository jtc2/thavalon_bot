import copy 
import os 
import random 
import shutil
import sys 

# get_role_descriptions - this is called when information files are generated.
def get_role_description(role):
	return { 
		'Tristan'		: 'The person you see is also Good and is aware that you are Good.',
		'Iseult'		: 'The person you see is also Good and is aware that you are Good.',
		'Merlin' 		: 'You know which people have Evil roles, but not who has any specific role.',
		'Percival'		: 'You know which people have the Merlin or Morgana roles, but not specifically who has each.',
		'Lancelot'		: 'You may play Reversal cards while on missions.',
		'Guinevere'		: 'You see three connections between pairs of people. Two of those connections are true, and represent actual connections between Information roles. The other connection is false.',
		'Arthur'		: 'After you are on a mission that Fails, you may declare as Arthur, establishing that you are Good for the remainder of the game.\n Once you do this, you are no longer able to go on missions, but your voting power is doubled.',
		'Mordred' 		: 'You are hidden from all Good Information roles. \nLike other Evil characters, you know who else is Evil (except Colgrevance).',
		'Morgana'		: 'You appear like Merlin to Percival. \nLike other Evil characters, you know who else is Evil (except Colgrevance).',
		'Maelegant'		: 'You may play Reversal cards while on missions. \nLike other Evil characters, you know who else is Evil (except Colgrevance).',
		'Agravaine'		: 'You must play Fail cards while on missions. \nIf you are on a mission that Succeeds, you may declare as the Enforcer to cause it to Fail instead. \nLike other Evil characters, you know who else is Evil (except Colgrevance).',
		'Colgrevance' 	: 'You know not only who else is Evil, but what role each other Evil player possess. \nEvil players know that there is a Colgrevance, but do not know that it is you.', 
	}.get(role,'ERROR: No description available.')

# get_role_information: this is called to populate information files 
# blank roles:
# - Lancelot: no information
# - Arthur: no information?
# - Guinevere: too complicated to generate here
# - Colgrevance: name,role (evil has an update later to inform them about the presence of a Colgrevance)
def get_role_information(my_player,players):
	return { 
		'Tristan' 		: ['{} is Iseult.'.format(player.name) for player in players if player.role is 'Iseult'],
		'Iseult' 		: ['{} is Tristan.'.format(player.name) for player in players if player.role is 'Tristan'],
		'Merlin' 		: ['{} is Evil.'.format(player.name) for player in players if player.team is 'Evil' and player.role is not 'Mordred'],
		'Percival'		: ['{} is Merlin or Morgana.'.format(player.name) for player in players if player.role is 'Merlin' or player.role is 'Morgana'],
		'Lancelot'		: [],
		'Arthur'		: [],
		'Guinevere'		: [],
		'Mordred'	 	: ['{} is Evil.'.format(player.name) for player in players if player.team is 'Evil' and player is not my_player and player.role is not 'Colgrevance'],
		'Morgana' 		: ['{} is Evil.'.format(player.name) for player in players if player.team is 'Evil' and player is not my_player and player.role is not 'Colgrevance'],
		'Maelegant' 	: ['{} is Evil.'.format(player.name) for player in players if player.team is 'Evil' and player is not my_player and player.role is not 'Colgrevance'],
		'Agravaine'		: ['{} is Evil.'.format(player.name) for player in players if player.team is 'Evil' and player is not my_player and player.role is not 'Colgrevance'],
		'Colgrevance' 	: ['{} is {}'.format(player.name,player.role) for player in players if player.team is 'Evil' and player is not my_player],
	}.get(my_player.role,[])

def get_role_type(role):
	return { 
		'Tristan'		: 'Information',
		'Iseult'		: 'Information',
		'Merlin'		: 'Information',
		'Percival'		: 'Information',
		'Lancelot'		: 'Ability',
		'Arthur'		: 'Ability',
		'Guinevere'		: 'Information',
		'Mordred'		: 'Information',
		'Morgana'		: 'Information',
		'Maelegant'		: 'Ability',
		'Agravaine'		: 'Ability',
		'Colgrevance'	: 'Information',
	}.get(role,'Undefined')

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
		self.type = None 
		self.role = None 
		self.team = None 
		self.modifier = None 
		self.info = []

	def set_role(self, role):
		self.role = role
		self.type = get_role_type(role)

	def set_team(self, team):
		self.team = team

	def add_info(self,info):
		self.info += info

	def generate_info(self,players):
		pass

def main(): 
	if not (6 <= len(sys.argv) <= 11):
		print('ERROR: Invalid number of players.')
		exit(1)
	player_names = sys.argv[1:]
	num_players = len(player_names)
	player_names = list(set(sys.argv[1:])) # removes duplicates
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

	# establish available roles
	good_roles = ['Merlin','Percival','Lancelot','Tristan','Iseult']
	evil_roles = ['Mordred','Morgana','Maelegant']

	# roles added in larger games
	# arthur and guinevere on hold until mechanics devised
	if num_players > 6:
		# good_roles.append('Guinevere')
		# good_roles.append('Arthur')
		pass

	if num_players > 7:
		evil_roles.append('Agravaine')

	if num_players == 10:
		evil_roles.append('Colgrevance')

	good_roles_in_game = random.sample(good_roles,num_good)
	evil_roles_in_game = random.sample(evil_roles,num_evil)

	# remove lone lovers
	# this is temporarily suspended so that games of up to 8 can be played without runtime errors (due to lack of good roles implemented)
	'''
	if sum(gr in ['Tristan','Iseult'] for gr in good_roles_in_game) == 1: 
		available_roles = set(good_roles)-set(good_roles_in_game)-set(['Tristan','Iseult']) 
		if 'Tristan' in good_roles_in_game:
			good_roles_in_game.remove('Tristan') 
		if 'Iseult' in good_roles_in_game:
			good_roles_in_game.remove('Iseult') 
		good_roles_in_game.append(random.sample(set(available_roles),1)[0])
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

	for ep in evil_players: 
		new_role = evil_roles_in_game.pop()
		ep.set_role(new_role)
		ep.set_team('Evil')
		player_of_role[new_role] = ep

	for p in players:
		p.add_info(get_role_information(p,players))
		print(p.name,p.role,p.team,p.info)

	# Informing Evil about a Colgrevance
	for ep in evil_players:
		if ep.role is not 'Colgrevance' and player_of_role.get('Colgrevance'):
			ep.add_info(['Colgrevance lurks in the shadows'])

	bar = '----------------------------------------\n'
	for player in players: 
		print(bar+'You are '+player.role+' ['+player.team+' '+player.type+']\n'+bar+get_role_description(player.role)+'\n'+bar+'\n'.join(player.info)+'\n'+bar)

	print(player_of_role)

	
if __name__ == "__main__":
	main()
