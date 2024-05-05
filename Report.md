
# Coursework report

<br>
<br>

## Introduction

<br>

**Description of the application**

My application is a game called "Durak". "Durak" is a traditional Russian card game that is popular in many post-soviet states. This application is a simple simulation of the game using the standard 52-card deck.

<br>

**How to run the program?**

Simply hover on the "Run" option in the top-left corner and then press the "Run without debugging" option. Or you could type "python Durak.py" in the terminal

<br>

**How to play Durak/How to use the program**

After running the game, a hand of cards appears on the bottom. You can pick any card from your hand to play by pressing on the card and dragging it out of your hand. When your turn ends, press "Next turn". When the button is pressed the hand on the bottom gets hidden and another hand gets displayed on the top of the screen. Now it's the second players turn. The objective is to beat the card of your opponent. To beat the card, you have to find a card that has the same suit as the card that you have to beat but higher rank. Then, simply press on the card and drag it onto the card you want to beat. When you manage to beat all of your opponents cards, you can press next turn. If you don't have a way to beat your opponents cards, you have to press the "Take cards" button. If your opponent has a card with the same rank as the cards displayed on the table, he has the choice to attack you with that card and you have to beat that card once again. The game goes on with the same logic until the amount of the cards in the deck is zero and one of the players gets rid of their cards. The last player left with the cards is the "durak" or a fool and loses the game.

## Body/Analysis

**4 object-oriented programming pillars**

<br>

**1. Polymorphism**

Polymorphism allows objects of different types to be treated as if they were of the same type. 

Although I did not need to override a method, I used the same method in another class:

```Python
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.rank_values = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
                            "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
        self.suit = suit
        self.image = pygame.transform.scale(pygame.image.load(
            f"Images\\{self.rank}_of_{self.suit}.png").convert_alpha(), (100, 150))
        self.rect = self.image.get_rect()

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def draw(self, pos=None):  # draw card on screen
        if pos:
            screen.blit(self.image, pos)
        else:
            pos = self.rect.topleft
            screen.blit(self.image, pos)

    def set_top_left(self, pos):
        self.rect.topleft = pos

    def __gt__(self, other):
        return self.rank_values[self.rank] > self.rank_values[other.rank]


class TrumpCard(Card):
    def __init__(self, rank, suit):
        super().__init__(rank, suit)

    def draw(self, pos=None):  # draw trump card on screen
        pass
```

<br>

**2. Abstraction**

Abstraction allows us to simplify complex systems. By creating an abstract class and making abstract methods, we can reuse those abstract methods in other classes to make the code cleaner. Abstract classes cannot be instantiated. To implement abstraction you also need to import the abc module, to use the abstract base class utility.

In my code I made an abstract player class "AbstractPlayer". Then I created some abstract methods to use for specific players in the other class:

```Python
from abc import ABC, abstractmethod
```

<br>

