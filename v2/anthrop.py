import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

import seed_handler
from reality import World

# Human eyes operate at 60fps -> 60 perceives/sec * 60 sec/min * 60 min/hour = 216000 perceives/hour
PERCEIVES_PER_HOUR = 21600  # decreased for performance reasons

class Memory:
    '''
    Encodes an object with a diminishing salience connected to other memories.
    '''
    def __init__(self, object, salience:float):
        self.object = object
        self.salience = salience
        self.age = 0
        self.base_salience = salience
        self.connections = {}
    
    def connect(self, memory, strength:float) -> None:
        '''
        Connects other Memory to this Memory with a provided strength.
        ---
        memory: other Memory to connect to this Memory
        strength: strength of connection between this Memory and the provided memory
        '''
        if memory not in self.connections:
            self.connections[memory] = 0
        self.connections[memory] += strength

    def get_strength(self, memory):
        '''
        Returns the strength of the connection from this Memory to other Memory.
        '''
        return self.connections[memory]

    def __str__(self):
        return f'{self.object}'

    def __repr__(self):
        return f'{self.object}:{round(self.salience, 4)}'
    
    def __hash__(self):
        return hash(id(self.object))

    def __eq__(self, __o: object) -> bool:
        if type(__o) is not Memory:
            return False
        return __o.object is self.object

    def decay_function(age:float) -> float:
        '''
        Returns percentage left of memory based on memory age, modeling decay.
        Based on Jiang-Shedd hourly memory decay approximation.
        '''
        age_in_hours = age/PERCEIVES_PER_HOUR
        if age_in_hours < 1:
            return np.e**(-0.7*age_in_hours)
        else:
            return np.e**(-0.7*age_in_hours**(1/6))

# class VisualMemory(Memory):
#     def __init__(self, object, salience:float):
#         super(object, salience)

# class AudioMemory(Memory):
#     def __init__(self, object, salience:float):
#         super(object, salience)
    


class Mind:
    '''
    Holds the memories of a Person and allows them to intelligently function.
    '''
    def __init__(self, capacity:float, att_span:float, stm_thresh:float):
        '''
        capacity: space available for memories in long term memory
        att_span: attention span for focus, float between [0, 1]
        stm_thresh: threshold for a memory to stay in short term memory
        '''
        assert att_span >= 0 and att_span <= 1

        self.capacity = capacity
        self.att_span = att_span
        self.stm_thresh = stm_thresh
        self.focus = [None, None]
        self.ltm = set()  # long term memory
        self.stm = set()  # short term memory (more salient)

    def set_focus(self, perceiving:list, horizon:float):
        '''
        Moves focus based on attention span and distance of percepts from Person
        ---
        perceiving: list of perceived objects in environment with relative distances
        horizon: max perceivable distance from Person
        '''
        # attention span determines whether focus on last object continues
        p = np.random.uniform()
        if p <= self.att_span:
            # focus stays on last object
            for percept in perceiving:
                if percept[0] == self.focus[0]:
                    # last object still perceived
                    self.focus = percept  # object remains same, its distance updates
                    return
        # changes focus to something nearby (items farther from horizon more likely)
        reverse_dists = 0
        for percept in perceiving:
            dist = percept[1]
            reverse_dists += horizon - dist
        gaze = np.random.uniform(0, reverse_dists)
        for percept in perceiving:
            reverse_dists -= horizon - percept[1]
            if gaze >= reverse_dists:
                self.focus = percept
                return

    def memorize(self, perceiving:list, horizon:float, world):
        '''
        Encode focus into memory, associating surrounding percepts with it
        ---
        perceiving: list of perceived objects in environment with relative distances
        horizon: max perceivable distance from Person
        '''
        memory = self.deep_remember(self.focus[0])
        salience = np.e**((horizon/2 - self.focus[1]) * abs(np.random.normal(1)))
        if not memory:  # focus is not an existing memory
            memory = Memory(self.focus[0], salience)
        else:  # focus is an existing memory
            memory.salience += salience
            memory.base_salience = memory.salience  # reset the base salience for the decay function
        self.contextualize(memory, perceiving, world)
        self.ltm.add(memory)
    
    def contextualize(self, core_memory:Memory, perceiving:list, world) -> None:
        '''
        Connects Memory with the perceived Memories around it in short term memory
        ---
        core_memory: memory to have perceiving objects' memories connected to
        perceiving: list of perceived objects in environment with relative distances
        '''
        for percept in perceiving:
            memory = self.shallow_remember(percept[0])
            if not memory:  # percept not a memory in short term memory
                continue
            if memory is core_memory:
                continue
            dist = world.get_dist_between(core_memory.object, memory.object)
            core_memory.connect(memory, strength=dist)

    def move_memories(self) -> None:
        '''
        Decays memories and moves outdated memories to or from short term memory.
        '''
        # decay memories
        for memory in self.ltm:
            memory.age += 1
            memory.salience = memory.base_salience * Memory.decay_function(memory.age)
        # remove insufficiently salient memories from short term memory
        temp = self.stm.copy()
        for memory in self.stm:
            if memory.salience < self.stm_thresh:
                temp.remove(memory)
        self.stm = temp
        # add sufficiently salient memories to short term memory
        for memory in self.ltm:
            if memory.salience >= self.stm_thresh:
                self.stm.add(memory)

    def shallow_remember(self, object) -> Memory:
        '''
        Returns memory if the object is a memory in short term memory
        '''
        for memory in self.stm:
            if memory.object is object:
                return memory
        return None
    
    def deep_remember(self, object) -> Memory:
        '''
        Returns memory if the object is a memory in long term memory
        '''
        for memory in self.ltm:
            if memory.object is object:
                return memory
        return None

    # def memory_full(self) -> bool:
    #     total_salience = 0
    #     for memory in self.memories.items():
    #         total_salience += memory.salience
    #     return total_salience <= self.capacity
    
    def show_network(self, name:str, highlight:Memory=None) -> None:
        '''
        Display the network as a directed graph with an optional highlighted memory,
        otherwise the highlighted memory is the focus
        '''
        # highlight = self.deep_remember(self.focus[0])
        # if memory:
        #     highlight = memory
        # print(self.ltm)
        edges = []
        edges_labels = {}
        for memory in self.ltm:
            for connection in memory.connections:
                edges.append((connection, memory))
                edges_labels[(connection, memory)] = round(memory.get_strength(connection), 3)
        G = nx.DiGraph()
        G.add_edges_from(edges)
        print(edges)
        node_sizes = [memory.salience * 1000 for memory in G.nodes]
        
        pos = nx.spring_layout(G)
        # nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), 
        #                     node_color = values, node_size = 500)
        nx.draw_networkx(G, pos, arrows=True, with_labels=True, node_size=node_sizes)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edges_labels, font_color='red')
        plt.title(f'{name} memory network')
        plt.show()


