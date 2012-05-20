#!/usr/bin/env python
# encoding: utf-8

import json
import random
import sys
import uuid


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

    def __init__ (self, event, replace=False):
        self.event = event
        self.replace = replace


    def execute (self, game, us, them):
        if debug:
            print "nop"


class ForceReductionCard (Card):
    """
    representation for a 'force reduction' card in the deck
    """

    def __init__ (self, event, replace=False):
        Card.__init__(self, event, replace)


    def execute (self, game, us, them):
        ## DICE: d10+1/20

        IMPACT_FACTOR = 20.0
        roll = (roll_dice10() + 1.0) / IMPACT_FACTOR
        delta = round(roll * us.meta["n_deploy"], 0)

        if us.meta["enraged"]:
            REDUCE_FACTOR = 5.0
            casualty = round(roll / REDUCE_FACTOR * delta, 0)

            if debug:
                print them.meta["side"], ":", "CASUALTY", casualty

            delta -= casualty
            them.record_loss(casualty, "forces_name", "casualties")
            them.meta["n_casualty"] += casualty

        them.record_loss(delta, "forces_name", self.event)
        us.add_captive(game, delta)
        them.add_forces(game, -delta)


class InsurrectionCard (Card):
    """
    representation for an 'insurrection' card in the deck
    """

    def __init__ (self, event, replace=False):
        Card.__init__(self, event, replace)


    def execute (self, game, us, them):
        ## DICE: d10/10

        roll = roll_dice10() / 10.0
        delta = round(roll * them.meta["n_captive"], 0)

        if debug:
            print "exec insurrect", them.meta["n_captive"], "delta", delta

        INSURRECT_FACTOR = 10.0

        if delta > (them.meta["init_force"] / INSURRECT_FACTOR):
            them.record_loss(delta, "forces_name", self.event)
            them.add_captive(game, -delta)
            us.add_forces(game, delta)


class ConversionCard (Card):
    """
    representation for a 'conversion' card in the deck
    """

    def __init__ (self, event, replace=False):
        Card.__init__(self, event, replace)


    def execute (self, game, us, them):
        ## DICE: d10/10, >0

        ROLL_CONVERT = 0.0
        roll = roll_dice10() / 10.0

        if roll > ROLL_CONVERT:
            delta = round(roll * them.meta["n_forces"], 0)

            them.record_loss(delta, "forces_name", self.event)
            them.add_forces(game, -delta)
            us.add_forces(game, delta)


class SeriouslyWeirdCard (Card):
    """
    representation for a 'seriously weird' card in the deck
    """

    def __init__ (self, event, replace=False):
        Card.__init__(self, event, replace)


    def execute (self, game, us, them):
        ## DICE: d10/10, >1

        ROLL_WEIRD = 1.0

        roll = roll_dice10() / 10.0

        if roll > ROLL_WEIRD:
            delta = round(roll * them.meta["n_forces"], 0)
            them.record_loss(delta, "forces_name", self.event)
            them.add_forces(game, -delta)


class Player:
    """
    representation for a player in the game
    """

    def __init__ (self, meta):
        """
        initialize
        """

        self.meta = meta
        self.opponent = None
        self.meta["log"] = []
        self.conditions = []

        self.meta["n_forces"] = self.meta["init_force"]
        self.meta["n_deploy"] = self.meta["init_force"]
        self.meta["n_captive"] = 0
        self.meta["n_reserve"] = 0
        self.meta["n_casualty"] = 0

        self.meta["enraged"] = False
        self.meta["has_comm"] = True

        # populate cards in the deck

        self.deck = []

        for card_conf in self.meta["cards"]:
            card = eval("".join([card_conf["kind"], '("', card_conf["event"], '")']))

            for i in range(0, card_conf["num"]):
                self.deck.append(card)

        del self.meta["cards"]


    def set_opponent (self, opponent):
        self.opponent = opponent


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


    def simulate_jail (self, game, us, them):
        """
        model for the minimum number of Fellowship jail staff needed
        """

        n_reserve = us.calc_reserve()

        if n_reserve > us.meta["n_forces"]:
            ## DICE: d10/10, >0

            ROLL_AMNESTY = 0.0
            roll = roll_dice10() / 10.0

            if roll > ROLL_AMNESTY:
                delta = round(roll * us.meta["n_captive"], 0)
                us.record_loss(delta, "captive_state", "JAIL AMNESTY!")
                us.add_captive(game, -delta)
                them.add_forces(game, delta)

        us.meta["n_reserve"] = min(n_reserve, us.meta["n_forces"])
        us.meta["n_deploy"] = us.meta["n_forces"] - us.meta["n_reserve"]


    def simulate_hospital (self, game, us, them):
        """
        model for the minimum number of Founders hospital staff needed
        """

        n_reserve = us.calc_reserve()
        them.meta["enraged"] = False

        if n_reserve > us.meta["n_forces"]:
            ## DICE: d10, >6

            ROLL_RAGE = 6
            roll = roll_dice10()

            if roll > ROLL_RAGE:
                us.record_loss(0, "captive_state", "RIOT COP RAGE!")
                them.meta["enraged"] = True

        us.meta["n_reserve"] = min(n_reserve, us.meta["n_forces"])
        us.meta["n_deploy"] = us.meta["n_forces"] - us.meta["n_reserve"]


    def prevent_draw (self, game, us, them):
        """
        ensure that no more than N turns occur without change,
        otherwise the Status Quo prevails
        """

        full_meta = str(us.meta) + str(them.meta)

        if len(filter(lambda x: full_meta != x, game.last_full_meta)) == 0:
            game.game_over(them, "stalemate")
        else:
            game.last_full_meta.append(full_meta)
        
            if len(game.last_full_meta) > game.outcome["len_stalemate"]:
                game.last_full_meta = game.last_full_meta[0:game.outcome["len_stalemate"]]


    def calc_reserve (self):
        """
        calculate the required reserves
        """

        MIN_RESERVE = 2.0
        RESERVE_RATIO = 0.05

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
                raise AssertionError("negative forces size: " + self.meta["side"] + str(self.meta))


    def add_captive (self, game, delta):
        if delta != 0.0:
            if debug:
                print "add_captive", self.meta["n_captive"], "delta", delta

            self.meta["n_captive"] += delta;

            if not (self.meta["n_captive"] >= 0):
                raise AssertionError("negative captive size: " + self.meta["side"] + str(self.meta))


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

        self.meta["log"][-1].append([int(delta), self.meta[population], action])


