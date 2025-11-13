# Rating Handling

AudioMeta implements a sophisticated rating profile system to handle the complex compatibility requirements across different audio players and formats. This system ensures that ratings work consistently regardless of which software was used to create them.

## The Rating Profile Problem

**The Problem**: Different audio players use completely different numeric values for the same star ratings. For example, a 3-star rating can be stored as:

- `128` (Windows Media Player, MusicBee, Winamp)
- `60` (FLAC players, Vorbis)
- `153` (Traktor)

> 📋 **Complete Compatibility Table**: See [`rating_profiles.py`](../audiometa/utils/rating_profiles.py) for the detailed reference table showing all player compatibility and exact numeric values.

**Key Points:**

- **0/None ratings**: `0` can mean either "no rating" (Traktor) or "0 stars" (MusicBee) - AudioMeta distinguishes between them and handles "no rating" cases
- **Half-star support**: Limited support - mainly MusicBee and some ID3v2 implementations
- **Traktor limitation**: Only supports whole stars (1, 2, 3, 4, 5)
- **Format compatibility**: Different formats use different rating systems
- **Automatic handling**: AudioMeta manages all the complexity for you

## Rating Profile Types

AudioMeta recognizes three main rating profiles:

**Profile A: 255 Non-Proportional (Most Common)**

- Used by: ID3v2 (MP3), RIFF (WAV), most standard players
- Examples: Windows Media Player, MusicBee, Winamp, kid3
- **Half-star support**: ✅ Full support (0.5, 1.5, 2.5, 3.5, 4.5 stars)

**Profile B: 100 Proportional (FLAC Standard)**

- Used by: Vorbis (FLAC), some WAV ID3v2 implementations
- Examples: FLAC files, some modern players
- **Half-star support**: ✅ Full support (0.5, 1.5, 2.5, 3.5, 4.5 stars)

**Profile C: 255 Proportional (Traktor)**

- Used by: Traktor software (Native Instruments)
- For MP3 ID3v2 and FLAC Vorbis (Traktor does not write tags on WAV files)
- Examples: Traktor Pro, Traktor DJ
- **Half-star support**: ❌ No support (only whole stars: 1, 2, 3, 4, 5)

## Rating Normalization

AudioMeta supports two modes for handling ratings:

1. **Raw Mode** (default): Returns and accepts raw profile-specific values
2. **Normalized Mode**: Converts between raw values and a normalized scale

```python
from audiometa import get_unified_metadata, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat

# Reading without normalization (raw values)
metadata = get_unified_metadata("song.mp3")
rating = metadata.get(UnifiedMetadataKey.RATING)  # Returns: 128, 60, 153, etc. (raw profile values)

# Reading with normalization
metadata = get_unified_metadata("song.mp3", normalized_rating_max_value=10)
rating = metadata.get(UnifiedMetadataKey.RATING)  # Returns: 0, 2, 4, 6, 8, 10 (normalized)

# Writing without normalization (raw values)
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 128}, metadata_format=MetadataFormat.ID3V2)  # Direct raw value

# Writing with normalization
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 6}, normalized_rating_max_value=10)  # Writes 128 (Profile A)
update_metadata("song.flac", {UnifiedMetadataKey.RATING: 6}, normalized_rating_max_value=10)  # Writes 60 (Profile B)
```

**Normalization Formula**:

- **Reading**: `normalized_rating = star_rating_base_10 * normalized_rating_max_value / 10`
  - Example: 3 stars (star_rating_base_10=6) with max=100 → `6 * 100 / 10 = 60`
- **Writing**: `star_rating_base_10 = int((normalized_rating * 10) / normalized_rating_max_value)`
  - Example: normalized_rating=60 with max=100 → `int((60 * 10) / 100) = 6` → Profile A writes 128

**Benefits of Normalization**:

- Consistent values across different rating profiles
- Easy to work with regardless of source player
- Flexible scale (can use 0-10, 0-100, 0-255, etc.)

**When to Use Each Mode**:

- **Normalized**: When you want consistent, player-agnostic rating values
- **Raw**: When you need direct control over the exact profile values written to files

## Normalized Rating Scale

When `normalized_rating_max_value` is provided, AudioMeta uses a normalized scale. With `normalized_rating_max_value=10`, the scale is:

