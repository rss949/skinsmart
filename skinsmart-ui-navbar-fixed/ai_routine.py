import json
import os
import re
import time
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ALL_BRANDS = [
    "Mamaearth",
    "Foxtale",
    "Dot & Key",
    "The Derma Co",
    "Minimalist",
    "Cetaphil",
    "Himalaya",
    "Plix",
]


PRODUCT_CATALOG = {
    "Mamaearth": {
        "cleanser": {
            "product": "Tea Tree Face Wash",
            "price_inr": 249,
            "image_url": "https://images.mamaearth.in/catalog/product/t/e/tea-tree-facewash_1.jpg",
            "buy_url": "https://mamaearth.in/product/tea-tree-face-wash"
        },
        "cleanser_oily": {
            "product": "Tea Tree Oil Control Face Wash",
            "price_inr": 349,
            "image_url": "https://images.mamaearth.in/catalog/product/1/_/1_229.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/tea-tree-oil-control-face-wash-with-tea-tree-neem-for-normal-to-oily-skin-150-ml"
        },
        "cleanser_dry": {
            "product": "Chia Calming Face Cleanser",
            "price_inr": 349,
            "image_url": "https://images.mamaearth.in/catalog/product/1/_/1_132.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/mamaearth-chia-calming-face-cleanser-with-chia-seed-ceramides-for-dry-sensitive-skin-180-ml"
        },
        "cleanser_combination": {
            "product": "Chia Oil-Free Face Wash",
            "price_inr": 299,
            "image_url": "https://images.mamaearth.in/catalog/product/1/_/1_129.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/mamaearth-chia-oil-free-face-wash-with-chia-seed-ceramides-for-normal-to-oily-skin-100-ml"
        },
        "cleanser_normal": {
            "product": "Rice Face Wash",
            "price_inr": 299,
            "image_url": "https://images.mamaearth.in/catalog/product/r/i/rice_fw_150ml.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/rice-face-wash-with-rice-water-niacinamide-for-glass-skin-150-ml"
        },
        "moisturizer_oily": {
            "product": "Oil-Free Face Moisturizer",
            "price_inr": 299,
            "image_url": "https://images.mamaearth.in/catalog/product/o/i/oil-free-face-moisturizer_1.jpg",
            "buy_url": "https://mamaearth.in/product/oil-free-face-moisturizer-with-apple-cider-vinegar-for-acne-prone-skin"
        },
        "moisturizer_dry": {
            "product": "Vitamin C Oil-Free Moisturizer",
            "price_inr": 399,
            "image_url": "https://images.mamaearth.in/catalog/product/v/i/vitamin-c-moisturizer_1.jpg",
            "buy_url": "https://mamaearth.in/product/vitamin-c-ultra-light-gel-oil-free-moisturizer-with-vitamin-c-aloe-vera-water-for-glowing-hydration-200-ml"
        },
        "sunscreen": {
            "product": "Ultra Light Indian Sunscreen SPF 50",
            "price_inr": 499,
            "image_url": "https://images.mamaearth.in/catalog/product/u/l/ultra-light-indian-sunscreen_1.jpg",
            "buy_url": "https://mamaearth.in/product/ultra-light-indian-sunscreen"
        },
        "acne_treatment": {
            "product": "Tea Tree Spot Gel",
            "price_inr": 349,
            "image_url": "https://images.mamaearth.in/catalog/product/t/e/tea-tree-spot-gel_1.jpg",
            "buy_url": "https://mamaearth.in/product/tea-tree-spot-gel-face-cream-with-tea-tree-salicylic-acid-for-acne-pimples-15-g"
        },
        "dark_spot_serum": {
            "product": "Skin Correct Face Serum",
            "price_inr": 599,
            "image_url": "https://images.mamaearth.in/catalog/product/s/k/skin-correct-face-serum_1.jpg",
            "buy_url": "https://mamaearth.in/product/skin-correct-face-serum-with-niacinamide-and-ginger-extract-for-acne-marks-scars-30-ml"
        },
        "eye_cream": {
            "product": "Bye Bye Dark Circles Eye Cream",
            "price_inr": 399,
            "image_url": "https://images.mamaearth.in/catalog/product/b/y/bye-bye-dark-circles-eye-cream_1.jpg",
            "buy_url": "https://mamaearth.in/product/bye-bye-dark-circles-eye-cream-with-cucumber-peptides-for-dark-circles-20ml"
        },
        "hydrating_serum": {
            "product": "Rice Water Hydra Glow Serum",
            "price_inr": 499,
            "image_url": "https://images.mamaearth.in/catalog/product/r/i/rice-water-hydra-glow-serum_1.jpg",
            "buy_url": "https://mamaearth.in/product/skin-plump-serum-for-face-glow-with-hyaluronic-acid-rosehip-oil-for-ageless-skin-30ml"
        },
        "serum_oily": {
            "product": "Leaves of Clarity Essence Serum",
            "price_inr": 599,
            "image_url": "https://images.mamaearth.in/catalog/product/l/e/leaves-of-clarity-essence-serum_2_1_1.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/leaves-of-clarity-essence-serum-with-neem-salicylic-acid-for-clear-skin-30-ml"
        },
        "serum_dry": {
            "product": "Aqua Glow Face Serum",
            "price_inr": 499,
            "image_url": "https://images.mamaearth.in/catalog/product/a/q/aqua-glow-face-serum-1.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/aqua-glow-face-serum-with-himalayan-thermal-water-hyaluronic-acid-30-ml"
        },
        "serum_combination": {
            "product": "Skin Correct Face Serum",
            "price_inr": 599,
            "image_url": "https://images.mamaearth.in/catalog/product/s/k/skin-correct-face-serum-with-ingredient_1.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/skin-correct-face-serum-with-niacinamide-and-ginger-extract-for-acne-marks-scars-30-ml"
        },
        "serum_normal": {
            "product": "Rosehip Face Serum",
            "price_inr": 599,
            "image_url": "https://images.mamaearth.in/catalog/product/r/o/rosehip-serum.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/rosehip-face-serum-for-glowing-skin-with-rosehip-gotu-kola-for-glowing-skin-30-ml"
        },
        "moisturizer_combination": {
            "product": "Chia Oil-Free Moisturizer",
            "price_inr": 349,
            "image_url": "https://images.mamaearth.in/catalog/product/1/_/1_130.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/mamaearth-chia-oil-free-moisturizer-with-chia-seed-ceramides-for-healthy-skin-barrier-80g"
        },
        "moisturizer_normal": {
            "product": "Rice Dewy Bright Light Gel Moisturizer",
            "price_inr": 349,
            "image_url": "https://images.mamaearth.in/catalog/product/1/_/1_113.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/rice-dewy-bright-light-gel-moisturizer-with-rice-niacinamide-for-glass-skin-glow-200-g"
        },
        "sunscreen_oily": {
            "product": "Chia Oil-Free Sunscreen SPF 50",
            "price_inr": 399,
            "image_url": "https://images.mamaearth.in/catalog/product/1/_/1_189.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/chia-oil-free-sunscreen-with-chia-seed-ceramides-for-healthy-skin-barrier-sun-protection-50g"
        },
        "sunscreen_dry": {
            "product": "Chia Calming Sunscreen",
            "price_inr": 399,
            "image_url": "https://images.mamaearth.in/catalog/product/1/_/1_133.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/chia-calming-sunscreen-with-chia-seed-ceramides-for-healthy-skin-barrier-sun-protection-50-g"
        },
        "sunscreen_combination": {
            "product": "Rice Water Dewy Sunscreen SPF 50",
            "price_inr": 449,
            "image_url": "https://images.mamaearth.in/catalog/product/p/r/product_with_ingridents_1.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/mamaearth-rice-water-dewy-sunscreen-with-spf-50-pa-80g"
        },
        "sunscreen_normal": {
            "product": "Vitamin C Daily Glow Sunscreen",
            "price_inr": 449,
            "image_url": "https://images.mamaearth.in/catalog/product/1/_/1_191_1.jpg?format=auto&height=600",
            "buy_url": "https://mamaearth.in/product/vitamin-c-daily-glow-sunscreen-with-vitamin-c-turmeric-for-sun-protection-glow-50-g-1"
        }
    },
    "Foxtale": {
        "cleanser": {
            "product": "Daily Duet Cleanser",
            "price_inr": 349,
            "image_url": "https://foxtale.in/cdn/shop/files/1_15_3055917f-fc4a-466a-a5e7-c0148f4db8ec.jpg?v=1743841339",
            "buy_url": "https://www.indiangoods.shop/products/foxtale-the-daily-duet-gentle-cleanser-hydrating-face-wash-for-pore-cleansing-dirt-control-makeup-remover-for-all-skin-types"
        },
        "cleanser_oily": {
            "product": "True Clarity Oil & Acne Control Face Wash",
            "price_inr": 349,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/FXN-OAFW100_201.png?v=1775741011",
            "buy_url": "https://foxtale.in/products/true-clarity-oil-acne-control-face-wash"
        },
        "cleanser_dry": {
            "product": "The Daily Duet Cleanser",
            "price_inr": 349,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/HYDRATING_CLEANSER.png?v=1775478668",
            "buy_url": "https://foxtale.in/products/the-daily-duet-cleanser"
        },
        "cleanser_combination": {
            "product": "Acne Control Cleanser",
            "price_inr": 349,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/ACNE_CONTROL.png?v=1775479385",
            "buy_url": "https://foxtale.in/products/acne-control-cleanser"
        },
        "cleanser_normal": {
            "product": "Super Glow Face Wash",
            "price_inr": 349,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/FXN-SGFW100_1-x.jpg?v=1775651776",
            "buy_url": "https://foxtale.in/products/super-glow-face-wash"
        },
        "moisturizer_oily": {
            "product": "Oil-Free Moisturizer",
            "price_inr": 395,
            "image_url": "https://foxtale.in/cdn/shop/files/1_14.jpg?v=1743842225",
            "buy_url": "https://www.indiangoods.shop/products/foxtale-oil-free-gel-moisturizer-with-hyaluronic-acid-niacinamide-boosts-hydration-brightens-skin-soothes-acne"
        },
        "moisturizer_dry": {
            "product": "Ceramide Supercream Moisturizer",
            "price_inr": 445,
            "image_url": "https://foxtale.in/cdn/shop/files/Ceramidesupercream.jpg?v=1743841546",
            "buy_url": "https://www.indiangoods.shop/products/foxtale-hydrating-ceramide-supercream-moisturizer-with-hyaluronic-acid"
        },
        "sunscreen": {
            "product": "SPF 50 Matte Finish Sunscreen",
            "price_inr": 449,
            "image_url": "https://foxtale.in/cdn/shop/files/1_12_1f17fba8-9ed4-439e-b3f8-03f3fdbf7f0a.jpg?v=1744784849",
            "buy_url": "https://www.indiangoods.shop/products/foxtale-niacinamide-mattifying-sunscreen-spf-70-pa-prevents-tanning-uva-uvb-protection"
        },
        "acne_treatment": {
            "product": "2% Salicylic Acid Serum",
            "price_inr": 545,
            "image_url": "https://foxtale.in/cdn/shop/files/2salicylicacidsserum.jpg?v=1743841428",
            "buy_url": "https://www.indiangoods.shop/products/foxtale-2-salicylic-acid-aha-bha-exfoliating-serum-with-niacinamide-fights-acne-reduces-blackheads-whiteheads-reduces-excess-oil-bumpy-texture"
        },
        "dark_spot_serum": {
            "product": "AHA BHA Exfoliating Serum",
            "price_inr": 595,
            "image_url": "https://foxtale.in/cdn/shop/files/AHABHAexfoliatingserum.jpg?v=1743841494",
            "buy_url": "https://www.indiangoods.shop/products/foxtale-2-salicylic-acid-aha-bha-exfoliating-serum-with-niacinamide-fights-acne-reduces-blackheads-whiteheads-reduces-excess-oil-bumpy-texture"
        },
        "eye_cream": {
            "product": "Under Eye Gel",
            "price_inr": 445,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/BRIGHTENING_EYE_CREAM.jpg?v=1775478963",
            "buy_url": "https://foxtale.in/products/brightening-under-eye-cream"
        },
        "hydrating_serum": {
            "product": "Hydrating Serum",
            "price_inr": 595,
            "image_url": "https://foxtale.in/cdn/shop/files/Keephydratingdailyserum.jpg?v=1743841702",
            "buy_url": "https://www.indiangoods.shop/products/foxtale-daily-hydrating-serum-with-hyaluronic-acid-for-plump-glowing-skin"
        },
        "serum_oily": {
            "product": "Niacinamide Clarifying Serum",
            "price_inr": 595,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/FXN-DINS30_21.png?v=1775739509",
            "buy_url": "https://foxtale.in/products/niacinamide-clarifying-serum"
        },
        "serum_dry": {
            "product": "Cell Renewal Collagen PDRN Serum",
            "price_inr": 745,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/PDRN.png?v=1775539014",
            "buy_url": "https://foxtale.in/products/cell-renewal-collagen-pdrn-serum"
        },
        "serum_combination": {
            "product": "3% Tranexamic Acid Serum",
            "price_inr": 595,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/RAPID_SPOT_REDUCTION.png?v=1775541202",
            "buy_url": "https://foxtale.in/products/hyperpigmentation-serum-with-tranexamic-acid"
        },
        "serum_normal": {
            "product": "15% Vitamin C Serum",
            "price_inr": 595,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/VIT_C_c23ad065-dc46-4e11-8b29-bfa0b48ba6cc.png?v=1775740729",
            "buy_url": "https://foxtale.in/products/c-for-yourself-vitamin-c-serum"
        },
        "moisturizer_combination": {
            "product": "Oil-Free Moisturizer",
            "price_inr": 395,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/OIL_FREE_MOISTURIZER.jpg?v=1764856503",
            "buy_url": "https://foxtale.in/products/oil-free-moisturizer"
        },
        "moisturizer_normal": {
            "product": "Super Glow Moisturizer",
            "price_inr": 445,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/SGM_d685c69a-0269-4980-99ae-aa83174cfd12.png?v=1775721226",
            "buy_url": "https://foxtale.in/products/super-glow-moisturizer"
        },
        "sunscreen_oily": {
            "product": "Cool Shade Oil Control Water Gel Sunscreen",
            "price_inr": 449,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/FXN-OCGS50-51.jpg?v=1774944091",
            "buy_url": "https://foxtale.in/products/foxtale-cool-shade-oil-control-water-gel-sunscreen"
        },
        "sunscreen_dry": {
            "product": "SPF 70 Dewy Finish Sunscreen",
            "price_inr": 449,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/DSS_f64d1d4e-455d-40c8-9fad-860362d7177e.png?v=1775538764",
            "buy_url": "https://foxtale.in/products/spf-70-dewy-finish-sunscreen"
        },
        "sunscreen_combination": {
            "product": "Matte Finish Sunscreen",
            "price_inr": 449,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/MSS_da91b1ef-9a43-4daa-836d-389c3e0b24b7.png?v=1775740609",
            "buy_url": "https://foxtale.in/products/matte-finish-sunscreen"
        },
        "sunscreen_normal": {
            "product": "Glow Sunscreen SPF 50",
            "price_inr": 449,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/FXN-ESDS50_51.png?v=1775719328",
            "buy_url": "https://foxtale.in/products/glow-sunscreen"
        },
        "acne_treatment": {
            "product": "Acne Spot Corrector Gel",
            "price_inr": 395,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/ASCG_817f5274-5d6b-4384-b7a0-74037c205ce9.png?v=1775723094",
            "buy_url": "https://foxtale.in/products/acne-spot-corrector-gel"
        },
        "dark_spot_serum": {
            "product": "3% Tranexamic Acid Serum",
            "price_inr": 595,
            "image_url": "https://cdn.shopify.com/s/files/1/0609/6096/4855/files/RAPID_SPOT_REDUCTION.png?v=1775541202",
            "buy_url": "https://foxtale.in/products/hyperpigmentation-serum-with-tranexamic-acid"
        }
    },
    "Dot & Key": {
        "cleanser": {
            "product": "Cica Calming Blemish Clearing Face Wash",
            "price_inr": 349,
            "image_url": "https://www.dotandkey.com/cdn/shop/files/CicaFaceWash.jpg",
            "buy_url": "https://www.dotandkey.com/products/cica-calming-blemish-clearing-face-wash"
        },
        "cleanser_oily": {
            "product": "Cica + Salicylic Acid Face Wash",
            "price_inr": 349,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/1-175ml.jpg?v=1754918657",
            "buy_url": "https://www.dotandkey.com/products/cica-calming-blemish-clearing-face-wash"
        },
        "cleanser_dry": {
            "product": "Barrier Repair Gentle Hydrating Face Wash",
            "price_inr": 395,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/1-BRfacewash-Listing-175ml.jpg?v=1754918416",
            "buy_url": "https://www.dotandkey.com/products/dot-key-barrier-repair-gentle-hydrating-face-wash-with-5-essential-ceramides-hyaluronic-ph-5-5-fragrance-sulphate-free-for-sensitive-dry-skin"
        },
        "cleanser_combination": {
            "product": "Deep Pore Clean Foaming Face Wash",
            "price_inr": 375,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/1-Deep-Pore-Cleanser_1.jpg?v=1705741985",
            "buy_url": "https://www.dotandkey.com/products/deep-pore-clean-milky-foam-cleanser-120ml"
        },
        "cleanser_normal": {
            "product": "Vitamin C Foaming Face Wash",
            "price_inr": 349,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/1-Vit-C-Foaming-FW.jpg?v=1738833219",
            "buy_url": "https://www.dotandkey.com/products/vitamin-c-super-bright-foaming-face-wash"
        },
        "moisturizer_oily": {
            "product": "Cica Niacinamide Oil-Free Moisturizer",
            "price_inr": 395,
            "image_url": "https://www.dotandkey.com/cdn/shop/files/CicaNiacinamideMoisturizer.jpg",
            "buy_url": "https://www.dotandkey.com/products/cica-5-niacinamide-oil-free-moisturizer-for-dark-spots-acne-fragrance-free-oily-sensitive-acne-prone-skin"
        },
        "moisturizer_dry": {
            "product": "Barrier Repair Hydrating Moisturizer",
            "price_inr": 495,
            "image_url": "https://www.dotandkey.com/cdn/shop/files/BarrierRepairMoisturizer.jpg",
            "buy_url": "https://www.dotandkey.com/products/72-hr-hydrating-probiotic-gel-moisturizer-for-face-with-hyaluronic-rice-water-25ml"
        },
        "sunscreen": {
            "product": "Watermelon Cooling Sunscreen SPF 50",
            "price_inr": 499,
            "image_url": "https://www.dotandkey.com/cdn/shop/files/WatermelonSunscreenSPF50.jpg",
            "buy_url": "https://www.dotandkey.com/products/watermelon-cooling-spf-50-face-sunscreen"
        },
        "acne_treatment": {
            "product": "2% Salicylic + Cica Serum",
            "price_inr": 545,
            "image_url": "https://www.dotandkey.com/cdn/shop/files/2SalicylicCicaSerum.jpg",
            "buy_url": "https://www.dotandkey.com/products/dot-key-cica-2-salicylic-acne-control-serum-with-zinc-for-clear-skin-reduces-blackheads-whiteheads-oily-acne-prone-skin"
        },
        "dark_spot_serum": {
            "product": "10% Vitamin C + E Super Bright Serum",
            "price_inr": 599,
            "image_url": "https://www.dotandkey.com/cdn/shop/files/VitaminCSuperBrightSerum.jpg",
            "buy_url": "https://www.dotandkey.com/products/dot-key-cica-10-niacinamide-serum-for-blemish-free-spotless-glowing-skin-3-tranexamic-reduces-acne-dark-spots-oily-acne-prone-sensitive-skin"
        },
        "eye_cream": {
            "product": "Vitamin C + Caffeine Under Eye Cream",
            "price_inr": 399,
            "image_url": "https://www.dotandkey.com/cdn/shop/files/VitaminCCaffeineUnderEyeCream.jpg",
            "buy_url": "https://www.dotandkey.com/products/retinol-eye-cream"
        },
        "hydrating_serum": {
            "product": "72HR Hydrating Gel + Probiotics",
            "price_inr": 595,
            "image_url": "https://www.dotandkey.com/cdn/shop/files/72HRHydratingGel.jpg",
            "buy_url": "https://www.dotandkey.com/products/hydrating-hyaluronic-face-serum"
        },
        "serum_oily": {
            "product": "Cica + 2% Salicylic Acid Serum",
            "price_inr": 545,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/Artboard1copy_c9675994-8c27-4894-9bea-a1955aaa404f.jpg?v=1754039836",
            "buy_url": "https://www.dotandkey.com/products/dot-key-cica-2-salicylic-acne-control-serum-with-zinc-for-clear-skin-reduces-blackheads-whiteheads-oily-acne-prone-skin"
        },
        "serum_dry": {
            "product": "12% Barrier Boost Serum",
            "price_inr": 649,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/1-1_2.jpg?v=1761888895",
            "buy_url": "https://www.dotandkey.com/products/barrier-repair-serum"
        },
        "serum_combination": {
            "product": "Cica + 10% Niacinamide Face Serum",
            "price_inr": 599,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/1c_2.jpg?v=1727355078",
            "buy_url": "https://www.dotandkey.com/products/dot-key-cica-10-niacinamide-serum-for-blemish-free-spotless-glowing-skin-3-tranexamic-reduces-acne-dark-spots-oily-acne-prone-sensitive-skin"
        },
        "serum_normal": {
            "product": "10% Vitamin C + E Face Serum",
            "price_inr": 649,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/1-1_b4ae866f-e0a8-43d1-971f-1d143d76f01c.jpg?v=1761888942",
            "buy_url": "https://www.dotandkey.com/products/dot-key-10-vitamin-c-e-5-niacinamide-serum-for-glowing-skin-beginner-friendly"
        },
        "moisturizer_combination": {
            "product": "Barrier Repair Oil-Free Moisturizer",
            "price_inr": 445,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/1-1_cc24a602-1169-487d-8419-5681659434b2.jpg?v=1757933155",
            "buy_url": "https://www.dotandkey.com/products/barrier-repair-oil-free-moisturizer"
        },
        "moisturizer_normal": {
            "product": "Vitamin C + E Moisturizer",
            "price_inr": 495,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/1.webp?v=1770640542",
            "buy_url": "https://www.dotandkey.com/products/vitamin-c-e-super-bright-moisturizer"
        },
        "sunscreen_oily": {
            "product": "Cica + Niacinamide Sunscreen SPF 50+",
            "price_inr": 499,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/CicaSunscreenListing1-50g_95ce58f1-bd67-4d5c-9179-44129fb40502.jpg?v=1770185396",
            "buy_url": "https://www.dotandkey.com/products/cica-calming-mattifying-sunscreen-spf-50-pa"
        },
        "sunscreen_dry": {
            "product": "Barrier Repair Sunscreen SPF 50+",
            "price_inr": 499,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/Artboard_1_copy_c38bbbf3-ec26-4add-9b79-df3f9eb96600.jpg?v=1772446737",
            "buy_url": "https://www.dotandkey.com/products/barrier-repair-sunscreen"
        },
        "sunscreen_combination": {
            "product": "Watermelon Cooling Sunscreen SPF 50+",
            "price_inr": 499,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/1_2_c4b41e22-06fe-4394-a7f8-a5aa302bc000.jpg?v=1772446468",
            "buy_url": "https://www.dotandkey.com/products/watermelon-cooling-spf-50-face-sunscreen"
        },
        "sunscreen_normal": {
            "product": "Vitamin C + E Sunscreen SPF 50+",
            "price_inr": 499,
            "image_url": "http://www.dotandkey.com/cdn/shop/files/80newww.jpg?v=1770965371",
            "buy_url": "https://www.dotandkey.com/products/dot-key-vitamin-c-e-spf-50-pa-face-sunscreen-for-glowing-skin-uv-protection-for-dull-skin"
        }
    },
    "The Derma Co": {
        "cleanser": {
            "product": "Creamy Face Cleanser",
            "price_inr": 299,
            "image_url": "https://thedermaco.com/cdn/shop/files/CreamyFaceCleanser.jpg",
            "buy_url": "https://thedermaco.com/products/creamy-cleanser"
        },
        "cleanser_oily": {
            "product": "2% Niacinamide Oily Skin Cleanser",
            "price_inr": 299,
            "image_url": "http://thedermaco.com/cdn/shop/files/2-niacinamide_oily_skin_cleanser_for_sensitive_oily_combination_skin.png?v=1758286818",
            "buy_url": "https://thedermaco.com/products/2-niacinamide-oily-skin-cleanser-for-sensitive-oily-combination-skin-125-ml"
        },
        "cleanser_dry": {
            "product": "2% Niacinamide Gentle Dry Skin Cleanser",
            "price_inr": 299,
            "image_url": "http://thedermaco.com/cdn/shop/files/1-niacinamide_gentle_skin_cleanser_for_sensitive_dry_normal_skin_79a6002c-a0fa-47c4-bed1-3aa6c41f48e7.jpg?v=1758286821",
            "buy_url": "https://thedermaco.com/products/2-niacinamide-gentle-skin-cleanser-for-sensitive-dry-normal-skin-125-ml"
        },
        "cleanser_combination": {
            "product": "Oil-Free Daily Face Wash",
            "price_inr": 299,
            "image_url": "http://thedermaco.com/cdn/shop/files/PDP_10b2f0d4-0281-4802-aef0-d1e8c223f103.jpg?v=1773726179",
            "buy_url": "https://thedermaco.com/products/oil-free-daily-face-wash-with-hyaluronic-acid-glycolic-acid-multivitamins-for-clear-hydrated-skin-100ml"
        },
        "cleanser_normal": {
            "product": "2% Vitamin C Gel Daily Face Wash",
            "price_inr": 299,
            "image_url": "http://thedermaco.com/cdn/shop/files/1_-_2_vitamin_c_gel_daily_face_wash.jpg?v=1758286854",
            "buy_url": "https://thedermaco.com/products/2-vitamin-c-gel-daily-face-wash-with-vitamin-c-rosehip-orange-peel-extract-for-glowing-skin-80ml"
        },
        "moisturizer_oily": {
            "product": "Oil-Free Daily Face Moisturizer",
            "price_inr": 349,
            "image_url": "https://thedermaco.com/cdn/shop/files/OilFreeDailyFaceMoisturizer.jpg",
            "buy_url": "https://thedermaco.com/products/1-salicylic-acid-oil-free-moisturizer-for-face-with-oat-extract-50g"
        },
        "moisturizer_dry": {
            "product": "Ceramide + HA Intense Moisturizer",
            "price_inr": 449,
            "image_url": "https://thedermaco.com/cdn/shop/files/CeramideHAIntenseMoisturizer.jpg",
            "buy_url": "https://thedermaco.com/products/ceramide-ha-intense-moisturizer"
        },
        "sunscreen": {
            "product": "1% Hyaluronic Sunscreen Aqua Gel SPF 50",
            "price_inr": 499,
            "image_url": "https://thedermaco.com/cdn/shop/files/HyaluronicSunscreenAquaGel.jpg",
            "buy_url": "https://thedermaco.com/products/1-hyaluronic-sunscreen-aqua-gel"
        },
        "acne_treatment": {
            "product": "2% Salicylic Acid Serum",
            "price_inr": 499,
            "image_url": "https://thedermaco.com/cdn/shop/files/2SalicylicAcidSerum.jpg",
            "buy_url": "https://thedermaco.com/products/2-salicylic-acid-serum"
        },
        "dark_spot_serum": {
            "product": "10% Niacinamide Face Serum",
            "price_inr": 499,
            "image_url": "https://thedermaco.com/cdn/shop/files/10NiacinamideFaceSerum.jpg",
            "buy_url": "https://thedermaco.com/products/10-percent-niacinamide-serum"
        },
        "eye_cream": {
            "product": "5% Caffeine Under Eye Serum",
            "price_inr": 449,
            "image_url": "https://thedermaco.com/cdn/shop/files/5CaffeineUnderEyeSerum.jpg",
            "buy_url": "https://thedermaco.com/products/5-caffeine-under-eye-serum-for-dark-circles-puffiness"
        },
        "hydrating_serum": {
            "product": "2% Hyaluronic Acid Serum",
            "price_inr": 499,
            "image_url": "https://thedermaco.com/cdn/shop/files/2HyaluronicAcidSerum.jpg",
            "buy_url": "https://thedermaco.com/products/10-percent-niacinamide-serum"
        },
        "serum_oily": {
            "product": "Sali-Cinamide Anti-Acne Serum",
            "price_inr": 549,
            "image_url": "http://thedermaco.com/cdn/shop/files/pdp_sali-cinamide_serum.jpg?v=1758286814",
            "buy_url": "https://thedermaco.com/products/sali-cinamide-anti-acne-serum-with-2-salicylic-acid-5-niacinamide-30ml"
        },
        "serum_dry": {
            "product": "1% Hyaluronic Serum Sunscreen",
            "price_inr": 549,
            "image_url": "http://thedermaco.com/cdn/shop/files/1_-hyaluronic-sunscreen-serum-2.jpg?v=1758286662",
            "buy_url": "https://thedermaco.com/products/1-hyaluronic-acid-sunscreen-serum-with-spf-50-niacinamide-30ml"
        },
        "serum_combination": {
            "product": "Pore Minimizing Face Serum",
            "price_inr": 599,
            "image_url": "http://thedermaco.com/cdn/shop/files/pore-minimizing-face-serum.jpg?v=1758286636",
            "buy_url": "https://thedermaco.com/products/pore-minimizing-face-serum-with-4-niacinamide-5-pha-and-p-refinylr-30-ml"
        },
        "serum_normal": {
            "product": "C-Cinamide Radiance Serum",
            "price_inr": 599,
            "image_url": "http://thedermaco.com/cdn/shop/files/1_5_3.jpg?v=1758286787",
            "buy_url": "https://thedermaco.com/products/c-cinamide-radiance-serum-with-10-vitamin-c-5-niacinamide-30ml"
        },
        "moisturizer_combination": {
            "product": "Pore Minimizing Daily Face Moisturizer",
            "price_inr": 449,
            "image_url": "http://thedermaco.com/cdn/shop/files/pore-minimizing-moisturizer_2.jpg?v=1758286634",
            "buy_url": "https://thedermaco.com/products/pore-minimizing-daily-face-moisturizer-with-3-niacinamide-3-pha-and-p-refinylr-50-g"
        },
        "moisturizer_normal": {
            "product": "3% Vitamin E Face Moisturizer",
            "price_inr": 399,
            "image_url": "http://thedermaco.com/cdn/shop/files/1st-image.jpg?v=1758286590",
            "buy_url": "https://thedermaco.com/products/3-vitamin-e-face-moisturizer"
        },
        "sunscreen_oily": {
            "product": "Ultra Matte Sunscreen Gel SPF 60",
            "price_inr": 599,
            "image_url": "http://thedermaco.com/cdn/shop/files/ultra_matte_sunscreen.jpg?v=1758286466",
            "buy_url": "https://thedermaco.com/products/ultra-matte-sunscreen-gel"
        },
        "sunscreen_dry": {
            "product": "1% Hyaluronic Sunscreen Aqua Gel",
            "price_inr": 499,
            "image_url": "http://thedermaco.com/cdn/shop/files/1_PDP_fea245fa-2933-433c-82ef-c5bc8c2070b4.jpg?v=1775563596",
            "buy_url": "https://thedermaco.com/products/1-hyaluronic-sunscreen-aqua-gel"
        },
        "sunscreen_combination": {
            "product": "Pore Minimizing Priming Sunscreen SPF 50",
            "price_inr": 499,
            "image_url": "http://thedermaco.com/cdn/shop/files/1_PDP_5907e859-db48-4170-80fc-80ad85051367.jpg?v=1773233915",
            "buy_url": "https://thedermaco.com/products/pore-minimizing-priming-sunscreen-with-spf-50-pa-for-open-pores-uva-uvb-protection-50g"
        },
        "sunscreen_normal": {
            "product": "C-Cinamide Radiance Sunscreen Aqua Gel",
            "price_inr": 499,
            "image_url": "http://thedermaco.com/cdn/shop/files/fop_c-cinamide_white_bg.jpg?v=1758286799",
            "buy_url": "https://thedermaco.com/products/c-cinamide-radiance-sunscreen-aqua-gel-with-spf-50-pa-50g"
        },
        "dark_spot_serum": {
            "product": "2% Kojic Acid Face Serum",
            "price_inr": 549,
            "image_url": "http://thedermaco.com/cdn/shop/files/pdp_2_kojic_serum_new.jpg?v=1758286610",
            "buy_url": "https://thedermaco.com/products/2-kojic-acid-face-serum-with-1-alpha-arbutin-niacinamide-30-ml"
        },
        "eye_cream": {
            "product": "5% Caffeine Under Eye Serum",
            "price_inr": 449,
            "image_url": "http://thedermaco.com/cdn/shop/files/5_caffiene_serum_fy1glk9capyvca0o.jpg?v=1758286528",
            "buy_url": "https://thedermaco.com/products/5-caffeine-under-eye-serum-for-dark-circles-puffiness"
        }
    },
    "Minimalist": {
        "cleanser": {
            "product": "2% Salicylic Acid Cleanser",
            "price_inr": 299,
            "image_url": "http://beminimalist.co/cdn/shop/files/SalicylicCleanserNew.jpg?v=1756796206",
            "buy_url": "https://beminimalist.co/products/salicylic-lha-2-cleanser"
        },
        "cleanser_oily": {
            "product": "Salicylic + LHA 2% Cleanser",
            "price_inr": 299,
            "image_url": "http://beminimalist.co/cdn/shop/files/SalicylicCleanserNew.jpg?v=1756796206",
            "buy_url": "https://beminimalist.co/products/salicylic-lha-2-cleanser"
        },
        "cleanser_dry": {
            "product": "Oat Extract 06% Gentle Cleanser",
            "price_inr": 299,
            "image_url": "http://beminimalist.co/cdn/shop/products/OatCleanser1200-1.png?v=1651078209",
            "buy_url": "https://beminimalist.co/products/oat-extract-06-gentle-cleanser"
        },
        "cleanser_combination": {
            "product": "Aquaporin Booster 05% Cleanser",
            "price_inr": 299,
            "image_url": "http://beminimalist.co/cdn/shop/files/AquaporinNew.png?v=1721398128",
            "buy_url": "https://beminimalist.co/products/aquaporin-booster-05-cleanser"
        },
        "cleanser_normal": {
            "product": "Alpha Lipoic + Glycolic 07% Cleanser",
            "price_inr": 299,
            "image_url": "http://beminimalist.co/cdn/shop/files/AlphaLipoicNew.png?v=1746106817",
            "buy_url": "https://beminimalist.co/products/alpha-lipoic-glycolic-07-cleanser"
        },
        "moisturizer_oily": {
            "product": "Vitamin B5 10% Moisturizer",
            "price_inr": 349,
            "image_url": "http://beminimalist.co/cdn/shop/products/B5Moisturizer1200-2-min.png?v=1756800645",
            "buy_url": "https://beminimalist.co/products/vitamin-b5-10-moisturizer"
        },
        "moisturizer_dry": {
            "product": "Marula 5% Moisturizer",
            "price_inr": 349,
            "image_url": "http://beminimalist.co/cdn/shop/files/ListingMarulaOil05.jpg?v=1760096773",
            "buy_url": "https://beminimalist.co/collections/new-launches/products/marula-oil-05-cleansing-oil"
        },
        "sunscreen": {
            "product": "SPF 50 Sunscreen",
            "price_inr": 399,
            "image_url": "http://beminimalist.co/cdn/shop/files/SPF50New.jpg?v=1756795782",
            "buy_url": "https://beminimalist.co/products/multi-vitamin-spf-50"
        },
        "acne_treatment": {
            "product": "2% Salicylic Acid Serum",
            "price_inr": 549,
            "image_url": "http://beminimalist.co/cdn/shop/products/SalicylicAcid2_1200-1-min.png?v=1646458899",
            "buy_url": "https://beminimalist.co/products/salicylic-acid-2"
        },
        "dark_spot_serum": {
            "product": "Niacinamide 10% Serum",
            "price_inr": 599,
            "image_url": "http://beminimalist.co/cdn/shop/files/Nia10New.png?v=1721398127",
            "buy_url": "https://beminimalist.co/products/niacinamide-10-with-matmarine"
        },
        "eye_cream": {
            "product": "Vitamin K + Retinal Eye Cream",
            "price_inr": 399,
            "image_url": "http://beminimalist.co/cdn/shop/files/KRetinalNew.png?v=1721632054",
            "buy_url": "https://beminimalist.co/products/vitamin-k-retinal-01-eye-cream"
        },
        "hydrating_serum": {
            "product": "2% Hyaluronic Acid Serum",
            "price_inr": 549,
            "image_url": "http://beminimalist.co/cdn/shop/files/B12ListingImage.jpg?v=1756800848",
            "buy_url": "https://beminimalist.co/products/vitamin-b12-repair-complex-5-5-face-moisturizer"
        },
        "serum_oily": {
            "product": "Niacinamide 10% + Zinc Serum",
            "price_inr": 599,
            "image_url": "http://beminimalist.co/cdn/shop/files/Nia10New.png?v=1721398127",
            "buy_url": "https://beminimalist.co/products/niacinamide-10-with-matmarine"
        },
        "serum_dry": {
            "product": "Multi Peptide Serum",
            "price_inr": 699,
            "image_url": "http://beminimalist.co/cdn/shop/files/MultiNew.png?v=1721398128",
            "buy_url": "https://beminimalist.co/products/multi-peptide-serum-7-matrixyl-3000-3-bio-placenta"
        },
        "serum_combination": {
            "product": "Multi Repair Actives 15% Face Serum",
            "price_inr": 649,
            "image_url": "http://beminimalist.co/cdn/shop/files/MultiRepairListing.jpg?v=1762515398",
            "buy_url": "https://beminimalist.co/products/multi-repair-actives-15-face-serum"
        },
        "serum_normal": {
            "product": "Vitamin C + E + Ferulic 16% Serum",
            "price_inr": 699,
            "image_url": "http://beminimalist.co/cdn/shop/files/Vit16New.png?v=1721398127",
            "buy_url": "https://beminimalist.co/products/vitamin-c-e-ferulic-16"
        },
        "moisturizer_combination": {
            "product": "Sepicalm 3% + Oat Moisturiser",
            "price_inr": 349,
            "image_url": "http://beminimalist.co/cdn/shop/files/Sepicalm_New.png?v=1721398128",
            "buy_url": "https://beminimalist.co/products/sepicalm-3-oat-moisturiser"
        },
        "moisturizer_normal": {
            "product": "B12 + Repair Complex 5.5% Face Moisturizer",
            "price_inr": 399,
            "image_url": "http://beminimalist.co/cdn/shop/files/B12ListingImage.jpg?v=1756800848",
            "buy_url": "https://beminimalist.co/products/vitamin-b12-repair-complex-5-5-face-moisturizer"
        },
        "sunscreen_oily": {
            "product": "SPF 60 + Silymarin Sunscreen",
            "price_inr": 599,
            "image_url": "http://beminimalist.co/cdn/shop/products/SPF601200-2-min.png?v=1646571969",
            "buy_url": "https://beminimalist.co/products/spf-60-silymarin"
        },
        "sunscreen_dry": {
            "product": "Multi-Vitamin SPF 50",
            "price_inr": 399,
            "image_url": "http://beminimalist.co/cdn/shop/files/SPF50New.jpg?v=1756795782",
            "buy_url": "https://beminimalist.co/products/multi-vitamin-spf-50"
        },
        "sunscreen_combination": {
            "product": "Light Fluid SPF 50 Sunscreen",
            "price_inr": 499,
            "image_url": "http://beminimalist.co/cdn/shop/files/LightFluid_New.png?v=1741082933",
            "buy_url": "https://beminimalist.co/products/light-fluid-spf-50-sunscreen"
        },
        "sunscreen_normal": {
            "product": "Multi-Vitamin SPF 50",
            "price_inr": 399,
            "image_url": "http://beminimalist.co/cdn/shop/files/SPF50New.jpg?v=1756795782",
            "buy_url": "https://beminimalist.co/products/multi-vitamin-spf-50"
        }
    },
    "Cetaphil": {
    "cleanser": {
        "product": "Gentle Skin Cleanser",
        "price_inr": 399,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw311450bb/GSC%20Revive%20A%2B/236%20ml/ATF/1.FoP-236.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/products/cleansers/gentle-skin-cleanser/8906005274069.html"
    },
    "cleanser_oily": {
        "product": "Oily Skin Cleanser",
        "price_inr": 399,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw2803e62d/OSC%20Revive%20A%2B/OSC%20236ml/ATF/1.%20FoP.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/products/cleansers/oily-skin-cleanser/8906005274090.html"
    },
    "cleanser_dry": {
        "product": "Gentle Skin Cleanser",
        "price_inr": 399,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw311450bb/GSC%20Revive%20A%2B/236%20ml/ATF/1.FoP-236.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/products/cleansers/gentle-skin-cleanser/8906005274069.html"
    },
    "cleanser_combination": {
        "product": "Gentle Foaming Cleanser",
        "price_inr": 549,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw04656763/Gentle%20Foaming%20Cleanser%208%20Oz/051872-GFC8oz_Front.PNG?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/products/cleansers/gentle-foaming-cleanser/3499320010092.html"
    },
    "cleanser_normal": {
        "product": "Brightness Reveal Cream Cleanser",
        "price_inr": 699,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dwa987ef39/Rebranding/3499320011556/ATF/Cetaphil%20Bright%20Healthy%20Radiance%20Reveal%20Creamy%20Cleanser%20100g-1.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/products/cleansers/cetaphil-bright-healthy-radiance-reveal-creamy-cleanser/3499320011556.html"
    },
    "moisturizer_oily": {
        "product": "Moisturising Lotion",
        "price_inr": 499,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw1ee5a892/CML%20Revive%20A%2B/236ml/ATF/1.%20FoP.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/moisturizers/cetaphil-moisturising-lotion/8906005271623.html"
    },
    "moisturizer_dry": {
        "product": "Moisturising Cream",
        "price_inr": 649,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw17957a60/8906005273437/rebranding/ATF/1.%20FoP.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/moisturizers/moisturising-cream/8906005273436.html/"
    },
    "sunscreen": {
        "product": "Sun SPF 50+ Light Gel",
        "price_inr": 899,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw76b723b9/Sun%2050%20Revive%20A%2B/ATF/1.%20FoP%20%281%29.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/sunscreens/cetaphil-spf-50%2B-sunscreen/3499320013192.html"
    },
    "acne_treatment": {
        "product": "Gentle Clear Triple-Action Acne Serum",
        "price_inr": 799,
        "image_url": "https://www.cetaphil.com/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-us-m-catalog/default/dw05965c08/New-Pics/%28084012%29_GC_Treatment_Serum_1oz_Tube-Front.PNG?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.com/us/products/product-categories/all-cleansers/gentle-clear-triple-action-acne-serum/302994130009.html"
    },
    "dark_spot_serum": {
        "product": "Bright Healthy Radiance Serum",
        "price_inr": 999,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dwf0e0bdc5/Rebranding/Serum/30Ml/ATF/Cetaphil%20Bright%20Healthy%20Radiance%20Perfecting%20Serum%2030ml-1.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/moisturizers/facial-moisturizers-serums/cetaphil-bright-healthy-radiance-perfecting-serum-30g-with-antioxidant-c-and-advanced-peptides/IN_3499320016056.html"
    },
    "eye_cream": {
        "product": "Hydrating Eye Gel-Cream",
        "price_inr": 849,
        "image_url": "https://www.cetaphil.com/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-us-m-catalog/default/dw1f5eb4b4/Hydrating%20Eye%20Gel-Cream%2C%200%2C5%20fl%20oz/082000_HEGC%200.5oz%2014ml_Tube-Front.PNG?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.com/us/products/product-categories/eye-creams/hydrating-eye-gel-cream/302993889168.html"
    },
    "hydrating_serum": {
        "product": "Optimal Hydration Serum",
        "price_inr": 899,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw6abb88b7/8906005274656/Serum.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/moisturiser/serums/cetaphil-optimal-hydration-serum/8906005274656_OH_Serum_IN.html"
    },
    "serum_oily": {
        "product": "Gentle Clear Triple-Action Acne Serum",
        "price_inr": 799,
        "image_url": "https://www.cetaphil.com/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-us-m-catalog/default/dw05965c08/New-Pics/%28084012%29_GC_Treatment_Serum_1oz_Tube-Front.PNG?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.com/us/products/product-categories/all-cleansers/gentle-clear-triple-action-acne-serum/302994130009.html"
    },
    "serum_dry": {
        "product": "Optimal Hydration Serum",
        "price_inr": 899,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw6abb88b7/8906005274656/Serum.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/moisturiser/serums/cetaphil-optimal-hydration-serum/8906005274656_OH_Serum_IN.html"
    },
    "serum_combination": {
        "product": "Bright Healthy Radiance Serum",
        "price_inr": 999,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dwf0e0bdc5/Rebranding/Serum/30Ml/ATF/Cetaphil%20Bright%20Healthy%20Radiance%20Perfecting%20Serum%2030ml-1.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/moisturizers/facial-moisturizers-serums/cetaphil-bright-healthy-radiance-perfecting-serum-30g-with-antioxidant-c-and-advanced-peptides/IN_3499320016056.html"
    },
    "serum_normal": {
        "product": "Bright Healthy Radiance Serum",
        "price_inr": 999,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dwf0e0bdc5/Rebranding/Serum/30Ml/ATF/Cetaphil%20Bright%20Healthy%20Radiance%20Perfecting%20Serum%2030ml-1.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/moisturizers/facial-moisturizers-serums/cetaphil-bright-healthy-radiance-perfecting-serum-30g-with-antioxidant-c-and-advanced-peptides/IN_3499320016056.html"
    },
    "moisturizer_combination": {
        "product": "Daily Advance Ultra Hydrating Lotion",
        "price_inr": 699,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw7dc30439/8906005271709/Cetaphil-Daily-Advance-Ultra-Hydrating-Lotion-100gm.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/moisturizers/daily-advance-ultra-hydrating-lotion/8906005271708.html"
    },
    "moisturizer_normal": {
        "product": "Bright Healthy Radiance Day Protection Cream",
        "price_inr": 899,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw54b217f4/Rebranding/3499320011518/ATF/Cetaphil%20Bright%20Healthy%20Radiance%20Brightening%20Day%20Protection%20Cream%2050g-1.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/moisturizers/cetaphil-bright-healthy-radiance-brightening-day-protection-cream-spf15/3499320011549.html"
    },
    "sunscreen_oily": {
        "product": "Sun SPF 50+ Light Gel",
        "price_inr": 899,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw76b723b9/Sun%2050%20Revive%20A%2B/ATF/1.%20FoP%20%281%29.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/sunscreens/cetaphil-spf-50%2B-sunscreen/3499320013192.html"
    },
    "sunscreen_dry": {
        "product": "Sun Kids Liposomal Lotion SPF 50",
        "price_inr": 999,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dwe5e24f48/3499320012065/Cetaphil-Sun-Kids-SPF-50-FR.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/sunscreens/sun-kids-spf-50%2B-lotion/3499320012065.html"
    },
    "sunscreen_combination": {
        "product": "Bright Healthy Radiance Day Protection Cream SPF 15",
        "price_inr": 899,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw54b217f4/Rebranding/3499320011518/ATF/Cetaphil%20Bright%20Healthy%20Radiance%20Brightening%20Day%20Protection%20Cream%2050g-1.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/moisturizers/cetaphil-bright-healthy-radiance-brightening-day-protection-cream-spf15/3499320011549.html"
    },
    "sunscreen_normal": {
        "product": "Sun SPF 50+ Light Gel",
        "price_inr": 899,
        "image_url": "https://www.cetaphil.in/dw/image/v2/BGGN_PRD/on/demandware.static/-/Sites-galderma-in-m-catalog/default/dw76b723b9/Sun%2050%20Revive%20A%2B/ATF/1.%20FoP%20%281%29.png?q=85&sh=900&sm=fit&sw=900",
        "buy_url": "https://www.cetaphil.in/sunscreens/cetaphil-sun-light-gel-spf-50/3499320013192.html"
    }
},

    "Himalaya": {
        "cleanser": {
            "product": "Purifying Neem Face Wash",
            "price_inr": 179,
            "image_url": "https://himalayawellness.in/cdn/shop/files/7918780-4_Himalaya-Purifying-Neem-Face-Wash-100ml-Tube_FOP.jpg?v=1748409998",
            "buy_url": "https://himalayawellness.in/products/himalaya-purifying-neem-face-wash"
        },
        "cleanser_oily": {
            "product": "Purifying Neem Face Wash",
            "price_inr": 179,
            "image_url": "https://himalayawellness.in/cdn/shop/files/7918780-4_Himalaya-Purifying-Neem-Face-Wash-100ml-Tube_FOP.jpg?v=1748409998",
            "buy_url": "https://himalayawellness.in/products/himalaya-purifying-neem-face-wash"
        },
        "cleanser_dry": {
            "product": "Moisturizing Aloe Vera Face Wash",
            "price_inr": 199,
            "image_url": "https://himalayawellness.in/cdn/shop/files/7918780-4_Himalaya-Purifying-Neem-Face-Wash-100ml-Tube_FOP.jpg?v=1748409998",
            "buy_url": "https://himalayawellness.in/collections/face-care"
        },
        "cleanser_combination": {
            "product": "Deep Cleansing Apricot Face Wash",
            "price_inr": 185,
            "image_url": "https://himalayawellness.in/cdn/shop/files/7918780-4_Himalaya-Purifying-Neem-Face-Wash-100ml-Tube_FOP.jpg?v=1748409998",
            "buy_url": "https://himalayawellness.in/collections/face-care"
        },
        "cleanser_normal": {
            "product": "Vitamin C Glow Face Wash",
            "price_inr": 199,
            "image_url": "https://himalayawellness.in/cdn/shop/files/7918780-4_Himalaya-Purifying-Neem-Face-Wash-100ml-Tube_FOP.jpg?v=1748409998",
            "buy_url": "https://himalayawellness.in/collections/face-care"
        },
        "serum_oily": {
            "product": "Oil Control Clarifying Serum",
            "price_inr": 399,
            "image_url": "https://himalayawellness.in/cdn/shop/products/dark-spot-clearing-turmeric-face-serum.jpg",
            "buy_url": "https://himalayawellness.in/collections/face-care"
        },
        "serum_dry": {
            "product": "Hydrating Aloe Vera Face Gel Serum",
            "price_inr": 399,
            "image_url": "https://himalayawellness.in/cdn/shop/files/Face-Gels-2000x2000_6e098a9d-3185-40f0-b081-da88eb01bcf8.jpg",
            "buy_url": "https://himalayawellness.in/products/himalaya-moisturizing-aloe-vera-face-gel"
        },
        "serum_combination": {
            "product": "Dark Spot Clearing Turmeric Serum",
            "price_inr": 399,
            "image_url": "https://himalayawellness.in/cdn/shop/files/Himalaya-Dark-Spot-Clearing-Turmeric-Face-Serum_Carton_30ml_FOP.jpg",
            "buy_url": "https://himalayawellness.in/products/dark-spot-clearing-turmeric-face-serum"
        },
        "serum_normal": {
            "product": "Vitamin C Glow Booster Serum",
            "price_inr": 449,
            "image_url": "https://himalayawellness.ae/cdn/shop/files/brightening-vitamin-C-labels-2024-face-serum-carton-30ml-gcc-comb.jpg?v=1733809197&width=1080",
            "buy_url": "https://himalayawellness.in/collections/face-care"
        },
        "moisturizer_oily": {
            "product": "Oil-Free Radiance Gel Cream",
            "price_inr": 249,
            "image_url": "https://himalayawellness.in/cdn/shop/products/oil-free-radiance-gel-cream.jpg",
            "buy_url": "https://himalayawellness.in/products/oil-free-radiance-gel-cream"
        },
        "moisturizer_dry": {
            "product": "Nourishing Skin Cream",
            "price_inr": 210,
            "image_url": "https://himalayawellness.in/cdn/shop/products/nourishing-skin-cream.jpg",
            "buy_url": "https://himalayawellness.in/products/nourishing-skin-cream"
        },
        "moisturizer_combination": {
            "product": "Clear Complexion Brightening Day Cream",
            "price_inr": 299,
            "image_url": "https://himalayawellness.in/cdn/shop/files/Resizepackshots.jpg",
            "buy_url": "https://himalayawellness.in/products/himalaya-clear-complexion-brightening-day-cream"
        },
        "moisturizer_normal": {
            "product": "Revitalizing Night Cream",
            "price_inr": 349,
            "image_url": "https://himalayawellness.in/cdn/shop/products/revitalizing-night-cream.jpg?v=1622097701",
            "buy_url": "https://himalayawellness.in/products/revitalizing-night-cream"
        },
        "sunscreen": {
            "product": "Protecting Sunscreen Lotion SPF 50",
            "price_inr": 349,
            "image_url": "https://himalayawellness.in/cdn/shop/files/AmazonPDP_Sunscreen-01.jpg?v=1748345092",
            "buy_url": "https://himalayawellness.in/products/himalaya-sun-protect-ultra-light-sunscreen"
        },
        "sunscreen_oily": {
            "product": "Sun Protect Ultra Light Sunscreen",
            "price_inr": 349,
            "image_url": "https://himalayawellness.in/cdn/shop/files/AmazonPDP_Sunscreen-01.jpg?v=1748345092",
            "buy_url": "https://himalayawellness.in/products/himalaya-sun-protect-ultra-light-sunscreen"
        },
        "sunscreen_dry": {
            "product": "Protective Sunscreen Lotion SPF 50",
            "price_inr": 349,
            "image_url": "https://himalayawellness.in/cdn/shop/files/AmazonPDP_Sunscreen-01.jpg?v=1748345092",
            "buy_url": "https://himalayawellness.in/products/himalaya-sun-protect-ultra-light-sunscreen"
        },
        "sunscreen_combination": {
            "product": "Radiance Mineral Sunscreen",
            "price_inr": 399,
            "image_url": "https://himalayawellness.in/cdn/shop/files/AmazonPDP_Sunscreen-01.jpg?v=1748345092",
            "buy_url": "https://himalayawellness.in/products/himalaya-sun-protect-ultra-light-sunscreen"
        },
        "sunscreen_normal": {
            "product": "Daily Glow Sunscreen SPF 50",
            "price_inr": 399,
            "image_url": "https://himalayawellness.in/cdn/shop/files/AmazonPDP_Sunscreen-01.jpg?v=1748345092",
            "buy_url": "https://himalayawellness.in/products/himalaya-sun-protect-ultra-light-sunscreen"
        },
        "acne_treatment": {
            "product": "Clarina Anti-Acne Cream",
            "price_inr": 165,
            "image_url": "https://himalayawellness.in/cdn/shop/products/clarina-anti-acne-cream.jpg",
            "buy_url": "https://himalayawellness.in/products/clarina-anti-acne-cream"
        },
        "dark_spot_serum": {
            "product": "Dark Spot Clearing Turmeric Serum",
            "price_inr": 399,
            "image_url": "https://himalayawellness.in/cdn/shop/files/Himalaya-Dark-Spot-Clearing-Turmeric-Face-Serum_Carton_30ml_FOP.jpg",
            "buy_url": "https://himalayawellness.in/products/dark-spot-clearing-turmeric-face-serum"
        },
        "eye_cream": {
            "product": "Under Eye Cream",
            "price_inr": 225,
            "image_url": "https://himalayawellness.in/cdn/shop/products/under-eye-cream.jpg",
            "buy_url": "https://himalayawellness.in/products/under-eye-cream"
        },
        "hydrating_serum": {
            "product": "Hydrating Aloe Vera Face Serum",
            "price_inr": 399,
            "image_url": "https://himalayawellness.in/cdn/shop/files/Face-Gels-2000x2000_6e098a9d-3185-40f0-b081-da88eb01bcf8.jpg",
            "buy_url": "https://himalayawellness.in/products/himalaya-moisturizing-aloe-vera-face-gel"
        }
    },

    "Plix": {
        "cleanser": {
            "product": "Jamun Active Acne Face Wash",
            "price_inr": 299,
            "image_url": "https://images.plixlife.com/products/484-da0975ffce0b4a57a03fc2e56ef0c0a5.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/jamun-cleanser-for-active-acne-treatment/484/4095"
        },
        "cleanser_oily": {
            "product": "Jamun Active Acne Face Wash",
            "price_inr": 299,
            "image_url": "https://images.plixlife.com/products/484-da0975ffce0b4a57a03fc2e56ef0c0a5.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/jamun-cleanser-for-active-acne-treatment/484/4095"
        },
        "cleanser_dry": {
            "product": "Avocado Ceramide Moisture Rush Juicy Cleanser",
            "price_inr": 349,
            "image_url": "",
            "buy_url": "https://www.plixlife.com/product/avocado-ceramide-moisture-rush-juicy-cleanser"
        },
        "cleanser_combination": {
            "product": "Pineapple De-Pigmentation Juicy Cleanser",
            "price_inr": 349,
            "image_url": "",
            "buy_url": "https://www.plixlife.com/product/pineapple-de-pigmentation-juicy-facewash-with-niacinamide-for-reducing-pigmentation/469"
        },
        "cleanser_normal": {
            "product": "Guava Juicy Cleanser Facewash",
            "price_inr": 349,
            "image_url": "",
            "buy_url": "https://www.plixlife.com/product/guava-juicy-cleanser-facewash/530"
        },
        "serum_oily": {
            "product": "Jamun 10% Niacinamide Face Serum",
            "price_inr": 549,
            "image_url": "",
            "buy_url": "https://www.plixlife.com/product/jamunserum/352"
        },
        "serum_dry": {
            "product": "Hydra Glow Face Serum",
            "price_inr": 549,
            "image_url": "https://images.plixlife.com/products/369-f8c16c6e1ec94a11974f05086c7d2dd9.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/guava-glow-dewy-serum"
        },
        "serum_combination": {
            "product": "10% Niacinamide Face Serum",
            "price_inr": 599,
            "image_url": "https://images.plixlife.com/products/352-44d9909e3c114277a85486461ec381a1.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/jamunserum/352"
        },
        "serum_normal": {
            "product": "Guava Glow Dewy Serum",
            "price_inr": 449,
            "image_url": "",
            "buy_url": "https://www.plixlife.com/product/10percent-vitamin-c-guava-glow-dewy-serum-with-hyaluronic-acid-and-1percent-pentavitin/455"
        },
        "moisturizer_oily": {
            "product": "Pineapple De-Pigmentation Gel Moisturizer",
            "price_inr": 399,
            "image_url": "https://images.plixlife.com/products/476-33c270575f5b444fafded7209020b546.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/pineapple-de-pigmentation-smoothie-moisturiser"
        },
        "moisturizer_dry": {
            "product": "Barrier Repair Gel Moisturizer",
            "price_inr": 399,
            "image_url": "https://images.plixlife.com/products/476-33c270575f5b444fafded7209020b546.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/collections/skin-care"
        },
        "moisturizer_combination": {
            "product": "Pineapple De-Pigmentation Smoothie Moisturiser",
            "price_inr": 399,
            "image_url": "",
            "buy_url": "https://www.plixlife.com/product/pineapple-de-pigmentation-smoothie-moisturiser/476"
        },
        "moisturizer_normal": {
            "product": "Guava Glow Smoothie Moisturizer",
            "price_inr": 550,
            "image_url": "",
            "buy_url": "https://www.plixlife.com/product/guava-glow-moisturizer/584"
        },
        "sunscreen": {
            "product": "Guava Glow Sunscreen SPF 50",
            "price_inr": 449,
            "image_url": "https://images.plixlife.com/products/477-630311a3cc8a418a8186192710e2d522.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/guava-glow-invisible-sunscreen-for-sun-protection-with-ceramide-11-suncat-de-for-reducing-photoageing-brightening-skin-tone"
        },
        "sunscreen_oily": {
            "product": "Guava Glow Invisible Sunscreen SPF 50",
            "price_inr": 449,
            "image_url": "https://images.plixlife.com/products/477-630311a3cc8a418a8186192710e2d522.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/guava-glow-invisible-sunscreen-for-sun-protection-with-ceramide-11-suncat-de-for-reducing-photoageing-brightening-skin-tone"
        },
        "sunscreen_dry": {
            "product": "Watermelon Dual Sunscreen SPF 50",
            "price_inr": 350,
            "image_url": "https://images.plixlife.com/products/1259-3c3095ac0e9f496dad153d34c314a957.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/watermelon-2-in-1-mosturizer-and-sunscreen/1259"
        },
        "sunscreen_combination": {
            "product": "Pineapple Advanced Depigmentation Dewy Sunscreen SPF 50",
            "price_inr": 399,
            "image_url": "https://images.plixlife.com/products/1213-7bba59b5ce21483292faa62dc64fc35d.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/pineapple-advanced-depigmentation-sunscreen-with-spf-50/1213"
        },
        "sunscreen_normal": {
            "product": "Guava Glow Invisible Sunscreen SPF 50",
            "price_inr": 449,
            "image_url": "",
            "buy_url": "https://www.plixlife.com/product/guava-glow-invisible-sunscreen-for-sun-protection-with-ceramide-11-suncat-de-for-reducing-photoageing-brightening-skin-tone/477"
        },
        "acne_treatment": {
            "product": "2% Salicylic Acid Face Serum",
            "price_inr": 549,
            "image_url": "https://images.plixlife.com/products/454-44d9909e3c114277a85486461ec381a1.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/jamun-active-acne-control-dewy-serum/454"
        },
        "dark_spot_serum": {
            "product": "10% Niacinamide Face Serum",
            "price_inr": 599,
            "image_url": "https://images.plixlife.com/products/352-44d9909e3c114277a85486461ec381a1.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/jamunserum/352"
        },
        "eye_cream": {
            "product": "Under Eye Brightening Gel",
            "price_inr": 449,
            "image_url": "https://images.plixlife.com/products/516-48360ef7dacd430bbf8d83e634458305.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/guava-under-eye-gel/516"
        },
        "hydrating_serum": {
            "product": "Hydra Glow Face Serum",
            "price_inr": 549,
            "image_url": "https://images.plixlife.com/products/369-f8c16c6e1ec94a11974f05086c7d2dd9.jpg?aio=w-1200",
            "buy_url": "https://www.plixlife.com/product/guava-glow-dewy-serum"
        }
    }
    }


