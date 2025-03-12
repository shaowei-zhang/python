import paramiko
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("time_sync.log"),  # 日志写入文件
        logging.StreamHandler()  # 日志输出到控制台
    ]
)

# Linux 服务器的连接信息
LINUX_SERVER_IP = "192.168.1.200"  # 替换为 Linux 服务器的 IP 地址
LINUX_USERNAME = "root"  # 替换为 Linux 服务器的用户名
LINUX_PASSWORD = "DELL-8888"  # 替换为 Linux 服务器的密码


def get_windows_time():
    """
    获取本地 Windows 系统时间
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sync_time_to_linux():
    """
    将本地 Windows 时间同步到 Linux 服务器
    """
    try:
        # 获取本地 Windows 时间
        windows_time = get_windows_time()
        logging.info(f"本地 Windows 时间: {windows_time}")

        # 连接到 Linux 服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(LINUX_SERVER_IP, username=LINUX_USERNAME, password=LINUX_PASSWORD)
        logging.info("已连接到 Linux 服务器。")

        # 设置 Linux 服务器时间
        command = f'sudo date -s "{windows_time}"'
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
        stdin.write(LINUX_PASSWORD + '\n')  # 输入密码（如果需要）
        stdin.flush()

        # 检查命令执行结果
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        if error:
            logging.error(f"设置时间失败: {error}")
        else:
            logging.info(f"Linux 服务器时间已更新为: {output}")

        # 关闭 SSH 连接
        ssh.close()
        logging.info("SSH 连接已关闭。")
    except Exception as e:
        logging.error(f"同步时间时发生错误: {e}")


if __name__ == "__main__":
    logging.info("时间同步脚本已启动。")
    while True:
        sync_time_to_linux()
        logging.info("等待1小时后再次执行...")
        time.sleep(3600)  # 3600秒 = 1小时
