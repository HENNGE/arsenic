import sys

if sys.platform != "win32":

    def check_ie11_environment_cli():
        pass

    def configure_ie11_environment_cli():
        pass


else:
    import ctypes
    import winreg
    from collections import defaultdict
    from ctypes import wintypes

    KEYS = [
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_BFCACHE",
            "iexplore.exe",
            0,
            winreg.REG_DWORD,
        ),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Wow6432Node\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_BFCACHE",
            "iexplore.exe",
            0,
            winreg.REG_DWORD,
        ),
        (
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Internet Explorer\Zoom",
            "ZoomFactor",
            100_000,
            winreg.REG_DWORD,
        ),
    ]
    PROTECTION_MODES = [
        (
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings\Lockdown_Zones\0",
            "CurrentLevel",
            winreg.REG_DWORD,
        ),
        (
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings\Lockdown_Zones\1",
            "CurrentLevel",
            winreg.REG_DWORD,
        ),
        (
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings\Lockdown_Zones\2",
            "CurrentLevel",
            winreg.REG_DWORD,
        ),
        (
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings\Lockdown_Zones\3",
            "CurrentLevel",
            winreg.REG_DWORD,
        ),
        (
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings\Lockdown_Zones\4",
            "CurrentLevel",
            winreg.REG_DWORD,
        ),
    ]

    KEY_NAMES = {
        value: key for key, value in vars(winreg).items() if key.startswith("HKEY_")
    }

    TYPE_NAMES = {
        value: key for key, value in vars(winreg).items() if key.startswith("REG_")
    }

    def detect_dpi_setting():
        ctypes.windll.shcore.SetProcessDpiAwareness(2)

        ok = []

        def cb(monitor, dc, rect, data):
            x = wintypes.UINT()
            y = wintypes.UINT()
            ctypes.windll.shcore.GetDpiForMonitor(
                monitor, 0, ctypes.pointer(x), ctypes.pointer(y)
            )
            if (x.value, y.value) != (96, 96):
                print("DPI Scaling does not seem to be set to 100%")
                ok.append(False)
            else:
                ok.append(True)
            return 0

        ctypes.windll.user32.EnumDisplayMonitors(
            0,
            0,
            ctypes.WINFUNCTYPE(
                ctypes.c_uint,
                ctypes.c_ulong,
                ctypes.c_ulong,
                ctypes.POINTER(wintypes.RECT),
                ctypes.c_double,
            )(cb),
            0,
        )
        if not ok:
            print("No Monitors found")
        return ok and all(ok)

    def check_ie11_environment():
        ok = True
        for key, subkey, attribute, value, value_type in KEYS:
            path = f"{KEY_NAMES[key]}\\{subkey}"
            try:
                with winreg.OpenKey(key, subkey) as regkey:
                    try:
                        actual_value, actual_type = winreg.QueryValueEx(
                            regkey, attribute
                        )
                    except OSError:
                        ok = False
                        print(f"Key {path} has no attribute {attribute}")
                    else:
                        if actual_value != value:
                            ok = False
                            print(
                                f"Key {path}\\{attribute} has value {actual_value}, expected {value}"
                            )
                        if actual_type != value_type:
                            ok = False
                            print(
                                f"Key {path}\\{attribute} has value type {TYPE_NAMES[actual_type]}, expected {TYPE_NAMES[value_type]}"
                            )
            except OSError:
                ok = False
                print(f"Key {path} does not exist!")
        modes = defaultdict(list)
        for key, subkey, attribute, value_type in PROTECTION_MODES:
            path = f"{KEY_NAMES[key]}\\{subkey}"
            try:
                with winreg.OpenKey(key, subkey) as regkey:
                    try:
                        actual_value, actual_type = winreg.QueryValueEx(
                            regkey, attribute
                        )
                    except OSError:
                        ok = False
                        print(f"Key {path} has no attribute {attribute}")
                    else:
                        modes[actual_value].append(path)
                        if actual_type != value_type:
                            ok = False
                            print(
                                f"Key {path}\\{attribute} has value type {TYPE_NAMES[actual_type]}, expected {TYPE_NAMES[value_type]}"
                            )
            except OSError:
                ok = False
                print(f"Key {path} does not exist!")
        if len(modes) > 1:
            print("Not all zones have same protected mode setting:")
            for value, zones in modes.items():
                print(f'{", ".join(zones)} have value {value}')
        ok = ok and detect_dpi_setting()
        if ok:
            print("Environment looks okay")
        return ok

    def check_ie11_environment_cli():
        if not check_ie11_environment():
            sys.exit(-1)

    def configure_ie11_environment(protected_mode):
        for key, subkey, attribute, value, value_type in KEYS:
            try:
                regkey = winreg.OpenKey(key, subkey, access=winreg.KEY_SET_VALUE)
            except OSError:
                regkey = winreg.CreateKey(key, subkey)
            try:
                winreg.SetValueEx(regkey, attribute, 0, value_type, value)

            finally:
                winreg.CloseKey(regkey)
        for key, subkey, attribute, value_type in PROTECTION_MODES:
            try:
                regkey = winreg.OpenKey(key, subkey, access=winreg.KEY_SET_VALUE)
            except OSError:
                regkey = winreg.CreateKey(key, subkey)
            try:
                winreg.SetValueEx(regkey, attribute, 0, value_type, protected_mode)
            finally:
                winreg.CloseKey(regkey)

    def configure_ie11_environment_cli():
        configure_ie11_environment(0)
