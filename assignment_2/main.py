import random
import time
from matplotlib import pyplot as plt

from aloha_algorithm import Aloha
from host import Host
from simulator import simulator


def main():
    print("Starting main function")

    # Create nodes here
    nodes = configure_nodes(10, ranges=[100, 100], min_radius=50, max_radius=100, message_length=5, send_freq_interval=(100, 200))

    # Simulator is started here with a large timeout
    sim = simulator(nodes, 10000)

    started_calc = time.time()
    sim.begin_loop()
    ended_calc = time.time()

    print(f"Calculation time {format(ended_calc - started_calc, '.4f')}")

    sim.print_results()
    plot_points(nodes)


def configure_nodes(number_of_nodes: int, ranges: [int, int], min_radius: int, max_radius: int,
                    message_length: int, send_freq_interval: (int, int)):
    nodes = []
    random.seed(10)

    for id in range(number_of_nodes):
        x = random.randint(0, ranges[0])
        y = random.randint(0, ranges[1])

        radius = random.randint(min_radius, max_radius)

        nodes.append(Host(id, x, y, radius, Aloha(message_length, send_freq_interval)))

    return nodes

def plot_points(nodes):
    points = []
    radius_all = []
    ids = []
    plt.figure()
    for node in nodes:
        x = node.get_positionx()
        y = node.get_positiony()
        radius = node.get_reach()
        points.append((x, y))
        radius_all.append(radius)
        ids.append(node.mac)

    def plot_circles_around_points(points, radius_all, ids):
        for (x, y), radius, id in zip(points, radius_all, ids):
            circle = plt.Circle((x, y), radius, color='blue', fill=False)
            plt.gca().add_patch(circle)
            plt.text(x, y - 0.2 * radius, id, ha='center', va='center')

    x, y = zip(*points)
    plt.scatter(x, y, color='red', label='Points')

    plot_circles_around_points(points, radius_all, ids)

    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Points with Circles')
    plt.legend()
    plt.axis('equal')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    main()
