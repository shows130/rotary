import RPi.GPIO as GPIO

#클래스 Encoder를 정의 하는 코드
class Encoder:
    #클래스 초기상태 설정
    def __init__(self, leftPin, rightPin, callback=None):
        self.leftPin = leftPin
        self.rightPin = rightPin
        self.value = 0
        self.state = '00'
        self.direction = None
        self.callback = callback
        #칩셋 설정
        GPIO.setmode(GPIO.BCM)          #라즈베리파이 모드 설정
        GPIO.setup(self.leftPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)       #leftPin을 수신모드,  수신되지 않았을 때 off, 수신됐을 때 on
        GPIO.setup(self.rightPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)      #rightPin을 수신모드,  수신되지 않았을 때 off, 수신됐을 때 on
        GPIO.add_event_detect(self.leftPin, GPIO.BOTH,
                              callback=self.transitionOccurred)             #leftPin에 특정 엣지(0->1 or 1->0)가 일어났을 때 transitionOccurred라는 함수 실행
        GPIO.add_event_detect(self.rightPin, GPIO.BOTH,
                              callback=self.transitionOccurred)             #rightPin에 특정 엣지(0->1 or 1->0)가 일어났을 때 transitionOccurred라는 함수 실행

    def transitionOccurred(self, channel):
        p1 = GPIO.input(self.leftPin)           #leftpin에 input된 값을 p1에 저장
        p2 = GPIO.input(self.rightPin)          #rightpin에 input된 값을 p2에 저장
        newState = "{}{}".format(p1, p2)        #p1과 p2를 붙인 문자열 생성

        if self.state == "00":  # Resting position
            if newState == "01":  # Turned right 1
                self.direction = "R"
            elif newState == "10":  # Turned left 1
                self.direction = "L"

        elif self.state == "01":  # R1 or L3 position
            if newState == "11":  # Turned right 1
                self.direction = "R"
            elif newState == "00":  # Turned left 1
                if self.direction == "L":
                    self.value = self.value - 1
                    if self.callback is not None:
                        self.callback(self.value)

        elif self.state == "10":  # R3 or L1
            if newState == "11":  # Turned left 1
                self.direction = "L"
            elif newState == "00":  # Turned right 1
                if self.direction == "R":
                    self.value = self.value + 1
                    if self.callback is not None:
                        self.callback(self.value)

        else:  # self.state == "11"
            if newState == "01":  # Turned left 1
                self.direction = "L"
            elif newState == "10":  # Turned right 1
                self.direction = "R"
            elif newState == "00":  # Skipped an intermediate 01 or 10 state, but if we know direction then a turn is complete
                if self.direction == "L":
                    self.value = self.value - 1
                    if self.callback is not None:
                        self.callback(self.value)
                elif self.direction == "R":
                    self.value = self.value + 1
                    if self.callback is not None:
                        self.callback(self.value)

        self.state = newState

    def getValue(self):
        return self.value