from abc import abstractmethod

from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey

from ..._audio_file import _AudioFile
from ...exceptions import ConfigurationError, InvalidRatingValueError, MetadataFieldNotSupportedByMetadataFormatError
from ...utils.rating_profiles import RatingReadProfile, RatingWriteProfile
from ...utils.types import AppMetadataValue, RawMetadataDict, RawMetadataKey, UnifiedMetadata
from .._MetadataManager import _MetadataManager


class _RatingSupportingMetadataManager(_MetadataManager):
    TRAKTOR_RATING_TAG_MAIL = "traktor@native-instruments.de"

    normalized_rating_max_value: int | None
    rating_write_profile: RatingWriteProfile

    def __init__(
        self,
        audio_file: _AudioFile,
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

    @abstractmethod
    def _get_raw_rating_by_traktor_or_not(self, raw_clean_metadata: RawMetadataDict) -> tuple[int | None, bool]:
        """Return True if the rating is from Traktor, False otherwise."""
        raise NotImplementedError()

    @abstractmethod
    def _get_undirectly_mapped_metadata_value_other_than_rating_from_raw_clean_metadata(
        self, raw_clean_metadata: RawMetadataDict, unified_metadata_key: UnifiedMetadataKey
    ) -> AppMetadataValue:
        raise NotImplementedError()

    def _get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
        self, raw_clean_metadata_uppercase_keys: RawMetadataDict, unified_metadata_key: UnifiedMetadataKey
    ) -> AppMetadataValue | None:
        if unified_metadata_key == UnifiedMetadataKey.RATING:
            return self._get_potentially_normalized_rating_from_raw(raw_clean_metadata_uppercase_keys)
        else:
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
        else:
            return file_rating

    def _convert_normalized_rating_to_file_rating(self, normalized_rating: int) -> int | None:
        if not self.normalized_rating_max_value:
            raise ConfigurationError("normalized_rating_max_value must be set.")

        star_rating_base_10 = int((normalized_rating * 10) / self.normalized_rating_max_value)
        result = self.rating_write_profile[star_rating_base_10]
        return int(result) if result is not None else 0

    def _validate_rating_value(self, rating_value: int) -> None:
        """Validate rating value based on normalized_rating_max_value.

        Rules:
        - When normalized_rating_max_value is None: value must be >= 0 (any non-negative integer is allowed)
        - When normalized_rating_max_value is provided: value must be between 0 and normalized_rating_max_value
          and must be a tenth ratio of max (i.e., (value * 10) % normalized_rating_max_value == 0)

        Raises InvalidRatingValueError if validation fails.
        """
        if self.normalized_rating_max_value is None:
            # Rating is written as-is - must be non-negative
            if rating_value < 0:
                raise InvalidRatingValueError(
                    f"Rating value {rating_value} is invalid. Rating values must be non-negative (>= 0)."
                )
        else:
            # Value is normalized - must be non-negative, within max, and a tenth ratio of max
            if rating_value < 0:
                raise InvalidRatingValueError(
                    f"Rating value {rating_value} is invalid. Rating values must be non-negative (>= 0)."
                )
            if rating_value > self.normalized_rating_max_value:
                raise InvalidRatingValueError(
                    f"Rating value {rating_value} is out of range. "
                    f"Value must be between 0 and {self.normalized_rating_max_value} (inclusive)."
                )
            # Formula: (value * 10) must be divisible by normalized_rating_max_value
            if (rating_value * 10) % self.normalized_rating_max_value != 0:
                raise InvalidRatingValueError(
                    f"Rating value {rating_value} is not a valid tenth ratio of max value "
                    f"{self.normalized_rating_max_value}. "
                    f"Value must satisfy: (value * 10) % {self.normalized_rating_max_value} == 0"
                )

    def _validate_rating_in_unified_metadata(self, unified_metadata: UnifiedMetadata) -> None:
        """Validate rating value in unified metadata if present.

        Args:
            unified_metadata: The metadata dictionary to validate

        Raises:
            InvalidRatingValueError: If rating value is invalid
        """
        if UnifiedMetadataKey.RATING in unified_metadata:
            value: int | None = unified_metadata[UnifiedMetadataKey.RATING]  # type: ignore
            if value is not None:
                if isinstance(value, (int, float)):
                    rating_int = int(value)
                    self._validate_rating_value(rating_int)
                else:
                    raise InvalidRatingValueError(f"Rating value must be numeric, got {type(value).__name__}")

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
            metadata_format_name = self.__class__.__name__.replace("Manager", "").upper()
            if metadata_format_name == "RIFF":
                metadata_format_name = "RIFF"
            elif metadata_format_name == "ID3V2":
                metadata_format_name = "ID3v2"
            elif metadata_format_name == "VORBIS":
                metadata_format_name = "Vorbis"
            raise MetadataFieldNotSupportedByMetadataFormatError(
                f"{UnifiedMetadataKey.RATING} metadata not supported by {metadata_format_name} format"
            )

        # Validate rating value before processing
        self._validate_rating_in_unified_metadata(unified_metadata)

        # If rating is mapped to None, it means it's handled indirectly by the manager
        # We should let the manager handle it in its own way
        if self.metadata_keys_direct_map_write[UnifiedMetadataKey.RATING] is not None:
            # Only process rating if it's handled directly by the base class
            # (i.e., when using mutagen-based approach)
            if self.update_using_mutagen_metadata:
                value: int | None = unified_metadata[UnifiedMetadataKey.RATING]  # type: ignore
                if value is not None:
                    if self.normalized_rating_max_value is None:
                        # When no normalization, write value as-is (already validated above)
                        pass
                    else:
                        try:
                            normalized_rating = int(float(value))
                            file_rating = self._convert_normalized_rating_to_file_rating(
                                normalized_rating=normalized_rating
                            )
                            unified_metadata[UnifiedMetadataKey.RATING] = file_rating
                        except (TypeError, ValueError):
                            raise InvalidRatingValueError(f"Invalid rating value: {value}. Expected a numeric value.")
                # If value is None, let the individual managers handle the removal

    def update_metadata(self, unified_metadata: UnifiedMetadata) -> None:
        self._validate_and_process_rating(unified_metadata)
        super().update_metadata(unified_metadata)
