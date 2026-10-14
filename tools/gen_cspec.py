import sys
out=sys.argv[1]
ins=''.join('        <pentry minsize="4" maxsize="4"><register name="g%d"/></pentry>\n'%i for i in range(12))
un=''.join('        <register name="%s"/>\n'%n for n in ['pfp','rip']+['r%d'%i for i in range(3,16)])
kb=''.join('        <register name="g%d"/>\n'%i for i in range(15))
x='''<?xml version="1.0" encoding="UTF-8"?>
<compiler_spec>
  <data_organization>
    <absolute_max_alignment value="0"/><machine_alignment value="4"/><default_alignment value="1"/>
    <default_pointer_alignment value="4"/><pointer_size value="4"/><wchar_size value="2"/>
    <short_size value="2"/><integer_size value="4"/><long_size value="4"/><long_long_size value="8"/>
    <float_size value="4"/><double_size value="8"/><long_double_size value="8"/>
  </data_organization>
  <global><range space="ram"/></global>
  <stackpointer register="sp" space="ram" growth="positive"/>
  <default_proto>
    <prototype name="__stdcall" extrapop="0" stackshift="0">
      <input>
%s      </input>
      <output>
        <pentry minsize="1" maxsize="4"><register name="g0"/></pentry>
        <pentry minsize="5" maxsize="8"><register name="g0g1"/></pentry>
        <pentry minsize="9" maxsize="12"><register name="g0g1g2"/></pentry>
        <pentry minsize="13" maxsize="16"><register name="g0g1g2g3"/></pentry>
      </output>
      <unaffected>
%s        <register name="fp"/><register name="sp"/>
      </unaffected>
      <killedbycall>
%s      </killedbycall>
    </prototype>
  </default_proto>
</compiler_spec>
'''
open(out+'/i960.cspec','w').write(x%(ins,un,kb))
