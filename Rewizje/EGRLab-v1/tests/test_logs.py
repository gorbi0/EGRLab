import io
import json
import math
from pathlib import Path
import struct
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]/'tools'))
import egrlog as log

class LogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'sample.egr';log.synth(self.path)
    def test_abi(self):
        self.assertEqual(log.HEADER.size,32);self.assertEqual(log.BLOCK.size,16);self.assertEqual(log.RECORD.size,32)
    def test_roundtrip(self):
        r=log.inspect(self.path);self.assertTrue(r['synthetic']);self.assertEqual(r['records'],4000)
        self.assertEqual(r['max_dt_us'],500);self.assertEqual(r['gap_flags'],0)
    def test_crc_failure_is_not_recovered(self):
        data=bytearray(self.path.read_bytes());data[60]^=1;self.path.write_bytes(data)
        with self.assertRaisesRegex(log.LogError,'CRC'):log.inspect(self.path,True)
    def test_truncated_last_block(self):
        self.path.write_bytes(self.path.read_bytes()[:-19])
        with self.assertRaisesRegex(log.LogError,'Truncated'):log.inspect(self.path)
        r=log.inspect(self.path,True);self.assertEqual(r['records'],3968);self.assertTrue(r['warnings'])
    def test_invalid_count(self):
        data=bytearray(self.path.read_bytes());struct.pack_into('<I',data,36,0xffffffff);self.path.write_bytes(data)
        with self.assertRaises(log.LogError):log.inspect(self.path)
    def test_both_polarities_ratiometric(self):
        meta=dict(log.DEFAULT_META,gain=[1]*8,offset=[0]*8)
        for pin in (5,6):
            v=[0,0,2.5,5,0,2.5,2.5,10]
            if pin==6:v[3],v[4]=v[4],v[3]
            raw=[min(32767,round(x*32768/10)) for x in v]
            row=(1,0,*raw,0,0);meta['supply_pin']=pin
            result=log.physical(row,meta);self.assertAlmostEqual(result[-2],.5,places=4)
    def test_unknown_polarity(self):
        meta=dict(log.DEFAULT_META,supply_pin=0)
        self.assertTrue(math.isnan(log.physical((1,0,*([0]*8),0,0),meta)[-2]))
    def test_export(self):
        target=self.path.with_suffix('.csv')
        log.export(self.path,self.path.with_suffix('.json'),target)
        self.assertEqual(len(target.read_text().splitlines()),4001)
    def test_non_monotonic_time(self):
        rows=[(10,0,*([0]*8),0,0),(9,1,*([0]*8),0,0)]
        log.write_log(self.path,rows)
        with self.assertRaisesRegex(log.LogError,'monotonic'):log.inspect(self.path)

if __name__=='__main__':unittest.main()
