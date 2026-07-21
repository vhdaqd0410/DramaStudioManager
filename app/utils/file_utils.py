import os
import re
import subprocess
import sys


def open_in_explorer(path: str):
    """在文件资源管理器中打开路径"""
    if not path or not os.path.exists(path):
        return False
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False


def validate_path(path: str) -> bool:
    """检查路径是否存在"""
    return bool(path and os.path.exists(path))


def parse_project_name(dir_name: str) -> dict | None:
    """
    从文件夹名解析项目编号和名称。
    规则：找到最后一个连续的 4 位数字作为项目编号，
          编号之后的内容作为项目名称。
    例：
      'H0123-8948 《换面复仇》' → no='8948', name='《换面复仇》'
      '393-8935-（海外）《八零甜妻灿若明野》' → no='8935', name='（海外）《八零甜妻灿若明野》'
    """
    if not dir_name:
        return None
    # 找所有 4 位数字及其位置
    matches = list(re.finditer(r'\d{4}', dir_name))
    if not matches:
        return None
    # 取最后一个
    last = matches[-1]
    project_no = last.group()
    # 编号之后的部分
    suffix = dir_name[last.end():]
    # 去掉前导分隔符和空格
    suffix = suffix.lstrip(' -—–_《》「」\t')
    return {"project_no": project_no, "name": suffix}
