import pygame
import random
from abc import ABC, abstractmethod

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)


class Cards:
    def __init__(self):
        self.rank = ("2", "3", "4", "5", "6", "7", "8",
                     "9", "10", "J", "Q", "K", "A")
        self.suit = ("spades", "diamonds", "clubs", "hearts")
        self.cards = []

    def create_cards(self):
        for rank in self.rank:
            for suit in self.suit:
                self.cards.append((rank, suit))

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

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def deal_cards(self, num_cards):
        hand = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return hand

    def trump_card(self):
        if self.cards:
            return self.cards.pop(0)
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

    @abstractmethod
    def deal_hand(self, num_cards):
        pass

    def toggle_visibility(self):
        self._visible = not self._visible

    def is_visible(self):
        return self._visible

    def draw_hand(self, screen, y_position, offset):
        for i, (rank, suit) in enumerate(self.hand):
            card_image = pygame.image.load(
                f"Images\\{rank}_of_{suit}.png").convert_alpha()
            card_image = pygame.transform.scale(card_image, (100, 150))
            card_rect = card_image.get_rect()
            card_rect.topleft = (i*110 + offset, y_position)
            screen.blit(card_image, card_rect)

    @abstractmethod
    def event_handler(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw_dragged_card(self, screen):
        pass


class TurnManager(metaclass=SingletonMeta):

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.defender = self.player2
        


class Player(AbstractPlayer):
    def __init__(self, deck, hand_position):
        super().__init__(deck)
        self.hand_position = hand_position
        self.cards_to_display = []
        self.cards_played = 0

    def deal_hand(self, num_cards):
        self.hand = self.deck.deal_cards(num_cards)

    def event_handler(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for i, (rank, suit) in enumerate(self.hand):
                    card_rect = pygame.Rect(
                        i*110 + self.hand_position[0], self.hand_position[1], 100, 150)
                    if card_rect.collidepoint(mouse_pos):
                        if not self._dragging:
                            self._dragging = True
                            self._dragged_card = (rank, suit)
                            self._original_index = i
                            return

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging:
                self._dragging = False
                if len(self.cards_to_display) == 0:
                    card = self.hand.pop(self._original_index)
                    self.cards_to_display.append(card)
                    self.cards_played += 1
                    self._dragged_card = None
                    self._original_index = None
                else:
                    if not self.check_boundaries(screen) == -1:
                        card = self.hand.pop(self._original_index)
                        self.cards_to_display.append(card)
                        self.cards_played += 1
                        self._dragged_card = None
                        self._original_index = None

    def update(self):
        if self._dragging:
            mouse_pos = pygame.mouse.get_pos()
            self._dragged_card_pos = mouse_pos

    def draw_dragged_card(self, screen):
        if self._dragging and self._dragged_card is not None:
            rank, suit = self._dragged_card
            card_image = pygame.image.load(
                f"Images\\{rank}_of_{suit}.png").convert_alpha()
            card_image = pygame.transform.scale(card_image, (100, 150))
            card_rect = card_image.get_rect()
            card_rect.center = pygame.mouse.get_pos()
            screen.blit(card_image, card_rect)

    def draw_cards_to_display(self, screen, isDefender):
        card_width = 100
        stack_gap = 20
        card_overlap_gap = 40

        initial_x = screen.get_width() // 2 - ((self.cards_played - 1)
                                               * (card_width + stack_gap) // 2)
        initial_y = screen.get_height() // 2 + isDefender * card_overlap_gap

        for i, card in enumerate(self.cards_to_display):
            rank, suit = card
            card_image = pygame.image.load(
                f"Images\\{rank}_of_{suit}.png").convert_alpha()
            card_image = pygame.transform.scale(card_image, (100, 150))
            if isDefender:
                card_rect = card_image.get_rect()
                card_rect.centerx = initial_x + (self.check_boundaries(screen) * (card_width + stack_gap))
            else:
                card_rect = card_image.get_rect()
                card_rect.centerx = initial_x + (i * (card_width + stack_gap))
            card_rect.centery = initial_y
            screen.blit(card_image, card_rect)

    def check_boundaries(self, screen):
        card_height = 150
        card_width = 100
        stack_gap = 20

        mouse_pos = pygame.mouse.get_pos()

        initial_x = screen.get_width() // 2 - ((self.cards_played - 1)
                                               * (card_width + stack_gap) // 2)
        initial_y = screen.get_height() // 2
        
        for i, card in enumerate(self.cards_to_display):
            if initial_x + (i * (card_width + stack_gap)) - card_width // 2 <= mouse_pos[0] <= initial_x + (i * (card_width + stack_gap)) + card_width // 2 and initial_y - card_height // 2 <= mouse_pos[1] <= initial_y + card_height // 2:
                return i
        return -1
        
        


def isDefender(player, defender):
    if defender == player:
        return 1
    else:
        return 0


def main():

    screen_size_x = screen.get_width()
    screen_size_y = screen.get_height()
    pygame.display.set_caption("Durak")

    quit_button_rect = pygame.Rect((screen_size_x - 120, 20, 100, 40))
    font = pygame.font.SysFont(None, 32)
    quit_text = font.render("Quit", True, (255, 255, 255))

    next_button_rect = pygame.Rect(
        (screen_size_x - 160, screen_size_y / 2 - 20, 140, 40))
    next_button_text = font.render("Next turn", True, (255, 255, 255))

    deck_rect = pygame.Rect((50, 325, 100, 150))
    deck = Deck()
    player1_hand_position = (400, screen_size_y - 250)
    player2_hand_position = (400, 100)
    player1 = Player(deck, player1_hand_position)
    player2 = Player(deck, player2_hand_position)

    turnManager = TurnManager(player1, player2)

    player1.deal_hand(6)
    player2.deal_hand(6)

    trump_card = deck.trump_card()
    if trump_card:
        trump_image = pygame.image.load(
            f"Images\\{trump_card[0]}_of_{trump_card[1]}.png")
        trump_image = pygame.transform.scale(trump_image, (100, 150))

    background_image = pygame.image.load(
        "Images\\green-casino-poker-table-texture-game-background-free-vector.jpg")
    background_image = pygame.transform.scale(
        background_image, (screen_size_x, screen_size_y))
    back_of_card = pygame.image.load("Images\\back of the card.jpg")
    back_of_card = pygame.transform.scale(back_of_card, (100, 150))

    run = True

    player1_visible = True
    player2_visible = False

    while run:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if turnManager.defender == player1:
                        turnManager.defender = player2
                    else:
                        turnManager.defender = player1

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and quit_button_rect.collidepoint(event.pos):
                    run = False
                elif event.button == 1 and next_button_rect.collidepoint(event.pos):
                    player1.toggle_visibility()
                    player2.toggle_visibility()
                    player1_visible = not player1_visible
                    player2_visible = not player2_visible

            player1.event_handler(event)
            player2.event_handler(event)

        player1.update()
        player2.update()

        screen.blit(background_image, (0, 0))
        pygame.draw.rect(screen, (255, 255, 255), deck_rect)
        screen.blit(back_of_card, (50, 325))
        screen.blit(trump_image, (180, 325))
        if player1_visible:
            player1.draw_hand(
                screen, player1_hand_position[1], player1_hand_position[0])
        if player2_visible:
            player2.draw_hand(
                screen, player2_hand_position[1], player2_hand_position[0])

        player1.draw_dragged_card(screen)
        player2.draw_dragged_card(screen)

        player1.draw_cards_to_display(
            screen, isDefender(turnManager.defender, player1))
        player2.draw_cards_to_display(
            screen, isDefender(turnManager.defender, player2))

        pygame.draw.rect(screen, (255, 0, 0), quit_button_rect)
        screen.blit(quit_text, (screen_size_x - 110, 30))

        pygame.draw.rect(screen, (0, 255, 0), next_button_rect)
        screen.blit(next_button_text, (screen_size_x -
                    150, screen_size_y / 2 - 10))

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
    