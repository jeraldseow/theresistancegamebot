import StringIO
import json
import logging
import random
import urllib
import urllib2


# for sending images
#from PIL import Image
#import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2
from models import Game, Player
import utils

from secrets import TOKEN

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

# ================================
class EnableStatus(ndb.Model):
	# key name: str(chat_id)
	enabled = ndb.BooleanProperty(indexed=False, default=False)
# ================================

def setEnabled(chat_id, yes):
	es = EnableStatus.get_or_insert(str(chat_id))
	es.enabled = yes
	es.put()

def getEnabled(chat_id):
	es = EnableStatus.get_by_id(str(chat_id))
	if es:
		return es.enabled
	return False

class MeHandler(webapp2.RequestHandler):
	def get(self):
		urlfetch.set_default_fetch_deadline(60)
		self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))

class GetUpdatesHandler(webapp2.RequestHandler):
	def get(self):
		urlfetch.set_default_fetch_deadline(60)
		self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))

class SetWebhookHandler(webapp2.RequestHandler):
	def get(self):
		urlfetch.set_default_fetch_deadline(60)
		url = self.request.get('url')
		if url:
			self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})
																	  )
													)
											)
								)

class WebhookHandler(webapp2.RequestHandler):
	def post(self):
		urlfetch.set_default_fetch_deadline(60)
		body = json.loads(self.request.body)
		logging.info('request body:')
		logging.info(body)
		self.response.write(json.dumps(body))

		update_id = body['update_id']
		try:
			message = body['message']
		except:
			message = body['edited_message']
		message_id = message.get('message_id')
		date = message.get('date')
		text = message.get('text')
		fr = message.get('from')
		chat = message['chat']
		chat_id = chat['id']
		if 'title' in chat:
			chat_title = chat['title']
		chat_type = chat['type']
		fr_user_id = fr['id']
		fr_user_name = fr['first_name'] 
		if 'last_name' in fr:
			fr_user_name += ' ' + fr['last_name']

		if not text:
			logging.info('no text')
			return