```python
# 0 = No rating
# 2 = 1 star
# 4 = 2 stars
# 6 = 3 stars
# 8 = 4 stars
# 10 = 5 stars

# Reading with normalization
metadata = get_unified_metadata("song.mp3", normalized_rating_max_value=10)
rating = metadata.get('rating')  # Returns 0-10 scale

# Writing with normalization
update_metadata("song.mp3", {"rating": 8}, normalized_rating_max_value=10)  # 4 stars
```

**Note**: Without `normalized_rating_max_value`, AudioMeta returns raw profile-specific values (e.g., 128, 60, 153) instead of normalized values.

## How AudioMeta Handles Rating Profiles

### Reading Ratings

**Automatic Profile Detection**

```python
from audiometa import get_unified_metadata

# AudioMeta automatically detects the rating profile
# Without normalization: returns raw profile values
metadata = get_unified_metadata("song.mp3")
rating = metadata.get('rating')  # Returns raw values: 128, 60, 153, etc.

# With normalization: returns consistent normalized values
metadata = get_unified_metadata("song.mp3", normalized_rating_max_value=10)
rating = metadata.get('rating')  # Returns 0-10 scale: 0, 2, 4, 6, 8, 10, etc.

# Examples of what you get with normalization (normalized_rating_max_value=10):
# - File rated 3 stars in Windows Media Player (128) → rating = 6
# - File rated 3 stars in FLAC player (60) → rating = 6
# - File rated 3 stars in Traktor (153) → rating = 6
# - File rated 3.5 stars in MusicBee (186) → rating = 7
# - File rated 2.5 stars in FLAC (50) → rating = 5

# Examples without normalization:
# - File rated 3 stars in Windows Media Player → rating = 128 (raw)
# - File rated 3 stars in FLAC player → rating = 60 (raw)
# - File rated 3 stars in Traktor → rating = 153 (raw)
```

### Writing Ratings

#### Rating Writing Profiles

AudioMeta uses two write profiles to ensure maximum compatibility across different audio players:

- **BASE_255_NON_PROPORTIONAL** (Profile A): Used for ID3v2 (MP3) and RIFF (WAV)
  - Values: `[0, 13, 1, 54, 64, 118, 128, 186, 196, 242, 255]`
  - Most widely supported profile
  - Full half-star support (0.5, 1.5, 2.5, 3.5, 4.5 stars)

- **BASE_100_PROPORTIONAL** (Profile B): Used for Vorbis (FLAC)
  - Values: `[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]`
  - Standard for FLAC files
  - Full half-star support (0.5, 1.5, 2.5, 3.5, 4.5 stars)

AudioMeta automatically selects the appropriate profile based on the file format:

```python
from audiometa import update_metadata

# AudioMeta automatically uses the most compatible profile for each metadata format
update_metadata("song.mp3", {"rating": 6})   # ID3v2 uses BASE_255_NON_PROPORTIONAL (128)
update_metadata("song.flac", {"rating": 6})  # Vorbis uses BASE_100_PROPORTIONAL (60)
update_metadata("song.wav", {"rating": 6})   # RIFF uses BASE_255_NON_PROPORTIONAL (128)

# Half-star ratings are also supported:
update_metadata("song.mp3", {"rating": 7})   # 3.5 stars → BASE_255_NON_PROPORTIONAL (186)
update_metadata("song.flac", {"rating": 5})  # 2.5 stars → BASE_100_PROPORTIONAL (50)
```

#### Rating Validation Rules

