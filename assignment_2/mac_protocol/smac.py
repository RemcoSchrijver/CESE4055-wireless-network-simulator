import random
from enum import Enum, auto

from network.host import Host
from network.message import Message

# Random WAIT constants (gaussian)
MEAN_WAIT = 30
STD_WAIT = 10

# SYNC init bounds (min/max uniform)
SYNC_MIN_INIT_WAIT = 500
SYNC_MAX_INIT_WAIT = 1000

# SYNC schedule bounds (min/max uniform)
SYNC_MIN_SLEEP_WAIT = 50
SYNC_MAX_SLEEP_WAIT = 100
SYNC_MIN_SLEEP_PERIOD = 500
SYNC_MAX_SLEEP_PERIOD = 1000
SYNC_MIN_LISTEN_PERIOD = 150
SYNC_MAX_LISTEN_PERIOD = 300

class State(Enum):
    INIT = auto()
    SYNC_INIT = auto()
    SYNC_SCHEDULE = auto()
    SLEEP = auto()
    LISTEN = auto()


class MessageType(Enum):
    SYNC = auto()
    RTS = auto()
    CTS = auto()
    DATA = auto()
    ACK = auto()

class NodeType(Enum):
    FOLLOWER = auto()
    SYNCHRONIZER = auto()

class SMAC:

    def __init__(self):
        self.state = State.INIT
        self.node_type = NodeType.FOLLOWER
        self.next_available_round = 1

        # Counters for alternating sleep/listen cycle
        self.next_listen_period = None
        self.next_sleep_period = None

        # SYNC schedules of neighbouring nodes
        self.schedule_table = dict()

        # SYNC schedule
        self.sync_init_wait = None
        self.sync_sleep_wait = None
        self.listen_period = None
        self.sleep_period = None

        # TODO: provide realistic (mininum) message durations
        self.message_durations = {
            MessageType.SYNC: 15,
            MessageType.RTS: 10,
            MessageType.CTS: 10,
            MessageType.DATA: 20,
            MessageType.ACK: 5
        }

    def process_algorithm(self, node: Host, round_counter, incoming_message):
        message = None
        received_message = None

        if incoming_message:
            received_message = incoming_message.message.split()

        if self.state == State.INIT:
            # Wait for other SYNC messages
            self.sync_init_wait = round_counter + random.randint(SYNC_MIN_INIT_WAIT, SYNC_MAX_INIT_WAIT)
            self.state = State.SYNC_INIT

        elif self.state == State.SYNC_INIT:
            # No SYNC from other nodes, create a schedule
            if round_counter >= self.sync_init_wait:
                self.sync_init_wait = None

                # Create schedule
                sleep_period = random.randint(SYNC_MIN_SLEEP_PERIOD, SYNC_MAX_SLEEP_PERIOD)
                listen_period = random.randint(SYNC_MIN_LISTEN_PERIOD, SYNC_MAX_LISTEN_PERIOD)
                sleep_wait = round_counter + random.randint(SYNC_MIN_SLEEP_WAIT, SYNC_MAX_SLEEP_WAIT)

                # Create and broadcast schedule
                schedule = f"{sleep_period} {listen_period} {sleep_wait}"
                message = self.send_message(node, round_counter, MessageType.SYNC, schedule)

                # Update own state
                self.state = State.SYNC_SCHEDULE
                self.node_type = NodeType.SYNCHRONIZER
                self.sleep_period = sleep_period
                self.listen_period = listen_period
                self.sync_sleep_wait = sleep_wait

                print(message)
                return message

            if received_message:
                if received_message[0] == "SYNC": # TODO: Receiving this can always happen: merge sleep tables(?check paper)
                    self.state = State.SYNC_SCHEDULE
                    self.node_type = NodeType.SYNCHRONIZER
                    self.sleep_period = int(received_message[1])
                    self.listen_period = int(received_message[2])
                    self.sync_sleep_wait = int(received_message[3])
                    # TODO: Update schedule table

        elif self.state == State.SYNC_SCHEDULE:
            # Sync our schedule to the one we received
            if round_counter >= self.sync_sleep_wait:
                self.sync_sleep_wait = None
                self.next_listen_period = round_counter + self.sleep_period
                self.state = State.SLEEP

        elif self.state == State.SLEEP:
            if round_counter >= self.next_listen_period:
                self.next_sleep_period = round_counter + self.listen_period
                self.state = State.LISTEN

        elif self.state == State.LISTEN:
            if round_counter >= self.next_sleep_period:
                self.next_listen_period = round_counter + self.sleep_period
                self.state = State.SLEEP
        else:
            print("Unknown state")

        return message

    def send_message(self, node: Host, round_counter: int,  message_type: MessageType, payload: str):
        message = None
        neighbors = node.get_neighbors()

        # Simulate random processing time
        random_wait = self.get_random_wait()
        start_time = random.randint(round_counter, round_counter + random_wait)

        # Add transmission time of the message
        end_time = start_time + self.message_durations[message_type]

        if message_type == MessageType.SYNC:
            # Broadcast SYNC to all neighbours
            if len(neighbors) > 0:
                message = Message(node.mac, -1, start_time, end_time, f"{message_type.name} {payload}")

        # Set next available round to the endtime of the current transmission
        self.next_available_round = end_time

        return message

    @staticmethod
    def get_random_wait():
        return round(random.gauss(MEAN_WAIT, STD_WAIT))