```Python
class AbstractPlayer(ABC):
    def __init__(self, deck):
        self.deck = deck
        self._hand = []
        self._visible = False
        self._dragging = False
        self._dragged_card = None
        self._original_index = None

    card_width = 100
    stack_gap = 10

    @abstractmethod
    def deal_hand(self, num_cards):
        pass

    def toggle_visibility(self):  # toggle player hand visibility (whose turn it is)
        self._visible = not self._visible

    def is_visible(self):
        return self._visible

    def draw_hand(self, screen, offset, y_position):  # draw player hand on screen
        max_cards_in_row = 8
        for i, card in enumerate(self._hand):  # for card in hand
            card.set_top_left((i % max_cards_in_row*(self.card_width +
                              self.stack_gap) + offset, y_position + i//max_cards_in_row*35))
            card.draw()

    @abstractmethod
    def event_handler(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw_dragged_card(self):
        pass


class Player(AbstractPlayer):
    def __init__(self, deck, name, hand_position):
        super().__init__(deck)
        self.name = name
        self.hand_position = hand_position
        self.num_cards_played = 0
        self.num_cards_in_hand = 0
        global players
        global cards_to_display
        players.append(self)

    card_to_defend = None

    def deal_hand(self, num_cards):  # deal hand to player
        self._hand = self.deck.deal_cards(num_cards, self._hand)
        self.num_cards_in_hand = len(self._hand)

    def event_handler(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:  # check for card click
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                cards_clicked = [card for card in self._hand if card.rect.collidepoint(
                    mouse_pos)]  # cards that the mouse is over
                if cards_clicked:  # if there are cards that were clicked
                    # get the card on top
                    card_clicked = cards_clicked[len(cards_clicked) - 1]
                    cards_clicked.clear()
                    if not self._dragging:
                        self._dragging = True
                        self._dragged_card = card_clicked
                        self._original_index = self._hand.index(card_clicked)
                        return

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # check for card release
            if self._dragging:
                self._dragging = False
                if isDefender(self) == 0:  # attacker
                    # print("A: attacker " + self.name + " played a card against defender " + defender.name)
                    if self.num_cards_played == 0:
                        card = self._hand.pop(self._original_index)
                        cards_to_display[card] = None
                        self.num_cards_played += 1
                    else:
                        for attacker_card, defender_card in cards_to_display.items():
                            if attacker_card.rank == self._dragged_card.rank:
                                card = self._hand.pop(self._original_index)
                                cards_to_display[card] = None
                                self.num_cards_played += 1
                                break
                            if defender_card != None:
                                if defender_card.rank == self._dragged_card.rank:
                                    card = self._hand.pop(self._original_index)
                                    cards_to_display[card] = None
                                    self.num_cards_played += 1
                                    break
                    self._dragged_card = None
                    self._original_index = None
                else:  # defender
                    # print("B: defender tried playing a card")
                    opponent = players[1-players.index(self)]
                    self.card_to_defend = self.check_boundaries(
                        screen, opponent)
                    if not self.card_to_defend == None and cards_to_display[self.card_to_defend] == None:  # card released on top of opponents card and it has not been defended yet?\
                        if self.is_valid_move(self.deck, self._dragged_card):
                            # print("C: defender played a card (dragged card over opponents card)")
                            self._hand.pop(self._original_index)
                            cards_to_display[self.card_to_defend] = self._dragged_card
                            self.num_cards_played += 1
                    self._dragged_card = None
                    self._original_index = None

    def update(self):  # update dragged card position
        if self._dragging:
            mouse_pos = pygame.mouse.get_pos()
            self._dragged_card.rect.centerx = mouse_pos[0]
            self._dragged_card.rect.centery = mouse_pos[1]

    def draw_dragged_card(self):
        if self._dragging and self._dragged_card is not None:
            card = self._dragged_card
            card.rect.center = pygame.mouse.get_pos()
            card.draw()

    # draw cards played by both players
    def draw_cards_to_display(self, screen, is_defender, opponent):

        if is_defender == 0:  # attacker
            self.draw_attackers_played_cards(screen, self)
        else:  # defender
            self.draw_attackers_played_cards(screen, opponent)
        self.draw_defenders_played_cards()

    # draw cards played by the attacker
    def draw_attackers_played_cards(self, screen, attacker):

        card_width = 100
        stack_gap = 20  # horizontal gap between cards

        initial_x = screen.get_width() // 2 - ((attacker.num_cards_played - 1)
                                               * (card_width + stack_gap) // 2)
        initial_y = screen.get_height() // 2

        for i, card in enumerate(cards_to_display):  # for card played by attacker
            card.rect.centerx = initial_x + (i * (card_width + stack_gap))
            card.rect.centery = initial_y
            card.draw()

    def draw_defenders_played_cards(self):  # draw cards played by the defender
        # how much lower the defenders cards are displayed than the attackers
        defender_card_offset_y = 40
        defender_cards_to_display = {
            key: value for key, value in cards_to_display.items() if value is not None}
        for attacker_card, defender_card in defender_cards_to_display.items():
            defender_card.rect.centerx = attacker_card.rect.centerx
            defender_card.rect.centery = attacker_card.rect.centery + defender_card_offset_y
            defender_card.draw()

    # returns the index of the card the dragged card is released on top of
    def check_boundaries(self, screen, player):
        card_height = 150
        card_width = 100
        stack_gap = 20  # horizontal gap between cards

        mouse_pos = pygame.mouse.get_pos()

        initial_x = screen.get_width() // 2 - ((player.num_cards_played - 1)
                                               * (card_width + stack_gap) // 2)
        initial_y = screen.get_height() // 2

        for i, card in enumerate(cards_to_display):
            if initial_x + (i * (card_width + stack_gap)) - card_width // 2 <= mouse_pos[0] <= initial_x + (i * (card_width + stack_gap)) + card_width // 2 and initial_y - card_height // 2 <= mouse_pos[1] <= initial_y + card_height // 2:
                return card
        return None

    @log_func_call
    def is_valid_move(self, deck, defender_card):
        attacker_card = self.card_to_defend
        if defender_card.suit == attacker_card.suit and defender_card > attacker_card:
            return True
        elif defender_card.suit == deck.trump_card.suit and attacker_card.suit != deck.trump_card.suit:
            return True
        else:
            return False
```

