import pygame
import random
from abc import ABC, abstractmethod
import logging
import unittest

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

logging.basicConfig(level=logging.INFO)


def log_func_call(func):
    def wrapper(*args, **kwargs):
        logging.info(f"Calling function {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"Function {func.__name__} returned {result}")
        return result
    return wrapper


defender = None
players = list()
# pavadinimas = dict() - padaryti dictionary, iskviecia dict klases konstruktoriu
cards_to_display = dict()


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
        # Implement the logic to draw the trump card
        pass


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


def isDefender(player):  # is the player the defender?
    if defender == player:
        return 1
    else:
        return 0


def check_win(deck):  # check if the game has ended
    if (len(deck.cards)) == 0:  # if the deck is empty
        for player in players:
            if (player.num_cards_in_hand == 0):  # if a player has no cards left
                # if the other player also has no cards left
                if players[1 - players.index(player)].num_cards_in_hand == 0:
                    print("Tie!")
                else:  # the other player has cards left
                    print(player.name + " wins!")
                return True

    return False


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


def is_enabled(button):  # check if the button can be pressed and is visible

    end_round_button_enabled = False
    next_button_enabled = False

    not_all_cards_defended = False
    for defender_card in cards_to_display.values():  # if there are undefended cards
        if defender_card == None:
            not_all_cards_defended = True
            break

    for i, player in enumerate(players):
        if player.is_visible():  # this player's turn
            if isDefender(player):  # defender
                if not_all_cards_defended:
                    end_round_button_enabled = True
                else:
                    next_button_enabled = True

            else:  # attacker
                if (len(cards_to_display) > 0 and not_all_cards_defended):
                    next_button_enabled = True
                elif (len(cards_to_display) > 0):
                    end_round_button_enabled = True

    if button == "end_round_button":
        return end_round_button_enabled
    elif button == "next_button":
        return next_button_enabled


def main():

    # set up screen
    screen_size_x = screen.get_width()
    screen_size_y = screen.get_height()
    pygame.display.set_caption("Durak")

    # create quit button
    quit_button_rect = pygame.Rect((screen_size_x - 120, 20, 100, 40))
    font = pygame.font.SysFont(None, 32)
    quit_text = font.render("Quit", True, (255, 255, 255))

    # create next turn button
    next_button_rect = pygame.Rect(
        (screen_size_x - 160, screen_size_y / 2 - 20, 140, 40))
    next_button_text = font.render("Next turn", True, (255, 255, 255))

    end_round_button_rect = pygame.Rect(
        (screen_size_x - 160, screen_size_y / 2 + 30, 140, 40))
    end_round_button_text = font.render("End round", True, (255, 255, 255))

    global defender

    # create deck and players
    deck = Deck()
    player1 = Player(deck, "player1", (400, screen_size_y - 250))
    player1._visible = True
    player2 = Player(deck, "player2", (400, 100))
    defender = player2

    player1.deal_hand(6)
    player2.deal_hand(6)

    # set up background and card stack images
    background_image = pygame.image.load(
        "Images\\green-casino-poker-table-texture-game-background-free-vector.jpg")
    background_image = pygame.transform.scale(
        background_image, (screen_size_x, screen_size_y))
    back_of_card = pygame.image.load("Images\\back of the card.jpg")
    back_of_card = pygame.transform.scale(back_of_card, (100, 150))

    # start game loop
    run = True

    while run:
        events = pygame.event.get()

        for event in events:  # end game
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_data(deck, player1, player2)
                if event.key == pygame.K_l:
                    load_data(deck, player1, player2)

            if event.type == pygame.MOUSEBUTTONDOWN:  # handle mouse clicks
                # quit button pressed
                if event.button == 1 and quit_button_rect.collidepoint(event.pos):
                    run = False

                # next turn button pressed
                elif event.button == 1 and next_button_rect.collidepoint(event.pos):
                    if (is_enabled("next_button")):
                        player1.toggle_visibility()
                        player2.toggle_visibility()

                # end round button pressed
                elif event.button == 1 and end_round_button_rect.collidepoint(event.pos):
                    if is_enabled("end_round_button"):
                        player1.num_cards_in_hand = len(player1._hand)
                        player2.num_cards_in_hand = len(player2._hand)
                        # finds player who clicked the button
                        for i, player in enumerate(players):
                            if player.is_visible():
                                button_clicked_by = player

                        # gynejas (zaidejas, nepaspaudes mygtuko) apsigyne / puolejas paspaude mygtuka
                        if (not isDefender(button_clicked_by)):
                            if (len(cards_to_display) > 0):  # attacker played cards this round
                                undefended_cards = [attacker_card for attacker_card in cards_to_display.keys(
                                ) if cards_to_display[attacker_card] == None]
                                # all cards have been defended (the button was pressed legally)
                                if len(undefended_cards) == 0:
                                    # other player becomes defender
                                    defender = players[1 -
                                                       players.index(defender)]
                                    player1.toggle_visibility()
                                    player2.toggle_visibility()
                                    cards_to_display.clear()
                                    player1.num_cards_played = 0
                                    player2.num_cards_played = 0
                                    run = not check_win(deck)
                                    # check if both players have at least 6 cards in hand
                                    if (player1.num_cards_in_hand < 6):
                                        player1.deal_hand(
                                            6 - player1.num_cards_in_hand)
                                        player1.num_cards_in_hand = len(
                                            player1._hand)
                                    if (player2.num_cards_in_hand < 6):
                                        player2.deal_hand(
                                            6 - player2.num_cards_in_hand)
                                        player2.num_cards_in_hand = len(
                                            player1._hand)

                        # gynejas (zaidejas, paspaudes mygtuka) paeme kortas / gynejas paspaude mygtuka
                        else:
                            undefended_cards = [attacker_card for attacker_card in cards_to_display.keys(
                            ) if cards_to_display[attacker_card] == None]
                            # all cards have NOT been defended (the button was pressed legally)
                            if not len(undefended_cards) == 0:
                                for attacker_card in cards_to_display.keys():
                                    defender._hand.append(attacker_card)
                                for defender_card in cards_to_display.values():
                                    if defender_card != None:
                                        defender._hand.append(defender_card)
                                defender.num_cards_in_hand = len(
                                    defender._hand)
                                player1.toggle_visibility()
                                player2.toggle_visibility()
                                cards_to_display.clear()
                                player1.num_cards_played = 0
                                player2.num_cards_played = 0
                                run = not check_win(deck)
                                # check if both players have at least 6 cards in hand
                                if (player1.num_cards_in_hand < 6):
                                    player1.deal_hand(
                                        6 - player1.num_cards_in_hand)
                                    player1.num_cards_in_hand = len(
                                        player1._hand)
                                if (player2.num_cards_in_hand < 6):
                                    player2.deal_hand(
                                        6 - player2.num_cards_in_hand)
                                    player2.num_cards_in_hand = len(
                                        player1._hand)

            player1.event_handler(event)
            player2.event_handler(event)

        # draw screen
        screen.blit(background_image, (0, 0))
        # pygame.draw.rect(screen, (0, 255, 0), deck_rect)
        if (len(deck.cards) > 0):
            screen.blit(back_of_card, (50, 325))
            back_of_card_text = font.render(
                str(len(deck.cards)), True, (255, 255, 255))
            screen.blit(back_of_card_text, (85, 295))
            deck.trump_card.draw((180, 325))
        elif (len(deck.cards) == 0 and not deck.trump_card_taken):
            deck.trump_card.draw((50, 325))

        # draw buttons
        pygame.draw.rect(screen, (255, 0, 0), quit_button_rect)
        screen.blit(quit_text, (screen_size_x - 110, 30))

        # draw player hand, dragged card and cards played by both players
        for i, player in enumerate(players):
            if player.is_visible():  # this player's turn

                if isDefender(player):  # defender
                    if is_enabled("end_round_button"):  # not all cards defended
                        end_round_button_text = font.render(
                            "Take cards", True, (255, 255, 255))
                        pygame.draw.rect(screen, (0, 0, 255),
                                         end_round_button_rect)
                        screen.blit(end_round_button_text, (screen_size_x -
                                                            150, screen_size_y / 2 + 40))
                    else:  # all cards defended
                        pygame.draw.rect(screen, (0, 255, 0), next_button_rect)
                        screen.blit(next_button_text, (screen_size_x -
                                                       150, screen_size_y / 2 - 10))

                else:  # attacker
                    if is_enabled("next_button"):  # played a card this turn
                        pygame.draw.rect(screen, (0, 255, 0), next_button_rect)
                        screen.blit(next_button_text, (screen_size_x -
                                                       150, screen_size_y / 2 - 10))
                    elif is_enabled("end_round_button"):  # all cards defended
                        end_round_button_text = font.render(
                            "End round", True, (255, 255, 255))
                        pygame.draw.rect(screen, (0, 0, 255),
                                         end_round_button_rect)
                        screen.blit(end_round_button_text, (screen_size_x -
                                                            150, screen_size_y / 2 + 40))

                player.draw_hand(
                    screen, player.hand_position[0], player.hand_position[1])
                opponent = players[1-i]
                player.draw_cards_to_display(
                    screen, isDefender(player), opponent)
                player.update()  # update dragged card position
                player.draw_dragged_card()

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
    unittest.main()
