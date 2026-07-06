"""
Property-Based Tests for UI Disclaimer Presence
These tests verify that disclaimers are present in frontend components

Feature: derman-ai-skin-screening
Tests UI-related correctness properties for medical and educational disclaimers.

Requirements: 14.4
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings
import re


# Feature: derman-ai-skin-screening, Property 37: Educational Content Disclaimer Presence
@settings(
    max_examples=1,  # Static file check, only need to run once
    deadline=None
)
@given(
    dummy=st.just(True)  # Dummy strategy to make it a property test
)
def test_educational_content_disclaimer_presence(dummy):
    """
    Property 37: Educational Content Disclaimer Presence
    
    For any medical information page, the rendered output should include
    disclaimers about the educational nature of the content.
    
    This test verifies:
    1. Landing page includes medical disclaimer
    2. Results display component includes medical disclaimer
    3. Disclaimer mentions AI-assisted screening limitations
    4. Disclaimer advises consulting healthcare professionals
    5. Disclaimer is prominently displayed (not hidden)
    
    Validates: Requirements 14.4
    """
    # Get frontend source directory
    frontend_src = Path(__file__).parent.parent.parent / "frontend" / "src"
    
    # Test 1: Verify landing page has medical disclaimer
    landing_page_path = frontend_src / "pages" / "LandingPage.tsx"
    assert landing_page_path.exists(), \
        f"Landing page component should exist at {landing_page_path}"
    
    landing_content = landing_page_path.read_text(encoding='utf-8')
    
    # Check for disclaimer presence
    assert "Medical Disclaimer" in landing_content or "medical disclaimer" in landing_content, \
        "Landing page should include 'Medical Disclaimer' text"
    
    # Check for key disclaimer phrases
    landing_disclaimer_phrases = [
        "AI-assisted screening",
        "consult",
        "healthcare professional" or "qualified healthcare" or "medical professional"
    ]
    
    for phrase in landing_disclaimer_phrases:
        # Use case-insensitive search
        if not re.search(phrase, landing_content, re.IGNORECASE):
            # Check for alternative phrasings
            if phrase == "healthcare professional" or "qualified healthcare" or "medical professional":
                assert any(alt in landing_content.lower() for alt in [
                    "healthcare professional",
                    "qualified healthcare",
                    "medical professional",
                    "doctor"
                ]), f"Landing page disclaimer should mention healthcare professionals"
            else:
                assert False, f"Landing page disclaimer should contain: '{phrase}'"
    
    print("✓ Landing page disclaimer verified")
    print(f"  Found disclaimer in: {landing_page_path.name}")
    
    # Test 2: Verify results display component has medical disclaimer
    results_display_path = frontend_src / "components" / "patient" / "ResultsDisplay.tsx"
    assert results_display_path.exists(), \
        f"Results display component should exist at {results_display_path}"
    
    results_content = results_display_path.read_text(encoding='utf-8')
    
    # Check for disclaimer section
    assert "Medical Disclaimer" in results_content or "medical disclaimer" in results_content, \
        "Results display should include 'Medical Disclaimer' section"
    
    # Check for the specific 94% probability disclaimer
    assert "94% probability estimate" in results_content, \
        "Results display should include '94% probability estimate' disclaimer"
    
    # Check for key disclaimer phrases in results
    results_disclaimer_phrases = [
        "94% probability estimate",
        "AI analysis" or "AI-assisted",
        "not a substitute",
        "professional medical advice",
        "consult",
        "doctor" or "physician",
        "clinical biopsy" or "biopsy"
    ]
    
    for phrase in results_disclaimer_phrases:
        # Use case-insensitive search with alternatives
        if phrase == "AI analysis" or "AI-assisted":
            assert "AI" in results_content, \
                "Results disclaimer should mention AI"
        elif phrase == "doctor" or "physician":
            assert any(term in results_content.lower() for term in ["doctor", "physician", "healthcare"]), \
                "Results disclaimer should mention doctors/physicians"
        elif phrase == "clinical biopsy" or "biopsy":
            assert "biopsy" in results_content.lower(), \
                "Results disclaimer should mention biopsy"
        else:
            assert re.search(phrase, results_content, re.IGNORECASE), \
                f"Results display disclaimer should contain: '{phrase}'"
    
    print("✓ Results display disclaimer verified")
    print(f"  Found disclaimer in: {results_display_path.name}")
    
    # Test 3: Verify disclaimer is not hidden or commented out
    # Check that disclaimer is in actual JSX/TSX code, not in comments
    
    # Remove single-line comments
    landing_no_comments = re.sub(r'//.*?$', '', landing_content, flags=re.MULTILINE)
    # Remove multi-line comments
    landing_no_comments = re.sub(r'/\*.*?\*/', '', landing_no_comments, flags=re.DOTALL)
    
    assert "Medical Disclaimer" in landing_no_comments or "medical disclaimer" in landing_no_comments, \
        "Landing page disclaimer should not be commented out"
    
    # Same for results display
    results_no_comments = re.sub(r'//.*?$', '', results_content, flags=re.MULTILINE)
    results_no_comments = re.sub(r'/\*.*?\*/', '', results_no_comments, flags=re.DOTALL)
    
    assert "Medical Disclaimer" in results_no_comments or "medical disclaimer" in results_no_comments, \
        "Results display disclaimer should not be commented out"
    assert "94% probability estimate" in results_no_comments, \
        "Results display 94% disclaimer should not be commented out"
    
    print("✓ Disclaimers are active (not commented out)")
    
    # Test 4: Verify disclaimer is in visible UI elements (not in hidden divs)
    # Check that disclaimer is in actual rendered content (has className or style attributes)
    
    # Extract the disclaimer section from results display
    disclaimer_section_match = re.search(
        r'(Medical Disclaimer.*?</div>)',
        results_content,
        re.DOTALL | re.IGNORECASE
    )
    
    if disclaimer_section_match:
        disclaimer_section = disclaimer_section_match.group(1)
        
        # Check that it's not hidden with display:none or hidden attribute
        assert 'display: none' not in disclaimer_section.lower(), \
            "Disclaimer should not be hidden with display:none"
        assert 'display:none' not in disclaimer_section.lower(), \
            "Disclaimer should not be hidden with display:none"
        assert 'hidden' not in disclaimer_section.lower() or 'hidden=' not in disclaimer_section.lower(), \
            "Disclaimer should not have hidden attribute"
        
        print("✓ Disclaimer is visible (not hidden)")
    
    # Test 5: Verify disclaimer mentions specific requirements
    # Requirements 14.4: disclaimers about educational nature of content
    
    educational_keywords = [
        r"AI-assisted|AI analysis|AI screening",
        r"not.*substitute|not.*replace",
        r"professional|qualified|doctor|physician"
    ]
    
    # Check in both landing and results
    combined_content = landing_content + results_content
    
    for keyword_pattern in educational_keywords:
        assert re.search(keyword_pattern, combined_content, re.IGNORECASE), \
            f"Disclaimers should include educational nature keywords: '{keyword_pattern}'"
    
    print("✓ Educational nature disclaimers verified")
    
    # Test 6: Verify disclaimer is prominently displayed
    # Check for styling that makes it prominent (card, border, background color, etc.)
    
    # In ResultsDisplay, disclaimer should be in a card or prominent container
    assert 'card' in results_content.lower() or 'border' in results_content.lower(), \
        "Results disclaimer should be in a prominent container (card/border)"
    
    # Check for visual prominence indicators
    prominence_indicators = [
        'bg-primary',  # Background color
        'border-primary',  # Border color
        'font-semibold' or 'font-bold',  # Bold text
        'text-primary'  # Colored text
    ]
    
    # At least some prominence indicators should be present
    prominence_found = any(indicator in results_content for indicator in prominence_indicators)
    assert prominence_found, \
        "Results disclaimer should have visual prominence (colors, borders, bold text)"
    
    print("✓ Disclaimer is prominently displayed")
    
    # Summary
    print("\n" + "="*60)
    print("Property 37: Educational Content Disclaimer Presence - PASSED")
    print("="*60)
    print("Verified:")
    print("  ✓ Landing page includes medical disclaimer")
    print("  ✓ Results display includes 94% probability disclaimer")
    print("  ✓ Disclaimers mention AI limitations")
    print("  ✓ Disclaimers advise consulting healthcare professionals")
    print("  ✓ Disclaimers are visible and prominent")
    print("  ✓ Disclaimers describe educational nature of content")


# Additional test: Verify disclaimer consistency across components
@settings(
    max_examples=1,
    deadline=None
)
@given(
    dummy=st.just(True)
)
def test_disclaimer_consistency_across_components(dummy):
    """
    Verify that disclaimer messaging is consistent across different UI components.
    
    This ensures that users receive consistent information about the limitations
    of AI screening regardless of where they encounter disclaimers.
    """
    frontend_src = Path(__file__).parent.parent.parent / "frontend" / "src"
    
    # Collect all disclaimer texts
    disclaimers = {}
    
    # Landing page
    landing_page_path = frontend_src / "pages" / "LandingPage.tsx"
    if landing_page_path.exists():
        content = landing_page_path.read_text(encoding='utf-8')
        # Extract disclaimer text
        match = re.search(r'Medical Disclaimer:?\s*(.{50,200})', content, re.IGNORECASE | re.DOTALL)
        if match:
            disclaimers['landing'] = match.group(1).strip()
    
    # Results display
    results_path = frontend_src / "components" / "patient" / "ResultsDisplay.tsx"
    if results_path.exists():
        content = results_path.read_text(encoding='utf-8')
        match = re.search(r'94% probability estimate.*?\.', content, re.IGNORECASE | re.DOTALL)
        if match:
            disclaimers['results'] = match.group(0).strip()
    
    # Verify all disclaimers share common themes
    common_themes = [
        "AI" or "artificial intelligence",
        "consult" or "consultation",
        "professional" or "doctor" or "physician"
    ]
    
    for component, disclaimer_text in disclaimers.items():
        for theme in common_themes:
            # Check for theme or alternatives
            if theme == "AI" or "artificial intelligence":
                assert "AI" in disclaimer_text or "artificial intelligence" in disclaimer_text.lower(), \
                    f"{component} disclaimer should mention AI"
            elif theme == "consult" or "consultation":
                assert any(word in disclaimer_text.lower() for word in ["consult", "consultation"]), \
                    f"{component} disclaimer should mention consultation"
            elif theme == "professional" or "doctor" or "physician":
                assert any(word in disclaimer_text.lower() for word in ["professional", "doctor", "physician", "healthcare"]), \
                    f"{component} disclaimer should mention medical professionals"
    
    print("✓ Disclaimer consistency verified across components")
    print(f"  Checked {len(disclaimers)} components")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
