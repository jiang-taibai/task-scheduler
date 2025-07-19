import json
import time

from config import MAX_EMPTY_FETCHES, FETCH_INTERVAL
from dal.sqlite import TaskDB
from biz.handlers import HandlerFactory
from common.logger import get_logger

logger = get_logger(__name__)


class TaskScheduler:
    def __init__(self):
        self.db = TaskDB()
        self.empty_fetch_count = 0

    def run(self):
        logger.info("开始运行任务调度器...")
        while True:
            tasks = self.db.fetch_pending_tasks()
            if not tasks:
                self.empty_fetch_count += 1
                if self.empty_fetch_count >= MAX_EMPTY_FETCHES:
                    logger.info(f"超过 {self.empty_fetch_count} 次没有任务，停止调度器。")
                    break
                time.sleep(FETCH_INTERVAL)
                continue
            self.empty_fetch_count = 0
            for task in tasks:
                logger.info(f"开始运行 ID 为 {task['id']} 的任务，该任务类型为：({task['type']})")
                self.db.update_task_status_to_running(task['id'])
                try:
                    handler = HandlerFactory.get_handler(task['type'])
                    handler.execute(json.loads(task['value']))
                    self.db.update_task_status_to_done(task['id'])
                except Exception as e:
                    logger.warning(f"任务 ID {task['id']} 执行失败: {e}")
                    self.db.update_task_status_to_failed(task['id'])


if __name__ == '__main__':
    scheduler = TaskScheduler()
    scheduler.run()