_LIVE_META_CACHE = {}
_CACHE_TTL_SECONDS = 6 * 60 * 60
MAX_MORNING_STEPS = 4
MAX_EVENING_STEPS = 3
SKIN_TYPE_ALIASES = {
    "oily": "Oily",
    "dry": "Dry",
    "combination": "Combination",
    "normal": "Normal",
}

BRAND_CORE_ROUTINES = {
    brand: {
        "Oily": {
            "cleanser_key": "cleanser",
            "serum_key": "acne_treatment",
            "moisturizer_key": "moisturizer_oily",
            "sunscreen_key": "sunscreen",
            "serum_label": "Oil-control serum",
            "moisturizer_label": "Oil-free moisturizer",
            "sunscreen_label": "Lightweight sunscreen",
        },
        "Dry": {
            "cleanser_key": "cleanser",
            "serum_key": "hydrating_serum",
            "moisturizer_key": "moisturizer_dry",
            "sunscreen_key": "sunscreen",
            "serum_label": "Hydrating serum",
            "moisturizer_label": "Barrier moisturizer",
            "sunscreen_label": "Comfort sunscreen",
        },
        "Combination": {
            "cleanser_key": "cleanser",
            "serum_key": "dark_spot_serum",
            "moisturizer_key": "moisturizer_oily",
            "sunscreen_key": "sunscreen",
            "serum_label": "Balancing serum",
            "moisturizer_label": "Balanced moisturizer",
            "sunscreen_label": "Daily sunscreen",
        },
        "Normal": {
            "cleanser_key": "cleanser",
            "serum_key": "hydrating_serum",
            "moisturizer_key": "moisturizer_dry",
            "sunscreen_key": "sunscreen",
            "serum_label": "Daily serum",
            "moisturizer_label": "Daily moisturizer",
            "sunscreen_label": "Daily sunscreen",
        },
    }
    for brand in ALL_BRANDS
}

