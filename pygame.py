#!/usr/bin/env python
# encoding: utf-8

# by Liber 118
# http://liber118.com/
# licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License
# http://creativecommons.org/licenses/by-sa/3.0/


import json
import random
import re
import sys
import uuid


######################################################################
## global variables and utility methods
      
debug = True # False

def verify_move (pt0, pt1):
    """
    verify that a move from one hex to another is valid
    """

    (x0, y0) = map(lambda x: int(x), pt0.split(","))
    (x1, y1) = map(lambda x: int(x), pt1.split(","))

    if (abs(x0 - x1) == abs(y0 - y1)):
        # valid diagonal move
        return True
    elif ((x0 == x1) and (abs(y0 - y2) == 2)):
        # valid vertical move
        return True
    else:
        return False


def roll_dice (notation):
    """
    simulate a dice roll, based on the given notation
    """

    base = None
    roll, cond = notation.split(", ")

    p = re.compile("^d(\d+)(.*)$")
    m = p.match(roll)

    if m:
        die_count = int(m.group(1))
        base = random.randint(0, die_count)

        for op in re.findall("[\-\+\*\/]\d+", m.group(2)):
            base = eval("%f %s %s" % (base, op[0], op[1:]))

    accepted = eval("%f %s" % (base, cond))

    return base, accepted


######################################################################
## class definitions

class GameOverException (Exception):

    def __init__(self, value):
        self.value = value


    def __str__(self):
        return repr(self.value)


class Condition:
    """
    representation for a condition to test in the simulation
    """

    def __init__ (self, notation=None):
        self.notation = notation


    def execute (self, game, us, them):
        if debug:
            print "nop"


class PreventDraw (Condition):
    def __init__(self, notation):
        Condition.__init__(self, notation)


    def execute (self, game, us, them):
        """
        ensure that no more than N turns occur without change,
        otherwise the Status Quo prevails
        """

        meta_0 = json.dumps(us.meta)
        meta_1 = json.dumps(them.meta)

        unmeta_0 = json.loads(meta_0)
        len_log_0 = len(filter(lambda x: len(x) < 1, unmeta_0["log"]))
        del unmeta_0["log"]

        unmeta_1 = json.loads(meta_1)
        len_log_1 = len(filter(lambda x: len(x) < 1, unmeta_1["log"]))
        del unmeta_1["log"]

        full_meta = str(unmeta_0) + str(unmeta_1)

        if len(filter(lambda x: full_meta != x, game.last_full_meta)) == 0:
            game.game_over(them, "stalemate")
        elif (len_log_0 > game.outcome["len_stalemate"]) or (len_log_1 > game.outcome["len_stalemate"]):
            game.game_over(them, "stalemate")
        else:
            game.last_full_meta.append(full_meta)
        
            if len(game.last_full_meta) > game.outcome["len_stalemate"]:
                game.last_full_meta = game.last_full_meta[0:game.outcome["len_stalemate"]]


class SimulateJail (Condition):
    def __init__(self, notation):
        Condition.__init__(self, notation)


    def execute (self, game, us, them):
        """
        model for the minimum number of Fellowship jail staff needed
        """

        n_reserve = us.calc_reserve()

        if n_reserve > us.meta["n_forces"]:
            roll, accepted = roll_dice(self.notation)

            if accepted:
                delta = round(roll * us.meta["n_captive"], 0)
                us.log_event(delta, "captive_state", "JAIL AMNESTY!")
                us.add_captive(game, -delta)
                them.add_forces(game, delta)

        us.meta["n_reserve"] = min(n_reserve, us.meta["n_forces"])
        us.meta["n_deployed"] = us.meta["n_forces"] - us.meta["n_reserve"]


class SimulateHospital (Condition):
    def __init__(self, notation):
        Condition.__init__(self, notation)


    def execute (self, game, us, them):
        """
        model for the minimum number of Founders hospital staff needed
        """

        n_reserve = us.calc_reserve()
        them.meta["rage"] = 0.0

        if n_reserve > us.meta["n_forces"]:
            roll, accepted = roll_dice(self.notation)

            if accepted:
                us.log_event(0, "captive_state", "RIOT COP RAGE!")
                them.meta["rage"] += 0.2

        us.meta["n_reserve"] = min(n_reserve, us.meta["n_forces"])
        us.meta["n_deployed"] = us.meta["n_forces"] - us.meta["n_reserve"]


