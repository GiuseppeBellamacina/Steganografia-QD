from PIL import Image

def binaryConvert(text):
    """Converte una stringa di testo in una stringa binaria (carattere per carattere)"""
    return ''.join(format(ord(char), '08b') for char in text)

def binaryConvertBack(text):
    """Converte una stringa binaria in una stringa di testo (8-bit)"""
    return ''.join(chr(int(text[i*8:i*8+8],2)) for i in range(len(text)//8))

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

def hide_message(img, msg):
    """Nasconde una stringa in una foto"""
    # controlla se l'immagine è abbastanza grande
    if (img.width * img.height) * 3 < len(msg) * 8:
        raise ValueError(f"Immagine troppo piccola per nascondere il messaggio.\nMessaggio: {len(msg)} caratteri\nImmagine: {img.width}x{img.height}")
    
    # converte in RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    # inizia a nascondere
    print("Nascondendo messaggio...")
    img_copy = img.copy()
    mat = img_copy.load()
    msg_binary = binaryConvert(msg)
    msg_binary = msg_binary + "0000"  # terminatore
    msg_list = list(msg_binary)
    
    for i in range(img.width):
        for j in range(img.height):
            for z in range(3):
                if msg_list != []:
                    bit = msg_list.pop(0)
                    color = mat[i,j][z] # ottieni il colore
                    color = setLastBit(color, bit) # cambia l'ultimo bit
                    mat = setComponentOfColor(mat, i, j, color, z) # setta il colore
                else:
                    break
    
    original_len = len(msg_binary)
    percentage = format(((original_len / ((img.width * img.height) * 3)) * 100), '.2f')
    print(f"TERMINATO - Percentuale di pixel usati: {percentage}%")

    return img_copy


def get_message(img):

    if img.mode != "RGB":
        img = img.convert("RGB")
    
    # inizia la procedura
    mat = img.load()
    msg, stop = [], []
    
    for i in range(img.width):
        for j in range(img.height):
            for z in range(3):
                color = mat[i,j][z]
                bit = format(color, '08b')[-1]
                stop.append(bit)
                msg.append(bit)
                if len(stop) == 8:
                    if ''.join(stop) == "0000":
                        msg = ''.join(msg)
                        msg = msg[:-8]
                        msg = binaryConvertBack(msg)
                        
                        
                        return msg
                    stop = []
    
    msg = ''.join(msg)
    msg = msg[:-8]
    try:
        msg = binaryConvertBack(msg)
        if not msg or len(msg.strip()) == 0:
            raise ValueError("Nessun messaggio valido trovato nell'immagine")
        return msg
    except:
        raise ValueError("Impossibile decodificare il messaggio dall'immagine. Verifica che contenga davvero un messaggio nascosto")


