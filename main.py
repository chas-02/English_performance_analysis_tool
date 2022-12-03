"""
@author: ‘WhiteRed‘
@software: PyCharm
@file: main.py
@time: 2022/11/25 15:30
"""
import sys
import os
import lk_logger
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QFileDialog
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from main_window import Ui_MainWindow
from input_form import Ui_Form


class MyForm(QWidget, Ui_Form):
    textSignal = pyqtSignal([str])

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("输入框")
        self.pushButton.clicked.connect(self.closeForm)
        self.pushButton_6.clicked.connect(self.closeForm)
        self.pushButton_6.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.label_8.setEnabled(False)

    def closeForm(self):
        self.textSignal.emit(self.textEdit.toPlainText())
        MyForm.close(self)


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon("icons/favicon.ico"))
        self.setWindowTitle("成绩分析工具")
        self.start_x = None
        self.start_y = None
        self.window_x = 0
        self.window_y = 0
        self.formIsOpen = False
        self.isTop = False  # 窗口置顶
        self.isDebugging = False  # 调试模式
        self.textScore = None
        self.normal_size = self.size().width(), self.size().height()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置窗口标志：隐藏窗口边框
        self.setSignConnect()
        self.setCursorStyle()  # 设置光标样式

    # 设置鼠标移动光标样式
    def setCursorStyle(self):
        self.pushButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_2.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_3.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_6.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_7.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_8.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_11.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_12.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_13.setCursor(QCursor(Qt.PointingHandCursor))

    # 设置控件信号连接
    def setSignConnect(self):
        self.label_8.setEnabled(False)
        self.pushButton_2.clicked.connect(self.setDebugging)
        self.pushButton_8.clicked.connect(self.setWindowSize)
        self.pushButton_11.clicked.connect(self.setTopWindow)
        self.pushButton_12.setEnabled(False)
        self.pushButton_13.setEnabled(False)
        self.frame_3.setHidden(True)
        self.pushButton_10.clicked.connect(self.changePage)
        self.pushButton.clicked.connect(self.formOpen)
        self.pushButton_3.clicked.connect(self.getFile)

    def setDebugging(self):
        if self.isDebugging:
            lk_logger.setup(show_varnames=True)
            self.pushButton_2.setStyleSheet('''QPushButton{
                                        border-image: url(:/icons/bug.svg);
                                        }
                                        ''')
            self.isDebugging = False
            self.show()
        else:
            from time import strftime, localtime
            lk_logger.unload()
            # 日志文件名按照程序运行时间设置
            log_file_name = 'log-' + strftime("%Y%m%d-%H%M%S", localtime()) + '.log'
            # 记录正常的 print 信息
            sys.stdout = Logger(log_file_name)
            # 记录 traceback 异常信息
            sys.stderr = Logger(log_file_name)
            self.pushButton_2.setStyleSheet('''QPushButton{
                                        border-image: url(:/icons/bug-fill.svg);
                                        }
                                        ''')
            self.isDebugging = True
            self.show()

    def backPage(self):
        self.pushButton_12.disconnect()
        self.pushButton_12.setEnabled(False)
        self.frame_3.setHidden(True)
        self.frame_2.setHidden(False)
        self.pushButton_13.setEnabled(True)
        self.pushButton_13.clicked.connect(self.gotoPage)

    def gotoPage(self):
        self.pushButton_13.disconnect()
        self.pushButton_12.setEnabled(True)
        self.frame_3.setHidden(False)
        self.frame_2.setHidden(True)
        self.pushButton_13.setEnabled(False)
        self.pushButton_12.clicked.connect(self.backPage)

    def getScore(self, text):
        if text!='':
            from crawler import runGetHtml
            self.textScore = runGetHtml(text, self.comboBox.currentText())
            print(self.textScore)
            self.outputScore()

    def outputScore(self):
        buttons = [self.textBrowser, self.textBrowser_4, self.textBrowser_3, self.textBrowser_5, self.textBrowser_6, self.textBrowser_2]
        for idx, button in enumerate(buttons):
            button.clear()
            button.setText(self.textScore[idx][1])

    def ocrRecognition(self, fileName):
        from ocr import OCRrecognition
        ocr = OCRrecognition(use_gpu=False)
        result = ocr.ocr(fileName)[0]
        string = ""
        for item in result:
            item = item[1][0]
            string += item + '\n'

        self.setWindowModality(Qt.ApplicationModal)
        self.formOpen(string)

    def getFile(self):
        try:
            fileName, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(), "图片文件(*.jpg *.png)")
            if fileName != '':
                self.ocrRecognition(fileName)
        except Exception as e:
            print("In getFile function:", e)

    def closeForm(self):
        self.formIsOpen = False

    def getText(self, text):
        print(text)
        self.closeForm()
        self.getScore(text)

    def formOpen(self, string):
        try:
            if not self.formIsOpen:
                if string == False:
                    string = ''
                self.setWindowModality(Qt.ApplicationModal)
                self.formIsOpen = True
                Form = MyForm(self)
                Form.resize(int(self.width() * 0.8), self.height())
                Form.textSignal.connect(self.closeForm)
                Form.textSignal.connect(self.getText)
                Form.textEdit.setText(string)
                Form.show()
        except Exception as e:
            print("In formOpen function:", e)

    def changePage(self):
        if self.comboBox.currentText() == "请选择试卷类型":
            return
        self.gotoPage()

    def setTopWindow(self):
        if self.isTop:
            self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
            self.pushButton_11.setStyleSheet('''QPushButton{
                                        border-image: url(:/icons/pin-angle.svg);
                                        }
                                        ''')
            self.isTop = False
            self.show()
        else:
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            self.pushButton_11.setStyleSheet('''QPushButton{
                                        border-image: url(:/icons/pin-angle-fill.svg);
                                        }
                                        ''')
            self.isTop = True
            self.show()

    #  设置窗口大小
    def setWindowSize(self):
        try:
            if self.size() == self.screen().size():
                self.move(self.window_x, self.window_y)
                self.resize(self.normal_size[0], self.normal_size[1])
            else:
                self.window_x, self.window_y = self.x(), self.y()
                self.move(0, 0)
                self.resize(self.screen().size())
        except Exception as e:
            print("In setWindowSize function:", e)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            super(MyWindow, self).mouseDoubleClickEvent(event)
            self.setWindowSize()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            super(MyWindow, self).mousePressEvent(event)
            self.start_x = event.x()
            self.start_y = event.y()

    def mouseReleaseEvent(self, event):
        self.start_x = None
        self.start_y = None
        mouse_y = QCursor.pos().y()
        if not mouse_y:
            self.setWindowSize()

    def mouseMoveEvent(self, event):
        try:
            super(MyWindow, self).mouseMoveEvent(event)
            dis_x = event.x() - self.start_x
            dis_y = event.y() - self.start_y
            mouse_y = QCursor.pos().y()
            if self.size() == self.screen().size():
                mouse_x = QCursor.pos().x()

                pos_x = mouse_x - int(self.normal_size[0]*(mouse_x - self.x())/self.width())
                pos_y = mouse_y - int(self.normal_size[1]*(mouse_y - self.y())/self.width())
                self.move(pos_x + dis_x, pos_y + dis_y)
                self.resize(self.normal_size[0], self.normal_size[1])
                self.start_x = mouse_x - self.x()
                self.start_y = mouse_y - self.y()
            else:
                self.move(self.x() + dis_x, self.y() + dis_y)
        except:
            pass


class Logger(object):
    def __init__(self, file_name="main.log", stream=sys.stdout):
        self.terminal = stream
        self.log = open(file_name, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

    def fileno(self):
        pass

if __name__ == '__main__':
    lk_logger.setup(show_varnames=True)
    app = QApplication(sys.argv)
    MainWindow = MyWindow()
    MainWindow.show()
    sys.exit(app.exec_())
