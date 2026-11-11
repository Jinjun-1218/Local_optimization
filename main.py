"""
题目：局部优化的实现
1.设计出划分基本块的算法；
2.在每一个基本块中实现：合并已知量、删除多余运算和删除无用赋值三种局部优化；
3.设计构造基本块的DAG图的算法，以及将DAG图还原实现基本块的优化的算法。
project  项目文件夹
    main.py    主程序文件
    jiemian.ui  .ui界面文件
    jiamian.py  界面设计文件
    GUI.py      界面逻辑文件
    BB_Division.py 基本块划分
    BB_Optimization.py  三种局部优化的实现
    DAG.py       DAG优化的实现
"""
import os, PyQt5
dirname = os.path.dirname(PyQt5.__file__)
qt_dir = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_dir


import sys
from PyQt5 import QtWidgets
from src.GUI import MyGui

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv) # 创建应用实例
    w = MyGui()     # 初始化主窗口程序并显示
    w.show()
    sys.exit(app.exec_())
