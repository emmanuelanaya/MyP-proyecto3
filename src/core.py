#!/usr/bin/python3

import sys, os, getpass, re, s4cipher

def msg_uso():
    print("\nShamir Secret Sharing Scheme (S^4)")
    print("Implementacion por Emmanuel Anaya")
    
    print("\nPara cifrar, ejecute\n")
    print("\tssss -c <archivo_claro> n t <archivo_claves> <archivo_cifrado>\n")
    print("\tdonde\t<archivo_claro>\t\tes el texto a cifrar")
    print("\t\tn\t\t\tes el numero de claves a generar (n > 2)")
    print("\t\tt\t\t\tes el numero de claves necesarias para decifrar"
          " (1 < t <= n)")
    print("\t\t<archivo_claves>\tes el archivo donde se guardaran las claves")
    print("\t\t<archivo_cifrado>\tes el archivo donde se guardara el texto"
          " cifrado\n\n")

    print("Para descifrar, ejecute\n")
    print("\tssss -d <archivo_cifrado> <archivo_claves>\n")
    print("\tdonde\t<archivo_cifrado>\tes el archivo a descifrar")
    print("\t\t<archivo_claves>\tes el archivo con las evaluaciones,"
          " una por linea, de la\n\t\t\t\t\tforma \"x,f(x)\", sin comillas y"
          " sin lineas en blanco\n")

    sys.exit()


def pairs_file_syntax(f):
    lines = f.read().splitlines()
    for l in lines:
        if not re.match("-?\d+,-?\d+|", l): return False

    return True
    
def check_args_syntax(args):

    if len(args) < 2 or (args[1] not in ["-c", "-d"]):
        msg_uso()
    
    if args[1] == "-c":
        try:
            open(args[2], "r").close()
            int(args[3])
            int(args[4])
            f = open(args[5], "w")
            f.close(); os.remove(f.name);
            f = open(args[6], "wb")
            f.close(); os.remove(f.name);
        except:
            msg_uso()

        return 1
    else:
        try:
            open(args[2], "rb").close()
            with open(args[3], "r") as f:
                if not pairs_file_syntax(f): raise
        except:
            msg_uso()
            raise

        return 2


args = sys.argv

if(check_args_syntax(args) == 1):

    clave = getpass.getpass()
    with open(args[2], "r") as inp:
        claro = inp.read()
        name = inp.name
    n = int(args[3])
    t = int(args[4])
    cifrado = s4cipher.encrypt(claro, name, n, t, clave)
    with open(args[6], "wb") as out:
        out.write(cifrado[0])
    with open(args[5], "w") as out:
        for p in cifrado[1]:
            out.write("{},{}\n".format(p[0], p[1]))

    print("Cifrado exitoso")
    
else:
    
    with open(args[2], "rb") as inp:
        c_text = inp.read()
    points = []
    with open(args[3], "r") as inp:
        for s in inp.read().splitlines():
            spl = s.split(",")
            points.append((int(spl[0]), int(spl[1])))

    dec = s4cipher.decrypt(c_text, points)
    with open(dec[0], "w") as out:
        out.write(dec[1])

    print("Descifrado exitoso")
