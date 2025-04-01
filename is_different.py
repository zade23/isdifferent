#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import hashlib
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, 
                            QLineEdit, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent


class FileDropLineEdit(QLineEdit):
    """支持拖放文件的输入框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setReadOnly(True)
        self.setPlaceholderText("拖放文件到此处或点击选择按钮")
        self.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f9f9f9;
            }
        """)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖动进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # 改变样式以提供视觉反馈
            self.setStyleSheet("""
                QLineEdit {
                    padding: 5px;
                    border: 2px dashed #3498db;
                    border-radius: 4px;
                    background-color: #e8f4fc;
                }
            """)
            
    def dragLeaveEvent(self, event):
        """拖动离开事件"""
        # 恢复原始样式
        self.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f9f9f9;
            }
        """)
        
    def dropEvent(self, event: QDropEvent):
        """放下事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.setText(file_path)
            # 恢复原始样式
            self.setStyleSheet("""
                QLineEdit {
                    padding: 5px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    background-color: #f9f9f9;
                }
            """)


class FileHashCalculator:
    """文件哈希计算器类，负责文件哈希值的计算"""
    
    @staticmethod
    def calculate_md5(file_path):
        """计算文件MD5哈希值"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest(), None  # 返回哈希值和None作为错误
        except Exception as e:
            return None, str(e)  # 返回None作为哈希值和错误消息


class HashComparer(QMainWindow):
    """哈希比较器主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.file_calculator = FileHashCalculator()
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        # 设置主窗口
        self.setWindowTitle('文件哈希值比较工具')
        self.setGeometry(300, 300, 700, 450)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        
        # 创建中央小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 文件选择区域
        main_layout.addLayout(self._create_file_selection_area())
        
        # 哈希值显示区域
        main_layout.addWidget(self._create_hash_display_area())
        
        # 结果显示区域
        main_layout.addWidget(self._create_result_area())
        
        # 比较按钮
        compare_btn = QPushButton("比较文件")
        compare_btn.setMinimumHeight(40)
        compare_btn.setFont(QFont("", 11, QFont.Weight.Bold))
        compare_btn.clicked.connect(self.compare_files)
        main_layout.addWidget(compare_btn)
    
    def _create_file_selection_area(self):
        """创建文件选择区域"""
        files_layout = QHBoxLayout()
        files_layout.setSpacing(15)
        
        # 文件1选择部分
        self.file1_group = QGroupBox("文件1")
        file1_layout = QVBoxLayout()
        file1_layout.setSpacing(10)
        
        self.file1_path = FileDropLineEdit()  # 使用支持拖放的输入框
        
        self.file1_btn = QPushButton("选择文件")
        self.file1_btn.clicked.connect(lambda: self._select_file(self.file1_path))
        
        file1_layout.addWidget(self.file1_path)
        file1_layout.addWidget(self.file1_btn)
        self.file1_group.setLayout(file1_layout)
        
        # 文件2选择部分
        self.file2_group = QGroupBox("文件2")
        file2_layout = QVBoxLayout()
        file2_layout.setSpacing(10)
        
        self.file2_path = FileDropLineEdit()  # 使用支持拖放的输入框
        
        self.file2_btn = QPushButton("选择文件")
        self.file2_btn.clicked.connect(lambda: self._select_file(self.file2_path))
        
        file2_layout.addWidget(self.file2_path)
        file2_layout.addWidget(self.file2_btn)
        self.file2_group.setLayout(file2_layout)
        
        files_layout.addWidget(self.file1_group)
        files_layout.addWidget(self.file2_group)
        
        return files_layout
        
    def _create_hash_display_area(self):
        """创建哈希值显示区域"""
        hash_group = QGroupBox("哈希值 (MD5)")
        hash_layout = QVBoxLayout()
        hash_layout.setSpacing(10)
        
        # 文件1哈希值
        hash1_layout = QHBoxLayout()
        hash1_label = QLabel("文件1哈希值:")
        self.hash1_value = QLineEdit()
        self.hash1_value.setReadOnly(True)
        self.hash1_value.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                font-family: Consolas, monospace;
            }
        """)
        hash1_layout.addWidget(hash1_label)
        hash1_layout.addWidget(self.hash1_value)
        
        # 文件2哈希值
        hash2_layout = QHBoxLayout()
        hash2_label = QLabel("文件2哈希值:")
        self.hash2_value = QLineEdit()
        self.hash2_value.setReadOnly(True)
        self.hash2_value.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                font-family: Consolas, monospace;
            }
        """)
        hash2_layout.addWidget(hash2_label)
        hash2_layout.addWidget(self.hash2_value)
        
        hash_layout.addLayout(hash1_layout)
        hash_layout.addLayout(hash2_layout)
        hash_group.setLayout(hash_layout)
        
        return hash_group
        
    def _create_result_area(self):
        """创建结果显示区域"""
        result_group = QGroupBox("比较结果")
        result_layout = QVBoxLayout()
        
        self.result_label = QLabel("请选择两个文件进行比较")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.result_label.setFont(font)
        self.result_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                border-radius: 4px;
                background-color: #f8f8f8;
            }
        """)
        
        result_layout.addWidget(self.result_label)
        result_group.setLayout(result_layout)
        
        return result_group
        
    def _select_file(self, line_edit):
        """选择文件并显示路径"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*)")
        if file_path:
            line_edit.setText(file_path)
            
    def calculate_hash(self, file_path):
        """计算文件哈希值"""
        result, error = self.file_calculator.calculate_md5(file_path)
        if error:
            QMessageBox.critical(self, "错误", f"计算文件哈希值时出错: {error}")
            return None
        return result
            
    def compare_files(self):
        """比较两个文件的哈希值"""
        file1_path = self.file1_path.text()
        file2_path = self.file2_path.text()
        
        if not file1_path or not file2_path:
            QMessageBox.warning(self, "警告", "请先选择两个文件")
            return
            
        # 计算哈希值
        hash1 = self.calculate_hash(file1_path)
        hash2 = self.calculate_hash(file2_path)
        
        if hash1 is None or hash2 is None:
            return
            
        # 显示哈希值
        self.hash1_value.setText(hash1)
        self.hash2_value.setText(hash2)
        
        # 比较并显示结果
        if hash1 == hash2:
            self.result_label.setText("文件哈希值相同")
            self.result_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    border-radius: 4px;
                    background-color: #dff0d8;
                    color: #3c763d;
                    font-weight: bold;
                }
            """)
        else:
            self.result_label.setText("文件哈希值不同")
            self.result_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    border-radius: 4px;
                    background-color: #f2dede;
                    color: #a94442;
                    font-weight: bold;
                }
            """)


def main():
    app = QApplication(sys.argv)
    window = HashComparer()
    window.show()
    sys.exit(app.exec())  # PyQt6中不再需要下划线


if __name__ == '__main__':
    main()