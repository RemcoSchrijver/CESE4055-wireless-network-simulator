import time
from matplotlib import pyplot as plt

from aloha_algorithm import Aloha
from host import Host
from simulator import simulator


def main():
    print("Starting main function")
    

    # Create nodes here
    nodes = []
    nodes.append(Host(0, 4,5, 6, Aloha()))
    nodes.append(Host(1, 3, 2, 18, Aloha()))
    nodes.append(Host(2, 5, 2, 7, Aloha()))
    nodes.append(Host(3, 1, 2, 13, Aloha()))
    nodes.append(Host(4, 5, 4, 12, Aloha()))
    # nodes.append(Host(5, 1, 2, 3, Aloha()))
    # nodes.append(Host(6, 2, 3, 9, Aloha()))
    # nodes.append(Host(7, 4, 6, 4, Aloha()))

    plt.figure()
    for node in nodes:
        plt.plot(node.get_positionx(), node.get_positiony(), 'bo')

    plt.show()

    # Simulator is started here with a large timeout 
    sim = simulator(nodes, 40000)

    started_calc = time.time()
    sim.begin_loop()
    ended_calc = time.time()

    print(f"Calculation time {ended_calc - started_calc}")

    sim.print_results() 

if __name__ == '__main__':
    main()