BRAND_CORE_ROUTINES["Mamaearth"] = {
    "Oily": {
        "cleanser_key": "cleanser_oily",
        "serum_key": "serum_oily",
        "moisturizer_key": "moisturizer_oily",
        "sunscreen_key": "sunscreen_oily",
        "serum_label": "Oil-control serum",
        "moisturizer_label": "Oil-free moisturizer",
        "sunscreen_label": "Lightweight sunscreen",
    },
    "Dry": {
        "cleanser_key": "cleanser_dry",
        "serum_key": "serum_dry",
        "moisturizer_key": "moisturizer_dry",
        "sunscreen_key": "sunscreen_dry",
        "serum_label": "Hydrating serum",
        "moisturizer_label": "Barrier moisturizer",
        "sunscreen_label": "Comfort sunscreen",
    },
    "Combination": {
        "cleanser_key": "cleanser_combination",
        "serum_key": "serum_combination",
        "moisturizer_key": "moisturizer_combination",
        "sunscreen_key": "sunscreen_combination",
        "serum_label": "Balancing serum",
        "moisturizer_label": "Balanced moisturizer",
        "sunscreen_label": "Daily sunscreen",
    },
    "Normal": {
        "cleanser_key": "cleanser_normal",
        "serum_key": "serum_normal",
        "moisturizer_key": "moisturizer_normal",
        "sunscreen_key": "sunscreen_normal",
        "serum_label": "Daily serum",
        "moisturizer_label": "Daily moisturizer",
        "sunscreen_label": "Daily sunscreen",
    },
}

