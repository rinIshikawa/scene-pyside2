"""PySide2 & OpenGL sample"""

import sys

from PySide2 import QtCore, QtWidgets, QtOpenGL
from glmatrix import *
from ctypes import sizeof, c_float, c_void_p, c_uint

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

def generateModelFromObj(text, vertices, triangles):
    lines = text.split('\n');
    lines = list(filter(lambda x: len(x) > 0, lines))
    vc = 0;
    tc = 0;
    for i in range(len(lines)):
        params = lines[i].strip().split(' ');
        params = list(filter(lambda x: len(x) > 0, params))
        if len(params) == 0: 
            continue;

        if params[0] == "v":
            # Append vertex.
            vertices.append(float(params[1]));
            vertices.append(float(params[2]));
            vertices.append(float(params[3]));
            vc += 1;
        elif params[0] == "f":
            # Append triangle.
            triangles.append(int(params[1]) - 1);
            triangles.append(int(params[2]) - 1);
            triangles.append(int(params[3]) - 1);
            tc += 1;

def generateNormals(vertices, triangles, normals):
    for i in range(0, len(triangles), 3):
        # Find the face normal
        vertex1 = vec3_fromValues(vertices[triangles[i] * 3], vertices[triangles[i] * 3 + 1], vertices[triangles[i] * 3 + 2]);
        vertex2 = vec3_fromValues(vertices[triangles[i + 1] * 3], vertices[triangles[i + 1] * 3 + 1], vertices[triangles[i + 1] * 3 + 2]);
        vertex3 = vec3_fromValues(vertices[triangles[i + 2] * 3], vertices[triangles[i + 2] * 3 + 1], vertices[triangles[i + 2] * 3 + 2]);

        vect31 = vec3_create();
        vect21 = vec3_create();
        vec3_sub(vect21, vertex2, vertex1);
        vec3_sub(vect31, vertex3, vertex1)
        v = vec3_create();
        vec3_cross(v, vect21, vect31);

        # Add the face normal to all the faces vertices
        normals[triangles[i] * 3] += v[0];
        normals[triangles[i] * 3 + 1] += v[1];
        normals[triangles[i] * 3 + 2] += v[2];

        normals[triangles[i + 1] * 3] += v[0];
        normals[triangles[i + 1] * 3 + 1] += v[1];
        normals[triangles[i + 1] * 3 + 2] += v[2];

        normals[triangles[i + 2] * 3] += v[0];
        normals[triangles[i + 2] * 3 + 1] += v[1];
        normals[triangles[i + 2] * 3 + 2] += v[2];

    # Normalize each vertex normal
    for i in range(0, len(normals), 3):
        v = vec3_fromValues(normals[i], normals[i + 1], normals[i + 2]);
        vec3_normalize(v, v);

        normals[i] = v[0];
        normals[i + 1] = v[1];
        normals[i + 2] = v[2];

vertexShaderSource ='''#version 330
attribute vec4 aVertexPosition;
varying vec4 col;
uniform vec4 uColor;
uniform mat4 uModelMatrix;
uniform mat4 uViewMatrix;
uniform mat4 uProjectionMatrix;

void main() {
    col = uColor;
    gl_Position = uProjectionMatrix * uViewMatrix * uModelMatrix * aVertexPosition;
}
''';

fragmentShaderSource = '''#version 330
varying vec4 col;

void main() {
    gl_FragColor = col;
}
'''

# vec3LightPosition = vec3_create()
# vec3AmbientColor = vec3_create()
# vec3DiffuseColor = vec3_create()
# vec3SpecularColor = vec3_create()
vec3LightPosition = [0, 10, 4];
vec3AmbientColor = [0.1, 0.1, 0.1];
vec3DiffuseColor = [0.82, 0.81, 0.8];
vec3SpecularColor = [0.6, 0.61, 0.62];

matModel = mat4_create()
matView = mat4_create()
matProjection = mat4_create()

fFogDensity = 0.001

colors = [
    1.0, 0.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 0.0, 1.0
]


normals = [
    0, 0, 0,
    0, 0, 0,
    0, 0, 0
]
verticesCube = []
verticesSphere = []

