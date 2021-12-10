from random import randint
from prime_gen import is_prime
import hashlib
import math

'''
SM2 验收要求
1.椭圆曲线参数，可以用文档例题中的，也可以直接用miracl库里封装的。
2.Hash函数，可以用miracl库里其他Hash函数替代，只要格式合适即可；也可以自己编写SM3。
3.验收时，会提供十个文件，每个文件包含一段或长或短的英文段落，作为明文。
4.运行后屏幕显示必要的椭圆曲线参数，以及明文、对应密文、解密后的明文。
5.验收分为两个时间段：12月12日和12月19日，临近期末，请同学们尽量选择12月12日进行验收。
6.作为最后一次实验，每个同学需单独进行验收、提交电子版报告和代码到邮箱，才算完成该实验。
'''

EC_INFINITY_POINT = None

class MySM2:
    def __init__(self, compress:int=0):
        '''
        :Fp-256 默认参数来自文档p(90/93)   
        :素数p
        :8542D69E 4C044F18 E8B92435 BF6FF7DE 45728391 5C45517D 722EDB8B 08F1DFC3
        :系数a
        :787968B4 FA32C3FD 2417842E 73BBFEFF 2F3C848B 6831D7E0 EC65228B 3937E498
        :系数b
        :63E4C6D3 B23B0C84 9CF84241 484BFE48 F61D59A5 B16BA06E 6E12D1DA 27C5249A
        :基点G=(xG,yG)，其阶记为n。
        :坐标xG
        :421DEBD6 1B62EAB6 746434EB C3CC315E 32220B3B ADD50BDC 4C4E6C14 7FEDD43D
        :坐标yG
        :0680512B CBB42C07 D47349D2 153B70C4 E5D7FDFC BFA36EA1 A85841B9 E46E09A2
        :阶n
        :8542D69E 4C044F18 E8B92435 BF6FF7DD 29772063 0485628D 5AE74EE7 C32E79B7
        '''
        self.__compress = compress
        self.__ec_a = 0x787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498
        self.__ec_b = 0x63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A
        self.__ec_p = 0x8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3
        print("椭圆曲线方程 y^2 = x^3 + ax + b")
        print(f"参数 p: {hex(self.__ec_p)}")
        print(f"参数 a: {hex(self.__ec_a)}")
        print(f"参数 b: {hex(self.__ec_b)}")
        xG = 0x421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D
        yG = 0x0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2
        self.__ec_base_G = (xG, yG)
        print(f"基点 G = (xG, yG)")
        print(f"坐标 xG: {hex(xG)}")
        print(f"坐标 yG: {hex(yG)}")
        self.__ec_n = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
        self.__ec_h = 1
        print(f"阶 n: {hex(self.__ec_n)}")
        print(f"余因子 h: {hex(self.__ec_h)}")
        self.Hv = 256

    @classmethod
    def randint_gen(cls, _start:int, _end:int):
        return randint(_start, _end)

    @classmethod
    def IntToBytes(cls, x:int, k:int):
        '''
        :Input 非负整数x，以及字节串的目标长度k (其中k满足2^(8k) > x)。
        :Output 长度为k的字节串M
        '''
        M = b""
        for _shift in range(k):
            M = bytes([(x >> (8*_shift)) & 0xFF]) + M
        return M

    @classmethod
    def BytesToInt(cls, M:bytes):
        '''
        :Input：长度为k的字节串M。
        :Output：整数x。
        '''
        x = 0
        k = len(M)
        M = list(reversed(M))
        for _shift in range(k):
            x += M[_shift] << (_shift*8)
        return x;

    @classmethod
    def BitsToBytes(cls, s:str):
        '''
        :Input：长度为m的比特串s。
        :Output：长度为k的字节串M，其中k = ⌈m/8⌉
        '''
        m = len(s)
        k = math.ceil(m/8)
        s = s.rjust(k*8, "0")
        M = b""
        for _shift in range(k):
            M = bytes([int(s[-(_shift*8+8):][:8], 2)]) + M
        return M

    @classmethod
    def BytesToBits(cls, M:bytes):
        '''
        :Input：长度为k的字节串M。
        :Output：长度为m的比特串s，其中m = 8k。
        '''
        s = ""
        k = len(M)
        # m = 8*k
        M = list(reversed(M))
        for idx in range(k):
            s = (bin(M[idx])[2:]).rjust(8, "0") + s
        return s

    def DomainElemToBytes(self, a, l:int=0):
        '''
        :Input Fq中的元素α
        :Output 长度l =⌈t/8⌉的字节串S，其中t =⌈log2 q⌉
        '''
        q = self.__ec_p
        # q为奇素数
        if is_prime(q) and q>2:
            assert isinstance(a, int)
            assert a>=0 and a<=q-1
            l = math.ceil(math.log2(q)/8) if not l else l
            return self.IntToBytes(a, l)
        raise ValueError

    def BytesToDomainElem(self, S:bytes):
        '''
        : Input 长度为l =⌈t/8⌉的字节串S，其中t =⌈log2 q⌉
        '''
        q = self.__ec_p
        # q为奇素数
        if is_prime(q) and q>2:
            a = self.BytesToInt(S)
            assert a>=0 and a<=q-1
            return a
        raise ValueError

    def DomainElemToInt(self, a):
        '''
        :Input：Fq中的元素α
        :Output：整数x
        '''
        q = self.__ec_p
        # q为奇素数
        if is_prime(q) and q>2:
            assert isinstance(a, int)
            return a
        raise ValueError

    def PointToBytes(self, P:tuple, compress:int=None):
        '''
        : 点到字节串的转换
        :Input 椭圆曲线上的点P =(xP,yP)，且P ̸=O。
        :Output 字节串S。若选用未压缩表示形式或混合表示形式，则输出字节串长度为2l+1；若选用压
缩表示形式，则输出字节串长度为l+1。(l =⌈(log2 q)/8⌉。)
        :compress 0-未压缩 1-压缩 2-混合表示
        '''
        assert len(P) == 2
        self.__compress = compress if compress != None else self.__compress
        q = self.__ec_p
        l = math.ceil(math.log2(q)/8)

        xP = P[0]
        yP = P[1]
        X1 = self.DomainElemToBytes(xP, l) # 长度为l的字节串X1

        assert self.__compress in [0, 1, 2]
        if self.__compress == 0: # 未压缩
            Y1 = self.DomainElemToBytes(yP, l)
            PC = b"\x04"
            return PC+X1+Y1
        elif self.__compress == 1:
            pass
        elif self.__compress == 2:
            pass
        raise ValueError

    def BytesToPoint(self, S:bytes, compress:int=None):
        '''
        : 字节串到点的转换
        : Input 定义Fq上椭圆曲线的域元素a、b，字节串S
        : Output 输出椭圆曲线上的点P =(xP,yP)，且P!=O
        : compress 参数 0-未压缩 1-压缩 2-混合表示
        '''
        self.__compress = compress if compress != None else self.__compress
        assert self.__compress in [0, 1, 2]
        assert len(S)>1
        q = self.__ec_p
        l = math.ceil(math.log2(q)/8)
    
        PC = S[0]
        X1 = S[1:1+l]
        Y1 = S[1+l:1+2*l]
        xp = self.BytesToInt(X1)

        if self.__compress == 0: # 未压缩
            assert PC == 0x4 # 校验PC值
            yp = self.BytesToInt(Y1)
        elif self.__compress == 1:
            pass
        elif self.__compress == 2:
            pass
        # 返回前校验点是否满足椭圆曲线曲线方程
        assert pow(yp, 2)%self.__ec_p \
            == (pow(xp, 3)+self.__ec_a*xp+self.__ec_b)%self.__ec_p
        return (xp, yp)

    def _negate(self, x):
        return (-x) % self.__ec_p

    def _sub(self, x, y):
        return (x-y) % self.__ec_p

    def _add(self, x, y):
        return (x+y) % self.__ec_p

    def _mul(self, x, y):
        return (x*y) % self.__ec_p

    def _inv(self, x):
        #print(pow(x, self.__ec_p-2, mod=self.__ec_p))
        #print(self.findModReverse(x, self.__ec_p))
        #input()
        return pow(x, self.__ec_p-2, mod=self.__ec_p)
        #return self.findModReverse(x, self.__ec_p)

    def _calc_lambda_in_add(self, x1:int, y1:int, x2:int, y2:int):
        a = self._sub(y2, y1)
        b = self._sub(x2, x1)
        b_inv = self._inv(b)
        return self._mul(a, b_inv)
    
    def _calc_lambda_in_mul(self, x1:int, y1:int):
        a = self._mul(x1, x1)
        a = self._mul(3, a) + self.__ec_a
        b = self._mul(2, y1)
        b_inv = self._inv(b)
        return self._mul(a, b_inv)

    def _point_add(self, P1, P2):
        '''
        : calc P1+P2 in domain Fp
        : 无穷远点用EC_INFINITY_POINT表示，def EC_INFINITY_POINT = None
        '''
        # 处理无穷远点
        if P1 == EC_INFINITY_POINT:
            return P2
        elif P2 == EC_INFINITY_POINT:
            return P1
        assert isinstance(P1, tuple) and isinstance(P2, tuple) and len(P1) == 2 and len(P2) == 2

        x1, y1 = P1
        x2, y2 = P2
        # 检查P1, P2是否互逆
        if x1==x2:
            # 互逆
            if self._negate(y1)==y2:
                return EC_INFINITY_POINT
            # 倍点运算
            else:
                _lambda = self._calc_lambda_in_mul(x1, y1)
        else:
            # 非互逆不同点相加
            _lambda = self._calc_lambda_in_add(x1, y1, x2, y2)
        # x3 = _lambda^2 - x1 - x2
        x3 = self._mul(_lambda, _lambda)
        x3 = self._sub(x3, x1)
        x3 = self._sub(x3, x2)
        # y3 = _lambda*(x1 - x3) - y1
        y3 = self._sub(x1, x3)
        y3 = self._mul(_lambda, y3)
        y3 = self._sub(y3, y1)
        return (x3, y3)

    def _ktimes_point(self, P, k):
        if P == EC_INFINITY_POINT:
            return P
        assert isinstance(P, tuple) and len(P)==2
        # 二进制展开法
        k = list(reversed(bin(k)[2:]))
        l = len(k)
        # print("len(k):", len(k))
        Q = EC_INFINITY_POINT
        for j in range(l-1, -1, -1):
            Q = self._point_add(Q, Q)
            if k[j] == "1":
                Q = self._point_add(Q, P)
            # print(f"Q{j}: ({hex(Q[0])}, {hex(Q[1])})")
        return Q

    def bits_hash_256(self, data:str)->str:
        data = self.BitsToBytes(data)
        sm3 = hashlib.new("sm3")
        sm3.update(data)
        return self.BytesToBits(sm3.digest())

    def KDF(self, Z:str, klen:int):
        '''
        : 密钥派生函数 KDF
        : 密钥派生函数的作用是从一个共享的秘密比特串中派生出密钥数据
        : Input 比特串Z，整数klen(表示要获得的密钥数据的比特长度，要求该值小于(2^32-1)v)
        : Output 长度为klen的密钥数据比特串K
        '''
        ct = 0x00000001
        v = self.Hv
        Ha = {}
        for i in range(1, math.ceil(klen/v)+1):
            # 计算Hai =Hv(Z||ct)
            Ha[i] = self.bits_hash_256(Z+bin(ct)[2:].rjust(32, "0"))
            # ct++
            ct += 1
        #print(self.BitsToBytes(Ha[1]).hex())
        # 判断是否需要取前klen-(v*math.ceil(klen/v))比特
        if klen%v != 0:
            Ha[math.ceil(klen/v)] = Ha[math.ceil(klen/v)][:klen-v*math.ceil(klen/v)]
        K = ""
        # 拼接并返回
        for i in range(1, math.ceil(klen/v)+1):
            K += Ha[i]
        #print(self.BitsToBytes(K).hex())
        return K

    def gen_key_pair(self):
        '''
        : 获取密钥对
        : compress 参数 0-未压缩(默认) 1-压缩 2-混合表示
        : Output (d, PA)
        : d 为私钥 PA 为公钥
        '''
        # 计算d倍点
        d = self.randint_gen(1, self.__ec_n-2) # 获取随机数d∈[1, n-1]
        d = 0x1649AB77A00637BD5E2EFE283FBF353534AA7F7CB89463F208DDBC2920BB0DA0
        self.__private_key = d
        #print(f"私钥 d: {hex(d)}")
        P = self._ktimes_point(self.__ec_base_G, d)
        self.__public_key = P
        #print(f"公钥 P: ({hex(P[0])}, {hex(P[1])})")
        return d, P

    def bits_xor(self, x:str, y:str):
        mlen = len(x) if len(x)>len(y) else len(y)
        x.ljust(mlen, "0")
        y.ljust(mlen, "0")
        res = "".join([str(int(x[i])^int(y[i])) for i in range(mlen)])
        return res

    def encrypt(self, msg:bytes, PB:tuple=None):
        M = self.BytesToBits(msg)
        klen = len(M)
        PB = self.__public_key if PB is None else PB # 公钥
        while True:
            # 取随机数k∈[1, n-1]
            k = self.randint_gen(1, self.__ec_n) 
            k = 0x4C62EEFD6ECFC2B95B92FD6C3D9575148AFA17425546D49018E5388D49DD7B4F
            # 计算G的K倍点为C1，并转化为比特串
            C1 = self._ktimes_point(self.__ec_base_G, k) 
            C1 = self.BytesToBits(self.PointToBytes(C1))
            # S=[h]PB，若S是无穷远点，则报错
            assert self._ktimes_point(PB, self.__ec_h) != EC_INFINITY_POINT
            # 计算椭圆曲线点[k]PB=(x2,y2)，并将x2y2存为比特串
            x2, y2 = self._ktimes_point(PB, k)
            x2 = self.BytesToBits(self.DomainElemToBytes(x2))
            y2 = self.BytesToBits(self.DomainElemToBytes(y2))
            # 计算t=KDF(x2||y2, klen)，若t为全0比特串，则返回第一步
            t = self.KDF(x2+y2, klen)
            if t.find("1") != -1:
                break
        # 计算C2 =M⊕t；
        C2 = self.bits_xor(M, t)
        # C3 =Hash(x2||M||y2)
        C3 = self.bits_hash_256(x2+M+y2)
        # 最后密文C=C1||C2||C3
        C = C1+C2+C3
        print(f"随机数 k: {hex(k)}")
        print(f"C1: {self.BitsToBytes(C1).hex()}")
        print(f"x2: {self.BitsToBytes(x2).hex()}")
        print(f"y2: {self.BitsToBytes(y2).hex()}")
        #print(f"len(t): {len(t)}")
        print(f"t: {self.BitsToBytes(t).hex()}")
        print(f"M: {self.BitsToBytes(M).hex()}")
        print(f"C2: {self.BitsToBytes(C2).hex()}")
        print(f"C3: {self.BitsToBytes(C3).hex()}")

        return self.BitsToBytes(C)

    def decrypt(self, cipher:bytes, d:int=None):
        C = self.BytesToBits(cipher)
        dB = self.__private_key if d is None else d # 私钥
        p = self.__ec_p
        if self.__compress == 0:
            # 未压缩状态下C1的比特长度
            C1_len = 8*(2*math.ceil(math.log2(p)/8)+1)
        elif self.__compress == 1:
            pass
        elif self.__compress == 2:
            pass
        # 计算C2, C3的长度
        C3_len = self.Hv
        C2_len = len(C)-C1_len-C3_len
        klen = C2_len
        # 从C中取出比特串C1，并转换为椭圆曲线上的点，同时检查点的合法性
        C1 = C[:C1_len]
        C1 = self.BytesToPoint(self.BitsToBytes(C1))
        # 计算椭圆曲线点S=[h]C1
        S = self._ktimes_point(C1, self.__ec_h)
        # 校验S不为无穷远点
        assert S != EC_INFINITY_POINT
        # 计算[dB]C1=(x2,y2)
        x2, y2 = self._ktimes_point(C1, dB)
        x2 = self.BytesToBits(self.DomainElemToBytes(x2))
        y2 = self.BytesToBits(self.DomainElemToBytes(y2))
        # 计算t=KDF(x2||y2, klen)，若t为全0比特串，则报错并退出
        t = self.KDF(x2+y2, klen)
        assert t.find("1") != -1
        # 从C中取出比特串C2，计算M′=C2 ⊕t
        C2 = C[C1_len:C1_len+klen]
        M = self.bits_xor(C2, t)
        # 计算u=Hash(x2||M′||y2)，从C中取出比特串C3，若u̸=C3，则报错并退出
        u = self.bits_hash_256(x2+M+y2)
        C3 = C[C1_len+klen:]
        assert u == C3

        print(f"x2: {self.BitsToBytes(x2).hex()}")
        print(f"y2: {self.BitsToBytes(y2).hex()}")
        #print(f"len(t): {len(t)}")
        print(f"t: {self.BitsToBytes(t).hex()}")
        print(f"u: {self.BitsToBytes(u).hex()}")

        return self.BitsToBytes(M)

