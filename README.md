# Steganografia-QD

Applicazione di steganografia LSB per nascondere e recuperare dati (stringhe, immagini, file binari) all'interno di immagini.

## Descrizione

Il progetto implementa tecniche di steganografia basate su **Least Significant Bit (LSB)** per occultare informazioni in immagini PNG/JPG senza alterazioni visibili.

### Funzionalità principali

- **Stringhe**: Nascondi messaggi di testo in immagini
- **Immagini**: Nascondi un'immagine dentro un'altra
- **File binari**: Nascondi file arbitrari (con supporto compressione ZIP)
- **Backup parametri**: Salvataggio automatico dei parametri per facilitare il recupero

## File principali

### `steganografia.py`

Modulo core con le funzioni di steganografia:

- `hide_message(img, msg, backup_file)` - Nasconde stringhe
- `get_message(img, backup_file)` - Recupera stringhe
- `hide_image(img1, img2, lsb, msb, div, backup_file)` - Nasconde immagini
- `get_image(img, new_img, lsb, msb, div, width, height, backup_file)` - Recupera immagini
- `hide_bin_file(img, file, zipMode, n, div, backup_file)` - Nasconde file binari
- `get_bin_file(img, new_file_path, zipMode, n, div, size, backup_file)` - Recupera file binari

**Parametri chiave:**

- `lsb/n`: Numero di bit meno significativi da modificare nell'immagine host
- `msb`: Numero di bit più significativi da estrarre dai dati da nascondere
- `div`: Fattore di distribuzione dei dati (0 = automatico)
- `backup_file`: Path del file .dat per salvare i parametri

### `streamlit_app.py`

Interfaccia web Streamlit con due modalità operative:

**Modalità "Nascondere dati":**

1. Carica immagine host
2. Carica/inserisci dati da nascondere
3. Configura parametri (opzionale - automatico per default)
4. Salva backup parametri (opzionale)
5. Scarica risultato

**Modalità "Recuperare dati":**

1. Carica immagine con dati nascosti
2. Scegli fonte parametri:
   - Automatico (variabili recenti)
   - File backup (.dat)
   - Inserimento manuale
3. Scarica dati recuperati

## Installazione

```bash
pip install -r requirements.txt
```

## Utilizzo

### Interfaccia web (Streamlit)

```bash
streamlit run streamlit_app.py
```

### Uso programmatico

```python
from PIL import Image
from steganografia import hide_message, get_message

# Nascondere un messaggio
img = Image.open('host.png')
result = hide_message(img, "Messaggio segreto", "backup.dat")
result.save('output.png')

# Recuperare il messaggio
img_hidden = Image.open('output.png')
message = get_message(img_hidden, "backup.dat")
print(message)
```

## Requisiti

- Python 3.7+
- PIL/Pillow
- NumPy
- Streamlit (per interfaccia web)

## Note tecniche

- **Formato immagini**: PNG consigliato (lossless), JPG supportato ma può causare perdita dati
- **Dimensioni**: L'immagine host deve avere capacità sufficiente per i dati da nascondere
- **Backup parametri**: Essenziali per recuperare immagini e file binari nascosti
- **Compressione**: Riduce la dimensione dei file binari da nascondere

## Modalità compressione

- `NO_ZIP (0)`: Nessuna compressione
- `FILE (1)`: Comprimi singolo file
- `DIR (2)`: Comprimi intera directory
