import sys
from math import *
import numpy as np

def vec3_create():
  return np.zeros(3)

def vec3_fromValues(x, y, z):
  out = np.zeros(3);
  out[0] = x;
  out[1] = y;
  out[2] = z;
  return out;

def vec3_sub(out, a, b):
  out[0] = a[0] - b[0];
  out[1] = a[1] - b[1];
  out[2] = a[2] - b[2];
  return out;

def vec3_cross(out, a, b):
  ax = a[0]
  ay = a[1]
  az = a[2];
  bx = b[0]
  by = b[1]
  bz = b[2];
  out[0] = ay * bz - az * by;
  out[1] = az * bx - ax * bz;
  out[2] = ax * by - ay * bx;
  return out;

def vec3_normalize(out, a):
  x = a[0];
  y = a[1];
  z = a[2];
  length = x * x + y * y + z * z;
  if length > 0:
    length = 1 / sqrt(length);
  out[0] = a[0] * length;
  out[1] = a[1] * length;
  out[2] = a[2] * length;
  return out;

def quat_create():
  out = np.zeros(4)
  out[3] = 1
  return out

def quat_identity(out):
  out[0] = 0;
  out[1] = 0;
  out[2] = 0;
  out[3] = 1;
  return out;

def quat_rotateY(out, a, rad):
  rad *= 0.5;
  ax = a[0]
  ay = a[1]
  az = a[2]
  aw = a[3];
  by = sin(rad)
  bw = cos(rad);
  out[0] = ax * bw - az * by;
  out[1] = ay * bw + aw * by;
  out[2] = az * bw + ax * by;
  out[3] = aw * bw - ay * by;
  return out;


def quat_fromEuler(out, x, y, z):
  halfToRad = (0.5 * pi) / 180.0;
  x *= halfToRad;
  y *= halfToRad;
  z *= halfToRad;
  sx = sin(x);
  cx = cos(x);
  sy = sin(y);
  cy = cos(y);
  sz = sin(z);
  cz = cos(z);
  out[0] = sx * cy * cz - cx * sy * sz;
  out[1] = cx * sy * cz + sx * cy * sz;
  out[2] = cx * cy * sz - sx * sy * cz;
  out[3] = cx * cy * cz + sx * sy * sz;
  return out;


def mat3_create():
  out = np.zeros(9)
  out[0] = 1;
  out[4] = 1;
  out[8] = 1;
  return out;

def mat3_fromMat4(out, a):
  out[0] = a[0];
  out[1] = a[1];
  out[2] = a[2];
  out[3] = a[4];
  out[4] = a[5];
  out[5] = a[6];
  out[6] = a[8];
  out[7] = a[9];
  out[8] = a[10];
  return out;

def mat3_transpose(out, a):
  # If we are transposing ourselves we can skip a few steps but have to cache some values
  if out is a:
    a01 = a[1];
    a02 = a[2];
    a12 = a[5];
    out[1] = a[3];
    out[2] = a[6];
    out[3] = a01;
    out[5] = a[7];
    out[6] = a02;
    out[7] = a12;
  else:
    out[0] = a[0];
    out[1] = a[3];
    out[2] = a[6];
    out[3] = a[1];
    out[4] = a[4];
    out[5] = a[7];
    out[6] = a[2];
    out[7] = a[5];
    out[8] = a[8];

  return out;

def mat3_invert(out, a):
  a00 = a[0];
  a01 = a[1];
  a02 = a[2];
  a10 = a[3];
  a11 = a[4];
  a12 = a[5];
  a20 = a[6];
  a21 = a[7];
  a22 = a[8];
  b01 = a22 * a11 - a12 * a21;
  b11 = -a22 * a10 + a12 * a20;
  b21 = a21 * a10 - a11 * a20;
  # Calculate the determinant
  det = a00 * b01 + a01 * b11 + a02 * b21;
  det = 1.0 / det;
  out[0] = b01 * det;
  out[1] = (-a22 * a01 + a02 * a21) * det;
  out[2] = (a12 * a01 - a02 * a11) * det;
  out[3] = b11 * det;
  out[4] = (a22 * a00 - a02 * a20) * det;
  out[5] = (-a12 * a00 + a02 * a10) * det;
  out[6] = b21 * det;
  out[7] = (-a21 * a00 + a01 * a20) * det;
  out[8] = (a11 * a00 - a01 * a10) * det;
  return out;

