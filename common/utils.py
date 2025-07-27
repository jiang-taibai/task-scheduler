import os
import os.path as osp

_ROOT_PATH = osp.dirname(osp.dirname(osp.abspath(__file__)))


def root_path(relative_path: str = '') -> str:
    """
    获取项目根目录路径。
    :return: 项目根目录路径
    """
    if osp.isabs(relative_path):
        return osp.abspath(relative_path)
    abs_path = osp.join(_ROOT_PATH, relative_path)
    return osp.abspath(abs_path)


def make_sure_dir_exists(path: str) -> None:
    """
    确保目录存在，如果不存在则创建。
    可以传入相对目录路径、绝对目录路径、相对文件路径或绝对文件路径。
    :param path: 可选相对目录路径、绝对目录路径、相对文件路径或绝对文件路径
    :return:
    """
    # 如果路径有扩展名且其父目录存在，则认为是文件路径，获取其目录
    if osp.splitext(path)[1]:
        path = osp.dirname(path)

    # 如果是相对路径，转换为绝对路径
    if not osp.isabs(path):
        path = osp.join(root_path(), path)

    # 创建目录
    os.makedirs(path, exist_ok=True)


def get_absolute_path(path: str) -> str:
    """
    获取给定路径的绝对路径。
    如果路径是相对路径，则转换为绝对路径。
    :param path: 相对或绝对路径
    :return: 绝对路径
    """
    if not osp.isabs(path):
        path = osp.join(root_path(), path)
    return path


def get_filename_stem(path: str) -> str:
    """
    获取文件名的主干部分（不包含扩展名）。
    :param path: 文件路径
    :return: 文件名的主干部分
    """
    return osp.splitext(osp.basename(path))[0]


def get_timestamp() -> str:
    """
    获取当前时间戳，格式为 YYYYMMDD_HHMMSS。
    :return: 当前时间戳字符串
    """
    from datetime import datetime
    return datetime.now().strftime('%Y%m%d%H%M%S')
