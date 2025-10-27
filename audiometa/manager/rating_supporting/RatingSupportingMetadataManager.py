from abc import abstractmethod

from ...audio_file import AudioFile
from ...exceptions import ConfigurationError, InvalidRatingValueError, MetadataFieldNotSupportedByMetadataFormatError
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from ...utils.rating_profiles import RatingReadProfile, RatingWriteProfile
from ...utils.types import UnifiedMetadata, AppMetadataValue, RawMetadataDict, RawMetadataKey
from ..MetadataManager import MetadataManager


class RatingSupportingMetadataManager(MetadataManager):

    TRAKTOR_RATING_TAG_MAIL = 'traktor@native-instruments.de'

    normalized_rating_max_value: int | None
    rating_write_profile: RatingWriteProfile

    def __init__(self, audio_file: AudioFile,
                 metadata_keys_direct_map_read: dict[UnifiedMetadataKey, RawMetadataKey | None],
                 metadata_keys_direct_map_write: dict[UnifiedMetadataKey, RawMetadataKey | None],
                 rating_write_profile: RatingWriteProfile,
                 normalized_rating_max_value: int | None,
                 update_using_mutagen_metadata: bool = True):

        self.rating_write_profile = rating_write_profile
        self.normalized_rating_max_value = normalized_rating_max_value
        super().__init__(audio_file=audio_file,
                         update_using_mutagen_metadata=update_using_mutagen_metadata,
                         metadata_keys_direct_map_read=metadata_keys_direct_map_read,
                         metadata_keys_direct_map_write=metadata_keys_direct_map_write)

    @abstractmethod
    def _get_raw_rating_by_traktor_or_not(self, raw_clean_metadata: RawMetadataDict) -> tuple[int | None, bool]:
        """
        Returns True if the rating is from Traktor, False otherwise.
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_undirectly_mapped_metadata_value_other_than_rating_from_raw_clean_metadata(
            self, raw_clean_metadata: RawMetadataDict, unified_metadata_key: UnifiedMetadataKey) -> AppMetadataValue:
        raise NotImplementedError()

    def _get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            self, raw_clean_metadata_uppercase_keys: RawMetadataDict, unified_metadata_key: UnifiedMetadataKey) -> AppMetadataValue | None:
        if unified_metadata_key == UnifiedMetadataKey.RATING:
            return self._get_potentially_normalized_rating_from_raw(raw_clean_metadata_uppercase_keys)
        else:
            return self._get_undirectly_mapped_metadata_value_other_than_rating_from_raw_clean_metadata(
                raw_clean_metadata=raw_clean_metadata_uppercase_keys, unified_metadata_key=unified_metadata_key)

    def _get_potentially_normalized_rating_from_raw(self, raw_clean_metadata: RawMetadataDict) -> int | None:
        file_rating, is_rating_from_traktor = self._get_raw_rating_by_traktor_or_not(raw_clean_metadata)
        if file_rating is None:
            return None
        if self.normalized_rating_max_value:
            if file_rating == 0 and is_rating_from_traktor:
                return None
            for star_rating_base_10 in range(11):
                if file_rating in [RatingReadProfile.BASE_255_PROPORTIONAL_TRAKTOR[star_rating_base_10],
                                   RatingReadProfile.BASE_255_NON_PROPORTIONAL[star_rating_base_10],
                                   RatingReadProfile.BASE_100_PROPORTIONAL[star_rating_base_10]]:
                    return int(star_rating_base_10 * self.normalized_rating_max_value / 10)
            return None
        else:
            return file_rating

    def _convert_normalized_rating_to_file_rating(self, normalized_rating: int) -> int | None:
        if not self.normalized_rating_max_value:
            raise ConfigurationError("normalized_rating_max_value must be set.")

        star_rating_base_10 = (int)((normalized_rating * 10)/self.normalized_rating_max_value)
        return self.rating_write_profile[star_rating_base_10]

    def update_metadata(self, unified_metadata: UnifiedMetadata):
        if UnifiedMetadataKey.RATING in list[UnifiedMetadataKey](unified_metadata.keys()):
            # Check if rating is supported by this format first
            if (not self.metadata_keys_direct_map_write or 
                UnifiedMetadataKey.RATING not in self.metadata_keys_direct_map_write):
                # Get the format name for a more specific error message
                format_name = self.__class__.__name__.replace('Manager', '').upper()
                if format_name == 'RIFF':
                    format_name = 'RIFF'
                elif format_name == 'ID3V2':
                    format_name = 'ID3v2'
                elif format_name == 'VORBIS':
                    format_name = 'Vorbis'
                raise MetadataFieldNotSupportedByMetadataFormatError(f"{UnifiedMetadataKey.RATING} metadata not supported by {format_name} format")
            
            # If rating is mapped to None, it means it's handled indirectly by the manager
            # We should let the manager handle it in its own way
            if self.metadata_keys_direct_map_write[UnifiedMetadataKey.RATING] is not None:
                # Only process rating if it's handled directly by the base class
                # (i.e., when using mutagen-based approach)
                if self.update_using_mutagen_metadata:
                    value: int | None = unified_metadata[UnifiedMetadataKey.RATING]  # type: ignore
                    if value is not None:
                        if self.normalized_rating_max_value is None:
                            raise ConfigurationError(
                                "If updating the rating, the max value of the normalized rating must be set.")

                        try:
                            normalized_rating = int(float(value))
                            file_rating = self._convert_normalized_rating_to_file_rating(normalized_rating=normalized_rating)
                            unified_metadata[UnifiedMetadataKey.RATING] = file_rating
                        except (TypeError, ValueError):
                            raise InvalidRatingValueError(f"Invalid rating value: {value}. Expected a numeric value.")
                    # If value is None, let the individual managers handle the removal

        super().update_metadata(unified_metadata)