BRAND_CORE_ROUTINES["Foxtale"] = {
    "Oily": {
        "cleanser_key": "cleanser_oily",
        "serum_key": "serum_oily",
        "moisturizer_key": "moisturizer_oily",
        "sunscreen_key": "sunscreen_oily",
        "serum_label": "Oil-control serum",
        "moisturizer_label": "Oil-control moisturizer",
        "sunscreen_label": "Gel sunscreen",
    },
    "Dry": {
        "cleanser_key": "cleanser_dry",
        "serum_key": "serum_dry",
        "moisturizer_key": "moisturizer_dry",
        "sunscreen_key": "sunscreen_dry",
        "serum_label": "Repair serum",
        "moisturizer_label": "Nourishing moisturizer",
        "sunscreen_label": "Dewy sunscreen",
    },
    "Combination": {
        "cleanser_key": "cleanser_combination",
        "serum_key": "serum_combination",
        "moisturizer_key": "moisturizer_combination",
        "sunscreen_key": "sunscreen_combination",
        "serum_label": "Spot-correcting serum",
        "moisturizer_label": "Balanced moisturizer",
        "sunscreen_label": "Matte sunscreen",
    },
    "Normal": {
        "cleanser_key": "cleanser_normal",
        "serum_key": "serum_normal",
        "moisturizer_key": "moisturizer_normal",
        "sunscreen_key": "sunscreen_normal",
        "serum_label": "Glow serum",
        "moisturizer_label": "Glow moisturizer",
        "sunscreen_label": "Daily glow sunscreen",
    },
}

