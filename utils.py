from google.appengine.ext import ndb
from models import Game, Player
import random
import logging

# ==============GLOBAL DICs==================

emo1 = u"\U00000031\U0000FE0F\U000020E3"
emo2 = u"\U00000032\U0000FE0F\U000020E3"
emo3 = u"\U00000033\U0000FE0F\U000020E3"
emo4 = u"\U00000034\U0000FE0F\U000020E3"
emo5 = u"\U00000035\U0000FE0F\U000020E3"

emoman = u"\U0001F464"

emotick = u"\U00002705"
emocross = u"\U0000274C"

identityDictRS = {1:(1,0), 2:(1,1), 3:(2,1), 4:(3,1), 5:(3,2), 6:(4,2), 7:(4,3), 8:(5,3), 9:(6,3), 10:(6,4)}
missionDict = {1:(0,1,1,1,1,1), 2:(0,2,2,2,2,2), 3:(0,2,2,2,2,3), 4:(0,2,2,2,3,3), 5:(0,2,3,2,3,3), 6:(0,2,3,3,3,4), 7:(0,2,3,3,4,4), 8:(0,3,4,4,5,5), 9:(0,3,4,4,5,5), 10:(0,3,3,4,4,5)}
num_for_msn = {1:(0,emo1,emo1,emo1,emo1,emo1), 2:(0,emo2,emo2,emo2,emo2,emo2), 3:(0,emo2,emo2,emo2,emo2,emo3), 4:(0,emo2,emo2,emo2,emo3,emo3), 5:(0,emo2,emo3,emo2,emo3,emo3), 6:(0,emo2,emo3,emo3,emo3,emo4), 7:(0,emo2,emo3,emo3,emo4,emo4), 8:(0,emo3,emo4,emo4,emo5,emo5), 9:(0,emo3,emo4,emo4,emo5,emo5), 10:(0,emo3,emo3,emo4,emo4,emo5)}



def get_curr_game(chat_id):
	""" return current game (entity) corresponding to chat_id"""
	curr_game = ndb.Key('Game', str(chat_id)).get()
	return curr_game

def get_player(chat_id):
	player = ndb.Key('Player', str(chat_id)).get()
	return player

def get_curr_player_list(chat_id):
	""" a list of current players (entity)"""
	player_list = []
	players = Player.query(Player.parent_chat_id == chat_id).fetch()
	for player in players: 
		player_list.append(player)
	return player_list

def get_curr_player_slashnamelist(chat_id):
	""" a list of current players (entity)"""
	player_list = []
	players = Player.query(Player.parent_chat_id == chat_id).fetch()
	for player in players: 
		player_list.append(["/" + player.name])
	return player_list

def get_spy_namelist(chat_id):
	spy_namelist = []
	players = Player.query(Player.parent_chat_id == chat_id).fetch()
	for player in players:
		if player.role == 'spy':
			spy_namelist.append(player.name)
	return spy_namelist
def get_spy_list(chat_id):
	spy_list = []
	players = Player.query(Player.parent_chat_id == chat_id).fetch()
	for player in players:
		if player.role == 'spy':
			spy_list.append(player)
	return spy_list

def get_resistance_list(chat_id):
	resistance_list = []
	players = Player.query(Player.parent_chat_id == chat_id).fetch()
	for player in players:
		if player.role == 'resistance':
			resistance_list.append(player)
	return resistance_list

def clear_identities(chat_id):
	players = get_curr_player_list(chat_id)
	for player in players:
		player.role = 'None'
		player.put()
	return

def no_ready(chat_id):
	players = get_curr_player_list(chat_id)
	no_ready_list = []
	for player in players:
		if main.getEnabled(player.user_id) == False:
			no_ready_list.append[player]
	return no_ready_list

def put_new_player (chat_id, fr_user_id, fr_user_name):
	"""add in this new player and return its key"""
	"""increment in num_player"""
	curr_game = get_curr_game(chat_id)
	existing_player = get_player(fr_user_id)
	if existing_player == None:
		new_player = Player(parent_chat_id = chat_id, id = str(fr_user_id), name = fr_user_name)
		new_player.put()
		curr_game = increment_game_num_player(chat_id)
	return curr_game

def remove_player(chat_id, fr_user_id):
	curr_game = get_curr_game(chat_id)
	existing_player = get_player(fr_user_id)
	if existing_player:
		existing_player.key.delete()
		curr_game = decrement_game_num_player(chat_id)
	return curr_game

