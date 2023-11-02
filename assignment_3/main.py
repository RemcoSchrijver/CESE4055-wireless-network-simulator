import random
import time
from typing import List
from matplotlib import pyplot as plt
import tkinter as tk

from host import Host
from simulator import simulator


def main():
    print("Starting main function")
    # Seed we need for tests of different algos
    seed = None

    # Create nodes here
    nodes = configure_nodes(4, ranges=[50, 50], max_radius=40)

    # Start tkinter
    window = tk.Tk()
    window.title("Routing simulator")
    canvas = tk.Canvas(window, width=1920, height=1080)
    canvas.configure(background="grey")
    canvas.pack()
    dot_dict = create_dots_on_canvas(nodes, canvas)

    # Simulator is started here with a large timeout
    sim = simulator(nodes, 1000000, window, canvas, dot_dict)

    started_calc = time.time()
    sim.begin_loop()
    ended_calc = time.time()

    print(f"Calculation time {format(ended_calc - started_calc, '.4f')}")

    sim.print_results()


def configure_nodes(number_of_nodes: int, ranges: List[int], max_radius: int):
    nodes = []
    random.seed(10)

    for id in range(number_of_nodes):
        x = random.randint(0, ranges[0])
        y = random.randint(0, ranges[1])

        radius = random.randint(1, max_radius)

        nodes.append(Host(id, x, y, radius, lambda x: print(x), movement_frequency=0.5, message_chance=0.0))

    return nodes

def create_dots_on_canvas(nodes: List[Host], canvas):
    dot_dict = {}
    node: Host
    for node in nodes:
        dot_dict[node] = create_dot(node, canvas)

    return dot_dict

def create_dot(node: Host, canvas):

    fill_color = "#{:02x}{:02x}{:02x}".format(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )  

    dot = canvas.create_oval(node.positionx, node.positiony, node.positionx+10, node.positiony+10, fill=fill_color)
    return dot

if __name__ == '__main__':
    main()
