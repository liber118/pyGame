#!/usr/bin/env python
# encoding: utf-8

# example Python code - plays "tic tac toe"
# author: Paco Xander Nathan <pacoid@cs.stanford.edu>
# license: Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# http://creativecommons.org/licenses/by-sa/3.0/


import logging
import sys
import unittest


class TestChooseMoves (unittest.TestCase):
    """unit tests for AI"""

    def setUp (self):
        self.t3 = TicTacToe()


    def test_ai_wins (self):
        """force a condition where the AI should win this turn"""

        self.t3.board = ['O', 'X', ' ', 'X', 'O', ' ', ' ', ' ', ' ']
        you_win, game_over, stimulus_ai = self.t3.player_takes_turn(6, 'X', 'O')

        self.assertFalse(you_win)
        self.assertTrue(game_over)


    def test_player_wins (self):
        """force a condition where the player should win this turn"""

        self.t3.board = ['O', 'X', ' ', 'O', 'X', ' ', ' ', ' ', ' ']
        you_win, game_over, stimulus_ai = self.t3.player_takes_turn(7, 'X', 'O')

        self.assertTrue(you_win)
        self.assertTrue(game_over)


class T3_UI:
    """default class for UI definitions"""

    def show_message (self, message=None):
        """output a message to the player"""

        # very simple text-based UI on stdout, but override for
        # integration with a client, etc.

        if message:
            print message
        else:
            print


    def display_board (self, prompt, t3):
        """display the current state of the board"""

        self.show_message(prompt)
        self.show_message(t3.header_text)

        for i in range(0, t3.max_index, t3.board_size):
            board_elem = t3.board[i:(i + t3.board_size)]
            moves_elem = t3.moves[i:(i + t3.board_size)]

            self.show_message("|".join(board_elem) + t3.SPACE + "|".join(moves_elem))


    def prompt_input (self, prompt_text):
        """prompt for a line of input from the player"""

        return raw_input(prompt_text)


class T3_AI:
    """default class for AI definitions"""

    def choose_move (self, marks, span, player, t3):
        """choose the next best move for the AI"""

        move = None

        # NB: this is not particularly greedy, just follows the rules
        # naively... however, this method is where prioritizing the
        # center and corners could come in handy

        for j in range(0, t3.span_length):
            if marks[0][j] == t3.BLANK:
                move = span[0][j]
                t3.board[move] = player
                break

        t3.logger.debug(str(("MOVE", player, move)))

        # example assertion -- even though it's overly simplistic...
        # if this class was used in a UI client, an error would likely
        # be posted via a remote crash reporter, or if this was
        # running on server-side it would probably be posted onto some
        # notification service

        assert move >= 0, "No move possible given state %s" % str(marks)

        return move


    def ai_takes_turn (self, best_you_count, best_you_marks, best_you_span, other, t3):
        """determine strategy for the AI to play a turn"""

        game_over = True
        stimulus_ai = t3.stalemate_text

        # by default, the game becomes a stalemate..
        # but let's determine if it's in another state

        best_ai_count, best_ai_marks, best_ai_span = t3.get_best_span(other)

        t3.logger.debug(str(("BEST", other, best_ai_count, best_ai_marks, best_ai_span)))

        if best_you_count > best_ai_count:
            # player blocks the AI
            t3.logger.debug(str(("BLOCK", best_you_span)))

            move = self.choose_move(best_you_marks, best_you_span, other, t3)
            game_over = False
            stimulus_ai = t3.describe_move(move, t3.ai_puts_text)

        elif best_ai_marks:
            # AI has a possible move and seizes the lead
            t3.logger.debug(str(("SEIZE", best_ai_span)))

            move = self.choose_move(best_ai_marks, best_ai_span, other, t3)

            if best_ai_count == (t3.span_length - 1):
                # AI wins the game
                game_over = True
                stimulus_ai = t3.describe_move(move, t3.ai_wins_text)
            else:
                # game continues
                game_over = False
                stimulus_ai = t3.describe_move(move, t3.ai_puts_text)

        return game_over, stimulus_ai


    def analyze_board (self, player, other, t3):
        """analyze the board to select the best next move for the AI"""

        you_win = False
        game_over = False
        stimulus_ai = None

        # evaluate the player's move
        best_you_count, best_you_marks, best_you_span = t3.get_best_span(player)

        t3.logger.debug(str(("BEST", player, best_you_count, best_you_marks, best_you_span)))

        if best_you_count == t3.span_length:
            # player wins the game
            you_win = True
            game_over = True
            stimulus_ai = t3.you_win_text

        else:
            # AI takes a turn
            game_over, stimulus_ai = self.ai_takes_turn(best_you_count, best_you_marks, best_you_span, other, t3)

        return you_win, game_over, stimulus_ai


