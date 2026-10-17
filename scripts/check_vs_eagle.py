"""Compare the KiCad netlist with the Eagle GlitchStorm-v2 board netlist (eagle_brd_nets.txt)."""
import re, sys
REF = {'U$1': 'A1', 'IC1': 'U1', 'POT1': 'RV1', 'POT2': 'RV2', 'POT3': 'RV3', 'RATE': 'RV4', 'VOL': 'RV5', 'S3': 'SW3', 'S4': 'SW4'}
NANO = {'5V': '27', 'GND': '4', 'D3': '6', 'D4': '7', 'D7': '10', 'D8': '11', 'D9': '12', 'D10': '13', 'D11': '14', 'A0': '19', 'A1': '20', 'A2': '21', 'A3': '22'}
def eag(ref, pad):
    r = REF.get(ref, ref)
    if ref == 'U$1': pad = NANO[pad]
    elif ref.startswith(('POT', 'RATE', 'VOL')): pad = pad.replace('P$', '')
    elif ref in ('S3', 'S4'): pad = '1' if pad in ('1', '2') else '2'
    elif ref == 'J1': pad = {'P$1': 'S', 'P$2': 'TR', 'P$3': 'TR'}[pad]
    elif ref.startswith('D'): pad = {'ANODE': '2', 'P$1': '1'}[pad]
    elif ref in ('C1', 'C2', 'C3', 'C4'): pad = {'+': '1', '-': '2'}[pad]
    elif re.match(r'^(R\d|C[56])$', ref): pad = '*'
    return r, pad
def kic(ref, pad):
    if ref == 'A1' and pad == '29': pad = '4'
    if ref == 'J1' and pad in ('T', 'R'): pad = 'TR'
    if re.match(r'^(R\d|C[56])$', ref): pad = '*'
    return ref, pad
E_ = set()
for l in open(sys.argv[1]):
    q = l.split()
    if len(q) < 2 or "('" in l: continue
    n = frozenset(eag(*x.rsplit('.', 1)) for x in q[1:])
    if len(n) > 1: E_.add(n)
K_ = set()
for b in re.split(r'\(net\s*\(code', open(sys.argv[2]).read())[1:]:
    n = frozenset(kic(r, p) for r, p in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"', b) if not r.startswith('#'))
    if len(n) > 1: K_.add(n)
print('matches the Eagle board:', E_ == K_)
for x in E_ - K_: print(' eagle only:', sorted(x))
for x in K_ - E_: print(' kicad only:', sorted(x))
