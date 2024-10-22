
def outer():
    x = "local"
    def inner():
        global y
        print("inner:", y)
        x = "nonlocal"

    inner()
    print("outer:", x)

x = 'global'
outer()
print('glabal:', x)