BRAND_CORE_ROUTINES["Dot & Key"] = {
    "Oily": {
        "cleanser_key": "cleanser_oily",
        "serum_key": "serum_oily",
        "moisturizer_key": "moisturizer_oily",
        "sunscreen_key": "sunscreen_oily",
        "serum_label": "Oil-control serum",
        "moisturizer_label": "Oil-free moisturizer",
        "sunscreen_label": "Mattifying sunscreen",
    },
    "Dry": {
        "cleanser_key": "cleanser_dry",
        "serum_key": "serum_dry",
        "moisturizer_key": "moisturizer_dry",
        "sunscreen_key": "sunscreen_dry",
        "serum_label": "Barrier serum",
        "moisturizer_label": "Barrier moisturizer",
        "sunscreen_label": "Barrier sunscreen",
    },
    "Combination": {
        "cleanser_key": "cleanser_combination",
        "serum_key": "serum_combination",
        "moisturizer_key": "moisturizer_combination",
        "sunscreen_key": "sunscreen_combination",
        "serum_label": "Balancing serum",
        "moisturizer_label": "Balanced moisturizer",
        "sunscreen_label": "Cooling sunscreen",
    },
    "Normal": {
        "cleanser_key": "cleanser_normal",
        "serum_key": "serum_normal",
        "moisturizer_key": "moisturizer_normal",
        "sunscreen_key": "sunscreen_normal",
        "serum_label": "Glow serum",
        "moisturizer_label": "Glow moisturizer",
        "sunscreen_label": "Glow sunscreen",
    },
}

BRAND_CORE_ROUTINES["The Derma Co"] = {
    "Oily": {
        "cleanser_key": "cleanser_oily",
        "serum_key": "serum_oily",
        "moisturizer_key": "moisturizer_oily",
        "sunscreen_key": "sunscreen_oily",
        "serum_label": "Anti-acne serum",
        "moisturizer_label": "Oil-free moisturizer",
        "sunscreen_label": "Matte sunscreen",
    },
    "Dry": {
        "cleanser_key": "cleanser_dry",
        "serum_key": "serum_dry",
        "moisturizer_key": "moisturizer_dry",
        "sunscreen_key": "sunscreen_dry",
        "serum_label": "Hydrating serum",
        "moisturizer_label": "Barrier moisturizer",
        "sunscreen_label": "Hydrating sunscreen",
    },
    "Combination": {
        "cleanser_key": "cleanser_combination",
        "serum_key": "serum_combination",
        "moisturizer_key": "moisturizer_combination",
        "sunscreen_key": "sunscreen_combination",
        "serum_label": "Pore-minimizing serum",
        "moisturizer_label": "Pore-minimizing moisturizer",
        "sunscreen_label": "Priming sunscreen",
    },
    "Normal": {
        "cleanser_key": "cleanser_normal",
        "serum_key": "serum_normal",
        "moisturizer_key": "moisturizer_normal",
        "sunscreen_key": "sunscreen_normal",
        "serum_label": "Radiance serum",
        "moisturizer_label": "Daily moisturizer",
        "sunscreen_label": "Radiance sunscreen",
    },
}

BRAND_CORE_ROUTINES["Minimalist"] = {
    "Oily": {
        "cleanser_key": "cleanser_oily",
        "serum_key": "serum_oily",
        "moisturizer_key": "moisturizer_oily",
        "sunscreen_key": "sunscreen_oily",
        "serum_label": "Oil-balancing serum",
        "moisturizer_label": "Lightweight moisturizer",
        "sunscreen_label": "High-protection sunscreen",
    },
    "Dry": {
        "cleanser_key": "cleanser_dry",
        "serum_key": "serum_dry",
        "moisturizer_key": "moisturizer_dry",
        "sunscreen_key": "sunscreen_dry",
        "serum_label": "Repair serum",
        "moisturizer_label": "Nourishing moisturizer",
        "sunscreen_label": "Comfort sunscreen",
    },
    "Combination": {
        "cleanser_key": "cleanser_combination",
        "serum_key": "serum_combination",
        "moisturizer_key": "moisturizer_combination",
        "sunscreen_key": "sunscreen_combination",
        "serum_label": "Multi-repair serum",
        "moisturizer_label": "Balanced moisturizer",
        "sunscreen_label": "Fluid sunscreen",
    },
    "Normal": {
        "cleanser_key": "cleanser_normal",
        "serum_key": "serum_normal",
        "moisturizer_key": "moisturizer_normal",
        "sunscreen_key": "sunscreen_normal",
        "serum_label": "Brightening serum",
        "moisturizer_label": "Daily moisturizer",
        "sunscreen_label": "Daily sunscreen",
    },
}

BRAND_CORE_ROUTINES["Cetaphil"] = {
    "Oily": {
        "cleanser_key": "cleanser_oily",
        "serum_key": "serum_oily",
        "moisturizer_key": "moisturizer_oily",
        "sunscreen_key": "sunscreen_oily",
        "serum_label": "Acne-control serum",
        "moisturizer_label": "Daily lotion",
        "sunscreen_label": "Light gel sunscreen",
    },
    "Dry": {
        "cleanser_key": "cleanser_dry",
        "serum_key": "serum_dry",
        "moisturizer_key": "moisturizer_dry",
        "sunscreen_key": "sunscreen_dry",
        "serum_label": "Hydration serum",
        "moisturizer_label": "Rich moisturizer",
        "sunscreen_label": "Protective sunscreen",
    },
    "Combination": {
        "cleanser_key": "cleanser_combination",
        "serum_key": "serum_combination",
        "moisturizer_key": "moisturizer_combination",
        "sunscreen_key": "sunscreen_combination",
        "serum_label": "Tone-correcting serum",
        "moisturizer_label": "Hydrating lotion",
        "sunscreen_label": "Day protection cream",
    },
    "Normal": {
        "cleanser_key": "cleanser_normal",
        "serum_key": "serum_normal",
        "moisturizer_key": "moisturizer_normal",
        "sunscreen_key": "sunscreen_normal",
        "serum_label": "Radiance serum",
        "moisturizer_label": "Day cream",
        "sunscreen_label": "Daily sunscreen",
    },
}

BRAND_CORE_ROUTINES["Himalaya"] = {
    "Oily": {
        "cleanser_key": "cleanser_oily",
        "serum_key": None,
        "moisturizer_key": "moisturizer_oily",
        "sunscreen_key": "sunscreen_oily",
        "serum_label": "Oil-control serum",
        "moisturizer_label": "Oil-free moisturizer",
        "sunscreen_label": "Ultra-light sunscreen",
    },
    "Dry": {
        "cleanser_key": "cleanser_dry",
        "serum_key": "serum_dry",
        "moisturizer_key": "moisturizer_dry",
        "sunscreen_key": "sunscreen_dry",
        "serum_label": "Hydrating serum",
        "moisturizer_label": "Nourishing moisturizer",
        "sunscreen_label": "Comfort sunscreen",
    },
    "Combination": {
        "cleanser_key": "cleanser_combination",
        "serum_key": "serum_combination",
        "moisturizer_key": "moisturizer_combination",
        "sunscreen_key": "sunscreen_combination",
        "serum_label": "Balancing serum",
        "moisturizer_label": "Balanced moisturizer",
        "sunscreen_label": "Daily sunscreen",
    },
    "Normal": {
        "cleanser_key": "cleanser_normal",
        "serum_key": "serum_normal",
        "moisturizer_key": "moisturizer_normal",
        "sunscreen_key": "sunscreen_normal",
        "serum_label": "Glow serum",
        "moisturizer_label": "Daily moisturizer",
        "sunscreen_label": "Daily sunscreen",
    },
}

