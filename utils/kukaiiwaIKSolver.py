import os
import sys
sys.path.append(os.getcwd())


import numpy as np
from utils.debug import *
from utils.mathHelper import deg2Rad, rad2Deg


def Configuration(rconf):
    arm = 1
    elbow = 1
    wrist = 1

    if rconf & 1:
        arm = -1

    if rconf & 2:
        elbow = -1

    if rconf & 4:
        wrist = -1

    return arm, elbow, wrist

def ForwardKinematics(joints):
    # Tolerance
    tol = 1e-8

    # Robot parameters
    # Link length
    l = np.array([0.36, 0.42, 0.4, 0.15194])

    # Denavit-Hartenberg parameters 7 DoF
    # DH: [a, alpha, d, theta]
    dh = np.array([[0, -np.pi/2, 0.36   , 0],
                   [0, np.pi/2 , 0      , 0],
                   [0, np.pi/2 , 0.42   , 0],
                   [0, -np.pi/2, 0      , 0],
                   [0, -np.pi/2, 0.4    , 0],
                   [0, np.pi/2 , 0      , 0],
                   [0, 0       , 0.15194, 0]])

    # Number of joints
    nj = dh.shape[0]

    # Robot configuration
    rconf = (joints[1] < 0) + 2 * (joints[3] < 0) + 4 * (joints[5] < 0)

    arm, elbow, wrist = Configuration(rconf)

    # Assign joint values to the theta column of the DH parameters
    dh[:, 3] = joints

    # Store transformations from the base reference frame to the index joint
    tr = np.zeros((4, 4, nj))

    for i in range(nj):
        a, alpha, d, theta = dh[i]
        v = np.array([a * np.cos(theta), a * np.sin(theta), d])
        Xx, Yx, Zx = np.cos(theta),-np.sin(theta) * np.cos(alpha), np.sin(theta) * np.sin(alpha)
        Xy, Yy, Zy = np.sin(theta), np.cos(theta) * np.cos(alpha),-np.cos(theta) * np.sin(alpha)
        Xz, Yz, Zz = 0            , np.sin(alpha)                , np.cos(alpha)
        tmp = np.array([[Xx, Yx, Zx, v[0]],
                        [Xy, Yy, Zy, v[1]],
                        [Xz, Yz, Zz, v[2]],
                        [0 , 0 , 0 , 1   ]])
        if i == 0:
            tr[:, :, 0] = tmp
        else:
            tr[:, :, i] = np.matmul(tr[:, :, i - 1], tmp)

    xs = tr[:3, 3, 0]  # shoulder position from base
    xe = tr[:3, 3, 3]  # elbow position from base
    xw = tr[:3, 3, 5]  # wrist position from base
    xsw = xw - xs  # wrist position from shoulder
    pose = tr[:, :, -1]  # end-effector transformation from base

    # Calculate the nsparam - Arm Angle
    vv, _, jout = ReferencePlane(pose, elbow)

    # vv is the vector normal to the reference plane: xs-xe0-xw
    # vc is the vector normal to the current plane:   xs-xe-xw
    v1 = unit(xe - xs)
    v2 = unit(xw - xs)
    vc = np.cross(v1, v2)

    cos_ns = np.dot(unit(vv), unit(vc))
    if abs(np.linalg.norm(cos_ns)) > 1:
        cos_ns = np.sign(cos_ns)

    # this vector will give the sign of the nsparam
    v3 = np.cross(unit(vv), unit(vc))

    if np.linalg.norm(v3) > tol:
        nsparam = np.sign(np.dot(v3, xsw)) * np.arccos(cos_ns)
    else:
        if np.linalg.norm(vv - vc) < tol:
            nsparam = 0
        else:
            nsparam = np.pi

    return pose, nsparam, rconf, jout

