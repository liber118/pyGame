#!/usr/bin/env python
# encoding: utf-8

import json
import random
import sys
import uuid


######################################################################
## game parameters

MAX_TURNS = 100
LEN_STALEMATE = 3

INIT_FORCE = 100.0
MIN_RESERVE = 2.0
RESERVE_RATIO = 0.05


######################################################################
## global variables and utility methods
      
debug = True # False


def roll_dice10 ():
    return random.randint(0, 9)


######################################################################
## class definitions

class GameOverException (Exception):

    def __init__(self, value):
        self.value = value


    def __str__(self):
        return repr(self.value)


class Card:
    """
    representation for a generic card in the deck
    """

    def __init__ (self, name, replace=False):
        self.name = name
        self.replace = replace


    def execute (self, game, us, them):
        if debug:
            print "nop"


class ForceReductionCard (Card):
    """
    representation for a 'force reduction' card in the deck
    """

    def __init__ (self, name, replace=False):
        Card.__init__(self, name, replace)


    def execute (self, game, us, them):
        ## DICE: d10+1/20

        IMPACT_FACTOR = 20.0
        roll = (roll_dice10() + 1.0) / IMPACT_FACTOR
        delta = round(roll * us.meta["n_deploy"], 0)

        if us.meta["enraged"]:
            REDUCE_FACTOR = 5.0
            casualty = round(roll / REDUCE_FACTOR * delta, 0)

            if debug:
                print them.name, ":", "CASUALTY", casualty

            delta -= casualty
            them.record_loss(casualty, "forces_name", "casualties")
            them.meta["n_casualty"] += casualty

        them.record_loss(delta, "forces_name", self.name)
        us.add_captive(game, delta)
        them.add_forces(game, -delta)


class InsurrectionCard (Card):
    """
    representation for an 'insurrection' card in the deck
    """

    def __init__ (self, name, replace=False):
        Card.__init__(self, name, replace)


    def execute (self, game, us, them):
        ## DICE: d10/10

        roll = roll_dice10() / 10.0
        delta = round(roll * them.meta["n_captive"], 0)

        if debug:
            print "exec insurrect", them.meta["n_captive"], "delta", delta

        INSURRECT_FACTOR = 10.0

        if delta > (them.meta["init_force"] / INSURRECT_FACTOR):
            them.record_loss(delta, "forces_name", self.name)
            them.add_captive(game, -delta)
            us.add_forces(game, delta)


class ConversionCard (Card):
    """
    representation for a 'conversion' card in the deck
    """

    def __init__ (self, name, replace=False):
        Card.__init__(self, name, replace)


    def execute (self, game, us, them):
        ## DICE: d10/10, >0

        ROLL_CONVERT = 0.0
        roll = roll_dice10() / 10.0

        if roll > ROLL_CONVERT:
            delta = round(roll * them.meta["n_forces"], 0)

            them.record_loss(delta, "forces_name", self.name)
            them.add_forces(game, -delta)
            us.add_forces(game, delta)


class SeriouslyWeirdCard (Card):
    """
    representation for a 'seriously weird' card in the deck
    """

    def __init__ (self, name, replace=False):
        Card.__init__(self, name, replace)


    def execute (self, game, us, them):
        ## DICE: d10/10, >1

        ROLL_WEIRD = 1.0

        roll = roll_dice10() / 10.0

        if roll > ROLL_WEIRD:
            delta = round(roll * them.meta["n_forces"], 0)
            them.record_loss(delta, "forces_name", self.name)
            them.add_forces(game, -delta)


