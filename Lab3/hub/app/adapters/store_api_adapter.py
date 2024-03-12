#!/usr/bin/env python3

import json
import logging
from typing import List

import pydantic_core
import requests as req

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_api_gateway import StoreGateway
from config import STORE_API_BASE_URL


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        # Make a POST request to the Store API endpoint with the processed data
        data = json.dumps(processed_agent_data_batch)
        r = req.post(STORE_API_BASE_URL, data)
        if r.status_code == 200:
            return 0
        else:
            return {r.status_code, r.text}
        pass
