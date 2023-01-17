import numpy as np
# import matplotlib.pyplot as plt

import seed_handler

class World:
    def __init__(self, width:int, height:int, seed:int):
        seed = seed_handler.load_seed()
        np.random.seed(seed)

        self.width = width
        self.height = height
        self.tiles = []
        for i in range(width):
            self.tiles.append([])
            for _ in range(height):
                self.tiles[i].append(None)
        self.objects = {}  # object id with coordinates

    def create_person(self, x:int, y:int, parent=None):
        '''
        Inits and places a new Person in World.
        '''
        if self.tiles[x][y]:
            print(self.tiles[x][y])
            print(f'PERSON NOT CREATED - object found at ({x},{y})')
            return None
        import anthrop
        p = anthrop.Person(parent)
        self.tiles[x][y] = p
        self.objects[id(p)] = (x, y)
        return p

    def get_dist_between(self, obj1, obj2) -> float:
        '''
        Gets distance between two provided objects, first checking they exist in the world.
        '''
        assert id(obj1) in self.objects
        assert id(obj2) in self.objects
        
        x1, y1 = self.objects[id(obj1)]
        x2, y2 = self.objects[id(obj2)]
        return self.euclidean_dist(x1, y1, x2, y2)

    def get_coords(self, obj) -> tuple:
        '''
        Returns (x,y) coordinate tuple of provided object if found in map.
        '''
        return self.objects.get(id(obj))

    def get_nearby_from_object(self, obj, radius:float) -> list:
        '''
        Returns list of nearby objects within a radius relative to a provided object.
        '''
        coords = self.get_coords(obj)
        if not coords:
            return []
        return self.get_nearby(coords[0], coords[1], radius)

    def get_nearby(self, x:int, y:int, radius:float) -> list:
        '''
        Returns list of nearby objects within a radius relative to provided coordinates.
        '''
        nearby = []
        for i in range(len(self.tiles)):
            for j in range(len(self.tiles[0])):
                dist = self.euclidean_dist(x, y, i, j)
                if dist > radius:
                    pass
                obj = self.tiles[i][j]
                if obj: nearby.append([obj, dist])
        return nearby

    def euclidean_dist(self, x1:int, y1:int, x2:int, y2:int) -> float:
        return np.sqrt((x1-x2)**2+(y1-y2)**2)

    def show(self) -> None:
        for y in range(len(self.tiles[0])):
            row = ''
            for x in range(len(self.tiles)):
                t = self.tiles[x][y]
                # print(t)
                if not t:
                    row += '• '
                else:
                    row += 'x '
            print(row)