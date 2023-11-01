import pygame
import random
import numpy as np
from math import sqrt
from enum import Enum

class Snake:
    class Player(Enum):
        human  = 1
        ai     = 2
        train  = 3

    def __init__(self):
        self.player = self.Player.human
        self.scr_width = 1280 / 2  # TODO DEBUG
        self.scr_height = 720 / 2
        self.scr = pygame.display.set_mode((self.scr_width, self.scr_height))
        self.clock = pygame.time.Clock()
        self.dt = 0.0
        self.running = True
        self.food = pygame.Rect(0, 0, 0, 0)
        self.is_food = False
        self.direction = 4
        self.snake_pos = pygame.Vector2(self.scr.get_width() / 2, self.scr.get_height() / 2)
        self.snake_head = pygame.Rect(self.snake_pos[0], self.snake_pos[1], 10, 10)
        self.snake_speed_x = 0.0
        self.snake_speed_y = 0.0
        self.snake_size = 1
        self.segments = []  # queue FIFO

    def calculate_distance(self, a, b):
        return sqrt(((a.x - b.x) ** 2) + ((a.y - b.y) ** 2))

    def normalize(self, x):
        return 1.0 / (1.0 + x)

    def calculate_cost(self, state, weights):
        snake_head = state["snake_head"]
        food = state["food"]
        segments = state["segments"]
        distance_head_segment = 1.0

        distances = []
        distance_head_segment = -10000

        if len(segments) > 3:
            for segment in segments[:-2]:
                distances.append(self.calculate_distance(snake_head, segment))

            nearest_segment = min(distances)
            distance_head_segment = np.exp(-1 * nearest_segment)

        distance_head_food = self.calculate_distance(snake_head, food)

        features = np.array([distance_head_food, distance_head_segment])

        return (np.dot(features, weights) ** 2) / 2.0

    def calculate_actions(self, state, speed):
        sample_space = [state] * 4
        sample_space = [
            {"snake_head": pygame.Rect(state["snake_head"].x + speed, state["snake_head"].y, 10, 10),
             "food": state["food"], "segments": state["segments"]},
            {"snake_head": pygame.Rect(state["snake_head"].x - speed, state["snake_head"].y, 10, 10),
             "food": state["food"], "segments": state["segments"]},
            {"snake_head": pygame.Rect(state["snake_head"].x, state["snake_head"].y + speed, 10, 10),
             "food": state["food"], "segments": state["segments"]},
            {"snake_head": pygame.Rect(state["snake_head"].x, state["snake_head"].y - speed, 10, 10),
             "food": state["food"], "segments": state["segments"]}
        ]

        return sample_space

    def minimize(self, state, speed, weights):
        actions = self.calculate_actions(state, speed)
        decision = state

        index = 0
        i = 0
        for i in range(len(actions)):
            if self.calculate_cost(actions[i], weights) < self.calculate_cost(decision, weights):
                decision = actions[i]
                index = i

        return index  # right, left, down, up

    def main(self, weights):
        pygame.init()

        self.scr = pygame.display.set_mode((self.scr_width, self.scr_height))

        self.clock = pygame.time.Clock()
        self.dt = 0.0
        self.running = True

        self.food = pygame.Rect(0, 0, 0, 0)
        self.is_food = False

        self.direction = 4

        self.snake_pos = pygame.Vector2(self.scr.get_width() / 2, self.scr.get_height() / 2)
        self.snake_head = pygame.Rect(self.snake_pos[0], self.snake_pos[1], 10, 10)
        self.snake_speed_x = 0.0
        self.snake_speed_y = 0.0
        self.snake_size = 1
        self.segments = []  # queue FIFO

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.scr.fill("black")

            if not self.is_food:
                food_pos = pygame.Vector2(
                    random.uniform(0, self.scr.get_width()),
                    random.uniform(0, self.scr.get_height()))
                self.food = pygame.Rect(food_pos[0], food_pos[1], 10, 10)
                self.is_food = True

            self.segments.append(pygame.Rect(self.snake_pos[0], self.snake_pos[1], 10, 10))
            if len(self.segments) >= self.snake_size:
                self.segments.pop(0)

            self.snake_pos[0] += self.snake_speed_x
            self.snake_pos[1] += self.snake_speed_y

            self.snake_head = pygame.Rect(self.snake_pos[0], self.snake_pos[1], 10, 10)

            for segment in self.segments[:-2]:
                if collision := self.snake_head.colliderect(segment):
                    print("Score: ", self.snake_size)

            if self.snake_pos[0] < 0 or self.snake_pos[0] > self.scr.get_width() or self.snake_pos[1] < 0 or self.snake_pos[1] > self.scr.get_height():
                self.snake_pos = pygame.Vector2(self.scr.get_width() / 2, self.scr.get_height() / 2)

            state = {"snake_head": self.snake_head, "segments": self.segments, "food": self.food}

            if self.Player == self.Player.train:
                speed = 10.0
            else:
                k = 5.0 
                divisor = 15.0
                speed = (k * self.dt) / divisor

            keys = pygame.key.get_pressed()
            if keys[pygame.K_d] and self.direction != 1:
                self.direction = 0
            if keys[pygame.K_a] and self.direction != 0:
                self.direction = 1
            if keys[pygame.K_s] and self.direction != 3:
                self.direction = 2
            if keys[pygame.K_w] and self.direction != 2:
                self.direction = 3

            if self.Player != self.Player.human:
                self.direction = self.minimize(state, speed, weights)

            if self.direction == 0:
                self.snake_speed_x = speed
                self.snake_speed_y = 0

            if self.direction == 1:
                self.snake_speed_x = -1 * speed
                self.snake_speed_y = 0

            if self.direction == 2:
                self.snake_speed_x = 0
                self.snake_speed_y = speed

            if self.direction == 3:
                self.snake_speed_x = 0
                self.snake_speed_y = -1 * speed

            if collision := self.snake_head.colliderect(self.food):
                self.is_food = False
                self.snake_size += 10

            for segment in self.segments:
                pygame.draw.rect(self.scr, "blue", segment)
            pygame.draw.rect(self.scr, "white", self.snake_head)
            pygame.draw.rect(self.scr, "red", self.food) 
            pygame.display.flip()

            fps = 1000 if self.Player == self.Player.train else 60
            self.dt = self.clock.tick(fps)

        pygame.quit()

    def a(self, w1, w2):
        return np.array([w1, w2])

    def run(self, arr):
        fitnesses = []
        for _ in range(5):
            fitnesses.append(self.main(self.a(arr[0], arr[1])))
        return np.mean(fitnesses)

    def playAI(self, parameters):
        self.Player = self.Player.ai
        self.main(parameters)

    def learn(self):
        self.Player = self.Player.train
        bestw1 = 0.0
        bestw2 = 0.0
        best = 0.0

        while best < 400:
            w1 = random.uniform(0, 1000.0)
            w2 = random.uniform(-1000.0, 0)

            current = self.run(self.a(w1, w2))
            if current > best:
                best = current
                bestw1 = w1
                bestw2 = w2

        for _ in range(10):
            w1 = random.uniform(bestw1 - 10.0, bestw1 + 10.0)
            w2 = random.uniform(bestw2 - 10.0, bestw2 + 10.0)

            current = self.run(self.a(w1, w2))
            if current > best:
                best = current
                bestw1 = w1
                bestw2 = w2

        for _ in range(10):
            w1 = random.uniform(bestw1 - 1.0, bestw1 + 1.0)
            w2 = random.uniform(bestw2 - 1.0, bestw2 + 1.0)

            current = self.run(self.a(w1, w2))
            if current > best:
                best = current
                bestw1 = w1
                bestw2 = w2

        return np.array([bestw1, bestw2])

    def play_player(self):
        self.Player = self.Player.human
        empty_array = np.array([[1], [1]])
        self.main(empty_array)

if __name__ == "__main__":
    snake = Snake()
    # parameters = snake.learn()
    parameters = np.array([900, -180])
    snake.playAI(parameters)
    # snake.play_player()
