from common.utils import root_path

# 数据库文件
DB_PATH = root_path('./data/task.sqlite')
# 间隔多少秒尝试获取一次任务
FETCH_INTERVAL = 5
# 超过多少次没有任务则停止调度器
MAX_EMPTY_FETCHES = 5
# 日志根目录
LOG_ROOT = root_path('./logs')
