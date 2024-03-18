import asyncio
import math
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import Datasource, ProcessedAgentData
import logging
import uuid
from typing import List, Tuple
from time import sleep

logger = logging.getLogger()


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        # додати необхідні змінні
        self.markers = []
        self.zoom_coords = {"min_x": 1e7, "min_y": 1e7, "max_x": -1e7, "max_y": -1e7}
        self.car_coords = {"x": 0, "y": 0}
        # Init data source
        self.datasource = Datasource(user_id=str(uuid.uuid4()))

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        # We're assuming, that we don't have any information on boot
        # So we just update map
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        # Refresh data source information
        new_points = self.refresh_datasource()
        logger.info(f"Received points: {new_points}")
        # Update map center
        self.recalculate_map_center(new_points)
        coords = {
            "x": (self.zoom_coords["max_x"] + self.zoom_coords["min_x"]) / 2,
            "y": (self.zoom_coords["max_y"] + self.zoom_coords["min_y"]) / 2,
        }
        logger.debug(f"New map center coords: {coords}")
        max_delta = max(
            self.zoom_coords["max_x"] - self.zoom_coords["min_x"],
            self.zoom_coords["max_y"] - self.zoom_coords["min_y"],
        )
        self.mapview.lat = coords["x"]
        self.mapview.lon = coords["y"]
        logger.debug(f"max delta: {max_delta}")
        if max_delta != 0 and 360 / max_delta > 0:
            self.mapview.zoom = int(math.log2(360 / max_delta))
        # Update car marker
        # self.update_car_marker()
        # Update potholes
        # Update road bumps

    def recalculate_map_center(self, points: List[Tuple[float, float, str]]):

        logger.debug(f"count of new points: {len(points)}")
        if len(points) != 0:
            self.zoom_coords["min_x"] = min(
                self.zoom_coords["min_x"], min([x[1] for x in points])
            )
            self.zoom_coords["min_y"] = min(
                self.zoom_coords["min_y"], min([x[0] for x in points])
            )
            self.zoom_coords["max_x"] = max(
                self.zoom_coords["max_x"], min([x[1] for x in points])
            )
            self.zoom_coords["max_y"] = max(
                self.zoom_coords["max_y"], min([x[0] for x in points])
            )

        # if self.car_coords["x"] < self.zoom_coords["min_x"]:
        #     self.zoom_coords["min_x"] = self.car_coords["x"]
        # if self.car_coords["x"] > self.zoom_coords["max_x"]:
        #     self.zoom_coords["max_x"] = self.car_coords["x"]
        # if self.car_coords["y"] < self.zoom_coords["min_y"]:
        #     self.zoom_coords["min_y"] = self.car_coords["y"]
        # if self.car_coords["y"] > self.zoom_coords["max_y"]:
        #     self.zoom_coords["max_y"] = self.car_coords["y"]

    def refresh_datasource(self):
        # Trigger get_new_points
        return self.datasource.get_new_points()

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        x, y = point.latitude, point.longitude
        logger.info(x, y)
        pass

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """
        pass

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """
        pass

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.mapview = MapView()
        self.mapview.zoom = 6
        self.mapview.lat = 48.560
        self.mapview.lon = 31.443
        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
