import os
import json
from datetime import datetime
from collections import defaultdict


def read_build_status(build_marker_path):
    """读取标记文件，返回构建状态的字典"""
    build_marker_path = os.path.join(build_marker_path, "build.json")
    if os.path.exists(build_marker_path):
        with open(build_marker_path, "r") as f:
            return json.load(f)

    with open(build_marker_path, "w") as f:
        json.dump({}, f, indent=4)

    return {}


def write_build_status(build_marker_path, status_dict):
    """写入构建状态到标记文件"""
    build_marker_path = os.path.join(build_marker_path, "build.json")
    with open(build_marker_path, "w") as f:
        json.dump(status_dict, f, indent=4)


def check_build_status(build_marker_path, domain, component):
    """检查指定组件的构建状态

    Args:
        build_marker_path (str): 构建状态标记文件路径
        component (str): 组件名称

    Returns:
        bool: 如果组件已经构建完成，返回 False 否则返回 True
    """
    build_status = read_build_status(build_marker_path)
    if domain not in build_status:
        build_status.update(
            {domain: {component: {"status": "incomplete", "time": None}}}
        )
        write_build_status(build_marker_path, build_status)
        return True
    
    domain_status = build_status.get(domain, {})
    component_status = domain_status.get(component, {})

    time = component_status.get("time")
    if component_status.get("status") == "complete":
        return False
    return True


def update_build_status(build_marker_path, domain, component):
    """更新指定组件的构建状态为已完成

    Args:
        build_marker_path (str): 构建状态标记文件路径
        component (str): 组件名称
    """
    build_status = read_build_status(build_marker_path)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if domain not in build_status:
        build_status.update({domain: {component: {"status": "complete", "time": time}}})
    else:
        build_status[domain].update({component: {"status": "complete", "time": time}})
    print(f"domain: {domain} ||| {component} ||| at {time}.")
    write_build_status(build_marker_path, build_status)


def reset_build_status(build_marker_path, domain, component):
    """重置构建component状态"""
    build_status = read_build_status(build_marker_path)
    build_status[domain].update({component: {"status": "incomplete", "time": None}})
    write_build_status(build_marker_path, build_status)