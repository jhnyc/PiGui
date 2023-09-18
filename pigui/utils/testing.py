import time


def measure_event_time(event_func):
    """Function to measure event time to determine the right debounce time for an event.
    For example, Joystick `Up` is about 0.12s, so an ideal threshold could be 0.1s.
    """
    started = False
    start_time = None
    while True:
        if not started and event_func():
            started = True
            start_time = time.time()
        if started and not event_func():
            end_time = time.time()
            reaction_time = end_time - start_time
            print(reaction_time)
            return reaction_time
