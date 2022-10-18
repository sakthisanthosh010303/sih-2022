# Author: Sakthi Santhosh
# Created on: 28/08/2022
#
# Smart India Hackathon
def main() -> int:
    import RPi.GPIO as gpio
    from lib.process import run
    from time import sleep

    CHANNELS = (8, 10, 12, 16)

    gpio.setmode(gpio.BOARD)

    for channel in CHANNELS:
        gpio.setup(
            channel=channel,
            direction=gpio.IN,
            pull_up_down=gpio.PUD_UP
        )

    while True:
        try:
            for channel in CHANNELS:
                run(channel, gpio.input(channel))
                sleep(2)
        except KeyboardInterrupt:
            print("\rExit")
            break

    return 0

if __name__ == "__main__":
    exit(main())
