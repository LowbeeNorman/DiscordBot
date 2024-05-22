# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import os
import discord
import requests
import json
import random
import time
import pickle

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

blackjack_dict = {}
blackjack_curr_hand_dict = {}
winstreaks = {"fjoiwaejofansjgnajoofgweisgoiase": 0}
totalwins = {"fjoiwaejofansjgnajoofgweisgoiase": 0}

with open("winstreaks.pkl", "rb") as in_:
    winstreaks = pickle.load(in_)

with open("totalwins.pkl", "rb") as in_:
    totalwins = pickle.load(in_)


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote


def get_affirmation():
    response = requests.get("https://www.affirmations.dev/")
    json_data = json.loads(response.text)
    affirmation = json_data["affirmation"]
    return affirmation


def urban_dictionary(word):
    response = requests.get("https://api.urbandictionary.com/v0/define?term=" +
                            word)
    json_data = json.loads(response.text)
    definition = json_data["list"][0]["definition"]
    return definition


def blackjack(player_name):
    if player_name not in winstreaks:
        winstreaks[player_name] = 0
    if player_name not in totalwins:
        totalwins[player_name] = 0
    if player_name in blackjack_dict:
        return False
    else:
        new_deck = Deck()
        return new_deck


def blackjack_cleanup(player_name):
    del blackjack_dict[player_name]
    del blackjack_curr_hand_dict[player_name]


def calculatePoints(hand):
    currSum = 0
    for i in range(len(hand)):
        currSum += hand[i].value
    if currSum > 21:
        for i in range(len(hand)):
            if hand[i].value == 11:
                currSum -= 10
            if currSum <= 21:
                break
    return currSum


class Card:

    def __init__(self, suit, value, name):
        self.suit = suit
        self.value = value
        self.name = name

    def __str__(self):
        return f"{self.name} of {self.suit}"


