#!/usr/bin/env python3
from pydantic import BaseModel
from app.entities.agent_data import AgentData


class ProcessedAgentData(BaseModel):
    road_state: str
    road_state_n: int
    agent_data: AgentData
