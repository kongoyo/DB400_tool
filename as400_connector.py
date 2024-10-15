import jaydebeapi
import os
import logging  # 添加日誌模組
from PyQt5.QtWidgets import QMessageBox

# 設置日誌紀錄
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 取得當前文件的目錄
current_dir = os.path.dirname(__file__)
# 設定相對路徑
jt400_path = os.path.join(current_dir, "jt400.jar")  # 替換為實際的相對路徑

# 記錄當前使用的.py檔案
logging.info("當前使用的檔案: %s", __file__)

class AS400Connector:
    def __init__(self):
        self.connections = {}
        self.current_connection = None
        logging.info("AS400Connector 初始化")  # 日誌紀錄

    def connect_to_as400(self, host, user, password):
        logging.info("嘗試連接到 AS400，主機: %s", host)  # 日誌紀錄

        # 檢查是否已經連接到相同的主機
        # if self.current_connection == host:
        #     logging.warning("已經連接到 %s", host)  # 日誌紀錄
        #     return None, "已經連接到該主機"

        try:
            connection_string = f"jdbc:as400://{host}"
            connection = jaydebeapi.connect("com.ibm.as400.access.AS400JDBCDriver",
                                            connection_string,
                                            [user, password],
                                            jt400_path)  # 確保這裡正確使用 jt400_path
            self.connections[host] = connection
            self.current_connection = host
            logging.info("成功連接到 AS400: %s", host)  # 日誌紀錄
            return connection, None
        except Exception as e:
            logging.error("連接失敗: %s", str(e))  # 日誌紀錄
            return None, str(e)

    def disconnect_from_as400(self, host):
        logging.info("嘗試斷開連接: %s", host)  # 日誌紀錄
        if host in self.connections:
            try:
                self.connections[host].close()
                del self.connections[host]
                if self.connections:
                    self.current_connection = next(iter(self.connections))
                else:
                    self.current_connection = None
                logging.info("成功斷開連接: %s", host)  # 日誌紀錄
                return True, None
            except Exception as e:
                logging.error("斷開連接失敗: %s", str(e))  # 日誌紀錄
                return False, str(e)
        else:
            logging.warning("找不到指定的連接: %s", host)  # 日誌紀錄
            return False, "找不到指定的連接"

    def switch_system(self, selected_system):
        logging.info("嘗試切換系統: %s", selected_system)  # 日誌紀錄
        if selected_system in self.connections:
            self.current_connection = selected_system
            logging.info("成功切換到系統: %s", selected_system)  # 日誌紀錄
            return True
        logging.warning("切換系統失敗: %s 不在連接中", selected_system)  # 日誌紀錄
        return False

    def execute_query(self, query):
        logging.info("執行查詢: %s", query)  # 日誌紀錄
        if not self.current_connection:
            logging.warning("沒有活動的連接")  # 日誌紀錄
            return None, "沒有活動的連接"
        try:
            with self.connections[self.current_connection].cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                result = cursor.fetchall()
                logging.info("查詢成功，返回 %d 行結果", len(result))  # 日誌紀錄
                return (columns, result), None
        except Exception as e:
            logging.error("查詢執行失敗: %s", str(e))  # 日誌紀錄
            return None, str(e)

def disconnect_from_as400(connection):
    logging.info("使用獨立函數斷開連接")  # 日誌紀錄
    try:
        connection.close()
        logging.info("成功斷開連接")  # 日誌紀錄
        return True, None
    except Exception as e:
        logging.error("斷開連接失敗: %s", str(e))  # 日誌紀錄
        return False, str(e)

# utils.py
def handle_error(e):
    logging.error("處理錯誤: %s", str(e))  # 日誌紀錄
    QMessageBox.critical(None, "錯誤", str(e))

# config.py
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
}