def assign_role (chat_id):
	"""after player_addition phase, roles/leaders are assigned"""
	curr_game = get_curr_game(chat_id)
	numSpies = identityDictRS[curr_game.num_player][1]
	player_list = get_curr_player_list(chat_id)
	spies_list = random.sample(player_list, numSpies)
	for spy in spies_list:
		spy.role = 'spy'
		spy.put()
	return 

def get_game_state(chat_id):
	curr_game = get_curr_game(chat_id)
	return curr_game.state


def get_role_dict(chat_id):
	"""return a dictionary. format - {user_name: role_name}"""
	role_dict = {}
	curr_game = get_curr_game(chat_id)
	player_list = get_curr_player_list(chat_id)
	for player in player_list:
		if player.role == 'spy':
			role_dict[player.name] = 'spy'
		else:
			role_dict[player.name] = 'resistance'
	return role_dict

def player_selected(chat_id, text):
	"""return a player ENTITY(get or fetch from database)that is selected/queried by user name(indicated by text)"""
	curr_game = get_curr_game(chat_id)
	player_list = get_curr_player_list(chat_id)
	for player in player_list:
		if player.name == text: #need to check if it's player.name or player.user_id    ## i checked liao but thanks!
			return player
	return None #just in case no matches.

def mission_full(chat_id):
	"""return a boolean: query the database for ppl on the mission & check with mission dict."""
	"""return True if got enough number of ppl to go on mission for the current rd"""
	curr_game = get_curr_game(chat_id)
	full_count = missionDict[curr_game.num_player][curr_game.mission_num]
	player_list = get_curr_player_list(chat_id)
	count = 0
	for player in player_list:
		if player.on_mission == True:
			count += 1
	if count == full_count:
		return True
	return False

def get_mission_namelist(chat_id):
	"""return a NAME LIST of players who are on a mission now"""
	curr_game = get_curr_game(chat_id)
	player_list = get_curr_player_list(chat_id)
	name_list = []
	for player in player_list:
		if player.on_mission == True:
			name_list += [player.name]
	return name_list

def get_mission_entitylist(chat_id):
	"""returns an ENTITY LIST of players who are on a mission now"""
	curr_game = get_curr_game(chat_id)
	player_list = get_curr_player_list(chat_id)
	name_list = []
	for player in player_list:
		if player.on_mission == True:
			name_list += [player]
	return name_list

def mission_clear(chat_id):
	"""set on mission attribute to be False for every player under the chat"""
	curr_game = get_curr_game(chat_id)
	player_list = get_curr_player_list(chat_id)
	for player in player_list:
		player.on_mission = False
		player.put()
	curr_game.put()
	return 

def get_mission_idlist(chat_id):
	"""someone's fav private messaging part haha"""
	"""returns a list of player user_ids on the mission"""
	curr_game = get_curr_game(chat_id)
	player_list = get_curr_player_list(chat_id)
	going_list = []
	for player in player_list:
		if player.on_mission == True:
			going_list += [player.user_id]
	return going_list

	
######
def next_leader(chat_id):
	"""Changes the next player's is_leader to True, and changes the current leader's is_leader to False"""
	"""and return the current leader as a player entity"""
	curr_game = get_curr_game(chat_id)
	player_list = get_curr_player_list(chat_id)		

	count = 0
	for player in player_list:
		if player.is_leader == True:
			player.is_leader = False
			player.put()
			break
		else:
			count += 1
	new_leader = player_list[(count + 1) % len(player_list)]
	new_leader.is_leader = True
	new_leader.put()

	return new_leader

def game_leader(chat_id):
	"""returns the current player who is the leader as an entity"""
	curr_game = get_curr_game(chat_id)
	player_list = get_curr_player_list(chat_id)

	for player in player_list:
		if player.is_leader == True:
			return player
	return

def all_can_vote(chat_id):
	curr_game = get_curr_game(chat_id)
	player_list = get_curr_player_list(chat_id)

	for player in player_list:
		player.can_vote = True
		player.put()
	return

def all_cannot_vote(chat_id):
	curr_game = get_curr_game(chat_id)
	player_list = get_curr_player_list(chat_id)

	for player in player_list:
		player.can_vote = False
		player.put()
	return