def mat4_create():
  out = np.zeros(16)
  out[0] = 1;
  out[5] = 1;
  out[10] = 1;
  out[15] = 1;
  return out;

def mat4_multiply(out, a, b):
  a00 = a[0];
  a01 = a[1];
  a02 = a[2];
  a03 = a[3];
  a10 = a[4];
  a11 = a[5];
  a12 = a[6];
  a13 = a[7];
  a20 = a[8];
  a21 = a[9];
  a22 = a[10];
  a23 = a[11];
  a30 = a[12];
  a31 = a[13];
  a32 = a[14];
  a33 = a[15];
  # Cache only the current line of the second matrix
  b0 = b[0];
  b1 = b[1];
  b2 = b[2];
  b3 = b[3];
  out[0] = b0 * a00 + b1 * a10 + b2 * a20 + b3 * a30;
  out[1] = b0 * a01 + b1 * a11 + b2 * a21 + b3 * a31;
  out[2] = b0 * a02 + b1 * a12 + b2 * a22 + b3 * a32;
  out[3] = b0 * a03 + b1 * a13 + b2 * a23 + b3 * a33;
  b0 = b[4];
  b1 = b[5];
  b2 = b[6];
  b3 = b[7];
  out[4] = b0 * a00 + b1 * a10 + b2 * a20 + b3 * a30;
  out[5] = b0 * a01 + b1 * a11 + b2 * a21 + b3 * a31;
  out[6] = b0 * a02 + b1 * a12 + b2 * a22 + b3 * a32;
  out[7] = b0 * a03 + b1 * a13 + b2 * a23 + b3 * a33;
  b0 = b[8];
  b1 = b[9];
  b2 = b[10];
  b3 = b[11];
  out[8] = b0 * a00 + b1 * a10 + b2 * a20 + b3 * a30;
  out[9] = b0 * a01 + b1 * a11 + b2 * a21 + b3 * a31;
  out[10] = b0 * a02 + b1 * a12 + b2 * a22 + b3 * a32;
  out[11] = b0 * a03 + b1 * a13 + b2 * a23 + b3 * a33;
  b0 = b[12];
  b1 = b[13];
  b2 = b[14];
  b3 = b[15];
  out[12] = b0 * a00 + b1 * a10 + b2 * a20 + b3 * a30;
  out[13] = b0 * a01 + b1 * a11 + b2 * a21 + b3 * a31;
  out[14] = b0 * a02 + b1 * a12 + b2 * a22 + b3 * a32;
  out[15] = b0 * a03 + b1 * a13 + b2 * a23 + b3 * a33;
  return out;

def mat4_fromRotationTranslationScale(out, q, v, s):
  # Quaternion math
  x = q[0]
  y = q[1]
  z = q[2]
  w = q[3];
  x2 = x + x;
  y2 = y + y;
  z2 = z + z;
  xx = x * x2;
  xy = x * y2;
  xz = x * z2;
  yy = y * y2;
  yz = y * z2;
  zz = z * z2;
  wx = w * x2;
  wy = w * y2;
  wz = w * z2;
  sx = s[0];
  sy = s[1];
  sz = s[2];
  out[0] = (1 - (yy + zz)) * sx;
  out[1] = (xy + wz) * sx;
  out[2] = (xz - wy) * sx;
  out[3] = 0;
  out[4] = (xy - wz) * sy;
  out[5] = (1 - (xx + zz)) * sy;
  out[6] = (yz + wx) * sy;
  out[7] = 0;
  out[8] = (xz + wy) * sz;
  out[9] = (yz - wx) * sz;
  out[10] = (1 - (xx + yy)) * sz;
  out[11] = 0;
  out[12] = v[0];
  out[13] = v[1];
  out[14] = v[2];
  out[15] = 1;
  return out;

