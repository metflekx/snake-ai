from game import initialize, calculate_distance, Direction, Player
pygame = initialize()

import random
import numpy as np
from enum import Enum
import sys


from snake import Snake
from ai import AI


class Game:
    def __init__(self, player):
        """
        Initialize game
        :param player: player type
        """

        self.player = Player[player]
        self.scr_width = 1280 / 2  
        self.scr_height = 720 / 2
        self.scr = pygame.display.set_mode((self.scr_width, self.scr_height))
        self.clock = pygame.time.Clock()
        self.dt = 0.0
        self.running = True
        self.food = pygame.Rect(0, 0, 0, 0)
        self.is_food = False
        self.state = {}

        self.snake = Snake(self.scr, self.player)
        self.AI = AI()

    def main(self, weights):
        """
        runs the game loop.
        :param weights: weights for the AI
        :return: fitness of the snake
        """

        # game loop
        while self.running:
            for event in pygame.event.get(): # event loop
                if event.type == pygame.QUIT:
                    self.running = False

            self.scr.fill("black") # fill screen

            if not self.is_food:
                food_pos = pygame.Vector2(
                    random.uniform(0, self.scr.get_width()),
                    random.uniform(0, self.scr.get_height()))
                self.food = pygame.Rect(food_pos[0], food_pos[1], 10, 10)
                self.is_food = True

            # obtain state dictionary
            self.state = {"snake_head": self.snake.snake_head, "segments": self.snake.segments, "food": self.food}
            
            if self.player == Player.AI or self.player == Player.TRAIN:
                self.snake.set_direction(self.AI.minimize(weights, self.state, self.snake))

            # set speed
            self.snake.update()

            # collision with food
            if self.snake.is_collision(self.food):
                self.is_food = False
                self.snake.get_big()

            if self.snake.game_over():
                return self.snake.get_fitness() 

            # Render
            for segment in self.snake.segments:
                pygame.draw.rect(self.scr, "blue", segment)
            pygame.draw.rect(self.scr, "white", self.snake.snake_head)
            pygame.draw.rect(self.scr, "red", self.food) 
            pygame.display.flip()

            fps = 1000 if self.player == Player.TRAIN else 50
            self.dt = self.clock.tick(fps)

        pygame.quit()


# TESTING CODE
if __name__ == "__main__":
    def play_ai():
        game = Game("AI")
        parameters = np.array([50.0, 10.0])
        fitness = game.main(parameters)
        print(f"for parameters {parameters} fitness is -> {fitness}")
    
    def play_human():
        game = Game("HUMAN")
        game.main(np.array([0.0, 0.0]))

    def play_train():
        fitness = 0.0
        parameters = np.array([0.0, 0.0])

        while fitness < 200:
            parameters = np.array([random.randint(0.0, 100.0),
                                   random.randint(0.0, 10.0)])
    
            game = Game("TRAIN")
            fitnesses = []
            for _ in range(3): # avoiding lucky/unlucky fitnesses
                fitnesses.append(game.main(parameters))
            fitness = np.mean(fitnesses)

        print(f"for parameters {parameters} fitness is -> {fitness}")

    play_ai()
    # play_human()
    # play_train() 
