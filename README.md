# Pythonen æder påskeæggene
En scriptløsning på FE's gækkebrev 2026.

## Gækkebrev:
4 billeder med læsebar tekst og der imellem indsat rækker af forskellige æg-symboler.
Æg-symboler repræsenterer bogstaver, som efter afkryptering tilsammen danner ord, der i kombination med den læsebare tekst kan svare på: "Hvem er afsenderen af årets gækkebrev, og gemmer der sig mon andre budskaber i brevet?"<br>
Det andet budskab er indkodet som binært signal ved at de enkelte æg-symboler enten vender op eller ned; 1 / 0

## Løsning

### Substitutionskode

#### Kort fortalt
Python-scriptet forsøger at finde ud af, hvilke bogstaver de forskellige æg-symboler står for.
Det gør scriptet ved at sammenligne mønstrene i den krypterede tekst med en dansk ordliste.
Når scriptet har fundet de mest sandsynlige bogstavvalg, for hvert enkelte ord, tester det dem samlet og vælger den løsning, der giver flest rigtige danske ord.

#### Længere fortalt
Alle æg-symboler hver især er indtastet manuelt i **input.txt** med hvert deres unikke bogstav som repræsentant. 
Et python-script **paralleltest.py** gennemgår så hver hvert ord, der dannes ved, at et bestemt bogstav (æg-symbol) i forvejen er *mappet* (valgt som repræsentant) til  ' ', mellemrumstegnet.<br> 
For ikke at skulle bruteforce igennem et kvadratet af alle det danske skriftsprogs bogtaver, udvindes et subset af mulige *bogstavmappinger* før disse så bruteforces igennem.<br> 
Først testes hvert krypteret ords bestemte bogstavkombination op mod et leksikon over danske ord. Alle de leksikonord, der opfylder det krypterede ords bogstavkombination findes, og ud fra dem, opsamles  alle de *bogstavmappinger*, der skal bruges til at afkode de enkelte krypterede ord til danske ord hver især.<br> 
Hvert bogstav (æg-symbol) er stadig mappet til flere mulige bogstaver, men ikke alle. En intersektion af alle disse mulige *bogstavmappinger* er det subset hvori, der skal findes det bestemte alfabet af *bogstavmappinger* , der kan afkode hele den krypterede tekst samlet. Dette gøres ved at udelukke alle de *bogstavmapping* alfabeter der ikke kan bruges til at dekryptere *alle* de krypterede ord til rigtige danske ord. Her bruges der en bruteforce gennemgang af alle *bogstavmapping* alfabeterne, og til dét anvendes der parallelisering, så det tager ~14,5 sekunder på min egen PC.

Denne metode kan dog ikke nødvendigvis finde en *bogstavmapping* for bogstaver (æg-symboler) der kun optræder 1 gang i teksten. Hvis flere danske ord kun har 1 bogstav til forskel indbyrdes, men har netop samme bogstavkombination som det krypterede ord hvori bogstavet optræder, så må løsningen nøjes med en ambivalens mellem flere danske ord, som så må udvælges  med sund fornuft.

#### Resultat
```text
Mapping fundet:
[{'Q': 'I', 'G': 'D', 'P': 'A', 'R': 'N', 'B': 'E', 'U': 'C', 'K': 'O', 'M': 'S', 'J': 'L', 'L': 'T', 'C': 'G', 'O': 'M', 'A': 'J', 'E': 'R', 'F': 'Å', 'H': 'Æ', 'I': 'V', 'N': 'Å', 'S': 'K', 'T': 'B', 'V': 'Y', 'W': 'Æ', 'X': 'F'}]
Dekryptering:
['JEG', 'RIDE/RODE/RUDE/RYDE/RÅDE/RØDE', 'DJÆVLE', 'OG', 'TROLDE', 'DET', 'STAR/STOR/STYR/STÅR/STÆR/STØR', 'MED', 'MALEDE', 'ÆG', 'INDEN', 'MIN', 'SKÆBNE', 'BLEV', 'CYANID', 'ALAN', 'TURING/TÆRING', 'DATALOGIENS', 'BADER/FADER/HADER/JADER/KADER/LADER/NADER/VADER', 'ENCODED', 'I', 'ASCII']
Tid: 14.22s
```

**Afsenderen er Alan Turing, Datalogiens fader**

#### Antagelser:
- Æg-symbolet som er det eneste ikke malede repræsenterer mellemrum tegnet, er indtastet som 'D' i **input.txt**, det giver også god semantisk mening
- Den krypterede tekst er substitutionskodet; kun 1 æg-symbol repræsenterer kun 1 unikt bogstav. Ingen Enigmakode her.
- Alle ord som kan dannes ud fra den krypterede tekst er også at finde i leksikonet.


### Binære signal   
Æg-symbolernes retning indtastes som '1' eller '0' i *input2.txt*.
I *onesandzeroes.py* indlæses bitsekvensen fra *input2.txt* og sekvensen opdeles i 8-bit bytes. Hver byte konverteres fra binær til ASCII, så den skjulte tekst kan læses direkte.
Som kontrol prøver scriptet også en inverteret version (0/1 byttet om) med bitvis NOT. Det viser, om signalet muligvis er indtastet omvendt.

#### Resultat
```text
120 bit

Prøver 8-bit ASCII: 
10101100 00000111 10011000 10011011 10010110 10001011 10010001 10000110 10011010 10010101 10010000 10011101 10010110 10111001 10111010
'¬' '' '' '' '' '' '' '' '' '¹' 'º' 

Prøver med NOT:
01010011 11111000 01100111 01100100 01101001 01110100 01101110 01111001 01100101 01101010 01101111 01100010 01101001 01000110 01000101
'S' 'ø' 'g' 'd' 'i' 't' 'n' 'y' 'e' 'j' 'o' 'b' 'i' 'F' 'E' 
```

**Det andet budskab i beskeden er :Søg dit nye job i FE**





## TODO:
- Udvid scriptet med gennemgang af mulige repræsentationer af mellemrum.
- ~~Lav script der med en indtastet repræsentation af det binære signal, finder en meningsfuld besked - muligvis vha. ASCII værdier eller Base64~~
