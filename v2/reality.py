import numpy as np
# import matplotlib.pyplot as plt

# import seed_handler


class World:
    '''
    Class representing the World in which the simulation takes place.
    '''

    def __init__(self, width: int, height: int):
        # seed = seed_handler.load_seed()
        # np.random.seed(seed)

        self.width = width
        self.height = height
        self.tiles = []
        for i in range(width):
            self.tiles.append([])
            for _ in range(height):
                self.tiles[i].append([])
        self.objects = {}  # object id with coordinates
        self.population = []  # list of people created

    def create_person(self, x: int, y: int, parent=None):
        '''
        Initializes and places a new Person in World.

        Parameters:
        x: x-coordinate of the Person
        y: y-coordinate of the Person
        parent: parent of the Person
        '''
        try:
            assert x < self.width
            assert y < self.height
        except AssertionError:
            print(f'PERSON NOT CREATED: object out of bounds ({x},{y})')
            return None
        try:
            assert len(self.tiles[x][y]) == 0
        except AssertionError:
            print(f'PERSON NOT CREATED: object {self.tiles[x][y]} found at '
                  f'({x},{y})')
            return None

        from anthrop import Person
        p = Person(parent)
        # place person
        self.tiles[x][y] = [p]
        self.objects[id(p)] = (x, y)
        self.population.append(p)
        return p

    def attribute_sound(self, source_obj, sound) -> None:
        '''
        Place Sound on its source object in World.

        Parameters:
        source_obj: object from which the Sound is produced
        '''
        if not self.object_exists(source_obj):
            return None

        x, y = self.get_coords(source_obj)
        self.tiles[x][y].append(sound)
        self.objects[id(sound)] = (x, y)

    def object_exists(self, obj) -> bool:
        '''
        Returns True if object exists in the world, False otherwise.

        Parameters:
        obj: object to check for existence
        '''
        try:
            assert id(obj) in self.objects
        except AssertionError:
            print(f'OBJECT NOT FOUND: {obj}')
            return False
        return True

    def get_dist_between(self, obj1, obj2) -> float:
        '''
        Gets distance between two provided objects,
        first checking they exist in the world.
        '''
        for obj in [obj1, obj2]:
            if not self.object_exists(obj):
                return None

        x1, y1 = self.get_coords(obj1)
        x2, y2 = self.get_coords(obj2)
        return self.euclidean_dist(x1, y1, x2, y2)

    def get_nearby_from_object(self, obj, radius: float) -> list:
        '''
        Returns list of nearby objects within a radius relative
        to a provided object.

        Parameters:
        obj: object from which to calculate distance
        radius: distance within which to find nearby objects
        '''
        if not self.object_exists(obj):
            return None

        coords = self.get_coords(obj)
        return self.get_nearby(coords[0], coords[1], radius)

    def get_coords(self, obj) -> tuple:
        '''
        Returns (x,y) coordinate tuple of provided object if found in map.

        Parameters:
        obj: object to find in the map
        '''
        return self.objects.get(id(obj), None)

    def get_nearby(self, x: int, y: int, radius: float) -> list:
        '''
        Returns list of nearby objects within a radius relative
        to provided coordinates.

        Parameters:
        x: x-coordinate from which to calculate distance
        y: y-coordinate from which to calculate distance
        radius: distance within which to find nearby objects
        '''
        from anthrop import Sound
        nearby = []
        for i in range(len(self.tiles)):
            for j in range(len(self.tiles[i])):
                objs = self.tiles[i][j]
                if objs == []:
                    # no objects at this location
                    continue
                dist = self.euclidean_dist(x, y, i, j)
                for obj in objs:
                    if type(obj) is Sound:
                        # inverse relative volume
                        nearby.append([obj, dist/obj.volume])
                    elif dist <= radius:
                        nearby.append([obj, dist])
        return nearby

    def euclidean_dist(self, x1: int, y1: int, x2: int, y2: int) -> float:
        return np.linalg.norm([x1 - x2, y1 - y2])

    def show(self) -> None:
        for y in range(len(self.tiles[0])):
            row = ''
            for x in range(len(self.tiles)):
                t = self.tiles[x][y]
                if t:
                    row += 'x '
                else:
                    row += '• '
            print(row)
