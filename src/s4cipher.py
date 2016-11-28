from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import random

P = 208351617316091241234326746312124448251235562226470491514186331217050270460481

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
            res = ((res * x) + self.coefs[i]) % P

        return res;
            
    def rand_evals(self, n):
        points = []
        for i in range(n):
            r = random.getrandbits(256)
            points.append((r, self.evaluate(r)))

        return points
    
            
# def preprocess(st, t):
    
def encrypt(claro, n, t, clave):
    safe_key = SHA256.new(clave)
    pol = Polinomio(int(safe_key.hexdigest(), 16), t - 1)
    points = pol.rand_evals(n)
    
