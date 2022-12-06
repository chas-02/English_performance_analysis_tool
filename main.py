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
from PyQt5.Qt import QThread
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QObject
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
            lk_logger.unload()
            # 记录正常的 print 信息
            sys.stdout = Logger(sys.stdout)
            # 记录 traceback 异常信息
            sys.stderr = Logger(sys.stderr)
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
            # 创建子线程实例
            self.thread = QThread()
            # 创建爬虫实例
            self.crawler_thread = CrawlerThread()
            # 向子线程传递参数
            self.crawler_thread.text = text
            self.crawler_thread.grade = self.comboBox.currentText()
            # 将子线程移动到多线程类中
            self.crawler_thread.moveToThread(self.thread)
            # 子线程开始前, 连接相关运行函数
            self.thread.started.connect(self.crawler_thread.run)
            # 获取子线程信号
            self.crawler_thread.scoreSignal.connect(self.outputScore)
            # 子线程运行完时, 结束
            self.thread.finished.connect(self.thread.quit)
            # 开始运行子线程
            self.thread.start()

    def outputScore(self, score_list):
        buttons = [self.textBrowser, self.textBrowser_4, self.textBrowser_3, self.textBrowser_5, self.textBrowser_6, self.textBrowser_2]
        for idx, button in enumerate(buttons):
            button.clear()
            button.setText(score_list[idx][1])

    def ocr2form(self, string):
        self.setWindowModality(Qt.ApplicationModal)
        self.formOpen(string)

    def ocrRecognition(self, img_path):
        self.thread = QThread()
        self.ocrthread = OCRThread()
        self.ocrthread.img_path = img_path
        self.ocrthread.moveToThread(self.thread)
        self.thread.started.connect(self.ocrthread.run)
        self.ocrthread.textSignal.connect(self.ocr2form)
        self.thread.finished.connect(self.thread.quit)
        self.thread.start()

    def getFile(self):
        try:
            filePath, fileType = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(), "图片文件(*.jpg *.png)")
            if filePath != '':
                self.ocrRecognition(filePath)
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


class CrawlerThread(QObject):
    scoreSignal = pyqtSignal(list)
    text = ''
    grade = ''
    def __init__(self):
        super().__init__()

    def run(self):
        from crawler import runGetHtml
        score_list = runGetHtml(self.text, self.grade)
        self.scoreSignal.emit(score_list)


class OCRThread(QObject):
    textSignal = pyqtSignal(str)
    img_path = ''
    def __init__(self):
        super().__init__()

    def run(self):
        from ocr import OCRrecognition
        ocr = OCRrecognition(use_gpu=False)
        result = ocr.ocr(self.img_path)[0]
        string = ""
        for item in result:
            item = item[1][0]
            string += item + '\n'
        self.textSignal.emit(string)


class Logger(object):
    def __init__(self, stream=sys.stdout):
        from time import strftime, localtime
        output_dir = "log"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # 日志文件名按照程序运行时间设置
        log_name = 'log-' + strftime("%Y%m%d-%H%M%S", localtime()) + '.log'
        filename = os.path.join(output_dir, log_name)

        self.terminal = stream
        self.log = open(filename, 'a+')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

if __name__ == '__main__':
    lk_logger.setup(show_varnames=True)
    app = QApplication(sys.argv)
    MainWindow = MyWindow()
    MainWindow.show()
    sys.exit(app.exec_())
