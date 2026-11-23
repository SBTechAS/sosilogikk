"""Regression coverage for LINJE objects without descriptive attributes."""

from pathlib import Path
import tempfile
import unittest

from sosilogikk import _read_sosi_file, read_sosi


class LineAttributeTests(unittest.TestCase):
    def test_lines_with_and_without_attributes_at_object_boundaries_and_eof(self):
        for ending in ('.SLUTT\n', ''):
            with self.subTest(ending=ending):
                source = '''.HODE
..TEGNSETT UTF-8
..TRANSPAR
...KOORDSYS 210
...ORIGO-NØ 100 200
...ENHET 0.001
.LINJE 1:
..OBJTYPE Rekkverk
..Layer Steel
..Acad_ID ABC
..NØH
0 0 1000
1000 2000 3000
.LINJE 2:
..NØH
2000 3000 4000 ...KP 1
..NØH
3000 4000 5000
.LINJE 3:
..NAVN Last line
..NØH
4000 5000 6000
5000 6000 7000
.LINJE 4:
..NØH
6000 7000 8000
7000 8000 9000
''' + ending
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / 'lines.sos'
                    path.write_text(source, encoding='utf-8')
                    parsed = _read_sosi_file(path)
                    gdf, metadata = read_sosi(path, return_metadata=True)

                self.assertEqual(len(parsed['data']['geometry']), 4)
                self.assertEqual(len(parsed['data']['attributes']), 4)
                self.assertEqual(len(gdf), 4)
                self.assertEqual(gdf['OBJTYPE'].tolist(), ['Rekkverk'] + ['Unknown'] * 3)
                self.assertIn('OBJTYPE', metadata['all_attributes'])
                self.assertEqual(gdf.crs.to_epsg(), 5110)
                self.assertEqual(gdf.iloc[0]['Layer'], 'Steel')
                self.assertEqual(gdf.iloc[0]['Acad_ID'], 'ABC')
                self.assertEqual(gdf.iloc[2]['NAVN'], 'Last line')
                self.assertNotIn('Layer', parsed['data']['attributes'][1])
                self.assertNotIn('Acad_ID', parsed['data']['attributes'][1])
                self.assertEqual(gdf.geometry.geom_type.tolist(), ['LineString'] * 4)
                self.assertEqual(list(gdf.geometry.iloc[1].coords),
                                 [(203, 102, 4), (204, 103, 5)])
                self.assertEqual(list(gdf.geometry.iloc[-1].coords),
                                 [(207, 106, 8), (208, 107, 9)])


if __name__ == '__main__':
    unittest.main()
