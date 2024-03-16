#!/usr/bin/env python3
from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

import numpy as np
from numpy.linalg import lstsq
import logging

data_history = []
logger = logging.getLogger()


def process_agent_data(agent_data: AgentData) -> ProcessedAgentData:
    """
        Process agent data and classify the state of the road surface.
        Parameters:
            agent_data (AgentData): Agent data that contains accelerometer, GPS, and timestamp.
        Returns:
            processed_data (ProcessedAgentData): Processed data containing the classified state of
    the road surface and agent data.
    """
    road_state = ""
    road_state_n = 2

    data_history.append(agent_data.accelerometer)

    if len(data_history) < 10:
        return ProcessedAgentData(
            road_state=road_state, agent_data=agent_data, road_state_n=road_state_n
        )

    # Processing 4 elements from array

    x = np.array([i for i in range(10)])
    A = np.vstack([x, np.ones(len(x))]).T

    y_x = [val.x for val in data_history]
    y_y = [val.y for val in data_history]
    y_z = [val.z for val in data_history]

    # Calculate coeffs for line y = mx + c
    m1, c1 = lstsq(A, y_x, rcond=None)[0]
    m2, c2 = lstsq(A, y_y, rcond=None)[0]
    m3, c3 = lstsq(A, y_z, rcond=None)[0]

    # Validate deviation of last point from retrieved line formula
    d1 = abs(y_x[len(y_x) - 1] - (m1 * 3 + c1))
    d2 = abs(y_y[len(y_y) - 1] - (m2 * 3 + c2))
    d3 = abs(y_z[len(y_z) - 1] - (m3 * 3 + c3))

    if d1 >= 2000 and d2 >= 2000 and d3 >= 2000:
        road_state = "Bad"
        road_state_n = 0
    elif 500 <= d1 <= 2000 and 500 <= d2 <= 2000 and 500 <= d3 <= 2000:
        road_state = "Normal"
        road_state_n = 1
    else:
        road_state = "Good"
        road_state_n = 2

    data_history.pop(0)

    logger.debug(f"Road state: {road_state}")
    logger.debug(f"Deltas: {d1}, {d2}, {d3}")

    return ProcessedAgentData(
        road_state=road_state, agent_data=agent_data, road_state_n=road_state_n
    )
