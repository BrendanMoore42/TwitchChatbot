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
    def __init__(self, username, client_id, token, channel, admin, mode="normal", print_x=5):
        self.mode = mode
        self.channel = "#" + channel  # add hashtag to make connection work
        self.admin = admin  # enables admin commands only accessible to host channel

        # Set up Alfred, or the bots personality class
        self.alf = Alfred(iters=1500, memory="Memory/poker.csv", emoji_list=["CoolCat ", "PlupPls ", "PotFriend "])

        # Set up time variables
        self.start_time = datetime.datetime.now()
        self.follow_reminder = datetime.datetime.now()
        self.today = datetime.datetime.now().strftime("%m_%d_%Y")

        self.chat_mps = 0  # messages per second
        self.print_every_x = print_x  # print to console every x message, None to disable
        self.message_count = None
        self.chat_logs = []
        self.admin_commands = ["normal", "chill"]

        # Create IRC connection
        server = "irc.chat.twitch.tv"
        port = 6667
        print("Connecting to " + server + " on port " + str(port) + "...")
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, "oauth:" + token)], username, username)

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

            if self.channel[:1] == "[your_channel_or_friends]":
                """When joining a specific channel, specify custom greetings here"""
                c.privmsg(self.channel, "Hello Hola Bonjour ")
                time.sleep(2)
                c.privmsg(self.channel, self.alf.send_emoji())
            # Returning to chat on the same day
            if os.path.exists(f"Memory/{self.channel}/{self.channel}_chatlog_{self.today}.txt"):
                c.privmsg(self.channel, self.alf.send_emoji())
            else:
                # First time in chat, say hello and add emoji
                phrase = random.choice(["Hello ", "Greetings ", "Whats up ", "Hola ", "PotFriend "])
                c.privmsg(self.channel, phrase + self.alf.send_emoji(3))
        elif self.mode == "chill":
            # Non-chalantly say hi and quietly remain in the background
            # Chill mode doesn't respond to chat commands other than from the top user
            c.privmsg(self.channel, "Sup " + self.alf.send_emoji(1))

        print(f"joined {self.channel}...")

    def on_pubmsg(self, c, e):
        """Receive chat"""
        chat_user = e.source.split("!")[0]  # pull user
        chat_message = e.arguments[0]  # grab message

        self.message_count += 1  # increment self counter

        # Initialize time deltas
        sleep_rand = random.randint(1, 4)
        message_time = datetime.datetime.now()
        message_time_str = message_time.strftime("%H:%M:%S")  # time message
        message_elasped = message_time - self.start_time
        reminder_elapsed = message_time - self.follow_reminder

        temp_elapsed = (message_time - self.start_time).seconds + 1  # add one in case == 0, avoid div/0
        # if temp_elapsed == 0:
        #     temp_elapsed = 1
        self.chat_mps = round((self.message_count/temp_elapsed)*60, 2)

        if self.print_every_x:
            if self.message_count % self.print_every_x == 0:
                print(temp_elapsed, self.message_count, self.chat_mps, message_time_str, chat_user, chat_message)

        if chat_user == self.admin and chat_message in self.admin_commands:
            """Admin commands change bots mode from normal, chill, or any additional"""
            print(f"{self.admin} command: {chat_message}")
            for command in self.admin_commands:
                if chat_message == command:
                    self.mode = command

        # Remember chat every n messages depending on chat speed
        if self.message_count % 50 == 0 and self.chat_mps < 10:  # slow chat
            self.alf.remember_chat(self.channel, self.chat_logs, self.today)
            print('Remembering chat...\n')
        elif self.message_count % 500 == 0:  # anytime we hit 500 messages
            self.alf.remember_chat(self.channel, self.chat_logs, self.today)
            print('Remembering chat...\n')
        elif self.message_count % 100 == 0 and self.chat_mps >= 10:  # fast chat
            self.alf.remember_chat(self.channel, self.chat_logs, self.today)
            print('Remembering chat...\n')




alf = TwitchBot("_", "_", "_", "_", admin="YourChannel")  # Test params without logging in
