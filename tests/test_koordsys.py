"""Regression coverage for SOSI coordinate reference systems."""

from pathlib import Path
import tempfile
import unittest

from sosilogikk import read_sosi


class KoordsysTests(unittest.TestCase):
    def test_read_ntm_zone_8_and_reproject(self):
        source = '''.HODE
..TEGNSETT UTF-8
..SOSI-VERSJON 4.5
..TRANSPAR
...KOORDSYS 208
...ORIGO-NØ 1000000 100000
...ENHET 0.001
.PUNKT 1:
..OBJTYPE TEST
..NØ
0 0
.SLUTT
'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ntm8.sos'
            path.write_text(source, encoding='utf-8')
            gdf, metadata = read_sosi(path, return_metadata=True)

        self.assertEqual(metadata['header']['KOORDSYS'], '208')
        self.assertEqual(gdf.crs.to_epsg(), 5108)
        self.assertEqual(list(gdf.geometry.iloc[0].coords), [(100000, 1000000)])
        # NTM's false origin is at the zone's central meridian and 58 N.
        geographic = gdf.to_crs(4326).geometry.iloc[0]
        self.assertAlmostEqual(geographic.x, 8.5, places=6)
        self.assertAlmostEqual(geographic.y, 58, places=6)


if __name__ == '__main__':
    unittest.main()
