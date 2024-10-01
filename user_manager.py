import jaydebeapi
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                               QMessageBox, QInputDialog, QLineEdit, QComboBox, QDialog, QFormLayout, QCheckBox, QDialogButtonBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class PasswordLineEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.toggle_button = QPushButton("顯示密碼", self)
        self.toggle_button.clicked.connect(self.toggle_password_visibility)
        layout.addWidget(self.toggle_button)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_button.setText("隱藏密碼")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_button.setText("顯示密碼")

    def text(self):
        return self.password_input.text()

class CreateUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("創建新用戶")
        self.layout = QFormLayout(self)

        # 用戶名
        self.username_input = QLineEdit(self)
        self.layout.addRow("用戶名:", self.username_input)

        # 密碼
        self.password_input = PasswordLineEdit(self)
        self.layout.addRow("密碼:", self.password_input)

        # 描述
        self.description_input = QLineEdit(self)
        self.layout.addRow("描述:", self.description_input)

        # User Class
        self.user_class_combo = QComboBox(self)
        self.user_class_combo.addItems(["*USER", "*SYSOPR", "*PGMR", "*SECADM", "*SECOFR"])
        self.layout.addRow("User Class:", self.user_class_combo)

        # 特殊權限
        self.special_auth_checkboxes = []
        special_auths = ["*ALLOBJ", "*AUDIT", "*IOSYSCFG", "*JOBCTL", "*SAVSYS", "*SECADM", "*SERVICE", "*SPLCTL"]
        auth_layout = QVBoxLayout()
        for auth in special_auths:
            checkbox = QCheckBox(auth)
            self.special_auth_checkboxes.append(checkbox)
            auth_layout.addWidget(checkbox)
        self.layout.addRow("特殊權限:", auth_layout)

        # 確認和取消按鈕
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addRow(self.button_box)

    def get_user_info(self):
        special_auths = [cb.text() for cb in self.special_auth_checkboxes if cb.isChecked()]
        return {
            "username": self.username_input.text(),
            "password": self.password_input.text(),
            "description": self.description_input.text(),
            "user_class": self.user_class_combo.currentText(),
            "special_authorities": special_auths
        }

class UserManager:
    def __init__(self, connection):
        self.connection = connection

    def list_users(self):
        """列出所有使用者"""
        query = """
        SELECT USER_NAME, STATUS, PREVIOUS_SIGNON, PASSWORD_CHANGE_DATE
        FROM QSYS2.USER_INFO
        ORDER BY USER_NAME
        """
        return self._execute_query(query)

    def create_user(self, username, password, description="", user_class="*USER", special_authorities=[]):
        """創建新使用者"""
        special_auth = " ".join(special_authorities)
        cmd = f"CRTUSRPRF USRPRF({username}) PASSWORD({password}) TEXT('{description}') USRCLS({user_class}) SPCAUT({special_auth})"
        self._execute_command(cmd)

    def delete_user(self, username):
        """刪除使用者"""
        cmd = f"DLTUSRPRF USRPRF({username})"
        self._execute_command(cmd)

    def change_password(self, username, new_password):
        """更改使用者密碼"""
        cmd = f"CHGUSRPRF USRPRF({username}) PASSWORD({new_password})"
        self._execute_command(cmd)

    def disable_user(self, username):
        """停用用戶帳號"""
        cmd = f"CHGUSRPRF USRPRF({username}) STATUS(*DISABLED)"
        self._execute_command(cmd)

    def enable_user(self, username):
        """啟用用戶帳號"""
        cmd = f"CHGUSRPRF USRPRF({username}) STATUS(*ENABLED)"
        self._execute_command(cmd)

    def _execute_query(self, query):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                result = cursor.fetchall()
                return columns, result
        except Exception as e:
            print(f"執行查詢時發生錯誤: {str(e)}")
            return None

    def _execute_command(self, cmd):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("CALL QSYS2.QCMDEXC(?)", (cmd,))
        except Exception as e:
            print(f"執行命令時發生錯誤: {str(e)}")
            raise

