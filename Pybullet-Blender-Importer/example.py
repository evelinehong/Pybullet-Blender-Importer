from pyBulletSimRecorder import PyBulletRecorder
import time
import pybullet as p
import numpy as np
import math
# Can alternatively pass in p.DIRECT 
client = p.connect(p.GUI)

cart = p.loadURDF("100502/mobility.urdf", [0,0,0.1], (0, 0, 0, 0.5), useFixedBase=1)

numJoints = p.getNumJoints(cart)
for j in range (numJoints):
  p.setJointMotorControl2(cart,j, p.VELOCITY_CONTROL,force=1)

# p.resetJointState(cart, 1, targetValue=1.0)

p.resetDebugVisualizerCamera(cameraDistance=3, cameraYaw=-60, cameraPitch=-15, cameraTargetPosition=[0,0,0])
recorder = PyBulletRecorder()

recorder.register_object(cart, "100502/mobility.urdf")

for t in range (500):
  p.resetJointState(cart, 1, 0.2 - 1.0 * t / 500)

  position, orientation = p.getBasePositionAndOrientation(cart)
  orientation = [orientation[0], orientation[1], orientation[2]-0.001, orientation[3]]
  position = [position[0] - 0.0005, position[1], position[2]]
  p.resetBasePositionAndOrientation(cart,  position, orientation)
  p.stepSimulation()
  time.sleep(1./300.)
  if t % 50 == 0:
    recorder.add_keyframe()

recorder.save('demo.pkl')