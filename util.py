import re
import subprocess


def devices():
    """
    获取已连接的adb设备。

    返回值:
        tuple: 包含三个元素的元组：
            - devices (dict): 正确连接的设备字典，键是设备代号，值是设备名称。
            - unauthorized_devices (list): 未授权调试的设备列表。
            - offline_devices (list): 离线设备列表。
    """
    devices = {}
    unauthorized_devices = []
    offline_devices = []

    # 执行adb devices命令获取设备列表
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    output = result.stdout

    # 解析adb devices命令的输出
    lines = output.strip().split('\n')
    for line in lines[1:]:  # 跳过第一行表头
        parts = line.split()
        if len(parts) == 2:
            device_id, status = parts
            if status == 'device':
                # 获取设备名称
                device_name_result = subprocess.run(
                    ['adb', '-s', device_id, 'shell', 'settings', 'get', 'global', 'device_name'], capture_output=True,
                    text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                device_name = device_name_result.stdout.strip()
                devices[device_id] = device_name
            elif status == 'unauthorized':
                unauthorized_devices.append(device_id)
            elif status == 'offline':
                offline_devices.append(device_id)

    return devices, unauthorized_devices, offline_devices


def get_display_ids(device_id=None):
    """
    获取设备的屏幕ID列表。

    参数:
        device_id (str, optional): 设备代号。如果为None，则使用当前连接的设备。默认为None。

    返回值:
        list: 包含设备屏幕ID的列表。

    异常:
        subprocess.CalledProcessError: 如果执行scrcpy --list-displays命令失败，则抛出该异常。
    """
    display_ids = []

    command = ['scrcpy', '--list-displays']
    if device_id:
        command.extend(['--serial', device_id])

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        output = result.stdout

        lines = output.strip().split('\n')
        for line in lines:
            if line.startswith('    --display-id='):
                display_id = int(line.split('=')[1].split()[0])
                display_ids.append(display_id)

    except subprocess.CalledProcessError as e:
        # print(f"执行scrcpy --list-displays命令失败: {e}")
        raise e

    return display_ids


def get_camera_sizes():
    """
    获取设备摄像头支持的分辨率和帧率。

    返回值:
        dict: 包含摄像头ID的字典,每个摄像头ID对应一个字典,
              该字典的键为分辨率,值为支持的帧率列表。
    """
    camera_sizes = {}

    result = subprocess.run(['scrcpy', '--list-camera-sizes'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    output = result.stdout

    current_camera_id = None
    high_speed_mode = False

    lines = output.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('--camera-id='):
            match = re.match(r'--camera-id=(\d+).*fps=\[(.*?)]', line)
            if match:
                current_camera_id = int(match.group(1))
                fps = match.group(2).split(', ')
                if current_camera_id not in camera_sizes:
                    camera_sizes[current_camera_id] = {}
                high_speed_mode = False
        elif line == 'High speed capture (--camera-high-speed):':
            high_speed_mode = True
        elif line.startswith('-'):
            resolution = line.lstrip('-').strip()
            if high_speed_mode:
                resolution_match = re.match(r'(.+?) \(fps=\[(.*?)]\)', resolution)
                if resolution_match:
                    resolution_base = resolution_match.group(1).strip()
                    high_speed_fps = resolution_match.group(2).split(', ')
                    if resolution_base in camera_sizes[current_camera_id]:
                        camera_sizes[current_camera_id][resolution_base + '[高速]'] = camera_sizes[current_camera_id].pop(resolution_base) + high_speed_fps
                    else:
                        camera_sizes[current_camera_id][resolution_base + '[高速]'] = high_speed_fps
            else:
                camera_sizes[current_camera_id][resolution] = fps

    return {cam_id: dict(reversed(list(resolutions.items()))) for cam_id, resolutions in camera_sizes.items()}



def time_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s


def convert_bitrate(bitrate_str):
    bitrate_str = bitrate_str.replace(' ', '')
    if bitrate_str.endswith('M'):
        bitrate = float(bitrate_str[:-1]) * 1000000
    elif bitrate_str.endswith('K'):
        bitrate = float(bitrate_str[:-1]) * 1000
    else:
        bitrate = float(bitrate_str)

    return int(bitrate)


def check_args(args):
    invalid_args = [arg for arg in args if arg.endswith('=')]
    return [arg for arg in args if arg not in invalid_args], invalid_args


if __name__ == '__main__':
    devices, unauthorized_devices, offline_devices = devices()
    print("已连接的设备:")
    for device_id, device_name in devices.items():
        print(f"{device_id}: {device_name}")
    print("未授权调试的设备:")
    for device_id in unauthorized_devices:
        print(device_id)
    print("离线设备:")
    for device_id in offline_devices:
        print(device_id)

    display_ids = get_display_ids()
    print("屏幕ID列表:")
    for display_id in display_ids:
        print(display_id)

    camera_sizes = get_camera_sizes()
    print(camera_sizes)
    # for camera_id, resolutions in camera_sizes.items():
    #     print(f"摄像头 ID: {camera_id}")
    #     for resolution, fps in resolutions.items():
    #         print(f"  分辨率: {resolution}, 支持帧率: {fps}")
