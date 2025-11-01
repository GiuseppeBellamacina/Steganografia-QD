from PIL import Image
from os.path import exists
import pickle

# Variabili globali per il backup dei parametri recenti
_last_string_params = None
_last_image_params = None
_last_binary_params = None

def save_backup_data(data_type, params, backup_file=None):
    """Salva i parametri di occultamento in un file binario e nelle variabili locali"""
    global _last_string_params, _last_image_params, _last_binary_params
    
    # Salva nelle variabili globali per uso immediato
    if data_type == "string":
        _last_string_params = params
    elif data_type == "image":
        _last_image_params = params
    elif data_type == "binary":
        _last_binary_params = params
    
    # Salva su file se specificato
    if backup_file:
        try:
            with open(backup_file, 'wb') as f:
                backup_data = {
                    'type': data_type,
                    'params': params
                }
                pickle.dump(backup_data, f)
            print(f"Parametri salvati in {backup_file}")
        except Exception as e:
            raise ValueError(f"Errore nel salvataggio backup: {e}")

def load_backup_data(backup_file):
    """Carica i parametri di occultamento da un file binario"""
    try:
        if exists(backup_file):
            with open(backup_file, 'rb') as f:
                backup_data = pickle.load(f)
            print(f"Parametri caricati da {backup_file}")
            return backup_data
        else:
            print(f"File backup {backup_file} non trovato")
            return None
    except Exception as e:
        raise ValueError(f"Errore nel caricamento backup: {e}")
    
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
    msg_binary = msg_binary + "00000000"  # terminatore
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
                    if ''.join(stop) == "00000000":
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


