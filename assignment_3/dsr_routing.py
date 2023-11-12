from typing import List


def dsr_routing(neighbors, message):
    if message.type == "ReRequest" or message.type == "Known route" and len(message.route) > 1:
        message.destination = [message.route.pop()]
    else:
        direct_targets = []
        for each in neighbors:
            direct_targets.append(each)

        message.destination = direct_targets

    return message
