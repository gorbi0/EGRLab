from pathlib import Path
import pcbnew as p
import json,math
E=Path(__file__).resolve().parent
S=Path('C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji')
B=p.LoadBoard(str(S/'Plytki/M1-R1-review/eda/M1.kicad_pcb'))
mm=lambda v:round(p.ToMM(v),6)
pt=lambda v:[mm(v.x),mm(v.y)]
selected=['K_PLUS','K_MINUS','INA_INP','INA_INM','ADC_CH1','P1_ECU','P1_EGR','VBUS','BAT_P']
nets={}
for name in sorted(set(t.GetNetname() for t in B.GetTracks())):
    if name in selected or 'K_' in name or 'INA' in name:
        tracks=[t for t in B.GetTracks() if t.GetNetname()==name and t.GetClass()!='PCB_VIA']
        vias=[t for t in B.GetTracks() if t.GetNetname()==name and t.GetClass()=='PCB_VIA']
        nets[name]={'segment_length_mm':round(sum(mm(t.GetLength()) for t in tracks),3),
                    'segments':[{'start':pt(t.GetStart()),'end':pt(t.GetEnd()),'layer':B.GetLayerName(t.GetLayer()),'width':mm(t.GetWidth())} for t in tracks],
                    'vias':[pt(t.GetPosition()) for t in vias]}
out={'nets':nets,'pads':{f.GetReference():{q.GetNumber():{'pos':pt(q.GetPosition()),'size':pt(q.GetSize()),'net':q.GetNetname()} for q in f.Pads()} for f in B.GetFootprints() if f.GetReference() in ['RSH1','U3','U4','R22','R23','R11','R12']},
     'TPS2553_232k_1pct_mA':{'min':25230/(232*1.01)**1.016,'nom':23950/232**.977,'max':22980/(232*.99)**.94},
     'INA_gain_10ohm':50*3000/3010,'volts_per_amp_with_10ohm':.005*50*3000/3010,
     'shunt_watts_7p5A':7.5**2*.005,'shunt_watts_10A':10**2*.005,
     'current_zero_shift_per_10mV_5V_change_A':(.010/2)/(.005*50*3000/3010),
     'R2_4p7k_GPIO39_3p3V_PU45k_typ_V':3.3*4.7/(45+4.7),
     'Rpu_min_for_0p8V_3p6V_Rpd4p747k_kohm':4.747*(3.6/.8-1)}
(E/'geometry-and-calculations.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({n:{k:v for k,v in d.items() if k!='segments'} for n,d in nets.items()},indent=2))
print(json.dumps({k:v for k,v in out.items() if k not in ['nets','pads']},indent=2))
