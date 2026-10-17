"""GlitchStorm v2 - faithful KiCad transcription of the Eagle build (~/Documents/eagle/projects/GlitchStorm-v2, sch == brd).
Wired functional blocks.  usage: build_glitchstorm.py <out.kicad_sch>"""
from sch import *
import sys
OUT = sys.argv[1]
g = lambda n: round(n * 2.54, 3)
s = Sheet('GlitchStorm', 'A3')
FR = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical'
FPOT = 'Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical'
FCE = 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm'
W = lambda *p: s.wire(*p)
P = s.P
def GND(p): s.power('GND', p)
def V5(p): s.power('+5V', p)
def lab(n, p, side='r'): s.label(n, p, side)
def POT(ref, v, name, x, y, rot=0, mirror=None, text='r'):
    if text == 'r': text = ((x + 4.445, y - 1.27), (x + 4.445, y + 1.27), 'left')
    s.part(ref, 'Device', 'R_Potentiometer', v, x, y, rot, mirror=mirror, fp=FPOT, desc=f'{name} pot, 9 mm (Eagle 9MM_W/MOUNTS; no value set)', text=text, extra={'Panel': name})

# ================================================================ ARDUINO NANO + CONTROLS
s.box('ARDUINO NANO (A1) + CONTROLS: 4 pots on A0-A3, 2 buttons on D3/D4, 4 LEDs on D7-D10', g(3), g(5), g(88), g(76))
s.part('A1', 'MCU_Module', 'Arduino_Nano_v3.x', 'Arduino Nano', g(45), g(45), 0, fp='Module:Arduino_Nano', desc='Arduino Nano module (Eagle U$1)', text=((g(51), g(33)), (g(51), g(34.5)), 'left'))
V5(P('A1', '27')); GND(P('A1', '4')); GND(P('A1', '29'))
for pin in ('1', '2', '3', '5', '8', '9', '15', '16', '17', '18', '23', '24', '25', '26', '28', '30'):
    s.noconnect(P('A1', pin))
# pots: A0-A3, pin 3 = +5V, pin 1 = GND (Eagle P$3 / P$1)
for i, (ref, name, apin) in enumerate((('RV1', 'POT1', '19'), ('RV2', 'POT2', '20'), ('RV3', 'POT3', '21'), ('RV4', 'RATE', '22'))):
    xi = g(56 + 7 * i)
    POT(ref, 'POT', name, xi, g(22), rot=270, text=((xi - g(2), g(17)), (xi - g(2), g(18.5)), 'left'))
    V5(P(ref, '3')); GND(P(ref, '1'))
    q = P('A1', apin)
    W(P(ref, '2'), (xi, q[1]), q)
# buttons (Omron B3F): pins 1/2 to the Nano pin, 3/4 to ground (INPUT_PULLUP in firmware)
for ref, dpin, y in (('SW3', '6', g(42)), ('SW4', '7', g(45))):
    s.part(ref, 'Switch', 'SW_Push', 'B3F-10XX', g(27), y, 180, fp='Button_Switch_THT:SW_PUSH_6mm', desc=f'Tactile button (Eagle {ref.replace("SW", "S")})', text='t')
    q = P('A1', dpin)
    W(q, (g(32), q[1]), (g(32), y), P(ref, '1')); W(P(ref, '2'), (g(23), y)); GND((g(23), y))
# LEDs: D7 -> D4/R4, D8 -> D3/R3, D9 -> D2/R2, D10 -> D1/R1 (anode to the pin, cathode through R to GND)
for i, (dpin, led, res) in enumerate((('10', 'D4', 'R4'), ('11', 'D3', 'R3'), ('12', 'D2', 'R2'), ('13', 'D1', 'R1'))):
    xi = g(12 + 5 * i)
    s.part(led, 'Device', 'LED', 'LED', xi, g(62), 90, fp='LED_THT:LED_D3.0mm', desc='3mm LED', text='r')
    s.part(res, 'Device', 'R', 'R?', xi, g(66.5), 0, fp=FR, desc='LED resistor - NO VALUE in the Eagle design', text='r')
    q = P('A1', dpin)
    W(q, (xi, q[1]), P(led, '2')); W(P(led, '1'), P(res, '1')); GND(P(res, '2'))
q = P('A1', '14'); W(q, (g(37), q[1])); lab('D11_AUDIO', (g(37), q[1]), 'l')
s.text('POT1-3 and RATE: 9 mm pots, no value in the Eagle file. R1-R4: no value in the Eagle file.', g(5), g(74))

