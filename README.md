# Task Scheduler

## 1 背景

由于最近需要频繁地运行一些脚本，所以我写了一个轻量化的任务调度器：

- 高扩展性：支持自定义任务的具体执行逻辑
- 动态性：支持动态添加和删除任务
- 日志记录：支持实时日志记录
- 轻量持久化：支持任务的持久化，使用 SQLite 数据库无需额外的数据库服务

## 2 快速开始

### 2.1 创建项目

```bash
git clone https://github.com/jiang-taibai/task-scheduler.git --depth 1
cd task-scheduler
```

### 2.2 自定义任务

biz/handlers.py 提供了统一的任务处理框架：

* 定义了抽象基类 BaseHandler，要求子类实现 execute 和 add_task 方法。
* 通过装饰器 @register_handler 将子类自动注册到 HANDLER_REGISTRY 中。
* 通过 HandlerFactory.get_handler(type_name) 按名称获取对应的处理器实例。

约定：

* 每个 Handler 都必须继承 BaseHandler。
* 必须在类属性 type_name 中指定唯一的类型名，用于注册和查找。
* 实现 execute(self, value: Dict[str, Any], **kwargs) ：从 value 中读取参数并执行业务逻辑。value 等于 add_task 方法的 value 参数。
* 实现 add_task(self, ...) ：将任务写入数据库（通过 self.db.add_task(type_name, json.dumps(task_value))）。
* 在定义类的最外层使用 @register_handler 装饰，以完成自动注册。

示例：

```python
from typing import Dict, Any
from biz.handlers import BaseHandler, register_handler

@register_handler
class EchoHandler(BaseHandler):
    type_name = "echo"

    def execute(self, value: Dict[str, Any], **kwargs) -> None:
        # 从 value 中获取 message 并打印
        msg = value.get("message", "")
        print(f"[EchoHandler] 收到消息：{msg}")

    def add_task(self, message: str) -> None:
        # 将任务写入数据库，序列化为 JSON 字符串
        task_value = {"message": message}
        self.db.add_task(self.type_name, json.dumps(task_value))
```

### 2.3 自动执行任务

```bash
python main.py
```

### 2.4 测试任务

提供了一个简单的测试任务，防止一觉醒来发现后面的任务都失败了。
原理就是开始执行某 ID 的任务，在 running_second 秒内没报错，则认为可行。

```python
from biz.task_testing import test_task

task_ids = [1]
running_second = 60  # 模拟运行的秒数
for task_id in task_ids:
    if test_task(task_id, running_second):
        print(f"任务 ID {task_id} 可行")
    else:
        print(f"任务 ID {task_id} 不可行")
```