def mission_members_can_vote(chat_id):
	curr_game = get_curr_game(chat_id)
	player_list = get_mission_entitylist(chat_id)

	for player in player_list:
		player.can_vote = True
		player.put()
	return

def who_can_vote(chat_id):
	"""Returns a list of player (entities) who can still vote)"""
	player_list = get_curr_player_list(chat_id)
	new_list = []
	for player in player_list:
		if player.can_vote == True:
			new_list.append(player)
	return new_list

def update_mission_summary(chat_id, mission_success, num_succ):
	curr_game = get_curr_game(chat_id)
	if mission_success == True:
		if curr_game.mission_num == 1:
			curr_game.msn1 = "Success"
			curr_game.msn1numsucc = num_succ
			curr_game.put()
		elif curr_game.mission_num == 2:
			curr_game.msn2 = "Success"
			curr_game.msn2numsucc = num_succ
			curr_game.put()
		elif curr_game.mission_num == 3:
			curr_game.msn3 = "Success"
			curr_game.msn3numsucc = num_succ
			curr_game.put()
		elif curr_game.mission_num == 4:
			curr_game.msn4 = "Success"
			curr_game.msn4numsucc = num_succ
			curr_game.put()
		elif curr_game.mission_num == 5:
			curr_game.msn5 = "Success"
			curr_game.msn5numsucc = num_succ
			curr_game.put()
	else:
		if curr_game.mission_num == 1:
			curr_game.msn1 = "Failure"
			curr_game.msn1numsucc = num_succ
			curr_game.put()
		elif curr_game.mission_num == 2:
			curr_game.msn2 = "Failure"
			curr_game.msn2numsucc = num_succ
			curr_game.put()
		elif curr_game.mission_num == 3:
			curr_game.msn3 = "Failure"
			curr_game.msn3numsucc = num_succ
			curr_game.put()
		elif curr_game.mission_num == 4:
			curr_game.msn4 = "Failure"
			curr_game.msn4numsucc = num_succ
			curr_game.put()
		elif curr_game.mission_num == 5:
			curr_game.msn5 = "Failure"
			curr_game.msn5numsucc = num_succ
			curr_game.put()


def game_summary(chat_id):
	"""Returns a string showing a summary of the current game"""
	curr_game = get_curr_game(chat_id)
	text = "Current Mission progress: \n \n"
	text += "Mission 1: " 
	if curr_game.msn1 == "":
		for i in range(missionDict[curr_game.num_player][1]):
			text += emoman
	else:
		numfail1 = missionDict[curr_game.num_player][1] - curr_game.msn1numsucc
		for i in range(curr_game.msn1numsucc):
			text += emotick
		for i in range(numfail1):
			text += emocross
		if curr_game.msn1 == "Success":
			text += " Mission SUCCESS"
		else:
			text += " Mission FAILURE"
	text += "\nMission 2: "
	if curr_game.msn2 == "":
		for i in range(missionDict[curr_game.num_player][2]):
			text += emoman
	else:
		numfail2 = missionDict[curr_game.num_player][2] - curr_game.msn2numsucc
		for i in range(curr_game.msn2numsucc):
			text += emotick
		for i in range(numfail2):
			text += emocross
		if curr_game.msn2 == "Success":
			text += " Mission SUCCESS"
		else:
			text += " Mission FAILURE"
	text += "\nMission 3: "
	if curr_game.msn3 == "":
		for i in range(missionDict[curr_game.num_player][3]):
			text += emoman
	else:
		numfail3 = missionDict[curr_game.num_player][3] - curr_game.msn3numsucc
		for i in range(curr_game.msn3numsucc):
			text += emotick
		for i in range(numfail3):
			text += emocross
		if curr_game.msn3 == "Success":
			text += " Mission SUCCESS"
		else:
			text += " Mission FAILURE"
	text += "\nMission 4: "
	if curr_game.msn4 == "":
		for i in range(missionDict[curr_game.num_player][4]):
			text += emoman
	else:
		numfail4 = missionDict[curr_game.num_player][4] - curr_game.msn4numsucc
		for i in range(curr_game.msn4numsucc):
			text += emotick
		for i in range(numfail4):
			text += emocross
		if curr_game.msn4 == "Success":
			text += " Mission SUCCESS"
		else:
			text += " Mission FAILURE"
	text += "\nMission 5: "
	if curr_game.msn5 == "":
		for i in range(missionDict[curr_game.num_player][5]):
			text += emoman
	else:
		numfail5 = missionDict[curr_game.num_player][5] - curr_game.msn5numsucc
		for i in range(curr_game.msn5numsucc):
			text += emotick
		for i in range(numfail5):
			text += emocross
		if curr_game.msn5 == "Success":
			text += " Mission SUCCESS"
		else:
			text += " Mission FAILURE"
	text += "\n\nConsecutive nomination failures: " + str(curr_game.conesequetive_fail_votes_num) + "/5\n \n"
	return text