AudioMeta validates rating values based on whether normalization is enabled. You can also validate ratings independently using `_RatingSupportingMetadataManager.validate_rating_value()` (see [Pre-Update Validation Function](../README.md#pre-update-validation-function) in the main README).

**When `normalized_rating_max_value` is not provided (raw mode)**:

The rating value is written as-is. Any non-negative integer is allowed. Whole-number floats (like `196.0`) are also accepted and automatically converted to integers.

```python
from audiometa import update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat

# Any non-negative integer rating value is allowed when normalized_rating_max_value is not provided
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 128}, metadata_format=MetadataFormat.ID3V2)
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 75}, metadata_format=MetadataFormat.ID3V2)
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 0}, metadata_format=MetadataFormat.ID3V2)
update_metadata("song.flac", {UnifiedMetadataKey.RATING: 50}, metadata_format=MetadataFormat.VORBIS)

# Whole-number floats are accepted and converted to integers
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 196.0}, metadata_format=MetadataFormat.ID3V2)  # Treated as 196

# Invalid: fractional floats require normalization
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 1.5}, metadata_format=MetadataFormat.ID3V2)
# Error: Rating value 1.5 is invalid. In raw mode, float values must be whole numbers (e.g., 196.0). Half-star values like 1.5 require normalization.

# Invalid: negative values are rejected
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: -1}, metadata_format=MetadataFormat.ID3V2)
# Error: Rating value -1 is invalid. Rating values must be non-negative (>= 0)
```

**When `normalized_rating_max_value` is provided (normalized mode)**:

The rating value (int or float) is normalized and must map to a valid profile value. AudioMeta calculates `(value / max) * 100` and `(value / max) * 255`, then checks if at least one of these rounded values exists in a supported writing profile (BASE_100_PROPORTIONAL or BASE_255_NON_PROPORTIONAL).

```python
# Valid: 50/100 * 100 = 50, which is in BASE_100_PROPORTIONAL profile
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 50}, normalized_rating_max_value=100)

# Valid: 1.5/10 * 100 = 15, which is in BASE_100_PROPORTIONAL profile
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 1.5}, normalized_rating_max_value=10)

# Invalid: 37/100 * 100 = 37 (not in BASE_100_PROPORTIONAL)
# 37/100 * 255 = 94 (not in BASE_255_NON_PROPORTIONAL)
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 37}, normalized_rating_max_value=100)
# Error: Rating value 37 is not valid for max value 100. Calculated output values (37 for 100-scale, 94 for 255-scale) do not exist in any supported writing profile.

# Invalid: negative values are rejected
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: -1}, normalized_rating_max_value=100)
# Error: Rating value -1 is invalid. Rating values must be non-negative (>= 0)

# Invalid: values above max are rejected
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 101}, normalized_rating_max_value=100)
# Error: Rating value 101 is out of range. Value must be between 0 and 100 (inclusive)

# With max=10, any integer 0-10 is valid (all map to valid profile values)
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 7}, normalized_rating_max_value=10)

# With max=10, float values like 1.5, 2.5, etc. are also valid if they map to valid profile values
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 1.5}, normalized_rating_max_value=10)  # Valid: 1.5/10 * 100 = 15 (in BASE_100_PROPORTIONAL)

# With max=255, valid values include those that map to BASE_255_NON_PROPORTIONAL or BASE_100_PROPORTIONAL
# Examples: 0, 1, 13, 25, 50, 54, 64, 76, 102, 118, 128, 153, 178, 186, 196, 204, 229, 242, 255
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 128}, normalized_rating_max_value=255)  # Valid: maps to 128 in BASE_255_NON_PROPORTIONAL
update_metadata("song.mp3", {UnifiedMetadataKey.RATING: 50}, normalized_rating_max_value=255)   # Valid: maps to 20 in BASE_100_PROPORTIONAL
```

## Half-Star Rating Support

AudioMeta fully supports half-star ratings (0.5, 1.5, 2.5, 3.5, 4.5 stars) across all the formats. You can use float values directly:

```python
# Reading half-star ratings
metadata = get_unified_metadata("half_star_rated.mp3")
rating = metadata.get('rating')  # Could be 1.0, 3.0, 5.0, 7.0, 9.0 for half-stars

# Writing half-star ratings using integers (normalized mode)
update_metadata("song.mp3", {"rating": 7}, normalized_rating_max_value=10)   # 3.5 stars
update_metadata("song.flac", {"rating": 5}, normalized_rating_max_value=10)  # 2.5 stars
update_metadata("song.wav", {"rating": 9}, normalized_rating_max_value=10)   # 4.5 stars

# Writing half-star ratings using float values (normalized mode)
update_metadata("song.mp3", {"rating": 1.5}, normalized_rating_max_value=10)   # 1.5 stars
update_metadata("song.flac", {"rating": 2.5}, normalized_rating_max_value=10)  # 2.5 stars
update_metadata("song.wav", {"rating": 4.5}, normalized_rating_max_value=10)   # 4.5 stars
```

**Why profile-based validation?**

When normalization is enabled, ratings are converted to file-specific values using the writing profiles (BASE_100_PROPORTIONAL for Vorbis, BASE_255_NON_PROPORTIONAL for ID3v2/RIFF). The validation ensures that the normalized value maps to an actual profile value that can be written to the file. This guarantees that the rating will be correctly interpreted by audio players that follow these standard profiles.

**Error Handling**:

Invalid rating values raise `InvalidRatingValueError` with a descriptive message indicating why the value is invalid.
