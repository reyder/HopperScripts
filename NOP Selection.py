doc = Document.getCurrentDocument()
seg = doc.getCurrentSegment()
adr = doc.getCurrentAddress()
start, end = doc.getSelectionAddressRange()
ins = seg.getInstructionAtAddress(adr)
arch = ins.getArchitecture()

AARCH64_NOP = 0x1F2003D5
X86_NOP = 0x90


def nop_code():
    i = 1 if arch is ins.ARCHITECTURE_X86_64 else 4
    start_proc = seg.getProcedureAtAddress(start).getEntryPoint()

    for x in range(start, end, i):
        if arch is ins.ARCHITECTURE_X86_64:
            seg.writeByte(x, X86_NOP)
        else:
            seg.writeUInt32BE(x, AARCH64_NOP)

        seg.markAsCode(x)

    seg.markAsProcedure(start_proc)


if arch is ins.ARCHITECTURE_X86_64:
    nop_code()
elif arch in ins.ARCHITECTURE_AARCH64:
    if (end - start) % 4 != 0:
        doc.log("Something is really wrong here")
    else:
        nop_code()
else:
    doc.log("Unsupported architecture !")