#=====================================================

		def reply(msg=None):
			if msg:
				resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
					'chat_id': str(chat_id),
					'text': msg.encode('utf-8'),
					'disable_web_page_preview': 'true',
					'reply_to_message_id': str(message_id),
				})).read()
			else:
				logging.error('no msg or img specified')
				resp = None

			logging.info('send response:')
			logging.info(resp)

		def reply_to_user(user_id, msg=None):
			if msg:
				resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
					'chat_id': str(user_id),
					'text': msg.encode('utf-8'),
					'disable_web_page_preview': 'true',
				})).read()
			else:
				logging.error('no msg or img specified')
				resp = None

			logging.info('send response:')
			logging.info(resp)

		def announce(msg=None, img=None):
			if msg:
				resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
					'chat_id': str(chat_id),
					'text': msg.encode('utf-8'),
					'disable_web_page_preview': 'true',
				})).read()
			elif img:
				resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
					('chat_id', str(chat_id)),
				], [
					('photo', 'image.jpg', img),
				])
			else:
				logging.error('no msg or img specified')
				resp = None

			logging.info('send response:')
			logging.info(resp)

		def keyboard_yes_no(user_id, msg=None):
			keyboard = json.dumps({ 'keyboard':[["/yes"],["/no"]],
				'one_time_keyboard': True,
				'resize_keyboard': True
				})
			if msg:
				resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
					'chat_id': str(user_id),
					'text': msg.encode('utf-8'),
					'disable_web_page_preview': 'true',
					'reply_markup': keyboard,
				})).read()
			else:
				logging.error('no msg or img specified')
				resp = None

			logging.info('send response:')
			logging.info(resp)

		def keyboard_s_f(user_id, msg=None):
			keyboard = json.dumps({ 'keyboard':[["/success"],["/fail"]],
				'one_time_keyboard': True,
				'resize_keyboard': True
				})
			if msg:
				resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
					'chat_id': str(user_id),
					'text': msg.encode('utf-8'),
					'disable_web_page_preview': 'true',
					'reply_markup': keyboard,
				})).read()
			else:
				logging.error('no msg or img specified')
				resp = None

			logging.info('send response:')
			logging.info(resp)

		def keyboard_s(user_id, msg=None):
			keyboard = json.dumps({ 'keyboard':[["/success"]],
				'one_time_keyboard': True,
				'resize_keyboard': True
				})
			if msg:
				resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
					'chat_id': str(user_id),
					'text': msg.encode('utf-8'),
					'disable_web_page_preview': 'true',
					'reply_markup': keyboard,
				})).read()
			else:
				logging.error('no msg or img specified')
				resp = None

			logging.info('send response:')
			logging.info(resp)

		def keyboard_nomination(user_id, msg=None):
			player = Player.query(Player.user_id == user_id).get()
			buttons = utils.get_curr_player_slashnamelist(player.parent_chat_id)
			keyboard = json.dumps({ 'keyboard':buttons,
				'one_time_keyboard': True,
				'resize_keyboard': True
				})
			if msg:
				resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
					'chat_id': str(user_id),
					'text': msg.encode('utf-8'),
					'disable_web_page_preview': 'true',
					'reply_markup': keyboard,
				})).read()
			else:
				logging.error('no msg or img specified')
				resp = None

			logging.info('send response:')
			logging.info(resp)

		def end_game(chat_id):
			"""announce winner team; reveal role assignment; clear records"""
			curr_game = utils.get_curr_game(chat_id)
			line = "The winning team is: The " + curr_game.winner + ". Congratulations!"
			reply_to_user(chat_id, line)
			line = "The spies for this round were: "
			spy_namelist = utils.get_spy_namelist(chat_id)
			for spy_name in spy_namelist:
				line += spy_name
				line += ', '
			line = line[:-2]
			line += "\n \n"
			text = utils.end_game_summary(chat_id)
			line += text
			line += "\n Thanks for playing, see you next time!"
			reply_to_user(chat_id, line)
			for player in utils.get_curr_player_list(chat_id):
				player.key.delete()
			curr_game.key.delete()
			return 

