# Author: Sakthi Santhosh
# Created on: 27/08/2022
#
# Smart India Hackathon
def main() -> int:
    import RPi.GPIO as gpio
    from lib.process import run

    gpio.setmode(gpio.BOARD)

    gpio.setup(
        channel=16,
        direction=gpio.IN,
        pull_up_down=gpio.PUD_UP,
    )
    gpio.add_event_detect(
        gpio=16,
        edge=gpio.RISING,
        callback=run,
        bouncetime=20000
    )

    while True:
        try:
            pass
        except KeyboardInterrupt:
            print("\rExit")
            break
    return 0

if __name__ == "__main__":
    main()
