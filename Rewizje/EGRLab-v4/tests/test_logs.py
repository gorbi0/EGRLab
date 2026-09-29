import csv
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

    def rows(self, csv_path):
        with open(csv_path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    # --- format -----------------------------------------------------------
    def test_abi(self):
        self.assertEqual(log.HEADER.size, 32)
        self.assertEqual(log.BLOCK.size, 16)
        self.assertEqual(log.RECORD.size, 32)

    def test_roundtrip_is_version_4(self):
        r = log.inspect(self.path)
        self.assertEqual(r['version'], 4)
        self.assertTrue(r['synthetic'])
        self.assertEqual(r['records'], 4000)
        self.assertEqual(r['max_dt_us'], 500)
        self.assertEqual(r['gap_flags'], 0)
        self.assertEqual(sorted(r['config_ids']), [1, 2])

    def test_older_versions_still_read(self):
        rows = [(1, 0, *([0] * 8), 0, 0), (501, 1, *([0] * 8), 0, 0)]
        for version, name in ((1, 'v1.egr'), (2, 'v2.egr')):
            old = self.dir / name
            log.write_log(old, rows, version=version)
            self.assertEqual(log.inspect(old)['version'], version)
        self.assertIn('vprot_v', log.columns(1))
        self.assertIn('vbat_v', log.columns(2))
        self.assertIn('config_id', log.columns(3))

    # --- regresja F06: zmiana konfiguracji w trakcie sesji -----------------
    def test_range_change_does_not_change_exported_voltage(self):
        """Ten sam sygnal fizyczny przy dwoch zakresach musi dac to samo napiecie.

        W v2 kanal masy po przejsciu na +-2,5 V eksportowal sie razy cztery,
        czyli 20 mV wygladalo jak 80 mV — dokladnie tam, gdzie szukamy H2.
        """
        target = self.dir / 'out.csv'
        log.export(self.path, target)
        rows = self.rows(target)
        first = [r for r in rows if r['config_id'] == '1']
        second = [r for r in rows if r['config_id'] == '2']
        self.assertTrue(first and second)
        a = float(first[10]['pin6_v'])
        b = float(second[10]['pin6_v'])
        # Tolerancja to polowa dzialki danego zakresu: 311 uV przy +-10 V,
        # 78 uV przy +-2,5 V. Blad v2 wynosil 60 mV, czyli 400 dzialek.
        self.assertLess(abs(a - 0.025), 160e-6, 'zakres +-10 V: poza kwantyzacja')
        self.assertLess(abs(b - 0.025), 40e-6, 'zakres +-2,5 V: poza kwantyzacja')
        self.assertLess(abs(a - b), 200e-6, 'zmiana zakresu przesunela napiecie')
        # I dla porzadku: drobniejszy zakres ma byc blizej prawdy.
        self.assertLessEqual(abs(b - 0.025), abs(a - 0.025) + 1e-9)

    def test_current_zero_follows_config(self):
        """Zero pradu jest per konfiguracja, nie jedno na cala sesje."""
        target = self.dir / 'out.csv'
        log.export(self.path, target)
        rows = self.rows(target)
        # W obu konfiguracjach prad zerowy jest modulowany ta sama sinusoida
        # wokol wlasnego zera, wiec srednia musi wyjsc bliska zeru w obu.
        for config_id in ('1', '2'):
            values = [float(r['current_a']) for r in rows if r['config_id'] == config_id]
            self.assertLess(abs(sum(values) / len(values)), 0.02,
                            f'config {config_id}: zero pradu nie zostalo zastosowane')

    def test_missing_config_event_is_reported(self):
        events = self.dir / 'events.ndjson'
        kept = [line for line in events.read_text(encoding='utf-8').splitlines()
                if '"config_id": 2' not in line.replace('"config_id":2', '"config_id": 2')]
        events.write_text('\n'.join(kept) + '\n', encoding='utf-8')
        warnings = log.export(self.path, self.dir / 'out.csv')
        self.assertTrue(any('config_id=2' in w for w in warnings), warnings)

    def test_current_invalid_exports_empty_not_zero(self):
        cfg = log.config_event(1, current_valid=False, gain=[1] * 8, offset=[0] * 8,
                               full_scale=[10] * 8)
        raw = [0] * 8
        raw[5] = 16384
        result = log.physical((1, 0, *raw, 0, 1), cfg)
        self.assertTrue(math.isnan(result[-4]))

    # --- mapowanie pinow ---------------------------------------------------
    def test_every_channel_permutation_gives_the_same_ratio(self):
        base = dict(log.DEFAULT_META, gain=[1] * 8, offset=[0] * 8, full_scale=[10] * 8)
        for supply, ground, feedback in ((2, 3, 4), (2, 4, 3), (3, 2, 4),
                                         (3, 4, 2), (4, 2, 3), (4, 3, 2)):
            v = [0] * 8
            v[ground], v[supply], v[feedback] = 0.0, 5.0, 2.5
            raw = [min(32767, round(x * 32768 / 10)) for x in v]
            cfg = dict(base, ch_supply=supply, ch_ground=ground, ch_feedback=feedback)
            result = log.physical((1, 0, *raw, 0, 1), cfg)
            self.assertAlmostEqual(result[-2], .5, places=4,
                                   msg=f'permutacja {supply},{ground},{feedback}')

    def test_v1_supply_pin_mapping_still_works(self):
        cfg = dict(log.DEFAULT_META, gain=[1] * 8, offset=[0] * 8, full_scale=[10] * 8)
        for key in ('ch_supply', 'ch_ground', 'ch_feedback'):
            cfg.pop(key)
        for pin in (5, 6):
            v = [0, 0, 2.5, 5, 0, 2.5, 13, 0]
            if pin == 6:
                v[3], v[4] = v[4], v[3]
            raw = [min(32767, round(x * 32768 / 10)) for x in v]
            cfg['supply_pin'] = pin
            self.assertAlmostEqual(log.physical((1, 0, *raw, 0, 1), cfg)[-2], .5, places=4)

    def test_unknown_mapping_is_nan_not_zero(self):
        cfg = dict(log.DEFAULT_META, supply_pin=0)
        for key in ('ch_supply', 'ch_ground', 'ch_feedback'):
            cfg.pop(key)
        result = log.physical((1, 0, *([0] * 8), 0, 1), cfg)
        self.assertTrue(math.isnan(result[-2]))
        self.assertTrue(math.isnan(result[-1]))

    def test_bad_calibration_length_is_rejected(self):
        cfg = dict(log.DEFAULT_META, gain=[1] * 7)
        with self.assertRaises(log.LogError):
            log.physical((1, 0, *([0] * 8), 0, 1), cfg)

    # --- integralnosc pliku ------------------------------------------------
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

    def test_non_monotonic_time(self):
        rows = [(10, 0, *([0] * 8), 0, 1), (9, 1, *([0] * 8), 0, 1)]
        log.write_log(self.path, rows)
        with self.assertRaisesRegex(log.LogError, 'monotonic'):
            log.inspect(self.path)

    # --- narzedzia ---------------------------------------------------------
    def test_export_and_report(self):
        target = self.dir / 'out.csv'
        log.export(self.path, target)
        lines = target.read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(lines), 4001)
        self.assertIn('aux_v', lines[0])
        html = self.dir / 'out.html'
        log.report(self.path, html)
        text = html.read_text(encoding='utf-8')
        self.assertIn('DANE SYNTETYCZNE', text)
        self.assertIn('"ground"', text)
        self.assertIn('config_id', text)

    def test_scan_reads_events(self):
        events = self.dir / 'scan.ndjson'
        events.write_text('\n'.join([
            json.dumps(log.config_event(1)),
            json.dumps(log.config_event(2, adc_config_ok=False)),
            '{"type":"mark","t_us":1000}',
            '{"type":"trigger","t_us":1200,"name":"ground"}',
            '{"type":"trigger","t_us":9000,"name":"ground"}',
            'to nie jest json',
            '{"type":"summary_dropped","t_us":5000}',
            '{"type":"hotsoak_point","index":0,"tc1":92.5,"i_break_open":0.61}',
        ]) + '\n', encoding='utf-8')
        r = log.scan(events)
        self.assertEqual(r['triggers']['ground'], 2)
        self.assertEqual(r['first_trigger_us']['ground'], 1200)
        self.assertEqual(r['marks_us'], [1000])
        self.assertEqual(len(r['hotsoak_points']), 1)
        self.assertEqual(len(r['configs']), 2)
        self.assertEqual(len(r['problems']), 1)
        self.assertTrue(any('niepotwierdzonym ADC' in w for w in r['warnings']))
        self.assertTrue(any('invalid NDJSON' in w for w in r['warnings']))


if __name__ == '__main__':
    unittest.main()
