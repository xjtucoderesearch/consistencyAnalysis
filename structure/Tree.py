class Node:
    def __init__(self, char, word, terminal=False, children=None ):
        self.char = char
        self.word = word
        self.children = children or set()
        self.terminal = terminal
        self.nodeset = set()

    def setTerminal(self):
        self.terminal = True


class nameTree:
    def __init__(self, node=Node):
        self.node = node
        self.mid = self.node(None, 0, '')

    def init(self, a):
        self.insert(a)

    def insert(self, item, id):
        bn = self.mid
        for index, j in enumerate(item):
            # traverse the children, if the item in the children, needn't add the item in the children
            for child in bn.children:
                if j == child.char:
                    if index == item.__len__():
                        child.nodeset.add(id)
                        child.setTerminal()
                        return
                    break
            else:
                child = self.node(j, '')
                bn.children.add(child)
            bn = child
        bn.word = item
        bn.nodeset.add(id)
        bn.setTerminal()

    def tree(self, bn: Node):
        """返回二叉树的树形结构"""
        def recursive(bn, dep=0, length=[]):
            if bn:
                stack.append(str(bn.char) + '(%d)' % bool(bn.word))
                if bn.children:
                    count = 0
                    for child in bn.children:
                        if count == 0:
                            if dep >= len(length):
                                length.append(len(str(bn.char)))
                            else:
                                length[dep] = max(length[dep], len(str(bn.char)))
                            dep += 1
                            stack.append('-->')
                            recursive(child, dep, length)
                            count = count + 1
                        else:
                            # child = bn.children[i]
                            s = ''
                            for i in range(dep):
                                s += ' ' * (length[i] + 6)
                            stack.append('\n%s└-->' % s[:-4])
                            recursive(child, dep, length)
            else:
                stack.pop(-1)

        if bn:
            stack = []
            recursive(bn)
            return ''.join(stack)

class Compare:
    def __init__(self):
        self.Equal_set = list()

    def compare(self, bn_left: Node,  bn_right: Node):
        if not bn_left:
            return
        if not bn_right:
            return
        if bn_left.char == bn_right.char:
            for child_left in bn_left.children:
                for child_right in bn_right.children:
                    if child_left.char == child_right.char:
                        if child_left.terminal & child_right.terminal:
                            self.Equal_set.append(tuple((child_left.nodeset, child_right.nodeset)))
                        self.compare(child_left, child_right)
        return self.Equal_set


if __name__ == "__main__":
    l_forest = nameTree()
    print(f"start load data:")
    l_name = ["com.xxmassdeveloper.mpchartexample",
              "com.xxmassdeveloper.InvertedLineChartActivity",
              "com.xxmassdeveloper.mpchartexample.InvertedLineChartActivity",
              "com.xxmassdeveloper.mpchartexample.InvertedLineChartActivity.getdata",
              "com.xxmassdeveloper.mpchartexample.InvertedLineChartActivity.getdata.i",
              "com.xxmassdeveloper"]
    l_id = [1, 2, 3, 4, 5, 6]
    for entity, id in zip(l_name, l_id):
        l_forest.insert(entity.split("."), id)
    r_forest = nameTree()
    print(f"start load data:")
    r_name = ["com.xxmassdeveloper.mpchartexample",
              "com.xxmassdeveloper.mpchartexample.InvertedLineChartActivity",
              "com.xxmassdeveloper.mpchartexample.InvertedLineChartActivity.getdata",
              "com.xxmassdeveloper.mpchartexample.InvertedLineChartActivity.test",
              "com.xxmassdeveloper.mpchartexample.InvertedLineChartActivity.line",
              "com.xxmassdeveloper.mpchartexample.getdata"]
    r_id = [1, 2, 3, 4, 5, 6]
    for entity, id in zip(r_name, r_id):
        r_forest.insert(entity.split("."), id)

    compare = Compare()
    print(l_forest.tree(l_forest.mid))
    print(r_forest.tree(r_forest.mid))
    equal_set = compare.compare(l_forest.mid, r_forest.mid)
    print(equal_set)