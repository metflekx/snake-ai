import pygame
from enum import Enum
from math import sqrt


class Player(Enum):
    HUMAN  = 1
    AI     = 2
    TRAIN  = 3
    MAX    = 4

class Direction(Enum):
    """ 
    Direction of snake
    """

    RIGHT = 0
    LEFT  = 1
    DOWN  = 2
    UP    = 3
    MAX   = 4

def calculate_distance(a, b):
    """
    Calculate distance between two points 
    :param a: point a
    :param b: point b
    :return: distance between a and b
    """

    return sqrt(((a.x - b.x) ** 2) + ((a.y - b.y) ** 2))

def initialize():
    """
    Initialize pygame
    :return: pygame
    """

    pygame.init()
    return pygame
