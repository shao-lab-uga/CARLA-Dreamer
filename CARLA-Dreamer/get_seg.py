import carla
import random
import subprocess
import time
import cv2
import numpy as np
import pygame
subprocess.Popen(r'C:\Users\zl00705\Documents\CARLA_0.9.15\WindowsNoEditor\CarlaUE4.exe -carla-server -windowed -ResX=1600 -ResY=900',shell=True)

time.sleep(10) 

IM_WIDTH = 1600
IM_HEIGHT = 900


RGB_ID = {'CAM_FRONT': 0, 'CAM_FRONT_LEFT': 0, 'CAM_FRONT_RIGHT': 0, 'CAM_BACK': 0, 'CAM_BACK_LEFT': 0, 'CAM_BACK_RIGHT': 0}
SEG_ID = {'CAM_FRONT': 0, 'CAM_FRONT_LEFT': 0, 'CAM_FRONT_RIGHT': 0, 'CAM_BACK': 0, 'CAM_BACK_LEFT': 0, 'CAM_BACK_RIGHT': 0}
actor_list = []

import os
if not os.path.exists('rgb'):
    os.makedirs('rgb')
    # create folder for each camera
    for cam_name in RGB_ID.keys():
        os.makedirs(f'rgb/{cam_name}')
        
else:
    # delete all image 
    for file in os.listdir('rgb'):
        os.remove(f'rgb/{file}')
if not os.path.exists('seg'):
    os.makedirs('seg')
    # create folder for each camera
    for cam_name in SEG_ID.keys():
        os.makedirs(f'seg/{cam_name}')
else:
    # delete all image 
    for file in os.listdir('seg'):
        os.remove(f'seg/{file}')

def process_rgb_image(image,cam_name='CAM_FRONT'):
    global RGB_ID
    array = np.frombuffer(image.raw_data, dtype=np.uint8)
    array = array.reshape((IM_HEIGHT, IM_WIDTH, 4))  # RGBA 格式
    rgb_image = array[:, :, :3]  
    cv2.imshow(f"{cam_name}", rgb_image)
    
    save_path = f'./rgb/{cam_name}/{RGB_ID[cam_name]}.png'
    RGB_ID[cam_name] += 1
    iswrite = cv2.imwrite(save_path, rgb_image)
    
    cv2.waitKey(1)

def process_segmentation_image(image,cam_name='CAM_FRONT'):
    global SEG_ID
    image.convert(carla.ColorConverter.CityScapesPalette)
    array = np.frombuffer(image.raw_data, dtype=np.uint8)
    array = array.reshape((IM_HEIGHT, IM_WIDTH, 4))  # BGRA 格式
    segmentation_image = array[:, :, :3]  # 提取 BGR 通道
    save_path = f'./seg/{cam_name}/{SEG_ID[cam_name]}.png'
    SEG_ID[cam_name]+= 1
    cv2.imwrite(save_path, segmentation_image)
    cv2.imshow(f"Segmentation Camera{cam_name}", segmentation_image)
    cv2.waitKey(1)


def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    blueprint_library = world.get_blueprint_library()
    vehicle_bp = blueprint_library.filter('model3')[0]

    spawn_points = world.get_map().get_spawn_points()
    spawn_point = random.choice(spawn_points)

    vehicle = world.spawn_actor(vehicle_bp, spawn_point)

    vehicle.set_autopilot(True)
    actor_list.append(vehicle)

    camera_configs = {
    'CAM_FRONT': {'transform': carla.Transform(carla.Location(x=1.5, y=0.0, z=2.0),
                                               carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)),
                  'fov': 70},
    'CAM_FRONT_LEFT': {'transform': carla.Transform(carla.Location(x=1.5, y=-0.5, z=2.0),
                                                    carla.Rotation(pitch=0.0, yaw=-45.0, roll=0.0)),
                       'fov': 70},
    'CAM_FRONT_RIGHT': {'transform': carla.Transform(carla.Location(x=1.5, y=0.5, z=2.0),
                                                     carla.Rotation(pitch=0.0, yaw=45.0, roll=0.0)),
                        'fov': 70},
    'CAM_BACK': {'transform': carla.Transform(carla.Location(x=-1.5, y=0.0, z=2.0),
                                              carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0)),
                 'fov': 110},
    'CAM_BACK_LEFT': {'transform': carla.Transform(carla.Location(x=-1.5, y=-0.5, z=2.0),
                                                   carla.Rotation(pitch=0.0, yaw=225.0, roll=0.0)),
                      'fov': 70},
    'CAM_BACK_RIGHT': {'transform': carla.Transform(carla.Location(x=-1.5, y=0.5, z=2.0),
                                                    carla.Rotation(pitch=0.0, yaw=135.0, roll=0.0)),
                       'fov': 70},
}


    rgb_cameras = []
    seg_cameras = []
    for cam_name, config in camera_configs.items():
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_seg = blueprint_library.find('sensor.camera.semantic_segmentation')
        
        camera_seg.set_attribute('image_size_x', '1600')
        camera_seg.set_attribute('image_size_y', '900')
        camera_seg.set_attribute('fov', str(config['fov']))
        

        camera_bp.set_attribute('image_size_x', '1600')
        camera_bp.set_attribute('image_size_y', '900')
        camera_bp.set_attribute('fov', str(config['fov']))
        camera_bp.set_attribute('sensor_tick', str(1.0 / 12.0))  # 12 Hz

        rgb_cam = world.spawn_actor(camera_bp, config['transform'], attach_to=vehicle)
        
        seg_cam = world.spawn_actor(camera_seg, config['transform'], attach_to=vehicle)

        rgb_cam.listen(lambda image: process_rgb_image(image,cam_name))
        seg_cam.listen(lambda image: process_segmentation_image(image,cam_name))
        rgb_cameras.append(rgb_cam)
        seg_cameras.append(seg_cam)
        time.sleep(15)

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print('\nCancelled by user.')
    finally:
    # 清理 CARLA 资源
        for actor in actor_list:
            actor.destroy()
