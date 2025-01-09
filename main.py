import argparse
import numpy as np

from scripts.seed_handler import save_seed
from scripts.reality import World


def main(width: int, height: int, seed: int):
    save_seed(seed)
    np.random.seed(seed)
    world = World(width, height)
    # population = 5
    # np.random.uniform(0, width, population).astype(int)
    # np.random.uniform(0, height, population).astype(int)
    world.create_person(1, 0),
    world.create_person(3, 0),
    world.create_person(0, 1),
    world.create_person(0, 2)

    world.show()
    print(world.population)
    # for _ in range(1):
    #     world.population[0].perceive(world)
    #     world.population[0].act(world)
    #     world.population[0].stats(world)
    world.population[0].perceive(world)
    world.population[0].stats(world)
    # world.population[0].act(world)
    world.population[1].perceive(world)
    world.population[1].stats(world)
    # world.population[0].show_network()


if __name__ == '__main__':
    # TODO: figure out what to put in description
    parser = argparse.ArgumentParser(description='Insert description.')
    parser.add_argument('width', type=int, help='width of the map')
    parser.add_argument('height', type=int, help='height of the map')
    parser.add_argument('-l', '--seed', default=1, type=int,
                        help='set random seed')

    args = parser.parse_args()
    main(args.width, args.height, args.seed)


# TODO
# introduce mutation chances changing with individual and environment
# consolidate memories during a sleep cycle?
# https://www.simplypsychology.org/memory.html
# feed, then wander
# inner product of fourier
# add muted feature when speaking and control with human_audible in Mouth.speak

# Score Metrics:
# score similarity of connections between sounds and objects in memory(?)
# score by performance on a "test" to see what they've learned(?)
# score by how many generations they've survived(?)
# score by how many offspring they've had(?)

# https://github.com/zakaton/Pink-Trombone