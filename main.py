from elements import World, Agent

# duration = 1.0   # in seconds, may be float
# f = 440.0        # sine frequency, Hz, may be float
    

def main():
    w = World(dim=(3,3), rand_walls=True, walliness=0.3)
    paul = Agent(name='paul', thinking_aloud=True)
    successfully_placed = w.place_agent(paul, pos=(0,0))

    if successfully_placed:
        while True:
            print('\n'+str(w)+'\n')
            (duration, f) = paul.plan(w, paul.uniform_less_greed_prob)
            paul.speak(duration, f)

            print('Allow? (y/n)')
            permission = (input() == 'y')
            paul.listen(w, permission)


if __name__ == '__main__':
    main()