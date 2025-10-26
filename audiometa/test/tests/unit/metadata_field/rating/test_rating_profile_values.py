
from audiometa.utils.rating_profiles import RatingReadProfile, RatingWriteProfile


class TestRatingProfileValues:
    
    def test_base_255_non_proportional_profile_values(self):
        profile = RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        expected_values = [0, 13, 1, 54, 64, 118, 128, 186, 196, 242, 255]
        
        assert profile == expected_values
        assert len(profile) == 11  # 0-5 stars (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)
        
        # Test that all values are integers
        for value in profile:
            assert isinstance(value, int)
            assert 0 <= value <= 255

    def test_base_100_proportional_profile_values(self):
        # Test description removed per workspace rules
        profile = RatingReadProfile.BASE_100_PROPORTIONAL.value
        expected_values = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        
        assert profile == expected_values
        assert len(profile) == 11  # 0-5 stars (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)
        
        # Test that all values are integers
        for value in profile:
            assert isinstance(value, int)
            assert 0 <= value <= 100

    def test_base_255_proportional_profile_values(self):
        # Test description removed per workspace rules
        profile = RatingReadProfile.BASE_255_PROPORTIONAL.value
        expected_values = [None, None, 51, None, 102, None, 153, None, 204, None, 255]
        
        assert profile == expected_values
        assert len(profile) == 11  # 0-5 stars (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)
        
        # Test that non-None values are integers in valid range
        for value in profile:
            if value is not None:
                assert isinstance(value, int)
                assert 0 <= value <= 255

    def test_write_profile_consistency(self):
        # Test description removed per workspace rules
        assert RatingWriteProfile.BASE_255_NON_PROPORTIONAL.value == RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        assert RatingWriteProfile.BASE_100_PROPORTIONAL.value == RatingReadProfile.BASE_100_PROPORTIONAL.value
        # Note: BASE_255_PROPORTIONAL is only for reading, not writing

    def test_profile_star_mapping_consistency(self):
        # Test description removed per workspace rules
        star_ratings = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
        
        base_255_non_prop = RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        base_100_prop = RatingReadProfile.BASE_100_PROPORTIONAL.value
        base_255_prop = RatingReadProfile.BASE_255_PROPORTIONAL.value
        
        # All profiles should have the same length (11 values for 0-5 stars)
        assert len(base_255_non_prop) == 11
        assert len(base_100_prop) == 11
        assert len(base_255_prop) == 11
        
        # Test that each star rating has a corresponding value in each profile
        for i, star_rating in enumerate(star_ratings):
            # BASE_255_NON_PROPORTIONAL should have a value for all star ratings
            assert base_255_non_prop[i] is not None
            assert isinstance(base_255_non_prop[i], int)
            
            # BASE_100_PROPORTIONAL should have a value for all star ratings
            assert base_100_prop[i] is not None
            assert isinstance(base_100_prop[i], int)
            
            # BASE_255_PROPORTIONAL should have None for half-star ratings and 0 stars, values for whole stars
            if star_rating % 1 == 0 and star_rating > 0:  # Whole star ratings (1, 2, 3, 4, 5)
                assert base_255_prop[i] is not None
                assert isinstance(base_255_prop[i], int)
            else:  # Half-star ratings (0.5, 1.5, 2.5, 3.5, 4.5) and 0 stars
                assert base_255_prop[i] is None

    def test_profile_value_ranges(self):
        # Test description removed per workspace rules
        base_255_non_prop = RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        base_100_prop = RatingReadProfile.BASE_100_PROPORTIONAL.value
        base_255_prop = RatingReadProfile.BASE_255_PROPORTIONAL.value
        
        # BASE_255_NON_PROPORTIONAL: values should be 0-255
        for value in base_255_non_prop:
            assert 0 <= value <= 255
        
        # BASE_100_PROPORTIONAL: values should be 0-100
        for value in base_100_prop:
            assert 0 <= value <= 100
        
        # BASE_255_PROPORTIONAL: non-None values should be 0-255
        for value in base_255_prop:
            if value is not None:
                assert 0 <= value <= 255

    def test_profile_value_progression(self):
        # Test description removed per workspace rules
        base_255_non_prop = RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        base_100_prop = RatingReadProfile.BASE_100_PROPORTIONAL.value
        base_255_prop = RatingReadProfile.BASE_255_PROPORTIONAL.value
        
        # BASE_100_PROPORTIONAL should be linear progression
        for i in range(1, len(base_100_prop)):
            assert base_100_prop[i] > base_100_prop[i-1]
        
        # BASE_255_NON_PROPORTIONAL is non-linear (not monotonically increasing)
        # This is expected behavior - the values are not in ascending order
        # We just verify they are all valid integers
        for value in base_255_non_prop:
            assert isinstance(value, int)
            assert 0 <= value <= 255
        
        # BASE_255_PROPORTIONAL should be linear for non-None values
        non_none_values = [v for v in base_255_prop if v is not None]
        for i in range(1, len(non_none_values)):
            assert non_none_values[i] > non_none_values[i-1]

    def test_profile_specific_values(self):
        """Test specific known values from the rating compatibility table."""
        base_255_non_prop = RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        base_100_prop = RatingReadProfile.BASE_100_PROPORTIONAL.value
        base_255_prop = RatingReadProfile.BASE_255_PROPORTIONAL.value
        
        # Test specific values from the compatibility table
        assert base_255_non_prop[0] == 0    # 0 stars
        assert base_255_non_prop[2] == 1    # 1 star
        assert base_255_non_prop[4] == 64   # 2 stars
        assert base_255_non_prop[6] == 128  # 3 stars
        assert base_255_non_prop[8] == 196  # 4 stars
        assert base_255_non_prop[10] == 255 # 5 stars
        
        assert base_100_prop[0] == 0    # 0 stars
        assert base_100_prop[2] == 20   # 1 star
        assert base_100_prop[4] == 40   # 2 stars
        assert base_100_prop[6] == 60   # 3 stars
        assert base_100_prop[8] == 80   # 4 stars
        assert base_100_prop[10] == 100 # 5 stars
        
        assert base_255_prop[0] is None     # 0 stars (Traktor)
        assert base_255_prop[2] == 51      # 1 star (Traktor)
        assert base_255_prop[4] == 102     # 2 stars (Traktor)
        assert base_255_prop[6] == 153     # 3 stars (Traktor)
        assert base_255_prop[8] == 204     # 4 stars (Traktor)
        assert base_255_prop[10] == 255    # 5 stars (Traktor)

    def test_profile_enum_behavior(self):
        # Test description removed per workspace rules
        # Test that we can access values
        assert hasattr(RatingReadProfile, 'BASE_255_NON_PROPORTIONAL')
        assert hasattr(RatingReadProfile, 'BASE_100_PROPORTIONAL')
        assert hasattr(RatingReadProfile, 'BASE_255_PROPORTIONAL')
        
        assert hasattr(RatingWriteProfile, 'BASE_255_NON_PROPORTIONAL')
        assert hasattr(RatingWriteProfile, 'BASE_100_PROPORTIONAL')
        
        # Test that values are lists
        assert isinstance(RatingReadProfile.BASE_255_NON_PROPORTIONAL.value, list)
        assert isinstance(RatingReadProfile.BASE_100_PROPORTIONAL.value, list)
        assert isinstance(RatingReadProfile.BASE_255_PROPORTIONAL.value, list)
        
        assert isinstance(RatingWriteProfile.BASE_255_NON_PROPORTIONAL.value, list)
        assert isinstance(RatingWriteProfile.BASE_100_PROPORTIONAL.value, list)
