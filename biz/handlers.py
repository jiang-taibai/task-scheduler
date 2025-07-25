import json
import os.path as osp
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type
from subprocess import run
from pathlib import Path

from common.utils import make_sure_dir_exists, get_absolute_path, get_filename_stem, get_timestamp
from config.config import LOG_ROOT
from dal.sqlite import TaskDB

from common.logger import get_logger

logger = get_logger(__name__)

# 用于自动注册处理程序的注册表和装饰器
HANDLER_REGISTRY: Dict[str, Type] = {}


def register_handler(cls):
    HANDLER_REGISTRY[cls.type_name] = cls
    return cls


class BaseHandler(ABC):
    type_name: str = "base_handler"

    def __init__(self):
        """
        BaseHandler 初始化方法，创建任务数据库实例。
        """
        self.db = TaskDB()

    @abstractmethod
    def execute(self, value: Dict[str, Any], **kwargs) -> None:
        pass

    @abstractmethod
    def add_task(self, *args, **kwargs) -> None:
        """
        添加任务到队列的方法，子类需要实现具体的任务添加逻辑。
        """
        raise NotImplementedError("本方法需要在子类中实现")


@register_handler
class PrintHandler(BaseHandler):
    type_name = "print"

    def execute(self, value: Dict[str, Any], **kwargs) -> None:
        message = value.get("message", "[No message provided]")
        print(f"[PrintHandler] {message}")

    def add_task(self, message: str) -> None:
        task_value = {"message": message}
        self.db.add_task(self.type_name, json.dumps(task_value))


@register_handler
class MMRotateTrainingHandler(BaseHandler):
    type_name = "mmrotate_training"

    def execute(self, value: Dict[str, Any], **kwargs) -> None:
        python_interpreter = value.get("python_interpreter", "python")
        training_script = value.get("training_script", "train.py")
        config_file = value.get("config_file", "default_config.py")
        optional_arguments = value.get("optional_arguments", [])
        working_dir = value.get("working_dir", str(Path(training_script).parent.parent))

        subprocess_output_filename = osp.join(
            LOG_ROOT,
            r"./handler_log/mmrotate_training/",
            f"{get_timestamp()}_{get_filename_stem(config_file)}.log"
        )
        subprocess_output_filename = osp.abspath(subprocess_output_filename)
        make_sure_dir_exists(subprocess_output_filename)

        command = [
            python_interpreter,
            training_script,
            config_file,
            *optional_arguments
        ]
        with open(get_absolute_path(subprocess_output_filename), "a", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write("config:\n" + json.dumps(value, indent=4) + "\n")
            f.write("command:\n" + " ".join(command) + "\n")
            f.write("=" * 50 + "\n\n")
            f.flush()
            logger.info(f"开始执行命令: {' '.join(command)} in {working_dir}")
            logger.info(f"运行下面指令可实时查看日志文件：")
            logger.info(f'Linux: tail -f "{subprocess_output_filename}"')
            logger.info(f'Windows: Get-Content "{subprocess_output_filename}" -Wait')
            result = run(command, check=True, cwd=working_dir, stdout=f, stderr=f, timeout=kwargs.get('timeout', None))
            if result.returncode != 0:
                raise RuntimeError(f"训练脚本执行失败，返回码：{result.returncode}")

    def add_task(self,
                 python_interpreter: str,
                 training_script: str,
                 config_file: str,
                 optional_arguments: List[str] = "",
                 working_dir: str = None) -> None:
        task_value = {
            "python_interpreter": python_interpreter,
            "training_script": training_script,
            "config_file": config_file,
            "optional_arguments": optional_arguments,
            "working_dir": working_dir
        }
        self.db.add_task(self.type_name, json.dumps(task_value, indent=4))


@register_handler
class MMRotateTestingHandler(BaseHandler):
    type_name = "mmrotate_testing"

    def execute(self, value: Dict[str, Any], **kwargs) -> None:
        python_interpreter = value.get("python_interpreter", "python")
        testing_script = value.get("testing_script", "test.py")
        config_file = value.get("config_file", "default_config.py")
        checkpoint_file = value.get("checkpoint_file", "latest.pth")
        optional_arguments = value.get("optional_arguments", [])
        working_dir = value.get("working_dir", str(Path(testing_script).parent.parent))

        subprocess_output_filename = osp.join(
            LOG_ROOT,
            r"./handler_log/mmrotate_testing/",
            f"{get_timestamp()}_{get_filename_stem(config_file)}.log"
        )
        subprocess_output_filename = osp.abspath(subprocess_output_filename)
        make_sure_dir_exists(subprocess_output_filename)

        command = [
            python_interpreter,
            testing_script,
            config_file,
            checkpoint_file,
            *optional_arguments,
        ]
        with open(get_absolute_path(subprocess_output_filename), "a", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write("config:\n" + json.dumps(value, indent=4) + "\n")
            f.write("command:\n" + " ".join(command) + "\n")
            f.write("=" * 50 + "\n\n")
            f.flush()
            logger.info(f"开始执行命令: {' '.join(command)} in {working_dir}")
            logger.info(f"运行下面指令可实时查看日志文件：")
            logger.info(f"Linux: tail -f {subprocess_output_filename}")
            logger.info(f"Windows: Get-Content {subprocess_output_filename} -Wait")
            result = run(command, check=True, cwd=working_dir, stdout=f, stderr=f, timeout=kwargs.get('timeout', None))
            if result.returncode != 0:
                raise RuntimeError(f"测试脚本执行失败，返回码：{result.returncode}")

    def add_task(
            self,
            python_interpreter: str,
            testing_script: str,
            config_file: str,
            checkpoint_file: str,
            optional_arguments: List[str] = "",
            working_dir: str = None,
    ) -> None:
        task_value = {
            "python_interpreter": python_interpreter,
            "testing_script": testing_script,
            "config_file": config_file,
            "checkpoint_file": checkpoint_file,
            "optional_arguments": optional_arguments,
            "working_dir": working_dir
        }
        self.db.add_task(self.type_name, json.dumps(task_value, indent=4))


class HandlerFactory:
    _handlers = HANDLER_REGISTRY

    @classmethod
    def get_handler(cls, type_name: str) -> BaseHandler:
        if type_name not in cls._handlers:
            raise ValueError(f"Unknown handler type: {type_name}")
        return cls._handlers[type_name]()
