
"""
在每一个基本块中实现：合并已知量、删除多余运算和删除无用赋值三种局部优化
"""

import re


class VariableTable():#变量表

    def __init__(self):
        """
        vars中每个变量的记录record内容如下:
        变量名 record[0]
        变量的值 record[1]
        引用该变量的行 record[2]    type:list
        该变量出现的行号列表 record[3]    type:list
        最新给该变量赋值的行 record[4]
        """
        self.vars = []  # type: list[list]#列表，存储变量记录

    # 查询某一变量是否存在于变量表中
    def find_var(self, var: str) -> (bool, list):    #var为字符串参数，返回状态(布尔值)，和结果(list)

        for record in self.vars:
            if var.__eq__(record[0]):       #比较变量名
                return True, record
        else:
            #未找到
            return False, None

    # 新增变量记录
    def add_var(self, var: str):
        self.vars.append([var, None, None, [], 1000])
     #其中var变量名 None 表示变量值和引用行号未定义，[] 表示变量出现的行号列表，1000 表示最新赋值的行号。
    # 修改变量状态 record[1-4]
    def change_var_status(self, var: str, linenumber: int, **kwargs):
        """
        :param var: 变量名
        :param linenumber: 变量出现的行号
        :param **kwargs:任意数量的关键字参数
        :keyword value: 变量的值
        :keyword referenced_line_number: 被引用的行号
        :keyword lastest_assign_line: 最新被赋值的行
        :return: None
        """
        keys = kwargs.keys()
        for index, record in enumerate(self.vars):

            if var.__eq__(record[0]):
                # print("变量:", var, "本次出现的行号：", linenumber, "\n变量表已有记录:", "索引:", index, ";变量名：" + record[0], ";值：",
                #       record[1], ";出现的行号列表", record[3])
                if linenumber not in record[3]:
                    # print("修改出现行号列表record[3]")
                    record[3].append(linenumber)

                if 'value' in keys:         # 传入的关键字参数中有变量值
                    # print("修改变量值record[1]")
                    record[1] = kwargs['value']     # 向记录中写入变量值

                if 'referenced_line_number' in keys:    # 传入的关键字参数中有引用的行号
                    # print("修改引用行号列表record[2]")
                    if record[2] is None:  # 如果为空则新建一个列表
                        record[2] = []
                        record[2].append(kwargs['referenced_line_number'])
                    else:
                        record[2].append(kwargs['referenced_line_number'])

                if 'lastest_assign_line' in keys:
                    record[4] = kwargs['lastest_assign_line']
                # print('{var}:{record}'.format(var=self.__vars[index][0], record=self.__vars[index]))

    # 获取变量表的内容
    def get_vars(self):
        return self.vars

    # 清空变量表
    def clear(self):
        self.vars = []


