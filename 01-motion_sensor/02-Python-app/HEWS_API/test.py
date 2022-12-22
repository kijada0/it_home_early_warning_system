import time
from datetime import datetime

time_now = datetime.now()
previous_time = time_now
time.sleep(5)

while(True):
    time_now = datetime.now()
    print((previous_time - time_now).total_seconds() *(-1))

    if (time_now - previous_time).total_seconds() > 1:
        print("\t\tTime loop")
        previous_time = datetime.now()

    time.sleep(0.1)