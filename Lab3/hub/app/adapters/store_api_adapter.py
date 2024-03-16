#!/usr/bin/env python3

import json
import logging
from typing import List

import pydantic_core
import requests as req

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_api_gateway import StoreGateway
from config import STORE_API_BASE_URL

logger = logging.getLogger()


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        # Make a POST request to the Store API endpoint with the processed data
        data = json.dumps(
            processed_agent_data_batch, default=pydantic_core.to_jsonable_python
        )
        logger.debug(f"data: {data}")
        logger.debug(f"processed_data: {processed_agent_data_batch}")
        r = req.post(f"{STORE_API_BASE_URL}/processed_agent_data/", data)
        if r.status_code == 200:
            return 0
        else:
            logger.error(
                f"Failed to send POST request to store API: {r.status_code} {r.text}"
            )
            return {r.status_code, r.text}
        pass
