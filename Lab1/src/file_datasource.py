from csv import reader
from datetime import datetime
from domain.aggregated_data import AggregatedData
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.parking import Parking
import logging

logging.basicConfig(filename='agent.log', level=logging.DEBUG)

class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, parking_filename: str) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename
        self.accelerometer_file = None
        self.gps_file = None
        self.parking_file = None

    def read(self) -> AggregatedData:
        if self.accelerometer_file is None or self.gps_file is None or self.parking_file is None:
            return None

        while True:
            accelerometer_data = next(self.accelerometer_reader, None)
            gps_data = next(self.gps_reader, None)
            parking_data = next(self.parking_reader, None)
            
            if accelerometer_data is None or gps_data is None or parking_data is None:
                self.stopReading()
                self.startReading()
            
            # Skip empty lines
            if not accelerometer_data or not gps_data or not parking_data:
                continue

            # Log accelerometer, GPS, and parking data
            logging.debug(f"Accelerometer data: {accelerometer_data}")
            logging.debug(f"GPS data: {gps_data}")
            logging.debug(f"Parking data: {parking_data}")

            try:
                # Parse accelerometer data
                accelerometer_values = [int(val) for val in accelerometer_data]

                # Parse GPS data
                gps_values = [float(val) for val in gps_data]

                # Parse Parking data
                empty_count = int(parking_data[0])
                gps = Gps(float(parking_data[1]), float(parking_data[2]))
            except (ValueError, IndexError):
                logging.error(f"Failed to parse data, Accelerometer data: {accelerometer_data}, GPS data: {gps_data}, Parking data: {parking_data}")
                continue

            # Create Accelerometer, Gps, and Parking objects
            accelerometer = Accelerometer(*accelerometer_values)
            parking = Parking(empty_count, gps)

            # Get current timestamp
            timestamp = datetime.now()
            
            return AggregatedData(accelerometer, gps, parking, timestamp)


    def startReading(self, *args, **kwargs):
        if self.accelerometer_file is not None or self.gps_file is not None:
            raise ValueError("Files already opened.")
        
        self.accelerometer_file = open(self.accelerometer_filename, 'r')
        self.gps_file = open(self.gps_filename, 'r')
        self.parking_file = open(self.parking_filename, 'r')
        self.accelerometer_reader = reader(self.accelerometer_file)
        self.gps_reader = reader(self.gps_file)
        self.parking_reader = reader(self.parking_file)

    def stopReading(self, *args, **kwargs):
        if self.accelerometer_file is None or self.gps_file is None:
            raise ValueError("Files not opened.")
        
        self.accelerometer_file.close()
        self.gps_file.close()
        self.parking_file.close()
        self.accelerometer_file = None
        self.gps_file = None
        self.parking_file = None