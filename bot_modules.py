"""
Twitch IRC Chatbot - Modules
Contains the class where advanced functions for the bot to use are kept.

author: brendanmoore42@github.com
date: June 2023
"""
import os, glob, json, time, random
import irc.bot
import datetime
import markovify
import numpy as np
import pandas as pd

"""
# First time set up for this module requires the vader sentiment to be downloaded first,
# simply un-comment the following lines then re-comment this block to use package.
import ssl
import nltk
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('vader_lexicon')
"""
from nltk.sentiment.vader import SentimentIntensityAnalyzer

"""Poker/Deuces Package:
Needs to be updated to python 3, package in repo works but pip install will break"""


pd.set_option("display.max_columns", None)
pd.options.mode.chained_assignment = None

class Alfred:
    def __init__(self, iters=100, memory=False, emoji_list=None):
        """Main personality will be Alfred, Bruce Wayne's Butler"""
        self.iters = iters  # number of iterations in Markov chains to generate new phrases
        self.memory = memory  # .csv filepath
        self.df_memory = []  # games database
        self.emoji_list = emoji_list  # import list of emojis that can be used

        self.temp_output = []
        self.vdr = SentimentIntensityAnalyzer()

    def add_player(self, game, user):
        """Adds player to game database"""

        if game == "poker":
            if any(user.lower() in s.lower() for s in self.df_memory["name"].tolist()):
                pass
            else:
                user = [game, user, 0, 0, 0]
                self.df_memory = self.df_memory.append(pd.Series(user, index=self.df_memory.columns), ignore_index=True)

    def check_poker_player(self, user):
        if any(user.lower() in s.lower() for s in self.df_memory["name"].tolist()):
            return True
        else:
            return False

    def play_poker(self, player):
        """Poker/Deuces Package: Needs to be updated to python 3, package in this works,
         but pip install is broken"""
        # from deuces.card import Card
        # from deuces.deckimport Deck
        # from deuces.evaluator import Evaluator

        # Check player in database
        self.add_player(player)

        # Create deck, export game
        # deck = Deck()
        # dealer = Evaluator()
        # board = deck.draw(5)
        # player1 = deck.draw(2)
        # player2 = deck.draw(2)
        # hands = [player1, player2]
        # game_info = dealer.hand_summary(board, hands)
        # cards = [Card.print_pretty_cards(board), Card.print_pretty_cards(player1), Card.print_pretty_cards(player2)]
        #
        # return game_info, cards

    def remember_chat(self, channel, log, today):
        """Save the chat to memory"""
        pass

    def rig_deck(self):
        """Rigs the poker deck"""
        # Just kidding

    def send_emoji(self, num="random"):
        """Sends random number of set emojies, or if unspecified, random amount"""
        if num == "random":
            random_num = random.randint(1, 8)
            return random.choice(self.emoji_list) * random_num
        else:
            return random.choice(self.emoji_list) * num


    def speak(self, emotion=None):
        """Intakes an emotion and outputs a phrase"""
        if not emotion:
            emotion = random.choice(["happy", "sass", "support"])
        if emotion == "happy":
            return ":)"
        if emotion == "sass":
            return "omg"
        if emotion == "support":
            return "GGs"