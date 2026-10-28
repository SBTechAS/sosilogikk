"""Regression coverage for SOSI comments and literal exclamation marks."""

from pathlib import Path
import tempfile
import unittest

from sosilogikk import _read_sosi_file, _strip_sosi_comment, read_sosi


class CommentTests(unittest.TestCase):
    def test_quoted_values(self):
        cases = [
            ('..NAVN "Hello!" ! comment', '..NAVN "Hello!" '),
            ("..NAVN 'Hello!' ! comment", "..NAVN 'Hello!' "),
            ('..NAVN "O\'Brien!" ! comment', '..NAVN "O\'Brien!" '),
            ("..NAVN O'Brien ! comment", "..NAVN O'Brien "),
            ('..NAVN "Hello!"', '..NAVN "Hello!"'),
            ('! comment', ''),
            ('123 456!comment', '123 456'),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(_strip_sosi_comment(source), expected)

    def test_comments_throughout_file(self):
        source = '''.HODE ! header
..TEGNSETT ISO8859-1 ! encoding
..SOSI-VERSJON 4.3
..SOSI-NIVÅ 3 !!!!!!!!!!!
..TRANSPAR ! parameters
...KOORDSYS 22 ! CRS
...ORIGO-NØ 100 200 ! origin
...ENHET 0.001 ! scale
...VERT-DATUM NN2000 ! datum
..OMRÅDE
...MIN-NØ 100 200 !!!!!!!!!!!!!!!!!!!!
...MAX-NØ 101 201 !!!!!!!!!!!!!!!!!!!!
.KURVE 1: ! curve
..OBJTYPE REKKVERK ! type
..NAVN "Rekkverk! ÆØÅ" ! name
..MERKNAD 'Keep! this' ! another name
..NØH ! coordinates
0 0 1000 ! first point
! comment between points

1000 1000 2000!last point
.SLUTT ! end
'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'comments.sos'
            path.write_bytes(source.encode('iso-8859-1'))
            parsed = _read_sosi_file(path)
            gdf, metadata = read_sosi(path, return_metadata=True)
            clean_path = Path(directory) / 'without_comments.sos'
            clean_source = '\n'.join(_strip_sosi_comment(line) for line in source.splitlines())
            clean_path.write_text(clean_source.replace('ISO8859-1', 'UTF-8'), encoding='utf-8')
            clean_gdf = read_sosi(clean_path)

        self.assertTrue(gdf.equals(clean_gdf))
        self.assertEqual(parsed['extent'], (100, 200, 101, 201))
        self.assertEqual(len(gdf), 1)
        self.assertEqual(gdf.iloc[0]['OBJTYPE'], 'REKKVERK')
        self.assertEqual(gdf.iloc[0]['NAVN'], '"Rekkverk! ÆØÅ"')
        self.assertEqual(gdf.iloc[0]['MERKNAD'], "'Keep! this'")
        self.assertEqual(list(gdf.geometry.iloc[0].coords),
                         [(200, 100, 1), (201, 101, 2)])
        self.assertEqual(metadata['header']['VERT-DATUM'], 'NN2000')
        self.assertEqual(metadata['header']['KOORDSYS'], '22')
        self.assertEqual(gdf.crs.to_epsg(), 25832)
        # The source index keeps original lines for the existing writer.
        self.assertIn('.KURVE 1: ! curve\n', metadata['sosi_index'][0])


if __name__ == '__main__':
    unittest.main()
