import pygame
import random

pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Durak")

deck = pygame.Rect((50, 225, 100, 150))

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
        self.hand = []

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def deal_cards(self):
        self.hand = self.cards[:6]
        self.cards = self.cards[6:]

        print("Hand: ")
        for card in self.hand:
            print(card)
        print("")

        print("Remaining cards in the deck: ")
        for card in self.cards:
            print(card)
        print("")

    def draw_hand(self):
        for i, (rank, suit) in enumerate(self.hand):
            card_image = pygame.image.load(f"Images\\{rank}_of_{suit}.png")
            card_image = pygame.transform.scale(card_image, (100, 150))
            screen.blit(card_image, (i*110, 225))

class Player(Deck):
    pass


deck = Deck()
player1 = Player()
player2 = Player()
player1.deal_cards()
player2.deal_cards()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Durak")

deck = pygame.Rect((50, 225, 100, 150))


def main():

    background_image = pygame.image.load(
        "Images\\green-casino-poker-table-texture-game-background-free-vector.jpg")
    back_of_card = pygame.image.load("Images\\back of the card.jpg")
    back_of_card = pygame.transform.scale(back_of_card, (100, 150))

    run = True

    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        screen.blit(background_image, (0, 0))
        pygame.draw.rect(screen, (255, 255, 255), deck)
        screen.blit(back_of_card, (50, 225))
        player1.draw_hand()
        player2.draw_hand()

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
