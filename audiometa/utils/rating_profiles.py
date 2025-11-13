"""Rating Compatibility Table Across Different Audio Players.

⚠️  AUTHORITATIVE SOURCE: This is the single source of truth for rating compatibility.
The README references this table for the complete details.

The following table shows how different audio players handle ratings across various audio formats.
Values represent the actual numbers written to files for each star rating (0-5 stars).

+----+----------------+------------+------------+------------+------------+---------+
| ⭐ |      kid3      |   Windows  |  MusicBee  |   Winamp   |   Traktor  |  iTunes |
|    |   /Lollypop    |Media Player|            |            |            |         |
+----+---+-------+----+------------+------------+------------+------------+---------+
|ext.|mp3|  wav  |flac|mp3 wav flac|mp3 wav flac|mp3 wav flac|mp3 wav flac|W ops not|
+----+-----------+----+------------+------------+------------+------------+         +
|tags|id3|rif id3|vorb|id3  ✗  vorb|id3 id3 vorb|id3  ✗  vorb|id3  ✗  vorb|supported|
+----+---+-------+----+------------+------------+------------+------------+---------+
|None| ✗   ✗   ✗    ✗ | ✗       ✗  | ✗   ✗   ✗  |  ✗      ✗  | 0        0 |         |
| 0  |                |            | 0   0   0  |            |            |         |
|0.5 |                |            |13   10  10 |            |            |         |
| 1  | 1   20  1   20 | 1       20 | 1   20  20 |  1      20 | 51      51 |         |
|1.5 |                |            |54   30  30 |            |            |         |
| 2  |64   40  64  40 | 64      40 |64   40  40 | 64      40 |102     102 |         |
|2.5 |                |            |118  50  50 |            |            |         |
| 3  |128  60 128  60 | 128     60 |128  60  60 | 128     60 |153     153 |         |
|3.5 |                |            |186  70  70 |            |            |         |
| 4  |196  80 196  80 |196  80  80 | 196     80 | 196     80 |204     204 |         |
|4.5 |                |            |242  90  90 |            |            |         |
| 5  |255 100 255  100| 255    100 |255 100 100 | 255    100 |255     255 |         |
+----+----------------+------------+------------+------------+------------+---------+
|Prof| A   B   A   B  |  A   ✗  B  | A   B   B  |  A   ✗  B  | C   ✗   C  |    ✗    |
+----+----------------+------------+------------+------------+------------+---------+

Legend:
    id3 = id3v2
    rif = RIFF
    vorb = Vorbis
    ✗ = No tag written
    empty = Rating value not supported
    ✓ = Can write ratings

- Rating Profiles:
    A. 255 non-proportional: .mp3 id3v2 not Traktor, RIFF
    B. 100 proportional: Vorbis not Traktor, .wav id3v2
    C. 255 proportional: Traktor id3v2/Vorbis

- Key Point
Despite having different profiles, each rating value uniquely maps to one star value, enabling reliable star rating
interpretation regardless of the source profile.

- Example: All these values map to 3 stars
    assert rating_to_stars(128) == 3.0  # Profile A
    assert rating_to_stars(60) == 3.0   # Profile B
    assert rating_to_stars(153) == 3.0  # Profile C

- Exception:
0 can either mean no rating (Traktor) or 0 stars (MusicBee).
Luckily, Traktor ratings are written with special tags making them easy to distinguish.
"""

from collections.abc import Iterator
from enum import Enum


class RatingReadProfile(Enum):
    """Enumeration of rating read profiles for different audio formats."""

    BASE_255_NON_PROPORTIONAL = (0, 13, 1, 54, 64, 118, 128, 186, 196, 242, 255)
    BASE_255_PROPORTIONAL_TRAKTOR = (None, None, 51, None, 102, None, 153, None, 204, None, 255)
    BASE_100_PROPORTIONAL = (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)

    def __getitem__(self, index: int) -> int | None:
        result = self.value[index]
        return result if isinstance(result, int | type(None)) else int(result)

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterator[int | None]:
        return iter(self.value)

    def __contains__(self, item: object) -> bool:
        return item in self.value


"""
Regarding the ratings that the app will write in the audio files, the app currently uses the 2 most widely supported
profiles:
- 255 non proportional (ID3v2, RIFF)
- 100 proportional (Vorbis)
"""


class RatingWriteProfile(Enum):
    """Enumeration of rating write profiles for different audio formats."""

    BASE_255_NON_PROPORTIONAL = RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
    BASE_100_PROPORTIONAL = RatingReadProfile.BASE_100_PROPORTIONAL.value

    def __getitem__(self, index: int) -> int | None:
        result = self.value[index]
        return result if isinstance(result, int | type(None)) else int(result)

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterator[int | None]:
        return iter(self.value)

    def __contains__(self, item: object) -> bool:
        return item in self.value
