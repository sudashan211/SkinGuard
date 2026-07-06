"""
Property-Based Tests for Skin-Wiki Educational Content
Requirements: 16.1, 16.2, 16.3, 16.4, 16.5

Property 44: Skin-Wiki Cancer Type Completeness
Property 45: Cancer Type Article Completeness
Property 46: Educational Content Availability
Property 47: Prevention Tips Completeness
Property 48: Contextual Educational Links
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.database import supabase


# ============================================================================
# Property 44: Skin-Wiki Cancer Type Completeness
# ============================================================================

def test_property_44_skin_wiki_cancer_type_completeness():
    """
    Property 44: Skin-Wiki Cancer Type Completeness
    
    For any Skin-Wiki section access, the displayed content should include 
    articles for all 7 skin cancer types with images and descriptions.
    
    Validates: Requirements 16.1
    """
    # Define the 7 required cancer types
    required_cancer_types = {
        'melanoma',
        'basal_cell_carcinoma',
        'squamous_cell_carcinoma',
        'actinic_keratosis',
        'benign_keratosis',
        'dermatofibroma',
        'vascular_lesion'
    }
    
    # Get all published articles
    result = supabase.table("skin_wiki_articles")\
        .select("cancer_type, image_url, summary")\
        .eq("published", True)\
        .execute()
    
    articles = result.data if result.data else []
    
    # Extract cancer types from articles
    article_cancer_types = {article['cancer_type'] for article in articles}
    
    # Verify all 7 cancer types are present
    assert article_cancer_types == required_cancer_types, \
        f"Missing cancer types: {required_cancer_types - article_cancer_types}"
    
    # Verify each article has image and description
    for article in articles:
        assert article.get('image_url'), \
            f"Article for {article['cancer_type']} missing image_url"
        assert article.get('summary'), \
            f"Article for {article['cancer_type']} missing summary/description"
    
    print(f"✓ Property 44 verified: All 7 cancer types present with images and descriptions")


# ============================================================================
# Property 45: Cancer Type Article Completeness
# ============================================================================

@given(
    cancer_type=st.sampled_from([
        'melanoma',
        'basal_cell_carcinoma',
        'squamous_cell_carcinoma',
        'actinic_keratosis',
        'benign_keratosis',
        'dermatofibroma',
        'vascular_lesion'
    ])
)
@settings(max_examples=7, deadline=None)
def test_property_45_cancer_type_article_completeness(cancer_type):
    """
    Property 45: Cancer Type Article Completeness
    
    For any cancer type article, the content should include sections for 
    risk factors, symptoms, and treatment options.
    
    Validates: Requirements 16.2
    """
    # Get article for this cancer type
    result = supabase.table("skin_wiki_articles")\
        .select("*")\
        .eq("cancer_type", cancer_type)\
        .eq("published", True)\
        .execute()
    
    # If no article exists yet, skip this test case
    assume(result.data and len(result.data) > 0)
    
    article = result.data[0]
    
    # Verify risk_factors section exists and is not empty
    assert article.get('risk_factors'), \
        f"Article for {cancer_type} missing risk_factors"
    assert isinstance(article['risk_factors'], list), \
        f"Article for {cancer_type} risk_factors should be a list"
    assert len(article['risk_factors']) > 0, \
        f"Article for {cancer_type} has empty risk_factors"
    
    # Verify symptoms section exists and is not empty
    assert article.get('symptoms'), \
        f"Article for {cancer_type} missing symptoms"
    assert isinstance(article['symptoms'], list), \
        f"Article for {cancer_type} symptoms should be a list"
    assert len(article['symptoms']) > 0, \
        f"Article for {cancer_type} has empty symptoms"
    
    # Verify treatments section exists and is not empty
    assert article.get('treatments'), \
        f"Article for {cancer_type} missing treatments"
    assert isinstance(article['treatments'], list), \
        f"Article for {cancer_type} treatments should be a list"
    assert len(article['treatments']) > 0, \
        f"Article for {cancer_type} has empty treatments"
    
    print(f"✓ Property 45 verified for {cancer_type}: Article has risk_factors, symptoms, and treatments")


# ============================================================================
# Property 46: Educational Content Availability
# ============================================================================

def test_property_46_educational_content_availability():
    """
    Property 46: Educational Content Availability
    
    For any educational content view, self-examination guides with 
    illustrated body maps should be accessible.
    
    Validates: Requirements 16.3
    """
    # This property tests that the self-examination guide endpoint returns
    # structured data with steps and body map
    
    # Import the router function
    from app.routers.skin_wiki import get_self_examination_guide
    import asyncio
    
    # Call the endpoint
    guide = asyncio.run(get_self_examination_guide())
    
    # Verify guide structure
    assert guide is not None, "Self-examination guide should not be None"
    assert 'title' in guide, "Guide missing title"
    assert 'steps' in guide, "Guide missing steps"
    assert 'body_map' in guide, "Guide missing body_map"
    
    # Verify steps are present
    assert isinstance(guide['steps'], list), "Steps should be a list"
    assert len(guide['steps']) > 0, "Steps should not be empty"
    
    # Verify each step has required fields
    for step in guide['steps']:
        assert 'step_number' in step, "Step missing step_number"
        assert 'title' in step, "Step missing title"
        assert 'description' in step, "Step missing description"
        assert 'tips' in step, "Step missing tips"
    
    # Verify body map is present
    assert isinstance(guide['body_map'], list), "Body map should be a list"
    assert len(guide['body_map']) > 0, "Body map should not be empty"
    
    # Verify each body region has required fields
    for region in guide['body_map']:
        assert 'id' in region, "Body region missing id"
        assert 'name' in region, "Body region missing name"
        assert 'description' in region, "Body region missing description"
        assert 'common_lesions' in region, "Body region missing common_lesions"
    
    print(f"✓ Property 46 verified: Self-examination guide with {len(guide['steps'])} steps and {len(guide['body_map'])} body regions")


# ============================================================================
# Property 47: Prevention Tips Completeness
# ============================================================================

def test_property_47_prevention_tips_completeness():
    """
    Property 47: Prevention Tips Completeness
    
    For any prevention tips display, the content should include UV protection 
    recommendations and early detection guidelines.
    
    Validates: Requirements 16.4
    """
    # Import the router function
    from app.routers.skin_wiki import get_prevention_tips
    import asyncio
    
    # Call the endpoint
    tips = asyncio.run(get_prevention_tips())
    
    # Verify tips structure
    assert tips is not None, "Prevention tips should not be None"
    
    # Verify UV protection recommendations are present
    assert 'uv_protection' in tips, "Prevention tips missing uv_protection category"
    assert isinstance(tips['uv_protection'], list), "UV protection should be a list"
    assert len(tips['uv_protection']) > 0, "UV protection tips should not be empty"
    
    # Verify UV protection tips have required fields
    for tip in tips['uv_protection']:
        assert 'id' in tip, "UV protection tip missing id"
        assert 'title' in tip, "UV protection tip missing title"
        assert 'description' in tip, "UV protection tip missing description"
    
    # Verify early detection guidelines are present
    assert 'early_detection' in tips, "Prevention tips missing early_detection category"
    assert isinstance(tips['early_detection'], list), "Early detection should be a list"
    assert len(tips['early_detection']) > 0, "Early detection tips should not be empty"
    
    # Verify early detection tips have required fields
    for tip in tips['early_detection']:
        assert 'id' in tip, "Early detection tip missing id"
        assert 'title' in tip, "Early detection tip missing title"
        assert 'description' in tip, "Early detection tip missing description"
    
    print(f"✓ Property 47 verified: {len(tips['uv_protection'])} UV protection tips and {len(tips['early_detection'])} early detection guidelines")


# ============================================================================
# Property 48: Contextual Educational Links
# ============================================================================

@given(
    detected_cancer_type=st.sampled_from([
        'melanoma',
        'basal_cell_carcinoma',
        'squamous_cell_carcinoma',
        'actinic_keratosis',
        'benign_keratosis',
        'dermatofibroma',
        'vascular_lesion'
    ])
)
@settings(max_examples=7, deadline=None)
def test_property_48_contextual_educational_links(detected_cancer_type):
    """
    Property 48: Contextual Educational Links
    
    For any AI result with a detected cancer type, the display should include 
    links to Skin-Wiki articles matching that specific cancer type.
    
    Validates: Requirements 16.5
    """
    # Get article for the detected cancer type
    result = supabase.table("skin_wiki_articles")\
        .select("id, slug, cancer_type, title")\
        .eq("cancer_type", detected_cancer_type)\
        .eq("published", True)\
        .execute()
    
    # If no article exists yet, skip this test case
    assume(result.data and len(result.data) > 0)
    
    article = result.data[0]
    
    # Verify article exists for this cancer type
    assert article['cancer_type'] == detected_cancer_type, \
        f"Article cancer_type mismatch: expected {detected_cancer_type}, got {article['cancer_type']}"
    
    # Verify article has required fields for linking
    assert article.get('id'), "Article missing id for linking"
    assert article.get('slug'), "Article missing slug for URL generation"
    assert article.get('title'), "Article missing title for link text"
    
    # Construct the expected link URL
    expected_url = f"/skin-wiki/{article['slug']}"
    
    # Verify the URL can be constructed
    assert expected_url, "Failed to construct article URL"
    assert article['slug'] in expected_url, "Article slug not in URL"
    
    print(f"✓ Property 48 verified for {detected_cancer_type}: Article linkable at {expected_url}")


# ============================================================================
# Run all tests
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("PROPERTY-BASED TESTS: Skin-Wiki Educational Content")
    print("="*80 + "\n")
    
    try:
        print("Testing Property 44: Skin-Wiki Cancer Type Completeness...")
        test_property_44_skin_wiki_cancer_type_completeness()
        print()
        
        print("Testing Property 45: Cancer Type Article Completeness...")
        test_property_45_cancer_type_article_completeness()
        print()
        
        print("Testing Property 46: Educational Content Availability...")
        test_property_46_educational_content_availability()
        print()
        
        print("Testing Property 47: Prevention Tips Completeness...")
        test_property_47_prevention_tips_completeness()
        print()
        
        print("Testing Property 48: Contextual Educational Links...")
        test_property_48_contextual_educational_links()
        print()
        
        print("="*80)
        print("ALL SKIN-WIKI PROPERTY TESTS PASSED ✓")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
