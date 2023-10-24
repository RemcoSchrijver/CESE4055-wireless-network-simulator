import random
from enum import Enum, auto

from assignment_2.network.host import Host
from assignment_2.network.message import Message

MEAN_WAIT = 30
STD_WAIT = 10

class State(Enum):
    INIT = auto()
    SLEEP = auto()
    LISTEN = auto()


class MessageType(Enum):
    SYNC = auto()
    RTS = auto()
    CTS = auto()
    DATA = auto()
    ACK = auto()

class SMAC:

    def __init__(self):
        self.state = State.INIT
        self.listen_period = None
        self.sleep_period = None
        self.message_counter = 0
        self.next_available_round = 1

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

        if self.state == State.INIT:
            # TODO: initialize sync schedule
            pass
        elif self.state == State.SLEEP:
            # TODO: logic for sleep cycle
            pass
        elif self.state == State.LISTEN:

            # TODO: logic for listen cycle
            pass
        else:
            print("Unknown state")

        # if round_counter >= self.begin_random + 1:
        #     self.message_send = False
        #
        # if incoming_message is None and self.message_send is False:
        #     message = self.send_message(node, round_counter)
        #     self.message_send = True

        return message

    def send_message(self, node: Host, round_counter,  message_type: MessageType):
        message = None
        neigbors = node.get_neighbors()

        # TODO: Send message logic

        # Simulate random processing time
        random_wait = self.get_random_wait()
        start_time = random.randint(self.next_available_round, self.next_available_round + random_wait)
        # Add transmission time of the message
        end_time = start_time + self.message_durations[message_type]

        # Send message to a randomly selected neighbour
        if len(neigbors) > 0:
            random_neigbour = random.randint(0, len(neigbors) - 1)
            destination = neigbors[random_neigbour].mac
            message = Message(node.mac, destination, start_time, end_time, "hello")

        # Set next available round to the endtime of the current transmission
        self.next_available_round = end_time
        self.message_counter += 1

        return message

    @staticmethod
    def get_random_wait():
        return round(random.gauss(MEAN_WAIT, STD_WAIT))

