"""Regression coverage for curves with missing descriptive attributes."""

from pathlib import Path
import tempfile
import unittest

from sosilogikk import read_sosi


class CurveAttributeTests(unittest.TestCase):
    def test_missing_objtype_defaults_in_geometry_and_metadata(self):
        for ending in ('.SLUTT\n', ''):
            for attributes, expected_type in (
                ('', 'Unknown'),
                ('..NAVN Test\n', 'Unknown'),
                ('..OBJTYPE Rekkverk\n', 'Rekkverk'),
            ):
                with self.subTest(ending=ending, attributes=attributes):
                    source = '''.HODE
..TEGNSETT UTF-8
..TRANSPAR
...KOORDSYS 22
...ORIGO-NØ 100 200
...ENHET 0.001
'''
                    # The first curve is flushed by the next curve; the second
                    # is flushed by either .SLUTT or end of file.
                    for identifier in (1, 2):
                        source += (
                            f'.KURVE {identifier}:\n{attributes}'
                            '..NØH\n0 0 1000\n1000 2000 3000\n'
                        )
                    source += ending
                    with tempfile.TemporaryDirectory() as directory:
                        path = Path(directory) / 'curves.sos'
                        path.write_text(source, encoding='utf-8')
                        gdf, metadata = read_sosi(path, return_metadata=True)

                    self.assertEqual(len(gdf), 2)
                    self.assertEqual(gdf['OBJTYPE'].tolist(), [expected_type] * 2)
                    self.assertIn('OBJTYPE', metadata['all_attributes'])
                    for geometry in gdf.geometry:
                        self.assertEqual(geometry.geom_type, 'LineString')
                        self.assertEqual(list(geometry.coords),
                                         [(200, 100, 1), (202, 101, 3)])
                    if attributes.startswith('..NAVN'):
                        self.assertEqual(gdf['NAVN'].tolist(), ['Test', 'Test'])


if __name__ == '__main__':
    unittest.main()