class Card (Condition):
    """
    representation for a generic card in the deck
    """

    def __init__ (self, event, notation, retry=False):
        Condition.__init__(self, notation)
        self.event = event
        self.retry = retry


class ForceReductionCard (Card):
    """
    representation for a 'force reduction' card in the deck
    """

    def __init__ (self, event, notation, retry=False):
        Card.__init__(self, event, notation, retry)


    def execute (self, game, us, them):
        roll, accepted = roll_dice(self.notation)

        if accepted:
            delta = round(roll * us.meta["n_deployed"], 0)

            if us.meta["rage"] > 0.5:
                REDUCE_FACTOR = 5.0
                casualty = round(roll / REDUCE_FACTOR * delta, 0)

                if debug:
                    print them.meta["side"], ":", "CASUALTY", casualty

                delta -= casualty
                them.log_event(casualty, "forces_name", "casualties")
                them.meta["n_casualty"] += casualty

            them.log_event(delta, "forces_name", self.event)
            us.add_captive(game, delta)
            them.add_forces(game, -delta)


class InsurrectionCard (Card):
    """
    representation for an 'insurrection' card in the deck
    """

    def __init__ (self, event, notation, retry=False):
        Card.__init__(self, event, notation, retry)


    def execute (self, game, us, them):
        roll, accepted = roll_dice(self.notation)

        if accepted:
            delta = round(roll * them.meta["n_captive"], 0)

            if debug:
                print "exec insurrect", them.meta["n_captive"], "delta", delta

            INSURRECT_FACTOR = 10.0

            if delta > (them.meta["init_force"] / INSURRECT_FACTOR):
                them.log_event(delta, "forces_name", self.event)
                them.add_captive(game, -delta)
                us.add_forces(game, delta)


class ConversionCard (Card):
    """
    representation for a 'conversion' card in the deck
    """

    def __init__ (self, event, notation, retry=False):
        Card.__init__(self, event, notation, retry)


    def execute (self, game, us, them):
        roll, accepted = roll_dice(self.notation)

        if accepted:
            delta = round(roll * them.meta["n_forces"], 0)

            them.log_event(delta, "forces_name", self.event)
            them.add_forces(game, -delta)
            us.add_forces(game, delta)


class SeriouslyWeirdCard (Card):
    """
    representation for a 'seriously weird' card in the deck
    """

    def __init__ (self, event, notation, retry=False):
        Card.__init__(self, event, notation, retry)


    def execute (self, game, us, them):
        roll, accepted = roll_dice(self.notation)

        if accepted:
            delta = round(roll * them.meta["n_forces"], 0)
            them.log_event(delta, "forces_name", self.event)
            them.add_forces(game, -delta)


class WinningPlayCard (Card):
    """
    representation for a 'winning play' card in the deck
    """

    def __init__ (self, event, notation, retry=False):
        Card.__init__(self, event, notation, retry)

    def execute (self, game, us, them):
        roll, accepted = roll_dice(self.notation)

        if accepted:
            print "WINNING PLAY"


class Player:
    """
    representation for a player in the game
    """

    def __init__ (self, meta, game):
        """
        initialize
        """

        self.meta = meta
        self.opponent = None
        self.meta["log"] = []

        self.meta["init_force"] = self.count_force(game)
        self.meta["n_forces"] = self.meta["init_force"]
        self.meta["n_deployed"] = self.meta["init_force"]

        self.meta["n_captive"] = 0
        self.meta["n_reserve"] = 0
        self.meta["n_casualty"] = 0

        # populate conditions in the simulation

        self.conditions = []

        for cond_conf in self.meta["conditions"]:
            cond_raw = "".join([cond_conf["kind"], '("', cond_conf["dice"], '")'])
            cond = eval(cond_raw)
            self.conditions.append(cond)

        del self.meta["conditions"]

        # populate cards in the deck

        self.deck = []

        for card_conf in self.meta["cards"]:
            card_raw = "".join([card_conf["kind"], '("', card_conf["event"], '", "', card_conf["dice"], '", ', card_conf["retry"], ')'])
            card = eval(card_raw)

            for i in range(0, card_conf["num"]):
                self.deck.append(card)

        del self.meta["cards"]


    def set_opponent (self, opponent):
        self.opponent = opponent


    def count_force (self, game):
        """
        count this player's forces, distributed across the map
        """

        n_forces = 0

        for geo, hex in game.outcome["map"].items():
            n_forces += hex["force"][self.meta["index"]]

        return n_forces


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

        if not card.retry:
            self.deck.remove(card)

        return card


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


    def log_event (self, delta, population, event):
        """
        record a loss in terms of impact on a given population, due to a specified event
        """

        log_entry = [int(delta), self.meta[population], event]
        
        if debug:
            print log_entry

        self.meta["log"][-1].append(log_entry)


