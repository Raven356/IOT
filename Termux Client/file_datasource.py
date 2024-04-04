from datetime import datetime
from domain.aggregated_data import AggregatedData
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.parking import Parking
from termux import Sensors, API

from typing import Iterable
import uuid
import logging

# logging.basicConfig(filename='agent.log', level=logging.DEBUG)
# Configure logging settings
logger = logging.getLogger()


class FileDatasource:
    def __init__(
        self, accelerometer_filename: str, gps_filename: str, parking_filename: str
    ) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename
        self.accelerometer_reader = None
        self.gps_reader = None
        self.parking_reader = None
        self.life_time_count = None
        self.time_index = None
        self.uuid = str(uuid.uuid4())

    def read(self) -> AggregatedData | None:
        # if (
        #     self.accelerometer_reader is None
        #     or self.gps_reader is None
        #     or self.parking_reader is None
        #     or self.life_time_count is None
        #     or self.time_index is None
        # ):
        #     return None

        while True:
            # if self.time_index == self.life_time_count:
            #     self.accelerometer_reader.reopen()
            #     self.gps_reader.reopen()
            #     self.parking_reader.reopen()
            #     self.time_index = 0

            # p = self.time_index / self.life_time_count + 1e-4

            # accelerometer_data_new_ind = int(self.accelerometer_reader.lines * p)
            # gps_data_new_ind = int(self.gps_reader.lines * p)
            # parking_data_new_ind = int(self.parking_reader.lines * p)

            # accelerometer_data = self.accelerometer_reader.getCurOrNext(
            #     accelerometer_data_new_ind
            # )
            # gps_data = self.gps_reader.getCurOrNext(gps_data_new_ind)
            # parking_data = self.parking_reader.getCurOrNext(parking_data_new_ind)
            accelerometer_data = Sensors.sensorsData(self.accelerometer_filename)
            gps_data = API.location()

            if accelerometer_data is None or gps_data is None:
                raise ValueError(
                    "Something very bad happened! One of exported data is None!"
                )

            # Log accelerometer, GPS, and parking data
            logger.debug(f"Accelerometer data: {accelerometer_data}")
            logger.debug(f"GPS data: {gps_data}")

            accelerometer_name = list(accelerometer_data[1].keys())[0]
            # Try/catch in case of wrong data inside
            try:
                # Parse accelerometer data
                accelerometer_values = [
                    int(accelerometer_data[1][accelerometer_name]["values"][0]),
                    int(accelerometer_data[1][accelerometer_name]["values"][1]),
                    int(accelerometer_data[1][accelerometer_name]["values"][2]),
                ]

                # Parse GPS data
                gps_values = [
                    float(gps_data[1]["longitude"]),
                    float(gps_data[1]["latitude"]),
                ]

            except (ValueError, IndexError):
                logger.error(
                    f"Failed to parse data, Accelerometer data: {accelerometer_data}, GPS data: {gps_data}"
                )
                continue

            # Create Accelerometer, Gps, and Parking objects
            accelerometer = Accelerometer(*accelerometer_values)
            gps = Gps(*gps_values)

            # Get current timestamp
            timestamp = datetime.now()

            # self.time_index += 1

            return AggregatedData(accelerometer, gps, timestamp, self.uuid)

    def startReading(self, *args, **kwargs):
        pass
        # if self.accelerometer_reader is not None or self.gps_reader is not None:
        # raise ValueError("Files already opened.")
        #
        # self.accelerometer_reader = CustomReader(self.accelerometer_filename)
        # self.gps_reader = CustomReader(self.gps_filename)
        # self.parking_reader = CustomReader(self.parking_filename)

    #
    # self.life_time_count = max(
    # self.accelerometer_reader.lines,
    # self.gps_reader.lines,
    # self.parking_reader.lines,
    # )
    #
    # self.time_index = 0

    def stopReading(self, *args, **kwargs):
        pass
        # if (
        #     self.accelerometer_reader is None
        #     or self.gps_reader is None
        #     or self.parking_reader is None
        # ):
        #     raise ValueError("Files not opened.")

        # # self.accelerometer_reader.close()
        # # self.gps_reader.close()
        # # self.parking_reader.close()
