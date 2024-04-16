import pygame
pygame.init()

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

        pygame.draw.rect(screen, (255, 255, 255), deck)
        screen.blit(back_of_card, (50, 225))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

        screen.blit(background_image, (0, 0))

    pygame.quit()


if __name__ == "__main__":
    main()