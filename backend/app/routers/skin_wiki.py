"""
Skin-Wiki Public API endpoints
Requirements: 16.1, 16.2, 16.3, 16.4, 16.5
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from app.database import supabase
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/skin-wiki", tags=["Skin-Wiki"])


@router.get("/articles")
async def get_all_articles():
    """
    Get all published Skin-Wiki articles
    Requirements: 16.1
    
    Property 44: Skin-Wiki Cancer Type Completeness
    For any Skin-Wiki section access, the displayed content should include 
    articles for all 7 skin cancer types with images and descriptions.
    
    Returns:
        List of published articles for all 7 cancer types
    """
    try:
        result = supabase.table("skin_wiki_articles")\
            .select("*")\
            .eq("published", True)\
            .order("cancer_type")\
            .execute()
        
        articles = result.data if result.data else []
        
        logger.info(f"Retrieved {len(articles)} published Skin-Wiki articles")
        return articles
        
    except Exception as e:
        logger.error(f"Failed to retrieve articles: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to retrieve articles",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get("/articles/type/{cancer_type}")
async def get_article_by_cancer_type(cancer_type: str):
    """
    Get article by cancer type
    Requirements: 16.1, 16.2
    
    Property 45: Cancer Type Article Completeness
    For any cancer type article, the content should include sections for 
    risk factors, symptoms, and treatment options.
    
    Args:
        cancer_type: One of the 7 cancer types
        
    Returns:
        Article with complete information including risk factors, symptoms, treatments
    """
    try:
        result = supabase.table("skin_wiki_articles")\
            .select("*")\
            .eq("cancer_type", cancer_type)\
            .eq("published", True)\
            .execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "ARTICLE_NOT_FOUND",
                    "message": f"Article for cancer type '{cancer_type}' not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        article = result.data[0]
        
        # Validate completeness (Property 45)
        if not article.get("risk_factors") or not article.get("symptoms") or not article.get("treatments"):
            logger.warning(f"Article {article['id']} is missing required sections")
        
        logger.info(f"Retrieved article for cancer type: {cancer_type}")
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve article: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to retrieve article",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get("/articles/{slug}")
async def get_article_by_slug(slug: str):
    """
    Get article by slug
    Requirements: 16.1, 16.2
    
    Args:
        slug: Article URL slug
        
    Returns:
        Article with complete information
    """
    try:
        result = supabase.table("skin_wiki_articles")\
            .select("*")\
            .eq("slug", slug)\
            .eq("published", True)\
            .execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "ARTICLE_NOT_FOUND",
                    "message": f"Article with slug '{slug}' not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        article = result.data[0]
        logger.info(f"Retrieved article by slug: {slug}")
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve article: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to retrieve article",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get("/self-examination-guide")
async def get_self_examination_guide():
    """
    Get self-examination guide with illustrated body map
    Requirements: 16.3
    
    Property 46: Educational Content Availability
    For any educational content view, self-examination guides with 
    illustrated body maps should be accessible.
    
    Returns:
        Self-examination guide with steps and body map
    """
    try:
        # Return structured self-examination guide
        guide = {
            "title": "Skin Self-Examination Guide",
            "frequency": "Monthly",
            "description": "Regular self-examination helps detect skin changes early. Follow these steps monthly.",
            "steps": [
                {
                    "step_number": 1,
                    "title": "Examine Your Face",
                    "description": "Use a mirror to check your face, ears, neck, chest, and scalp. Use a comb to part your hair.",
                    "tips": [
                        "Look for new moles or changes in existing ones",
                        "Check behind ears and along hairline",
                        "Use a hand mirror for hard-to-see areas"
                    ]
                },
                {
                    "step_number": 2,
                    "title": "Check Your Arms and Hands",
                    "description": "Examine both sides of your arms, hands, between fingers, and under fingernails.",
                    "tips": [
                        "Raise arms to check underarms",
                        "Look at palms and backs of hands",
                        "Check between all fingers"
                    ]
                },
                {
                    "step_number": 3,
                    "title": "Examine Your Torso",
                    "description": "Check your chest, abdomen, sides, and back using mirrors.",
                    "tips": [
                        "Use a full-length mirror",
                        "Use a hand mirror to check your back",
                        "Check under breasts and skin folds"
                    ]
                },
                {
                    "step_number": 4,
                    "title": "Check Your Legs and Feet",
                    "description": "Sit down and examine your legs, feet, between toes, and under toenails.",
                    "tips": [
                        "Check front and back of legs",
                        "Examine soles of feet",
                        "Look between all toes"
                    ]
                },
                {
                    "step_number": 5,
                    "title": "Use the ABCDE Rule",
                    "description": "When examining moles, remember ABCDE: Asymmetry, Border, Color, Diameter, Evolving.",
                    "tips": [
                        "A: One half doesn't match the other",
                        "B: Irregular, scalloped, or poorly defined borders",
                        "C: Varied colors (brown, black, tan, red, white, blue)",
                        "D: Diameter larger than 6mm (pencil eraser)",
                        "E: Changing in size, shape, or color"
                    ]
                }
            ],
            "body_map": [
                {
                    "id": "head_neck",
                    "name": "Head and Neck",
                    "description": "Face, ears, scalp, neck",
                    "common_lesions": ["Basal cell carcinoma", "Squamous cell carcinoma", "Melanoma"]
                },
                {
                    "id": "chest_abdomen",
                    "name": "Chest and Abdomen",
                    "description": "Front torso, sides",
                    "common_lesions": ["Melanoma", "Benign keratosis", "Vascular lesion"]
                },
                {
                    "id": "back",
                    "name": "Back",
                    "description": "Upper and lower back",
                    "common_lesions": ["Melanoma", "Dermatofibroma"]
                },
                {
                    "id": "arms",
                    "name": "Arms",
                    "description": "Upper arms, forearms, hands",
                    "common_lesions": ["Actinic keratosis", "Basal cell carcinoma"]
                },
                {
                    "id": "legs",
                    "name": "Legs",
                    "description": "Thighs, calves, feet",
                    "common_lesions": ["Melanoma", "Vascular lesion"]
                }
            ]
        }
        
        logger.info("Retrieved self-examination guide")
        return guide
        
    except Exception as e:
        logger.error(f"Failed to retrieve self-examination guide: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to retrieve self-examination guide",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get("/prevention-tips")
async def get_prevention_tips():
    """
    Get prevention tips including UV protection and early detection
    Requirements: 16.4
    
    Property 47: Prevention Tips Completeness
    For any prevention tips display, the content should include UV protection 
    recommendations and early detection guidelines.
    
    Returns:
        Prevention tips categorized by type
    """
    try:
        tips = {
            "uv_protection": [
                {
                    "id": "uv_1",
                    "title": "Use Broad-Spectrum Sunscreen",
                    "description": "Apply SPF 30+ sunscreen daily, even on cloudy days. Reapply every 2 hours when outdoors.",
                    "icon": "sun"
                },
                {
                    "id": "uv_2",
                    "title": "Seek Shade",
                    "description": "Avoid direct sun exposure between 10 AM and 4 PM when UV rays are strongest.",
                    "icon": "umbrella"
                },
                {
                    "id": "uv_3",
                    "title": "Wear Protective Clothing",
                    "description": "Cover up with long sleeves, pants, wide-brimmed hats, and UV-blocking sunglasses.",
                    "icon": "shirt"
                },
                {
                    "id": "uv_4",
                    "title": "Avoid Tanning Beds",
                    "description": "Tanning beds emit harmful UV radiation that increases skin cancer risk.",
                    "icon": "ban"
                }
            ],
            "early_detection": [
                {
                    "id": "ed_1",
                    "title": "Monthly Self-Examinations",
                    "description": "Check your skin monthly for new or changing moles, spots, or lesions.",
                    "icon": "search"
                },
                {
                    "id": "ed_2",
                    "title": "Annual Dermatologist Visits",
                    "description": "Get a professional skin exam yearly, or more often if you're at high risk.",
                    "icon": "calendar"
                },
                {
                    "id": "ed_3",
                    "title": "Know Your Risk Factors",
                    "description": "Be aware of family history, fair skin, many moles, and history of sunburns.",
                    "icon": "info"
                },
                {
                    "id": "ed_4",
                    "title": "Document Changes",
                    "description": "Take photos of moles and lesions to track changes over time.",
                    "icon": "camera"
                }
            ],
            "lifestyle": [
                {
                    "id": "ls_1",
                    "title": "Stay Hydrated",
                    "description": "Drink plenty of water to keep your skin healthy and resilient.",
                    "icon": "water"
                },
                {
                    "id": "ls_2",
                    "title": "Eat Antioxidant-Rich Foods",
                    "description": "Include fruits, vegetables, and foods high in vitamins C and E.",
                    "icon": "apple"
                },
                {
                    "id": "ls_3",
                    "title": "Don't Smoke",
                    "description": "Smoking damages skin and increases risk of squamous cell carcinoma.",
                    "icon": "no-smoking"
                },
                {
                    "id": "ls_4",
                    "title": "Manage Stress",
                    "description": "Chronic stress can weaken immune system and affect skin health.",
                    "icon": "heart"
                }
            ]
        }
        
        logger.info("Retrieved prevention tips")
        return tips
        
    except Exception as e:
        logger.error(f"Failed to retrieve prevention tips: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to retrieve prevention tips",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )
