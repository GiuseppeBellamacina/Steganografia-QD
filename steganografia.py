from os import remove, walk
from os.path import getsize, join, relpath, exists
import zipfile
import pickle
from PIL import Image
import numpy as np

# zipModes
NO_ZIP = 0
FILE = 1
DIR = 2

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

def get_last_params(data_type):
    """Ottiene gli ultimi parametri usati per il tipo di dato specificato"""
    global _last_string_params, _last_image_params, _last_binary_params
    
    if data_type == "string":
        return _last_string_params
    elif data_type == "image":
        return _last_image_params
    elif data_type == "binary":
        return _last_binary_params
    return None

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

def setLastNBits(value, bits, n):
    """Setta gli ultimi n bits di un numero"""
    value_str = format(value, '08b')
    if len(bits) < n:
        n = len(bits)
    value_str = value_str[:-n] + bits
    result = int(value_str, 2)
    result = min(255, max(0, result))
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

def findDiv(dim, file, n):
    """Calcola il valore di divisione per la distribuzione dei bit"""
    image_dim = dim * n
    div = ((image_dim - n) / (getsize(file) * 8))
    return div

def zipdir(path, ziph):
    """Comprime una directory"""
    for root, dirs, files in walk(path):
        for file in files:
            file_path = join(root, file)
            arcname = relpath(file_path, path)
            ziph.write(file_path, arcname)

def save_image(img, file_path):
    """Salva un'immagine PIL su disco"""
    try:
        img.save(file_path)
        print(f"Immagine salvata come {file_path}")
        return True
    except Exception as e:
        raise ValueError(f"Errore nel salvataggio: {e}")

# FUNZIONI PER STRINGHE

def hide_message(img, msg, backup_file=None):
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
    
    # Salva i parametri per il recupero
    params = {
        'original_message': msg,
        'method': 'string'
    }
    save_backup_data("string", params, backup_file)
    
    return img_copy

def get_message(img, backup_file=None):
    """Ottieni un messaggio nascosto"""
    # Controlla se esistono parametri di backup
    backup_data = None
    if backup_file:
        backup_data = load_backup_data(backup_file)
    
    # Se non ci sono backup file, controlla le variabili locali
    if not backup_data:
        recent_params = get_last_params("string")
        if recent_params:
            print("Usando parametri dall'ultima operazione di occultamento")
            backup_data = {'type': 'string', 'params': recent_params}
    
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
                        
                        # Verifica con il backup se disponibile
                        if backup_data and 'params' in backup_data:
                            original = backup_data['params'].get('original_message', '')
                            if original == msg:
                                print("Messaggio verificato con backup")
                        
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

# FUNZIONI PER IMMAGINI

def hide_image(img1, img2, lsb=0, msb=8, div=0, backup_file=None):
    """Nasconde un'immagine in un'altra
        img1: immagine che nasconde (più grande)
        img2: immagine da nascondere (più piccola)
        lsb: numero di bit meno significativi di img1 da modificare
        msb: numero di bit più significativi di img2 da nascondere"""
    
    # check if lsb is valid
    if lsb < 0 or lsb > 8:
        raise ValueError("Il valore di LSB deve essere compreso tra 1 e 8 oppure 0 per la modalità automatica")
    
    # check if msb is valid
    if msb < 0 or msb > 8:
        raise ValueError("Il valore di MSB deve essere compreso tra 1 e 8 oppure 0 per la modalità automatica")
    
    # check if lsb is bigger than msb
    if lsb > msb:
        raise ValueError("Il valore di LSB deve essere minore di MSB")
    
    # determine auto lsb and msb
    if lsb == 0:
        lsb = 1
        while (lsb * img1.width * img1.height * 3) < (msb * img2.width * img2.height * 3):
            lsb += 1
            if lsb > 8:
                raise ValueError(f"Immagine host troppo piccola per nascondere l'altra immagine.\nHost: {img1.width}x{img1.height}\nDa nascondere: {img2.width}x{img2.height}")
    
    # check if image is big enough
    if (lsb * img1.width * img1.height * 3) < (msb * img2.width * img2.height * 3):
        raise ValueError(f"Immagine host troppo piccola per nascondere l'altra immagine.\nHost: {img1.width}x{img1.height}\nDa nascondere: {img2.width}x{img2.height}")

    # convert image to RGB
    if img1.mode != "RGB":
        img1 = img1.convert("RGB")
    if img2.mode != "RGB":
        img2 = img2.convert("RGB")
    
    # start hiding image
    print("Nascondendo immagine...")
    arr1 = np.array(img1).flatten().copy()
    arr2 = np.array(img2).flatten().copy()
    
    if div == 0:
        div = (len(arr1) * lsb) / (len(arr2) * msb)
    else:
        if div * len(arr2) * msb > len(arr1) * lsb:
            raise ValueError(f"Il valore di DIV ({div}) è eccessivo per queste immagini. Prova con 0 per il calcolo automatico")
    
    # Algoritmo migliorato per nascondere l'immagine
    pos_in_img1 = 0.0
    bit_buffer = ""
    
    for i in range(0, len(arr2), 3):  # Processa ogni pixel di img2 (RGB)
        if i + 2 >= len(arr2):
            break
            
        # Estrai i bit più significativi da ogni canale di img2
        r_bits = format(arr2[i], '08b')[:msb]
        g_bits = format(arr2[i + 1], '08b')[:msb]  
        b_bits = format(arr2[i + 2], '08b')[:msb]
        
        # Aggiungi tutti i bit al buffer
        bit_buffer += r_bits + g_bits + b_bits
        
        # Inserisci i bit in img1 quando ne abbiamo abbastanza
        while len(bit_buffer) >= lsb and pos_in_img1 < len(arr1):
            # Prendi lsb bit dal buffer
            bits_to_hide = bit_buffer[:lsb]
            bit_buffer = bit_buffer[lsb:]
            
            # Nascondili nel pixel corrente di img1
            pixel_pos = int(pos_in_img1)
            if pixel_pos < len(arr1):
                arr1[pixel_pos] = setLastNBits(arr1[pixel_pos], bits_to_hide, lsb)
            
            # Avanza nella posizione di img1
            pos_in_img1 += div
    
    # Gestisci eventuali bit rimanenti nel buffer
    if bit_buffer and pos_in_img1 < len(arr1):
        # Padda i bit rimanenti con zeri a destra per raggiungere lsb bit
        while len(bit_buffer) < lsb:
            bit_buffer += "0"
        
        pixel_pos = int(pos_in_img1)
        if pixel_pos < len(arr1):
            arr1[pixel_pos] = setLastNBits(arr1[pixel_pos], bit_buffer[:lsb], lsb)
    
    # Salva risultato
    w, h = img2.width, img2.height
    percentage = format((msb * img2.width * img2.height * 3) / (lsb * img1.width * img1.height * 3) * 100, '.2f')
    print(f"TERMINATO - Percentuale di pixel usati con lsb={lsb}, msb={msb} e div={div:.2f}: {percentage}%")
    
    img1_copy = Image.fromarray(arr1.reshape(img1.height, img1.width, 3))
    
    # Salva i parametri per il recupero
    params = {
        'lsb': lsb,
        'msb': msb,
        'div': div,
        'width': w,
        'height': h,
        'method': 'image',
        'original_img1_size': (img1.width, img1.height),
        'original_img2_size': (img2.width, img2.height)
    }
    save_backup_data("image", params, backup_file)
    
    return (img1_copy, lsb, msb, div, w, h)

