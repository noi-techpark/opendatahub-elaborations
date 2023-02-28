from calculateFreeParkingSlots import FreeParkingSlotsCalculator
import schedule
import time
import os

f = FreeParkingSlotsCalculator()

def main():
    seconds= int(os.getenv("JOB_SCHEDULE_SEC"))
    schedule.every(seconds).seconds.do(f.startCalculations)
    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
