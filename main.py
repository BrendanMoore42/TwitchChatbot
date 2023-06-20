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
    def __init__(self, username, client_id, token, channel, admin, botname, mode="normal", print_x=5):
        self.mode = mode
        self.channel = "#" + channel  # add hashtag to make connection work
        self.admin = admin  # enables admin commands only accessible to host channel
        self.botname = botname.lower()  # the name of the bots personality

        # Set up Alfred, or the bots personality class
        self.alf = Alfred(iters=1500, memory="Memory/poker.csv", emoji_list=["CoolCat ", "PlupPls ", "PotFriend "])

        # Set up time variables
        self.start_time = datetime.datetime.now()
        self.follow_reminder = datetime.datetime.now()
        self.today = datetime.datetime.now().strftime("%m_%d_%Y")

        # Set up chat variables
        self.chat_mps = 0  # messages per second
        self.press_emoji = 0  # how many emojis pressed to prevent spam, will reset
        self.print_every_x = print_x  # print to console every x message, None to disable
        self.message_count = None
        self.chat_logs = []

        """Bot Modes:
        normal - interacts, does commands, the whole deal
        chill - will talk but not execute commands 
        listen - won't interact but will collect data and quietly observe from a distance
        """
        self.admin_commands = ["normal", "chill", "listen"]

        # Create IRC connection
        server = "irc.chat.twitch.tv"
        port = 6667
        print("Connecting to " + server + " on port " + str(port) + "...")
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, "oauth:" + token)], username, username)

    def coin_flip(self, low, high):
        """Returns a random integer between two bounds"""
        return random.randint(low, high)

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
            """Admin commands change bots mode from normal, chill, or any additional modes added"""
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

        # Normal functions, execute commands, respond to things, all the fun
        if self.mode == "normal":
            # Message is a command (starts with "!")
            if e.arguments[0][:1] == "!":
                command = e.arguments[0].split(" ")[0][1:].lower()
                print(f"Received command: {command}")

                if message_elasped > datetime.timedelta(seconds=2):
                    self.run_command(e, command)
                else:
                    # Prevent command spam if too many requests received at once
                    coin = self.coin_flip(1, 3)
                    if coin >= 2:
                        c.privmsg(self.channel, f"Tut tut. Time between requests {chat_user}")
                    else:
                        c.privmsg(self.channel, self.alf.speak("sass"))  # send random message of disappointment
                # Set timer for next command
                self.start_time = datetime.datetime.now()
            else:
                time.sleep(1)
                if e.arguments[0] == "F":
                    """Here we can isolate specific phrases for unique responses"""
                    c.privmsg(self.channel, self.alf.speak("support"))
                for y in e.arguments[0].split(" "):
                    if y.lower() == self.botname:  # comments addressed to the bot
                        c.privmsg(self.channel, self.alf.send_emoji())
                    elif y in ["catJAM", "cowJAM", "PlupPls", "pepeD", "dogJAM"]:  # common spammed animated emotes
                        coin = self.coin_flip(1, 8)
                        if coin <= 2:
                            self.press_emoji += 1
                            if self.press_emoji < 3:  # send it
                                c.privmsg(self.channel, (y + " ") * coin)
                            elif self.press_emoji >= 4:  # reset the counter and chill
                                time.sleep(coin)
                                self.press_emoji = 0
                            break

            if reminder_elapsed > datetime.timedelta(minutes=20):  # if it's been n mins past last reminder
                coin = self.coin_flip(1, 10)

                # Either drop a follow reminder or say something random
                if coin == 10:
                    line = f"Remember to follow {self.admin}!"
                elif coin >= 8:
                    # Add custom lines here
                    line = random.choice(["brb ", "ggs ", "anyone read any good books lately? ",
                                          "tea break ", "lol I just got a high score on tetris "])
                elif coin >= 5:
                    line = self.alf.speak()
                else:
                    line = self.alf.send_emoji(coin)
                c.privmsg(self.channel, line)

                self.follow_reminder = datetime.datetime.now()
        else:
            # Add in or change other modes here
            pass

    def run_command(self, e, command):
        """Executes a command and returns bot response"""

        # Ignore if in quiet modes
        if self.mode in ["chill", "listen"]:
            return

        # Set up connection for sending message
        c = self.connection
        # Pull user from message
        chat_user = e.source.split("!")[0]

        def calculate(equation):
            """Calculator"""
            if "+" in equation:
                y = equation.split("+")
                x = int(y[0] + int(y[1]))
            if "-" in equation:
                y = equation.split("-")
                x = int(y[0] - int(y[1]))
            if "*" in equation:
                y = equation.split("*")
                x = int(y[0] * int(y[1]))
            if "x" in equation:  # catch if x used instead of "*"
                y = equation.split("x")
                x = int(y[0] * int(y[1]))
            if "/" in equation:
                y = equation.split("/")
                x = int(y[0] / int(y[1]))
            return x

        if command == "follow":
            c.privmsg(self.channel, f"Remember to follow {self.admin}!")

        elif command == "8ball":  # answer a yes or no question
            coin = self.coin_flip(1, 4)
            line = random.choice(["Doesn't look great ", self.alf.send_emoji(), "Things are looking up ",
                                  "Listen to your heart ", "A thousand times yes ", "GGs haha gl ",
                                  "No. No, no, no, no. ", "Most likely ", "Hmm, doubtful ",
                                  "Ask again later ", "let me just do the math "])
            if line == "let me just do the math ":
                time.sleep(coin*2)
                c.privmsg(self.channel, "lol no ")
            else:
                time.sleep(coin)
                c.privmsg(self.channel, line)

        elif command == "poker":  # play a round of poker
            game_info, cards = self.alf.play_poker(player=chat_user)
            flop = cards[0].split(" ")

            self.alf.rig_deck()  # for the record, this does nothing

            try:
                z = e.arguments[0].split(" ")
                gg = [i + " " + j for i, j in zip(game_info[::2], game_info[1::2])]
                bot_game = True
                player_in, player_check = False, False
                if len(z) != 1:  # are there more players
                    try:
                        try:
                            player_in = z[1].split("@")[1]
                            player_check = self.alf.check_poker_player(player_in)
                            print(player_in, player_check)
                        except:
                            pass

                        if player_check:
                            bot_game = False
                        else:
                            raise IndexError
                    except:
                        bot_game = True
                        c.privmsg(self.channel, "Let's play instead ")
                if len(z) == 1 or bot_game:
                    # Game with the bot and user who initiated comment
                    player1 = self.botname
                    player2 = chat_user
                else:
                    # Two chat users
                    player1 = chat_user
                    player2 = z[1].split("@")[1]

                for ix, turn in enumerate(gg):
                    if turn.split(",")[0] == "FLOP":
                        c.privmsg(self.channel, f"Flop: {' '.join(flop[:3])}, I have {cards[1]}, {player1} has {cards[2]}")
                    if turn.split(",")[0] == "TURN":
                        float_match = re.findall("[+-]?\d+\.\d+", turn)  # get percentages
                        c.privmsg(self.channel, f"Turn: {' '.join(flop[:4])}, Chane of winning, player 1: {float_match[0][2:]}%, player 2: {float_match[1][2:]}%")
                    if turn.split(",")[0] == "RIVER":
                        c.privmsg(self.channel, f"River: {' '.join(flop[:5])}")

                time.sleep(self.coin_flip(1, 3))

                try:
                    winning_hand = game_info[-1].split(",")[1]
                    winner = int(game_info[-1].split(":")[1].split(",")[0])
                    if winner == 1:
                        victor = f"{self.alf.speak('gloat')} player 1 wins with {winning_hand} {self.alf.send_emoji()}"
                        outcome = [player1, 1, player2, 0]
                    else:
                        victor = f"{self.alf.speak('gloat')} player 2 wins with {winning_hand} {self.alf.send_emoji()}"
                        outcome = [player1, 0, player2, 1]
                    self.alf.update_score("poker", outcome)
                    c.privmsg(self.channel, victor)
                except IndexError as e:
                    print("Weird..", e)
                    c.privmsg(self.channel, "Very well, a Draw." + self.alf.speak("sass"))
            except TypeError as e:
                print(e)
                c.privmsg(self.channel, self.alf.send_emoji())

        elif command in ["cast", "fish"]:
            try:
                bait = e.arguments[0].split(" ")[1]
            except IndexError as e:
                bait = None
            if bait:
                c.privmsg(self.channel, f"{chat_user} throws out a line with {bait} as bait")
            else:
                c.privmsg(self.channel, f"{chat_user} throws out a line with no bait...good luck")
            time.sleep(self.coin_flip(2, 6))
            fish = self.alf.go_fishing(chat_user, bait)
            c.privmsg(self.channel, fish)


alf = TwitchBot("_", "_", "_", "_", admin="YourChannel", botname="alfred")  # Test params without logging in
