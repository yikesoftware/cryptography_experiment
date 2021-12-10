from random import randint
import time

def miller_rabin(p):
    if p == 1: return False
    if p == 2: return True
    if p % 2 == 0: return False
    m, k, = p - 1, 0
    while m % 2 == 0:
        m, k = m // 2, k + 1
    a = randint(2, p - 1)
    x = pow(a, m, p)
    if x == 1 or x == p - 1: return True
    while k > 1:
        x = pow(x, 2, p)
        if x == 1: return False
        if x == p - 1: return True
        k = k - 1
    return False

def is_prime(p, r = 40):
    for i in range(r):
        if miller_rabin(p) == False:
            return False
    return True

def get_prime_by_bits(nbits:int) -> int:
    '''get_prime_by_bits(nbits:int) -> int'''
    num = 0
    for _ in range(nbits):
        num = num * 2 + randint(0, 1)
    while not is_prime(num):
        num = num + 1
    return num

def get_prime_by_len(length:int, max_times:int=5):
    '''gget_prime_by_len(length:int, max_times:int=5) -> int'''
    def __get_prime_by_len(length:int):
        num = get_prime_by_bits(len(bin(int(length*"9")))  - randint(2,5))
        while is_prime(num) == False:
            num = num + 1
        if len(str(num)) == length:
            return num
        else:
            return None
    if max_times > 0:
        for _ in range(max_times):
            num = __get_prime_by_len(length)
            if len(str(num)) == length:
                return num
        return None
    else:
        while True:
            num = __get_prime_by_len(length)
            if len(str(num)) == length:
                return num

if __name__ == '__main__':
    T = time.perf_counter()
    print("TEST:")
    for _ in range(10):
        index = 1024
        print(index, "位质数: ", end="")
        num = 0
        for i in range(index):
            num = num * 2 + randint(0, 1)
        while is_prime(num) == False:
            num = num + 1
        print(num)
        print("----------------------------")
    print("用时：", time.perf_counter() - T)