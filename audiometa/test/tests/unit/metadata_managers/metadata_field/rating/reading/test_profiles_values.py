import pytest

from audiometa.utils.rating_profiles import RatingReadProfile


@pytest.mark.unit
class TestRatingProfileValues:
    @pytest.mark.parametrize(
        ("profile_enum", "expected_values"),
        [
            (RatingReadProfile.BASE_255_NON_PROPORTIONAL, (0, 13, 1, 54, 64, 118, 128, 186, 196, 242, 255)),
            (RatingReadProfile.BASE_100_PROPORTIONAL, (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)),
            (
                RatingReadProfile.BASE_255_PROPORTIONAL_TRAKTOR,
                (None, None, 51, None, 102, None, 153, None, 204, None, 255),
            ),
        ],
    )
    def test_profile_values(self, profile_enum, expected_values):
        profile = profile_enum.value

        assert profile == expected_values
        assert len(profile) == 11  # 0-5 stars (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)