class TicTacToe:
    """represents the game board for tic-tac-toe"""

    SPACE = "\t\t"
    BLANK = " "
    X_MARK = "X"
    O_MARK = "O"


    def __init__ (self, board_size=3, span_length=3, ui_class=T3_UI, ai_class=T3_AI, log_file="t3.log", log_level=logging.WARNING):
        """set board dimensions, rules of play, UI, AI, logging, text descriptions, etc., for the game"""

        self.board_size = board_size
        self.span_length = span_length
        self.ui = ui_class()
        self.ai = ai_class()

        self.max_index = self.board_size ** 2
        self.board = map(lambda x: self.BLANK, range(0, self.max_index))
        self.moves = map(lambda x: str(x + 1), range(0, self.max_index))

        # set up logging

        self.logger = logging.getLogger("t3")
        hdlr = logging.FileHandler(log_file)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr) 
        self.logger.setLevel(log_level)

        # all text output was refactored to be here, which could be
        # replaced by a config file, e.g., for internationalization

        self.welcome_text = "Welcome to Tic-Tac-Toe. Please make your move selection by entering a number 1-%d corresponding to the movement key on the right." % self.max_index
        self.header_text = "\nBoard:" + self.SPACE + "Movement Key:"
        self.input_text = "\nWhere to? "
        self.help_text = "Please enter a number 1-%d. Or type 'quit' to leave. Beware the Grue!!!" % self.max_index
        self.used_text = "You cannot move there, that square is already taken. Just be glad that you did not type 'xyzzy'."
        self.you_put_text = "You have put an " + self.X_MARK + " in the %s."
        self.ai_puts_text = "I put an " + self.O_MARK + " in the %s."
        self.xyzzy_text = "xyzzy"
        self.nothing_text = "Nothing happens."
        self.you_win_text = "You have beaten my poor AI!"
        self.ai_wins_text = "So I moved to the %s. Which you, my protoplasmic friend, perhaps could not forsee as a winning play. Just like Watson on Jeopardy.. AI FTW!"
        self.stalemate_text = "Shall we play another game, or would that violate DNA union rules?"
        self.terminate_text = "Bye, see ya. Be sure not to get lost in a twisty maze of passages, all alike."

        self.positions = ["upper left", "upper center", "upper right", "middle left", "center", "middle right", "lower left", "lower center", "lower right"]
        self.quit_list = ["q", "quit", "done", "bye"]


    def index2xy (self, move):
        """map from a board index to (x, y) coordinates"""

        x = move % self.board_size
        y = move / self.board_size

        return x, y


    def xy2index (self, x, y):
        """map from (x, y) coordinates to a board index"""

        move = (y * self.board_size) + x

        return move


    def terminate (self):
        """terminate the game"""

        self.ui.show_message(self.terminate_text)
        sys.exit(0)


    def get_next_move (self):
        """prompt the player for next move, and repeat until valid input or exit"""

        move = None
        in_loop = True

        while in_loop:
            try:
                # prompt for input based on the movement key
                input_line = self.ui.prompt_input(self.input_text)

                if input_line.lower() in self.quit_list:
                    # player entered a "quit"
                    self.terminate()
                elif input_line.lower() == self.xyzzy_text:
                    # easter egg
                    self.ui.show_message(self.nothing_text)
                    continue

                move = int(input_line)

                if (move < 1) or (move > self.max_index):
                    # invalid input
                    self.ui.show_message(self.help_text)
                else:
                    # at least it's a number...
                    move -= 1

                    if self.board[move] != self.BLANK:
                        # that position is already played
                        self.ui.show_message(self.used_text)
                    else:
                        # success, got a valid input
                        in_loop = False

            except EOFError, err:
                # player terminated input abruptly
                self.ui.show_message()
                self.terminate()
            except ValueError, err:
                # player entered something which was not a number
                self.ui.show_message(self.help_text)
                self.logger.error("ValueError: %(err)s\t%(data)s\n" % {"err": str(err), "data": input})

        return move


    def describe_move (self, move, text_template):
        """format text to describe a move on the board"""

        return text_template % self.positions[move]


    def generate_spans (self):
        """generator for possible spans of moves on the board"""

        for i in range(0, self.max_index):
            for transform in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                # attempt each of four possible transforms to collect a span
                x, y = self.index2xy(i)
                span = [i]

                for j in range(1, self.span_length):
                    # apply next step in the (x, y) transform
                    x += transform[0]
                    y += transform[1]

                    if (x >= 0) and (x < self.board_size) and (y >= 0) and (y < self.board_size):
                        # collect this index into the current span
                        i_trans = self.xy2index(x, y)

                        if i_trans < self.max_index:
                            span.append(i_trans)

                            if len(span) == self.span_length:
                                # success, a valid span
                                yield span


    def generate_scores (self, player):
        """generator for current scores for a given player"""

        for span in self.generate_spans():
            # score the marks already played on this span
            mark_span = [self.board[i] for i in span]
            mark_count = 0
            playable = True

            self.logger.debug(str(("SPAN", player, mark_count, mark_span, span)))

            for mark in mark_span:
                if mark == player:
                    # another mark in this span for the player
                    mark_count += 1
                elif mark != self.BLANK:
                    # at least one mark in this span for the AI
                    playable = False

            if playable:
                # success, this span could be played
                yield (mark_count, mark_span, span)


    def get_best_span (self, player):
        """find the best span for a given player"""

        best_count = 0
        best_marks = None
        best_span = None

        for count, marks, span in self.generate_scores(player):
            # NB: this could grow big, if there was a really large board...
            # so we scan yields from a generator instead of sorting a large list

            self.logger.debug(str(("MARKS", player, count, marks, span)))

            if (not best_span) or (count > best_count):
                # collect the set of potential wins, or best possible next moves
                best_count = count
                best_marks = [marks]
                best_span = [span]

        return best_count, best_marks, best_span


    def player_takes_turn (self, move, player, other):
        """play one turn in the game"""

        self.board[move] = player
        you_win, game_over, stimulus_ai = self.ai.analyze_board(player, other, self)

        # prepare a message to prompt the next turn, if any
        stimulus_you = self.describe_move(move, self.you_put_text)
        stimulus = " ".join((stimulus_you, stimulus_ai))

        return you_win, game_over, stimulus


    def play (self):
        """play the game until reaching a terminating condition"""

        game_over = False
        stimulus = self.welcome_text

        while not game_over:
            self.ui.display_board(stimulus, self)
            move = self.get_next_move()
            you_win, game_over, stimulus = self.player_takes_turn(move, self.X_MARK, self.O_MARK)

        # show the final board state before exit
        self.ui.display_board(stimulus, self)


def main ():
    """parse command line options"""

    # unittest already uses OptionParser, so this is a very simple cmd
    # line option...  in practice, we would fix that to have cmd line
    # parsing here as well

    mode = None

    if len(sys.argv) > 1:
        mode = sys.argv[1]
        del sys.argv[1]

    if mode == "test":
        # run unit tests
        unittest.main()
    else:
        # play the game
        tic_tac = TicTacToe()

        if mode == "debug":
            # increase logging level
            tic_tac.logger.setLevel(logging.DEBUG)

        tic_tac.play()


if __name__ == '__main__':
    main()
