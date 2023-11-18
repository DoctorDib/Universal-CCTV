from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

class Servo():
    step = 1
    sleep_duration = .001
    
    current_position = 7.5
    percentage = .5

    __left = 180 # 12.5
    __right = -180 # 2.5

    def __init__(self, pin):
        self.pin = pin        
        self.percentage = self.__scale_percentage(50)

    def setup(self):
        myCorrection = .45
        maxPw = (2.0+myCorrection)/1000
        minPw = (1.0-myCorrection)/1000

        factory = PiGPIOFactory()

        self.servo = AngularServo(17, min_angle=-180, max_angle=180,min_pulse_width=minPw, max_pulse_width=maxPw, pin_factory=factory)

    def move(self, percentage):
        # Scaling the percentage to be between 0 and 1
        self.percentage = self.__scale_percentage(percentage)

        # Ensure percentage is between 0 and 1

        self.target = float(self.__interpolate_value(self.percentage))
        print(f"Moving to {self.target} using {self.percentage * 100}%")
        print(self.target)

        self.should_increment = self.target >= self.current_position

        while (self.__check_limit()):
            self.__increment_current_position()
            print(self.current_position)
            self.__move_servo(self.current_position)
            sleep(self.sleep_duration)

        self.servo.detach()

    def __move_servo(self, value):
        if (value > self.__left):
            print("SEtting left")
            value = self.__left
        elif (value < self.__right):
            print("SEtting left")
            value = self.__right

        print(f"Moving to {value}")
        self.servo.angle = value
        
        
    def __check_limit(self):
        if (self.should_increment):
            return self.current_position < self.target
        else:
            return self.current_position > self.target

    def __increment_current_position(self):
        pos = self.current_position

        if (self.should_increment):
            pos += self.step
        else:
            pos -= self.step

        self.current_position = pos

    def __scale_percentage(self, percentage):
        if (percentage > 1):
            return percentage / 100
        else:
            return percentage

    def __interpolate_value(self, percentage):
        if (percentage > 100):
            percentage = 100
        elif (percentage < 0):
            percentage = 0

        result = self.__left + (percentage * (self.__right - self.__left))

        return result