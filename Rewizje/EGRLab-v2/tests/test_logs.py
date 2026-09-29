import json
import math
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / 'tools'))
import egrlog as log


class LogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.path = self.dir / 'samples.egr'
        log.synth(self.path)
        self.meta = self.path.with_suffix('.json')

    def test_abi(self):
        self.assertEqual(log.HEADER.size, 32)
        self.assertEqual(log.BLOCK.size, 16)
        self.assertEqual(log.RECORD.size, 32)

    def test_roundtrip_is_version_2(self):
        r = log.inspect(self.path)
        self.assertEqual(r['version'], 2)
        self.assertTrue(r['synthetic'])
        self.assertEqual(r['records'], 4000)
        self.assertEqual(r['max_dt_us'], 500)
        self.assertEqual(r['gap_flags'], 0)

    def test_version_1_files_still_read(self):
        rows = [(1, 0, *([0] * 8), 0, 0), (501, 1, *([0] * 8), 0, 0)]
        old = self.dir / 'old.egr'
        log.write_log(old, rows, version=1)
        self.assertEqual(log.inspect(old)['version'], 1)
        self.assertIn('vprot_v', log.columns(1))
        self.assertIn('vbat_v', log.columns(2))

    def test_crc_failure_is_not_recovered(self):
        data = bytearray(self.path.read_bytes())
        data[60] ^= 1
        self.path.write_bytes(data)
        with self.assertRaisesRegex(log.LogError, 'CRC'):
            log.inspect(self.path, True)

    def test_truncated_last_block(self):
        self.path.write_bytes(self.path.read_bytes()[:-19])
        with self.assertRaisesRegex(log.LogError, 'Truncated'):
            log.inspect(self.path)
        r = log.inspect(self.path, True)
        self.assertEqual(r['records'], 3968)
        self.assertTrue(r['warnings'])

    def test_invalid_count(self):
        data = bytearray(self.path.read_bytes())
        struct.pack_into('<I', data, 36, 0xffffffff)
        self.path.write_bytes(data)
        with self.assertRaises(log.LogError):
            log.inspect(self.path)

    def test_every_channel_permutation_gives_the_same_ratio(self):
        """Ratio nie może zależeć od tego, na których pinach siedzi trójka."""
        base = dict(log.DEFAULT_META, gain=[1] * 8, offset=[0] * 8, full_scale=[10] * 8)
        for supply, ground, feedback in ((2, 3, 4), (2, 4, 3), (3, 2, 4),
                                         (3, 4, 2), (4, 2, 3), (4, 3, 2)):
            v = [0] * 8
            v[ground], v[supply], v[feedback] = 0.0, 5.0, 2.5
            raw = [min(32767, round(x * 32768 / 10)) for x in v]
            meta = dict(base, ch_supply=supply, ch_ground=ground, ch_feedback=feedback)
            result = log.physical((1, 0, *raw, 0, 0), meta)
            self.assertAlmostEqual(result[-2], .5, places=4,
                                   msg=f'permutacja {supply},{ground},{feedback}')

    def test_v1_supply_pin_mapping_still_works(self):
        meta = dict(log.DEFAULT_META, gain=[1] * 8, offset=[0] * 8, full_scale=[10] * 8)
        for key in ('ch_supply', 'ch_ground', 'ch_feedback'):
            meta.pop(key)
        for pin in (5, 6):
            v = [0, 0, 2.5, 5, 0, 2.5, 13, 0]
            if pin == 6:
                v[3], v[4] = v[4], v[3]
            raw = [min(32767, round(x * 32768 / 10)) for x in v]
            meta['supply_pin'] = pin
            self.assertAlmostEqual(log.physical((1, 0, *raw, 0, 0), meta)[-2], .5, places=4)

    def test_unknown_mapping_is_nan_not_zero(self):
        meta = dict(log.DEFAULT_META, ch_supply=None, ch_ground=None, ch_feedback=None)
        meta.pop('ch_supply')
        result = log.physical((1, 0, *([0] * 8), 0, 0), dict(meta, supply_pin=0))
        self.assertTrue(math.isnan(result[-2]))
        self.assertTrue(math.isnan(result[-1]))

    def test_full_scale_changes_volts(self):
        meta = dict(log.DEFAULT_META, gain=[1] * 8, offset=[0] * 8)
        coarse = dict(meta, full_scale=[10] * 8)
        fine = dict(meta, full_scale=[2.5] * 8)
        raw = [1000] * 8
        a = log.physical((1, 0, *raw, 0, 0), coarse)[11]
        b = log.physical((1, 0, *raw, 0, 0), fine)[11]
        self.assertAlmostEqual(a / b, 4.0, places=6)

    def test_current_zero_is_applied(self):
        meta = dict(log.DEFAULT_META, gain=[1] * 8, offset=[0] * 8,
                    full_scale=[10] * 8, current_zero=2.6)
        raw = [0] * 8
        raw[5] = round(2.6 * 32768 / 10)
        self.assertAlmostEqual(log.physical((1, 0, *raw, 0, 0), meta)[-4], 0.0, places=3)

    def test_export(self):
        target = self.dir / 'out.csv'
        log.export(self.path, self.meta, target)
        lines = target.read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(lines), 4001)
        self.assertIn('aux_v', lines[0])

    def test_report_html(self):
        target = self.dir / 'out.html'
        log.report(self.path, self.meta, target)
        text = target.read_text(encoding='utf-8')
        self.assertIn('DANE SYNTETYCZNE', text)
        self.assertIn('"ground"', text)

    def test_scan_reads_events(self):
        events = self.dir / 'events.ndjson'
        events.write_text(
            '{"type":"mark","t_us":1000}\n'
            '{"type":"trigger","t_us":1200,"name":"ground"}\n'
            '{"type":"trigger","t_us":9000,"name":"ground"}\n'
            'to nie jest json\n'
            '{"type":"hotsoak_point","index":0,"tc1":92.5,"i_break_open":0.61}\n',
            encoding='utf-8')
        r = log.scan(events)
        self.assertEqual(r['triggers']['ground'], 2)
        self.assertEqual(r['first_trigger_us']['ground'], 1200)
        self.assertEqual(r['marks_us'], [1000])
        self.assertEqual(len(r['hotsoak_points']), 1)
        self.assertTrue(r['warnings'])

    def test_non_monotonic_time(self):
        rows = [(10, 0, *([0] * 8), 0, 0), (9, 1, *([0] * 8), 0, 0)]
        log.write_log(self.path, rows)
        with self.assertRaisesRegex(log.LogError, 'monotonic'):
            log.inspect(self.path)


if __name__ == '__main__':
    unittest.main()
