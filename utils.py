import os
import sys
from PySide6.QtCore import QCoreApplication

# 確保程序完全退出
def force_quit():
    QCoreApplication.quit()
    sys.exit(0)

def setup_environment(jt400_path):  # 添加 jt400_path 參數
    if not os.path.exists(jt400_path):
        print(f"錯誤：jt400.jar 文件未找到：{jt400_path}")
        sys.exit(1)  # 如果文件不存在，退出程序

    # 確保 CLASSPATH 正確設置
    current_classpath = os.environ.get('CLASSPATH', '')
    os.environ["CLASSPATH"] = f"{jt400_path}:{current_classpath}" if current_classpath else jt400_path