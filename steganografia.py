from PIL import Image

def binaryConvert(text):
    """Converte una stringa di testo in una stringa binaria (carattere per carattere)"""
    return ''.join(format(ord(char), '08b') for char in text)

def setLastBit(value, bit):
    """Setta l'ultimo bit di un numero"""
    value_str = format(value, '08b') # converte un intero in una stringa di 8 caratteri (byte)
    value_str = value_str[:7] + bit # cambia l'ultimo bit
    result = int(value_str, 2) # riconverte la stringa in un numero
    result = min(255, max(0, result)) # controlla se il numero è fuori range
    return result

def setComponentOfColor(mat, i, j, color, channel):
    """Cambia tutte e tre le componenti di colore RGB di un pixel"""
    if channel == 0:
        mat[i,j] = (color, mat[i,j][1], mat[i,j][2])
    elif channel == 1:
        mat[i,j] = (mat[i,j][0], color, mat[i,j][2])
    elif channel == 2:
        mat[i,j] = (mat[i,j][0], mat[i,j][1], color)
    return mat

