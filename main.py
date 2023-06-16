"""
Twitch IRC Chatbot
A personalized and interactive IRC AI chatbot that can execute commands, plays games,
moderate, answer questions, and much more.
Can be modified for additional tasks and functions.

author: brendanmoore42@github.com
date: June 2023
"""
import os, re, time, random
import irc.bot
import datetime
import wikipedia
from bot_modules import Alfred

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel, mode="normal"):
        self.mode = mode
        self.channel = channel

        # Set up Alfred, or the bots personality class
        self.alf = Alfred(iters=1500, memory="Memory/poker.csv", emoji_list=["CoolCat ", "PlupPls ", "PotFriend "])
        self.start_time = datetime.datetime.now()
        self.follow_reminder = datetime.datetime.now()

        self.chat_logs = []
        self.admin_commands = ["normal", "chill"]

        # Create IRC connection
        server = "irc.chat.twitch.tv"
        port = 6667
        print("Connecting to " + server + " on port " + str(port) + "...")
        # irc.bot.SingleServerIRCBot.__init__(self, [(server, port, "oauth:" + token)], username, username)

    def on_welcome(self, c, e):
        print("Joining " + self.channel)

        # Request specifics before use
        c.cap("REQ", ":twitch.tv/membership")
        c.cap("REQ", ":twitch.tv/tags")
        c.cap("REQ", ":twitch.tv/commands")
        c.join(self.channel)

        # Take a brief second before hopping in
        time.sleep(1)

        if self.mode == "normal":
            today = datetime.datetime.now().strftime("%m_%d_%Y")

            if self.channel[:1] == "[your_channel_or_friends]":
                """When joining a specific channel, specify custom greetings here"""
                c.privmsg(self.channel, "Hello Hola Bonjour")
                time.sleep(2)
                c.privmsg(self.channel, self.alf.random_emoji())

    def emojitest(self):
        self.alf.send_emoji()

alf = TwitchBot("_","_","_","_")
alf.emojitest()
