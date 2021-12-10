from random import randint
from prime_gen import get_prime_by_len, is_prime
import sys

'''
实验四验收要求：
1. 秘密长度近150位，验收用的5个秘密（145，140，135，130，125位）
2. 大素数的形式为p=2q+1形式的强素数，这里面q也是素数，要求p为150位的大素数，大素数p和本原根自己生成。（关于强素数，请同学们查阅文献资料了解学习）
3. 解密出的结果要与明文对比，验证解密是否正确。
另：中间数据显示在屏幕上，包括P，g，y，k及密文c=(y1, y2)等
强素数使得其p-1只有四个因子：1，2，q，p-1；从而使本原元的判断变的简单，只需要验证2和q即可。
'''

strong_primes = [
    264524496593608206264798617738129042221783219641399256538376069712089597186432827729210829823599408607385613184616870316102638648664225276907321134839,
    317125627518188730508020258802521364868324332706959835532545169063577310626921405794775974418002827629244384581836089237904108798412437031752348923963,
    125166846307653635581030337625159685816060200807252204162099079666519938958048656861713313156800814726900091849648073571745565522499285384543858980087,
    331544675508350033845109310099247673568902018614958753105701182279809706291471220832319589181897017647928048982201262010610044573142303858744796429323,
]


def get_strong_prime(prime_len: int):
    # 随机使用预生成的强素数
    p = strong_primes[randint(0, len(strong_primes)-1)]
    return p, (p-1)//2

    # 随机生成强素数（耗时较久）
    '''
    while True:
        p = get_prime_by_len(prime_len, 0) # 生成指定长度的素数
        if p%2 == 1 and is_prime((p-1)//2): # 该强素数需要满足 p = q*2+1
            return p, (p-1)//2
        else:
            continue    # 不满足条件继续生成
    '''


def gen_key_pair():
    '''生成密钥对'''
    def get_primordial_root(p: int, q: int):
        for tmp_g in range(2, p):
            # 由于取用素数的性质，只需要判断 g^2 mod p 和 g^q mod p 不为1即可
            if pow(tmp_g, 2, mod=p) != 1 and pow(tmp_g, q, mod=p) != 1:
                # 返回符合条件值的作为原根
                return tmp_g
        return None

    print("生成强素数...")
    p, q = get_strong_prime(150)  # 获取150位强素数
    print(f"p: {p}", end="\n\n")
    print(f"q: {q}", end="\n\n")
    g = get_primordial_root(p, q)  # 计算原根
    print(f"g: {g}", end="\n\n")
    a = randint(1, p-2)     # 随机取一个a
    print(f"a: {a}", end="\n\n")
    y = pow(g, a, mod=p)  # 计算y = g^a(mod p)
    print(f"y = g^a(mod p): {y}", end="\n\n")
    pub_key = (p, g, y)
    private_key = a
    print(f"PubKey: (p, g, y)\nPrivateKey: a", end="\n\n")

    return pub_key, private_key  # 返回公钥和私钥


def encrypt(m: int, pub_key: tuple):
    '''加密消息'''
    p, g, y = pub_key
    k = randint(1, p-2)  # 随机取一个k
    C1 = pow(g, k, mod=p)  # C1 = g^k(mod p)
    C2 = m * pow(y, k, mod=p)  # C2 = (m * (g^a)^k)(mod p)

    return C1, C2


def decrypt(c: tuple, pub_key: tuple, private_key: int):
    C1, C2 = c
    p, g, y = pub_key
    a = private_key
    V = pow(C1, a, p)  # C1为g^k(mod p)，计算得g^a^k(mod p)
    m = (C2//V) % p  # 计算明文m = (C2*V^(-1))(mod p) （m过大可能造成信息丢失）

    return m


def local_test(round=5, data_src="file"):
    for case_i in range(round):
        print(f"{'#'*40} 测试样例【{case_i+1}】{'#'*40}")
        if data_src == "file":
            with open(f"./4_data/secret_{case_i+1}.txt", "r") as f:
                raw_m = int(f.read())
        elif data_src == "input":
            raw_m = int(input(f"请输入m{case_i+1}: "))
        print(f"消息m{case_i+1}长度: {len(str(raw_m))}", end="\n\n")
        # 获取密钥对得到pub_key private_key
        pub_key, private_key = gen_key_pair()

        # 加密消息m，得到C1 C2
        C1, C2 = encrypt(raw_m, pub_key)
        print(f"C1: {C1}", end="\n\n")
        print(f"C2: {C2}", end="\n\n")

        # 解密密文C1 C2得到消息m
        dec_m = decrypt((C1, C2), pub_key, private_key)
        print(f"原明文消息: {raw_m}", end="\n\n")
        print(f"解密后消息: {dec_m}", end="\n\n")
        print(f"校验结果(True/False): {raw_m==dec_m}", end="\n\n")


def main():
    local_test(5, "file")  # 从文件测试
    # local_test(5, "input") # 手动输入测试


if __name__ == "__main__":
    main()