class BasicBlockOptimization:

    assignmentPattern = re.compile(r'\s*(\w+)\s*:=\s*(.+)$')  # 变量赋值语句正则
    variablePattern = re.compile(r'\b[a-zA-Z]\w*\b')  # 变量名正则
    valuePattern = re.compile(r'^\s*\d+\.?\d*\s*$')  # 匹配出现的数值（数字或者字符）
    ifPattern = re.compile(r'.*IF\s*(.+)\s*GOTO')  # IF语句正则
    line_numberPattern = re.compile(r'\s*[(](\d+)[)]\s*')  # 代码行号正则

    def __init__(self, name, code: list, start, end):
        self.name = name  # 名称
        self.start = start  # 基本块起始行号
        self.end = end  # 基本块结束行号
        self.code = [line for line in code[start - 1:end]]  # 记录基本块的代码 list[起始索引：结束索引]：切片时包含起始索引元素，不包含结束索引元素
        self.var_table = VariableTable()  # 基本块内变量的使用情况
        self.source_code = code  # 完整源程序

    # 将code转换成字符串，按换行符拼接，并按行分割得到列表
    def set_source_code(self, code: list):
        self.source_code = '\n'.join(map(str, code)).splitlines()
        # print("\n基本块划分后程序如下：")
        # print(self.source_code)
        # print("\n")

    def statistic_vars_referenced_line_list(self):
        """
        遍历整个源程序，将所有变量的引用情况统计到变量表中
        """
        for index, line in enumerate(self.source_code, start=1):
            # print(index, line)
            result = re.search(self.assignmentPattern, line)  # 匹配赋值语句
            if result is not None:
                value = result.group(2)  # 值
                # print("本句是赋值语句,值为：", value)
                # 寻找值value中是否有其他变量
                vars_in_value = re.findall(self.variablePattern, value)  # 匹配值中的变量
                #它返回string中所有与pattern匹配的全部字符串,返回形式为列表，
                # 如果pattern中含有分组，返回分组的匹配结果。如果有pattern中有多个分组，则返回元组列表。
                if vars_in_value:
                    vars_in_value = list(set(vars_in_value))  # 去重
                    # print("变量值:", value, "中有其他变量：",vars_in_value )
                    # print("***************************************************")
                    for var in vars_in_value:
                        # 有其他变量，先看变量表中有没有该变量
                        ret, _ = self.var_table.find_var(var)
                        if ret:
                            # 如果该变量在表中，直接修改其引用列表
                            self.var_table.change_var_status(var, index, referenced_line_number=index)
                        else:
                            # 如果变量不在表中，向变量表中添加新变量
                            self.var_table.add_var(var)
                            self.var_table.change_var_status(var, index, referenced_line_number=index)#被引用行号
                    # print("***************************************************")
            # 不是赋值语句
            result = re.search(self.ifPattern, line)  # 匹配IF语句
            # print(result.group(1),type(result.group(1)))
            if result is not None:
                # print("本句是IF语句")
                # print(result.group(1))
                # 寻找在IF语句中引用的变量
                vars_in_if_statement = re.findall(self.variablePattern, result.group(1))
                if vars_in_if_statement:
                    vars_in_if_statement = list(set(vars_in_if_statement))  # 去重
                    # print("IF语句中引用的变量：", vars_in_if_statement)
                    # print("***************************************************")
                    for var in vars_in_if_statement:
                        ret, _ = self.var_table.find_var(var)
                        if ret:
                            # 如果变量在表中出现过
                            self.var_table.change_var_status(var, index, referenced_line_number=index)
                        else:
                            # 如果变量没有在表中出现过
                            self.var_table.add_var(var)
                            self.var_table.change_var_status(var, index, referenced_line_number=index)

    def statistic_variables(self):
        """
        对每一基本块，统计变量表中变量的其他表项
        """
        for index, line in enumerate(self.code, start=self.start):
            # print(index, line)
            result = re.search(self.assignmentPattern, line)  # 匹配赋值语句
            if result is not None:
                # print("分析：\n本句是赋值语句")
                var = result.group(1)  # 被赋值的变量
                value = result.group(2)  # 值

                # 对被赋值变量var的处理:
                ret, _ = self.var_table.find_var(var)  # 查找该变量是否已存在于变量表
                if not ret:
                    # 如果变量还未出现在变量表中
                    self.var_table.add_var(var)  # 变量表中新增一变量记录
                    self.var_table.change_var_status(var, index, value=value)  # record[3]中添加index，record[1]设为value,
                    self.var_table.change_var_status(var, index, lastest_assign_line=index)
                else:
                    self.var_table.change_var_status(var, index, value=value)
                    self.var_table.change_var_status(var, index, lastest_assign_line=index)
        # print("变量表如下：")
        # self.print_var_table()

    def delete_no_use_line(self, no_use_linenumber: int):#删除指定的无用赋值语句

        for bb_index, bb_line in enumerate(self.code):
            res = re.search(self.line_numberPattern, bb_line)#搜索行号
            if res:
                if res.group(1) == str(no_use_linenumber):#res.group(1)第一个捕获组，数字
                    break
        print(self.code[bb_index]+"为无用赋值语句")
        no_use_line = self.code[bb_index]

        result = re.search(self.assignmentPattern, no_use_line)  # group（1）字母数字字符组合，变量名
        value = result.group(2)# 得到该赋值语句的值
        vars_in_value = re.findall(self.variablePattern, value)  # 寻找值中的变量
        if vars_in_value:
            vars_in_value = list(set(vars_in_value))  # 去重
            for var in vars_in_value:
                ret, var_record = self.var_table.find_var(var)
                if ret:
                    # print(var_record[0] + "记录更新前", var_record)
                    # print(var_record[3].index(no_use_linenumber))
                    var_record[3].pop(var_record[3].index(no_use_linenumber))  # 从值中变量的出现的行号列表中删除该行记录
                    var_record[2].pop(var_record[2].index(no_use_linenumber))# 从引用行号列表中删除该行记录
                    # print(var_record[0] + "记录更新后", var_record)

        self.code.pop(bb_index)  # 将基本块中的无用赋值删去

        for s_c_index, s_line in enumerate(self.source_code):  # 遍历整个源代码，找到与无用赋值语句相同的行，全部删除
            if s_line.__eq__(no_use_line):
                # print("源码：",s_c_index, self.source_code[s_c_index])
                break
        self.source_code.pop(s_c_index)  # 将源码中相应的无用赋值删去

    def del_unreferenced_var(self) -> bool:
        """
        删除无用赋值：
        遍历变量表，检查每一个变量的被引用列表record[2]是否为空
        若某一变量的record[2]为空，则该变量未被引用，若赋值语句有多行，则只需保留最新赋值，删除其他无用赋值语句，同时删除表中的相关记录
        若某一变量的record[2]不为空，若某一变量的两次赋值之间，该变量没有没引用，则前一次赋值为无用赋值，应删除，同时删除表中的相关记录
        """
        vars_table = self.var_table.get_vars()
        flag = 0       # flag =1 表示此基本块存在无用赋值
        assign_statements = []#用于无用赋值语句检查
        for index, record in enumerate(vars_table):#遍历每个变量的被引用列表是否为空
            assign_statements.clear()
            # print("index:",index,"\n变量表：",vars_table[index])

            if record[2] is None or len(record[2]) == 0:
                # 该变量从未被引用
                if len(record[3]) > 1:
                    # 如果有多个赋值行，则一定存在无用赋值
                    record[3].sort()
                    for i,line_number in enumerate(record[3][:-1]):
                        self.delete_no_use_line(line_number)
                        record[3].pop(i)
                        record[4]=record[3][-1]
                        flag = 1
                    continue

            else:
                # 该变量被引用过
                for line_number in record[3]:
                    if line_number not in record[2]: # 该行号不在引用列表，则该句可能为赋值语句
                        # 遍历基本块的每一行，找到该行号对应的代码
                        # print(line_number)
                        for i, bb_line in enumerate(self.code):
                            if self.get_line_number(bb_line) == str(line_number):
                                break
                        # print(i, self.code[i])
                        result = re.search(self.assignmentPattern, self.code[i])
                        if result:
                            assign_statements.append(line_number)

                # print(assign_statements)
                assign_statements.sort()
                # print(assign_statements)
                if len(assign_statements) > 1:#检查列表中是否有多于一个的赋值行号。如果有，继续进行无用赋值的检查
                    for k, assign_line_number in enumerate(assign_statements[:-1]):#循环中不包括最后一条语句
                        for referenced_line_number in record[2]:
                            if assign_statements[k] < referenced_line_number < assign_statements[k+1]:
                                #如果引用行号位于两个连续的赋值行号之间，那么当前的赋值行号 assign_statements[k] 不是无用的
                                print(assign_statements[k], "<",referenced_line_number,"<" , assign_statements[k+1])
                                continue
                            else:
                                print(assign_statements[k])
                                self.delete_no_use_line(assign_statements[k])
                                record[3].pop(record[3].index(assign_statements[k]))
                                flag = 1
        if flag == 0:
            print("此基本块不存在无用赋值")
            return False
        else:
            return True

    def merge_knowned_member(self)-> bool:
        """
        合并已知量： a := 3*7 + b  ==>  a := 21 + b  ,如果b已知，则可做进一步值的化简
        1.对基本块内的每一行，判断是否为赋值语句
        2.若是赋值语句，判断等号右边是数值还是表达式
        3.若等号右边是表达式，提取表达式中的所有变量
        4.对表达式中的每一个变量，查找其在变量赋值表中是否有数值，若有数值，用数值替换该变量
        5.计算替换后的表达式，更新代码

        """
        flag = 0
        for i, line in enumerate(self.code):
            # print("\n当前语句：", i, line)
            line_number = int(self.get_line_number(line))

            result = re.search(self.assignmentPattern, line)  # 匹配赋值语句
            if result is not None:  # 是赋值语句，看等号右边是数值还是表达式
                var = result.group(1)
                value = result.group(2)
                # print("变量:" + var, "值：" + value)

                for index, s_line in enumerate(self.source_code):  #  遍历源代码，找到与当前基本块代码行相同的行。
                    if s_line.__eq__(self.code[i]):
                        # print(index, self.source_code[index])
                        break

                number = re.match(self.valuePattern, value)  # 匹配变量所赋的值是否是数值
                if number is None:  # 不是数值，则是表达式
                    vars_in_value = re.findall(self.variablePattern, value)  # 提取所有表达式中的变量
                    if vars_in_value is not None:    # 有变量
                        vars_in_value = list(set(vars_in_value))  # 去重
                        # print("找到的变量：", vars_in_value)

                        for var_in_value in vars_in_value:
                            # print("当前待处理的变量：", var_in_value)
                            ret, record = self.var_table.find_var(var_in_value)#对于表达式中的每个变量，检查变量表中是否有对应的数值
                            if ret and record[1] is not None:
                                temp_value = record[1]

                                if re.match(self.valuePattern, temp_value):
                                    # 如果变量是数值
                                    value1 = value.replace(var_in_value, temp_value)        # 用数值替换变量
                                    self.code[i] = self.code[i].replace(value, value1)#更新基本块代码和源代码
                                    self.source_code[index] = self.code[i]
                                    # print(self.code[i])
                                    # exec(var_in_value + '=' + temp_value)  # 直接替换成值
                                    # 更新变量表record:
                                    record[3].pop(record[3].index(line_number))  # 从出现的行号列表中删除该行记录
                                    record[2].pop(record[2].index(line_number))  # 从引用列表中删除该行记录
                                    # print("flag = 1")
                                    flag = 1

                                else:
                                    if re.match(re.compile(r'^\s*[a-zA-Z]*\s*$'),temp_value) is not None: # 变量的值是变量
                                        print(var_in_value+"的值为"+temp_value)
                                        value1 = value.replace(var_in_value, temp_value)  # 将变量改成变量的值
                                        self.code[i] = self.code[i].replace(value, value1)
                                        self.source_code[index] = self.code[i]
                                        # print("flag = 1")
                                        flag = 1
                                        record[3].pop(record[3].index(line_number))  # 从出现的行号列表中删除该行记录
                                        record[2].pop(record[2].index(line_number))  # 从引用列表中删除该行记录
                                        ret, temp_value_record = self.var_table.find_var(temp_value)
                                        if ret:
                                            temp_value_record[3].append(temp_value_record[3].index(line_number))
                                            temp_value_record[2].append(temp_value_record[2].index(line_number))

                    result = re.search(self.assignmentPattern, self.code[i])  # 匹配赋值语句
                    if result is not None:  # 是赋值语句，看等号右边是数值还是表达式
                        value = result.group(2)
                        res = re.findall(self.variablePattern, value)
                        if len(res) == 0:        # 纯数值表达式，可以进行计算
                            new_value = eval(value)#计算完之后更新代码
                            # print('**计算后的表达式为:', new_value)
                            self.code[i] = self.code[i].replace(value, str(new_value))
                            self.source_code[index] = self.code[i]
                            print(line, "合并已知量后为：" + self.code[i])
                            self.var_table.change_var_status(var, line_number, value=str(new_value))

                        else:
                            self.var_table.change_var_status(var, line_number, value=str(value))

        if flag == 0:
            print("此基本块不需要合并已知量")
            return False
        else:
            return True

    def get_line_number(self, line):
        res = re.search(self.line_numberPattern, line)
        if res:
            return res.group(1)
        else:
            return None

    def del_redundant_operations(self) -> bool:
        """
        删除多余运算
        1.从基本块第二行开始，判断是不是赋值语句
        2.若是赋值语句，看等号右边的值中是否有变量
        3.若值中有变量，依次与基本块内该行之前的语句比较，判断是否满足多余运算的条件
        4.若是多余运算，则替换原来的值，并修改变量表中的相关记录
        """
        flag = 0
        for i, line in enumerate(self.code[1:], start=1):   # 基本块的第一行不可能是多余运算
            # print("\n***当前语句：", i, line)
            result = re.search(self.assignmentPattern, line)    # 找赋值语句
            if result is not None:
                var = result.group(1)
                value = result.group(2)
                assign_line_num = int(self.get_line_number(line))
                vars_in_value = re.findall(self.variablePattern, value)  # 找值中的变量
                # print(vars_in_value)
                if len(vars_in_value) == 0:  # 如果值中不存在变量则返回
                    continue

                for j, cmp_line in enumerate(self.code[:i]):    # 找的是当前语句前面的赋值语句
                    # print("比较：", j, cmp_line)
                    cmp_line_result = re.search(self.assignmentPattern, cmp_line)
                    if cmp_line_result is not None:    # 如果是赋值语句
                        cmp_line_var = cmp_line_result.group(1)
                        cmp_line_value = cmp_line_result.group(2)
                        cmp_assign_line_num = int(self.get_line_number(cmp_line))
                        if value.replace(' ', '').__eq__(cmp_line_value.replace(' ', '')):  # 去掉空格比较两变量的值，若相等则可能是多余运算
                            # print(value.replace(' ', ''), "=", cmp_line_value.replace(' ', ''))
                            temp_var = cmp_line_var

                            for var_in_value in vars_in_value:       # 对值中的每个变量进行比较，如果所有变量在比较行和当前行之间没有被重新赋值，则认为是多余运算
                                sign = 1
                                ret, var_in_value_record = self.var_table.find_var(var_in_value)
                                # print("var_in_value_record", var_in_value_record)
                                if var_in_value_record[4] == 1000:
                                    # 一直未赋值
                                    continue
                                else:
                                    for number in var_in_value_record[3]:
                                        if var_in_value_record[4] != 1000 and number not in var_in_value_record[2]:
                                            # 该变量被赋值而不是被引用
                                            if cmp_assign_line_num < number < assign_line_num:
                                                # 两相同表达式里的变量在两次出现中间被重新赋值了,不符合多余运算条件
                                                # print("比较：", cmp_assign_line_num, number, assign_line_num)
                                                sign = 0
                                                break
                                    else:
                                        # 两相同表达式里的变量在两次出现中间没有重新赋值,符合多余运算条件
                                        sign = 1

                                if sign == 1:       # 该变量满足多余运算条件
                                    continue
                                else:
                                    break   # 有一个变量不满足，则不是多余运算

                            else:
                                # 如果所有变量都满足了，则可以替换 “var := value  ==>  var:=temp_var”
                                flag = 1
                                print(line+"是多余运算")
                                new_line = line.replace(value, temp_var)
                                line_number = int(self.get_line_number(line))
                                print("替换后："+new_line)
                                for index, s_line in enumerate(self.source_code):  # 获得整个源码中该多余运算语句的位置，待后续更新
                                    if s_line.__eq__(self.code[i]):
                                        # print(index, self.source_code[index])
                                        break
                                self.source_code[index] = new_line  # 更新源程序
                                # print("\n源：")
                                # for s_line in self.source_code:
                                #     print(s_line)
                                self.code[i] = new_line     # 更新基本块语句
                                for var_in_value in vars_in_value:
                                    ret, var_in_value_record = self.var_table.find_var(var_in_value)
                                    # print(var_in_value_record)
                                    var_in_value_record[3].pop(var_in_value_record[3].index(line_number))  # 从值中变量的 出现的行号列表中删除该行记录
                                    var_in_value_record[2].pop(var_in_value_record[2].index(line_number))   # 从值中变量的 被引用的行号列表中删除该行记录

                                self.var_table.change_var_status(var, line_number, value=temp_var)  # 更改该变量的值
                                self.var_table.change_var_status(temp_var, line_number, referenced_line_number=line_number)
                                break
        if flag == 0:
            print("此基本块不存在多余运算")
            return False
        else:
            return True

    def print_var_table(self):
        for record in self.var_table.get_vars():
            print(record)

    def print_code(self):
        for code in self.code:
            print(code)

    def get_code(self) -> str:
        result = '\n'.join([code for code in self.code])
        return result

    # 局部优化
    def optimization(self):
        self.var_table.clear()

        print("**以下是统计变量过程：**")
        self.statistic_vars_referenced_line_list()
        self.statistic_variables()

        print("\n**开始合并已知量：**")
        result = self.merge_knowned_member()
        if result:
            print("\n**合并已知量后：**")
            self.print_code()

        print("\n**开始删除多余运算：**")
        result = self.del_redundant_operations()
        if result:
            print("\n**删除多余运算后：**")
            self.print_code()

        print("\n**开始删除无用赋值：**")
        result = self.del_unreferenced_var()
        if result:
            print("\n**删除无用赋值后：**")
            self.print_code()
        # print("变量表：")
        # self.print_var_table()


if __name__ == '__main__':
    pass
