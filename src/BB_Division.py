"""
实现基本块的划分功能
1.找入口语句  正则匹配
    入口语句的定义如下：
　　① 程序的第一个语句
　　② 条件转移语句或无条件转移语句的转移目标语句；
　　③ 紧跟在条件转移语句后面的语句
2.划分基本块
     对每一入口语句，构造其所属的基本块。
     它是由该入口语句到下一入口语句（不包括下一入口语句），或到一转移语句（包括该转移语句），或到一停语句（包括该停语句）之间的语句序列组成的。
"""

import re
from src.BB_Optimization import BasicBlockOptimization
from src.DAG import DAG


class BasicBlockDivsion:

    gotoPattern = re.compile(r'\s*GOTO (\d+)\s*')  # 转移语句正则，匹配 goto 1 语句，捕获行号
    ifPattern = re.compile(r'.*IF.+\s*GOTO')  # 条件转移语句正则，匹配if条件转移语句中的goto语句
    @staticmethod
    #寻找入口语句
    def find_entry(code:str) -> list:  # 返回为list
        # print("找入口语句：")
        entryStatements = []  # 入口语句的行号
        lines = code.splitlines()   # 按行分割

        entryStatements.append(1)  # 程序第一句是入口语句

        for i,line in enumerate(lines,start=1):#enumerate:将可以遍历的数据对象组合成一个索引序列，列出数据和其下标
            # print("当前语句:", line)
            # 遍历lines每一行判断是否为转移语句
            result = re.search(pattern=BasicBlockDivsion.gotoPattern, string=line)  # 匹配GOTO语句
            # print("result:", result)
            if result is not None:
                # print('跳转的目标语句'+result.group(1)+"是入口语句")
                gotolinenum = int(result.group(1))  # 跳转的目标语句的行号
                entryStatements.append(gotolinenum )  # 跳转的目标语句是入口语句
                # 判断是否到达程序结束语句
                if i < len(lines):                 # 若未到达结束语句
                    # 判断本条语句是否为条件转移语句
                    res = re.search(pattern=BasicBlockDivsion.ifPattern, string=line)  # 匹配条件转移语句
                    if res is not None:
                        # print("又由于本句是条件跳转语句,故其后面的相邻语句是入口语句")
                        entryStatements.append(i + 1)  # 条件转移语句后面的相邻语句是入口语句

        new_entryStatements=list(set(entryStatements))      # 去除重复元素
        new_entryStatements.sort()                  # 按顺序排列
        print("入口语句为：")
        print(new_entryStatements)
        print("————————————————————————————")
        return new_entryStatements

    @staticmethod
    def getBasicBlocks(code: str) -> list:

        entrylist = BasicBlockDivsion.find_entry(code)      # 得到入口语句行号
        lines = code.splitlines()  # 按行分割

        basic_blocks = []           # 基本块
        code = []  # 最终的整个程序

        # 若只有一个基本块
        if len(entrylist) == 1:
            name='BB1'
            basic_blocks.append(BasicBlockOptimization(name, lines, 1, len(lines)))
            for member in basic_blocks:
                print("\n基本块划分如下：")
                print(member.name)
                print(member.code)
                print("————————————————————————————")
            return basic_blocks

        # 得到基本块
        index = 1
        for i,entry in enumerate(entrylist[1:], start=1):
            # 对于一个入口语句，先将它所属的基本块 初步划分 为该入口语句到下一条入口语句(不包括下一条入口语句)
            name = 'BB' + str(i)
            print("初步划分：", name,":", index, entry-1)

            # 判断初步划分的块内有无跳转语句
            for j, line in enumerate(lines[index-1:entry-1], start=index):
                # print("当前语句：",j, line)
                result = re.search(pattern=BasicBlockDivsion.gotoPattern, string=line)  # 匹配GOTO语句
                if result is not None:
                    # 若有转移语句，则基本块为该入口语句到转移语句
                    print("初步划分的"+name+"中",j, '是跳转语句，则', j, "应为该块的出口语句")
                    break  # 跳转语句为出口语句
            basic_blocks.append(BasicBlockOptimization(name, lines, index, j))
            index = entry

        # 最后一个基本块为最后一个入口语句到停语句
        endStatement = len(lines)  # 程序的结束语句行号
        name = 'BB' + str(i+1)
        print("最后一个基本块：", name, ":", index,  endStatement)
        basic_blocks.append(BasicBlockOptimization(name, lines, index, endStatement))

        for member in basic_blocks:     # 删去源程序中未被纳入某一基本块中的语句
            bb_code = '\n'.join(map(str, member.code))  # code列表转换成字符串，按换行符拼接
            code.append(bb_code)
        # 重新设置每个基本快的源程序
        for bb in basic_blocks:
            bb.set_source_code(code)

        # 显示
        print("\n基本块划分如下：")
        for member in basic_blocks:
            print(member.name)
            print(member.code)
        print("————————————————————————————")

        return basic_blocks


# if __name__ == '__main__':
#     # 测试案例
#     f = open("E:/桌面/编译课设/源码/bianyikeshe_LocalOptimization/demo.txt", 'r')
#     text = f.read()
#     f.close()
#     bbs = BasicBlockDivsion.getBasicBlocks(text)
#
#     # print("局部优化过程:")
#     # for bb in bbs:
#     #     print("———————————————", bb.name, "———————————————————")
#     #     bb.optimization()
#     print("DAG优化过程:")
#     for bb in bbs:
#         print("******", bb.name, "******" )
#         code = bb.get_code()
#         if len(code) == 0:
#             continue
#         dag = DAG(code.splitlines())

