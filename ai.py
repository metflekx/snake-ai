from game import Direction, pygame, calculate_distance, Player
import numpy as np
import sys


class AI:
    def __init__(self):
        pass

    def __goes_dead_end(self, state, count, depth): # TODO DEBUG
        return False
        if count > depth:
            return False

        for action in self.__calculate_actions(state):
            next_states = self.__calculate_actions(action)
            for next_state in next_states:
                if self.__goes_dead_end(next_state, count + 1, depth):
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
            if self.__goes_dead_end(state, 0, 10):
                return sys.maxsize

        features = self.__get_features(state)
        return np.dot(features, weights)

    def __calculate_actions(self, state, speed=10):
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

    def __get_features(self, state):
        snake_head = state["snake_head"]
        food = state["food"]
        segments = state["segments"]

        distances = []
        mean_near_segments = 0.0

        if len(segments) > 3:
            for segment in segments:
                distances.append(calculate_distance(snake_head, segment))

            mean_near_segments = np.mean(sorted(distances)[:-3])

        distance_head_food = calculate_distance(snake_head, food)
        mean_near_segments_feature = np.exp( -1 * mean_near_segments ) # exponentialy grows as distance decreases

        features = np.array([distance_head_food, mean_near_segments_feature])

        return features

    def minimize(self, weights, state, snake):
        speed = snake.get_speed()
        actions = self.__calculate_actions(state, speed)
        decision = actions[0]
        index = 0
        
        for i in range(1, len(actions)):
            if self.__calculate_cost(actions[i], weights) < self.__calculate_cost(decision, weights):
                decision = actions[i]
                index = i

        return Direction(index)
