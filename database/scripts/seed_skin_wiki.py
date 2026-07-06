"""
Seed Skin-Wiki Articles
Creates sample articles for all 7 cancer types
"""

import os
import sys
from datetime import datetime
import uuid

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.database import supabase


def seed_skin_wiki_articles():
    """Seed Skin-Wiki articles for all 7 cancer types"""
    
    articles = [
        {
            "id": str(uuid.uuid4()),
            "title": "Melanoma: The Most Serious Skin Cancer",
            "slug": "melanoma",
            "cancer_type": "melanoma",
            "summary": "Melanoma is the most dangerous form of skin cancer, developing in melanocytes (pigment-producing cells). Early detection is crucial for successful treatment.",
            "content": "<p>Melanoma is a type of skin cancer that develops in melanocytes, the cells that produce melanin (skin pigment). While less common than other skin cancers, melanoma is more dangerous because it can spread to other parts of the body if not caught early.</p>",
            "image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800",
            "risk_factors": [
                "Excessive UV exposure from sun or tanning beds",
                "Fair skin, light hair, and light eyes",
                "History of sunburns, especially in childhood",
                "Many moles or atypical moles",
                "Family history of melanoma",
                "Weakened immune system"
            ],
            "symptoms": [
                "New mole or change in existing mole",
                "Asymmetrical shape",
                "Irregular or poorly defined borders",
                "Multiple colors (brown, black, tan, red, white, blue)",
                "Diameter larger than 6mm (pencil eraser)",
                "Evolving size, shape, or color"
            ],
            "treatments": [
                "Surgical excision (removal of melanoma and surrounding tissue)",
                "Immunotherapy to boost immune system",
                "Targeted therapy for specific genetic mutations",
                "Radiation therapy for advanced cases",
                "Chemotherapy for metastatic melanoma"
            ],
            "prevention_tips": [
                "Use broad-spectrum SPF 30+ sunscreen daily",
                "Avoid tanning beds",
                "Perform monthly self-examinations",
                "Get annual skin checks from dermatologist"
            ],
            "published": True,
            "version": 1,
            "created_by": "system",
            "updated_by": "system",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Basal Cell Carcinoma: The Most Common Skin Cancer",
            "slug": "basal-cell-carcinoma",
            "cancer_type": "basal_cell_carcinoma",
            "summary": "Basal cell carcinoma is the most common form of skin cancer, developing in the basal cells of the skin. It rarely spreads but should be treated promptly.",
            "content": "<p>Basal cell carcinoma (BCC) develops in the basal cells, which are found in the deepest layer of the epidermis. While BCC rarely metastasizes, it can cause significant local damage if left untreated.</p>",
            "image_url": "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=800",
            "risk_factors": [
                "Chronic sun exposure",
                "Fair skin that burns easily",
                "Age over 50",
                "Male gender",
                "History of radiation therapy",
                "Exposure to arsenic"
            ],
            "symptoms": [
                "Pearly or waxy bump",
                "Flat, flesh-colored or brown scar-like lesion",
                "Bleeding or scabbing sore that heals and returns",
                "Pink growth with raised edges",
                "Open sore that doesn't heal"
            ],
            "treatments": [
                "Mohs surgery (layer-by-layer removal)",
                "Excisional surgery",
                "Curettage and electrodesiccation",
                "Cryotherapy (freezing)",
                "Topical medications for superficial BCCs",
                "Radiation therapy"
            ],
            "prevention_tips": [
                "Limit sun exposure during peak hours",
                "Wear protective clothing and hats",
                "Apply sunscreen regularly",
                "Avoid tanning beds"
            ],
            "published": True,
            "version": 1,
            "created_by": "system",
            "updated_by": "system",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Squamous Cell Carcinoma: Second Most Common Skin Cancer",
            "slug": "squamous-cell-carcinoma",
            "cancer_type": "squamous_cell_carcinoma",
            "summary": "Squamous cell carcinoma develops in the squamous cells of the skin. It can spread if not treated, making early detection important.",
            "content": "<p>Squamous cell carcinoma (SCC) is the second most common type of skin cancer, developing in the squamous cells that make up the middle and outer layers of the skin.</p>",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800",
            "risk_factors": [
                "Cumulative sun exposure over lifetime",
                "Fair skin",
                "History of precancerous lesions",
                "Weakened immune system",
                "HPV infection",
                "Smoking"
            ],
            "symptoms": [
                "Firm, red nodule",
                "Flat lesion with scaly, crusted surface",
                "New sore or raised area on old scar",
                "Rough, scaly patch on lip",
                "Red, raised patch in mouth",
                "Wart-like growth"
            ],
            "treatments": [
                "Surgical excision",
                "Mohs surgery for high-risk areas",
                "Curettage and electrodesiccation",
                "Cryotherapy",
                "Radiation therapy",
                "Topical chemotherapy for superficial lesions"
            ],
            "prevention_tips": [
                "Protect skin from UV radiation",
                "Treat precancerous lesions promptly",
                "Regular skin examinations",
                "Quit smoking"
            ],
            "published": True,
            "version": 1,
            "created_by": "system",
            "updated_by": "system",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Actinic Keratosis: Precancerous Skin Lesion",
            "slug": "actinic-keratosis",
            "cancer_type": "actinic_keratosis",
            "summary": "Actinic keratosis is a precancerous skin condition caused by sun damage. Early treatment can prevent progression to skin cancer.",
            "content": "<p>Actinic keratosis (AK), also called solar keratosis, is a rough, scaly patch on the skin that develops from years of sun exposure. It's considered precancerous because it can develop into squamous cell carcinoma.</p>",
            "image_url": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=800",
            "risk_factors": [
                "Frequent or intense sun exposure",
                "Fair skin, blonde or red hair, blue or light-colored eyes",
                "Age over 40",
                "Living in sunny climates",
                "History of sunburns",
                "Weakened immune system"
            ],
            "symptoms": [
                "Rough, dry, or scaly patch of skin",
                "Flat to slightly raised patch",
                "Color variations (pink, red, or brown)",
                "Itching or burning sensation",
                "Crusting or bleeding",
                "Size typically less than 1 inch"
            ],
            "treatments": [
                "Cryotherapy (freezing with liquid nitrogen)",
                "Topical medications (5-fluorouracil, imiquimod)",
                "Photodynamic therapy",
                "Chemical peels",
                "Laser therapy",
                "Curettage"
            ],
            "prevention_tips": [
                "Use sunscreen daily",
                "Seek shade during peak sun hours",
                "Wear protective clothing",
                "Regular skin checks"
            ],
            "published": True,
            "version": 1,
            "created_by": "system",
            "updated_by": "system",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Benign Keratosis: Non-Cancerous Skin Growth",
            "slug": "benign-keratosis",
            "cancer_type": "benign_keratosis",
            "summary": "Benign keratosis, including seborrheic keratosis, is a non-cancerous skin growth that doesn't require treatment unless bothersome.",
            "content": "<p>Benign keratosis refers to non-cancerous skin growths, most commonly seborrheic keratosis. These growths are harmless and don't turn into cancer, though they may be removed for cosmetic reasons.</p>",
            "image_url": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=800",
            "risk_factors": [
                "Age (more common after 50)",
                "Family history",
                "Sun exposure (though not directly caused by sun)",
                "Genetics"
            ],
            "symptoms": [
                "Waxy, stuck-on appearance",
                "Raised, slightly elevated growth",
                "Color ranges from light tan to black",
                "Round or oval shape",
                "Rough or smooth texture",
                "May appear in clusters"
            ],
            "treatments": [
                "No treatment necessary (benign)",
                "Cryotherapy for cosmetic removal",
                "Curettage",
                "Electrocautery",
                "Laser therapy",
                "Shave excision"
            ],
            "prevention_tips": [
                "No specific prevention (age-related)",
                "Regular skin monitoring",
                "Consult dermatologist if changes occur",
                "Sun protection for overall skin health"
            ],
            "published": True,
            "version": 1,
            "created_by": "system",
            "updated_by": "system",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Dermatofibroma: Benign Skin Nodule",
            "slug": "dermatofibroma",
            "cancer_type": "dermatofibroma",
            "summary": "Dermatofibroma is a common benign skin nodule that typically appears on the legs. It's harmless and usually doesn't require treatment.",
            "content": "<p>Dermatofibroma is a benign (non-cancerous) skin growth that commonly appears on the lower legs. It's composed of fibrous tissue and is completely harmless, though it may be removed if bothersome.</p>",
            "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800",
            "risk_factors": [
                "Minor skin trauma or insect bites",
                "More common in women",
                "Age 20-40 years",
                "Unknown exact cause"
            ],
            "symptoms": [
                "Firm, raised bump",
                "Brown, red, or pink color",
                "Typically 0.5-1 cm in diameter",
                "Dimples when pinched",
                "Usually painless",
                "Most common on legs"
            ],
            "treatments": [
                "No treatment necessary (benign)",
                "Surgical excision if bothersome",
                "Cryotherapy",
                "Laser therapy",
                "Observation (may fade over time)"
            ],
            "prevention_tips": [
                "No specific prevention",
                "Protect skin from trauma",
                "Monitor for changes",
                "Consult dermatologist if concerned"
            ],
            "published": True,
            "version": 1,
            "created_by": "system",
            "updated_by": "system",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Vascular Lesion: Blood Vessel Skin Abnormality",
            "slug": "vascular-lesion",
            "cancer_type": "vascular_lesion",
            "summary": "Vascular lesions are abnormalities of blood vessels in the skin, including hemangiomas and port-wine stains. Most are benign.",
            "content": "<p>Vascular lesions are abnormalities of blood vessels in or under the skin. They include various types such as hemangiomas, port-wine stains, and cherry angiomas. Most are benign and harmless.</p>",
            "image_url": "https://images.unsplash.com/photo-1582719471137-c3967ffb1c42?w=800",
            "risk_factors": [
                "Congenital (present at birth)",
                "Age (cherry angiomas increase with age)",
                "Genetics",
                "Hormonal changes",
                "Sun exposure (for some types)"
            ],
            "symptoms": [
                "Red, purple, or blue discoloration",
                "Flat or raised appearance",
                "May blanch when pressed",
                "Various sizes and shapes",
                "Usually painless",
                "May grow or change over time"
            ],
            "treatments": [
                "Observation (many require no treatment)",
                "Laser therapy",
                "Sclerotherapy",
                "Surgical excision",
                "Cryotherapy",
                "Topical medications (for some types)"
            ],
            "prevention_tips": [
                "No specific prevention for congenital types",
                "Sun protection",
                "Regular monitoring",
                "Consult dermatologist for changes"
            ],
            "published": True,
            "version": 1,
            "created_by": "system",
            "updated_by": "system",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    print("Seeding Skin-Wiki articles...")
    
    for article in articles:
        try:
            # Check if article already exists
            existing = supabase.table("skin_wiki_articles")\
                .select("id")\
                .eq("cancer_type", article["cancer_type"])\
                .execute()
            
            if existing.data and len(existing.data) > 0:
                print(f"  ✓ Article for {article['cancer_type']} already exists, skipping...")
                continue
            
            # Insert article
            result = supabase.table("skin_wiki_articles").insert(article).execute()
            
            if result.data:
                print(f"  ✓ Created article: {article['title']}")
            else:
                print(f"  ✗ Failed to create article: {article['title']}")
                
        except Exception as e:
            print(f"  ✗ Error creating article {article['title']}: {str(e)}")
    
    print("\nSkin-Wiki seeding complete!")


if __name__ == "__main__":
    seed_skin_wiki_articles()
