from typing import List


def dsr_routing(neighbors, message):
    if (message.type == "ReRequest" or message.type == "Known route") and len(message.route) > 0:
        if message.type == "ReRequest":
            message.end_time = message.start_time + 2
        # if message.type == "Known route":
        #     print("Known route sent")
        message.destination = [message.route.pop()]
    else:
        direct_targets = []
        for each in neighbors:
            direct_targets.append(each)

        message.destination = direct_targets

    return message
