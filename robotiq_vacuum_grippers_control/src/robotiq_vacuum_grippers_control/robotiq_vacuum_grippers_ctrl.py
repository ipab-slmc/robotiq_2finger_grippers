#!/usr/bin/env python

from robotiq_vacuum_grippers_control.msg import RobotiqVacuumGrippers_robot_input as inputMsg
from robotiq_vacuum_grippers_control.msg import RobotiqVacuumGrippers_robot_output as outputMsg
import rospy
import numpy as np

import roslib
roslib.load_manifest('robotiq_vacuum_grippers_control')


class RobotiqVGripper(object):
    def __init__(self):
        self.cur_status = None
        self.status_sub = rospy.Subscriber('RobotiqVacuumGrippersRobotInput', inputMsg,
                                           self._status_cb)
        self.cmd_pub = rospy.Publisher(
            'RobotiqVacuumGrippersRobotOutput', outputMsg)

    def _status_cb(self, msg):
        self.cur_status = msg

    def wait_for_connection(self, timeout=-1):
        rospy.sleep(0.1)
        r = rospy.Rate(30)
        start_time = rospy.get_time()
        while not rospy.is_shutdown():
            if (timeout >= 0. and rospy.get_time() - start_time > timeout):
                return False
            if self.cur_status is not None:
                return True
            r.sleep()
        return False

    def is_ready(self):
        return self.cur_status.gSTA == 3 and self.cur_status.gACT == 1

    def is_reset(self):
        return self.cur_status.gSTA == 0 or self.cur_status.gACT == 0

    def is_moving(self):
        return self.cur_status.gGTO == 1 and self.cur_status.gOBJ == 0

    def is_stopped(self):
        return self.cur_status.gOBJ != 0

    def object_detected(self):
        return self.cur_status.gOBJ == 1 or self.cur_status.gOBJ == 2

    def get_fault_status(self):
        return self.cur_status.gFLT

    def get_pos(self):
        po = self.cur_status.gPO
        return np.clip(0.087/(13.-230.)*(po-230.), 0, 0.087)

    def get_req_pos(self):
        pr = self.cur_status.gPR
        return np.clip(0.087/(13.-230.)*(pr-230.), 0, 0.087)

    def is_closed(self):
        return self.cur_status.gPO >= 230

    def is_opened(self):
        return self.cur_status.gPO <= 13

    # if timeout is negative, wait forever

    def wait_until_stopped(self, timeout=-1):
        r = rospy.Rate(30)
        start_time = rospy.get_time()
        while not rospy.is_shutdown():
            if (timeout >= 0. and rospy.get_time() - start_time > timeout) or self.is_reset():
                return False
            if self.is_stopped():
                return True
            r.sleep()
        return False

    def wait_until_moving(self, timeout=-1):
        r = rospy.Rate(30)
        start_time = rospy.get_time()
        while not rospy.is_shutdown():
            if (timeout >= 0. and rospy.get_time() - start_time > timeout) or self.is_reset():
                return False
            if not self.is_stopped():
                return True
            r.sleep()
        return False

    def reset(self):
        cmd = outputMsg()
        cmd.rACT = 0
        self.cmd_pub.publish(cmd)

    def activate(self, timeout=-1):
        cmd = outputMsg()
        cmd.rACT = 1
        cmd.rMOD = 0
        cmd.rGTO = 1
        cmd.rPR = 0
        cmd.rSP = 150
        cmd.rFR = 50
        self.cmd_pub.publish(cmd)
        r = rospy.Rate(30)
        start_time = rospy.get_time()
        while not rospy.is_shutdown():
            if timeout >= 0. and rospy.get_time() - start_time > timeout:
                return False
            if self.is_ready():
                return True
            r.sleep()
        return False

    def auto_release(self):
        cmd = outputMsg()
        cmd.rACT = 1
        cmd.rATR = 1
        self.cmd_pub.publish(cmd)

    ##
    # Actuate
    # @param press is the Gripper max relative pressure level request [0, 0.087]
    # @param rdel is the Gripper timeout / release delay [0.013, 0.100]
    # @param mrprl is the Gripper minimum relative pressure level request [30, 100]
    def goto(self, press, rdel, mrprl, block=False, timeout=-1):
        cmd = outputMsg()
        cmd.rACT = 1
        cmd.rGTO = 1
        cmd.rPR = int(np.clip((13.-230.)/0.087 * press + 230., 0, 255))
        cmd.rSP = int(np.clip(255./(0.1-0.013) * (rdel-0.013), 0, 255))
        cmd.rFR = int(np.clip(255./(100.-30.) * (mrprl-30.), 0, 255))
        self.cmd_pub.publish(cmd)
        rospy.sleep(0.1)
        if block:
            if not self.wait_until_moving(timeout):
                return False
            return self.wait_until_stopped(timeout)
        return True

    def stop(self, block=False, timeout=-1):
        cmd = outputMsg()
        cmd.rACT = 1
        cmd.rGTO = 0
        self.cmd_pub.publish(cmd)
        rospy.sleep(0.1)
        if block:
            return self.wait_until_stopped(timeout)
        return True

    def open(self, rdel=0.1, mrprl=100, block=False, timeout=-1):
        if self.is_opened():
            return True
        return self.goto(1.0, rdel, mrprl, block=block, timeout=timeout)

    def close(self, rdel=0.1, mrprl=100, block=False, timeout=-1):
        if self.is_closed():
            return True
        return self.goto(-1.0, rdel, mrprl, block=block, timeout=timeout)


def main():
    rospy.init_node("robotiq_vacuum_grippers_ctrl_test")
    gripper = RobotiqVGripper()
    gripper.wait_for_connection()
    if gripper.is_reset():
        gripper.reset()
        gripper.activate()
    print(gripper.close(block=True))
    while not rospy.is_shutdown():
        print(gripper.open(block=False))
        rospy.sleep(0.11)
        gripper.stop()
        print(gripper.close(block=False))
        rospy.sleep(0.1)
        gripper.stop()


if __name__ == '__main__':
    main()