<br>

**3. Inheritance**

Inheritance is a mechanism that allows you to reuse existing classes and extend their functionality. The child class gets all the attributes and methods from the parent class

In my code, I used inheritance in many places. One example of it would be when i created a "Cards" class (the parent class) and made another class "Deck" (child class) inherit the parent class:

```Python
class Cards:
    def __init__(self):
        self.rank = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
                     "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
        self.suit = ("spades", "diamonds", "clubs", "hearts")
        self.cards = []

    def create_cards(self):
        for rank in self.rank:
            for suit in self.suit:
                self.cards.append(Card(rank, suit))

        return self.cards
```

<br>

```Python
class Deck(Cards, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__()
        self.create_cards()
        self.shuffle_deck()
        self.trump_card = self.get_trump_card()
        self.trump_card_taken = False

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def deal_cards(self, num_cards, hand):
        for card in self.cards[:num_cards]:  # deal numcard cards from the deck
            hand.append(card)
        if (num_cards > len(self.cards) and not self.trump_card_taken):
            hand.append(self.trump_card)
            self.trump_card_taken = True
        self.cards = self.cards[num_cards:]  # remove dealt cards from the deck
        return hand

    def get_trump_card(self):  # trump card is the first card in the deck
        if self.cards:
            trump_card = self.cards.pop(0)
            trump_card.image = pygame.transform.scale(pygame.image.load(
                f"Images\\{trump_card.rank}_of_{trump_card.suit}.png"), (100, 150))
            return trump_card
        else:
            return None
```

<br>

**4. Encapsulation**

Encapsulation bundles data and methods that work on data within one unit. It also serves as access control to protect or hide the data.

In my code, I used encapsulation to protect some variables within the classes. Here's the example:

```Python
def __init__(self, deck):
        self.deck = deck
        self._hand = []
        self._visible = False
        self._dragging = False
        self._dragged_card = None
        self._original_index = None
```

**Decorators**

<br>

**1. Singleton**

When I created the deck of cards and tried running the game, I encountered a problem. Every turn the game would take a different instance of the deck making the game unplayable. That's when I thought of using the Singleton Pattern to create one instance of the deck.

Singleton checks if there are any instances, if not, it creates an instance, if there already is an instance, it returns the instance that already exists.

Here's how I implemented Singleton in my code:

```Python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Deck(Cards, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__()
        self.create_cards()
        self.shuffle_deck()
        self.trump_card = self.get_trump_card()
        self.trump_card_taken = False

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def deal_cards(self, num_cards, hand):
        for card in self.cards[:num_cards]:  # deal numcard cards from the deck
            hand.append(card)
        if (num_cards > len(self.cards) and not self.trump_card_taken):
            hand.append(self.trump_card)
            self.trump_card_taken = True
        self.cards = self.cards[num_cards:]  # remove dealt cards from the deck
        return hand

    def get_trump_card(self):  # trump card is the first card in the deck
        if self.cards:
            trump_card = self.cards.pop(0)
            trump_card.image = pygame.transform.scale(pygame.image.load(
                f"Images\\{trump_card.rank}_of_{trump_card.suit}.png"), (100, 150))
            return trump_card
        else:
            return None
```

<br>

**2. Decorator**

Decorator is a design pattern in Python that allows a user to add new functionality to an existing object without modifying its structure.

The logic is simple: we create a wrapper for a method that we can reuse any time we need. It's useful for multiple functions that require the same additional functionality.

I used a decorator to make a method that checks if the player made a valid move and returns True or False during the game:

```Python
import logging
```

<br>

```Python
logging.basicConfig(level=logging.INFO)


def log_func_call(func):
    def wrapper(*args, **kwargs):
        logging.info(f"Calling function {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"Function {func.__name__} returned {result}")
        return result
    return wrapper
```

