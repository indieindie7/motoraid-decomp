// SetupMotorRaid.java <prog.bin> <seeds.txt>: adds the Model 2A fast-RAM code block (ROM 0xb0000..0xcffff copied to 0x200000
// at boot) and creates a function at every seed address (one hex address per line).
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class SetupMotorRaid extends GhidraScript {
	@Override
	public void run() throws Exception {
		String[] a = getScriptArgs();
		byte[] prog = Files.readAllBytes(Paths.get(a[0]));
		Memory mem = currentProgram.getMemory();
		Address ram = toAddr(0x200000);
		if (mem.getBlock(ram) == null) {
			byte[] code = Arrays.copyOfRange(prog, 0xb0000, 0xd0000);
			var b = mem.createInitializedBlock("ram_code", ram, new ByteArrayInputStream(code), code.length, monitor, false);
			b.setRead(true); b.setWrite(true); b.setExecute(true);
			println("added ram_code 0x200000 len 0x" + Integer.toHexString(code.length));
		}
		int made = 0, bad = 0;
		for (String l : Files.readAllLines(Paths.get(a[1]))) {
			l = l.trim();
			if (l.isEmpty()) continue;
			Address at = toAddr(Long.parseLong(l.substring(2), 16));
			new DisassembleCommand(at, null, true).applyTo(currentProgram, monitor);
			if (getFunctionAt(at) == null) {
				if (createFunction(at, null) != null) made++; else bad++;
			}
		}
		println("functions made " + made + " failed " + bad + " total " + currentProgram.getFunctionManager().getFunctionCount());
	}
}
