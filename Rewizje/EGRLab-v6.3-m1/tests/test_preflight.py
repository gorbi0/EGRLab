"""6.3.1-m1 (recenzja M1-07): zaleznosci testow przed ich uruchomieniem - fixture'y z sumami SHA-256 (tests/fixtures/FIXTURES.json)
i model sprzetu v6.1 (Rewizje/EGRLab-v6.1-rc1, ten sam commit repozytorium). Brak = jawny blad z nazwa pliku, nie FileNotFoundError w srodku testu."""
import hashlib,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class Preflight(unittest.TestCase):
    def test_fixtures(self):
        m=json.loads((R/'tests/fixtures/FIXTURES.json').read_text(encoding='utf-8'))
        for name,f in m['files'].items():
            p=R/'tests/fixtures'/name;self.assertTrue(p.exists(),f'brak fixture {name} (zrodlo {f["source"]} @ {m["source_commit"]})')
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),f['sha256'],f'zmieniony fixture {name}')
    def test_v61_model(self):
        hw=R.parent/'EGRLab-v6.1-rc1'
        self.assertTrue((hw/'hardware/components.json').exists(),f'brak modelu sprzetu v6.1: {hw} - pobierz Rewizje/EGRLab-v6.1-rc1 z tego samego commitu')
if __name__=='__main__':unittest.main()