trianglesCube = []
triangleSphere = []


verticesCube = [
    0, 0, 1,
    0, 1, 1,
    1, 1, 1,
    1, 0, 1,

    0, 0, 0,
    0, 1, 0,
    1, 1, 0,
    1, 0, 0,
];

trianglesCube = [
    0, 1, 2, 0, 2, 3,
    4, 7, 6, 4, 6, 5,
    0, 4, 5, 0, 5, 1,
    3, 2, 6, 3, 6, 7,
    1, 5, 6, 1, 6, 2,
    0, 3, 7, 0, 7, 4,
];
   
for i in range(len(verticesCube)):
    normals.append(0);
    colors.append(1.0);
generateNormals(verticesCube, trianglesCube, normals);

with open('sphere.obj') as f:
    text = f.read()
    colors = [];
    normals = [];
    verticesSphere = [];
    trianglesSphere = [];
    generateModelFromObj(text, verticesSphere, trianglesSphere);
    for i in range(len(verticesSphere)):
        normals.append(0);
        colors.append(1.0);
    generateNormals(verticesSphere, trianglesSphere, normals);

position = vec3_create()
rotation = quat_create()
scale = vec3_create()
position = [0, 0, 0]
quat_identity(rotation)
scale = [1, 1, 1]

fogOn = 0.001

def castUintArr(arr):
    return (c_uint*len(arr))(*arr)

def castFloatArr(arr):
    return (c_float*len(arr))(*arr)

