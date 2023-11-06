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

        self.snake = Snake(self.scr)
        self.AI = AI()

    def get_state(self):
        return self.state

    def main(self, weights):
        # initialize game objects
        self.scr = pygame.display.set_mode((self.scr_width, self.scr_height))
        self.clock = pygame.time.Clock()
        self.dt = 0.0
        self.running = True
        self.food = pygame.Rect(0, 0, 0, 0)
        self.is_food = False

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
                print("GAME OVER")

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
        parameters = np.array([100.0, 10.0])
        game.main(parameters)
    
    def play_human():
        game = Game("HUMAN")
        game.main(np.array([0.0, 0.0]))
    
    play_ai()
    # play_human()

# TODO
    # def run_main(parameters):
    #     fitnesses = []
    #     for _ in range(2):
    #         fitnesses.append(main(parameters))

    #     return np.mean(fitnesses)

    # def learn(self):
    #     self.Player = self.Player.train

    #     parameters = np.ones(7, dtype=np.float64)
    #     fitness = 0.0
    #     return parameters
