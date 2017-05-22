from random import randint

import pygame


def calc_scroll_freedom():
    q = set()

    rect = pygame.Rect(randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 100))
    parent = pygame.Rect(randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 100))

    if rect.centerx > parent.centerx:
        q.add("right")
    elif rect.centerx < parent.centerx:
        q.add("left")

    if rect.centery > parent.centery:
        q.add("bottom")
    elif rect.centery < parent.centery:
        q.add("top")

    return q


# faster
def calc_scroll_freedom2():
    rect = pygame.Rect(randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 100))
    parent = pygame.Rect(randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 100))

    x = rect.width > parent.width
    y = rect.height > parent.height

    if x and y:
        return {'x', 'y'}
    elif x:
        return {'x'}
    elif y:
        return {'y'}
    else:
        return None


def test():
    """Stupid test function"""
    lst = []
    for i in range(100):
        lst.append(i)


if __name__ == '__main__':
    import timeit

    print(timeit.timeit("calc_scroll_freedom()", setup="from __main__ import calc_scroll_freedom", number=100000))
    print(timeit.timeit("calc_scroll_freedom2()", setup="from __main__ import calc_scroll_freedom2", number=100000))
