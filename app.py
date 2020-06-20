import sys

from PySide2 import QtCore, QtWidgets, QtOpenGL, QtGui
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import (QAction, QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QListWidget, QListWidgetItem)
from PySide2.QtCharts import QtCharts


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


class GLWidget(QtOpenGL.QGLWidget):
    x_rotation_changed = QtCore.Signal(int)
    y_rotation_changed = QtCore.Signal(int)
    z_rotation_changed = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shape1 = None
        self.x_rot_speed = 0
        self.x_shape_rot = 0
        self.y_rot_speed = 0
        self.y_shape_rot = 0
        self.z_rot_speed = 0
        self.z_shape_rot = 0

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.advance)
        timer.start(20)

    def initializeGL(self):
        """Set up the rendering context, define display lists etc."""
        glEnable(GL_DEPTH_TEST)
        self.shape1 = self.make_shape()
        glEnable(GL_NORMALIZE)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def paintGL(self):
        """draw the scene:"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        self.draw_shape(self.shape1, -1.0, -1.0, 0.0,
            (self.x_shape_rot, self.y_shape_rot, self.z_shape_rot))
        glPopMatrix()

    def resizeGL(self, width, height):
        """setup viewport, projection etc."""
        side = min(width, height)
        if side < 0:
            return

        glViewport(int((width - side) / 2), int((height - side) / 2), side, side)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glFrustum(-1.2, +1.2, -1.2, 1.2, 6.0, 70.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslated(0.0, 0.0, -20.0)

    def free_resources(self):
        """Helper to clean up resources."""
        self.makeCurrent()
        glDeleteLists(self.shape1, 1)

    # slots
    def set_x_rot_speed(self, speed):
        self.x_rot_speed = speed
        self.updateGL()

    def set_y_rot_speed(self, speed):
        self.y_rot_speed = speed
        self.updateGL()

    def set_z_rot_speed(self, speed):
        self.z_rot_speed = speed
        self.updateGL()

    def advance(self):
        """Used in timer to actually rotate the shape."""
        self.x_shape_rot += self.x_rot_speed
        self.x_shape_rot %= 360
        self.y_shape_rot += self.y_rot_speed
        self.y_shape_rot %= 360
        self.z_shape_rot += self.z_rot_speed
        self.z_shape_rot %= 360
        self.updateGL()

    def make_shape(self):
        """Helper to create the shape and return list of resources."""
        list = glGenLists(1)
        glNewList(list, GL_COMPILE)

        glNormal3d(0.0, 0.0, 0.0)

        # Vertices
        a = ( 1, -1, -1),
        b = ( 1,  1, -1),
        c = (-1,  1, -1),
        d = (-1, -1, -1),
        e = ( 1, -1,  1),
        f = ( 1,  1,  1),
        g = (-1, -1,  1),
        h = (-1,  1,  1)

        edges = [
            (a, b), (a, d), (a, e),
            (c, b), (c, d), (c, h),
            (g, d), (g, e), (g, h),
            (f, b), (f, e), (f, h)
        ]

        glBegin(GL_LINES)
        for edge in edges:
            glVertex3fv(edge[0])
            glVertex3fv(edge[1])
        glEnd()

        glEndList()

        return list

    def draw_shape(self, shape, dx, dy, dz, rotation):
        """Helper to translate, rotate and draw the shape."""
        glPushMatrix()
        glTranslated(dx, dy, dz)
        glRotated(rotation[0], 1.0, 0.0, 0.0)
        glRotated(rotation[1], 0.0, 1.0, 0.0)
        glRotated(rotation[2], 0.0, 0.0, 1.0)
        glCallList(shape)
        glPopMatrix()



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
        return f'{self.name} {self.color} {self.pos}'


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.items = 0

        # Example data
        self.object_list = []
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
        self.right.addWidget(QLabel("position (x, y, z)"))
        self.right.addWidget(self.position)
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


    @Slot()
    def add_cube(self):
        cube = Geometry('cube')
        item = QListWidgetItem()
        item.setText(cube.name)
        self.listWidget.addItem(item)
        item.setData(QtCore.Qt.UserRole, cube)

        self.object_list.append(cube)
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
        # QListWidgetItem(sphere.name, self.listWidget)
        print(item.text())


    @Slot()
    def delete_object(self):
        try:
            row = self.listWidget.row(self.current_item)
            del self.object_list[row]
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