import sys
sys.path.append('../')

from Servo import Servo
from time import sleep
from enum import Enum

class TestAction(Enum):
    Default = 1
    SetUp = 2
    SpinBackAndForth = 3
    FarLeft = 4
    FarRight = 5
    FullTest = 6

class TestServoSuite():
    def __init__(self, pin : int, test_action : TestAction):
        self.__test_action = test_action
        self.__servo = Servo(pin) ## Testing 

        if (test_action != TestAction.SetUp):    
            self.__servo.setup()
        
    def __test_spin(self):
        cycles = 4

        for x in range(cycles):
            # self.__servo.move(0)
            sleep(1)
            # self.__servo.move(100)
            sleep(1)

        return True, ""
    
    def __test_setup(self):
        try:
            self.__servo.setup()
        except Exception as e:
            return False, e
        finally:
            return True, ""

    def run_test(self):
        # Corrected indentation for the match statement
        if self.__test_action == TestAction.SpinBackAndForth:
            return self.__test_spin()
        elif self.__test_action == TestAction.SetUp:
            return self.__test_setup()

if (__name__ == "__main__"):
    
    test_suite = TestServoSuite(11, TestAction.SpinBackAndForth)
    success, reason = test_suite.run_test()

    if (success):
        print("Test has successfully executed with no errors")
    else:
        print("Test failed...")
        print(reason)