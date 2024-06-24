
import asyncio
import os
import sys
from typing import Optional
import toml

from mikazuki.app.models import APIResponse
from mikazuki.log import log
from mikazuki.tasks import tm
from mikazuki.utils.redis_utils import publish_data, TRAINER_SERVER


def run_train(toml_path: str,
              trainer_file: str = "./sd-scripts/train_network.py",
              gpu_ids: Optional[list] = None,
              cpu_threads: Optional[int] = 2,
              task_id: Optional[str] = None):
    log.info(f"Training started with config file / 训练开始，使用配置文件: {toml_path}")
    args = [
        sys.executable, "-m", "accelerate.commands.launch",  # use -m to avoid python script executable error
        "--num_cpu_threads_per_process", str(cpu_threads),  # cpu threads
        "--quiet",  # silence accelerate error message
        trainer_file,
        "--config_file", toml_path,
    ]

    customize_env = os.environ.copy()
    customize_env["ACCELERATE_DISABLE_RICH"] = "1"
    customize_env["PYTHONUNBUFFERED"] = "1"

    if gpu_ids:
        customize_env["CUDA_VISIBLE_DEVICES"] = ",".join(gpu_ids)
        log.info(f"Using GPU(s) / 使用 GPU: {gpu_ids}")

        if len(gpu_ids) > 1:
            args[3:3] = ["--multi_gpu", "--num_processes", str(len(gpu_ids))]

    if not (task := tm.create_task(args, customize_env, task_id)):
        return APIResponse(status="error", message="Failed to create task / 无法创建训练任务")

    def _run():
        message = {
                "task_id": task_id,
                "task_type": "train",
                "task_status": "done",
                "task_worker": TRAINER_SERVER,
                "task_config": None
            }
        
        try:
            with open(toml_path, 'r', encoding='utf-8') as f:
                task_config = toml.load(f)
                message["task_config"] = task_config
            
            task.execute()
            result = task.communicate()
            if result.returncode != 0:
                log.error(f"Training failed / 训练失败")
                message["task_status"] = "failed"
            else:
                log.info(f"Training finished / 训练完成")
            
            publish_data("task_train", message)
        except Exception as e:
            log.error(f"An error occurred when training / 训练出现致命错误: {e}")
            message["task_status"] = "error"
            publish_data("task_train", message)

    coro = asyncio.to_thread(_run)
    asyncio.create_task(coro)

    return APIResponse(status="success", message=f"Training started / 训练开始 ID: {task.task_id}")
