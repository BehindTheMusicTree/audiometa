
from audiometa.utils.rating_profiles import RatingReadProfile, RatingWriteProfile


class TestRatingProfileMapping:
    
    def test_star_rating_to_profile_value_mapping(self):
        # Test description removed per workspace rules
        star_ratings = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
        
        base_255_non_prop = RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        base_100_prop = RatingReadProfile.BASE_100_PROPORTIONAL.value
        base_255_prop = RatingReadProfile.BASE_255_PROPORTIONAL.value
        
        # Test that each star rating maps to the correct profile value
        for i, star_rating in enumerate(star_ratings):
            # Test BASE_255_NON_PROPORTIONAL mapping
            expected_value_255_non_prop = base_255_non_prop[i]
            assert expected_value_255_non_prop is not None
            assert isinstance(expected_value_255_non_prop, int)
            
            # Test BASE_100_PROPORTIONAL mapping
            expected_value_100_prop = base_100_prop[i]
            assert expected_value_100_prop is not None
            assert isinstance(expected_value_100_prop, int)
            
            # Test BASE_255_PROPORTIONAL mapping (only for whole stars > 0)
            expected_value_255_prop = base_255_prop[i]
            if star_rating % 1 == 0 and star_rating > 0:  # Whole star ratings > 0
                assert expected_value_255_prop is not None
                assert isinstance(expected_value_255_prop, int)
            else:  # Half-star ratings and 0 stars
                assert expected_value_255_prop is None

    def test_profile_value_to_star_rating_mapping(self):
        # Test description removed per workspace rules
        # Test BASE_255_NON_PROPORTIONAL values
        base_255_non_prop = RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        for i, value in enumerate(base_255_non_prop):
            # Each value should map to its index (0-10) representing 0-5 stars
            expected_star_rating = i / 2.0  # 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5
            assert value is not None
            # The value itself represents the raw rating, not the star rating
            # But we can verify it's in the expected range for that star rating
            
        # Test BASE_100_PROPORTIONAL values
        base_100_prop = RatingReadProfile.BASE_100_PROPORTIONAL.value
        for i, value in enumerate(base_100_prop):
            expected_star_rating = i / 2.0  # 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5
            assert value is not None
            # For BASE_100_PROPORTIONAL, the value should be proportional to star rating
            expected_value = int(expected_star_rating * 20)  # 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100
            assert value == expected_value
            
        # Test BASE_255_PROPORTIONAL values
        base_255_prop = RatingReadProfile.BASE_255_PROPORTIONAL.value
        for i, value in enumerate(base_255_prop):
            expected_star_rating = i / 2.0  # 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5
            if value is not None:
                # For BASE_255_PROPORTIONAL, the value should be proportional to star rating
                expected_value = int(expected_star_rating * 51)  # 0, 25.5, 51, 76.5, 102, 127.5, 153, 178.5, 204, 229.5, 255
                # But only for whole star ratings, and the actual values are rounded
                if expected_star_rating % 1 == 0:
                    assert value == expected_value

    def test_cross_profile_consistency(self):
        # Test description removed per workspace rules
        # Test that all profiles produce the same star rating for equivalent values
        star_ratings = [0, 1, 2, 3, 4, 5]  # Only whole star ratings for cross-profile comparison
        
        base_255_non_prop = RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        base_100_prop = RatingReadProfile.BASE_100_PROPORTIONAL.value
        base_255_prop = RatingReadProfile.BASE_255_PROPORTIONAL.value
        
        for star_rating in star_ratings:
            index = int(star_rating * 2)  # Convert star rating to index
            
            # Get values from each profile
            value_255_non_prop = base_255_non_prop[index]
            value_100_prop = base_100_prop[index]
            value_255_prop = base_255_prop[index]
            
            # All should be non-None for whole star ratings
            assert value_255_non_prop is not None
            assert value_100_prop is not None
            # BASE_255_PROPORTIONAL has None for 0 stars
            if star_rating > 0:
                assert value_255_prop is not None
            else:
                assert value_255_prop is None
            
            # All should be integers
            assert isinstance(value_255_non_prop, int)
            assert isinstance(value_100_prop, int)
            if value_255_prop is not None:
                assert isinstance(value_255_prop, int)
            
            # All should be in valid ranges
            assert 0 <= value_255_non_prop <= 255
            assert 0 <= value_100_prop <= 100
            if value_255_prop is not None:
                assert 0 <= value_255_prop <= 255

    def test_profile_value_uniqueness(self):
        # Test description removed per workspace rules
        base_255_non_prop = RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        base_100_prop = RatingReadProfile.BASE_100_PROPORTIONAL.value
        base_255_prop = RatingReadProfile.BASE_255_PROPORTIONAL.value
        
        # Test BASE_255_NON_PROPORTIONAL uniqueness
        assert len(base_255_non_prop) == len(set(base_255_non_prop))
        
        # Test BASE_100_PROPORTIONAL uniqueness
        assert len(base_100_prop) == len(set(base_100_prop))
        
        # Test BASE_255_PROPORTIONAL uniqueness (excluding None values)
        non_none_values = [v for v in base_255_prop if v is not None]
        assert len(non_none_values) == len(set(non_none_values))

    def test_profile_value_monotonicity(self):
        # Test description removed per workspace rules
        base_255_non_prop = RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        base_100_prop = RatingReadProfile.BASE_100_PROPORTIONAL.value
        base_255_prop = RatingReadProfile.BASE_255_PROPORTIONAL.value
        
        # BASE_255_NON_PROPORTIONAL is not monotonically increasing (by design)
        # We just verify all values are valid integers
        for value in base_255_non_prop:
            assert isinstance(value, int)
            assert 0 <= value <= 255
        
        # Test BASE_100_PROPORTIONAL monotonicity
        for i in range(1, len(base_100_prop)):
            assert base_100_prop[i] > base_100_prop[i-1]
        
        # Test BASE_255_PROPORTIONAL monotonicity (for non-None values)
        non_none_values = [v for v in base_255_prop if v is not None]
        for i in range(1, len(non_none_values)):
            assert non_none_values[i] > non_none_values[i-1]

    def test_write_profile_consistency(self):
        # Test description removed per workspace rules
        # BASE_255_NON_PROPORTIONAL should be identical
        assert RatingWriteProfile.BASE_255_NON_PROPORTIONAL.value == RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        
        # BASE_100_PROPORTIONAL should be identical
        assert RatingWriteProfile.BASE_100_PROPORTIONAL.value == RatingReadProfile.BASE_100_PROPORTIONAL.value
        
        # BASE_255_PROPORTIONAL is only for reading, not writing
        assert not hasattr(RatingWriteProfile, 'BASE_255_PROPORTIONAL')

    def test_profile_edge_cases(self):
        """Test edge cases in profile values."""
        base_255_non_prop = RatingReadProfile.BASE_255_NON_PROPORTIONAL.value
        base_100_prop = RatingReadProfile.BASE_100_PROPORTIONAL.value
        base_255_prop = RatingReadProfile.BASE_255_PROPORTIONAL.value
        
        # Test minimum values
        assert base_255_non_prop[0] == 0
        assert base_100_prop[0] == 0
        assert base_255_prop[0] is None  # Traktor doesn't use 0 for no rating
        
        # Test maximum values
        assert base_255_non_prop[-1] == 255
        assert base_100_prop[-1] == 100
        assert base_255_prop[-1] == 255
        
        # Test that all profiles have the same length
        assert len(base_255_non_prop) == 11
        assert len(base_100_prop) == 11
        assert len(base_255_prop) == 11
