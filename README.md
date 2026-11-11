# 编译原理：局部优化

这是一个使用 Python 和 PyQt5 编写的编译技术课程项目，提供图形界面，对中间代码进行基本块划分和局部优化。

项目包含常量合并、冗余操作删除、无用变量删除及基于 DAG 的优化功能。仓库中的 demo.txt、demo2.txt 和 demo3.txt 是示例输入。

## 运行

1. 安装 Python 和依赖：python -m pip install -r requirements.txt
2. 运行程序：python main.py
3. 在界面中打开示例文件，选择需要的优化操作。

界面布局源文件为 jiemian.ui；src/jiemian.py 为对应的 Python 界面代码。
