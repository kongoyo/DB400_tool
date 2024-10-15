import os
import sys
from PySide6.QtCore import QTimer
from gui import AS400ConnectorGUI
from user_manager import UserManager
from job_manager import JobManager
from as400_connector import AS400Connector
from utils import setup_environment
import logging  # 添加此行以導入 logging 模組
from PyQt5.QtWidgets import QMessageBox
from PySide6.QtWidgets import QApplication

def create_application():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 風格以獲得更現代的外觀
    return app

def setup_main_gui(jt400_path):  # 修改此行以接受 jt400_path
    main_gui = AS400ConnectorGUI(jt400_path)  # 傳遞 jt400_path
    return main_gui

# 確保在使用之前定義 initialize_managers 函數
def initialize_managers(main_gui, connection):
    # ... 函數實現 ...
    pass  # 替換為實際代碼

def get_active_connection(main_gui):
    return main_gui.as400_connector.connections.get(main_gui.as400_connector.current_connection)

from gui import AS400ConnectorGUI  # 確保導入 AS400ConnectorGUI 類

def main():
    logging.info("開始主函數...")
    app = create_application()  # 確保在創建任何 QWidget 之前創建 QApplication
    
    # 取得當前文件的目錄
    current_dir = os.path.dirname(__file__)
    # 設定相對路徑
    jt400_path = os.path.join(current_dir, "jt400.jar")  # 替換為實際的相對路徑

    # 記錄 jt400_path 的路徑
    logging.info("jt400.jar 的路徑是: %s", jt400_path)

    main_gui = setup_main_gui(jt400_path)  # 使用 setup_main_gui 函數創建 AS400ConnectorGUI 實例
    main_gui.show()  # 顯示主畫面
    logging.info("主畫面顯示完成")
    
    logging.info("啟動應用程序事件循環...")
    sys.exit(app.exec())

if __name__ == '__main__':
    main()