class Deck:

    def __init__(self):
        self.cards = []
        self.build()

    def build(self):  # This has been specifcally modified for blackjack
        for suit in ["Spades", "Clubs", "Diamonds", "Hearts"]:
            for value in range(2, 11):
                self.cards.append(Card(suit, value, value))
            self.cards.append(Card(suit, 10, "Jack"))
            self.cards.append(Card(suit, 10, "Queen"))
            self.cards.append(Card(suit, 10, "King"))
            self.cards.append(Card(suit, 11, "Ace"))

    def show(self):
        for card in self.cards:
            print(card)

    def shuffle(self):
        for i in range(len(self.cards) - 1, 0, -1):
            r = random.randint(0, i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def draw(self):
        return self.cards.pop()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.content.startswith('$inspire'):
        quote = get_quote()
        await message.channel.send(quote)

    elif message.content.startswith('$affirm'):
        affirmation = get_affirmation()
        await message.channel.send(affirmation)

    elif message.content.startswith('$define'):
        word = message.content.split("$define ", 1)[1]
        definition = urban_dictionary(word)
        wholeMsg = word + ":\n" + definition
        await message.channel.send(wholeMsg)

    elif message.content.startswith('$echo'):
        echo = message.content.split("$echo ", 1)[1]
        gamer = echo
        for i in range(100):
            gamer = gamer + " " + echo
            i = i + 1
        await message.channel.send(gamer)

    elif message.content.startswith('$draw'):
        deck = Deck()
        deck.shuffle()
        card = deck.draw()
        await message.channel.send(card)

    elif message.content.startswith('$blackjack'):
        bResult = blackjack(message.author.name)
        if not bResult:
            await message.channel.send(
                "You already have an ongoing game in this server or another")

        else:
            bResult.shuffle()
            card1 = bResult.draw()
            card2 = bResult.draw()
            blackjack_dict[message.author.name] = bResult
            blackjack_curr_hand_dict[message.author.name] = [card1, card2]
            currPoints = calculatePoints(
                blackjack_curr_hand_dict[message.author.name])
            returnWord = "First two cards are: " + card1.__str__(
            ) + " and " + card2.__str__() + ". Current points are: " + str(
                currPoints)
            await message.channel.send(returnWord)

    elif message.content.startswith('$hit'):
        if message.author.name in blackjack_dict:
            bResult = blackjack_dict[message.author.name]
            bHand = blackjack_curr_hand_dict[message.author.name]
            bResult.shuffle()
            card = bResult.draw()
            bHand.append(card)
            blackjack_dict[message.author.name] = bResult
            currPoints = calculatePoints(bHand)

            if currPoints > 21:
                await message.channel.send("You drew the " + card.__str__())
                await message.channel.send(
                    "You busted with " + str(currPoints) +
                    " points. Type $blackjack to start a new game.")
                blackjack_cleanup(message.author.name)
            else:
                await message.channel.send("You drew the " + card.__str__() +
                                           ". Current points are: " +
                                           str(currPoints))
        else:
            await message.channel.send(
                "You don't have an ongoing game. Type $blackjack to start a new game."
            )

    elif message.content.startswith("$stay"):
        if message.author.name in blackjack_dict:
            bResult = blackjack_dict[message.author.name]
            bHand = blackjack_curr_hand_dict[message.author.name]
            playerPoints = calculatePoints(bHand)
            dealerPoints = 0
            blackjack_curr_hand_dict[message.author.name] = [
            ]  # Use the same hand for the dealer cards because we will reset is anyways after
            while dealerPoints < playerPoints:
                card = bResult.draw()
                blackjack_curr_hand_dict[message.author.name].append(card)
                dealerPoints = calculatePoints(
                    blackjack_curr_hand_dict[message.author.name])
                if dealerPoints <= 21 and dealerPoints < playerPoints:
                    await message.channel.send(
                        "Dealer drew the " + card.__str__() +
                        ". Current dealer points are: " + str(dealerPoints))
                else:
                    await message.channel.send("Dealer drew the " +
                                               card.__str__())
                time.sleep(1.15)
            if dealerPoints <= 21:
                if winstreaks[message.author.name] == 0:
                    await message.channel.send(
                        "Dealer wins with " + str(dealerPoints) + " points." +
                        " You lost with " + str(playerPoints) +
                        " points. Type $blackjack to start a new game.")
                else:
                    oldStreak = winstreaks[message.author.name]
                    winstreaks[message.author.name] = 0
                    with open("winstreaks.pkl", "wb") as out:
                        pickle.dump(winstreaks, out)
                    await message.channel.send(
                        "Dealer wins with " + str(dealerPoints) + " points." +
                        " You lost with " + str(playerPoints) +
                        " points. You also lost your winstreak of: " +
                        str(oldStreak) +
                        ". Type $blackjack to start a new game.")
            else:
                winstreaks[
                    message.author.name] = winstreaks[message.author.name] + 1
                totalwins[
                    message.author.name] = totalwins[message.author.name] + 1
                with open("winstreaks.pkl", "wb") as out:
                    pickle.dump(winstreaks, out)
                with open("totalwins.pkl", "wb") as out:
                    pickle.dump(totalwins, out)
                await message.channel.send(
                    "Dealer busted with " + str(dealerPoints) + " points." +
                    " You won with " + str(playerPoints) +
                    " points. You are on a winstreak of: " +
                    str(winstreaks[message.author.name]) +
                    ". Type $blackjack to start a new game.")
            blackjack_cleanup(message.author.name)
        else:
            await message.channel.send(
                "You don't have an ongoing game. Type $blackjack to start a new game."
            )
    elif message.content.startswith("$totalwins"):
        if message.author.name in totalwins:
            await message.channel.send(totalwins[message.author.name])
        else:
            await message.channel.send("You have played no blackjack games.")
    else:
        return


try:
    token = os.getenv("TOKEN") or ""
    if token == "":
        raise Exception("Please add your token to the Secrets pane.")
    client.run(token)
except discord.HTTPException as e:
    if e.status == 429:
        print(
            "The Discord servers denied the connection for making too many requests"
        )
        print(
            "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
        )
    else:
        raise e
