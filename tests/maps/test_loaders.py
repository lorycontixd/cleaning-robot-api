import pytest

from app.core.exceptions import InvalidMapContent, UnsupportedMapFormat
from app.core.map import Coordinate
from app.maps.json import parse_json
from app.maps.txt import parse_txt


class TestTxtLoader:
    def test_valid_map(self):
        input = b"oxo\nooo"  # 2x3 map
        input_clean = input.decode("utf-8").replace("\n", "")

        result = parse_txt(input)
        assert result.rows == 2
        assert result.cols == 3
        assert result.tiles is not None
        assert len(result.tiles) == 6

        for i, (_, tile) in enumerate(result.tiles.items()):
            if input_clean[i] == "o":
                assert tile.is_walkable and tile.is_dirty
            else:
                assert not tile.is_walkable and not tile.is_dirty

    def test_empty_map(self):
        input = b""

        with pytest.raises(InvalidMapContent):
            result = parse_txt(input)
            print(result)

    def test_empty_row(self):
        input = b"oo\n\noo"

        with pytest.raises(InvalidMapContent):
            parse_txt(input)

    def test_windows_end_of_line(self):
        input = b"oo\r\nxx"
        input_clean = input.decode("utf-8").replace("\r\n", "")

        result = parse_txt(input)
        assert result.rows == 2
        assert result.cols == 2

        assert result.tiles is not None
        assert len(result.tiles) == 4

        for i, (_, tile) in enumerate(result.tiles.items()):
            if input_clean[i] == "o":
                assert tile.is_walkable and tile.is_dirty
            else:
                assert not tile.is_walkable and not tile.is_dirty

    def test_inconsistent_row_length(self):
        input = b"oo\nooo"

        with pytest.raises(InvalidMapContent):
            parse_txt(input)

    def test_invalid_character(self):
        input = b"oo\noob"

        with pytest.raises(InvalidMapContent):
            parse_txt(input)

    def test_invalid_utf8(self):
        input = b"\xff\xfe\xfd"

        with pytest.raises(InvalidMapContent):
            parse_txt(input)


class TestJsonLoader:
    def test_valid_map(self):
        input = (
            b'{"rows": 2, "cols": 2, "tiles": [{"x": 0, "y": 0, '
            b'"walkable": true, "dirty": true}, {"x": 0, "y": 1, '
            b'"walkable": true, "dirty": true}, {"x": 1, "y": 0, '
            b'"walkable": false, "dirty": false}, {"x": 1, "y": 1, '
            b'"walkable": true, "dirty": true}]}'
        )

        result = parse_json(input)
        assert result.rows == 2
        assert result.cols == 2
        assert result.tiles is not None
        assert len(result.tiles) == 4
        assert result.tiles[Coordinate(x=0, y=0)].is_walkable is True
        assert result.tiles[Coordinate(x=0, y=1)].is_walkable is True
        assert result.tiles[Coordinate(x=1, y=0)].is_walkable is False
        assert result.tiles[Coordinate(x=1, y=1)].is_walkable is True
        assert result.tiles[Coordinate(x=0, y=0)].is_dirty is True
        assert result.tiles[Coordinate(x=0, y=1)].is_dirty is True
        assert result.tiles[Coordinate(x=1, y=0)].is_dirty is False
        assert result.tiles[Coordinate(x=1, y=1)].is_dirty is True

    def test_malformed_json(self):
        malformed = b"{invalid_json: true}"

        with pytest.raises(InvalidMapContent):
            parse_json(malformed)

    def test_tile_count_mismatch(self):
        input = (
            b'{"rows": 2, "cols": 2, "tiles": [{"x": 0, "y": 0, "walkable": true, "dirty": true}]}'
        )

        with pytest.raises(InvalidMapContent):
            parse_json(input)

    def test_out_of_bounds(self):
        input = (
            b'{"rows": 2, "cols": 2, "tiles": [{"x": 0, "y": 0, '
            b'"walkable": true, "dirty": true}, {"x": 0, "y": 1, '
            b'"walkable": true, "dirty": true}, {"x": 1, "y": 0, '
            b'"walkable": false, "dirty": false}, {"x": 2, "y": 1, '
            b'"walkable": true, "dirty": true}]}'
        )

        with pytest.raises(InvalidMapContent):
            parse_json(input)

    def test_non_walkable_but_dirty(self):
        input = (
            b'{"rows": 1, "cols": 1, "tiles": [{"x": 0, "y": 0, "walkable": false, "dirty": true}]}'
        )

        with pytest.raises(InvalidMapContent):
            parse_json(input)

    def test_invalid_content_raises_exception(self):
        invalid = b"\xff\xfe\xfd"

        with pytest.raises(InvalidMapContent):
            from app.maps.json import parse_json

            parse_json(invalid)


class TestLoadMap:
    def test_invalid_file_extension_raises_exception(self):
        invalid = b"{}"

        with pytest.raises(UnsupportedMapFormat):
            from app.maps.map_loader import load_map

            load_map("invalid_file.xyz", invalid)

    def test_empty_content_raises_exception(self):
        empty = b""

        with pytest.raises(InvalidMapContent):
            from app.maps.map_loader import load_map

            load_map("empty_file.txt", empty)

    def test_valid_txt(self):
        valid = b"ooo\noox"

        from app.maps.map_loader import load_map

        result = load_map("valid_file.txt", valid)
        assert result is not None
        assert result.tiles
        assert len(result.tiles) == 6  # 3x2 grid based on the input

    def test_valid_json(self):
        valid = (
            b'{"rows": 2, "cols": 2, "tiles": [{"x": 0, "y": 0, '
            b'"walkable": true, "dirty": true}, {"x": 0, "y": 1, '
            b'"walkable": true, "dirty": true}, {"x": 1, "y": 0, '
            b'"walkable": false, "dirty": false}, {"x": 1, "y": 1, '
            b'"walkable": true, "dirty": true}]}'
        )

        from app.maps.map_loader import load_map

        result = load_map("valid_file.json", valid)
        assert result is not None
        assert result.tiles
        assert len(result.tiles) == 4  # 2x2 grid based on the input

    def test_invalid_content_raises_exception(self):
        invalid = b"\xff\xfe\xfd"
        from app.core.exceptions import InvalidMapContent

        with pytest.raises(InvalidMapContent):
            from app.maps.map_loader import load_map

            load_map("invalid_file.txt", invalid)
