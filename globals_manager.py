# globals_manager.py
new_thread_ts_briefing = None

def test_set_thread_ts(value):
    global new_thread_ts_briefing
    new_thread_ts_briefing = value
    print(f"Thread TS set to: {new_thread_ts_briefing}")

def test_get_thread_ts():
    global new_thread_ts_briefing
    print(f"Current Thread TS: {new_thread_ts_briefing}")
    return new_thread_ts_briefing
