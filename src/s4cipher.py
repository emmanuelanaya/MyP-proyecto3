"""Modulo que proporciona funciones para encriptar y desencriptar archivos por el
metodo del Esquema de Secreto Compartido de Shamir, asi como una clase Polinomio
que facilita la manipulacion de poinomios aleatorios, asi como la evaluacion de 
estos por el metodo de interpolacion de LaGrange
"""

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import random
from binascii import unhexlify
import sys

"""Numero primo de 257 bits, tamano del campo donde se realizan las operaciones
algebraicas
"""
P = 208351617316091241234326746312124448251235562226470491514186331217050270460481

def inverso_zp(n):
    """Regresa el inverso multiplicativo de n en el campo Zp

    @param n un elemento de Zp no nulo de Zp
    @return el inverso multiplicativo de n en Zp
    """
    return pow(n, P - 2, P) % P

def suma_zp(n, m):
    """Regresa la suma de dos elementos en Zp

    @param n un elemento de Zp
    @param m un elemento de Zp
    @return la suma de m y n en Zp
    """
    return (n + m) % P


def resta_zp(n, m):
    """Regresa la resta de dos elementos en Zp

    @param n un elemento de Zp
    @param m un elemento de Zp
    @return la resta de m y n en Zp
    """
    return (n - m) % P

def prod_zp(n, m):
    """Regresa el producto de dos elementos en Zp

    @param n un elemento de Zp
    @param m un elemento de Zp
    @return el producto de m y n en Zp
    """
    return (n * m) % P

class Polinomio:
    """Implementacion de un polinomio de coeficientes enteros.
    
    Provee de metodos utiles para la implementacion del SSSS, cuya
    especificacion requiere evaluaciones de polinomios en el campo.
    """

    
    def __init__(self, indep, t):
        """ Metodo constructor de un polinomio aleatorio.

        Inicializa el polinomio con el termino independiente y grado
        especificados, coeficientes aleatorios.

        @param indep el termino independiente del polinomio
        @param t el grado del polinomio
        """
        self.grado = t
        self.coefs = []
        self.coefs.append(indep)
        for i in range(self.grado):
            self.coefs.append(random.getrandbits(256))
        while self.coefs[self.grado] == 0:
            self.coefs[self.grado] = random.getrandbits(256)

    def evaluate(self, x):
        """ Evalua el polinomio en el punto especificado
        
        Como el polinomio es sobre el campo Zp, el resultado se regresa
        modulo P

        @param x el valor entero donde se evaluara el polinomio
        @return f(x), la evaluacion del polinomio
        """
        res = self.coefs[self.grado]
        for i in reversed(range(self.grado)):
            res = suma_zp(prod_zp(res, x), self.coefs[i])

        return res;
            
    def rand_evals(self, n):
        """ Genera evaluaciones aleatorias del polinomio

        Regresa una lista de pares (x,f(x)) de tamaño n, donde x se 
        obtiene de manera aleatoria en Zp

        @param n el numero de evaluaciones aleatorias
        @return la lista con las n evaluaciones del polinomio
        """
        points = []
        s = set()
        for i in range(n): 
            r = random.getrandbits(256)
            while r in s:
                r = random.getrandbits(256)
            s.add(r)
            points.append((r, self.evaluate(r)))

        return points

   
    @staticmethod
    def get_ind(points):
        """ Regresa el termino independiente del polinomio determinado por
        un conjunto de puntos
        
        Dada una lista de evaluaciones de un polinomio, regresa el termino
        independiente de este, obteniendolo mediante el metodo de interpolacion
        de LaGrange
        
        @param points la lista con las evaluaciones del polinomio
        @return el termino independiente del polinomio
        """
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
    """ Preprocesa dos cadenas para que sirvan como clave para el cipher AES

    Concatena ambas cadenas, separandolas por el caracter nulo, y agrega
    caracteres hasta que el tamaño de la nueva cadena sea multiplo de 16

    @param st una cadena
    @param name el nombre de la cadena
    @return la cadena concatenada y con el tamaño correcto 
    """

    full = name + "\0" + st
    k = (16 - len(full) % 16)
    ap = format(k % 16, "x") * k;
    return full + ap
        

def encrypt(claro, nombre, n, t, clave):
    """ Encipta un texto claro usando el esquema de cifrado AES, y el SSSS para
    la contraseña

    Se genera una clave segura dada la clave original. Esta se usa para cifrar el
    texto claro usando el esquema AES, y a su vez se separa en n partes, usando el
    SSSS. t de estas partes se necesitan para descifrar el texto claro.

    @param claro una cadena de texto
    @param nombre el nombre del archivo que se encripta
    @param n el numero de partes del secreto a generar
    @param t el numero de partes necesarias para desencriptar
    @param clave la clave (no_segura) que se usara
    @return un par (t, p) donde t es el texto encriptado y p es lista de partes del secreto
    """
    
    safe_key = SHA256.new(bytes(clave, "utf-8"))
    pol = Polinomio(int(safe_key.hexdigest(), 16), t - 1)
    points = pol.rand_evals(n)
    cipher_text = AES.new(safe_key.digest()).encrypt(preprocess(claro, nombre))
    return (cipher_text, points)


def decrypt(c_text, points):
    """ Desencripta un texto cifrado por el metodo SSSS, con la lista de claves que se
    proporciona

    Dadas las evaluaciones de un polinomio, se obtiene su termino independiente, el
    cual servira comp clave para desencriptar el texto usando el esquema AES

    @param c_text el texto cifrado
    @param points la lista con las evaluaciones del polinomio
    @return un par (n, s) con el nombre del archivo y el texto claro 
    """
    safe_key = format(Polinomio.get_ind(points), "x")
    safe_key = "0" * (64 - len(safe_key)) + safe_key
    try:
        full = AES.new(unhexlify(safe_key)).decrypt(c_text).decode("utf-8")
    except:
        print("Claves incorrectas, saliendo...")
        sys.exit()
    fst = full.find("\0")
    name = full[:fst]
    st = full[fst+1:]
    extra = int(st[-1], 16)
    extra = extra if extra else 16
    st = st[:-extra]
    return (name, st)