#=====================================================
		if utils.get_curr_game(chat_id) != None:
			curr_game = utils.get_curr_game(chat_id)

			if curr_game != None and curr_game.num_player == 0:
				curr_game.key.delete()
				#announce("woops, there was a game going on that didn't have any players in it. Don't mind me while I just end that game.")
			elif date > curr_game.game_time + 172800:
				announce("This game has lasted way longer than it should have. Shutting down this instance of the game.")
				for player in utils.get_curr_player_list(chat_id):
					player.key.delete()
				curr_game.key.delete()
			elif date > curr_game.game_time + 120 and curr_game.state == 'player_addition':
				announce("Insufficient players to proceed, game shutting down now")
				for player in utils.get_curr_player_list(chat_id):
					player.key.delete()
				curr_game.key.delete()
			elif date > curr_game.game_time + 60 and curr_game.state == 'player_addition':
				announce(str(curr_game.game_time + 120 - date)+ " seconds left! Quick! Find more friends to join in on the fun!")


		if text.startswith('/'):

			if text == '/start': 
				reply('Bot enabled')
				setEnabled(chat_id, True)

			elif text == "/stop":
				reply('Bot disabled')
				setEnabled(chat_id, False)

			elif text == "/num":
				curr_game = utils.get_curr_game(chat_id)
				announce(str(curr_game.num_player))

			elif chat_type == 'group' or chat_type == 'supergroup':
				curr_player = Player.query(Player.user_id == fr_user_id).get()
				curr_game = utils.get_curr_game(chat_id)

				if curr_game == None:
					if text == '/newgame' or text == "/newgame@theresistancegamebot":
						if curr_player == None:
							new_game = Game(chat_id = chat_id, chat_title = chat_title, game_time = date)    
							new_game.put()
							utils.put_new_player(chat_id, fr_user_id, fr_user_name)
							line = fr_user_name + ' has started a game!'
							reply(line)
							announce("Please open a private conversation with me (by clicking on this -> @theresistancegamebot) and click start so that you can join in the fun! (And also so you won't mess up the game) \n \nType /startgame at any point after we have sufficient players to start the game (Min 5 players, Max 10) \n \nIt's time to type /join to join in on the fun if you have yet to do so! The game will self destruct in 2 minutes if there are insufficient players!")
						else:
							chat_name = utils.get_curr_game(curr_player.parent_chat_id).chat_title
							if chat_name == None:
								reply("Please start only one game at a time, end the other game you are in before starting another one!")
							else:
								reply("Please start only one game at a time, end the other game you are in with " + chat_name  + " before starting another one!")

					elif "@theresistancegamebot" in text:
						reply_to_user(chat_id, 'Please start a new game using /newgame')
					else:
						return 

				elif curr_player == None and (text == "/join" or text == "/join@theresistancegamebot"):
					if text == '/join' or text == "/join@theresistancegamebot":
						curr_game_key = curr_game.key
						existing_player = Player.query(ancestor = curr_game_key).filter(Player.user_id == fr_user_id).get()
						if existing_player:
							reply("You're already in this game!")
						else:
							num_players = curr_game.num_player
							if num_players < 10:
								utils.put_new_player(chat_id, fr_user_id, fr_user_name)
								line = fr_user_name + ' has joined the game! 1 minute countdown has been reset!'
								curr_game.game_time = date
								curr_game.put()
								this_player = Player.query(ancestor = curr_game_key).filter(Player.user_id == fr_user_id).get()	
								reply(line + " " + str(curr_game.num_player) + " players, 10 maximum")
								if getEnabled(this_player.user_id) == False:
									reply("Hi there " + this_player.name + ", I need you to click on me at -> @theresistancegamebot and press /start to activate me before I can tell you your role!")
								if curr_game.num_player == 10:
									announce("You already have 10 players! Somebody start the game using /startgame and let's get this game going!") 
								else:
									pass
							else:
								reply("You already have 10 players! Somebody start the game using /startgame and get this game going!")

				elif curr_player == None:
					reply("You my dear friend are not in a game! Type /join to join the game if it has not yet started!")

				elif curr_player.parent_chat_id != chat_id:
					reply("Get back to " + utils.get_curr_game(curr_player.parent_chat_id).chat_title + " where your game is ongoing! You don't belong here!")

				elif curr_player.parent_chat_id == chat_id:
					if text == "/end" or text == "/end@theresistancegamebot":
						existing_game = utils.get_curr_game(chat_id)
						for player in utils.get_curr_player_list(chat_id):
							player.key.delete()
						reply ("Thanks for playing, see you next time!")
						utils.get_curr_game(chat_id).key.delete()

					elif text == "/players" or text == "/players@theresistancegamebot":
						existing_game = utils.get_curr_game(chat_id)
						player_list = utils.get_curr_player_list(chat_id)
						player_namelist = 'Current players: '

						for cur_player in player_list:
							player_namelist = player_namelist + cur_player.name + ", "
						player_namelist = player_namelist[:-2]
						if curr_game.num_player > 4:
							player_namelist += ". There will be " + str(utils.identityDictRS[curr_game.num_player][1]) + " spies in the game."
						reply (player_namelist)

					elif text == '/missionmembers' or text == "/missionmembers@theresistancegamebot":
						if curr_game.state != 'mission':
							reply("The team has yet to be firmed up, wait till the mission phase to type this command")
						else:
							line = "Current Members chosen to be on the Mission: "
							mission_namelist = utils.get_mission_namelist(chat_id)
							for member in mission_namelist:
								line += member 
								line += ', '
							line = line[:-2]
							reply(line)

					elif (text == '/whoarewewaitingfor' or text == '/whoarewewaitingfor@theresistancegamebot') and (curr_game.state == 'voting' or curr_game.state == 'mission'):
						new_list = utils.who_can_vote(chat_id)
						if len(new_list) > 0:
							out = "We're still waiting for "
							for player in new_list:
								out += player.name + ", "
							out = out[:-2]
							out += " to vote! Hurry them up!"
							announce(out)
						else:
							announce("We're not waiting for anyone, let's keep the game going!")

					elif text == "/state" or text == "/state@theresistancegamebot":
						reply("Current game state: " + curr_game.state)

					elif text == "/summary" or text == "/summary@theresistancegamebot":
						reply(utils.game_summary(chat_id))

					elif text == "/help" or text == "/help@theresistancegamebot":
						reply("Here is a list of commands for the game: \n/newgame - Starts a new game! \n/players - Shows you a list of who is in the current game \n/leave - Allows you to leave the game if it has yet to start \n/startgame - Starts the game if there are sufficient players \n/yes - a Yes vote (to be sent privately to me in the Team Selection Phase) \n/no - a No vote (to be sent privately to me in the Team Selection Phase) \n/success - a Success vote (to be sent privately to me in the Mission Phase) \n/fail - a Faile vote (to be sent privately to me in the Mission Phase) \n/whoarewewaitingfor - Informs you who has yet to vote on the Team selection or on the ourtcome of the Mission \n/missionmembers - Informs you on who has been chosen to go on the Mission \n/summary - Gives you a summary of what the outcome of the previous missions have beeen thus far \n/end - **USE WITH CAUTION** can be entered by any participating player in the game to end the game immediately without an outcome.")

					elif text == "/rules" or text == "/rules@theresistancegamebot":
						reply("Welcome to The Resistance, a game that pits the closest of friends against one another in an epic battle of identity discovery and misplacement of trust. \n \
							When the game is started, each player is designated a role, either as a Member of the Resistance (the good guys), or a Member of the Spies (the baddies). The objective of each team is to cause Success (for the resistance) or Failure (for the spies) for 3 out of 5 of the available missions. The spies have an additional way to win, which will be described in greater detail during the 'Team selection' Phase. \n \
							After the game is started, the game goes into the 'Team selection' phase, where players take turns to become the leader of the current Mission, and get to select a certain number of players to go for the Mission. The leader is allowed to choose him or herself to go on the mission. Once the team has been formed, all the other players in the game get to vote on whether they want this team to go for the Mission. This is done through the /yes or /no votes sent through a private chat with the bot. If there is a majority of /yes votes, then the team will be passed and the game will proceed into the Mission phase. If there are insufficient /yes votes, then the next player will become the leader for the mission, and he/she will be able to choose a new team to go on the Mission. If there are five consequetive times within a mission whereby the group is not able to decide on a team to go on the mission, the Spies automatically win, and the game ends. \n \
							In the Mission phase, the selected players to be on the team that goes for the Mission each have the opportunity to submit a /success or /fail vote to the bot privately. These votes are in done in confidence, and will determine the outcome of the Mission. Apart from the cases whereby the team is on the fourth mission, and there are 7 or more players in the game, every other Mission only requires one Fail vote for the mission to fail. In the case where there are 7 or more players in the game, and the team is on the Fourth mission, TWO fail votes are required for the Mission to Fail. \n \
							Once all the votes have been consolidated, the outcome of the Mission will be announced, and the next leader will be selected for the next Mission. This process repeats itself until either one of the teams have achieved 3 mission failures or 3 mission successes, which will mark the end of the game, and the opportunity to start a new one.")

					elif curr_game.state == 'player_addition':
						if text == '/leave' or text == "/leave@theresistancegamebot":
							existing_player = Player.query(ancestor = curr_game.key).filter(Player.user_id == fr_user_id).get()
							announce(existing_player.name + " has left the game!")
							utils.remove_player(chat_id, existing_player.user_id)
							announce(str(curr_game.num_player) + " players, 10 maximum")

						elif text == '/startgame' or text == "/startgame@theresistancegamebot":
							curr_game = utils.get_curr_game(chat_id)
							curr_game.num_player = len(utils.get_curr_player_list(chat_id))
							num_players = curr_game.num_player
							players = utils.get_curr_player_list(chat_id)
							no_ready_list = []
							for player in players:
								if getEnabled(player.user_id) == False:
									no_ready_list.append(player)

							if num_players < 5:
								reply ('We need more players before we can start! Go get more friends to join the game!')
								announce("We now have " + str(num_players) + " players, we need at least 5 players to start the game!")

							elif len(no_ready_list) > 0:
								spoilers = ""
								for player in no_ready_list:
									spoilers += player.name + ", "
								spoilers = spoilers[:-2]
								announce("Your dear friend(s) " + spoilers + " did not activate me as I said, please do so by clicking on me -> @theresistancegamebot and pressing /start before trying to start the game again by entering /startgame")

							else:   
								curr_game.state = 'selection'
								curr_game.put()
								utils.assign_role(chat_id)
								spy_namelist = utils.get_spy_namelist(chat_id)
								line = ""
								for name in spy_namelist:
									line += name
									line += ", "
								line = line[:-2]
								for resistance in utils.get_resistance_list(chat_id):
									reply_to_user(resistance.user_id, u"You are a member of the Resistance! (a.k.a the good guys \U0001F607)")		
								for spy in utils.get_spy_list(chat_id):
									reply_to_user(spy.user_id, u"You are: a Spy. \U0001F608 Go and wreck havoc with your friends " + line)
								curr_leader = Player.query(ancestor = curr_game.key).fetch(1)[0]
								curr_leader.is_leader = True
								curr_leader.put()
								msg = "The current leader is " + curr_leader.name + ". Please nominate " + str(utils.missionDict[curr_game.num_player][curr_game.mission_num]) + " friends you wish to send on this Mission."
								announce(msg)
								keyboard_nomination(curr_leader.user_id, "Send me the names of those you wish to nominate for this Mission.")

						else:
							announce("Incorrect command, type /join or /startgame instead")

					elif curr_game.state == 'selection':
						reply("Please reply me in your private chat with me.")

					elif curr_game.state == 'voting':
						reply("Please reply me in your private chat with me.")

					elif curr_game.state == 'mission':
						reply("Shhh, you're not supposed to let your friends know how you voted. Please send your votes privately to me.")
						
					else:
						return
				else:
					reply("You are not in the game, wait for the next round to join in the fun!")

			else: 
				curr_player = Player.query(Player.user_id == fr_user_id).get()
				if curr_player != None:
					curr_game = utils.get_curr_game(curr_player.parent_chat_id)

					if curr_game.state == "player_addition":
						reply("Now's not the time for you to be talking to me here, get back on the group chat!")

					elif curr_game.state == "selection":
						member = Player.query(Player.user_id == fr_user_id).get()
						curr_game = utils.get_curr_game(member.parent_chat_id)
						role_dict = utils.get_role_dict(member.parent_chat_id)
						if member.is_leader == False:
							reply("You are not the leader for this round of nominations, get back onto the group chat")
						
						else:
							text = text[1::]
							if (text in role_dict): 
								if utils.mission_full(member.parent_chat_id):
									reply("We have enough players on Mission already!")
								else:
									selected_player = utils.player_selected(member.parent_chat_id, text)
									if selected_player.on_mission == True:
										reply("Please choose someone else who has not been nominated yet!")
										keyboard_nomination(utils.game_leader(curr_game.chat_id).user_id, "Who else would you like to nominate?")
									else:
										selected_player.on_mission = True
										selected_player.put()
										reply_msg = selected_player.name + " has been nominated to go for the Mission"
										reply_to_user(member.parent_chat_id, reply_msg)
										reply(reply_msg)
										if (utils.mission_full(member.parent_chat_id)):
											reply_msg = "We have enough players for the Mission! They are: "
											for name in utils.get_mission_namelist(member.parent_chat_id):
												reply_msg += name 
												reply_msg += ", "
											reply_msg = reply_msg[:-2]    
											reply_to_user(member.parent_chat_id, reply_msg)
											reply_to_user(member.parent_chat_id, "Please vote to decide if you want these guys on the Mission!")
											utils.all_can_vote(member.parent_chat_id)
											curr_game.state = 'voting'
											curr_game.put()
											for player in utils.get_curr_player_list(member.parent_chat_id):
												keyboard_yes_no(player.user_id,"Please submit a /yes or /no vote if you want these guys on the Mission!")
										else:
											keyboard_nomination(utils.game_leader(curr_game.chat_id).user_id, "Who else would you like to nominate?")
							else:
								reply("I think you must have made a typo? Please spell the player's name accurately or use the custom keyboard to help enter your friends' names accurately.")

					elif curr_game.state == "voting":
						member = Player.query(Player.user_id == fr_user_id).get()
						curr_game = utils.get_curr_game(member.parent_chat_id)

						if text == '/yes' or text == '/no':
							if member.can_vote == True:
								member.can_vote = False
								member.put()
								if text == "/yes": 
									curr_game.yes_count += 1
									curr_game.put()
									reply("Ok I've received your vote!")
									reply_to_user(member.parent_chat_id, member.name + u" has voted YES \U0001F44C")
								else:
									curr_game.no_count += 1 
									curr_game.put()
									reply("Ok I've received your vote!")
									reply_to_user(member.parent_chat_id, member.name + u" has voted NO \U0001F44E")
							else:
								reply("You've already submitted your vote! Each player is only entitled to ONE vote!")

							if curr_game.yes_count + curr_game.no_count == curr_game.num_player:
								if curr_game.yes_count > curr_game.no_count:
									curr_game.conesequetive_fail_votes_num = 0
									curr_game.state = 'mission'
									curr_game.put()
									line = "Our friends: "
									for name in utils.get_mission_namelist(member.parent_chat_id):
										line += name 
										line += ", "
									line = line[:-2]
									line += " are going on a Mission now! Give them a moment to determine the outcome of the Mission!"
									utils.mission_members_can_vote(member.parent_chat_id)
									reply_to_user(member.parent_chat_id, line)
									if curr_game.numplayer > 6 and curr_game.mission_num == 4:
										reply_to_user(member.parent_chat_id, "Spies do take note: you require TWO Fail votes for this Mission to fail.")
									
									for player in utils.get_mission_entitylist(member.parent_chat_id):
										if player.role == 'spy':
											keyboard_s_f(player.user_id, "Please reply /success or /fail to determine the outcome of the Mission!")
										else:
											keyboard_s(player.user_id, "As a member of the Resistance, you are only allowed to vote /success to the outcome of this Mission.")
									curr_game.yes_count = 0
									curr_game.no_count = 0
									curr_game.put()
								else:
									curr_game.yes_count = 0
									curr_game.no_count = 0
									curr_game.state = "selection"
									curr_game.conesequetive_fail_votes_num += 1
									curr_game.put()
									if curr_game.conesequetive_fail_votes_num < 5:
										new_leader = utils.next_leader(member.parent_chat_id)
										reply_to_user(member.parent_chat_id, "Insufficient Yes votes to proceed, next leader: " + new_leader.name + ". Please nominate a new set of " + str(utils.missionDict[curr_game.num_player][curr_game.mission_num]) + " friends to go for the Mission!")
										keyboard_nomination(utils.game_leader(curr_game.chat_id).user_id, "Send me the names of those you wish to nominate here")
										utils.all_can_vote(member.parent_chat_id)
										utils.mission_clear(member.parent_chat_id)
										if curr_game.numplayer > 6 and curr_game.mission_num == 4:
											reply_to_user(curr_game.chat_id, "Spies do take note: you require TWO Fail votes for this Mission to fail.")
									else:
										reply_to_user(member.parent_chat_id, "Insufficient Yes votes to proceed, the spies have caused sufficient chaos to confuse the resistance")
										curr_game.winner = 'Spies'
										curr_game.put()
										end_game(member.parent_chat_id)

						else:
							announce("please reply /yes or /no to indicate your vote")

					elif curr_game.state == "mission":
						if text == '/success' or text == '/fail':
							if curr_player.can_vote == True:
								if text == '/success':
									curr_player.can_vote = False
									curr_player.put()
									curr_game.succ_count += 1
									curr_game.put()
									reply(u"Thank you for not sabotaging the Mission \U0001F31D")
								else:
									if curr_player.role == 'spy':
										curr_player.can_vote = False
										curr_player.put()
										curr_game.fail_count += 1
										curr_game.put()
										reply(u"You crook, why would you want the Mission to fail?! \U0001F31A")
									else:
										reply("You're not allowed to sabotage the Mission as the member of the resistance! Send me your vote again!")
										keyboard_s(curr_player.user_id, "As a member of the Resistance, you are only allowed to vote /success to the outcome of this Mission.")
							else:
								reply("You have already cast your vote for this Mission!")
						else:
							reply("Please send me /success or /fail to indicate your vote")
						
						if curr_game.succ_count + curr_game.fail_count == len(utils.get_mission_namelist(curr_game.chat_id)):
							if (curr_game.fail_count == 0) or (curr_game.num_player >6 and curr_game.fail_count <= 1 and curr_game.mission_num == 4):
								line = "Mission " + str(curr_game.mission_num) + " has been successful! There were " + str(curr_game.succ_count) + " success votes and " + str(curr_game.fail_count) + " fail votes!" 
								utils.update_mission_summary(curr_game.chat_id, True)
								reply_to_user(curr_game.chat_id, line)
								curr_game.mission_succ_count += 1
								curr_game.mission_num += 1
								utils.mission_clear(curr_player.parent_chat_id)
								curr_game.put()
								if curr_game.mission_succ_count == 3:
									curr_game.winner = 'Resistance'
									end_game(curr_game.chat_id)
		
								else:
									curr_game.state = 'selection'
									curr_game.succ_count = 0
									curr_game.fail_count = 0
									curr_game.put()

									next_leader = utils.next_leader(curr_game.chat_id)
									line = "The leader for the next round is: " + next_leader.name + ". Please nominate a new set of " + str(utils.missionDict[curr_game.num_player][curr_game.mission_num]) +" friends to go for the Mission!"
									reply_to_user(curr_game.chat_id, line)
									keyboard_nomination(utils.game_leader(curr_game.chat_id).user_id, "Send me the names of those you wish to nominate here")
									if curr_game.numplayer > 6 and curr_game.mission_num == 4:
										reply_to_user(curr_game.chat_id, "Spies do take note: you require TWO Fail votes for this Mission to fail.")
							else:
								line = "Mission " + str(curr_game.mission_num) + " has ended in failure! There were " + str(curr_game.succ_count) + " success votes and " + str(curr_game.fail_count) + " fail votes!"
								utils.update_mission_summary(curr_game.chat_id, False)
								reply_to_user(curr_game.chat_id, line)
								curr_game.mission_fail_count += 1
								curr_game.mission_num += 1
								utils.mission_clear(curr_player.parent_chat_id)
								curr_game.put()
								if curr_game.mission_fail_count == 3:
									curr_game.winner = 'Spies'
									curr_game.put()
									end_game(curr_game.chat_id)
								
								else:
									curr_game.state = 'selection'
									curr_game.succ_count = 0
									curr_game.fail_count = 0
									curr_game.put()
									next_leader = utils.next_leader(curr_game.chat_id) 
									line = "The leader for the next round is: " + next_leader.name + ". Please nominate a new set of " + str(utils.missionDict[curr_game.num_player][curr_game.mission_num]) +" friends to go for the Mission!"
									reply_to_user(curr_game.chat_id, line)
									keyboard_nomination(utils.game_leader(curr_game.chat_id).user_id, "Send me the names of those you wish to nominate here")
									if curr_game.numplayer > 6 and curr_game.mission_num == 4:
										reply_to_user(curr_game.chat_id, "Spies do take note: you require TWO Fail votes for this Mission to fail.")  

					else:
						reply("save me I'm not supposed to be hereeee...")

				else:
					announce('Get into a game with a group of friends by typing /newgame on your group chat!')


app = webapp2.WSGIApplication([
	('/me', MeHandler),
	('/updates', GetUpdatesHandler),
	('/set_webhook', SetWebhookHandler),
	('/' + TOKEN, WebhookHandler),
], debug=True)