def InverseKinematics(pose, nsparam, rconf):
    arm, elbow, wrist = Configuration(rconf)

    # Tolerance
    tol = 1e-8

    # Robot parameters
    # Link length
    l = np.array([0.36, 0.42, 0.4, 0.15194])

    # Denavit-Hartenberg parameters 7 DoF
    # DH: [a, alpha, d, theta]
    dh = np.array([[0, -np.pi/2, 0.36   , 0],
                   [0, np.pi/2 , 0      , 0],
                   [0, np.pi/2 , 0.42   , 0],
                   [0, -np.pi/2, 0      , 0],
                   [0, -np.pi/2, 0.4    , 0],
                   [0, np.pi/2 , 0      , 0],
                   [0, 0       , 0.15194, 0]])

    # Number of joints
    nj = dh.shape[0]

    # Joint values of virtual manipulator
    joints = np.zeros(7)

    # Shoulder rotation matrices
    s_mat = np.zeros((3, 3, 3))

    # Wrist rotation matrices
    w_mat = np.zeros((3, 3, 3))

    xend = pose[:3, 3]  # end-effector position from base
    xs = np.array([0, 0, dh[0, 2]])  # shoulder position from base
    xwt = np.array([0, 0, dh[-1, 2]])  # end-effector position from wrist
    xw = xend - np.dot(pose[:3, :3], xwt)  # wrist position from base
    xsw = xw - xs  # shoulder to wrist vector
    usw = unit(xsw)

    lbs = l[0]
    lse = l[1]  # upper arm length (shoulder to elbow)
    lew = l[2]  # lower arm length (elbow to wrist)

    # Check if pose is within arm+forearm reach
    assert np.linalg.norm(xsw) < lse + lew and np.linalg.norm(xsw) > lse - lew, 'Specified pose outside reachable workspace'

    # -- Joint 4 --
    # Elbow joint can be directly calculated since it does only depend on the
    # robot configuration and the xsw vector
    assert abs((np.linalg.norm(xsw)**2 - lse**2 - lew**2) - (2*lse*lew)) > tol, 'Elbow singularity. Tip at reach limit.'
    # Cosine law - According to our robot, joint 4 rotates backwards
    joints[3] = elbow * np.arccos((np.linalg.norm(xsw)**2 - lse**2 - lew**2) / (2*lse*lew))

    # Added
    T34 = dh_calc(dh[3, 0], dh[3, 1], dh[3, 2], joints[3])
    R34 = T34[:3, :3]

    # Shoulder Joints
    # First compute the reference joint angles when the arm angle is zero.
    _, R03_o, _ = ReferencePlane(pose, elbow)

    skew_usw = skew(usw)
    # Following eq. (15), the auxiliary matrices As Bs and Cs can be calculated
    # by substituting eq. (6) into (9).
    # R0psi = I3 + sin(psi)*skew_usw + (1-cos(psi))*skew_usw²    (6)
    # R03 = R0psi * R03_o                                         (9)
    # Substituting (distributive prop.) we get:
    # R03 = R03_o*skew_usw*sin(psi) + R03_o*(-skew_usw²)*cos(psi) + R03_o(I3 + skew_usw²)
    # R03 =      As       *sin(psi) +        Bs         *cos(psi) +          Cs

    As = skew_usw @ R03_o
    Bs = -(skew_usw @ skew_usw) @ R03_o
    Cs = np.outer(usw, usw) @ R03_o

    psi = nsparam
    R03 = As * np.sin(psi) + Bs * np.cos(psi) + Cs

    # T03 transformation matrix (DH parameters)
    joints[0] = np.arctan2(arm * R03[1, 1], arm * R03[0, 1])
    joints[1] = arm * np.arccos(R03[2, 1])
    joints[2] = np.arctan2(arm * -R03[2, 2], arm * -R03[2, 0])

    Aw = R34.T @ As.T @ pose[:3, :3]
    Bw = R34.T @ Bs.T @ pose[:3, :3]
    Cw = R34.T @ Cs.T @ pose[:3, :3]

    R47 = Aw * np.sin(psi) + Bw * np.cos(psi) + Cw

    # T47 transformation matrix (DH parameters)
    joints[4] = np.arctan2(wrist * R47[1, 2], wrist * R47[0, 2])
    joints[5] = wrist * np.arccos(R47[2, 2])
    joints[6] = np.arctan2(wrist * R47[2, 1], wrist * -R47[2, 0])

    # Grouping Shoulder and Wrist matrices that will be used by the joint
    # limit algorithms
    s_mat[:, :, 0] = As
    s_mat[:, :, 1] = Bs
    s_mat[:, :, 2] = Cs
    w_mat[:, :, 0] = Aw
    w_mat[:, :, 1] = Bw
    w_mat[:, :, 2] = Cw

    return joints, s_mat, w_mat

