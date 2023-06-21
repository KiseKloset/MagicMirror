import asyncio
import platform
import subprocess

import cv2

if platform.system() == 'Windows':
    import winsdk.windows.devices.enumeration as windows_devices

VIDEO_DEVICES = 4


class Camera:

    def __init__(self):
        self.cameras = []

    def get_camera_info(self) -> list:
        self.cameras = []

        camera_indexes = self.get_camera_indexes()

        if len(camera_indexes) == 0:
            return self.cameras

        self.cameras = self.add_camera_information(camera_indexes)

        return self.cameras

    def get_camera_indexes(self):
        index = 0
        camera_indexes = []
        max_numbers_of_cameras_to_check = 10
        while max_numbers_of_cameras_to_check > 0:
            capture = cv2.VideoCapture(index)
            if capture.read()[0]:
                camera_indexes.append(index)
                capture.release()
            index += 1
            max_numbers_of_cameras_to_check -= 1
        return camera_indexes

    # TODO add MacOS specific implementations
    def add_camera_information(self, camera_indexes: list) -> list:
        platform_name = platform.system()
        cameras = []

        if platform_name == 'Windows':
            cameras_info_windows = asyncio.run(self.get_camera_information_for_windows())

            for camera_index in camera_indexes:
                camera_name = cameras_info_windows.get_at(camera_index).name.replace('\n', '')
                cameras.append({'camera_index': camera_index, 'camera_name': camera_name})

            return cameras

        if platform_name == 'Linux':
            for camera_index in camera_indexes:
                camera_name = subprocess.run(['cat', '/sys/class/video4linux/video{}/name'.format(camera_index)],
                                             stdout=subprocess.PIPE).stdout.decode('utf-8')
                camera_name = camera_name.replace('\n', '')
                cameras.append({'camera_index': camera_index, 'camera_name': camera_name})

            return cameras

    async def get_camera_information_for_windows(self):
        return await windows_devices.DeviceInformation.find_all_async(VIDEO_DEVICES)


camera = Camera()
connected_cameras = asyncio.run(camera.get_camera_information_for_windows())
names = [camera.name for camera in connected_cameras]
print(names)