class Player:
    """
    representation for a player in the game
    """

    def __init__ (self, name, init_force, forces_name, captive_name):
        """
        initialize
        """

        self.name = name
        self.meta = {}
        self.deck = []
        self.opponent = None

        self.meta["init_force"] = init_force
        self.meta["n_forces"] = init_force
        self.meta["n_deploy"] = init_force
        self.meta["n_captive"] = 0
        self.meta["n_reserve"] = 0
        self.meta["n_casualty"] = 0

        self.meta["enraged"] = False
        self.meta["has_comm"] = True
        self.meta["forces_name"] = forces_name
        self.meta["captive_name"] = captive_name


    def set_opponent (self, opponent):
        self.opponent = opponent


    def add_card (self, card, num):
        """
        add cards to the deck
        """

        for i in range(0, num):
            self.deck.append(card)


    def has_play (self):
        """
        test whether this player has a next play available
        """

        return len(self.deck) > 0


    def pick_card (self):
        """
        pick the next card to play
        """

        card = random.choice(self.deck)

        if not card.replace:
            self.deck.remove(card)

        return card


    def calc_reserve (self):
        """
        calculate the required reserves
        """

        return round(max(MIN_RESERVE, self.meta["n_captive"] * RESERVE_RATIO), 0)


    def add_forces (self, game, delta):
        if delta != 0.0:
            if debug:
                print "add_forces", self.meta["n_forces"], "delta", delta

            if self.meta["n_forces"] + delta <= 0:
                game.game_over(self.opponent, "overwhelmed opponents")
            else:
                self.meta["n_forces"] += delta;

            if not (self.meta["n_forces"] >= 0):
                raise AssertionError("negative forces size: " + self.name + str(self.meta))


    def add_captive (self, game, delta):
        if delta != 0.0:
            if debug:
                print "add_captive", self.meta["n_captive"], "delta", delta

            self.meta["n_captive"] += delta;

            if not (self.meta["n_captive"] >= 0):
                raise AssertionError("negative captive size: " + self.name + str(self.meta))


    def execute (self, game):
        """
        select a play and execute the strategy for it
        """

        card = self.pick_card()
        card.execute(game, self, self.opponent)


    def record_loss (self, delta, population, action):
        """
        record a loss in terms of impact on a given population, due to a specified action
        """

        self.meta["loss"].append([int(delta), self.meta[population], action])


class Founder (Player):
    """
    representation for the player on the Founders side
    """

    def __init__ (self):
        Player.__init__(self, "Founder", INIT_FORCE, "Occupy", "Hospitalized")

        self.add_card(ForceReductionCard("wounded in Friendly-Fire"), 10)
        self.add_card(ConversionCard("converted by Temple Prostitutes"), 2)
        self.add_card(InsurrectionCard("overcrowding leads to Jail Break"), 1)
        self.add_card(SeriouslyWeirdCard("bear the wrath of the Flying Spaghetti Monster"), 1)


class Fellows (Player):
    """
    representation for the player on the Fellowship side
    """

    def __init__ (self):
        Player.__init__(self, "Fellows", INIT_FORCE, "Police", "Incarcerated")

        self.add_card(ForceReductionCard("arrested for Domestic Terrorism"), 10)
        self.add_card(SeriouslyWeirdCard("witness the Resurrection of Ronald Reagan"), 1)


class GameIterator:
    """
    representation for a game iterator
    """

    game_dict = {}


    def __init__ (self, game):
        """
        initialize a game iterator, based on the UUID
        """

        self.uuid = game.uuid
        self.game_dict[self.uuid] = game


    def next (self):
        """
        iterate to run game until end
        """

        if not self.uuid in self.game_dict:
            raise StopIteration
        else:
            outcome = self.game_dict[self.uuid].play_duplex()

            if outcome["game_over"]:
                del self.game_dict[self.uuid]

            return outcome


