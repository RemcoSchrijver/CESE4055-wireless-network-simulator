from matplotlib import pyplot as plt

from assignment_2.aloha_algorithm import Aloha
from assignment_2.host import Host
from simulator import simulator


def main():
    print("Starting main function")

    algorithm = Aloha

    # Create nodes here
    nodes = []
    nodes.append(Host(0, 4,5, 6, algorithm))
    nodes.append(Host(1, 3, 2, 18, algorithm))
    nodes.append(Host(2, 5, 2, 7, algorithm))
    nodes.append(Host(3, 1, 2, 13, algorithm))
    nodes.append(Host(4, 5, 4, 12, algorithm))
    nodes.append(Host(5, 1, 2, 3, algorithm))
    nodes.append(Host(6, 2, 3, 9, algorithm))
    nodes.append(Host(7, 4, 6, 4, algorithm))

    # plt.figure()
    # for node in nodes:
    #     plt.plot(node.get_positionx(), node.get_positiony(), 'bo')
    #
    # plt.show()

    # Simulator is started here with a large timeout 
    sim = simulator(nodes, 10000)

    sim.begin_loop()

if __name__ == '__main__':
    main()