# ================================================================ AUDIO OUT: PWM -> VOL -> LM386 -> JACK
s.box('AUDIO: D11 PWM -> C6 / C5 -> VOL -> LM386 (U1, gain 200) -> STEREO JACK (tip + ring together)', g(92), g(5), g(160), g(76))
xa, ya = g(128), g(40)
lab('D11_AUDIO', (g(95), g(36)), 'l'); W((g(95), g(36)), (g(100), g(36)))
s.part('C6', 'Device', 'C', '100n', g(100), g(37.5), 0, fp='Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2', desc='Directly on the PWM pin (no series resistor)', text='l')
GND(P('C6', '2'))
s.part('C5', 'Device', 'C', '100n', g(104.5), g(36), 90, fp='Capacitor_THT:C_Rect_L13.0mm_W4.0mm_P10.00mm_FKS3_FKP3_MKS4', desc='Output coupling to VOL', text='t')
W((g(100), g(36)), P('C5', '1'))
POT('RV5', 'POT', 'VOL', g(110), g(40.5), mirror='x', text=((g(106), g(44)), (g(106), g(45.5)), 'left'))
W(P('C5', '2'), (g(110), g(36)), P('RV5', '3')); GND(P('RV5', '1'))
s.part('U1', 'Amplifier_Audio', 'LM386', 'LM386', xa, ya, 0, fp='Package_DIP:DIP-8_W7.62mm', desc='LM386 (Eagle IC1), powered from the Nano 5V', text=((xa + g(2), ya - g(5)), (xa + g(2), ya - g(4)), 'left'))
W(P('RV5', '2'), (g(113), P('RV5', '2')[1]), (g(113), P('U1', '3')[1]), P('U1', '3'))
W(P('U1', '2'), (xa - g(4), P('U1', '2')[1]), (xa - g(4), ya + g(3))); GND((xa - g(4), ya + g(3)))
GND(P('U1', '4')); V5(P('U1', '6'))
p1, p8 = P('U1', '1'), P('U1', '8')
s.part('C4', 'Device', 'C_Polarized', '10u', xa + g(2.5), ya + g(6), 90, fp=FCE, desc='Gain cap pins 1-8: gain 200', text='b')
W(p1, (p1[0], ya + g(6)), P('C4', '1')); W(p8, (p8[0], ya + g(4)), (xa + g(4), ya + g(4)), P('C4', '2'))
p7 = P('U1', '7')
s.part('C3', 'Device', 'C_Polarized', '47u', xa + g(6), ya - g(6.5), 0, fp=FCE, desc='Bypass (pin 7)', text='r')
W(p7, (p7[0], ya - g(8)), (xa + g(6), ya - g(8)), P('C3', '1')); GND(P('C3', '2'))
s.part('C2', 'Device', 'C_Polarized', '47u', xa + g(6.5), ya, 90, fp=FCE, desc='Output coupling', text='t')
W(P('U1', '5'), P('C2', '1'))
s.part('J1', 'Connector_Audio', 'AudioJack3', 'STEREO', xa + g(15), ya, 0, mirror='y', fp='Connector_Audio:Jack_6.35mm_Neutrik_NMJ6HCD2_Horizontal',
       desc='PCB stereo jack (Eagle STEREO_PCB; footprint is a placeholder), tip + ring tied together', text=((xa + g(15), ya - g(4)), (xa + g(15), ya - g(3)), None))
W(P('C2', '2'), (xa + g(10), ya), P('J1', 'R')); W((xa + g(10), ya), (xa + g(10), P('J1', 'T')[1]), P('J1', 'T'))
W(P('J1', 'S'), (xa + g(11), P('J1', 'S')[1]), (xa + g(11), ya - g(3))); GND((xa + g(11), ya - g(3)))
s.text('Issues: no series R on D11 (C6 loads the pin directly); gain 200 with a 5 V PWM source; no Zobel;', g(94), g(70))
s.text('mono plug shorts ring to sleeve = LM386 output to ground through C2. See the GlitchStorm roadmap.', g(94), g(72))

# ================================================================ POWER
s.box('POWER (from the Nano 5V pin - USB)', g(3), g(80), g(88), g(112))
V5((g(10), g(86))); W((g(10), g(86)), (g(10), g(88)))
s.part('C1', 'Device', 'C_Polarized', '47u', g(10), g(88) + 3.81, 0, fp=FCE, desc='5V bulk', text='r'); GND(P('C1', '2'))
s.power('PWR_FLAG', (g(20), g(90))); GND((g(20), g(90)))
s.text('No external power input: the board runs from the Nano (USB, or VIN not wired).', g(5), g(104))

s.write(OUT, {'title': 'GlitchStorm v2 (as built)', 'date': '2026-09-29', 'rev': 'Eagle 2025-09',
              'company': 'Super-Freq',
              'comments': ['Faithful transcription of ~/Documents/eagle/projects/GlitchStorm-v2 (sch == brd)',
                           'Arduino Nano bytebeat synth: PWM audio on D11 -> LM386 -> jack',
                           'Refs: U$1=A1, IC1=U1, POT1-3/RATE/VOL=RV1-5, S3/S4=SW3/SW4']})
print('ok', len(s.syms), 'symbols')
