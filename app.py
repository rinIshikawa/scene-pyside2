import sys
import math
import glfw
import pickle

from PySide2 import QtCore, QtWidgets, QtOpenGL, QtGui
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QPainter, QKeyEvent, QOpenGLShaderProgram
from PySide2.QtWidgets import (QAction, QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QOpenGLWidget)
from PySide2.QtCharts import QtCharts
from pyrr import Vector3, vector, vector3, matrix44
from ObjLoader import ObjLoader
from shader import Shader
from glmatrix import *

try:
    from OpenGL.GL import *
except ImportError:
    app = QtWidgets.QApplication(sys.argv)
    messageBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "OpenGL sample",
                                       "PyOpenGL must be installed to run this example.",
                                       QtWidgets.QMessageBox.Close)
    messageBox.setDetailedText("Run:\npip install PyOpenGL PyOpenGL_accelerate")
    messageBox.exec_()
    sys.exit(1)

from OpenGL.GL.shaders import compileProgram, compileShader
from glWidget import GLWidget

class Geometry:
    def __init__(self, geometry):
        self.name = f'new {geometry}'
        self.geometry = geometry
        self.position = [0.0, 0.0, 0.0]
        self.color = [0, 0, 1]
        self.scale = [1, 1, 1]
        self.rotation = [0, 0, 0]
        self.translation = [0, 0, 0]

    def get_name(self):
        return self.name

    def get_geometry(self):
        return self.geometry

    def get_color(self):
        return self.color

    def get_position(self):
        return self.position

    def get_scale(self):
        return self.scale

    def get_rotation(self):
        return self.rotation

    def get_translation(self):
        return self.translation

    def set_name(self,name):
        self.name = name

    def set_color(self,color):
        self.color = color

    def set_position(self,position):
        self.position = position

    def set_scale(self,scale):
        self.scale = scale

    def set_rotation(self,rotation):
        self.rotation = rotation

    def set_translation(self,translation):
        self.translation = translation

    def __repr__(self):
        return f'{self.name} {self.color}'


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.items = 0

        self.object_list = []
        try:
            f = open('cache','rb')
            self.object_list = pickle.load(f)
            print(self.object_list)
            f.close()

            for obj in self.object_list:
                print(obj)
        except:
            print("loading error")


        self.current_object = None
        self.current_item = None

        # Left
        self.left = QVBoxLayout()
        self.glWidget = GLWidget()

        self.glWidgetArea = QtWidgets.QScrollArea()
        self.glWidgetArea.setWidget(self.glWidget)
        self.glWidgetArea.setWidgetResizable(True)
        self.glWidgetArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.glWidgetArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.glWidgetArea.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
        #         QtWidgets.QSizePolicy.Ignored)
        self.glWidgetArea.setMinimumSize(200, 200)
        self.left.addWidget(self.glWidgetArea)


        # Right
        self.right = QVBoxLayout()
        self.right.setMargin(10)

        self.listWidget = QListWidget()
        self.right.addWidget(self.listWidget)

        self.addCube = QPushButton("Add Cube")
        self.addSphere = QPushButton("Add Sphere")
        self.right.addWidget(self.addCube)
        self.right.addWidget(self.addSphere)


        self.name = QLineEdit()
        self.color = QLineEdit()
        self.radius = QLineEdit()
        self.position = QLineEdit()
        self.scale = QLineEdit()
        self.rotation = QLineEdit()
        self.translation = QLineEdit()
        self.delete = QPushButton("Delete")

        self.right.addWidget(QLabel("name"))
        self.right.addWidget(self.name)
        # self.right.addWidget(QLabel("position (x, y, z)"))
        # self.right.addWidget(self.position)
        self.right.addWidget(QLabel("scale (x, y, z)"))
        self.right.addWidget(self.scale)
        self.right.addWidget(QLabel("rotation (x, y, z)"))
        self.right.addWidget(self.rotation)
        self.right.addWidget(QLabel("translation (x, y, z)"))
        self.right.addWidget(self.translation)
        self.right.addWidget(QLabel("color (r, g, b)"))
        self.right.addWidget(self.color)
        self.right.addWidget(self.delete)

        # QWidget Layout
        self.layout = QHBoxLayout()

        #self.table_view.setSizePolicy(size)
        self.layout.addLayout(self.left)
        self.layout.addLayout(self.right)

        # Set the layout to the QWidget
        self.setLayout(self.layout)

        # Signals and Slots
        self.listWidget.currentItemChanged.connect(self.item_clicked)
        self.addCube.clicked.connect(self.add_cube)
        self.addSphere.clicked.connect(self.add_sphere)
        self.delete.clicked.connect(self.delete_object)
        self.name.textChanged[str].connect(self.change_name)
        self.position.textChanged[str].connect(self.change_position)
        self.scale.textChanged[str].connect(self.change_scale)
        self.rotation.textChanged[str].connect(self.change_rotation)
        self.translation.textChanged[str].connect(self.change_translation)
        self.color.textChanged[str].connect(self.change_color)
        self.keyDownEvent = QKeyEvent(QKeyEvent.KeyPress, 10, Qt.NoModifier, '', False, 1)
        # self.keyUpEvent = QKeyEvent(QKeyEvent.KeyRelease, 10, Qt.NoModifier, '', False, 1)

        self.glWidget.setObjList(self.object_list)
        self.glWidget.updateGL()


    def keyPressEvent(self, e):
        print("pressed some key")
        print(e.key())

        # 'W'
        if e.key() == 87:
            print('W up?')
            self.glWidget.camPosition[2] -= 0.1

        # 'S'
        elif e.key() == 83:
            print('S up?')
            self.glWidget.camPosition[2] += 0.1

        # 'A'
        elif e.key() == 65:
            print('A up?')
            self.glWidget.camPosition[0] += 0.1

        # 'D'
        elif e.key() == 68:
            print('D up?')
            self.glWidget.camPosition[0] -= 0.1

        # 'Q'
        elif e.key() == 81:
            print('Q up?')
            quat_rotateY(self.glWidget.camRotation, self.glWidget.camRotation, -0.1)
        # 'E'
        elif e.key() == 69:
            print('E up?')
            quat_rotateY(self.glWidget.camRotation, self.glWidget.camRotation, 0.1)

        # 'R'
        elif e.key() == 82:
            print('R up?')
            self.glWidget.camPosition[1] -= 0.1

        # 'F'
        elif e.key() == 70:
            print('F up?')
            self.glWidget.camPosition[1] += 0.1


        self.glWidget.updateGL()

    @Slot()
    def add_cube(self):
        cube = Geometry('cube')
        item = QListWidgetItem()
        item.setText(cube.name)
        self.listWidget.addItem(item)
        item.setData(QtCore.Qt.UserRole, cube)

        self.object_list.append(cube)
        self.glWidget.setObjList(self.object_list)
        f = open('cache','wb')
        pickle.dump(self.object_list, f)
        f.close()
        # QListWidgetItem(cube.name, self.listWidget)
        print(item.text())


    @Slot()
    def add_sphere(self):
        sphere = Geometry('sphere')
        item = QListWidgetItem()
        item.setText(sphere.name)
        self.listWidget.addItem(item)
        item.setData(QtCore.Qt.UserRole, sphere)

        self.object_list.append(sphere)
        self.glWidget.setObjList(self.object_list)

        f = open('cache','wb')
        pickle.dump(self.object_list, f)
        f.close()
        
        # QListWidgetItem(sphere.name, self.listWidget)
        print(item.text())


    @Slot()
    def delete_object(self):
        try:
            row = self.listWidget.row(self.current_item)
            del self.object_list[row]
            self.glWidget.setObjList(self.object_list)
            f = open('cache','wb')
            for obj in self.object_list:
                pickle.dump(obj, f)
            f.close()
            self.listWidget.takeItem(row)
        except:
            print("Delete error.")


    @Slot()
    def item_clicked(self, arg=None):
        try:
            print(self.listWidget.currentItem().text())
            obj = arg.data(QtCore.Qt.UserRole)
            self.current_object = obj
            self.current_item = self.listWidget.currentItem()
            print('clicking the item')
            self.name.setText(obj.get_name())
            self.position.setText(str(obj.get_position())[1:-1])
            self.color.setText(str(obj.get_color())[1:-1])
            self.scale.setText(str(obj.get_scale())[1:-1])
            self.rotation.setText(str(obj.get_rotation())[1:-1])
            self.translation.setText(str(obj.get_translation())[1:-1])
            if self.listWidget.count() == 0:
                self.current_item = None
                self.current_object = None
        except:
            print("Error locating current item")


    @Slot()
    def change_name(self):
        if not self.name.text():
            pass
        else:
            try:
                self.current_object.set_name(self.name.text())
                self.current_item.setText(self.name.text())
                self.glWidget.setObjList(self.object_list)
                f = open('cache','wb')
                for obj in self.object_list:
                    pickle.dump(obj, f)
                f.close()
            except:
                print("Name change error")

    @Slot()
    def change_position(self):
        if not self.position.text():
            pass
        else:
            try:
                li = [float(s) for s in self.position.text().split(',')]
                print(len(li))
                if (len(li) > 3):
                    print("invalid input")
                    return

                while (len(li) < 3):
                    print('here')
                    li.append(0)
                self.current_object.set_position(li)
                self.glWidget.setObjList(self.object_list)
                f = open('cache','wb')
                for obj in self.object_list:
                    pickle.dump(obj, f)
                f.close()
            except:
                print("invalid input")
            print(self.current_object.get_position())


    @Slot()
    def change_color(self):
        if not self.color.text():
            pass
        else:
            try:
                li = [float(s) for s in self.color.text().split(',')]
                print(len(li))
                if (len(li) > 3):
                    print("invalid input")
                    return

                while (len(li) < 3):
                    print('here')
                    li.append(0)
                self.current_object.set_color(li)
                self.glWidget.setObjList(self.object_list)
                f = open('cache','wb')
                for obj in self.object_list:
                    pickle.dump(obj, f)
                f.close()
            except:
                print("invalid input")
            print(self.current_object.get_color())


    @Slot()
    def change_scale(self):
        if not self.scale.text():
            pass
        else:
            try:
                li = [float(s) for s in self.scale.text().split(',')]
                print(len(li))
                if (len(li) > 3):
                    print("invalid input")
                    return

                while (len(li) < 3):
                    print('here')
                    li.append(0)
                self.current_object.set_scale(li)
                self.glWidget.setObjList(self.object_list)
                f = open('cache','wb')
                for obj in self.object_list:
                    pickle.dump(obj, f)
                f.close()
            except:
                print("invalid input")
            print(self.current_object.get_scale())


    @Slot()
    def change_rotation(self):
        if not self.rotation.text():
            pass
        else:
            try:
                li = [float(s) for s in self.rotation.text().split(',')]
                print(len(li))
                if (len(li) > 3):
                    print("invalid input")
                    return

                while (len(li) < 3):
                    print('here')
                    li.append(0)
                self.current_object.set_rotation(li)
                self.glWidget.setObjList(self.object_list)
                f = open('cache','wb')
                for obj in self.object_list:
                    pickle.dump(obj, f)
                f.close()
            except:
                print("invalid input")
            print(self.current_object.get_rotation())


    @Slot()
    def change_translation(self):
        if not self.translation.text():
            pass
        else:
            try:
                li = [float(s) for s in self.translation.text().split(',')]
                print(len(li))
                if (len(li) > 3):
                    print("invalid input")
                    return

                while (len(li) < 3):
                    print('here')
                    li.append(0)
                self.current_object.set_translation(li)
                self.glWidget.setObjList(self.object_list)
                f = open('cache','wb')
                for obj in self.object_list:
                    pickle.dump(obj, f)
                f.close()
            except:
                print("invalid input")
            print(self.current_object.get_translation())


    @Slot()
    def quit_application(self):
        QApplication.quit()



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)

        self.setCentralWidget(widget)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    # QWidget
    widget = Widget()
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    window.resize(800, 600)
    window.show()
    res = app.exec_()
    widget.glWidget.free_resources()
    sys.exit(res)