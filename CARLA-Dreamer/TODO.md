DATA on CARLA part todo:


目的：测试工具 根据输入的指令生成对应的
1. HD MAP
2. Panotic map
3. Bounding box

Same scene, add different objects(buildings, people, vehicle etc) to the scene, and generate the corresponding HD map, panoramic map, and bounding box.

暂时不考虑天气，时间等因素

1. 在车道固定的情况下，随机生成ego, 并且在其附近生成几辆车
2. CARLA blueprint: 贴摄像头 参考nuscene 的摄像头位置
3. Panotic output 最好类别相近
4. Ego 位置 周围的HD Map 提出来，符合nuscene 的格式-
5. Bounding box 主要是坐标系的transformation 的问题





