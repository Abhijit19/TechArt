import sys
import random
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QMenuBar, QMenu
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QImage, QPixmap, QAction
import numpy as np
import noise

class PerlinNoiseWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 800, 600)

        self.imageLabel = QLabel(self)
        self.imageLabel.setMinimumSize(1, 1)  
        self.setCentralWidget(self.imageLabel)

        self.dim = 720
        self.xcoords = np.linspace(0, 1, self.dim)
        self.pixmap = None
        self.flowfield = self.generatePerlinNoise()  

        

    def generatePerlinNoise(self):
        img = np.zeros((self.dim, self.dim, 1), dtype=np.uint8)
        shape = (self.dim, self.dim)
        scale = 0.5
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        seed = random.randint(0, 100)
        world = np.zeros(shape)

        # Make coordinate grid of [0, 1] by [0, 1].
        world_x, world_y = np.meshgrid(self.xcoords, self.xcoords)

        # Apply "Improved Perlin" noise.
        world = np.vectorize(noise.pnoise2)(world_x/scale, world_y/scale,
                                            octaves=octaves, persistence=persistence, lacunarity=lacunarity,
                                            repeatx=self.dim, repeaty=self.dim,
                                            base=seed)

        # Re-range image values.
        img = np.floor((world + 0.5) * 255).astype(np.uint8)

        self.pixmap = QPixmap.fromImage(QImage(img.data, img.shape[1], img.shape[0], QImage.Format_Grayscale8))
        self.pixmap = self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(self.pixmap)

        flowfield = world
        #print(world[0,0])
        #print(flowfield[0,0])
        return flowfield
       
class EllipseWindow(QMainWindow):
    def __init__(self, flowfield,num_particles=1000): 
        super().__init__()
        self.setStyleSheet("background-color: black;") 

       

        self.flowfield = flowfield
        self.num_particles = num_particles
        self.pixmap = None

        self.particlepos = 1.0*np.random.randint(0, 720, size=(self.num_particles, 2))
        self.setGeometry(100, 100, 800, 800)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateEllipses)
        self.timer.start(100) 

    def updateEllipses(self):
        
        self.updateParticles()

        
        self.update()

    def updateParticles(self):
        

        for i in range(self.num_particles):
            x_ = self.flowfield[self.particlepos[i, 0].astype(int), self.particlepos[i, 1].astype(int)]
            y_ = self.flowfield[self.particlepos[i, 0].astype(int), self.particlepos[i, 1].astype(int)]
            
            self.particlepos[i, 0] = (self.particlepos[i, 0] + x_ * 20) % 720
            self.particlepos[i, 1] = (self.particlepos[i, 1] + y_ * 20) % 720

        
               
    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(QColor(255, 255, 255))
        painter.setPen(pen)
        brush = QBrush(QColor(255, 255, 255))
        painter.setBrush(brush)

        
        for x in range(self.num_particles):
            painter.drawEllipse(self.particlepos[x, 0], self.particlepos[x, 1], 2, 2)


        painter.end()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    perlin_noise_win = PerlinNoiseWindow()
    perlin_noise_win.show()

    ellipse_win = EllipseWindow(perlin_noise_win.flowfield, num_particles=1000)

    ellipse_win.show()

    sys.exit(app.exec())