def get_image(img, new_img, lsb=None, msb=None, div=None, width=None, height=None, backup_file=None):
    """Ottieni un'immagine nascosta da un'altra"""
    print("Cercando immagine nascosta...")
    
    # Recupera parametri automaticamente se non forniti
    if any(param is None for param in [lsb, msb, div, width, height]):
        print("Alcuni parametri mancanti, cercando nei backup...")
        
        # Controlla se esistono parametri di backup
        backup_data = None
        if backup_file:
            backup_data = load_backup_data(backup_file)
        
        # Se non ci sono backup file, controlla le variabili locali
        if not backup_data:
            recent_params = get_last_params("image")
            if recent_params:
                print("Usando parametri dall'ultima operazione di occultamento immagini")
                backup_data = {'type': 'image', 'params': recent_params}
        
        if backup_data and 'params' in backup_data:
            params = backup_data['params']
            lsb = lsb if lsb is not None else params.get('lsb')
            msb = msb if msb is not None else params.get('msb')
            div = div if div is not None else params.get('div')
            width = width if width is not None else params.get('width')
            height = height if height is not None else params.get('height')
            print(f"Parametri recuperati: lsb={lsb}, msb={msb}, div={div:.2f}, size={width}x{height}")
        else:
            raise ValueError("Parametri mancanti per il recupero dell'immagine. Fornisci un file backup (.dat) o inserisci i parametri manualmente")
    
    # Verifica che tutti i parametri siano validi
    if any(param is None for param in [lsb, msb, div, width, height]):
        raise ValueError("Alcuni parametri necessari per il recupero sono mancanti. Verifica il file backup o inserisci tutti i parametri manualmente")
    
    # Assert per il type checker
    assert lsb is not None and msb is not None and div is not None
    assert width is not None and height is not None
    
    size = width * height * 3
    arr = np.array(img).flatten().copy() 
    res = np.zeros(size, dtype=np.uint8)
    
    # Algoritmo migliorato per estrarre l'immagine
    pos_in_img1 = 0.0
    bit_buffer = ""
    pixels_written = 0
    
    # Calcola quanti pixel di img1 dobbiamo leggere
    total_bits_needed = size * msb
    pixels_to_read = int((total_bits_needed / lsb) * div) + 1
    
    while pixels_written < size and pos_in_img1 < len(arr):
        # Estrai lsb bit dal pixel corrente di img1
        pixel_pos = int(pos_in_img1)
        if pixel_pos < len(arr):
            extracted_bits = format(arr[pixel_pos], '08b')[-lsb:]
            bit_buffer += extracted_bits
        
        # Quando abbiamo abbastanza bit, ricostruisci un pixel di img2
        while len(bit_buffer) >= msb and pixels_written < size:
            # Prendi msb bit dal buffer  
            pixel_bits = bit_buffer[:msb]
            bit_buffer = bit_buffer[msb:]
            
            # Padda a sinistra con zeri per ottenere 8 bit (i bit più significativi)
            while len(pixel_bits) < 8:
                pixel_bits = pixel_bits + "0"
            
            # Converte in valore pixel e salva
            res[pixels_written] = int(pixel_bits, 2)
            pixels_written += 1
        
        # Avanza nella posizione di img1
        pos_in_img1 += div
    
    # Converte il risultato in immagine
    try:
        res_img = Image.fromarray(res.reshape(height, width, 3))
        res_img.save(new_img)
        print(f"IMMAGINE TROVATA - Immagine salvata come {new_img}")
        return res_img
    except Exception as e:
        raise ValueError(f"Impossibile ricostruire l'immagine nascosta. Verifica i parametri di recupero. Errore: {str(e)}")

# FUNZIONI PER FILE BINARI

def string_to_bytes(bit_string):
    """Converte una stringa di bit in bytes"""
    byte_array = bytearray()
    for i in range(0, len(bit_string), 8):
        byte = bit_string[i:i+8]
        if len(byte) == 8:
            byte_array.append(int(byte, 2))
    return byte_array