<br>

```Python
    @log_func_call
    def is_valid_move(self, deck, defender_card):
        attacker_card = self.card_to_defend
        if defender_card.suit == attacker_card.suit and defender_card > attacker_card:
            return True
        elif defender_card.suit == deck.trump_card.suit and attacker_card.suit != deck.trump_card.suit:
            return True
        else:
            return False
```

**Reading from file & writing to file**

I used writing and reading from file to save the data of a game. You can press the "S" key anytime during the game to save the data to a text file called "save_data.txt" and then press the "L" key to load the data of an unfinished game. Data gets loaded by reading the information that was saved from the same text file.

Save data:

```Python
# save cards in deck, trump card, player turn, player hands, defender and cards played this round
def save_data(deck, player1, player2):
    global defender
    global cards_to_display

    with open("save_data.txt", "w") as file:

        cards = "cards = ["
        if len(deck.cards) > 0:
            for card in deck.cards:
                cards += "Card('" + card.rank + "', '" + card.suit + "'), "
            cards = cards[:-2]  # remove the last comma
        else:
            cards += "None"
        file.write(cards + "]\n")

        trump_card = "trump card = Card('" + deck.trump_card.rank + \
            "', '" + deck.trump_card.suit + "')\n"
        file.write(trump_card)

        trump_card_taken = "trump card taken = " + \
            str(deck.trump_card_taken) + "\n"
        file.write(trump_card_taken)

        defender_line = "defender = " + defender.name + "\n"
        file.write(defender_line)

        player1_visible = "player1_visible = " + \
            str(player1.is_visible()) + "\n"
        file.write(player1_visible)

        attacker_cards_played = "Attacker cards played = ["
        if len(cards_to_display) > 0:
            for attacker_card in cards_to_display.keys():
                attacker_cards_played += "Card('" + attacker_card.rank + \
                    "', '" + attacker_card.suit + "'), "
            # remove the last comma
            attacker_cards_played = attacker_cards_played[:-2]
        else:
            attacker_cards_played += "None"
        file.write(attacker_cards_played + "]\n")

        defender_cards_played = "Defender cards played = ["
        if len(cards_to_display) > 0:
            for defender_card in cards_to_display.values():
                if defender_card != None:
                    defender_cards_played += "Card('" + defender_card.rank + \
                        "', '" + defender_card.suit + "'), "
                else:
                    defender_cards_played += "None, "
            # remove the last comma
            defender_cards_played = defender_cards_played[:-2]
        else:
            defender_cards_played += "None"
        file.write(defender_cards_played + "]\n")

        player1_hand = "Player 1 hand = ["
        if len(player1._hand) > 0:
            for card in player1._hand:
                player1_hand += "Card('" + card.rank + \
                    "', '" + card.suit + "'), "
            player1_hand = player1_hand[:-2]  # remove the last comma
        else:
            player1_hand += "None"
        file.write(player1_hand + "]\n")

        player2_hand = "Player 2 hand = ["
        if len(player2._hand) > 0:
            for card in player2._hand:
                player2_hand += "Card('" + card.rank + \
                    "', '" + card.suit + "'), "
            player2_hand = player2_hand[:-2]  # remove the last comma
        else:
            player2_hand += "None"
        file.write(player2_hand + "]\n")

        print("Data saved")
```

Load data:

