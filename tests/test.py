
def level3():
    print("进入 level3")
    1 / 0  # 抛出 ZeroDivisionError
    print("不会执行到这里")

def level2():
    print("进入 level2")
    level3()
    print("level2 后续代码不会执行")

def level1():
    print("进入 level1")
    level2()
    print("level1 后续代码不会执行")

level1()