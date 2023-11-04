import pygame
import random
import numpy as np

from math import sqrt
from enum import Enum
import sys


class Snake:
    class Player(Enum):
        human  = 1
        ai     = 2
        train  = 3

    class Direction(Enum):
        right = 0
        left  = 1
        down  = 2
        up    = 3

    def __init__(self):
        self.player = self.Player.human
        self.scr_width = 1280 / 2  
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
        self.state = {}
        self.speed = 10

    def get_speed(self):
        return self.speed

    def get_state(self):
        return self.state

    @staticmethod
    def __calculate_distance(a, b):
        return sqrt(((a.x - b.x) ** 2) + ((a.y - b.y) ** 2))

    def __get_features(self, state):
        snake_head = state["snake_head"]
        food = state["food"]
        segments = state["segments"]

        distances = []
        mean_near_segments = 0.0

        if len(segments) > 3:

            for segment in segments:
                distances.append(self.__calculate_distance(snake_head, segment))

            mean_near_segments = np.mean(sorted(distances)[:-3])

        distance_head_food = self.__calculate_distance(snake_head, food)
        mean_near_segments_feature = np.exp( -1 * mean_near_segments ) # exponentialy grows as distance decreases

        features = np.array([distance_head_food, mean_near_segments_feature])

        return features

    def goes_dead_end(self, state, count, depth): # TODO DEBUG
        if count > depth:
            return False

        for action in self.__calculate_actions(state):
            next_states = self.__calculate_actions(action)
            for next_state in next_states:
                if self.goes_dead_end(next_state, count + 1, depth):
                    return True

            head = action["snake_head"]
            segments = action["segments"]

            for segment in segments:
                if head.colliderect(segment):
                    break

        return True

    def __calculate_cost(self, state, weights):
        head = state["snake_head"]
        segments = state["segments"]

        if segments:
            # if action cuases collision, return a big cost
            for segment in segments:
                if head.colliderect(segment):
                    return sys.maxsize

            # if actions next possible actions cuase collision, return a big cost
            if self.goes_dead_end(state, 0, 10):
                print("dead end")
                return sys.maxsize

        features = self.__get_features(state)
        return np.dot(features, weights)

    def __calculate_actions(self, state):
        speed = self.get_speed()

        sample_space = [
            {"snake_head": pygame.Rect(state["snake_head"].x + speed, state["snake_head"].y, 10, 10),
             "food": state["food"], "segments": state["segments"]},
            {"snake_head": pygame.Rect(state["snake_head"].x - speed, state["snake_head"].y, 10, 10),
             "food": state["food"], "segments": state["segments"]},
            {"snake_head": pygame.Rect(state["snake_head"].x, state["snake_head"].y + speed, 10, 10),
             "food": state["food"], "segments": state["segments"]},
            {"snake_head": pygame.Rect(state["snake_head"].x, state["snake_head"].y - speed, 10, 10),
             "food": state["food"], "segments": state["segments"]}]

        return sample_space

    def __minimize(self, weights):
        speed = self.get_speed()

        actions = self.__calculate_actions(self.state)
        decision = actions[0]
        index = 0
        
        for i in range(1, len(actions)):
            if self.__calculate_cost(actions[i], weights) < self.__calculate_cost(decision, weights):
                decision = actions[i]
                index = i

        return self.Direction(index)

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

            for segment in self.segments:
                if self.snake_head.colliderect(segment):
                    return self.snake_size

            if self.snake_pos[0] < 0 or self.snake_pos[0] > self.scr.get_width() or self.snake_pos[1] < 0 or self.snake_pos[1] > self.scr.get_height():
                self.snake_pos = pygame.Vector2(self.scr.get_width() / 2, self.scr.get_height() / 2)

            self.state = {"snake_head": self.snake_head, "segments": self.segments, "food": self.food}

            # set speed
            speed = self.get_speed()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_d] and self.direction != self.Direction.left:
                self.direction = self.Direction.right
            if keys[pygame.K_a] and self.direction != self.Direction.right:
                self.direction = self.Direction.left 
            if keys[pygame.K_s] and self.direction != self.Direction.up:
                self.direction = self.Direction.down 
            if keys[pygame.K_w] and self.direction != self.Direction.down:
                self.direction = self.Direction.up

            if self.Player != self.Player.human:
                self.direction = self.__minimize(weights)

            if self.direction == self.Direction.right:
                self.snake_speed_x = speed
                self.snake_speed_y = 0

            if self.direction == self.Direction.left:
                self.snake_speed_x = -1 * speed
                self.snake_speed_y = 0

            if self.direction == self.Direction.down:
                self.snake_speed_x = 0
                self.snake_speed_y = speed

            if self.direction == self.Direction.up:
                self.snake_speed_x = 0
                self.snake_speed_y = -1 * speed

            if self.snake_head.colliderect(self.food):
                self.is_food = False
                self.snake_size += 10

            for segment in self.segments:
                pygame.draw.rect(self.scr, "blue", segment)
            pygame.draw.rect(self.scr, "white", self.snake_head)
            pygame.draw.rect(self.scr, "red", self.food) 
            pygame.display.flip()

            fps = 1000 if self.Player == self.Player.train else 50
            self.dt = self.clock.tick(fps)

        pygame.quit()

    def playAI(self, parameters):
        self.Player = self.Player.ai
        self.main(parameters)

    def play_player(self):
        self.Player = self.Player.human
        empty_array = np.array([[1], [1]])
        self.main(empty_array)

    # def run_main(parameters):
    #     fitnesses = []
    #     for _ in range(2):
    #         fitnesses.append(main(parameters))

    #     return np.mean(fitnesses)

    # def learn(self):
    #     self.Player = self.Player.train

    #     parameters = np.ones(7, dtype=np.float64)
    #     fitness = 0.0

    #     


    #     return parameters

if __name__ == "__main__":
    snake = Snake()
    # parameters = snake.learn()
    parameters = np.array([100.0, 10.0]) # , 10000.0]) # , 4.0, 8.0, 16.0, 32.0, 64.0])
    snake.playAI(parameters)

    # print(parameters)
    # snake.play_player()