class Person:
    '''
    A person perceives objects in its environment, forms memories,
    converses with other Persons
    '''
    counter = 0
    names = ['grant', 'ethan', 'jennifer', 'brent', 'braun', 'kevin', 'claudia', 'brian', 'dane', 'hunter', 'clinton', 'ashley']
    def __init__(self, parent=None):
        '''
        Constructs mind of Person and sets biophysiological facts
        ---
        parent: the Person(s) passing traits to this Person
        '''
        seed = seed_handler.load_seed()
        np.random.seed(seed)

        self.alive = True
        self.age = 0
        self.perceiving = []  # objects Person perceives
        self.horizon = 3  # distance Person can see
        self.name = Person.names[Person.counter]
        Person.counter += 1

        # construct mind
        capacity = np.random.normal(10, 2)
        att_span = np.random.normal(0.5, 0.2)
        stm_thresh = abs(np.random.normal(1, 0.25))
        if parent:
            capacity_mutation = np.random.normal(0, 1)
            att_span_mutation = np.random.normal(0, 0.05)
            stm_thresh_mutation = np.random.normal(0, 0.05)
            capacity = parent.mind.capacity + capacity_mutation
            att_span = parent.mind.att_span + att_span_mutation
            stm_thresh = parent.mind.stm_threh + stm_thresh_mutation
        if att_span > 1: att_span = 1
        elif att_span < 0: att_span = 0
        self.mind = Mind(capacity, att_span, stm_thresh)
        
        seed_handler.save_seed(seed+1)
    
    def perceive(self, world:World) -> None:
        self.perceiving = world.get_nearby_from_object(self, self.horizon)
        self.mind.set_focus(self.perceiving, self.horizon)
        self.mind.memorize(self.perceiving, self.horizon, world)
        self.mind.move_memories()
        self.age += 1
    
    def show_network(self) -> None:
        self.mind.show_network(self.name)
        
    def stats(self, world:World):
        print(self)
        print(f'  age: {self.age}')
        print(f'  coords: {world.get_coords(self)}')
        print(f'  horizon: {self.horizon}')
        print(f'  capacity: {self.mind.capacity}')
        print(f'  attention span: {self.mind.att_span}')
        print(f'  perceiving: {self.perceiving}')
        print(f'  focus: {self.mind.focus}')

    def __str__(self):
        return self.name
    def __repr__(self):
        return str(self)


# dist = np.random.normal(1, size=100)
# plt.hist(dist)
# plt.show()


# g = nx.Graph()
# g.add_edges_from([('1','2'), ('2','3'), ('2','4'), ('3','4')])
# d = dict(g.degree)

# nx.draw(g, nodelist=d.keys(), node_size=[v * 100 for v in d.values()], with_labels=True)
# plt.show()