
"""
实现界面的逻辑功能
"""

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog,QMessageBox

from src.jiemian import Ui_MainWindow
from src.BB_Division import BasicBlockDivsion
from src.DAG import DAG


class MyGui(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MyGui, self).__init__()  # 调用父类构造函数
        self.setupUi(self)              # 图形界面初始化函数
        self.sourceCode = None          # 源程序
        self.basic_block = None         # 基本块

    # 打开一个文件
    def openfile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "*.txt;;All Files(*)")
        if not filename:
            return

        try:
            with open(filename, 'r') as f:
                source_code = f.read()
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self, "打开文件失败", str(error))
            return

        self.sourceCode = source_code
        self.basic_block = None
        self.SourceProgramText.setPlainText(source_code)
        self.textEdit.clear()
        self.BasicBlockDivisionButton.setEnabled(True)
        self.LocalOptimizationButton.setEnabled(True)
        self.DAGOptimization.setEnabled(True)
        self.del_redundant_operations_btn.setEnabled(True)
        self.del_unreferenced_var_btn.setEnabled(True)
        self.merge_knowned_member_btn.setEnabled(True)

    # 点击划分基本块按钮
    def click_B_B_D_Button(self):
        print("click_B_B_D_Button  ")
        self.textEdit.clear()
        if self.SourceProgramText.toPlainText() == '':
            QMessageBox.warning(self,"提示", "未打开文件！")
            return

        self.basic_block=BasicBlockDivsion.getBasicBlocks(code=self.sourceCode)

        msg = []      # 要显示的基本块信息
        for member in self.basic_block:
            msg.append(member.name)
            bb_code='\n'.join(map(str,member.code))     # code列表转换成字符串，按换行符拼接
            msg.append(bb_code)

        # 将msg转换成str形式并显示在文本区
        text = '\n'.join(map(str, msg))
        self.textEdit.setText(text)
        self.textEdit.append("\n******\n")

    # 点击局部优化按钮
    def click_localOpt_Button(self):
        print("click_localOpt_Button")

        self.textEdit.clear()
        if self.SourceProgramText.toPlainText() == '':
            QMessageBox.warning(self,"提示", "未打开文件！")
            return

        self.basic_block = BasicBlockDivsion.getBasicBlocks(code=self.sourceCode)
        for bb in self.basic_block:
            print("———————————————", bb.name, "———————————————————")
            self.textEdit.append("\n***********")
            self.textEdit.append(bb.name)
            bb.optimization()
            self.textEdit.append(bb.get_code())
            self.textEdit.append("***********\n")

    # 点击合并已知量按钮
    def click_merge_knowned_member_btn(self):
        print("click_merge_knowned_member_btn")

        self.textEdit.clear()
        if self.SourceProgramText.toPlainText() == '':
            QMessageBox.warning(self,"提示", "未打开文件！")
            return
        self.basic_block = BasicBlockDivsion.getBasicBlocks(code=self.sourceCode)
        for bb in self.basic_block:
            print("———————————————", bb.name, "———————————————————")
            self.textEdit.append("\n***********")
            self.textEdit.append(bb.name)
            bb.statistic_vars_referenced_line_list()
            bb.statistic_variables()
            result = bb.merge_knowned_member()
            if result:
                self.textEdit.append(bb.get_code())
            else:
                self.textEdit.append(bb.get_code())
                self.textEdit.append("该基本块不需要合并已知量")
            self.textEdit.append("***********\n")

    # 点击删除多余运算按钮
    def click_del_redundant_operations_btn(self):
        print("click_del_redundant_operations_btn")

        self.textEdit.clear()
        if self.SourceProgramText.toPlainText() == '':
            QMessageBox.warning(self,"提示", "未打开文件！")
            return
        self.basic_block = BasicBlockDivsion.getBasicBlocks(code=self.sourceCode)
        for bb in self.basic_block:
            print("———————————————", bb.name, "———————————————————")
            self.textEdit.append("\n***********")
            self.textEdit.append(bb.name)
            bb.statistic_vars_referenced_line_list()
            bb.statistic_variables()
            result = bb.del_redundant_operations()
            if result:
                self.textEdit.append(bb.get_code())
            else:
                self.textEdit.append(bb.get_code())
                self.textEdit.append("该基本块不存在多余运算")
            self.textEdit.append("***********\n")

    # 点击删除无用赋值按钮
    def click_del_unreferenced_var_btn(self):
        print("click_del_unreferenced_var_btn")
        self.textEdit.clear()
        if self.SourceProgramText.toPlainText() == '':
            QMessageBox.warning(self,"提示", "未打开文件！")
            return
        self.basic_block = BasicBlockDivsion.getBasicBlocks(code=self.sourceCode)
        for bb in self.basic_block:
            print("———————————————", bb.name, "———————————————————")
            self.textEdit.append("\n***********")
            self.textEdit.append(bb.name)
            bb.statistic_vars_referenced_line_list()
            bb.statistic_variables()
            result = bb.del_unreferenced_var()
            if result is True:
                self.textEdit.append(bb.get_code())
            else:
                self.textEdit.append(bb.get_code())
                self.textEdit.append("该基本块不存在无用赋值")
            self.textEdit.append("***********\n")

    # 点击DAG优化按钮
    def click_DAGOpt_Button(self):
        print("click_DAGOpt_Button ")
        self.textEdit.clear()
        if self.SourceProgramText.toPlainText() == '':
            QMessageBox.warning(self,"提示", "未打开文件！")
            return
        self.sourceCode = self.SourceProgramText.toPlainText()
        # print(self.sourceCode)
        self.basic_block = BasicBlockDivsion.getBasicBlocks(code=self.sourceCode)
        for bb in self.basic_block:
            print("******", bb.name, "******")
            self.textEdit.append("***********")
            self.textEdit.append(bb.name)
            code = bb.get_code()
            if len(code) == 0:
                continue
            dag = DAG(code.splitlines())
            code = dag.get_final_code()
            self.textEdit.append(code)
            self.textEdit.append("***********\n")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MyGui()
    w.show()
    sys.exit(app.exec_())