class GameIterator:
    """
    representation for a game iterator
    """

    game_dict = {}


    def __init__ (self, game):
        """
        initialize a game iterator, based on the UUID
        """

        self.uuid = game.outcome["uuid"]
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

    def __init__ (self, file_conf, sim=None):
        """
        initialize a game with two players and run until end
        """

        with open(file_conf, "r") as f:
            self.outcome = json.load(f)

        self.outcome["n_turn"] = 1
        self.outcome["game_over"] = False

        self.outcome["uuid"] = str(uuid.uuid1())
        self.iterator = GameIterator(self)

        self.founder = Player(self.outcome["player0"])
        self.fellows = Player(self.outcome["player1"])

        self.founder.set_opponent(self.fellows)
        self.fellows.set_opponent(self.founder)

        del self.outcome["player0"]
        del self.outcome["player1"]

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
            elif (self.outcome["n_turn"] <= self.outcome["max_turns"]):
                self.attempt_turn()
            else:
                self.conclude()
                self.outcome["game_over"] = True
        except GameOverException, ex:
            self.outcome["end"] = ex.value
            self.outcome["game_over"] = True

        self.outcome[self.founder.meta["side"]] = self.founder.meta
        self.outcome[self.fellows.meta["side"]] = self.fellows.meta

        return self.outcome


    def attempt_turn (self):
        """
        advance the game play for one turn
        """

        self.founder.meta["log"].append([])
        self.fellows.meta["log"].append([])

        ## advance to next turn

        if self.founder.has_play():
            self.founder.execute(self)

        if self.fellows.has_play():
            self.fellows.execute(self)

        ## test for the end conditions

        for func in self.founder.conditions:
            func(self, self.founder, self.fellows)

        for func in self.fellows.conditions:
            func(self, self.fellows, self.founder)

        self.outcome["n_turn"] += 1


    def conclude (self):
        """
        no cards left; force a terminating condition
        """

        if self.outcome["n_turn"] >= self.outcome["max_turns"]:
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

        self.sim.tally(self.founder == winner)

        loser = winner.opponent
        margin = winner.meta["n_forces"] - loser.meta["n_forces"]
        stats = { "condition": condition, "winner": winner.meta["side"], "margin": int(margin) }

        raise GameOverException(stats)


class TBOO_Game (Game):
    """
    representation for the Battle of Oakland game 
    """

    def __init__ (self, file_conf, sim=None):
        Game.__init__(self, file_conf, sim)

        self.fellows.conditions.append(self.fellows.simulate_jail)
        self.founder.conditions.append(self.founder.simulate_hospital)
        self.founder.conditions.append(self.founder.prevent_draw)


class Simulation:
    """
    representation for the game simulation
    """

    def __init__ (self, file_conf, max_iterations=20):
        self.file_conf = file_conf
        self.max_iterations = max_iterations
        self.win_tally = { "0": 0, "1": 0 }


    def simulate (self):
        """
        iterate through N games to collect statistics
        """
        
        for i in range(0, self.max_iterations):
            for outcome in TBOO_Game(file_conf, sim):
                if debug:
                    print json.dumps(outcome)


    def tally (self, player0_wins):
        """
        tally counts for winning players
        """

        if player0_wins:
            self.win_tally["0"] += 1
        else:
            self.win_tally["1"] += 1


    def report (self):
        """
        report summary statistics for the simulation
        """

        print self.win_tally["0"] / float(self.max_iterations)


######################################################################
## command line interface

if __name__ == "__main__":
    file_conf = sys.argv[1]
    sim = Simulation(file_conf)

    sim.simulate()
    sim.report()