def hide_bin_file(img, file, zipMode=NO_ZIP, n=0, div=0, backup_file=None):
    """Nasconde un file binario o una cartella"""
    # check if n is in range
    if n < 0 or n > 8:
        raise ValueError("Il valore di N deve essere compreso tra 1 e 8, oppure 0 per la modalità automatica")
    
    # determine channels
    ch = 3
    if img.mode == "RGBA":
        ch = 4
    if img.mode != "RGB" and img.mode != "RGBA":
        img = img.convert("RGB")
    
    # check if zipMode is in range
    if zipMode not in [0, 1, 2]:
        raise ValueError("La modalità di compressione deve essere 0 (nessuna), 1 (file) o 2 (directory)")
    
    # zip file if zipMode is 1
    if zipMode == FILE:
        print("Compressione file...")
        with zipfile.ZipFile('tmp.zip', 'w') as zf:
            zf.write(file)
        file = 'tmp.zip'
        print("File compresso")
    
    # zip directory if zipMode is 2
    elif zipMode == DIR:
        print("Compressione directory...")
        zipf = zipfile.ZipFile('tmp.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir(file, zipf)
        file = 'tmp.zip'
        zipf.close()
        print("Directory compressa")
    
    # get file size
    total_bytes = getsize(file)
    
    # auto n
    if n == 0:
        while (img.width * img.height) * ch * n < total_bytes * 8:
            n += 1
            if n > 8:
                raise ValueError(f"Immagine troppo piccola per nascondere il file.\nFile: {total_bytes} bytes\nImmagine: {img.width}x{img.height}")
    
    # check if image is big enough
    elif (img.width * img.height) * ch * n < total_bytes * 8:
        raise ValueError(f"Immagine troppo piccola per nascondere il file.\nFile: {total_bytes} bytes\nImmagine: {img.width}x{img.height}")

    # convert image to array
    arr = np.array(img).flatten().copy()
    total_pixels_ch = len(arr)
    
    # check if div value is valid
    if div == 0:
        div = findDiv(total_pixels_ch, file, n)
    else:
        if total_pixels_ch * n < div * total_bytes * 8:
            raise ValueError(f"Il valore di DIV ({div}) è eccessivo per questo file. Prova con 0 per il calcolo automatico")
    
    # start hiding file
    print("Nascondendo file...")
    rsv = ""
    ind, pos = 0, 0
    
    # read file
    with open(file, 'rb') as f:
        f.seek(0)
        for i in range(total_bytes):
            byte = f.read(1) # read byte
            bits = format(ord(byte), '08b') # convert byte into string of bits
            bits = rsv + bits
            rsv = ""
            while len(bits) >= n:
                tmp = bits[:n]
                bits = bits[n:]
                # set last n bits of pixel
                arr[pos] = setLastNBits(arr[pos], tmp, n)
                ind += div
                pos = round(ind)
            if len(bits) > 0:
                rsv = bits
    
    f.close()
    while len(rsv) > 0:
        tmp = rsv[:n]
        rsv = rsv[n:]
        # set last n bits of pixel
        arr[pos] = setLastNBits(arr[pos], tmp, n)
        ind += div
        pos = round(ind)
    
    percentage = format(((total_bytes * 8) / ((img.width * img.height) * ch * n)) * 100, '.2f')
    print(f"TERMINATO - Percentuale di pixel usati con n={n} e div={div}: {percentage}%")
    
    if zipMode != NO_ZIP:
        # delete tmp.zip
        remove('tmp.zip')
    
    img_copy = Image.fromarray(arr.reshape(img.height, img.width, ch))
    
    # Salva i parametri per il recupero
    params = {
        'n': n,
        'div': div,
        'size': total_bytes,
        'zipMode': zipMode,
        'method': 'binary',
        'original_file': file,
        'channels': ch
    }
    save_backup_data("binary", params, backup_file)
    
    return (img_copy, n, div, total_bytes)
