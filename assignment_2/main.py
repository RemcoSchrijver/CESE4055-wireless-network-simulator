import random
import time
from matplotlib import pyplot as plt

from mac_protocol.aloha import Aloha
from mac_protocol.smac import SMAC
from network.host import Host
from simulator import simulator


def main():
    print("Starting main function")

    # Create nodes here
    nodes = configure_nodes(8, ranges=[800, 800], radius_node=[100, 200], message_length=2,
                            send_freq_interval=[100, 200])

    # Simulator is started here with a large timeout
    sim = simulator(nodes, 10000)

    started_calc = time.time()
    sim.begin_loop()
    ended_calc = time.time()

    print(f"Calculation time {format(ended_calc - started_calc, '.4f')}")

    stats = sim.get_stats()
    sim.print_results()
    plot_points(nodes)
    #plot_schedule(nodes)

    # plot_throughput()
    #plot_data_rate()
def plot_throughput():
    plot_range = range(3, 30)
    failed_percentage = []


    for number_of_nodes in plot_range:
        nodes = configure_nodes(number_of_nodes, ranges=[200, 200], radius_node=[50, 200], message_length=10,
                                send_freq_interval=[100, 200])

        # Simulator is started here with a large timeout
        sim = simulator(nodes, 10000)
        started_calc = time.time()
        sim.begin_loop()
        ended_calc = time.time()
        print(f"Calculation time {format(ended_calc - started_calc, '.4f')}")
        stats = sim.get_stats()
        failed_percentage.append(stats['failed_percentage'])

    plt.figure()
    plt.plot(plot_range, failed_percentage)
    plt.ylabel('Collision percentage')
    plt.xlabel('Nodes')
    plt.title('Node collisions')
    plt.show()

def plot_data_rate():
    plot_range = range(1, 3)
    failed_percentage = []

    freq_interval = []
    for freq in plot_range:
        send_freq_interval: [int, int] = [250-freq, 300-freq]
        nodes = configure_nodes(10, ranges=[200, 200], radius_node=[50, 200], message_length=10,
                                send_freq_interval=send_freq_interval)

        print("send freq interval from " + str(send_freq_interval[0]) + " to " + str(send_freq_interval[1]))

        # Simulator is started here with a large timeout
        sim = simulator(nodes, 10000)
        started_calc = time.time()
        sim.begin_loop()
        ended_calc = time.time()
        print(f"Calculation time {format(ended_calc - started_calc, '.4f')}")
        stats = sim.get_stats()
        failed_percentage.append(stats['failed_percentage'])
        freq_interval.append(250-freq)


    plt.figure()
    plt.plot(plot_range, failed_percentage)
    plt.ylabel('Collision percentage')
    plt.xlabel('Message random between (x, x+50)')
    plt.title('Data rate observation')
    plt.show()


def configure_nodes(number_of_nodes: int, ranges: [int, int], radius_node: [int, int],
                    message_length: int, send_freq_interval: [int, int]):
    nodes = []
    random.seed(10)

    for id in range(number_of_nodes):
        x = random.randint(0, ranges[0])
        y = random.randint(0, ranges[1])

        minRadius: int = radius_node[0]
        maxRadius: int = radius_node[1]

        radius = random.randint(minRadius, maxRadius)

        #nodes.append(Host(id, x, y, radius, Aloha(message_length, send_freq_interval)))
        nodes.append(Host(id, x, y, radius, SMAC()))
    return nodes


def plot_points(nodes):
    points = []
    radius_all = []
    ids = []
    # plt.figure(figsize=(3, 3), dpi=200)
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
            plt.text(x, y - 10, id, ha='center', va='center')

    x, y = zip(*points)
    plt.scatter(x, y, color='red', label='Points')

    plot_circles_around_points(points, radius_all, ids)

    plt.xlabel('X-location')
    plt.ylabel('Y-location')
    plt.title('Node locations')
    # plt.legend()
    plt.axis('equal')
    plt.grid(True)
    plt.show()

def plot_schedule(nodes):
    label_mapping = {
        0: 'INIT',
        1: 'SYNC_INIT',
        2: 'SYNC_SCHEDULE',
        3: 'SLEEP',
        4: 'LISTEN',
    }

    plt.figure()
    for node in nodes:
        plt.plot(node.plot_schedule)
        plt.xlabel('Round')
        plt.ylabel('State')
        plt.title(f"Schedule of node {node.mac}")
        plt.show()

if __name__ == '__main__':
    main()