BRAND_CORE_ROUTINES["Plix"] = {
    "Oily": {
        "cleanser_key": "cleanser_oily",
        "serum_key": "serum_oily",
        "moisturizer_key": "moisturizer_oily",
        "sunscreen_key": "sunscreen_oily",
        "serum_label": "Acne-control serum",
        "moisturizer_label": "Gel moisturizer",
        "sunscreen_label": "Invisible sunscreen",
    },
    "Dry": {
        "cleanser_key": "cleanser_dry",
        "serum_key": "serum_dry",
        "moisturizer_key": "moisturizer_dry",
        "sunscreen_key": "sunscreen_dry",
        "serum_label": "Hydra serum",
        "moisturizer_label": "Barrier moisturizer",
        "sunscreen_label": "Dewy sunscreen",
    },
    "Combination": {
        "cleanser_key": "cleanser_combination",
        "serum_key": "serum_combination",
        "moisturizer_key": "moisturizer_combination",
        "sunscreen_key": "sunscreen_combination",
        "serum_label": "Tone-correcting serum",
        "moisturizer_label": "Balanced moisturizer",
        "sunscreen_label": "Brightening sunscreen",
    },
    "Normal": {
        "cleanser_key": "cleanser_normal",
        "serum_key": "serum_normal",
        "moisturizer_key": "moisturizer_normal",
        "sunscreen_key": "sunscreen_normal",
        "serum_label": "Glow serum",
        "moisturizer_label": "Daily moisturizer",
        "sunscreen_label": "Daily sunscreen",
    },
}

CONCERN_CORE_SELECTIONS = {
    "Clear Skin": {
        "Oily": {
            "cleanser_candidates": ("cleanser_normal", "cleanser_oily", "cleanser"),
            "moisturizer_candidates": ("moisturizer_normal", "moisturizer_oily"),
            "sunscreen_candidates": ("sunscreen_normal", "sunscreen_oily", "sunscreen"),
        },
        "Dry": {
            "cleanser_candidates": ("cleanser_dry", "cleanser_normal", "cleanser"),
            "moisturizer_candidates": ("moisturizer_dry", "moisturizer_normal"),
            "sunscreen_candidates": ("sunscreen_dry", "sunscreen_normal", "sunscreen"),
        },
        "Combination": {
            "cleanser_candidates": ("cleanser_normal", "cleanser_combination", "cleanser"),
            "moisturizer_candidates": ("moisturizer_combination", "moisturizer_normal"),
            "sunscreen_candidates": ("sunscreen_normal", "sunscreen_combination", "sunscreen"),
        },
        "Normal": {
            "cleanser_candidates": ("cleanser_normal", "cleanser"),
            "moisturizer_candidates": ("moisturizer_normal", "moisturizer_dry"),
            "sunscreen_candidates": ("sunscreen_normal", "sunscreen"),
        },
    },
    "Pimples / Acne": {
        "Oily": {
            "cleanser_candidates": ("cleanser_oily", "cleanser_combination", "cleanser"),
            "moisturizer_candidates": ("moisturizer_oily", "moisturizer_combination"),
            "sunscreen_candidates": ("sunscreen_oily", "sunscreen_combination", "sunscreen"),
        },
        "Dry": {
            "cleanser_candidates": ("cleanser_combination", "cleanser_dry", "cleanser"),
            "moisturizer_candidates": ("moisturizer_dry", "moisturizer_oily"),
            "sunscreen_candidates": ("sunscreen_dry", "sunscreen_oily", "sunscreen"),
        },
        "Combination": {
            "cleanser_candidates": ("cleanser_combination", "cleanser_oily", "cleanser"),
            "moisturizer_candidates": ("moisturizer_combination", "moisturizer_oily"),
            "sunscreen_candidates": ("sunscreen_combination", "sunscreen_oily", "sunscreen"),
        },
        "Normal": {
            "cleanser_candidates": ("cleanser_oily", "cleanser_normal", "cleanser"),
            "moisturizer_candidates": ("moisturizer_normal", "moisturizer_oily"),
            "sunscreen_candidates": ("sunscreen_normal", "sunscreen_oily", "sunscreen"),
        },
    },
    "Dark Spots": {
        "Oily": {
            "cleanser_candidates": ("cleanser_combination", "cleanser_normal", "cleanser_oily", "cleanser"),
            "moisturizer_candidates": ("moisturizer_combination", "moisturizer_oily", "moisturizer_normal"),
            "sunscreen_candidates": ("sunscreen_combination", "sunscreen_normal", "sunscreen_oily", "sunscreen"),
        },
        "Dry": {
            "cleanser_candidates": ("cleanser_normal", "cleanser_dry", "cleanser"),
            "moisturizer_candidates": ("moisturizer_dry", "moisturizer_normal"),
            "sunscreen_candidates": ("sunscreen_normal", "sunscreen_dry", "sunscreen"),
        },
        "Combination": {
            "cleanser_candidates": ("cleanser_combination", "cleanser_normal", "cleanser"),
            "moisturizer_candidates": ("moisturizer_combination", "moisturizer_normal"),
            "sunscreen_candidates": ("sunscreen_combination", "sunscreen_normal", "sunscreen"),
        },
        "Normal": {
            "cleanser_candidates": ("cleanser_normal", "cleanser"),
            "moisturizer_candidates": ("moisturizer_normal", "moisturizer_combination"),
            "sunscreen_candidates": ("sunscreen_normal", "sunscreen_combination", "sunscreen"),
        },
    },
    "Dark Circles": {
        "Oily": {
            "cleanser_candidates": ("cleanser_normal", "cleanser_dry", "cleanser_oily", "cleanser"),
            "moisturizer_candidates": ("moisturizer_normal", "moisturizer_dry", "moisturizer_oily"),
            "sunscreen_candidates": ("sunscreen_normal", "sunscreen_dry", "sunscreen_oily", "sunscreen"),
        },
        "Dry": {
            "cleanser_candidates": ("cleanser_dry", "cleanser_normal", "cleanser"),
            "moisturizer_candidates": ("moisturizer_dry", "moisturizer_normal"),
            "sunscreen_candidates": ("sunscreen_dry", "sunscreen_normal", "sunscreen"),
        },
        "Combination": {
            "cleanser_candidates": ("cleanser_dry", "cleanser_normal", "cleanser_combination", "cleanser"),
            "moisturizer_candidates": ("moisturizer_dry", "moisturizer_combination", "moisturizer_normal"),
            "sunscreen_candidates": ("sunscreen_dry", "sunscreen_normal", "sunscreen_combination", "sunscreen"),
        },
        "Normal": {
            "cleanser_candidates": ("cleanser_normal", "cleanser_dry", "cleanser"),
            "moisturizer_candidates": ("moisturizer_normal", "moisturizer_dry"),
            "sunscreen_candidates": ("sunscreen_normal", "sunscreen_dry", "sunscreen"),
        },
    },
}

CONCERN_PRODUCT_SELECTIONS = {
    "Clear Skin": {
        "Oily": [
            {"candidate_keys": ("serum_oily", "hydrating_serum"), "label": "Daily balance serum"},
        ],
        "Dry": [
            {"candidate_keys": ("serum_dry", "hydrating_serum"), "label": "Daily hydration serum"},
        ],
        "Combination": [
            {"candidate_keys": ("serum_combination", "hydrating_serum"), "label": "Daily balance serum"},
        ],
        "Normal": [
            {"candidate_keys": ("serum_normal", "hydrating_serum"), "label": "Daily glow serum"},
        ],
        "default": [
            {"candidate_keys": ("hydrating_serum",), "label": "Daily serum"},
        ],
    },
    "Pimples / Acne": {
        "Oily": [
            {"candidate_keys": ("serum_oily", "acne_treatment"), "label": "Acne-control serum"},
            {"candidate_keys": ("acne_treatment",), "label": "Spot treatment"},
        ],
        "Dry": [
            {"candidate_keys": ("serum_dry", "acne_treatment"), "label": "Barrier-support serum"},
            {"candidate_keys": ("acne_treatment",), "label": "Spot treatment"},
        ],
        "Combination": [
            {"candidate_keys": ("serum_combination", "acne_treatment"), "label": "Balancing serum"},
            {"candidate_keys": ("acne_treatment",), "label": "Spot treatment"},
        ],
        "Normal": [
            {"candidate_keys": ("serum_normal", "acne_treatment"), "label": "Clarifying serum"},
            {"candidate_keys": ("acne_treatment",), "label": "Spot treatment"},
        ],
        "default": [
            {"candidate_keys": ("acne_treatment",), "label": "Treatment serum"},
        ],
    },
    "Dark Spots": {
        "Oily": [
            {"candidate_keys": ("serum_oily", "dark_spot_serum"), "label": "Tone-correcting serum"},
            {"candidate_keys": ("dark_spot_serum",), "label": "Dark spot serum"},
        ],
        "Dry": [
            {"candidate_keys": ("serum_dry", "dark_spot_serum"), "label": "Barrier-support serum"},
            {"candidate_keys": ("dark_spot_serum",), "label": "Dark spot serum"},
        ],
        "Combination": [
            {"candidate_keys": ("serum_combination", "dark_spot_serum"), "label": "Tone-correcting serum"},
            {"candidate_keys": ("dark_spot_serum",), "label": "Dark spot serum"},
        ],
        "Normal": [
            {"candidate_keys": ("serum_normal", "dark_spot_serum"), "label": "Brightening serum"},
            {"candidate_keys": ("dark_spot_serum",), "label": "Dark spot serum"},
        ],
        "default": [
            {"candidate_keys": ("dark_spot_serum",), "label": "Dark spot serum"},
        ],
    },
    "Dark Circles": {
        "Oily": [
            {"candidate_keys": ("serum_oily", "eye_cream"), "label": "Lightweight prep serum"},
            {"candidate_keys": ("eye_cream",), "label": "Under-eye treatment"},
        ],
        "Dry": [
            {"candidate_keys": ("serum_dry", "eye_cream"), "label": "Hydration serum"},
            {"candidate_keys": ("eye_cream",), "label": "Under-eye treatment"},
        ],
        "Combination": [
            {"candidate_keys": ("serum_combination", "eye_cream"), "label": "Balancing serum"},
            {"candidate_keys": ("eye_cream",), "label": "Under-eye treatment"},
        ],
        "Normal": [
            {"candidate_keys": ("serum_normal", "eye_cream"), "label": "Brightening serum"},
            {"candidate_keys": ("eye_cream",), "label": "Under-eye treatment"},
        ],
        "default": [
            {"candidate_keys": ("eye_cream",), "label": "Under-eye treatment"},
        ],
    },
}

