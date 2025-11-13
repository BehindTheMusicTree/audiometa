from abc import abstractmethod
from typing import TYPE_CHECKING

from audiometa.utils.unified_metadata_key import UnifiedMetadataKey

if TYPE_CHECKING:
    from ..._audio_file import _AudioFile
from ...exceptions import ConfigurationError, InvalidRatingValueError, MetadataFieldNotSupportedByMetadataFormatError
from ...utils.rating_profiles import RatingReadProfile, RatingWriteProfile
from ...utils.types import RawMetadataDict, RawMetadataKey, UnifiedMetadata, UnifiedMetadataValue
from .._MetadataManager import _MetadataManager

# Maximum star rating index (0-10, where 0=0 stars, 1=0.5 stars, 2=1 star, ..., 10=5 stars)
MAX_STAR_RATING_INDEX = 10


class _RatingSupportingMetadataManager(_MetadataManager):
    TRAKTOR_RATING_TAG_MAIL = "traktor@native-instruments.de"

    normalized_rating_max_value: int | None
    rating_write_profile: RatingWriteProfile

    def __init__(
        self,
        audio_file: "_AudioFile",
        metadata_keys_direct_map_read: dict[UnifiedMetadataKey, RawMetadataKey | None],
        metadata_keys_direct_map_write: dict[UnifiedMetadataKey, RawMetadataKey | None],
        rating_write_profile: RatingWriteProfile,
        normalized_rating_max_value: int | None,
        update_using_mutagen_metadata: bool = True,
    ):
        self.rating_write_profile = rating_write_profile
        self.normalized_rating_max_value = normalized_rating_max_value
        super().__init__(
            audio_file=audio_file,
            update_using_mutagen_metadata=update_using_mutagen_metadata,
            metadata_keys_direct_map_read=metadata_keys_direct_map_read,
            metadata_keys_direct_map_write=metadata_keys_direct_map_write,
        )

    def _get_formatted_metadata_format_name(self) -> str:
        """Get the formatted metadata format name from the class name.

        Returns:
            The formatted format name (e.g., 'RIFF', 'ID3v2', 'Vorbis')
        """
        metadata_format_name = self.__class__.__name__.replace("Manager", "").lstrip("_").upper()
        if metadata_format_name == "RIFF":
            return "RIFF"
        if metadata_format_name == "ID3V2":
            return "ID3v2"
        if metadata_format_name == "VORBIS":
            return "Vorbis"
        return metadata_format_name

    @staticmethod
    def validate_rating_value(rating_value: float, normalized_rating_max_value: int | None) -> None:
        """Validate rating value based on normalized_rating_max_value.

        Rules:
        - When normalized_rating_max_value is None: value must be >= 0 (any non-negative number is allowed)
        - When normalized_rating_max_value is provided: value must be between 0 and normalized_rating_max_value
          and when converted to output values (value/max * 100 or value/max * 255), at least one must exist
          in a writing profile (BASE_100_PROPORTIONAL or BASE_255_NON_PROPORTIONAL)

        Half-star ratings (e.g., 1.5, 2.5, 3.5) are supported to be consistent with classic star rating
        systems that allow half-star increments.

        Args:
            rating_value: The rating value to validate (int or float). Supports half-star ratings (e.g., 1.5, 2.5).
            normalized_rating_max_value: Maximum value for rating normalization, or None for raw values

        Raises InvalidRatingValueError if validation fails.
        """
        if normalized_rating_max_value is None:
            # Rating is written as-is - must be non-negative
            if rating_value < 0:
                msg = f"Rating value {rating_value} is invalid. Rating values must be non-negative (>= 0)."
                raise InvalidRatingValueError(msg)
        else:
            # Value is normalized - must be non-negative and within max
            if rating_value < 0:
                msg = f"Rating value {rating_value} is invalid. Rating values must be non-negative (>= 0)."
                raise InvalidRatingValueError(msg)
            if rating_value > normalized_rating_max_value:
                msg = (
                    f"Rating value {rating_value} is out of range. "
                    f"Value must be between 0 and {normalized_rating_max_value} (inclusive)."
                )
                raise InvalidRatingValueError(msg)
            # Convert normalized rating to star rating index (0-10, where 0=0 stars, 1=0.5 stars, 2=1 star, etc.)
            # Use round() to properly handle half-star ratings (consistent with classic star rating systems)
            star_rating_index = round((rating_value * 10) / normalized_rating_max_value)
            if star_rating_index < 0 or star_rating_index > MAX_STAR_RATING_INDEX:
                msg = (
                    f"Rating value {rating_value} results in invalid star rating index {star_rating_index}. "
                    f"Index must be between 0 and 10."
                )
                raise InvalidRatingValueError(msg)

            # Check if profile values at this star rating index exist in writing profiles
            profile_value_100 = RatingWriteProfile.BASE_100_PROPORTIONAL[star_rating_index]
            profile_value_255 = RatingWriteProfile.BASE_255_NON_PROPORTIONAL[star_rating_index]

            # At least one profile must have a valid value at this index
            if profile_value_100 is None and profile_value_255 is None:
                msg = (
                    f"Rating value {rating_value} is not valid for max value {normalized_rating_max_value}. "
                    f"Star rating index {star_rating_index} does not exist in any supported writing profile."
                )
                raise InvalidRatingValueError(msg)

    @abstractmethod
    def _get_raw_rating_by_traktor_or_not(self, raw_clean_metadata: RawMetadataDict) -> tuple[int | None, bool]:
        """Return True if the rating is from Traktor, False otherwise."""
        raise NotImplementedError

    @abstractmethod
    def _get_undirectly_mapped_metadata_value_other_than_rating_from_raw_clean_metadata(
        self, raw_clean_metadata: RawMetadataDict, unified_metadata_key: UnifiedMetadataKey
    ) -> UnifiedMetadataValue:
        raise NotImplementedError

    def _get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
        self, raw_clean_metadata_uppercase_keys: RawMetadataDict, unified_metadata_key: UnifiedMetadataKey
    ) -> UnifiedMetadataValue | None:
        if unified_metadata_key == UnifiedMetadataKey.RATING:
            return self._get_potentially_normalized_rating_from_raw(raw_clean_metadata_uppercase_keys)
        return self._get_undirectly_mapped_metadata_value_other_than_rating_from_raw_clean_metadata(
            raw_clean_metadata=raw_clean_metadata_uppercase_keys, unified_metadata_key=unified_metadata_key
        )

    def _get_potentially_normalized_rating_from_raw(self, raw_clean_metadata: RawMetadataDict) -> int | None:
        file_rating, is_rating_from_traktor = self._get_raw_rating_by_traktor_or_not(raw_clean_metadata)
        if file_rating is None:
            return None
        if self.normalized_rating_max_value:
            if file_rating == 0 and is_rating_from_traktor:
                return None
            for star_rating_base_10 in range(11):
                if file_rating in [
                    RatingReadProfile.BASE_255_PROPORTIONAL_TRAKTOR[star_rating_base_10],
                    RatingReadProfile.BASE_255_NON_PROPORTIONAL[star_rating_base_10],
                    RatingReadProfile.BASE_100_PROPORTIONAL[star_rating_base_10],
                ]:
                    return int(star_rating_base_10 * self.normalized_rating_max_value / 10)
            return None
        return file_rating

    def _convert_normalized_rating_to_file_rating(self, normalized_rating: float) -> int | None:
        if not self.normalized_rating_max_value:
            msg = "normalized_rating_max_value must be set."
            raise ConfigurationError(msg)

        # Convert normalized rating to star rating index (0-10, where 0=0 stars, 1=0.5 stars, 2=1 star, etc.)
        # Use round() to properly handle half-star ratings (consistent with classic star rating systems)
        star_rating_base_10 = round((normalized_rating * 10) / self.normalized_rating_max_value)
        result = self.rating_write_profile[star_rating_base_10]
        return int(result) if result is not None else 0

    def _validate_rating_in_unified_metadata(self, unified_metadata: UnifiedMetadata) -> None:
        """Validate rating value in unified metadata if present.

        Args:
            unified_metadata: The metadata dictionary to validate

        Raises:
            InvalidRatingValueError: If rating value is invalid
        """
        if UnifiedMetadataKey.RATING in unified_metadata:
            value = unified_metadata[UnifiedMetadataKey.RATING]
            if value is not None:
                if isinstance(value, int | float):
                    # In raw mode (no normalization), only accept floats that can be parsed to int
                    # This allows the library to accept values like 196.0 as 196
                    if self.normalized_rating_max_value is None and isinstance(value, float):
                        if value.is_integer():
                            value = int(value)
                            unified_metadata[UnifiedMetadataKey.RATING] = value
                        else:
                            msg = (
                                f"Rating value {value} is invalid. In raw mode, float values must be whole numbers "
                                f"(e.g., 196.0). Half-star values like {value} require normalization."
                            )
                            raise InvalidRatingValueError(msg)
                    self.validate_rating_value(value, self.normalized_rating_max_value)
                else:
                    msg = f"Rating value must be numeric, got {type(value).__name__}"
                    raise InvalidRatingValueError(msg)

    def _validate_and_process_rating(self, unified_metadata: UnifiedMetadata) -> None:
        """Validate and process rating in unified metadata if present.

        This method handles:
        - Checking if rating is supported by the format
        - Validating the rating value
        - Converting normalized ratings to file ratings (when applicable)

        Args:
            unified_metadata: The metadata dictionary to validate and process

        Raises:
            MetadataFieldNotSupportedByMetadataFormatError: If rating is not supported by the format
            InvalidRatingValueError: If rating value is invalid
        """
        if UnifiedMetadataKey.RATING not in unified_metadata:
            return

        # Check if rating is supported by this format first
        if (
            not self.metadata_keys_direct_map_write
            or UnifiedMetadataKey.RATING not in self.metadata_keys_direct_map_write
        ):
            metadata_format_name = self._get_formatted_metadata_format_name()
            msg = f"{UnifiedMetadataKey.RATING} metadata not supported by {metadata_format_name} format"
            raise MetadataFieldNotSupportedByMetadataFormatError(msg)

        # Validate rating value before processing
        self._validate_rating_in_unified_metadata(unified_metadata)

        # If rating is mapped to None, it means it's handled indirectly by the manager
        # We should let the manager handle it in its own way
        if (
            self.metadata_keys_direct_map_write[UnifiedMetadataKey.RATING] is not None
            and self.update_using_mutagen_metadata
        ):
            # Only process rating if it's handled directly by the base class
            # (i.e., when using mutagen-based approach)
            value: int | float | None = unified_metadata[UnifiedMetadataKey.RATING]  # type: ignore[assignment]
            if value is not None:
                if self.normalized_rating_max_value is None:
                    # When no normalization, write value as-is (already validated above - must be int, floats rejected)
                    pass
                else:
                    try:
                        # Preserve float values to support half-star ratings (consistent with classic star rating
                        # systems)
                        normalized_rating = float(value)
                        file_rating = self._convert_normalized_rating_to_file_rating(
                            normalized_rating=normalized_rating
                        )
                        unified_metadata[UnifiedMetadataKey.RATING] = file_rating
                    except (TypeError, ValueError) as e:
                        msg = f"Invalid rating value: {value}. Expected a numeric value."
                        raise InvalidRatingValueError(msg) from e
                # If value is None, let the individual managers handle the removal

    def update_metadata(self, unified_metadata: UnifiedMetadata) -> None:
        self._validate_and_process_rating(unified_metadata)
        super().update_metadata(unified_metadata)
