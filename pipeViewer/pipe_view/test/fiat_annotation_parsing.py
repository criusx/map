#!/usr/bin/env python



import re

a = "000 U506.1- ---- :03                :sI03            (IAdec4        cbnz      r3, 0x000000000000dee6  ) 'INT_DIR_BRANCH_REGRD' (0) parent(#506 @dec4: 0xb97b0000 t32 dbid=8297) [INT_DIR_BRANCH_REGRD, vaddr: 0x0, srcs_rdy:F, dst_rdy:F, comp:F Operands: {Source, Rn_16_3, Integer, arch_reg=3, phys_reg=?? Ready:F}]"
b = 'addr= 7001c  pick=y'
c = 'R5L LD 0x70000 beat=---- 181 dep=()( 366)()()'

expr_a = re.compile('^(?:(?P<reason>R[\w]c)|(?P<uid>[0-9a-zA-Z]{3})) U(?P<chapter>[0-9]+)\.(?P<section>[0-9]+)([-A-Za-z<\+]) (.)(.)(.)(.) (?P<operands>(?::[a-zA-Z]?[a-zA-Z]?[0-9]{2}\s+)+) \((?P<addr_type>[IV]A?)(?P<addr>[0-9a-fA-F]{1,16})\s+(?P<inst_mnemonic>\S+)\s+(?P<inst_operands>(?:\w+)?(?:,\s+(?:\w+))*)\s*\)\s+\'(\w+)\'')

print 'find'
print expr_a.findall(a)

print 'search'
search_a = expr_a.search(a)
print dir(search_a)

print 'match'
match_a = expr_a.match(a)
print dir(match_a)

print 'finditer'
iter_a = expr_a.finditer(a)
for x in iter_a:
    print x

print '\nMatches By Group:'
for x,y in match_a.groupdict().iteritems():
    print '{0:>16s}: {1}'.format(x,'"{}"'.format(y) if isinstance(y, str) else y)