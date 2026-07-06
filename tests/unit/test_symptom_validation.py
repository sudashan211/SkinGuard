"""
Unit tests for Symptom Data Validation
Tests specific examples and edge cases for symptom data validation

Requirements: 5.2, 5.3, 5.4, 5.5, 5.6
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.models import SymptomData
from pydantic import ValidationError


class TestSymptomDataValidation:
    """Test suite for SymptomData model validation"""
    
    def test_complete_symptom_data(self):
        """Test creating SymptomData with all fields"""
        symptom_data = SymptomData(
            body_location="left_arm",
            sensations=["itching", "pain"],
            visual_changes=["color", "size"],
            duration="2 weeks"
        )
        
        assert symptom_data.body_location == "left_arm"
        assert symptom_data.sensations == ["itching", "pain"]
        assert symptom_data.visual_changes == ["color", "size"]
        assert symptom_data.duration == "2 weeks"
    
    def test_empty_symptom_data(self):
        """Test creating SymptomData with no fields (all optional)"""
        symptom_data = SymptomData()
        
        assert symptom_data.body_location is None
        assert symptom_data.sensations == []
        assert symptom_data.visual_changes == []
        assert symptom_data.duration is None
    
    def test_partial_symptom_data_location_only(self):
        """Test creating SymptomData with only body location"""
        symptom_data = SymptomData(body_location="face")
        
        assert symptom_data.body_location == "face"
        assert symptom_data.sensations == []
        assert symptom_data.visual_changes == []
        assert symptom_data.duration is None
    
    def test_partial_symptom_data_sensations_only(self):
        """Test creating SymptomData with only sensations"""
        symptom_data = SymptomData(sensations=["burning", "numbness"])
        
        assert symptom_data.body_location is None
        assert symptom_data.sensations == ["burning", "numbness"]
        assert symptom_data.visual_changes == []
        assert symptom_data.duration is None
    
    def test_partial_symptom_data_visual_changes_only(self):
        """Test creating SymptomData with only visual changes"""
        symptom_data = SymptomData(visual_changes=["shape", "border"])
        
        assert symptom_data.body_location is None
        assert symptom_data.sensations == []
        assert symptom_data.visual_changes == ["shape", "border"]
        assert symptom_data.duration is None
    
    def test_valid_sensations(self):
        """Test all valid sensation values"""
        valid_sensations = ['itching', 'pain', 'burning', 'numbness', 'tingling', 'none']
        
        for sensation in valid_sensations:
            symptom_data = SymptomData(sensations=[sensation])
            assert sensation in symptom_data.sensations
    
    def test_valid_visual_changes(self):
        """Test all valid visual change values"""
        valid_changes = ['color', 'size', 'shape', 'border', 'texture', 'bleeding', 'none']
        
        for change in valid_changes:
            symptom_data = SymptomData(visual_changes=[change])
            assert change in symptom_data.visual_changes
    
    def test_invalid_sensation(self):
        """Test that invalid sensation is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            SymptomData(sensations=["invalid_sensation"])
        
        error = exc_info.value
        assert "Invalid sensation" in str(error)
    
    def test_invalid_visual_change(self):
        """Test that invalid visual change is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            SymptomData(visual_changes=["invalid_change"])
        
        error = exc_info.value
        assert "Invalid visual change" in str(error)
    
    def test_multiple_invalid_sensations(self):
        """Test that multiple invalid sensations are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            SymptomData(sensations=["invalid1", "invalid2"])
        
        error = exc_info.value
        assert "Invalid sensation" in str(error)
    
    def test_mixed_valid_invalid_sensations(self):
        """Test that mixed valid/invalid sensations are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            SymptomData(sensations=["itching", "invalid_sensation"])
        
        error = exc_info.value
        assert "Invalid sensation" in str(error)
    
    def test_case_insensitive_sensations(self):
        """Test that sensations are case-insensitive"""
        symptom_data = SymptomData(sensations=["ITCHING", "Pain", "BuRnInG"])
        
        # Should be normalized to lowercase
        assert symptom_data.sensations == ["itching", "pain", "burning"]
    
    def test_case_insensitive_visual_changes(self):
        """Test that visual changes are case-insensitive"""
        symptom_data = SymptomData(visual_changes=["COLOR", "Size", "ShApE"])
        
        # Should be normalized to lowercase
        assert symptom_data.visual_changes == ["color", "size", "shape"]
    
    def test_empty_string_body_location(self):
        """Test that empty string body location is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            SymptomData(body_location="   ")
        
        error = exc_info.value
        assert "Body location cannot be empty string" in str(error)
    
    def test_empty_string_duration(self):
        """Test that empty string duration is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            SymptomData(duration="   ")
        
        error = exc_info.value
        assert "Duration cannot be empty string" in str(error)
    
    def test_whitespace_trimming_body_location(self):
        """Test that body location whitespace is trimmed"""
        symptom_data = SymptomData(body_location="  left_arm  ")
        
        assert symptom_data.body_location == "left_arm"
    
    def test_whitespace_trimming_duration(self):
        """Test that duration whitespace is trimmed"""
        symptom_data = SymptomData(duration="  2 weeks  ")
        
        assert symptom_data.duration == "2 weeks"
    
    def test_dict_conversion(self):
        """Test converting SymptomData to dict for JSONB storage"""
        symptom_data = SymptomData(
            body_location="chest",
            sensations=["pain"],
            visual_changes=["color", "size"],
            duration="1 month"
        )
        
        symptom_dict = symptom_data.dict()
        
        assert isinstance(symptom_dict, dict)
        assert symptom_dict["body_location"] == "chest"
        assert symptom_dict["sensations"] == ["pain"]
        assert symptom_dict["visual_changes"] == ["color", "size"]
        assert symptom_dict["duration"] == "1 month"
    
    def test_dict_conversion_with_none_values(self):
        """Test dict conversion includes None values"""
        symptom_data = SymptomData()
        
        symptom_dict = symptom_data.dict()
        
        assert "body_location" in symptom_dict
        assert "sensations" in symptom_dict
        assert "visual_changes" in symptom_dict
        assert "duration" in symptom_dict
        assert symptom_dict["body_location"] is None
        assert symptom_dict["sensations"] == []
        assert symptom_dict["visual_changes"] == []
        assert symptom_dict["duration"] is None
    
    def test_none_sensation_value(self):
        """Test that 'none' is a valid sensation value"""
        symptom_data = SymptomData(sensations=["none"])
        
        assert symptom_data.sensations == ["none"]
    
    def test_none_visual_change_value(self):
        """Test that 'none' is a valid visual change value"""
        symptom_data = SymptomData(visual_changes=["none"])
        
        assert symptom_data.visual_changes == ["none"]
    
    def test_duplicate_sensations(self):
        """Test that duplicate sensations are allowed"""
        # Note: The model doesn't enforce uniqueness, but the frontend should
        symptom_data = SymptomData(sensations=["itching", "itching"])
        
        assert len(symptom_data.sensations) == 2
        assert symptom_data.sensations == ["itching", "itching"]
    
    def test_all_sensations_combined(self):
        """Test using all valid sensations together"""
        all_sensations = ['itching', 'pain', 'burning', 'numbness', 'tingling', 'none']
        symptom_data = SymptomData(sensations=all_sensations)
        
        assert symptom_data.sensations == all_sensations
    
    def test_all_visual_changes_combined(self):
        """Test using all valid visual changes together"""
        all_changes = ['color', 'size', 'shape', 'border', 'texture', 'bleeding', 'none']
        symptom_data = SymptomData(visual_changes=all_changes)
        
        assert symptom_data.visual_changes == all_changes
    
    def test_realistic_duration_formats(self):
        """Test various realistic duration formats"""
        durations = [
            "1 day",
            "2 weeks",
            "3 months",
            "1 year",
            "less than a week",
            "more than a month",
            "several weeks",
            "a few days"
        ]
        
        for duration in durations:
            symptom_data = SymptomData(duration=duration)
            assert symptom_data.duration == duration
    
    def test_realistic_body_locations(self):
        """Test various realistic body locations"""
        locations = [
            "left_arm", "right_arm", "left_leg", "right_leg",
            "chest", "back", "abdomen", "face", "neck",
            "left_hand", "right_hand", "left_foot", "right_foot",
            "scalp", "shoulder", "upper_back", "lower_back"
        ]
        
        for location in locations:
            symptom_data = SymptomData(body_location=location)
            assert symptom_data.body_location == location


class TestSymptomDataEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_long_body_location(self):
        """Test that very long body location strings are accepted"""
        long_location = "left_arm_upper_section_near_elbow_with_detailed_description"
        symptom_data = SymptomData(body_location=long_location)
        
        assert symptom_data.body_location == long_location
    
    def test_very_long_duration(self):
        """Test that very long duration strings are accepted"""
        long_duration = "approximately 2 weeks and 3 days, starting from last Tuesday"
        symptom_data = SymptomData(duration=long_duration)
        
        assert symptom_data.duration == long_duration
    
    def test_empty_sensations_list(self):
        """Test that empty sensations list is valid"""
        symptom_data = SymptomData(sensations=[])
        
        assert symptom_data.sensations == []
    
    def test_empty_visual_changes_list(self):
        """Test that empty visual changes list is valid"""
        symptom_data = SymptomData(visual_changes=[])
        
        assert symptom_data.visual_changes == []
    
    def test_single_sensation(self):
        """Test single sensation in list"""
        symptom_data = SymptomData(sensations=["itching"])
        
        assert len(symptom_data.sensations) == 1
        assert symptom_data.sensations[0] == "itching"
    
    def test_single_visual_change(self):
        """Test single visual change in list"""
        symptom_data = SymptomData(visual_changes=["color"])
        
        assert len(symptom_data.visual_changes) == 1
        assert symptom_data.visual_changes[0] == "color"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
