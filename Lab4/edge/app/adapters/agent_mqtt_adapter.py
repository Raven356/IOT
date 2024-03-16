#!/usr/bin/env python3
import logging
import uuid
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from app.interfaces.agent_gateway import AgentGateway
from app.entities.agent_data import AgentData, GpsData
from app.usecases.data_processing import process_agent_data
from app.interfaces.hub_gateway import HubGateway

logger = logging.getLogger()


class AgentMQTTAdapter(AgentGateway):
    def __init__(
        self,
        broker_host,
        broker_port,
        topic,
        hub_gateway: HubGateway,
        batch_size=10,
    ):
        self.batch_size = batch_size
        # MQTT
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        client_id = str(uuid.uuid4())
        self.client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id)
        # Hub
        self.hub_gateway = hub_gateway

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            logging.info("Connected to MQTT broker")
            self.client.subscribe(self.topic)
        else:
            logging.info(f"Failed to connect to MQTT broker with code: {rc}")

    def on_message(self, client, userdata, msg):
        """Processing agent data and sent it to hub gateway"""
        try:
            payload: str = msg.payload.decode("utf-8")
            # Create AgentData instance with the received data
            agent_data = AgentData.model_validate_json(payload, strict=True)
            # Process the received data (you can call a use case here if needed)
            processed_data = process_agent_data(agent_data)
            # Store the agent_data in the database (you can send it to the data processing module)
            if not self.hub_gateway.save_data(processed_data):
                logging.error("Hub is not available")
        except Exception as e:
            logging.error(f"Agent_MQTT: Error processing MQTT message: {e}")

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_host, self.broker_port, 60)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()


# Usage example:
if __name__ == "__main__":
    broker_host = "localhost"
    broker_port = 1883
    topic = "agent_data_topic"
    # Assuming you have implemented the StoreGateway and passed it to the adapter
    store_gateway = HubGateway()
    adapter = AgentMQTTAdapter(broker_host, broker_port, topic, store_gateway)
    adapter.connect()
    adapter.start()
    try:
        # Keep the adapter running in the background
        while True:
            pass
    except KeyboardInterrupt:
        adapter.stop()
        logging.info("Adapter stopped.")
