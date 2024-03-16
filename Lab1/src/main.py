from paho.mqtt import client as mqtt_client
import json
import time
from schema.aggregated_data_schema import AggregatedDataSchema
from file_datasource import FileDatasource
import config
import logging

# logging.basicConfig(filename='agent.log', level=logging.DEBUG)
# Configure logging settings
# logging.basicConfig(
#     level=logging.DEBUG,  # Set the log level to INFO (you can use logging.DEBUG for more detailed logs)
#     format="[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
#     handlers=[
#         logging.StreamHandler(),  # Output log messages to the console
#         logging.FileHandler("app.log"),  # Save log messages to a file
#     ],
# )

logger = logging.getLogger()
c_handler = logging.StreamHandler()
logger.addHandler(c_handler)
logger.setLevel(logging.INFO)


def connect_mqtt(broker, port):
    """Create MQTT client"""
    logger.info(f"CONNECT TO {broker}:{port}")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connected to MQTT Broker ({broker}:{port})!")
        else:
            logger.error("Failed to connect {broker}:{port}, return code %d\n", rc)
            exit(rc)  # Stop execution

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client


def publish(client, topic, datasource, delay):
    datasource.startReading()
    while True:
        time.sleep(delay)
        data = datasource.read()
        msg = AggregatedDataSchema().dumps(data)
        result = client.publish(topic, msg)
        logger.debug(f"Result: {result}")
        # result: [0, 1]
        status = result[0]
        if status == 0:
            pass
        # print(f"Send `{msg}` to topic `{topic}`")
        else:
            logger.warning(f"Failed to send message to topic {topic}")


def run():
    # Prepare mqtt client
    client = connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)
    logger.debug(f"Client: {client}")
    # Prepare datasource
    datasource = FileDatasource(
        "data/accelerometer.csv", "data/gps.csv", "data/parking.csv"
    )
    # Infinity publish data
    publish(client, config.MQTT_TOPIC, datasource, config.DELAY)


if __name__ == "__main__":
    run()
