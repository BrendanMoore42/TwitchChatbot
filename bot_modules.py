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

pd.set_option("display.max_columns", None)
pd.options.mode.chained_assignment = None

class Alfred:
    def __init__(self, iters=100, memory=False, emoji_list=None):
        """Main personality will be Alfred, Bruce Wayne's Butler"""
        self.iters = iters  # number of iterations in Markov chains to generate new phrases
        self.memory = memory  # .csv filepath
        self.emoji_list = emoji_list  # import list of emojis that can be used

        self.temp_output = []
        self.vdr = SentimentIntensityAnalyzer()


    def remember_chat(self, channel, log, today):
        """Save the chat to memory"""


    def send_emoji(self, num="random"):
        """Sends random number of set emojies, or if unspecified, random amount"""
        if num == "random":
            random_num = random.randint(1, 8)
            return random.choice(self.emoji_list) * random_num
        else:
            return random.choice(self.emoji_list) * num


    def speak(self, emotion="happy"):
        """Intakes an emotion and outputs a phrase"""
        if emotion == "happy":
            return ":)"
        if emotion == "upset":
            return "omg"