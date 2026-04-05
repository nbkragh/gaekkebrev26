# Pythonen æder påskeæggene
En scriptløsning på FE's gækkebrev 2026.

## Gækkebrev:
4 billeder med læsebar tekst og der imellem indsat rækker af forskellige æg-ikoner.
Æg-ikonerne repræsenterer *formentlig* bogstaver, som efter afkryptering tilsammen danner ord, der i kombination med den læsebare tekst kan svare på:
"Hvem er afsenderen af årets gækkebrev, og gemmer der sig mon andre budskaber i brevet?"
Det andet budskab er *formentligt* indkodet som binært signal ved at de enkelte æg-ikoner enten vender op eller ned; 1 / 0

## Løsning:
Alle æg-ikonerne hver især er indtastet manuelt i **input.txt** med hvert deres unikke bogstav som repræsentant. 
Et python-script **paralleltest.py** gennemgår så hver hvert ord dannet af at et bestemt bogstav/æg-ikon er *mappet* til  
' ' mellemrum. Hver bogstavkombination i hvert ord testes så op imod et leksikon over danske ord. Ved finde reelle danske ord der opfylder bogstavkombination og udvælge kun de bogstav-til-bogstav mappinger der optræder i alle de fundne ord, kan der laves et subset af mulige bogstav-til-bogstav mappinger, som den krypteret tekst tillader.   
Hver mulig bogstav-til-bogstav mapping sættes så sammen til et "alfabet" af mappinger, og hver af sådanne mulige alfabeter
testest der som de danner et rigtigt dansk ord hvert krypteret ord. Det bogstav-til-bogstav-mapping-alfabet, der danner flest rigtige danske ord vinder!

## Antagelser:

- Den krypteret tekst er substitutionskodet; kun 1 æg-ikon repræsenterer kun 1 unikt bogstav. Ingen Enigmakode her.
- Alle ord som kan dannes ud fra den krybterede tekst er også at finde i leksikonet.
- Æg-ikonet som er det eneste ikke malede repræsenterer mellemrum tegnet, er indtastet som 'D' i **input.txt**, det giver også god semantisk mening

## TODO:
Udvid scriptet med gennemgang af mulige repræsentationer af mellemrum.
Lav script der med en indtastet repræsentation af det binære signal, finder en meningsfuld besked - muligvis vha. ASCII værdier eller Base64
