doc = Document.getCurrentDocument()
seg = doc.getCurrentSegment()
adr = doc.getCurrentAddress()
ins = seg.getInstructionAtAddress(adr)
arch = ins.getArchitecture()


def patch_aarm64(b):
    opcode = b & 0x17000000 | 0x04000000
    offset = (b & 0x03FFFFFF) >> 5
    final = opcode | offset

    seg.writeUInt32LE(adr, final)
    seg.markAsCode(adr)


def unknown():
    doc.log("Unknown conditional jump!")


if not ins.isAConditionalJump:
    doc.log("This is not conditional jump!")
else:
    if arch is ins.ARCHITECTURE_X86_64:
        b = seg.readByte(adr)
        if 0x70 <= b <= 0x7F:
            # rel8
            seg.writeByte(adr, 0xEB)
            seg.markAsCode(adr)
        elif b == 0x0F:
            b = seg.readByte(adr + 1)
            if 0x80 <= b <= 0x8F:
                # rel16/32
                seg.writeByte(adr, 0x90)
                seg.writeByte(adr + 1, 0xE9)
                seg.markAsCode(adr)
            else:
                unknown()
        else:
            unknown()
    elif arch in ins.ARCHITECTURE_AARCH64:
        b = seg.readUInt32LE(adr)

        if (b >> 24) & 0x2F in (0x25, 0x24):
            doc.log("Recognized cbnz Rt / cbz Rt !")
            patch_aarm64(b)
        elif (b >> 24) & 0xEF == 0x44:
            doc.log("Recognized b.c jump!")
            patch_aarm64(b)
        else:
            unknown()
    else:
        doc.log("Unsupported arch!")
