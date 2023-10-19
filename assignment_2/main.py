from simulator import simulator

def main():
    print("Starting main function")
    # Create nodes here
    nodes = []

    # Simulator is started here with a large timeout 
    sim = simulator(nodes, 10000000)

    sim.begin_loop()

if __name__ == '__main__':
    main()
