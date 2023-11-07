from game import initialize, Direction
from controls import Controls
pygame = initialize()


class Snake:
    def __init__(self, scr):
        """
        Initialize snake
        :param scr: screen
        """

        self.scr = scr
        self.snake_speed_x = 0.0
        self.snake_speed_y = 0.0
        self.snake_size = 1
        self.segments = []  # queue FIFO
        self.speed = 10
        self.snake_pos = pygame.Vector2(scr.get_width() / 2, scr.get_height() / 2)
        self.snake_head = pygame.Rect(self.snake_pos[0], self.snake_pos[1], 10, 10)

        self.controls = Controls()

    def get_speed(self):
        return self.speed

    def is_collision(self, rectangle):
        """
        Check if snake collided with rectangle
        :param rectangle: rectangle to check
        :return: True if collided, False otherwise
        """

        return self.snake_head.colliderect(rectangle)

    def get_fitness(self):
        """
        Get fitness of snake
        :return: fitness
        """

        return self.snake_size

    def game_over(self):
        """
        Check if snake collided with itself
        :return: True if collided, False otherwise
        """

        for seg in self.segments:
            if self.is_collision(seg):
                return True

        return False

    def get_big(self):
        """
        Make snake bigger
        :return: None
        """

        self.snake_size += 10

    def set_direction(self, direction):
        """
        Set direction of snake
        :param direction: direction to set
        :return: None
        """

        self.controls.direction = direction

    def update(self):
        """
        Update snake
        :return: None
        """
        # update segments and size of snake
        self.segments.append(pygame.Rect(self.snake_pos[0], self.snake_pos[1], 10, 10))
        if len(self.segments) >= self.snake_size:
            self.segments.pop(0)

        # update direction
        self.controls.listener()
        if self.controls.direction == Direction.RIGHT:
            self.snake_speed_x = 1 * self.speed
            self.snake_speed_y = 0
        if self.controls.direction == Direction.LEFT:
            self.snake_speed_x = -1 * self.speed
            self.snake_speed_y = 0
        if self.controls.direction == Direction.UP:
            self.snake_speed_x = 0
            self.snake_speed_y = -1 * self.speed
        if self.controls.direction == Direction.DOWN:
            self.snake_speed_x = 0
            self.snake_speed_y = self.speed
        self.snake_pos[0] += self.snake_speed_x # update position
        self.snake_pos[1] += self.snake_speed_y

        # teleport from one side to another
        if self.snake_pos[0] < 0:
            self.snake_pos[0] = self.scr.get_width()
        if self.snake_pos[0] > self.scr.get_width():
            self.snake_pos[0] = 0
        if self.snake_pos[1] < 0:
            self.snake_pos[1] = self.scr.get_height()
        if self.snake_pos[1] > self.scr.get_height():
            self.snake_pos[1] = 0


        # update snake head
        self.snake_head = pygame.Rect(self.snake_pos[0], self.snake_pos[1], 10, 10)
