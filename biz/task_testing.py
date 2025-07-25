# -*- coding: utf-8 -*-
# @Time    : 2025-07-21 22:13
# @Author  : Jiang Liu
import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from subprocess import TimeoutExpired

from biz.handlers import HandlerFactory
from dal.sqlite import TaskDB
from common.logger import get_logger

logger = get_logger(__name__)


def test_task(task_id: int, running_second: int) -> bool:
    """
    测试任务可行性：是否能够在 running_second 秒内不报错运行
    :param task_id: 任务 ID
    :param running_second:  运行时间，单位为秒
    :return: 任务是否可行
    """
    db = TaskDB()
    task = db.query_task_by_id(task_id)
    db.update_task_status_to_testing(task_id)
    logger.info(f"开始测试运行 ID 为 {task['id']} 的任务，该任务类型为：({task['type']})")
    try:
        handler = HandlerFactory.get_handler(task['type'])
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(handler.execute, json.loads(task['value']), timeout=running_second)
            future.result(timeout=running_second)
    except (TimeoutExpired, TimeoutError):
        db.update_task_status_to_test_success(task_id)
        logger.info(f"任务 ID {task['id']} 在 {running_second} 秒内未报错，判定为可行")
        return True
    except Exception as e:
        db.update_task_status_to_test_failed(task_id)
        logger.error(f"任务 ID {task['id']} 执行失败: {e}")
        return False
    db.update_task_status_to_test_success(task_id)
    return True


def main():
    # 样例
    task_ids = [1]
    running_second = 10
    for task_id in task_ids:
        if test_task(task_id, running_second):
            print(f"任务 ID {task_id} 可行")
        else:
            print(f"任务 ID {task_id} 不可行")


if __name__ == '__main__':
    main()