class GLWidget(QtOpenGL.QGLWidget):
    x_rotation_changed = QtCore.Signal(int)
    y_rotation_changed = QtCore.Signal(int)
    z_rotation_changed = QtCore.Signal(int)

    programData = None
    program = None

    canvasWidth = 100
    canvasHeight = 100
    objectList = []

    camPosition = [0, 1, 4]
    camRotation = quat_create()

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
        timer.timeout.connect(self.tick)
        timer.start(1000)

    def setObjList(self, objectList):
        self.objectList = objectList
        self.updateGL()


    def initializeGL(self):
        """Set up the rendering context, define display lists etc."""
        vertexShader = glCreateShader(GL_VERTEX_SHADER);
        glShaderSource(vertexShader, vertexShaderSource);
        glCompileShader(vertexShader);
        if glGetShaderiv(vertexShader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(vertexShader))

        fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
        glShaderSource(fragmentShader, fragmentShaderSource);
        glCompileShader(fragmentShader);
        if glGetShaderiv(fragmentShader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(fragmentShader))

        program = glCreateProgram();
        glAttachShader(program, vertexShader);
        glAttachShader(program, fragmentShader);
        glLinkProgram(program);
        if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
            raise RuntimeError(glGetProgramInfoLog(program))
        self.program = program

        # glUseProgram(program)
        # Setup the uniform locations
        programData = {};
        programData['locLightPosition'] = glGetUniformLocation(program, "uLightPosition");
        programData['locAmbientColor'] = glGetUniformLocation(program, "uAmbientColor");
        programData['locDiffuseColor'] = glGetUniformLocation(program, "uDiffuseColor");
        programData['locSpecularColor'] = glGetUniformLocation(program, "uSpecularColor");
        programData['locCameraPosition'] = glGetUniformLocation(program, "uCameraPosition");
        programData['locNormalMatrix'] = glGetUniformLocation(program, "uNormalMatrix");
        programData['locModelNormalMatrix'] = glGetUniformLocation(program, "uModelNormalMatrix");
        programData['locModelMatrix'] = glGetUniformLocation(program, "uModelMatrix");
        programData['locViewMatrix'] = glGetUniformLocation(program, "uViewMatrix");
        programData['locProjectionMatrix'] = glGetUniformLocation(program, "uProjectionMatrix");
        programData['locFogDensity'] = glGetUniformLocation(program, "uFogDensity");

        programData['uColor'] = glGetUniformLocation(program, "uColor");

        # Setup the buffer objects and attributes
        programData['bufVertexNormal'] = glGenBuffers(1);
        programData['attribVertexNormal'] = glGetAttribLocation(program, "aVertexNormal");
        programData['bufVertexPosition'] = glGenBuffers(1);
        programData['attribVertexPosition'] = glGetAttribLocation(program, "aVertexPosition");

        programData['posAttr'] = glGetAttribLocation(program, 'posAttr');
        programData['colAttr'] = glGetAttribLocation(program, 'colAttr');
        programData['matrix'] = glGetUniformLocation(program, 'matrix');

        # No attribute for triangle buffer
        programData['bufTriangle'] = glGenBuffers(1);
        self.programData = programData
        print(programData)

        self.shape1 = self.make_shape()
        # glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)

    def paintGL(self):
        """draw the scene:"""
        programData = self.programData

        # glClear(GL_COLOR_BUFFER_BIT);

        # glUseProgram(self.program);

        # self.camPosition = [0, 0, 1];
        # mat4_fromRotationTranslation(matView, self.camRotation, self.camPosition);
        # mat4_invert(matView, matView);

        # mat4_perspective(matProjection, pi / 2, canvasWidth / canvasHeight, 0.001, 3000);
        # glUniformMatrix4fv(programData['matrix'], 1, False, matProjection);

        # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, programData['bufTriangle']);
        # glBufferData(GL_ELEMENT_ARRAY_BUFFER, castUintArr(triangles), GL_STATIC_DRAW);

        # glVertexAttribPointer(programData['posAttr'], 3, GL_FLOAT, GL_FALSE, 0, vertices);
        # glVertexAttribPointer(programData['colAttr'], 3, GL_FLOAT, GL_FALSE, 0, colors);

        # glEnableVertexAttribArray(programData['posAttr']);
        # glEnableVertexAttribArray(programData['colAttr']);

        # glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, c_void_p(0));

        # return
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # glPushMatrix()
        # self.draw_shape(self.shape1, -1.0, -1.0, 0.0,
        #     (self.x_shape_rot, self.y_shape_rot, self.z_shape_rot))

        
        # vec3.transformQuat(camPosition, camPosition, self.camRotation);

        # Model matrix
        mat4_fromRotationTranslationScale(matModel, rotation, position, scale);

        # View matrix
        mat4_fromRotationTranslation(matView, self.camRotation, self.camPosition);
        mat4_invert(matView, matView);

        # Projection matrix
        mat4_perspective(matProjection, pi / 2, self.canvasWidth / self.canvasHeight, 0.001, 3000);

        glClearColor(0.5, 0.5, 0.5, 1.0);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glLoadIdentity();

        # glEnable(GL_CULL_FACE);
        # glCullFace(GL_BACK);
        # glDisable(GL_CULL_FACE);

        # Render teapot
        glUseProgram(self.program);
        # glDepthMask(True);

        # Light
        # Since it is not restricted, I use a light that follows the camera
        #var lightPosition = vec3.clone(vec3LightPosition);
        #vec3.transformMat4(lightPosition, lightPosition, matSkyView);

        glUniform3fv(programData['locLightPosition'], 1, vec3LightPosition);
        glUniform3fv(programData['locAmbientColor'], 1, vec3AmbientColor);
        glUniform3fv(programData['locDiffuseColor'], 1, vec3DiffuseColor);
        glUniform3fv(programData['locSpecularColor'], 1, vec3SpecularColor);
        glUniform3fv(programData['locCameraPosition'], 1, self.camPosition);

        # Matrices
        matModelView = mat4_create();
        mat4_multiply(matModelView, matView, matModel);

        matNormal = mat3_create();
        mat3_fromMat4(matNormal, matModelView);
        mat3_transpose(matNormal, matNormal);
        mat3_invert(matNormal, matNormal);
        glUniformMatrix3fv(programData['locNormalMatrix'], 1, False, matNormal);

        # Normal matrix for model transform
        mat3_fromMat4(matNormal, matModel);
        mat3_transpose(matNormal, matNormal);
        mat3_invert(matNormal, matNormal);
        glUniformMatrix3fv(programData['locModelNormalMatrix'], 1, False, matNormal);

        glUniformMatrix4fv(programData['locModelMatrix'], 1, False, matModel);
        glUniformMatrix4fv(programData['locViewMatrix'], 1, False, matView);
        glUniformMatrix4fv(programData['locProjectionMatrix'], 1, False, matProjection);

        for obj in self.objectList:
            glUniform4fv(programData['uColor'], 1, obj.get_color());
            
            rot = obj.get_rotation()
            mat4_fromRotationTranslationScale(matModel, quat_fromEuler(rotation, rot[0], rot[1], rot[2]), obj.get_translation(), obj.get_scale());
            glUniformMatrix4fv(programData['locModelMatrix'], 1, False, matModel);

            if obj.get_geometry() == 'cube':
                glVertexAttribPointer(programData['attribVertexPosition'], 3, GL_FLOAT, GL_FALSE, 0, verticesCube);
                glEnableVertexAttribArray(programData['attribVertexPosition']);

                # Triangles
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, programData['bufTriangle']);
                glBufferData(GL_ELEMENT_ARRAY_BUFFER, castUintArr(trianglesCube), GL_STATIC_DRAW);
                glDrawElements(GL_TRIANGLES, len(trianglesCube), GL_UNSIGNED_INT, c_void_p(0));

                glDrawElements(GL_TRIANGLES, len(trianglesCube), GL_UNSIGNED_INT, c_void_p(0));

            elif obj.get_geometry() == 'sphere':
                glVertexAttribPointer(programData['attribVertexPosition'], 3, GL_FLOAT, GL_FALSE, 0, verticesSphere);
                glEnableVertexAttribArray(programData['attribVertexPosition']);

                # Triangles
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, programData['bufTriangle']);
                glBufferData(GL_ELEMENT_ARRAY_BUFFER, castUintArr(trianglesSphere), GL_STATIC_DRAW);
                glDrawElements(GL_TRIANGLES, len(trianglesSphere), GL_UNSIGNED_INT, c_void_p(0));

                glDrawElements(GL_TRIANGLES, len(trianglesSphere), GL_UNSIGNED_INT, c_void_p(0));

        # Vertex normals
        # glBindBuffer(GL_ARRAY_BUFFER, programData['bufVertexNormal']);
        # glBufferData(GL_ARRAY_BUFFER, castFloatArr(normals), GL_DYNAMIC_DRAW);
        # glVertexAttribPointer(programData['attribVertexNormal'], 3, GL_FLOAT, False, 3 *  sizeof(c_float), 0);
        # glEnableVertexAttribArray(programData['attribVertexNormal']);

        # Vertex vertices
        # glVertexAttribPointer(programData['attribVertexPosition'], 3, GL_FLOAT, GL_FALSE, 0, verticesSphere);
        # glEnableVertexAttribArray(programData['attribVertexPosition']);

        # # Triangles
        # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, programData['bufTriangle']);
        # glBufferData(GL_ELEMENT_ARRAY_BUFFER, castUintArr(trianglesSphere), GL_STATIC_DRAW);
        # glDrawElements(GL_TRIANGLES, len(trianglesSphere), GL_UNSIGNED_INT, c_void_p(0));

        # mat4_fromRotationTranslationScale(matModel, rotation, [2, 0, 0], scale);
        # glUniformMatrix4fv(programData['locModelMatrix'], 1, False, matModel);
        # glDrawElements(GL_TRIANGLES, len(trianglesSphere), GL_UNSIGNED_INT, c_void_p(0));

        print(len(verticesSphere) / 3, len(trianglesSphere) / 3)

    def resizeGL(self, width, height):
        """setup viewport, projection etc."""
        # side = min(width, height)
        # if side < 0:
        #     return
        # glViewport(int((width - side) / 2), int((height - side) / 2), side, side)
        glViewport(0, 0, width, height)

        # glMatrixMode(GL_PROJECTION)
        # glLoadIdentity()
        # glFrustum(-1.2, +1.2, -1.2, 1.2, 6.0, 70.0)
        # glMatrixMode(GL_MODELVIEW)
        # glLoadIdentity()
        # glTranslated(0.0, 0.0, -20.0)
        self.canvasWidth = width
        self.canvasHeight = height

        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();

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

    def tick(self):
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


