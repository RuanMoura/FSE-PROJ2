import RPi.GPIO as GPIO

class PWM_CLASS():
    def __init__(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(23, GPIO.OUT)
        GPIO.setup(24, GPIO.OUT)
        self.resistance = GPIO.PWM(23, 60)
        self.fan = GPIO.PWM(24, 60)

    def start(self) -> None:
        self.resistance.start(0)
        self.fan.start(0)

    def set_resistance(self, dc: int) -> None:
        print()
        print(f'R: {dc}')
        self.resistance.ChangeDutyCycle(dc)

    def set_fan(self, dc: int) -> None:
        print(f'F: {dc}')
        print()
        self.fan.ChangeDutyCycle(dc)

    def stop(self) -> None:
        self.resistance.stop()
        self.fan.stop()