```Python
def load_data(deck, player1, player2):  # load data from save file
    global defender
    global cards_to_display
    with open("save_data.txt", "r") as file:
        lines = file.readlines()

        # check if all lines containing the data are in the file
        # cards = [Card('A', 'spades'), Card('K', 'spades'), ...]
        cards_line = next((line for line in lines if "cards = " in line), None)
        if cards_line == None:
            print("No saved cards found")
            return

        trump_card_taken_line = next(
            # trump card taken = True
            (line for line in lines if "trump card taken = " in line), None)
        if trump_card_taken_line == None:
            print("No saved trump card taken found")
            return

        # trump card = Card('A', 'spades')
        trump_card_line = next(
            (line for line in lines if "trump card = " in line), None)
        if trump_card_line == None:
            print("No saved trump card found")
            return

        # defender = player1
        defender_line = next(
            (line for line in lines if "defender = " in line), None)
        if defender_line == None:
            print("No saved defender found")
            return

        player1_visible_line = next(
            # player1_visible = True
            (line for line in lines if "player1_visible = " in line), None)
        if player1_visible_line == None:
            print("No saved player 1 visibility found")
            return

        # Attacker cards played = [Card('A', 'spades'), Card('K', 'spades'), ...]
        attacker_cards_played_line = next(
            (line for line in lines if "Attacker cards played = " in line), None)
        if attacker_cards_played_line == None:
            print("No saved attacker cards played found")
            return

        # Defender cards played = [Card('A', 'spades'), Card('K', 'spades'), ...]
        defender_cards_played_line = next(
            (line for line in lines if "Defender cards played = " in line), None)
        if defender_cards_played_line == None:
            print("No saved defender cards played found")
            return

        # Player 1 hand =  [Card('A', 'spades'), Card('K', 'spades'), ...]
        player1_hand_line = next(
            (line for line in lines if "Player 1 hand = " in line), None)
        if player1_hand_line == None:
            print("No saved player 1 hand found")
            return

        # Player 2 hand =  [Card('A', 'spades'), Card('K', 'spades'), ...]
        player2_hand_line = next(
            (line for line in lines if "Player 2 hand = " in line), None)
        if player2_hand_line == None:
            print("No saved player 2 hand found")
            return

        # load data from the file

        # deck
        if not cards_line == "cards = [None]\n":
            # leaves only the object constructors [Card('A', 'spades'), Card('K', 'spades'), ...]
            cards_line = cards_line.replace("cards = ", "")
            cards_line = cards_line[:-1]  # removes \n at the end
            cards = eval(cards_line)  # creates a list of card objects
            deck.cards = cards

        # trump card taken
        trump_card_taken_line = trump_card_taken_line.replace(
            "trump card taken = ", "")  # leaves only the boolean value
        deck.trump_card_taken = eval(trump_card_taken_line)

        # trump card
        # leaves only the object constructor (Card('A', 'spades'))
        trump_card_line = trump_card_line.replace("trump card = ", "")
        trump_card_line = trump_card_line[:-1]  # removes \n at the end
        trump_card = eval(trump_card_line)  # creates a card object
        deck.trump_card = trump_card

        # defender
        defender_line = defender_line.replace(
            "defender = ", "")  # leaves only the player name
        if defender_line == "player1":
            defender = player1
        else:
            defender = player2

        # player visibility
        player1_visible_line = player1_visible_line.replace(
            "player1_visible = ", "")  # leaves only the boolean value
        player1_visible = eval(player1_visible_line)

        player1._visible = player1_visible
        player2._visible = not player1_visible

        # cards played this round
        cards_to_display.clear()

        if not attacker_cards_played_line == "Attacker cards played = [None]\n":

            # leaves only the object constructors [Card('A', 'spades'), Card('K', 'spades'), ...]
            attacker_cards_played_line = attacker_cards_played_line.replace(
                "Attacker cards played = ", "")
            attacker_cards_played_line = attacker_cards_played_line[:-1]
            attacker_cards = eval(attacker_cards_played_line)

            # leaves only the object constructors [Card('A', 'spades'), Card('K', 'spades'), ...]
            defender_cards_played_line = defender_cards_played_line.replace(
                "Defender cards played = ", "")
            defender_cards_played_line = defender_cards_played_line[:-1]
            defender_cards = eval(defender_cards_played_line)

            for attacker_card, defender_card in zip(attacker_cards, defender_cards):
                if defender_card == None:
                    cards_to_display[attacker_card] = None
                else:
                    cards_to_display[attacker_card] = defender_card

        # player hands
        if not player1_hand_line == "Player 1 hand = [None]\n":
            # leaves only the object constructors [Card('A', 'spades'), Card('K', 'spades'), ...]
            player1_hand_line = player1_hand_line.replace(
                "Player 1 hand = ", "")
            player1_hand_line = player1_hand_line[:-1]  # removes \n at the end
            # creates a list of card objects
            player1_hand = eval(player1_hand_line)
            player1._hand = player1_hand
            player1.num_cards_in_hand = len(player1._hand)
        else:
            player1._hand = []
            player1.num_cards_in_hand = 0

        if not player2_hand_line == "Player 2 hand = [None]\n":
            # leaves only the object constructors [Card('A', 'spades'), Card('K', 'spades'), ...]
            player2_hand_line = player2_hand_line.replace(
                "Player 2 hand = ", "")
            player2_hand_line = player2_hand_line[:-1]
            # creates a list of card objects
            player2_hand = eval(player2_hand_line)
            player2._hand = player2_hand
            player2.num_cards_in_hand = len(player2._hand)
        else:
            player2._hand = []
            player2.num_cards_in_hand = 0

        if (isDefender(player1)):
            player1.num_cards_played = sum(
                1 for card in cards_to_display.values() if not card == None)
        else:
            player1.num_cards_played = sum(
                1 for card in cards_to_display.keys())
```

