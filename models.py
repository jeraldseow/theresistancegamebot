from google.appengine.ext import ndb

class Game(ndb.Model):
    chat_title = ndb.StringProperty(required = True)
    game_time = ndb.IntegerProperty(required = True)
    mission_num = ndb.IntegerProperty(default = 1) 
    conesequetive_fail_votes_num = ndb.IntegerProperty(default = 0) ## 1 to 5; increase when each consequetive selection phase fails
    msn1 = ndb.StringProperty(choices = ["F", "S", "N"], default = "N")
    msn2 = ndb.StringProperty(choices = ["F", "S", "N"], default = "N")
    msn3 = ndb.StringProperty(choices = ["F", "S", "N"], default = "N")
    msn4 = ndb.StringProperty(choices = ["F", "S", "N"], default = "N")
    msn5 = ndb.StringProperty(choices = ["F", "S", "N"], default = "N")
    state = ndb.StringProperty(choices = ['player_addition', 'selection','voting','mission'], default = 'player_addition')
    
    num_player = ndb.IntegerProperty(default = 0)

    yes_count = ndb.IntegerProperty(default = 0)
    no_count = ndb.IntegerProperty(default = 0)

    succ_count = ndb.IntegerProperty(default = 0)
    fail_count = ndb.IntegerProperty(default = 0)

    mission_succ_count = ndb.IntegerProperty(default = 0)
    mission_fail_count = ndb.IntegerProperty(default = 0)

    winner = ndb.StringProperty(choices = ['Spies','Resistance'])

    def get_id(self):
        return self.key().name()

   
class Player(ndb.Model):
    user_id = ndb.IntegerProperty(required=True)
    role = ndb.StringProperty (
        choices = ['spy','resistance']) 
    name = ndb.StringProperty()
    is_leader = ndb.BooleanProperty(default = False)
    on_mission = ndb.BooleanProperty(default = False)
    parent_chat_id = ndb.IntegerProperty(required = True)
    can_vote = ndb.BooleanProperty(default = False)
