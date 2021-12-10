# 中国剩余定理
from math import prod
import sys


def gcd(x: int, y: int):
    return x if y == 0 else gcd(y, x % y)


def qPow(a: int, n: int):
    '''快速幂'''
    ans = 1
    if n == 0:
        return 1
    ans = qPow(a, n >> 1)
    return ans*ans*a if (n & 1) else ans*ans


def mutual_prime_check(m: list):
    '''互素校验'''
    size = len(m)
    for i in range(size):
        for j in range(i+1, size):
            if gcd(m[i], m[j]) != 1:
                return False
    return True


'''
test case 1:
3
3 2
2 9
4 5
29(mod 90)

test case 2:
3
2 3
3 5
2 7
x ≡ 23(mod 105)

test case 3:
3
3 449
2 367
4 317
x ≡ 4406938(mod 52236211)

'''


def main():
    def safe_input(msg, maxlen):
        _input = input(msg)
        if len(_input) > maxlen:  # 限制最大长度
            print(f"最大长度 {maxlen}")
            sys.exit(-1)
        return _input

    #equation_num = int(input("同余方程数量："))
    equation_num = 3
    mj = []
    aj = []
    # 读入a和m的值
    for _ in range(equation_num):
        aj.append(int(safe_input(f"Input a{_+1}: ", 500)))
    for _ in range(equation_num):
        mj.append(int(safe_input(f"Input m{_+1}: ", 500)))
    print()
    print("aj:", aj)
    print("mj:", mj)

    # 检查各个m值之间是否互素
    if not mutual_prime_check(mj):  # 互素检查
        print("不能直接利用中国剩余定理")
        return

    # 计算 m = m1*m2*···*mj
    m = prod(mj)

    # 计算 Mj = m / mj
    Mj = [m//_mj for _mj in mj]

    # 计算 Mj逆元
    inv_Mj = [qPow(m//_mj, _mj-2) for _mj in mj]  # 逆元计算方法： Mj^(-1) = Mj^(mj-2)

    # 计算 xj ≡  Mj*Mj^(-1)*aj(mod m)
    xj = [(Mj[j]*inv_Mj[j]*aj[j]) % m for j in range(equation_num)]
    print("m:", m)
    print("Mj:", Mj)
    print("inv_Mj:", inv_Mj)
    print()

    # 输出x结果
    print(f"解得：x ≡ {sum(xj) % m}(mod {m})")
    print()


if __name__ == "__main__":
    print("求解一次同余方程组的解")
    main()