**Testing**

I wrote an additional script for testing the core functionality of the application using unittest framework. Additional tests can be added any time.

Here's the code:

```Python
import unittest
from Durak import Player
from Durak import Deck


class TestPlayer(unittest.TestCase):
    def setUp(self):
        deck = Deck()
        self.player1 = Player(deck, "Player 1", (0, 0))
        self.player2 = Player(deck, "Player 2", (0, 0))

    def test_deal_hand(self):
        self.player1.deal_hand(6)
        self.player2.deal_hand(6)
        self.assertEqual(len(self.player1._hand), 6)
        self.assertEqual(len(self.player2._hand), 6)

    def test_player_name(self):
        self.assertEqual(self.player1.name, "Player 1")
        self.assertEqual(self.player2.name, "Player 2")
        self.assertEqual(self.player1.name, "Player 2")

    def test_loaded_data(self):
        with open("save_data.txt", "r") as file:
            lines = file.readlines()

            cards_line = next(
                (line for line in lines if "cards = " in line), None)
            self.assertIsNone(cards_line)

            trump_card_taken_line = next(
                (line for line in lines if "trump card taken = " in line), None)
            self.assertIsNone(trump_card_taken_line)

            trump_card_line = next(
                (line for line in lines if "trump card = " in line), None)
            self.assertIsNone(trump_card_line)

            defender_line = next(
                (line for line in lines if "defender = " in line), None)
            self.assertIsNone(defender_line)

            player1_visible_line = next(
                (line for line in lines if "player1_visible = " in line), None)
            self.assertIsNone(player1_visible_line)

            attacker_cards_played_line = next(
                (line for line in lines if "Attacker cards played = " in line), None)
            self.assertIsNone(attacker_cards_played_line)

            defender_cards_played_line = next(
                (line for line in lines if "Defender cards played = " in line), None)
            self.assertIsNone(defender_cards_played_line)

            player1_hand_line = next(
                (line for line in lines if "Player 1 hand = " in line), None)
            self.assertIsNone(player1_hand_line)

            player2_hand_line = next(
                (line for line in lines if "Player 2 hand = " in line), None)
            self.assertIsNone(player2_hand_line)


if __name__ == '__main__':
    unittest.main()
```

**PEP8 style guidelines**

I downloaded a tool through the command prompt called "autopep8". This tool automatically rearranges the code in Pep8 code style just by typing "autopep8 File_name.py --in-place". It is an amazing and incredible tool. The author of this tool is Hideo Hattori.

## Results and summary

**Results:**

* Very hard to find a place to use polymorphism.
* Hard to keep a clean structure of the code.
* The code turned out unnecessarily long and all over the place.
* The visuals (game screen) turned out sloppy and not refined.

<br>

**Conclusion:**

The project was very helpful to get to understand the fundamental concepts of object_oriented programming, as well as, other concepts of programming such as reading from a file and writing to a file, logic, flags. The visual part also required some mathematical knowledge to calculate the positions of the cards and so on. Overall, I am happy with the outcome as it is my first programming project that I finished.

**How could I extend my application?**

I could definitely shorten the code overall, especially the "save_data" and "load_data" methods. Also, I noticed that I forgot to implement a mechanic of the game, where the different can turn the table and make the opponent defend by putting a card of the same rank next to an already placed card. Then, I also forgot to implement some logic: in the end game, when the deck is empty, the attacker should only be allowed to put the amount of cards, depending on how many cards the defender has in his hand. Lastly, I could add some additional options: choosing how many cards there are in a deck (standard 52-cards deck, 36-cards deck, 24-cards deck), choosing a table to play on, cards to play with (skins).