class GameIterator:
    """
    representation for a game iterator
    """

    game_dict = {}


    def __init__ (self, game):
        """
        initialize a game iterator, based on the UUID
        """

        self.game = game
        self.uuid = game.outcome["uuid"]
        self.game_dict[self.uuid] = game


    def next (self):
        """
        iterate to run game until its end
        """

        if not self.uuid in self.game_dict:
            raise StopIteration
        else:
            outcome = self.game_dict[self.uuid].play_duplex()

            if outcome["game_over"]:
                del self.game_dict[self.uuid]

            return self.game, outcome


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

        self.founder = Player(self.outcome["player0"], self)
        self.fellows = Player(self.outcome["player1"], self)

        self.founder.set_opponent(self.fellows)
        self.fellows.set_opponent(self.founder)

        del self.outcome["player0"]
        del self.outcome["player1"]

        self.sim = sim
        self.last_full_meta = ["0", "0"]


    def __iter__(self):
        return GameIterator(self)


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

        self.outcome[self.founder.meta["index"]] = self.founder.meta
        self.outcome[self.fellows.meta["index"]] = self.fellows.meta

        return self.outcome


    def attempt_turn (self):
        """
        advance the game play for one turn
        """

        self.founder.count_force(self)
        self.fellows.count_force(self)

        self.founder.meta["log"].append([])
        self.fellows.meta["log"].append([])

        ## advance to next turn

        if self.founder.has_play():
            self.founder.execute(self)

        if self.fellows.has_play():
            self.fellows.execute(self)

        ## test for the end conditions

        for cond in self.fellows.conditions:
            cond.execute(self, self.fellows, self.founder)

        for cond in self.founder.conditions:
            cond.execute(self, self.founder, self.fellows)

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

        self.sim.tally(self.founder)

        loser = winner.opponent
        margin = winner.meta["n_forces"] - loser.meta["n_forces"]
        stats = { "condition": condition, "winner": winner.meta["side"], "margin": int(margin) }

        raise GameOverException(stats)


    def report (self, outcome):
        """
        print a text report of the game outcome
        """

        print "n_turn", outcome["n_turn"]
        print json.dumps(outcome["0"])
        print json.dumps(outcome["1"])

        if "end" in outcome:
            print json.dumps(outcome['end'])

        #print outcome.keys()
        #print json.dumps(outcome)


class Simulation:
    """
    representation for the game simulation
    """

    def __init__ (self, file_conf, max_iterations):
        self.file_conf = file_conf
        self.max_iterations = max_iterations
        self.win_tally = { "0": 0, "1": 0 }


    def simulate (self):
        """
        iterate through N games to collect statistics
        """
        
        for i in range(0, self.max_iterations):
            for game, outcome in Game(file_conf, sim):
                if debug:
                    game.report(outcome)


    def tally (self, winner):
        """
        tally counts for winning players
        """

        self.win_tally[winner.meta["index"]] += 1


    def report (self):
        """
        report summary statistics for the simulation
        """

        print self.win_tally["0"] / float(self.max_iterations)


######################################################################
## command line interface

if __name__ == "__main__":
    file_conf = sys.argv[1]
    max_iterations = int(sys.argv[2])

    sim = Simulation(file_conf, max_iterations)

    sim.simulate()
    sim.report()
