from game import initialize, Direction
pygame = initialize()


class Controls:
    def __init__(self):
        """
        Initialize controls
        """

        self.direction = Direction.MAX

    def listener(self):
        """
        Listen for key presses
        :return: None
        """

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and self.direction != Direction.LEFT:
            self.direction = Direction.RIGHT
        if keys[pygame.K_a] and self.direction != Direction.RIGHT:
            self.direction = Direction.LEFT
        if keys[pygame.K_w] and self.direction != Direction.DOWN:
            self.direction = Direction.UP
        if keys[pygame.K_s] and self.direction != Direction.UP:
            self.direction = Direction.DOWN
