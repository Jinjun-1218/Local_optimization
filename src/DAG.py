#\s*：匹配任意数量的空白字符（包括空格、制表符等）
#(\w+)：匹配一个或多个字母、数字或下划线，并将这部分作为一个捕获组，代表变量名
#(.+)$：匹配一个或多个任意字符，直到行尾，并将其作为一个捕获组，代表赋值的表达式。$确保匹配到行的末尾
"""
DAG 算法的实现
需要的数据结构：
1.图结构——记录DAG图，可以使用不严格树形结构
2.变量记录表
3.节点存放表

DAG图构造算法：
对基本块的每一四元式，依次执行：
　　1． 如果NODE（B）无定义，则构造一标记为B的叶结点并定义NODE（B）为这个结点；
　　如果当前四元式是0型，则记NODE（B）的值为n，转4。
　　如果当前四元式是1型，则转2.（1）。
　　如果当前四元式是2型，则：（Ⅰ）如果NODE（C）无定义，则构造一标记为C的叶结点并定义NODE（C）为这个结点，（Ⅱ）转2.（2）。
　　2．
　　（1） 如果NODE（B）是标记为常数的叶结点，则转2.（3），否则转3.（1）。
　　（2） 如果NODE（B）和NODE（C）都是标记为常数的叶结点，则转2.（4），否则转3.（2）。
　　（3） 执行op　B（即合并已知量），令得到的新常数为P。如果NODE（B）是处理当前四元式时 新构造出来的结点，则删除它。如果NODE（P）无定义，则构造一用P做标记的叶结点n。置NODE（P）＝n，转4.。
　　（4） 执行B　op　C(即合并已知量)，令得到的新常数为P。如果NODE（B）或NODE（C）是处理当前四元式时新构造出来的结点，则删除它。如果NODE（P）无定义，则构造一用P做标记的叶结点n。置NODE（P）＝n，转4.。
　　3．
　　（1） 检查DAG中是否已有一结点，其唯一后继为NODE（B），且标记为op（即找公共子表达式）。如果没有，则构造该结点n，否则就把已有的结点作为它的结点并设该结点为n，转4.。
　　（2） 检查DAG中是否已有一结点，其左后继为NODE（B），右后继为NODE（C），且标记为op(即找公共子表达式)。如果没有，则构造该结点n，否则就把已有的结点作为它的结点并设该结点为n。转4.。
　　4．
　　如果NODE（A）无定义，则把A附加在结点n上并令NODE（A）＝n；否则先把A从NODE（A）结点上的附加标识符集中删除（注意，如果NODE（A）是叶结点，则其标记A不删除），把A附加到新结点n上并令NODE（A）＝n。转处理下一四元式。
"""

import re


class DAGNode:
    """
    DAG 图节点
    """

    def __init__(self) -> None:
        self.__parent_node = set()  # 记录父节点
        self.__child_nodes = []  # 记录子节点列表
        self.__value = None  # 节点标记:记录值（唯一变量名字|常数）
        self.__var = set()  # 附加标识符：变量名字表
        self.__op = None  # 子节点间的操作符

    @property
    def parent(self):
        return self.__parent_node

    def add_parent(self, value):
        self.__parent_node.add(value)

    def add_children(self, children):
        self.__child_nodes.append(children)

    @property
    def child(self):
        return self.__child_nodes

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def vars(self):
        return self.__var

    def remove_var(self, var):
        if var in self.vars:
            self.__var.remove(var)

    def add_var(self, var):
        self.__var.add(var)

    def get_op(self):
        return self.__op

    def set_op(self, value):
        self.__op = value

    def __repr__(self) -> str:
        parents = list(self.__parent_node)
        parents = [str(i) for i in parents]#将parents列表每个元素转换为字符串形式
        parents = ' '.join(parents)#将parents列表每个字符串元素合并成一个单一字符串，元素之间用空格分隔

        children = list(self.__child_nodes)
        children = [str(i) for i in children]
        children = ' '.join(children)

        vars_ = list(self.__var)
        vars_ = ' '.join(vars_)

        result = 'var:' + vars_ + '\n'
        result += 'parent:' + parents + '\n'
        result += 'children:' + children + '\n'
        if self.__op is not None:
            result += 'op:'+ self.get_op()+ '\n'
        if self.__value is not None:
            result += 'value:' + str(self.__value) + '\n'
        return result


