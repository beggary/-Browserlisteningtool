import subprocess

def adb_forward(_port_number: str = None):
    try:
        port_number = _port_number
        subprocess.run(
            ['adb', 'forward', '--remove-all'],
            capture_output=True,
            text=True,
            check=True
        )
        result = subprocess.run(
            ['adb', 'forward','tcp:9222','localabstract:chrome_devtools_remote'],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout
        lines = output.strip().split('\n')
        so = int(lines[0])
        # print(type(so))
        if so == 9222:
            return True
        else:
            return False
    except Exception as error:
        print(f"确认手机是否连接…… USB调试状态是否开启…… {error}")

# if __name__ == "__main__":
#     devices = adb_forward()
#     print(devices)