def ReferencePlane(pose, elbow):
    # Calculations tolerance
    tol = 1e-6

   
    # Robot parameters
    # Link length
    l = np.array([0.36, 0.42, 0.4, 0.15194])

    # Denavit-Hartenberg parameters 7 DoF
    # DH: [a, alpha, d, theta]
    dh = np.array([[0, -np.pi/2, 0.36   , 0],
                   [0, np.pi/2 , 0      , 0],
                   [0, np.pi/2 , 0.42   , 0],
                   [0, -np.pi/2, 0      , 0],
                   [0, -np.pi/2, 0.4    , 0],
                   [0, np.pi/2 , 0      , 0],
                   [0, 0       , 0.15194, 0]])
                
    joints = np.zeros(7)

    xend = pose[:3, 3]
    xs0 = np.array([0, 0, dh[0, 2]])
    xwt = np.array([0, 0, dh[-1, 2]])
    xw0 = xend - np.matmul(pose[:3, :3], xwt)
    xsw = xw0 - xs0

    lbs = l[0]
    lse = l[1]
    lew = l[2]

    assert np.linalg.norm(xsw) < lse + lew and np.linalg.norm(xsw) > lse - lew, 'Specified pose outside reachable workspace'

    # -- Joint 4 --
    assert np.abs((np.linalg.norm(xsw)**2 - lse**2 - lew**2) - (2*lse*lew)) > tol, 'Elbow singularity. Tip at reach limit.'
    joints[3] = elbow * np.arccos((np.linalg.norm(xsw)**2 - lse**2 - lew**2) / (2*lse*lew))

    # Shoulder Joints
    T34 = dh_calc(dh[3, 0], dh[3, 1], dh[3, 2], joints[3])
    R34 = T34[:3, :3]

    xse = np.array([0, lse, 0])
    xew = np.array([0, 0, lew])

    m = xse + np.matmul(R34, xew)

    # -- Joint 1 --
    if np.linalg.norm(np.cross(xsw, np.array([0, 0, 1]))) > tol:
        joints[0] = np.arctan2(xsw[1], xsw[0]) # ::neg x?
    else:
        joints[0] = 0

    # -- Joint 2 --
    r = np.hypot(xsw[0], xsw[1])
    dsw = np.linalg.norm(xsw)
    phi = np.arccos((lse**2 + dsw**2 - lew**2) / (2*lse*dsw))

    joints[1] = np.arctan2(r, xsw[2]) + elbow * phi # ::neg r?

    # Lower arm transformation
    T01 = dh_calc(dh[0, 0], dh[0, 1], dh[0, 2], joints[0])
    T12 = dh_calc(dh[1, 0], dh[1, 1], dh[1, 2], joints[1])
    T23 = dh_calc(dh[2, 0], dh[2, 1], dh[2, 2], 0)
    T34 = dh_calc(dh[3, 0], dh[3, 1], dh[3, 2], joints[3])
    T04 = T01 @ T12 @ T23 @ T34

    rot_base_elbow = T01[:3, :3] @ T12[:3, :3] @ T23[:3, :3]

    x0e = T04[:3, 3]

    v1 = unit(x0e - xs0)
    v2 = unit(xw0 - xs0)

    ref_plan_vector = np.cross(v1, v2)

    return ref_plan_vector, rot_base_elbow, joints

def dh_calc(a, alpha, d, theta):
    T = np.array([[np.cos(theta), -np.sin(theta) * np.cos(alpha), np.sin(theta) * np.sin(alpha) , a * np.cos(theta)],
                  [np.sin(theta), np.cos(theta) * np.cos(alpha) , -np.cos(theta) * np.sin(alpha), a * np.sin(theta)],
                  [0.0          , np.sin(alpha)                 , np.cos(alpha)                 , d                ],
                  [0.0          , 0.0                           , 0.0                           , 1.0              ]])

    return T

def skew(v):
    m = np.array([[ 0   ,-v[2], v[1]],
                  [ v[2], 0   ,-v[0]],
                  [-v[1], v[0], 0   ]])

    return m

def unit(v):
    n = np.linalg.norm(v)
    if n < np.finfo(float).eps:
        raise ValueError('RTB:unit:zero_norm', 'Vector has zero norm')

    u = v / n
    return u

if __name__ == '__main__':
    """
    real xyz abc
    [-699.05, -14.29, 1264.87]
    [-1.54, -0.002, 0.59]
    """

    # joints = [0.4145, -16.2216, 0.9526, 48.1185, -0.6516, 30.3565, -80.1974]
    joints = [90, 30, 0, 90, 0, -90, 0]
    # joints = [45, 45, 45, 45, 45, 45, 45]
    joints = list(map(deg2Rad, joints))
    print(joints)
    print('--------------'*10)

    pose, nsparam, rconf, jout = ForwardKinematics(joints)
    print(pose)
    # print(list(map(rad2Deg, jout)))
    # print(nsparam)
    joints, s_mat, w_mat = InverseKinematics(pose, nsparam, rconf)

    print('--------------'*10)
    print(joints)
    # print(list(map(rad2Deg, joints)))














