# SteelSectionCheck

Applicazione Streamlit per analizzare sezioni in acciaio, ricavare le proprieta'
geometriche principali e preparare una relazione Word scaricabile.

## Funzioni principali

- definizione di una sezione composta saldata a doppio T;
- importazione di sezioni generiche da file DXF raccolti in uno ZIP;
- calcolo delle proprieta' geometriche con `sectionproperties` per le sezioni DXF;
- calcolo delle proprieta' elastiche e del peso lineare per la doppia T saldata;
- verifica elastica delle tensioni normali per `NEd`, `Mx,Ed` e `My,Ed`;
- anteprima grafica della sezione e dei risultati principali;
- generazione di una relazione Word `.docx` per il caso analizzato.

## Modalita' operative

### Sezione composta saldata a doppio T

La sezione viene definita con:

- altezza totale `h`;
- larghezza e spessore della piattabanda superiore;
- larghezza e spessore della piattabanda inferiore;
- spessore dell'anima;
- tensione di snervamento `fy`;
- coefficiente parziale `gamma_M0`.

L'app calcola area, baricentro, momenti di inerzia, raggi giratori, moduli elastici,
stima della costante torsionale e peso lineare. Inserendo le sollecitazioni di
progetto, produce anche il controllo tensionale elastico sui punti estremi della
sezione.

### Import DXF da ZIP

Caricando uno ZIP contenente file `.dxf`, l'app importa le geometrie, genera la
mesh e calcola le proprieta' geometriche e di ingobbamento tramite
`sectionproperties`. E' possibile applicare un angolo di rotazione prima del
calcolo.

Questa modalita' e' utile per sezioni non standard, sagome composte o profili
che non conviene descrivere con pochi parametri geometrici.

## Relazione Word

In entrambe le modalita' e' disponibile il pulsante per scaricare una relazione
Word:

- `SteelSectionCheck_DoppiaT.docx` per la sezione saldata;
- `SteelSectionCheck_DXF.docx` per le sezioni importate da DXF.

Il report include intestazione, data di generazione, modello di calcolo, tabelle
di input, proprieta' calcolate, verifiche disponibili e immagine della sezione.

## Installazione

```powershell
cd C:\Users\Domenico\Downloads\Temporanea\SteelSectionCheck\src
pip install -r requirements.txt
```

## Avvio

```powershell
streamlit run runApp.py
```

L'app si apre nel browser locale. Dalla barra laterale si sceglie la sorgente
della sezione:

- `Sezione composta saldata a doppio T`;
- `Import DXF da ZIP`.

## Struttura del progetto

- `src/runApp.py`: interfaccia Streamlit e flussi operativi;
- `src/steel_builtup.py`: modello e verifiche per la doppia T saldata;
- `src/steel_word.py`: generazione della relazione Word;
- `src/codes.py`: importazione DXF e calcolo proprieta' con `sectionproperties`;
- `src/requirements.txt`: dipendenze Python dell'app;
- `docs/DOCUMENTAZIONE.html`: documentazione tecnica in formato HTML.

## Note tecniche

- Le dimensioni geometriche sono inserite in millimetri.
- Le azioni sono inserite in `kN` e `kNm`.
- Le verifiche implementate sono controlli elastici di tensione normale.
- Per sezioni DXF la qualita' del risultato dipende dalla pulizia della geometria
  importata e dalla mesh generata.
- La relazione prodotta non sostituisce il controllo professionale del progettista.