def mat4_fromRotationTranslation(out, q, v):
  # Quaternion math
  x = q[0]
  y = q[1]
  z = q[2]
  w = q[3];
  x2 = x + x;
  y2 = y + y;
  z2 = z + z;
  xx = x * x2;
  xy = x * y2;
  xz = x * z2;
  yy = y * y2;
  yz = y * z2;
  zz = z * z2;
  wx = w * x2;
  wy = w * y2;
  wz = w * z2;
  out[0] = 1 - (yy + zz);
  out[1] = xy + wz;
  out[2] = xz - wy;
  out[3] = 0;
  out[4] = xy - wz;
  out[5] = 1 - (xx + zz);
  out[6] = yz + wx;
  out[7] = 0;
  out[8] = xz + wy;
  out[9] = yz - wx;
  out[10] = 1 - (xx + yy);
  out[11] = 0;
  out[12] = v[0];
  out[13] = v[1];
  out[14] = v[2];
  out[15] = 1;
  return out;

def mat4_invert(out, a):
  a00 = a[0]
  a01 = a[1]
  a02 = a[2]
  a03 = a[3];
  a10 = a[4]
  a11 = a[5]
  a12 = a[6]
  a13 = a[7];
  a20 = a[8]
  a21 = a[9]
  a22 = a[10]
  a23 = a[11];
  a30 = a[12]
  a31 = a[13]
  a32 = a[14]
  a33 = a[15];
  b00 = a00 * a11 - a01 * a10;
  b01 = a00 * a12 - a02 * a10;
  b02 = a00 * a13 - a03 * a10;
  b03 = a01 * a12 - a02 * a11;
  b04 = a01 * a13 - a03 * a11;
  b05 = a02 * a13 - a03 * a12;
  b06 = a20 * a31 - a21 * a30;
  b07 = a20 * a32 - a22 * a30;
  b08 = a20 * a33 - a23 * a30;
  b09 = a21 * a32 - a22 * a31;
  b10 = a21 * a33 - a23 * a31;
  b11 = a22 * a33 - a23 * a32;
  # Calculate the determinant
  det = b00 * b11 - b01 * b10 + b02 * b09 + b03 * b08 - b04 * b07 + b05 * b06;
  det = 1.0 / det;
  out[0] = (a11 * b11 - a12 * b10 + a13 * b09) * det;
  out[1] = (a02 * b10 - a01 * b11 - a03 * b09) * det;
  out[2] = (a31 * b05 - a32 * b04 + a33 * b03) * det;
  out[3] = (a22 * b04 - a21 * b05 - a23 * b03) * det;
  out[4] = (a12 * b08 - a10 * b11 - a13 * b07) * det;
  out[5] = (a00 * b11 - a02 * b08 + a03 * b07) * det;
  out[6] = (a32 * b02 - a30 * b05 - a33 * b01) * det;
  out[7] = (a20 * b05 - a22 * b02 + a23 * b01) * det;
  out[8] = (a10 * b10 - a11 * b08 + a13 * b06) * det;
  out[9] = (a01 * b08 - a00 * b10 - a03 * b06) * det;
  out[10] = (a30 * b04 - a31 * b02 + a33 * b00) * det;
  out[11] = (a21 * b02 - a20 * b04 - a23 * b00) * det;
  out[12] = (a11 * b07 - a10 * b09 - a12 * b06) * det;
  out[13] = (a00 * b09 - a01 * b07 + a02 * b06) * det;
  out[14] = (a31 * b01 - a30 * b03 - a32 * b00) * det;
  out[15] = (a20 * b03 - a21 * b01 + a22 * b00) * det;
  return out;

def mat4_perspective(out, fovy, aspect, near, far):
  f = 1.0 / tan(fovy / 2)
  out[0] = f / aspect;
  out[1] = 0;
  out[2] = 0;
  out[3] = 0;
  out[4] = 0;
  out[5] = f;
  out[6] = 0;
  out[7] = 0;
  out[8] = 0;
  out[9] = 0;
  out[11] = -1;
  out[12] = 0;
  out[13] = 0;
  out[15] = 0;
  nf = 1 / (near - far);
  out[10] = (far + near) * nf;
  out[14] = 2 * far * near * nf;
  return out;

