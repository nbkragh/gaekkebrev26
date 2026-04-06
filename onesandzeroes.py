


binaryText = ""
with open("input2.txt", encoding="utf-8") as filecontent:
    binaryText = "".join(line.strip() for line in filecontent)

print(str(len(binaryText))+" bit\n")
Bytes = " ".join(binaryText[i:i+8] for i in range(0, len(binaryText), 8))
print("Prøver 8-bit ASCII: ")
print(Bytes)
binaryText = "".join(binaryText.split())
for i in range(0, len(binaryText), 8):
    byte = binaryText[i:i+8]
    asciiValue = int(byte, 2)
    print("'" + chr(asciiValue) + "'", end=" ")

print("\n\nPrøver med NOT:")
print(" ".join("".join('1' if bit == '0' else '0' for bit in byte) for byte in Bytes.split()))
for i in range(0, len(binaryText), 8):
    byte = binaryText[i:i+8]
    asciiValue = int(byte, 2)
    invertedValue = asciiValue ^ 0xFF
    print("'" + chr(invertedValue) + "'", end=" ")