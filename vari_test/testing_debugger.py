passaggio = []
def fun1():
    print("Function 1 is running")
    passaggio.append('fun1')

def fun2():
    print("Function 2 is running")
    passaggio.append('fun2')

def fun3():
    print("Function 3 is running")
    passaggio.append('fun3')
    
fun1()
fun2()
fun3()
fun1()

print("Current passaggio:", passaggio)