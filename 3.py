from math import prod, gcd
from math import pow as math_pow
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

def crt(equation_num, a_list:list, m_list:list):
    mj = []
    aj = []
    # 读入a和m的值
    for _ in range(equation_num):
        aj.append(a_list[_])
        mj.append(m_list[_])
    #print()
    #print("aj:", aj)
    #print("mj:", mj)

    # 检查各个m值之间是否互素
    if not mutual_prime_check(mj):  # 互素检查
        print("不能直接利用中国剩余定理")
        return None
    # 计算 m = m1*m2*···*mj
    m = prod(mj)
    # 计算 Mj = m / mj
    Mj = [m//_mj for _mj in mj]
    # 计算 Mj逆元
    inv_Mj = [pow(m//_mj, _mj-2, mod=m) for _mj in mj]  # 逆元计算方法： Mj^(-1) = Mj^(mj-2)
    # 计算 xj ≡  Mj*Mj^(-1)*aj(mod m)
    xj = [(Mj[j]*inv_Mj[j]*aj[j]) % m for j in range(equation_num)]

    # 输出x结果
    res = sum(xj) % m
    #print(f"解得：x ≡ {res}(mod {m})")
    return res

d_seq = [
19199315540070837227525605167183444047909530679322325914085849862925810723227370859901004942966369161515225484662629816381893112332953277014518678836856719207092395742184117962914223327436002122582851,
25683263256535151403395058478100074765863863617370536002075130258480121902852042213125508298472605208767515191665580002889107342756209737430298125545301667176063926246766746109952647578167945204039677,
25788663317832667763282112323593821294042382096417374670776340951799511067480928544406141073815016239204683693383622648968351155071699088529118509814874598438674272394046192980594347703994493143074801,
76857100116727982855093490106022768028914976071737210523681693966922586096716470989225665181076353401693645603018093547103801135759909426709591468479552466615074395563441505582306383372570368554522739,
82557581285544266678907597256319796666068470815886640491655970155115894682743253940909952911708685134795210859543670547733335714895935881464457468970952670923172319331049645281429210653182420773587431
    ]

def encrypt(k, t, n):
    # 前t组相乘计算N
    N = prod(d_seq[0:t])
    print(f"N: {N}")
    print()
    # 后t-1组相乘计算N
    M = prod(d_seq[n-t+1:n])
    print(f"M: {M}")
    print()
    # 需要满足N > k > M

    # 轮流求模得到一系列ki值
    ki = [k % d_seq[i] for i in range(n)]
    # 把生成的ki和di打包成对返回
    res = list(zip(ki, d_seq))
    
    return res

def decrypt(t, k_d:list):
    if len(k_d) < t:
        print(f"数据少于{t}组，无法解密")
        sys.exit()
    # 送入中国剩余定理求解函数拿到返回值就是秘密k
    return crt(t, [k_d[i][0] for i in range(t)], [k_d[j][1] for j in range(t)])

'''
d_seq = []

for i in range(5):
    d_tmp = int(os.popen("prime -L 200").read())
    print(d_tmp)
    d_seq.append(d_tmp)
    
d_seq.sort(reverse=False)
'''

def main():
    t = 3
    n = 5

    for d_idx in range(n):
        print(f"d{d_idx+1} = {d_seq[d_idx]}")
        print()

    for case_i in range(5):
        print(f"{'#'*36} 测试样例【{case_i+1}】{'#'*36}")
        with open(f"./3_data/bigint_{case_i+1}.txt", "r") as f:
            k = int(f.read())
            print("⚪ 测试加密：", end="\n\n")
            print("k = ", k, end="\n\n")
            res_enc = encrypt(k, t, n)
            for i in range(n):
                print(f"(k{i+1}, d{i+1})：{res_enc[i]}")
                print()
            print("⚪ 测试解密：", end="\n\n")
            # 取前t组用于解密（从res_enc中任取t组均可）
            res_dec = decrypt(t, res_enc[0:t])
            print("正确秘密k：", k, end="\n\n")
            print("还原秘密k：", res_dec, end="\n\n")
            if res_dec == k:
                print("秘密还原正确！")
            else:
                print("秘密还原错误！")

if __name__ == "__main__":
    main()