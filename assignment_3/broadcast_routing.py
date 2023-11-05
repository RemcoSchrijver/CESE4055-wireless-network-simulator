from typing import List

from host import Host
from message import Message


def broadcast_routing(neighbors: List[Host], message: Message):
    direct_targets = []
    for each in neighbors:
        direct_targets.append(each)
    
    message.destination = direct_targets
    return message
