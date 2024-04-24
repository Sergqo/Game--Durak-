import pygame
import random
from abc import ABC, abstractmethod

pygame.init()


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

class Player(AbstractPlayer):
    def __init__(self, deck, hand_position):
        super().__init__(deck)
        self.hand_position = hand_position
        self.cards_to_display = []
        self.cards_played = 0

    def deal_hand(self, num_cards):
        self.hand = self.deck.deal_cards(num_cards)

    def event_handler(self, event):
        offset_y = 20
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for i, (rank, suit) in enumerate(self.hand):
                    card_rect = pygame.Rect(i*110 + self.hand_position[0], self.hand_position[1], 100, 150)
                    if card_rect.collidepoint(mouse_pos):
                        if not self._dragging:
                            self._dragging = True
                            self._dragged_card = (rank, suit)
                            self._original_index = i
                            return

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging:
                self._dragging = False
                if 400 <= event.pos[0] <= 1000 and 100 <= event.pos[1] <= 750:
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

    def draw_cards_to_display(self, screen):
        initial_x = screen.get_width() // 2
        initial_y = screen.get_height() // 2

        card_width = 100
        stack_gap = 20
        offset_y = 20


        for i, card in enumerate(self.cards_to_display):
            rank, suit = card
            card_image = pygame.image.load(
                f"Images\\{rank}_of_{suit}.png").convert_alpha()
            card_image = pygame.transform.scale(card_image, (100, 150))
            card_rect = card_image.get_rect()
            card_rect.centerx = initial_x + (i * (card_width + stack_gap))
            card_rect.centery = initial_y + self.cards_played * offset_y
            screen.blit(card_image, card_rect)


def main():

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Durak")

    quit_button_rect = pygame.Rect((screen.get_width() - 120, 20, 100, 40))
    font = pygame.font.SysFont(None, 32)
    quit_text = font.render("Quit", True, (255, 255, 255))

    next_button_rect = pygame.Rect(
        (screen.get_width() - 160, screen.get_height() / 2 - 20, 140, 40))
    next_button_text = font.render("Next turn", True, (255, 255, 255))

    deck_rect = pygame.Rect((50, 325, 100, 150))
    deck = Deck()
    player1 = Player(deck, (400, 550))
    player2 = Player(deck, (400, 100))

    player1.deal_hand(6)
    player2.deal_hand(6)

    trump_card = deck.trump_card()
    if trump_card:
        trump_image = pygame.image.load(
            f"Images\\{trump_card[0]}_of_{trump_card[1]}.png")
        trump_image = pygame.transform.scale(trump_image, (100, 150))

    background_image = pygame.image.load(
        "Images\\green-casino-poker-table-texture-game-background-free-vector.jpg")
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
            player1.draw_hand(screen, 550, 400)
        if player2_visible:
            player2.draw_hand(screen, 100, 400)

        player1.draw_dragged_card(screen)
        player2.draw_dragged_card(screen)

        player1.draw_cards_to_display(screen)
        player2.draw_cards_to_display(screen)

        pygame.draw.rect(screen, (255, 0, 0), quit_button_rect)
        screen.blit(quit_text, (screen.get_width() - 110, 30))

        pygame.draw.rect(screen, (0, 255, 0), next_button_rect)
        screen.blit(next_button_text, (screen.get_width() -
                    150, screen.get_height() / 2 - 10))

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
