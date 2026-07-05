"""Report CPU, battery and RAM status using psutil.

Works on Windows, Linux and macOS. Battery reporting degrades gracefully on
machines without a battery (e.g. desktops and servers, where
``sensors_battery`` returns ``None``).
"""


def _psutil():
    try:
        import psutil
        return psutil
    except ImportError:
        print("[check_hardware] psutil not installed")
        return None


def getcpuper(percpu=False):
    """Return a string describing CPU usage."""
    psutil = _psutil()
    if psutil is None:
        return "CPU information is unavailable."

    if percpu:
        cpu_say = "The usages of cpu cores are "
        for x in psutil.cpu_percent(interval=1, percpu=True):
            cpu_say += str(x) + ", "
        cpu_say += "percent respectively"
    else:
        cpu_say = "CPU usage is " + str(psutil.cpu_percent(interval=1)) + " percent"
    print(cpu_say)
    return cpu_say


def getbattery():
    """Return a string describing battery status."""
    psutil = _psutil()
    if psutil is None:
        return "Battery information is unavailable."

    battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
    if battery is None:
        battery_say = "No battery detected on this system."
        print(battery_say)
        return battery_say

    battery_say = str(battery.percent) + " percent power left. "
    if battery.percent < 30 and (not battery.power_plugged):
        battery_say += (
            "running on emergency backup power. approximately "
            + str(int(battery.secsleft / 60))
            + " minutes remaining."
        )
    elif not battery.power_plugged:
        battery_say += " approximately " + str(int(battery.secsleft / 60)) + " minutes remaining."
    else:
        battery_say += "plugged in, charging"
    print(battery_say)
    return battery_say


def getram():
    """Return a string describing RAM usage."""
    psutil = _psutil()
    if psutil is None:
        return "Memory information is unavailable."

    ram_say = "System memory usage is "
    memory = psutil.virtual_memory()
    ram_say += str(memory.percent) + " percent."
    if memory.percent > 85:
        ram_say += " System overload detected."
    else:
        ram_say += " No overload detected"
    print(ram_say)
    return ram_say