class UserManagerGUI(QWidget):
    def __init__(self, parent, user_manager):
        super().__init__(parent)
        self.parent = parent
        self.user_manager = user_manager
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # 創建按鈕
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton('刷新用戶列表')
        self.create_button = QPushButton('創建用戶')
        self.delete_button = QPushButton('刪除用戶')
        self.change_password_button = QPushButton('更改密碼')
        self.disable_user_button = QPushButton('停用帳號')
        self.enable_user_button = QPushButton('啟用帳號')

        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.change_password_button)
        button_layout.addWidget(self.disable_user_button)
        button_layout.addWidget(self.enable_user_button)

        layout.addLayout(button_layout)

        # 創建表格
        self.user_table = QTableWidget()
        layout.addWidget(self.user_table)

        # 連接按鈕信號
        self.refresh_button.clicked.connect(self.refresh_user_list)
        self.create_button.clicked.connect(self.create_user_dialog)
        self.delete_button.clicked.connect(self.delete_user_dialog)
        self.change_password_button.clicked.connect(self.change_password_dialog)
        self.disable_user_button.clicked.connect(self.disable_user_dialog)
        self.enable_user_button.clicked.connect(self.enable_user_dialog)

        # 初始化用戶列表
        self.refresh_user_list()

    def refresh_user_list(self):
        result = self.user_manager.list_users()
        if result:
            columns, data = result
            self.user_table.setColumnCount(len(columns))
            self.user_table.setRowCount(len(data))
            self.user_table.setHorizontalHeaderLabels(columns)

            for row, user_data in enumerate(data):
                for col, value in enumerate(user_data):
                    self.user_table.setItem(row, col, QTableWidgetItem(str(value)))

            self.user_table.resizeColumnsToContents()
            self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        else:
            QMessageBox.warning(self, "錯誤", "無法���取用戶列表")

    def create_user_dialog(self):
        dialog = CreateUserDialog(self)
        if dialog.exec_():
            user_info = dialog.get_user_info()
            try:
                self.user_manager.create_user(
                    user_info["username"],
                    user_info["password"],
                    user_info["description"],
                    user_info["user_class"],
                    user_info["special_authorities"]
                )
                QMessageBox.information(self, "成功", f"用戶 {user_info['username']} 已成功創建")
                self.refresh_user_list()
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"創建用戶時發生錯誤：{str(e)}")

    def delete_user_dialog(self):
        username, ok = QInputDialog.getText(self, "刪除用戶", "輸入要刪除的用戶名:")
        if ok and username:
            confirm = QMessageBox.question(self, "確認", f"確定要刪除用戶 {username} 嗎？",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    self.user_manager.delete_user(username)
                    QMessageBox.information(self, "成功", f"用戶 {username} 已成功刪除")
                    self.refresh_user_list()
                except Exception as e:
                    QMessageBox.critical(self, "錯誤", f"刪除用戶時發生錯誤：{str(e)}")

    def change_password_dialog(self):
        username, ok = QInputDialog.getText(self, "更改密碼", "輸入要更改密碼的用戶名:")
        if ok and username:
            password_dialog = QDialog(self)
            password_dialog.setWindowTitle("輸入新密碼")
            layout = QVBoxLayout(password_dialog)
            password_input = PasswordLineEdit(password_dialog)
            layout.addWidget(password_input)
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, password_dialog)
            buttons.accepted.connect(password_dialog.accept)
            buttons.rejected.connect(password_dialog.reject)
            layout.addWidget(buttons)

            if password_dialog.exec_() == QDialog.Accepted:
                new_password = password_input.text()
                try:
                    self.user_manager.change_password(username, new_password)
                    QMessageBox.information(self, "成功", f"用戶 {username} 的密碼已成功更改")
                except Exception as e:
                    QMessageBox.critical(self, "錯誤", f"更改密碼時發生錯誤：{str(e)}")

    def disable_user_dialog(self):
        username, ok = QInputDialog.getText(self, "停用帳號", "輸入要停用的用戶名:")
        if ok and username:
            try:
                self.user_manager.disable_user(username)
                QMessageBox.information(self, "成功", f"用戶 {username} 的帳號已成功停用")
                self.refresh_user_list()
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"停用帳號時發生錯誤：{str(e)}")

    def enable_user_dialog(self):
        username, ok = QInputDialog.getText(self, "啟用帳號", "輸入要啟用的用戶名:")
        if ok and username:
            try:
                self.user_manager.enable_user(username)
                QMessageBox.information(self, "成功", f"用戶 {username} 的帳號已成功啟用")
                self.refresh_user_list()
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"啟用帳號時發生錯誤：{str(e)}")