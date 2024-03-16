#!/usr/bin/env python3
from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

import numpy as np
from math import abs
from numpy.linalg import lstsq

data_history = []


def process_agent_data(agent_data: AgentData) -> ProcessedAgentData:
    """
        Process agent data and classify the state of the road surface.
        Parameters:
            agent_data (AgentData): Agent data that contains accelerometer, GPS, and timestamp.
        Returns:
            processed_data (ProcessedAgentData): Processed data containing the classified state of
    the road surface and agent data.
    """
    res = ProcessedAgentData(road_state="", agent_data=agent_data)

    data_history.append(agent_data.accelerometer)

    if len(data_history) != 4:
        return res

    # Processing 4 elements from array

    x = np.array([0, 1, 2, 3])
    A = np.vstack([x, np.ones(len(x))]).T

    y_x = [val[0] for val in data_history]
    y_y = [val[1] for val in data_history]
    y_z = [val[2] for val in data_history]

    # Calculate coeffs for line y = mx + c
    m1, c1 = lstsq(A, y_x, rcond=None)[0]
    m2, c2 = lstsq(A, y_y, rcond=None)[0]
    m3, c3 = lstsq(A, y_z, rcond=None)[0]

    # Validate deviation of last point from retrieved line formula
    d1 = abs(y_x[3] - (m1 * 3 + c1))
    d2 = abs(y_y[3] - (m2 * 3 + c2))
    d3 = abs(y_z[3] - (m3 * 3 + c3))

    if d1 >= 4 and d2 >= 4 and d3 >= 4:
        res.road_state = "Bad"
    elif 2 <= d1 <= 4 and 2 <= d2 <= 4 and 2 <= d3 <= 4:
        res.road_state = "Normal"
    else:
        res.road_state = "Good"

    data_history.pop(0)

    return res