BRAND_CONCERN_PRODUCT_SELECTIONS = {
    "Mamaearth": {
        "Clear Skin": {
            "Oily": [{"candidate_keys": ("serum_oily",), "label": "Clarity serum"}],
            "Dry": [{"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydra-glow serum"}],
            "Combination": [{"candidate_keys": ("serum_combination",), "label": "Tone-balancing serum"}],
            "Normal": [{"candidate_keys": ("serum_normal", "hydrating_serum"), "label": "Glow serum"}],
        },
        "Pimples / Acne": {
            "Oily": [{"candidate_keys": ("serum_oily", "acne_treatment"), "label": "Clarifying serum"}, {"candidate_keys": ("acne_treatment",), "label": "Tea tree spot care"}],
            "Dry": [{"candidate_keys": ("acne_treatment", "serum_dry"), "label": "Acne spot care"}, {"candidate_keys": ("serum_dry",), "label": "Hydration support serum"}],
            "Combination": [{"candidate_keys": ("serum_combination", "acne_treatment"), "label": "Blemish-correcting serum"}, {"candidate_keys": ("acne_treatment",), "label": "Tea tree spot care"}],
            "Normal": [{"candidate_keys": ("serum_oily", "acne_treatment"), "label": "Purifying serum"}, {"candidate_keys": ("acne_treatment",), "label": "Tea tree spot care"}],
        },
        "Dark Spots": {
            "Oily": [{"candidate_keys": ("dark_spot_serum", "serum_oily"), "label": "Dark mark corrector"}, {"candidate_keys": ("serum_oily",), "label": "Oil-balancing serum"}],
            "Dry": [{"candidate_keys": ("dark_spot_serum", "serum_dry"), "label": "Dark mark corrector"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydra support serum"}],
            "Combination": [{"candidate_keys": ("dark_spot_serum", "serum_combination"), "label": "Tone-correcting serum"}],
            "Normal": [{"candidate_keys": ("dark_spot_serum", "serum_normal"), "label": "Brightening correction serum"}, {"candidate_keys": ("serum_normal",), "label": "Glow support serum"}],
        },
        "Dark Circles": {
            "Oily": [{"candidate_keys": ("eye_cream",), "label": "Under-eye treatment"}, {"candidate_keys": ("serum_oily",), "label": "Light prep serum"}],
            "Dry": [{"candidate_keys": ("eye_cream",), "label": "Under-eye treatment"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydration prep serum"}],
            "Combination": [{"candidate_keys": ("eye_cream",), "label": "Under-eye treatment"}, {"candidate_keys": ("serum_combination",), "label": "Tone-balancing serum"}],
            "Normal": [{"candidate_keys": ("eye_cream",), "label": "Under-eye treatment"}, {"candidate_keys": ("serum_normal",), "label": "Brightening prep serum"}],
        },
    },
    "Foxtale": {
        "Clear Skin": {
            "Oily": [{"candidate_keys": ("serum_oily",), "label": "Niacinamide daily serum"}],
            "Dry": [{"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydrating daily serum"}],
            "Combination": [{"candidate_keys": ("serum_combination",), "label": "Tone-evening daily serum"}],
            "Normal": [{"candidate_keys": ("serum_normal",), "label": "Vitamin C daily serum"}],
        },
        "Pimples / Acne": {
            "Oily": [{"candidate_keys": ("serum_oily",), "label": "Niacinamide clarifying serum"}, {"candidate_keys": ("acne_treatment",), "label": "Acne spot corrector"}],
            "Dry": [{"candidate_keys": ("acne_treatment",), "label": "Acne spot corrector"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Barrier support serum"}],
            "Combination": [{"candidate_keys": ("serum_oily", "serum_combination"), "label": "Clarifying serum"}, {"candidate_keys": ("acne_treatment",), "label": "Acne spot corrector"}],
            "Normal": [{"candidate_keys": ("acne_treatment",), "label": "Acne spot corrector"}, {"candidate_keys": ("serum_normal",), "label": "Brightening support serum"}],
        },
        "Dark Spots": {
            "Oily": [{"candidate_keys": ("dark_spot_serum",), "label": "Tranexamic correction serum"}, {"candidate_keys": ("serum_oily",), "label": "Niacinamide balancing serum"}],
            "Dry": [{"candidate_keys": ("dark_spot_serum",), "label": "Tranexamic correction serum"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydration support serum"}],
            "Combination": [{"candidate_keys": ("dark_spot_serum", "serum_combination"), "label": "Tranexamic correction serum"}],
            "Normal": [{"candidate_keys": ("dark_spot_serum",), "label": "Spot-fading serum"}, {"candidate_keys": ("serum_normal",), "label": "Vitamin C glow serum"}],
        },
        "Dark Circles": {
            "Oily": [{"candidate_keys": ("eye_cream",), "label": "Under-eye gel"}, {"candidate_keys": ("serum_oily",), "label": "Lightweight prep serum"}],
            "Dry": [{"candidate_keys": ("eye_cream",), "label": "Under-eye gel"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydrating prep serum"}],
            "Combination": [{"candidate_keys": ("eye_cream",), "label": "Under-eye gel"}, {"candidate_keys": ("serum_combination",), "label": "Tone-evening prep serum"}],
            "Normal": [{"candidate_keys": ("eye_cream",), "label": "Under-eye gel"}, {"candidate_keys": ("serum_normal",), "label": "Brightening prep serum"}],
        },
    },
    "Dot & Key": {
        "Clear Skin": {
            "Oily": [{"candidate_keys": ("serum_oily",), "label": "Cica balancing serum"}],
            "Dry": [{"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Probiotic hydration serum"}],
            "Combination": [{"candidate_keys": ("serum_combination",), "label": "Niacinamide balancing serum"}],
            "Normal": [{"candidate_keys": ("serum_normal",), "label": "Vitamin C glow serum"}],
        },
        "Pimples / Acne": {
            "Oily": [{"candidate_keys": ("acne_treatment", "serum_oily"), "label": "Salicylic acne serum"}],
            "Dry": [{"candidate_keys": ("acne_treatment",), "label": "Targeted acne serum"}, {"candidate_keys": ("serum_dry", "hydrating_serum"), "label": "Barrier support serum"}],
            "Combination": [{"candidate_keys": ("serum_oily", "acne_treatment"), "label": "Blemish-control serum"}, {"candidate_keys": ("serum_combination",), "label": "Niacinamide support serum"}],
            "Normal": [{"candidate_keys": ("acne_treatment",), "label": "Targeted acne serum"}, {"candidate_keys": ("serum_normal",), "label": "Radiance support serum"}],
        },
        "Dark Spots": {
            "Oily": [{"candidate_keys": ("serum_combination", "dark_spot_serum"), "label": "Niacinamide spot serum"}, {"candidate_keys": ("dark_spot_serum",), "label": "Vitamin C brightening serum"}],
            "Dry": [{"candidate_keys": ("dark_spot_serum",), "label": "Vitamin C brightening serum"}, {"candidate_keys": ("serum_dry", "hydrating_serum"), "label": "Barrier support serum"}],
            "Combination": [{"candidate_keys": ("serum_combination", "dark_spot_serum"), "label": "Spotless skin serum"}],
            "Normal": [{"candidate_keys": ("dark_spot_serum", "serum_normal"), "label": "Brightening serum"}],
        },
        "Dark Circles": {
            "Oily": [{"candidate_keys": ("eye_cream",), "label": "Caffeine eye cream"}, {"candidate_keys": ("serum_oily",), "label": "Oil-light prep serum"}],
            "Dry": [{"candidate_keys": ("eye_cream",), "label": "Caffeine eye cream"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydrating prep serum"}],
            "Combination": [{"candidate_keys": ("eye_cream",), "label": "Caffeine eye cream"}, {"candidate_keys": ("serum_combination",), "label": "Tone-evening prep serum"}],
            "Normal": [{"candidate_keys": ("eye_cream",), "label": "Caffeine eye cream"}, {"candidate_keys": ("serum_normal",), "label": "Brightening prep serum"}],
        },
    },
    "The Derma Co": {
        "Clear Skin": {
            "Oily": [{"candidate_keys": ("serum_oily",), "label": "Anti-acne daily serum"}],
            "Dry": [{"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hyaluronic daily serum"}],
            "Combination": [{"candidate_keys": ("serum_combination",), "label": "Pore-refining serum"}],
            "Normal": [{"candidate_keys": ("serum_normal",), "label": "Radiance daily serum"}],
        },
        "Pimples / Acne": {
            "Oily": [{"candidate_keys": ("serum_oily", "acne_treatment"), "label": "Sali-cinamide serum"}, {"candidate_keys": ("acne_treatment",), "label": "2% salicylic serum"}],
            "Dry": [{"candidate_keys": ("acne_treatment",), "label": "2% salicylic serum"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydration support serum"}],
            "Combination": [{"candidate_keys": ("serum_combination", "serum_oily"), "label": "Pore-refining serum"}, {"candidate_keys": ("acne_treatment",), "label": "Targeted acne serum"}],
            "Normal": [{"candidate_keys": ("acne_treatment",), "label": "Targeted acne serum"}, {"candidate_keys": ("serum_normal",), "label": "Radiance support serum"}],
        },
        "Dark Spots": {
            "Oily": [{"candidate_keys": ("dark_spot_serum",), "label": "Kojic correction serum"}, {"candidate_keys": ("serum_oily",), "label": "Oil-balancing serum"}],
            "Dry": [{"candidate_keys": ("dark_spot_serum",), "label": "Kojic correction serum"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydration support serum"}],
            "Combination": [{"candidate_keys": ("dark_spot_serum", "serum_combination"), "label": "Pigmentation correction serum"}],
            "Normal": [{"candidate_keys": ("dark_spot_serum",), "label": "Pigmentation correction serum"}, {"candidate_keys": ("serum_normal",), "label": "Radiance support serum"}],
        },
        "Dark Circles": {
            "Oily": [{"candidate_keys": ("eye_cream",), "label": "Caffeine under-eye serum"}, {"candidate_keys": ("serum_oily",), "label": "Light prep serum"}],
            "Dry": [{"candidate_keys": ("eye_cream",), "label": "Caffeine under-eye serum"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydrating prep serum"}],
            "Combination": [{"candidate_keys": ("eye_cream",), "label": "Caffeine under-eye serum"}, {"candidate_keys": ("serum_combination",), "label": "Pore-refining prep serum"}],
            "Normal": [{"candidate_keys": ("eye_cream",), "label": "Caffeine under-eye serum"}, {"candidate_keys": ("serum_normal",), "label": "Radiance prep serum"}],
        },
    },
    "Minimalist": {
        "Clear Skin": {
            "Oily": [{"candidate_keys": ("serum_oily",), "label": "Niacinamide daily serum"}],
            "Dry": [{"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hyaluronic daily serum"}],
            "Combination": [{"candidate_keys": ("serum_combination",), "label": "Repair daily serum"}],
            "Normal": [{"candidate_keys": ("serum_normal",), "label": "Vitamin C daily serum"}],
        },
        "Pimples / Acne": {
            "Oily": [{"candidate_keys": ("acne_treatment", "serum_oily"), "label": "2% salicylic acne serum"}, {"candidate_keys": ("serum_oily",), "label": "Niacinamide support serum"}],
            "Dry": [{"candidate_keys": ("acne_treatment",), "label": "2% salicylic acne serum"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydration support serum"}],
            "Combination": [{"candidate_keys": ("serum_oily", "serum_combination"), "label": "Niacinamide balancing serum"}, {"candidate_keys": ("acne_treatment",), "label": "Targeted acne serum"}],
            "Normal": [{"candidate_keys": ("acne_treatment",), "label": "Targeted acne serum"}, {"candidate_keys": ("serum_normal",), "label": "Brightening support serum"}],
        },
        "Dark Spots": {
            "Oily": [{"candidate_keys": ("dark_spot_serum", "serum_oily"), "label": "Niacinamide dark spot serum"}],
            "Dry": [{"candidate_keys": ("dark_spot_serum",), "label": "Niacinamide dark spot serum"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydration support serum"}],
            "Combination": [{"candidate_keys": ("serum_combination", "dark_spot_serum"), "label": "Repair correction serum"}],
            "Normal": [{"candidate_keys": ("serum_normal", "dark_spot_serum"), "label": "Vitamin C brightening serum"}, {"candidate_keys": ("dark_spot_serum",), "label": "Niacinamide support serum"}],
        },
        "Dark Circles": {
            "Oily": [{"candidate_keys": ("eye_cream",), "label": "Vitamin K eye cream"}, {"candidate_keys": ("serum_oily",), "label": "Light prep serum"}],
            "Dry": [{"candidate_keys": ("eye_cream",), "label": "Vitamin K eye cream"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydrating prep serum"}],
            "Combination": [{"candidate_keys": ("eye_cream",), "label": "Vitamin K eye cream"}, {"candidate_keys": ("serum_combination",), "label": "Repair prep serum"}],
            "Normal": [{"candidate_keys": ("eye_cream",), "label": "Vitamin K eye cream"}, {"candidate_keys": ("serum_normal",), "label": "Brightening prep serum"}],
        },
    },
    "Cetaphil": {
        "Clear Skin": {
            "Oily": [{"candidate_keys": ("serum_oily",), "label": "Gentle clear serum"}],
            "Dry": [{"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydration daily serum"}],
            "Combination": [{"candidate_keys": ("serum_combination",), "label": "Radiance daily serum"}],
            "Normal": [{"candidate_keys": ("serum_normal",), "label": "Radiance daily serum"}],
        },
        "Pimples / Acne": {
            "Oily": [{"candidate_keys": ("acne_treatment", "serum_oily"), "label": "Triple-action acne serum"}],
            "Dry": [{"candidate_keys": ("acne_treatment",), "label": "Gentle clear acne serum"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydration support serum"}],
            "Combination": [{"candidate_keys": ("acne_treatment", "serum_oily"), "label": "Acne-control serum"}, {"candidate_keys": ("serum_combination",), "label": "Radiance support serum"}],
            "Normal": [{"candidate_keys": ("acne_treatment",), "label": "Gentle clear acne serum"}, {"candidate_keys": ("serum_normal",), "label": "Radiance support serum"}],
        },
        "Dark Spots": {
            "Oily": [{"candidate_keys": ("dark_spot_serum", "serum_combination"), "label": "Radiance correction serum"}],
            "Dry": [{"candidate_keys": ("dark_spot_serum",), "label": "Radiance correction serum"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydration support serum"}],
            "Combination": [{"candidate_keys": ("dark_spot_serum", "serum_combination"), "label": "Tone-correcting serum"}],
            "Normal": [{"candidate_keys": ("dark_spot_serum", "serum_normal"), "label": "Bright radiance serum"}],
        },
        "Dark Circles": {
            "Oily": [{"candidate_keys": ("eye_cream",), "label": "Hydrating eye gel-cream"}, {"candidate_keys": ("serum_oily",), "label": "Light prep serum"}],
            "Dry": [{"candidate_keys": ("eye_cream",), "label": "Hydrating eye gel-cream"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydration prep serum"}],
            "Combination": [{"candidate_keys": ("eye_cream",), "label": "Hydrating eye gel-cream"}, {"candidate_keys": ("serum_combination",), "label": "Tone prep serum"}],
            "Normal": [{"candidate_keys": ("eye_cream",), "label": "Hydrating eye gel-cream"}, {"candidate_keys": ("serum_normal",), "label": "Radiance prep serum"}],
        },
    },
    "Himalaya": {
        "Clear Skin": {
            "Oily": [{"candidate_keys": ("serum_oily",), "label": "Clarifying daily serum"}],
            "Dry": [{"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Aloe hydration serum"}],
            "Combination": [{"candidate_keys": ("serum_combination",), "label": "Turmeric glow serum"}],
            "Normal": [{"candidate_keys": ("serum_normal",), "label": "Vitamin C glow serum"}],
        },
        "Pimples / Acne": {
            "Oily": [{"candidate_keys": ("acne_treatment", "serum_oily"), "label": "Anti-acne cream"}, {"candidate_keys": ("serum_oily",), "label": "Clarifying serum"}],
            "Dry": [{"candidate_keys": ("acne_treatment",), "label": "Anti-acne cream"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Aloe support serum"}],
            "Combination": [{"candidate_keys": ("acne_treatment",), "label": "Anti-acne cream"}, {"candidate_keys": ("serum_combination",), "label": "Turmeric support serum"}],
            "Normal": [{"candidate_keys": ("acne_treatment",), "label": "Anti-acne cream"}, {"candidate_keys": ("serum_normal",), "label": "Glow support serum"}],
        },
        "Dark Spots": {
            "Oily": [{"candidate_keys": ("dark_spot_serum", "serum_combination"), "label": "Turmeric spot serum"}, {"candidate_keys": ("serum_oily",), "label": "Clarifying serum"}],
            "Dry": [{"candidate_keys": ("dark_spot_serum",), "label": "Turmeric spot serum"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Aloe support serum"}],
            "Combination": [{"candidate_keys": ("dark_spot_serum", "serum_combination"), "label": "Turmeric spot serum"}],
            "Normal": [{"candidate_keys": ("dark_spot_serum",), "label": "Turmeric brightening serum"}, {"candidate_keys": ("serum_normal",), "label": "Glow support serum"}],
        },
        "Dark Circles": {
            "Oily": [{"candidate_keys": ("eye_cream",), "label": "Under-eye cream"}, {"candidate_keys": ("serum_oily",), "label": "Light prep serum"}],
            "Dry": [{"candidate_keys": ("eye_cream",), "label": "Under-eye cream"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Aloe prep serum"}],
            "Combination": [{"candidate_keys": ("eye_cream",), "label": "Under-eye cream"}, {"candidate_keys": ("serum_combination",), "label": "Turmeric prep serum"}],
            "Normal": [{"candidate_keys": ("eye_cream",), "label": "Under-eye cream"}, {"candidate_keys": ("serum_normal",), "label": "Glow prep serum"}],
        },
    },
    "Plix": {
        "Clear Skin": {
            "Oily": [{"candidate_keys": ("serum_oily",), "label": "Jamun daily serum"}],
            "Dry": [{"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydra glow serum"}],
            "Combination": [{"candidate_keys": ("serum_combination",), "label": "Niacinamide daily serum"}],
            "Normal": [{"candidate_keys": ("serum_normal",), "label": "Guava glow serum"}],
        },
        "Pimples / Acne": {
            "Oily": [{"candidate_keys": ("acne_treatment", "serum_oily"), "label": "Jamun acne serum"}, {"candidate_keys": ("serum_oily",), "label": "Niacinamide support serum"}],
            "Dry": [{"candidate_keys": ("acne_treatment",), "label": "Jamun acne serum"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydra support serum"}],
            "Combination": [{"candidate_keys": ("serum_combination", "acne_treatment"), "label": "Niacinamide balancing serum"}, {"candidate_keys": ("acne_treatment",), "label": "Jamun acne serum"}],
            "Normal": [{"candidate_keys": ("acne_treatment",), "label": "Jamun acne serum"}, {"candidate_keys": ("serum_normal",), "label": "Glow support serum"}],
        },
        "Dark Spots": {
            "Oily": [{"candidate_keys": ("dark_spot_serum", "serum_combination"), "label": "Niacinamide spot serum"}, {"candidate_keys": ("serum_oily",), "label": "Jamun balancing serum"}],
            "Dry": [{"candidate_keys": ("dark_spot_serum",), "label": "Niacinamide spot serum"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydra support serum"}],
            "Combination": [{"candidate_keys": ("dark_spot_serum", "serum_combination"), "label": "Tone-correcting serum"}],
            "Normal": [{"candidate_keys": ("dark_spot_serum", "serum_normal"), "label": "Brightening serum"}, {"candidate_keys": ("serum_normal",), "label": "Glow support serum"}],
        },
        "Dark Circles": {
            "Oily": [{"candidate_keys": ("eye_cream",), "label": "Under-eye brightening gel"}, {"candidate_keys": ("serum_oily",), "label": "Light prep serum"}],
            "Dry": [{"candidate_keys": ("eye_cream",), "label": "Under-eye brightening gel"}, {"candidate_keys": ("hydrating_serum", "serum_dry"), "label": "Hydra prep serum"}],
            "Combination": [{"candidate_keys": ("eye_cream",), "label": "Under-eye brightening gel"}, {"candidate_keys": ("serum_combination",), "label": "Tone prep serum"}],
            "Normal": [{"candidate_keys": ("eye_cream",), "label": "Under-eye brightening gel"}, {"candidate_keys": ("serum_normal",), "label": "Glow prep serum"}],
        },
    },
}


def _fallback_image_url(brand, product_name):
    params = urllib.parse.urlencode({"brand": brand, "product": product_name})
    return "/product-fallback?" + params


def _app_image_proxy_url(image_url):
    if not image_url:
        return ""
    return "/product-image?src=" + urllib.parse.quote(image_url, safe="")


def _local_preview_paths(brand, product_key):
    brand_slug = re.sub(r"[^a-z0-9]+", "-", brand.lower()).strip("-")
    for ext in ("jpg", "png", "webp", "svg"):
        absolute_fs = os.path.join(BASE_DIR, "static", "products_previews", brand_slug, f"{product_key}.{ext}")
        if os.path.exists(absolute_fs):
            return absolute_fs, f"/static/products_previews/{brand_slug}/{product_key}.{ext}"
    return "", ""


def _pick_brands(preferred_brand=None):
    brands = ALL_BRANDS[:]
    if preferred_brand in brands:
        brands.remove(preferred_brand)
        brands.insert(0, preferred_brand)
    return brands


def _normalize_skin_type(skin_type):
    value = (skin_type or "").strip().lower()
    return SKIN_TYPE_ALIASES.get(value, "Normal")


def _resolve_product_key(brand, *candidate_keys):
    catalog = PRODUCT_CATALOG[brand]
    for key in candidate_keys:
        if key and key in catalog:
            return key

    fallback_map = {
        "cleanser": ("cleanser",),
        "moisturizer": ("moisturizer_normal", "moisturizer_oily", "moisturizer_dry"),
        "sunscreen": ("sunscreen",),
        "hydrating_serum": ("hydrating_serum",),
    }

    for key in candidate_keys:
        if not key:
            continue
        family = key.split("_")[0]
        if family == "hydrating" and "serum" in key:
            family = "hydrating_serum"
        if family == "moisturizer":
            fallback_keys = fallback_map["moisturizer"]
        else:
            fallback_keys = fallback_map.get(family, ())
        for fallback_key in fallback_keys:
            if fallback_key in catalog:
                return fallback_key

    raise KeyError(f"No product key found for {brand}: {candidate_keys}")


def _is_serum_like(product_key):
    if not product_key:
        return False
    return (
        product_key.endswith("_serum")
        or product_key in {"acne_treatment", "dark_spot_serum"}
    )


def _dedupe_serum_steps(optional_steps):
    filtered = []
    has_serum = False
    for product_key, label in optional_steps:
        if _is_serum_like(product_key):
            if has_serum:
                continue
            has_serum = True
        filtered.append((product_key, label))
    return filtered


def _has_serum_in_steps(optional_steps):
    return any(_is_serum_like(product_key) for product_key, _ in optional_steps)


def _morning_serum_label(product_key, fallback_label):
    if product_key == "acne_treatment":
        return "Oil-control serum"
    if product_key == "dark_spot_serum":
        return "Balancing serum"
    return fallback_label


def _resolve_concern_steps(brand, skin_concern, normalized_skin_type):
    concern_selection = (
        BRAND_CONCERN_PRODUCT_SELECTIONS.get(brand, {}).get(skin_concern)
        or CONCERN_PRODUCT_SELECTIONS.get(skin_concern, {})
    )
    step_configs = concern_selection.get(normalized_skin_type) or concern_selection.get("default") or []
    resolved_steps = []
    seen_keys = set()
    seen_products = set()

    for step_config in step_configs:
        candidate_keys = tuple(step_config.get("candidate_keys") or ())
        if not candidate_keys:
            continue
        try:
            product_key = _resolve_product_key(brand, *candidate_keys)
        except KeyError:
            continue
        if product_key in seen_keys:
            continue
        product_name = (PRODUCT_CATALOG.get(brand, {}).get(product_key, {}).get("product") or "").strip().lower()
        if product_name and product_name in seen_products:
            continue
        resolved_steps.append((product_key, step_config.get("label", "Concern care")))
        seen_keys.add(product_key)
        if product_name:
            seen_products.add(product_name)

    return resolved_steps


def _product_name_for_key(brand, product_key):
    if not product_key:
        return ""
    return (PRODUCT_CATALOG.get(brand, {}).get(product_key, {}).get("product") or "").strip().lower()


def _add_steps_with_limit(routine_steps, start_step_number, optional_steps, max_total_steps, brand):
    next_step = start_step_number
    remaining_slots = max_total_steps - len(routine_steps)
    if remaining_slots <= 0:
        return next_step

    for product_key, label in optional_steps[:remaining_slots]:
        routine_steps.append(_entry(f"Step {next_step}", product_key, label, brand))
        next_step += 1

    return next_step


def _resolve_core_selection(brand, skin_concern, normalized_skin_type, brand_selection):
    concern_core = CONCERN_CORE_SELECTIONS.get(skin_concern, {}).get(normalized_skin_type, {})

    cleanser_key = _resolve_product_key(
        brand,
        *(concern_core.get("cleanser_candidates") or ()),
        brand_selection.get("cleanser_key"),
        "cleanser",
    )
    moisturizer_key = _resolve_product_key(
        brand,
        *(concern_core.get("moisturizer_candidates") or ()),
        brand_selection.get("moisturizer_key"),
        "moisturizer_normal",
        "moisturizer_oily",
        "moisturizer_dry",
    )
    sunscreen_key = _resolve_product_key(
        brand,
        *(concern_core.get("sunscreen_candidates") or ()),
        brand_selection.get("sunscreen_key"),
        "sunscreen",
    )
    return cleanser_key, moisturizer_key, sunscreen_key


def _extract_first_image(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        for item in value:
            img = _extract_first_image(item)
            if img:
                return img
    if isinstance(value, dict):
        for key in ("url", "contentUrl"):
            if isinstance(value.get(key), str):
                return value[key]
    return None


def _safe_price(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(round(float(value)))
    if isinstance(value, str):
        clean = re.sub(r"[^\d.]", "", value)
        if not clean:
            return None
        try:
            parsed = float(clean)
            # Some stores expose price in paise/cents (e.g. 39500 for Rs 395.00)
            if parsed > 5000:
                parsed = parsed / 100.0
            return int(round(parsed))
        except ValueError:
            return None
    return None


def _extract_from_json_ld(html):
    scripts = re.findall(
        r"<script[^>]*type=['\"]application/ld\+json['\"][^>]*>(.*?)</script>",
        html,
        flags=re.IGNORECASE | re.DOTALL
    )

    for script in scripts:
        text = script.strip()
        if not text:
            continue

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue

        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
                continue
            if not isinstance(node, dict):
                continue

            node_type = node.get("@type", "")
            type_str = " ".join(node_type) if isinstance(node_type, list) else str(node_type)
            if "Product" in type_str:
                image = _extract_first_image(node.get("image"))

                offers = node.get("offers")
                price = None
                if isinstance(offers, list):
                    for offer in offers:
                        if isinstance(offer, dict):
                            price = _safe_price(offer.get("price"))
                            if price:
                                break
                elif isinstance(offers, dict):
                    price = _safe_price(offers.get("price"))

                if image or price:
                    return {"image_url": image, "price_inr": price}

            stack.extend(node.values())

    return {"image_url": None, "price_inr": None}


def _extract_meta_tag(html, key, attr="property"):
    pattern = rf'<meta[^>]+{attr}=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)["\']'
    match = re.search(pattern, html, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None


def _fetch_live_meta(product_url):
    now = time.time()
    cached = _LIVE_META_CACHE.get(product_url)
    if cached and (now - cached["ts"]) < _CACHE_TTL_SECONDS:
        return cached["data"]

    data = {"image_url": None, "price_inr": None}

    try:
        req = urllib.request.Request(
            product_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0 Safari/537.36"
                )
            }
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        data = _extract_from_json_ld(html)

        if not data.get("image_url"):
            data["image_url"] = _extract_meta_tag(html, "og:image")

        if not data.get("price_inr"):
            for key in ("product:price:amount", "og:price:amount"):
                candidate = _extract_meta_tag(html, key)
                parsed = _safe_price(candidate)
                if parsed:
                    data["price_inr"] = parsed
                    break
    except Exception:
        data = {"image_url": None, "price_inr": None}

    _LIVE_META_CACHE[product_url] = {"ts": now, "data": data}
    return data


def _entry(step, product_key, display_step, brand):
    product = PRODUCT_CATALOG[brand][product_key]
    live = _fetch_live_meta(product["buy_url"])

    product_image_url = product["image_url"]
    live_image_url = None if product.get("disable_live_image") else live.get("image_url")
    has_catalog_placeholder = "via.placeholder.com" in (product_image_url or "")
    is_generic_listing_url = product["buy_url"].rstrip("/").endswith(("/products", "/collections/face-care", "/collections/skin-care"))

    if live_image_url and not is_generic_listing_url:
        resolved_image_url = live_image_url
    elif product_image_url and not has_catalog_placeholder:
        resolved_image_url = product_image_url
    else:
        resolved_image_url = ""

    resolved_price_inr = live.get("price_inr") or product["price_inr"]
    if resolved_price_inr < 100 or resolved_price_inr > 5000:
        resolved_price_inr = product["price_inr"]
    proxy_image_url = "https://images.weserv.nl/?url=" + resolved_image_url.replace("https://", "").replace("http://", "")
    app_proxy_url = _app_image_proxy_url(resolved_image_url)
    local_preview_fs, local_preview_url = _local_preview_paths(brand, product_key)
    fallback_image_url = _fallback_image_url(brand, product["product"])

    local_preview_is_svg = local_preview_fs.lower().endswith(".svg") if local_preview_fs else False

    if local_preview_url and not local_preview_is_svg:
        display_image_url = local_preview_url
    elif resolved_image_url:
        display_image_url = resolved_image_url
    elif app_proxy_url:
        display_image_url = app_proxy_url
    elif local_preview_url:
        display_image_url = local_preview_url
    else:
        display_image_url = fallback_image_url

    return {
        "step": step,
        "display_step": display_step,
        "product": product["product"],
        "brand": brand,
        "price_inr": resolved_price_inr,
        "image_url": resolved_image_url,
        "image_proxy_url": proxy_image_url,
        "app_proxy_url": app_proxy_url,
        "local_preview_url": local_preview_url,
        "fallback_image_url": fallback_image_url,
        "display_image_url": display_image_url,
        "price_source": "live" if live.get("price_inr") else "catalog",
        "buy_url": product["buy_url"]
    }


def generate_skincare_routine(
    skin_concern,
    age,
    skin_type,
    lifestyle,
    preferred_brand=None
):
    brands = _pick_brands(preferred_brand)
    primary_brand = preferred_brand if preferred_brand in ALL_BRANDS else brands[0]
    normalized_skin_type = _normalize_skin_type(skin_type)
    brand_selection = BRAND_CORE_ROUTINES.get(primary_brand, {}).get(normalized_skin_type, {})
    cleanser_key, moisturizer_key, sunscreen_key = _resolve_core_selection(
        primary_brand,
        skin_concern,
        normalized_skin_type,
        brand_selection,
    )
    configured_serum_key = brand_selection.get("serum_key", "__default__")
    if configured_serum_key is None:
        serum_key = ""
    else:
        serum_key = _resolve_product_key(
            primary_brand,
            None if configured_serum_key == "__default__" else configured_serum_key,
            "hydrating_serum",
        )
    routine = {
        "morning": [],
        "evening": [],
        "brand_recommendations": brands,
        "selected_brand": primary_brand,
        "skin_type": normalized_skin_type,
    }
    concern_steps = _resolve_concern_steps(primary_brand, skin_concern, normalized_skin_type)
    concern_step_keys = {product_key for product_key, _ in concern_steps}
    concern_step_products = {_product_name_for_key(primary_brand, product_key) for product_key, _ in concern_steps}
    serum_product_name = _product_name_for_key(primary_brand, serum_key)
    has_serum_step = (
        bool(serum_key)
        and serum_key not in concern_step_keys
        and (not serum_product_name or serum_product_name not in concern_step_products)
    )

    routine["morning"].append(_entry("Step 1", cleanser_key, "Skin-type cleanser", primary_brand))
    next_morning_step = 2
    morning_optional_steps = []
    if concern_steps:
        morning_optional_steps.extend(concern_steps)
    if has_serum_step and not _has_serum_in_steps(concern_steps):
        morning_optional_steps.append(
            (serum_key, _morning_serum_label(serum_key, brand_selection.get("serum_label", "Daily serum")))
        )
    morning_optional_steps = _dedupe_serum_steps(morning_optional_steps)
    next_morning_step = _add_steps_with_limit(
        routine["morning"],
        next_morning_step,
        morning_optional_steps,
        MAX_MORNING_STEPS - 2,
        primary_brand,
    )
    routine["morning"].append(_entry(f"Step {next_morning_step}", moisturizer_key, brand_selection.get("moisturizer_label", "Daily moisturizer"), primary_brand))
    next_morning_step += 1
    routine["morning"].append(_entry(f"Step {next_morning_step}", sunscreen_key, brand_selection.get("sunscreen_label", "Daily sunscreen"), primary_brand))

    routine["evening"].append(_entry("Step 1", cleanser_key, "Skin-type cleanser", primary_brand))
    next_evening_step = 2
    evening_optional_steps = []
    if concern_steps:
        evening_optional_steps.extend(concern_steps)
    elif has_serum_step:
        evening_optional_steps.append((serum_key, "Recovery serum"))
    evening_optional_steps = _dedupe_serum_steps(evening_optional_steps)
    next_evening_step = _add_steps_with_limit(
        routine["evening"],
        next_evening_step,
        evening_optional_steps,
        MAX_EVENING_STEPS - 1,
        primary_brand,
    )
    routine["evening"].append(_entry(f"Step {next_evening_step}", moisturizer_key, "Night moisturizer", primary_brand))

    routine["note"] = f"Showing {skin_concern.lower()} recommendations for {normalized_skin_type.lower()} skin from {primary_brand}."
    return routine
