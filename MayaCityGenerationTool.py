import maya.cmds as cmds
import random
import math
import os
from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)

class SimpleMayaWindow(QMainWindow):
    def __init__(self, parent=maya_main_window()):
        super(SimpleMayaWindow, self).__init__(parent)
        self.setWindowTitle("Procedural buildings by Abhi")
        self.setGeometry(100, 100, 400, 200)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        label = QLabel("Let's build a city.Click the button to do so!But make sure you select a ground to do it on", central_widget)
        layout.addWidget(label)


        button = QPushButton("Create", central_widget)
        layout.addWidget(button)

        button2 = QPushButton("CameraMovement", central_widget)
        layout.addWidget(button)


        button.clicked.connect(self.on_button_pressed)
        button2.clicked.connect(self.on_button2_pressed)

    def on_button_pressed(self):
        createCity()

    def on_button2_pressed(self):
        handheld_camera()
def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def lerp(t, a, b):
    return a + t * (b - a)

def grad(hash, x):
    h = hash & 15
    grad = 1 + (h & 7) if h < 8 else -1
    return grad * x

def perlin_noise_function(width, height, scale, octaves, persistence, lacunarity, seed):
    p = list(range(512))
    random.seed(seed)
    random.shuffle(p)
    p += p

    world = [[0] * width for _ in range(height)]

    for y in range(height):
        for x in range(width):
            X = int(math.floor(x / scale)) & 255
            Y = int(math.floor(y / scale)) & 255

            x -= math.floor(x / scale)
            y -= math.floor(y / scale)

            u = fade(x)
            v = fade(y)

            a = p[X] + Y
            b = p[X + 1] + Y

            world[y][x] = lerp(v, lerp(u, grad(p[a], x), grad(p[b], x - 1)),
                               lerp(u, grad(p[a + 1], x), grad(p[b + 1], x - 1)))

    return world


def assign_texture(object_name):
   
  
    texture_path = "G:\TATDFinal\downtown1.jpg"

    file_node = cmds.shadingNode('file', asTexture=True)
    

    cmds.setAttr(file_node + '.fileTextureName', texture_path, type='string')


    shading_node = cmds.shadingNode('lambert', asShader=True)
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shading_node + 'SG')
    cmds.connectAttr(shading_node + '.outColor', shading_group + '.surfaceShader')


    cmds.connectAttr(file_node + '.outColor', shading_node + '.color')


    cmds.select(object_name)
    cmds.hyperShade(assign=shading_node)








def spawn_city_on_plane(width, height, noise_map):
    threshold = 0.5
    min_height = 1
    max_height = 10
    building_scale = 0.2
    num_sets = 5  
    Skyscraper_lim = 0


    selected_plane = cmds.ls(selection=True, type="transform")
    if not selected_plane:
        cmds.error("Please select a ground.")
        return

    plane_position = cmds.xform(selected_plane[0], query=True, translation=True)

    for _ in range(num_sets):
        set_offset_x = random.uniform(0, 75)
        set_offset_z = random.uniform(0, 75)

        for y in range(len(noise_map)):
            for x in range(len(noise_map[0])):
                value = noise_map[y][x]
                building_height = random.randint(min_height, max_height)
                offset_x = random.uniform(2, 5)  
                offset_z = random.uniform(2, 5)

                if value == 0:
                    if Skyscraper_lim < 10:
                        Skyscraper_lim += 1

                        building = "Home"
                        duplicated_object = cmds.duplicate(building, name=building + "_duplicate{}".format(x))[0]

                            
                        x_position = x * building_scale*20  + offset_x+50 + set_offset_x + plane_position[0]
                        z_position = y * building_scale*20  + offset_z+50 + set_offset_z + plane_position[2]

                        cmds.move(x_position, plane_position[1], z_position, duplicated_object)
                        #assign_texture(duplicated_object, is_building=False)

                if value > threshold:
                    building = cmds.polyCube(width=building_scale*10, height=building_height, depth=building_scale*10)[0]

     
                    x_position = x * building_scale + offset_x + set_offset_x + plane_position[0]
                    z_position = y * building_scale + offset_z + set_offset_z + plane_position[2]

                    cmds.move(x_position, plane_position[1] + building_height / 2, z_position, building)
                    assign_texture(building)


def createCity():
    width = 50
    height = 50
    octaves = 6
    persistence = 0.5
    lacunarity = 2.0
    seed = random.randint(1, 100)

    noise_map = perlin_noise_function(width, height, scale=5, octaves=octaves, persistence=persistence, lacunarity=lacunarity, seed=seed)
    spawn_city_on_plane(width, height, noise_map)

   
    obj_del="Home_duplicate0"
    if cmds.objExists(obj_del):
        cmds.delete(obj_del)
    obj_del="Home_duplicate1"
    if cmds.objExists(obj_del):
        cmds.delete(obj_del)

def handheld_camera():
    # Ensure a transform node is selected.
    selection = cmds.ls(selection=True, type='transform')
    if not selection:
        raise Exception("Please select a camera's transform node.")
    transform_node = selection[0]

    # Find the range of keyframes on timeline.
    start_frame, end_frame = cmds.playbackOptions(query=True, min=True), cmds.playbackOptions(query=True, max=True)
    x=581
    y=446
    z=-711
    t=[x,y,z]
    
    # Iterate over the keyframes using a fixed interval.
    frame = int(start_frame)
    while frame <= int(end_frame):
        cmds.currentTime(frame)

        # Sample the current transformation values of the transform node.
        t=[x,y,t[2]+50]
        r=[-18,118,0]
        
        new_translate=tuple(t)
        new_rotate=tuple(r)
        cmds.setAttr(transform_node + ".translate", *new_translate)
        cmds.setAttr(transform_node + ".rotate", *new_rotate)
        cmds.setKeyframe(transform_node, attribute='translate', time=frame)
        cmds.setKeyframe(transform_node, attribute='rotate', time=frame)
        # Set keyframe tangents to linear.
        cmds.keyTangent(transform_node, edit=True, time=(frame, frame), attribute='translate', inTangentType='linear', outTangentType='linear')
        cmds.keyTangent(transform_node, edit=True, time=(frame, frame), attribute='rotate', inTangentType='linear', outTangentType='linear')

        # Move to the next keyframe with a fixed interval.
        frame += 5  # Adjust the interval as needed.

if __name__ == "__main__":

    window_name = "simpleMayaWindow"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name, window=True)


    simple_window = SimpleMayaWindow()
    simple_window.show()