def end_game_summary(chat_id):
	curr_game = get_curr_game(chat_id)
	text = "The results of the Missions: \n \n"
	text += "Mission 1: " 
	if curr_game.msn1 == "":
		for i in range(missionDict[curr_game.num_player][1]):
			text += emoman
	else:
		numfail1 = missionDict[curr_game.num_player][1] - curr_game.msn1numsucc
		for i in range(curr_game.msn1numsucc):
			text += emotick
		for i in range(numfail1):
			text += emocross
		if curr_game.msn1 == "Success":
			text += " Mission SUCCESS"
		else:
			text += " Mission FAILURE"
	text += "\nMission 2: "
	if curr_game.msn2 == "":
		for i in range(missionDict[curr_game.num_player][2]):
			text += emoman
	else:
		numfail2 = missionDict[curr_game.num_player][2] - curr_game.msn2numsucc
		for i in range(curr_game.msn2numsucc):
			text += emotick
		for i in range(numfail2):
			text += emocross
		if curr_game.msn2 == "Success":
			text += " Mission SUCCESS"
		else:
			text += " Mission FAILURE"
	text += "\nMission 3: "
	if curr_game.msn3 == "":
		for i in range(missionDict[curr_game.num_player][3]):
			text += emoman
	else:
		numfail3 = missionDict[curr_game.num_player][3] - curr_game.msn3numsucc
		for i in range(curr_game.msn3numsucc):
			text += emotick
		for i in range(numfail3):
			text += emocross
		if curr_game.msn3 == "Success":
			text += " Mission SUCCESS"
		else:
			text += " Mission FAILURE"
	text += "\nMission 4: "
	if curr_game.msn4 == "":
		for i in range(missionDict[curr_game.num_player][4]):
			text += emoman
	else:
		numfail4 = missionDict[curr_game.num_player][4] - curr_game.msn4numsucc
		for i in range(curr_game.msn4numsucc):
			text += emotick
		for i in range(numfail4):
			text += emocross
		if curr_game.msn4 == "Success":
			text += " Mission SUCCESS"
		else:
			text += " Mission FAILURE"
	text += "\nMission 5: "
	if curr_game.msn5 == "":
		for i in range(missionDict[curr_game.num_player][5]):
			text += emoman
	else:
		numfail5 = missionDict[curr_game.num_player][5] - curr_game.msn5numsucc
		for i in range(curr_game.msn5numsucc):
			text += emotick
		for i in range(numfail5):
			text += emocross
		if curr_game.msn5 == "Success":
			text += " Mission SUCCESS"
		else:
			text += " Mission FAILURE"
	return text

@ndb.transactional
def increment_game_yes(chat_id):
	curr_game = get_curr_game(chat_id)
	curr_game.yes_count += 1
	curr_game.put()
	return curr_game

@ndb.transactional
def increment_game_no(chat_id):
	curr_game = get_curr_game(chat_id)
	curr_game.no_count += 1
	curr_game.put()
	return curr_game

@ndb.transactional
def increment_game_succ(chat_id):
	curr_game = get_curr_game(chat_id)
	curr_game.succ_count += 1
	curr_game.put()
	return curr_game

@ndb.transactional
def increment_game_fail(chat_id):
	curr_game = get_curr_game(chat_id)
	curr_game.fail_count += 1
	curr_game.put()
	return curr_game

@ndb.transactional
def increment_game_num_player(chat_id):
	curr_game = get_curr_game(chat_id)
	curr_game.num_player += 1
	curr_game.put()
	return curr_game

@ndb.transactional
def decrement_game_num_player(chat_id):
	curr_game = get_curr_game(chat_id)
	curr_game.num_player -= 1
	curr_game.put()
	return curr_game





