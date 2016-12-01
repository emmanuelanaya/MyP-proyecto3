import os, sys
sys.path.insert(0, os.path.abspath("src"))
import s4cipher, unittest, random, string

class TestS4Cipher(unittest.TestCase):

    def test_inverso_zp(self):
        n = random.getrandbits(256)
        self.assertEqual(1, (n * s4cipher.inverso_zp(n)) % s4cipher.P)
    
    def test_polinomio_init(self):
        n = random.getrandbits(256)
        g = random.randint(0, 100)
        p = s4cipher.Polinomio(n, g)
        self.assertEqual(len(p.coefs), g + 1)
        self.assertTrue(0 != p.coefs[g])
        g = 0
        p = s4cipher.Polinomio(n, g)
        self.assertEqual(p.coefs[0], n)
        
    def test_polinomio_evaluate(self):
        n = random.getrandbits(256)
        g = random.randint(0, 100)
        p = s4cipher.Polinomio(n, g)
        m = random.getrandbits(256)
        self.assertEqual(p.evaluate(m * -1), p.evaluate(s4cipher.P - m))

    def test_polinomio_rand_evals(self):
        n = random.getrandbits(256)
        g = random.randint(0, 100)
        p = s4cipher.Polinomio(n, g)
        s = set()
        for pi in p.rand_evals(random.randint(0, 100)):
            self.assertFalse(pi[0] in s)
            s.add(pi[0])
        
    def test_polinomio_get_ind(self):
        l = [(0, 10)]
        self.assertEqual(s4cipher.Polinomio.get_ind(l), 10)
        l = [(1, 3), (4, 111), (3, 59), (2, 23)]
        self.assertEqual(s4cipher.Polinomio.get_ind(l), -1 % s4cipher.P)
        l = [(1, 3), (4, 111), (3, 59), (2, 23), (5, 179)]
        self.assertEqual(s4cipher.Polinomio.get_ind(l), -1 % s4cipher.P)

    def test_preprocess(self):
        n = random.randint(0, 10000)
        a = "".join(random.choice(string.printable) for i in range(n))
        n = random.randint(0, 10000)
        b = "".join(random.choice(string.printable) for i in range(n))
        s = s4cipher.preprocess(a, b)
        self.assertEqual(0, len(s) % 16)

    def test_encrypt_decrypt(self):
        for i in range(10):
        
            n = random.randint(0, 100)
            nombre = "".join(random.choice(string.printable) for i in range(n))
            n = random.randint(0, 100000)
            claro = "".join(random.choice(string.printable) for i in range(n))
            m = random.randint(1, 100)
            t = random.randint(1, m)
            n = random.randint(0, 1000)
            clave = "".join(random.choice(string.printable) for i in range(n))
            
            enc = s4cipher.encrypt(claro, nombre, m, t, clave)
            dect = s4cipher.decrypt(enc[0], enc[1])
            
            self.assertEqual(dect[0], nombre)
            self.assertEqual(dect[1], claro)
        
 
        
if __name__ == "__main__":
    unittest.main()