class Game:
    """
    representation for the game state
    """

    def __init__ (self, name, sim=None):
        """
        initialize a game with two players and run until end
        """

        self.name = name
        self.uuid = str(uuid.uuid1())
        self.iterator = GameIterator(self)
        self.conditions = []
        self.outcome = { "game_over": False, "n_turn": 1, "uuid": self.uuid, "name": self.name }

        self.founder = Founder()
        self.fellows = Fellows()

        self.founder.set_opponent(self.fellows)
        self.fellows.set_opponent(self.founder)

        self.sim = sim
        self.last_full_meta = ["0", "0"]


    def __iter__(self):
        return self.iterator


    def play_duplex (self):
        """
        iterate to run game until end
        """

        try:
            if self.outcome["game_over"]:
                raise StopIteration
            elif (self.outcome["n_turn"] <= MAX_TURNS):
                self.attempt_turn()
            else:
                self.conclude()
                self.outcome["game_over"] = True
        except GameOverException, ex:
            self.outcome["end"] = ex.value
            self.outcome["game_over"] = True

        self.outcome[self.founder.name] = self.founder.meta
        self.outcome[self.fellows.name] = self.fellows.meta

        return self.outcome


    def attempt_turn (self):
        """
        advance the game play for one turn
        """

        self.founder.meta["loss"] = []
        self.fellows.meta["loss"] = []

        ## advance to next turn

        if self.founder.has_play():
            self.founder.execute(self)

        if self.fellows.has_play():
            self.fellows.execute(self)

        ## test for the end conditions

        for func in self.conditions:
            func()

        self.outcome["n_turn"] += 1


    def prevent_draw (self):
        """
        ensure no more than N turns without change before Status Quo prevails
        """

        full_meta = str(self.founder.meta) + str(self.fellows.meta)

        if len(filter(lambda x: full_meta != x, self.last_full_meta)) == 0:
            self.game_over(self.fellows, "stalemate")
        else:
            self.last_full_meta.append(full_meta)
        
            if len(self.last_full_meta) > LEN_STALEMATE:
                self.last_full_meta = self.last_full_meta[0:LEN_STALEMATE]


    def conclude (self):
        """
        no cards left; force a terminating condition
        """

        if self.outcome["n_turn"] >= MAX_TURNS:
            self.game_over(self.fellows, "status quo")
        elif self.founder.meta["n_forces"] > self.fellows.meta["n_forces"]:
            self.game_over(self.founder, "both ran out of cards")
        elif self.fellows.meta["n_forces"] > self.founder.meta["n_forces"]:
            self.game_over(self.fellows, "both ran out of cards")
        else:
            self.game_over(self.fellows, "status quo")


    def game_over (self, winner, condition):
        """
        winning condition terminates game
        """

        self.sim.tally(winner)

        loser = winner.opponent
        margin = winner.meta["n_forces"] - loser.meta["n_forces"]
        stats = { "condition": condition, "winner": winner.name, "margin": int(margin) }

        raise GameOverException(stats)


class TBOO_Game (Game):
    """
    representation for the Battle of Oakland game 
    """

    def __init__ (self, sim=None):
        Game.__init__(self, "The Battle Of Oakland", sim)

        self.conditions.append(self.simulate_jail)
        self.conditions.append(self.simulate_hospital)
        self.conditions.append(self.prevent_draw)


    def simulate_jail (self):
        """
        model for the minimum number of Fellowship jail staff needed
        """

        n_reserve = self.fellows.calc_reserve()

        if n_reserve > self.fellows.meta["n_forces"]:
            ## DICE: d10/10, >0

            ROLL_AMNESTY = 0.0
            roll = roll_dice10() / 10.0

            if roll > ROLL_AMNESTY:
                delta = round(roll * self.fellows.meta["n_captive"], 0)
                self.fellows.record_loss(delta, "captive_name", "JAIL AMNESTY!")
                self.fellows.add_captive(self, -delta)
                self.founder.add_forces(self, delta)

        self.fellows.meta["n_reserve"] = min(n_reserve, self.fellows.meta["n_forces"])
        self.fellows.meta["n_deploy"] = self.fellows.meta["n_forces"] - self.fellows.meta["n_reserve"]


    def simulate_hospital (self):
        """
        model for the minimum number of Founders hospital staff needed
        """

        n_reserve = self.founder.calc_reserve()
        self.fellows.meta["enraged"] = False

        if n_reserve > self.founder.meta["n_forces"]:
            ## DICE: d10, >6

            ROLL_RAGE = 6
            roll = roll_dice10()

            if roll > ROLL_RAGE:
                self.founder.record_loss(0, "captive_name", "RIOT COP RAGE!")
                self.fellows.meta["enraged"] = True

        self.founder.meta["n_reserve"] = min(n_reserve, self.founder.meta["n_forces"])
        self.founder.meta["n_deploy"] = self.founder.meta["n_forces"] - self.founder.meta["n_reserve"]


class Simulation:
    """
    representation for the game simulation
    """

    def __init__ (self, max_iterations=20):
        self.max_iterations = max_iterations
        self.win_tally = { "Founder": 0, "Fellows": 0 }


    def simulate (self):
        """
        iterate through N games to collect statistics
        """
        
        for i in range(0, self.max_iterations):
            for outcome in TBOO_Game(sim):
                if debug:
                    print json.dumps(outcome)


    def tally (self, winner):
        """
        tally counts for winning players
        """

        self.win_tally[winner.name] += 1


    def report (self):
        """
        report summary statistics for the simulation
        """

        print self.win_tally["Founder"] / float(self.max_iterations)


######################################################################
## command line interface

if __name__ == "__main__":
    sim = Simulation()
    sim.simulate()
    sim.report()