class DAG:

    assignmentPattern = re.compile(r'\s*(\w+)\s*:=\s*(.+)$')  # 变量赋值语句正则
    zero_type = re.compile(r'^\s*(\w+\.?\w*)\s*$')  # 0型四元式正则，形如 A:=B
    first_type = re.compile(r'^\s*([*\-+/])\s*(\w+\.?\w*)\s*$')  # 1型四元式正则，形如 A:= op B
    second_type = re.compile(r'^\s*(\w+\.?\w*)\s*([*\-+/])\s*(\w+\.?\w*)\s*')  # 2型四元式正则，形如 A:= B op C
    node_type = ["number", "unknown", "variable"]

    code = []

    def __init__(self, code: list):

        self.node_list = []  # type: list[DAGNode]
        self.final_code = []    # 化简后的代码
        self.code = code
        self.var_table = {}  # 记录变量所在的节点索引及引用情况 str:([],bool)

        self.create_dag()   # 构建DAG图
        self.rebuild()      # 生成优化序列
        print("——————DAG节点如下：——————")
        for index, node in enumerate(self.node_list):
            print(index)
            print(node)
        result = self.get_final_code()

        print("优化后的语句序列如下：")
        print(result)
        print("——————————————————")

    def create_dag(self):
        """
        构造DAG图
        """
        for line in self.code:
            print("\n****当前node_list：")
            for index, node in enumerate(self.node_list):
                print(index)
                print(node)

            result = re.search(self.assignmentPattern, line)    # 匹配赋值语句
            if result is not None:
                var = result.group(1)
                value = result.group(2)
                print("\n当前", line, '是赋值语句，var = {var},value={value}'.format(var=var, value=value))

                # 判断该四元式是否是 0 型 A := B
                res0 = re.match(self.zero_type, value)
                if res0 is not None:
                    value = res0.group(1)
                    print("该四元式是0型,value="+value)
                    # 处理node(value)
                    (type_, index, flag) = self.name(value)
                    print(value+'：类型 = {type_}, 索引 = {index}，是否新构建={flag}'.format(type_=type_, index=index, flag=flag))
                    # 处理node(var)
                    self.node_list[index].add_var(var)  # 在值为value的节点的标签中添加一个变量名var
                    self.delete_no_use_var(var, index)  # 判断是否将变量名从原来的附加信息中删除
                    continue

                # 判断该四元式是否是 1 型 A := op B
                else:
                    res1 = re.match(self.first_type, value)
                    if res1 is not None:
                        op = res1.group(1)
                        op_num = res1.group(2)
                        print("该四元式是1型", op, op_num)
                        self.change_var_reference(op_num)#标记op_num已经被引用

                        (type_, index_, flag_) = self.name(op_num)  # 判断操作数类型
                        print(op_num + '：类型 = {type_}, 索引 = {index_}，是否新构建={flag_}'.format(type_=type_,index_=index_, flag_=flag_))

                        if type_ == self.node_type[0]:
                            print("op_num为常数")
                            new_value = eval(op + op_num)   # 计算
                            print(str(new_value))
                            if flag_ is True:
                                # op_num 是处理当前语句新构造的节点，应删去
                                print(op_num + "是处理当前语句新购造出的节点")
                                self.node_list.pop(index_)

                            (type_new_value, index, flag_new_value) = self.name(str(new_value))
                            self.node_list[index].add_var(var)
                            self.delete_no_use_var(var, index)

                        else:
                            if type_ == self.node_type[2]:
                                print("op_num为变量")
                                temp_value = self.node_list[index_].value#获取op_num对应节点的值
                                (type_temp_value, index_temp_value, flag_temp_value) = self.name(temp_value)
                                if type_temp_value == self.node_type[0]:  # 变量存储的是一个数值
                                    print(op_num+"存储的是一个数值")
                                    final_value = eval(op + temp_value)
                                    print(str(final_value))
                                    (type_final_value, index_final_value, flag_final_value) = self.name(str(final_value))
                                    self.node_list[index_final_value].add_var(var)
                                    self.delete_no_use_var(var, index_final_value)

                                else:
                                    print(op_num + "存储的是一个未知数")
                                    temp_node = DAGNode()
                                    temp_node.add_var(var)
                                    temp_node.add_children(index_)
                                    temp_node.set_op(op)

                                    index = self.find_same(temp_node)
                                    if index >= 0:
                                        # 找到相同的节点，在该节点的附加信息中加上var
                                        self.node_list[index].add_var(var)
                                        self.delete_no_use_var(var, index)
                                    else:
                                        # 没找到，则将新构建的temp_node加入节点列表
                                        self.node_list.append(temp_node)
                                        temp_node_index = self.node_list.index(temp_node)
                                        self.delete_no_use_var(var, temp_node_index)
                                        self.node_list[index_].add_parent(temp_node_index)

                    # 判断该四元式是否是 2 型 A := B op C
                    else:
                        res2 = re.match(self.second_type, value)
                        if res2 is not None:
                            op = res2.group(2)
                            values = [res2.group(1), res2.group(3)]
                            print("该四元式是2型,var = {var},op_num_1={v1}, op={op}, op_num_2={v2}".format(var=var, v1=values[0], v2=values[1], op=op))

                            # values 中的变量被引用，更新变量引用表
                            self.change_var_reference(values[0])
                            self.change_var_reference(values[1])

                            (type_1, index_1, flag_1) = self.name(values[0])
                            print(values[0]+'：类型 = {type_1}, 索引 = {index_1}，是否新构建={flag_1}'.format(type_1=type_1,index_1=index_1, flag_1=flag_1))
                            (type_2, index_2, flag_2) = self.name(values[1])
                            print(values[1] + '：类型 = {type_2}, 索引 = {index_2}，是否新构建={flag_2}'.format(type_2=type_2,index_2=index_2, flag_2=flag_2))

                            # node(values[0])和node(values[1])的标记都为常数
                            if {type_1, type_2} == {self.node_type[0], self.node_type[0]}:
                                print("两个常数")
                                new_value = eval(values[0] + op + values[1])
                                print(str(new_value))
                                # 若两节点都是标记为常数的节点，如果是处理当前语句新购造出的节点，则删除它
                                if flag_1 is True:
                                    print(values[0] + "是处理当前语句新购造出的节点")
                                    self.node_list.pop(index_1)
                                if flag_2 is True:
                                    print(values[1] + "是处理当前语句新购造出的节点")
                                    self.node_list.pop(index_2)
                                (type_, index, flag) = self.name(str(new_value))
                                print(str(new_value) + '：类型 = {type_}, 索引 = {index}，是否新构建={flag}'.format(
                                    type_=type_, index=index, flag=flag))
                                self.node_list[index].add_var(var)
                                self.delete_no_use_var(var, index)

                            # node(values[0])和node(values[1])的标记为一个常数一个变量
                            elif {type_1, type_2} == {self.node_type[0], self.node_type[2]}:
                                # 一个数值一个变量（变量可能取值）
                                print("一个数值一个变量")
                                number_index, variable_index = -1, -1
                                if type_1 == self.node_type[2]:     # type_1是变量
                                    number_index, variable_index = index_2, index_1
                                else:
                                    number_index, variable_index = index_1, index_2

                                # 判断变量的取值
                                temp_value = self.node_list[variable_index].value
                                (type_temp_value, index_temp_value, flag_temp_value) = self.name(temp_value)

                                if type_temp_value == self.node_type[0]:  # 变量存储的是一个数值
                                    final_value = eval(temp_value + op + self.node_list[number_index].value)
                                    print(temp_value + op + self.node_list[number_index].value+"="+str(final_value))

                                    # 两节点都是标记为常数的节点，如果是处理当前语句新购造出的节点，则删除它
                                    if number_index == index_1:
                                        if flag_1 is True:
                                            print(values[0] + " 是处理当前语句新购造出的节点")
                                            self.node_list.pop(index_1)
                                    else:
                                        if flag_2 is True:
                                            print(values[1] + " 是处理当前语句新购造出的节点")
                                            self.node_list.pop(index_2)

                                    (type_, index, flag) = self.name(str(final_value))
                                    print(str(final_value) + '：类型 = {type_}, 索引 = {index}，是否新构建={flag}'.format(
                                        type_=type_, index=index, flag=flag))
                                    self.node_list[index].add_var(var)
                                    self.delete_no_use_var(var, index)

                                else:  # 变量存储的是一个未知数
                                    temp_node = DAGNode()
                                    temp_node.add_var(var)
                                    temp_node.add_children(index_1)
                                    temp_node.add_children(index_2)
                                    temp_node.set_op(op)

                                    index = self.find_same(temp_node)#查找是否存在相同的结点
                                    if index >= 0:
                                        self.node_list[index].add_var(var)
                                        self.delete_no_use_var(var, index)
                                    else:
                                        self.node_list.append(temp_node)
                                        temp_node_index = self.node_list.index(temp_node)
                                        self.delete_no_use_var(var, temp_node_index)
                                        self.node_list[index_1].add_parent(temp_node_index)
                                        self.node_list[index_2].add_parent(temp_node_index)

                            elif {type_1, type_2} == {self.node_type[2], self.node_type[2]}:
                                print("两个变量")
                                if self.node_list[index_1].value == self.node_type[0] and self.node_list[index_2].value == self.node_type[0]:
                                    print("op_num_1和op_num_2存储的都是数值")
                                    final_value = eval(self.node_list[index_1].value + op + self.node_list[index_2].value)
                                    print("最终结果",str(final_value))
                                    (type_, index, flag) = self.name(str(final_value))
                                    self.node_list[index].add_var(var)#将结果变量添加到结果节点
                                    self.delete_no_use_var(var, index)

                                else:
                                    print("存在未知数")
                                    temp_node = DAGNode()
                                    temp_node.add_var(var)
                                    temp_node.add_children(index_1)
                                    temp_node.add_children(index_2)
                                    temp_node.set_op(op)
                                    index = self.find_same(temp_node)
                                    if index >= 0:
                                        self.node_list[index].add_var(var)
                                        self.delete_no_use_var(var, index)
                                    else:
                                        self.node_list.append(temp_node)
                                        temp_node_index = self.node_list.index(temp_node)
                                        self.delete_no_use_var(var, temp_node_index)
                                        self.node_list[index_1].add_parent(temp_node_index)
                                        self.node_list[index_2].add_parent(temp_node_index)

                            else:  # 存在未知数
                                print("存在未知数")
                                temp_node = DAGNode()
                                temp_node.add_var(var)
                                temp_node.add_children(index_1)
                                temp_node.add_children(index_2)
                                temp_node.set_op(op)
                                index = self.find_same(temp_node)
                                if index >= 0:
                                    # 在node_list找到op和子节点都相同的节点，直接在该节点的附加信息中加上var
                                    self.node_list[index].add_var(var)
                                    # 判断var是否在其他节点的附加信息中，如果在就删掉
                                    self.delete_no_use_var(var, index)
                                else:
                                    self.node_list.append(temp_node)
                                    temp_node_index = self.node_list.index(temp_node)
                                    self.delete_no_use_var(var, temp_node_index)
                                    self.node_list[index_1].add_parent(temp_node_index)
                                    self.node_list[index_2].add_parent(temp_node_index)

    def name(self, var: str) -> tuple:    # return: (参数类型， 参数索引，是否为新构建的节点)
        """
        判断参数所属类型（数值/未知数/变量）,并返回与其关联的节点索引
        node_type[0]="number", 该参数为常数
        node_type[1]="unknown", 该参数为变量，但不存在于某个节点的附加标识符中，为未知数
        node_type[2]="variable"，该参数为变量，且存在于某个节点的附加标识符中
        """
        result = []
        if re.match(r'^\s*(\d+.?\d*)\s*$', var):
            # 是数值
            # print(var+"是数值")
            result.append(self.node_type[0])
            for index, node in enumerate(self.node_list):   # 判断节点列表中是否已有值为常数var的节点
                if node.value == var:
                    # print(index, "node:\n", node)
                    result.append(index)
                    result.append(False)
                    break
            else:           # 节点列表中不存在此节点，则新增一个节点
                temp_node = DAGNode()
                temp_node.value = var
                self.node_list.append(temp_node)
                result.append(self.node_list.index(temp_node))
                result.append(True)
            return tuple(result)

        if re.match(r'^\s*([a-zA-Z]\w*)\s*$', var):
            # 不是数值，那么一定是一个变量或者是一个未知数
            for index, node in enumerate(self.node_list):
                if var in node.vars:
                    #  如果存在于某个节点的变量列表里，那么是变量
                    # print(var + "是变量")
                    result.append(self.node_type[2])
                    result.append(index)
                    result.append(False)
                    return tuple(result)
            # 不是变量，那么一定是未知数
            for index, node in enumerate(self.node_list):
                # print(var + "是未知数")
                if node.value == var:  # 未知数已存在
                    result.append(self.node_type[1])
                    result.append(index)
                    result.append(False)
                    break
            else:
                temp_node = DAGNode()
                temp_node.value = var
                self.node_list.append(temp_node)
                result.append(self.node_type[1])
                result.append(self.node_list.index(temp_node))
                result.append(True)
            return tuple(result)

    def delete_no_use_var(self, var: str, index: int):

        print("待处理变量:", var,index)
        print("var_table:", self.var_table)
        if var in self.var_table.keys():  # 如果变量出现过
            print(var+"出现过:")
            if self.var_table[var][1] is False:  # 上次赋值后还没有被引用过,从之前的附加标签中删除
                print(var + "没被引用过")
                print(var+"的节点信息：\n", self.node_list[self.var_table[var][0][-1]])
                self.node_list[self.var_table[var][0][-1]].remove_var(var)  # 从节点列表删除上个信息
                print(self.node_list[self.var_table[var][0][-1]])
                self.var_table[var][0].pop(-1)  # 更新var_table
                self.var_table[var][0].append(index)
                # print("var_table:", self.var_table)

            else:  # 被引用过， 则直接添加索引， 同时修改引用标志量
                print(var+"被引用过")
                self.var_table[var][1] = False  # var被引用过后又重新赋值，所以重新修改引用标志量
                self.var_table[var][0].append(index)
                # print("var_table:", self.var_table)

        else:  # 还没有出现过
            print(var+"还没有出现过")
            self.var_table[var] = [[index], False]

    def change_var_reference(self, var: str):
        if var in self.var_table.keys():
            self.var_table[var][1] = True#标记变量已经被引用
    # 寻找相同的节点
    def find_same(self, mynode: DAGNode) -> int:
        mynode.child.sort()
        for index, node in enumerate(self.node_list):
            node.child.sort()
            if node.child == mynode.child and node.get_op() == mynode.get_op():
                print(node.child, ' = ', mynode.child)
                print(node.get_op(), ' = ', mynode.get_op())
                return index
        return -1

    # 由DAG生成优化序列
    def rebuild(self):
        for index, node in enumerate(self.node_list):
            if len(node.vars) == 0:
                continue
            else:
                templist = list(node.vars)
                templist.sort()
                if len(templist) != 0 and node.value is not None:  # var := 数值  |  var := 未知数
                    for var in templist:
                        self.final_code.append(var + ' := ' + node.value)
                    continue

                if len(templist) != 0 and node.get_op() is not None and node.child != []:#计算结点
                    values = []
                    if len(node.child) == 2:
                        if self.node_list[node.child[0]].value is not None:
                            values.append(self.node_list[node.child[0]].value)
                        else:
                            values.append(list(self.node_list[node.child[0]].vars)[-1])

                        if self.node_list[node.child[1]].value is not None:
                            values.append(self.node_list[node.child[1]].value)
                        else:
                            values.append(list(self.node_list[node.child[1]].vars)[-1])

                        self.final_code.append(templist[0] + ' := ' + values[0] + node.get_op() + values[1])
                        for var in templist[1:]:
                            self.final_code.append(var + ' := ' + templist[0])

                    else:
                        # 1型
                        if self.node_list[node.child[0]].value is not None:
                            values.append(self.node_list[node.child[0]].value)
                        else:
                            values.append(list(self.node_list[node.child[0]].vars)[-1])
                        self.final_code.append(templist[0] + ' := ' + node.get_op() + values[0])
                        for var in templist[1:]:
                            self.final_code.append(var + ' := ' + templist[0])

    def get_final_code(self):
        return '\n'.join(self.final_code)


if __name__ == '__main__':
    pass