def tester():
    a = MySM2.IntToBytes(0x11223344, 4)
    b = MySM2.BytesToInt(a)
    print("IntToBytes:", a.hex(" "))
    print("BytesToInt:", hex(b))

    c = MySM2.BitsToBytes("11111111101111111")
    d = MySM2.BytesToBits(c)
    print("BitsToBytes:", c.hex(" "))
    print("BytesToBits:", d)

def readfile(filename, mode:str="rb"):
    with open(filename, mode) as f:
        return f.read()

def main():
    # 创建sm2对象
    sm2 = MySM2(compress=0) # 使用“未压缩”模式做测试
    print()
    print("===============Key Pair===============")
    # 生成密钥对
    d, P = sm2.gen_key_pair()
    print(f"私钥 d: {hex(d)}")
    print(f"公钥 P: ({hex(P[0])}, {hex(P[1])})")
    print()
    # 加密
    print("===============Encrypt===============")
    #M1 = b"encryption standard"
    #M1 = input("请输入明文: ").encode('utf-8')
    M1 = readfile("./5_data/msg_1.txt")

    C = sm2.encrypt(M1)
    print()
    print(f"密文 C: {C.hex()}")
    print()
    # 解密
    print("===============Decrypt===============")
    M2 = sm2.decrypt(C)
    print()
    print(f"明文 M: {M2.hex()}")
    print(f"明文字节串:\n\n{M2.decode('utf-8')}")
    print()  
    # 校验
    print("================Check================") 
    if M1 == M2:
        print("成功: 明文密文校验结果一致!")
    else:
        print("失败: 明文密文校验结果不一致!")
    print()

if __name__ == "__main__":
    main()