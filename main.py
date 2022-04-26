from elements import World, Squealer, Interpreter, Mouth
import websockets
# duration = 1.0   # in seconds, may be float
# f = 440.0        # sine frequency, Hz, may be float
def human_game(world: World, searcher: Squealer):
    while True:
        print('\n'+str(world)+'\n')
        (duration, f) = searcher.plan(world, searcher.uniform_less_greed_prob)
        searcher.speak_human(Mouth())

        print('Allow? (y/n)')
        permission = (input() == 'y')
        searcher.listen(world, permission)

def humanless_game(world: World, searcher: Squealer, interpreter: Interpreter):
    distortion_func = lambda x: x
    while True:
        (duration, f) = searcher.plan(world, searcher.uniform_less_greed_prob)
        permission = interpreter.listen(world, duration, f, distortion_func, 1000)
        action = searcher.listen(world, permission)
        # interpreter.associate(action)



def main():
    w = World(dim=(10,10), rand_walls=True, walliness=0.3)
    searcher = Squealer(name='paul', thinking_aloud=False)
    human_present = True

    successfully_placed = w.place_agent(searcher, pos=(0,0))
    while not successfully_placed:
        pos = input(f'trouble placing {searcher}, give coords (\'n, m\'):')
        successfully_placed = w.place_agent(searcher, pos=pos)

    if human_present:
        score = human_game(w, searcher)
    else:
        interpreter = Interpreter(name='dave', thinking_alound=True)
        score = humanless_game(w, searcher, interpreter)
        
    # print(f'{searcher}\'s score: {searcher.score}')


if __name__ == '__main__':
    main()