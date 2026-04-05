


binaryText = ""
with open("input2.txt", encoding="utf-8") as filecontent:
    binaryText = "".join(line.strip() for line in filecontent)
    print(binaryText+"\n", "længde: "+str(len(binaryText)), "\n")

for i in range(0, len(binaryText), 8):
    byte = binaryText[i:i+8]
    print(byte, end=": ")
    asciiValue = int(byte, 2)
    print(chr(asciiValue), end="\n")

print("\nPrøver  NOT:\n")
for i in range(0, len(binaryText), 8):
    byte = binaryText[i:i+8]
    print("".join("1" if letter == "0" else "0" for letter in byte), end=": ")
    asciiValue = int(byte, 2)
    invertedValue = asciiValue ^ 0xFF
    print(chr(invertedValue), end="\n")