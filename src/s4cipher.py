from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import random

P = 208351617316091241234326746312124448251235562226470491514186331217050270460481

def inverso_zp(n):
    return pow(n, P - 2, P) % P

def suma_zp(n, m):
    return (n + m) % P

def resta_zp(n, m):
    return (n - m) % P

def prod_zp(n , m):
    return (n * m) % P

class Polinomio:

    def __init__(self, indep, t):
        self.grado = t
        self.coefs = []
        self.coefs.append(indep)
        for i in range(self.grado):
            self.coefs.append(random.getrandbits(256))
        while self.coefs[self.grado] == 0:
            self.coefs[self.grado] = random.getrandbits(256)

    def evaluate(self, x):
        res = self.coefs[self.grado]
        for i in reversed(range(self.grado)):
            res = suma_zp(prod_zp(res, x), self.coefs[i])

        return res;
            
    def rand_evals(self, n):
        points = []
        for i in range(n):
            r = random.getrandbits(256)
            points.append((r, self.evaluate(r)))

        return points

    @staticmethod
    def get_ind(points):
        n = len(points)
        res = 0
        for i in range(n):
            basis = 1
            for j in range(n):
                if i != j:
                    basis = prod_zp(basis,
                                    prod_zp(points[j][0],
                                            inverso_zp(resta_zp(points[j][0],
                                                             points[i][0]))))
            res = suma_zp(res, prod_zp(basis, points[i][1]))

        return res

    
def preprocess(st, name):
    full = name + "\0" + st
    k = (16 - len(full) % 16)
    ap = format(k % 16, "x") * k;
    return full + ap
        
    
def encrypt(claro, nombre, n, t, clave):
    safe_key = SHA256.new(bytes(clave, "utf-8"))
    pol = Polinomio(int(safe_key.hexdigest(), 16), t - 1)
    points = pol.rand_evals(n)
    cipher_text = AES.new(safe_key.digest()).encrypt(preprocess(claro, nombre))
    return (cipher_text, points)


claro = "Bicycle 808\nThe U.S. Playing Card Co.\nMade in U.S.A"
nombre = "Bi.txt"
clave = "password"

t = encrypt(claro, nombre, 5, 3, clave)
print(t[0])
