import streamlit as st
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO
import datetime
import base64
from typing import Dict, List, Tuple, Optional
import time
import random
import json
import uuid
import os
import re
from urllib.parse import urlencode, quote
import gc
from streamlit.errors import StreamlitAPIException, StreamlitSecretNotFoundError
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 應用配置
APP_TITLE = "🎨 AI 圖像生成器 (完整多模型版)"
APP_ICON = "🎨"
VERSION = "v2.0.0"

# 為免費方案設定限制
MAX_HISTORY_ITEMS = 25
MAX_FAVORITE_ITEMS = 50
MAX_BATCH_SIZE = 6
REQUEST_TIMEOUT = 180

# 擴展的圖像尺寸預設
IMAGE_SIZES = {
    "自定義...": "Custom",
    # 標準尺寸
    "512x512": "SD 標準 (1:1)", 
    "768x768": "SD XL 標準 (1:1)",
    "1024x1024": "正方形 (1:1)", 
    "1080x1080": "IG 貼文 (1:1)",
    # 縱向
    "512x768": "SD 縱向 (2:3)",
    "768x1024": "SDXL 縱向 (3:4)",
    "1080x1350": "IG 縱向 (4:5)", 
    "1080x1920": "IG Story (9:16)",
    "896x1152": "肖像模式 (7:9)",
    # 橫向
    "768x512": "SD 橫向 (3:2)",
    "1024x768": "SDXL 橫向 (4:3)",
    "1200x630": "FB 橫向 (1.91:1)",
    "1536x640": "超寬橫幅 (2.4:1)",
    "1152x896": "風景模式 (9:7)",
    # 特殊格式
    "640x1536": "超長縱向 (5:12)",
    "1344x768": "寬屏 (16:9)",
    "832x1216": "書本頁面 (13:19)",
}

# 完整的風格預設系統
STYLE_PRESETS = {
    # 基礎風格
    "無": "",
    "電影感": "cinematic, dramatic lighting, high detail, sharp focus, epic scene, movie still",
    "動漫風": "anime, manga style, vibrant colors, clean line art, studio ghibli style, cel shading", 
    "賽博龐克": "cyberpunk, neon lights, futuristic city, high-tech, Blade Runner style, dystopian",
    
    # 攝影風格
    "人像攝影": "portrait photography, professional headshot, studio lighting, bokeh background, 85mm lens",
    "街頭攝影": "street photography, candid moment, urban setting, documentary style, natural lighting",
    "風景攝影": "landscape photography, golden hour lighting, wide angle view, nature scenery, HDR",
    "微距攝影": "macro photography, extreme close-up, detailed textures, shallow depth of field",
    "黑白攝影": "black and white photography, monochrome, high contrast, dramatic shadows",
    
    # 藝術流派
    "印象派": "impressionism, soft brushstrokes, natural light, Monet style, plein air painting",
    "超現實主義": "surrealism, dreamlike imagery, impossible scenes, Salvador Dali style, melting reality",
    "普普藝術": "pop art, bold colors, comic book style, Andy Warhol aesthetic, screen printing effect",
    "抽象表現主義": "abstract expressionism, emotional brushwork, Jackson Pollock style, paint splatters",
    "立體主義": "cubism, geometric shapes, fragmented perspective, Pablo Picasso style, analytical",
    "新藝術運動": "art nouveau, ornate decorations, flowing organic lines, Alphonse Mucha style",
    
    # 傳統藝術
    "水墨畫": "traditional Chinese ink painting, brush strokes, minimalist zen aesthetic, black ink on rice paper",
    "水彩畫": "watercolor painting, soft transparent washes, wet-on-wet technique, delicate colors",
    "油畫": "oil painting, thick impasto, rich textures, renaissance style, classical technique",
    "素描": "pencil sketch, graphite drawing, crosshatching, detailed line work, academic drawing",
    
    # 數位藝術
    "3D 渲染": "3D render, octane rendering, photorealistic, volumetric lighting, global illumination",
    "像素藝術": "pixel art, 8-bit style, retro gaming aesthetic, low resolution, sprite art",
    "低面建模": "low poly art, geometric shapes, minimal vertices, isometric view, faceted surfaces",
    "矢量圖": "vector illustration, clean geometric lines, flat design, scalable graphics",
    
    # 特定風格
    "蒸汽龐克": "steampunk aesthetic, Victorian era meets technology, brass gears, copper pipes, clockwork",
    "賽博朋克": "cyberpunk style, neon-soaked streets, high-tech low-life, neural implants, megacorp",
    "太陽朋克": "solarpunk, ecological futurism, sustainable technology, green architecture, hopeful future",
    "波普浪潮": "vaporwave aesthetic, 80s nostalgia, neon grids, palm trees, retro futurism",
    
    # 幻想風格
    "奇幻藝術": "fantasy art, magical creatures, epic landscapes, detailed armor, mystical atmosphere",
    "黑暗奇幻": "dark fantasy, gothic horror, ominous mood, dramatic shadows, supernatural elements",
    "科幻藝術": "science fiction art, futuristic technology, space scenes, alien worlds, concept art",
    
    # 漫畫風格
    "美式漫畫": "American comic book style, bold outlines, dynamic poses, superhero aesthetic, halftone dots",
    "日式漫畫": "manga style, detailed line art, expressive characters, screen tones, Japanese comics",
    "歐式漫畫": "European comic art, detailed backgrounds, realistic proportions, graphic novel style",
    
    # 裝飾風格
    "包豪斯": "Bauhaus design, geometric minimalism, functional aesthetics, primary colors, clean typography",
    "裝飾藝術": "art deco style, geometric patterns, luxury aesthetics, gold accents, 1920s glamour",
    "復古海報": "vintage poster design, retro color palette, bold typography, propaganda style",
    
    # 材質風格
    "剪紙藝術": "paper cut art, layered paper sculpture, shadow box effect, handcraft aesthetic",
    "陶瓷風格": "ceramic art, glazed pottery, handmade textures, earthy color palette",
    "金屬質感": "metallic finish, brushed steel, chrome reflection, industrial materials",
    
    # 特殊效果
    "霓虹效果": "neon lighting effect, glowing edges, electric colors, night club atmosphere",
    "光線追蹤": "ray traced lighting, realistic reflections, caustics, global illumination",
    "雙重曝光": "double exposure effect, overlapping images, transparent blending, artistic composition",
}

# 負向提示詞預設
NEGATIVE_PROMPTS = {
    "基本": "blurry, low quality, distorted, deformed, ugly, bad anatomy",
    "攝影": "blurry, low resolution, overexposed, underexposed, noise, grain, amateur",
    "人像": "bad anatomy, deformed face, extra limbs, missing fingers, asymmetric eyes, ugly",
    "動漫": "realistic, photographic, 3d render, western cartoon, bad anatomy, low quality",
    "藝術": "photographic, realistic, low quality, commercial, amateur, stock photo",
    "建築": "blurry, distorted perspective, bad proportions, amateur photography, low quality",
}

def rerun_app():
    """安全的應用重載函數"""
    try:
        if hasattr(st, 'rerun'):
            st.rerun()
        elif hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
        else:
            st.stop()
    except Exception:
        st.stop()

# 頁面配置
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 完整的API供應商配置
API_PROVIDERS = {
    "Pollinations.ai": {
        "name": "Pollinations.ai Studio",
        "base_url_default": "https://image.pollinations.ai",
        "icon": "🌸",
        "description": "免費AI圖像生成服務，支持多種模型",
        "hardcoded_models": {
            # FLUX 系列
            "flux-1.1-pro": {"name": "Flux 1.1 Pro", "icon": "🏆", "category": "FLUX", "description": "最新旗艦級FLUX模型"},
            "flux.1-kontext-pro": {"name": "Flux.1 Kontext Pro", "icon": "🧠", "category": "FLUX", "description": "上下文理解增強版"},
            "flux.1-kontext-max": {"name": "Flux.1 Kontext Max", "icon": "👑", "category": "FLUX", "description": "最強上下文理解"},
            "flux-dev": {"name": "Flux Dev", "icon": "🛠️", "category": "FLUX", "description": "開發者版本"},
            "flux-schnell": {"name": "Flux Schnell", "icon": "⚡", "category": "FLUX", "description": "快速生成版本"},
            "flux-realism": {"name": "Flux Realism", "icon": "📷", "category": "FLUX", "description": "寫實風格專用"},
            "flux-anime": {"name": "Flux Anime", "icon": "🎌", "category": "FLUX", "description": "動漫風格專用"},
            "flux-3d": {"name": "Flux 3D", "icon": "🎯", "category": "FLUX", "description": "3D渲染風格"},
            
            # Stable Diffusion 系列
            "stable-diffusion-3.5-large": {"name": "SD 3.5 Large", "icon": "🎯", "category": "Stable Diffusion", "description": "最新大型SD模型"},
            "stable-diffusion-3.5-medium": {"name": "SD 3.5 Medium", "icon": "⚖️", "category": "Stable Diffusion", "description": "平衡性能版本"},
            "stable-diffusion-xl": {"name": "SDXL 1.0", "icon": "💎", "category": "Stable Diffusion", "description": "高分辨率標準版"},
            "stable-diffusion-xl-turbo": {"name": "SDXL Turbo", "icon": "🚀", "category": "Stable Diffusion", "description": "快速生成版"},
            "stable-diffusion-2.1": {"name": "SD 2.1", "icon": "🔄", "category": "Stable Diffusion", "description": "穩定版本"},
            "stable-diffusion-1.5": {"name": "SD 1.5", "icon": "🔰", "category": "Stable Diffusion", "description": "經典版本"},
            
            # 專業級模型
            "midjourney": {"name": "Midjourney", "icon": "🎭", "category": "Professional", "description": "藝術創作專家"},
            "dalle-3": {"name": "DALL-E 3", "icon": "🤖", "category": "Professional", "description": "OpenAI最新模型"},
            "playground-v2.5": {"name": "Playground v2.5", "icon": "🎪", "category": "Professional", "description": "商業級模型"},
            "leonardo-diffusion": {"name": "Leonardo Diffusion", "icon": "🎨", "category": "Professional", "description": "專業創作工具"},
            
            # 社區特化模型
            "dreamshaper": {"name": "DreamShaper", "icon": "💫", "category": "Community", "description": "夢境風格生成"},
            "realistic-vision": {"name": "Realistic Vision", "icon": "👁️", "category": "Community", "description": "超現實主義"},
            "deliberate": {"name": "Deliberate", "icon": "🎨", "category": "Community", "description": "精細控制"},
            "revanimated": {"name": "ReV Animated", "icon": "🎬", "category": "Community", "description": "動畫風格"},
            "protogen": {"name": "Protogen", "icon": "🤖", "category": "Community", "description": "科幻風格"},
            "openjourney": {"name": "OpenJourney", "icon": "🗺️", "category": "Community", "description": "開放式創作"},
            
            # 動漫專用模型
            "anything-v5": {"name": "Anything v5", "icon": "🌟", "category": "Anime", "description": "萬能動漫模型"},
            "waifu-diffusion": {"name": "Waifu Diffusion", "icon": "👩‍🎨", "category": "Anime", "description": "動漫角色專用"},
            "anythingv4": {"name": "Anything v4", "icon": "✨", "category": "Anime", "description": "經典動漫模型"},
            "counterfeit": {"name": "Counterfeit", "icon": "🎪", "category": "Anime", "description": "高質量動漫"},
            "pastel-mix": {"name": "Pastel Mix", "icon": "🌈", "category": "Anime", "description": "柔和色彩"},
            
            # 風格特化模型
            "analog-diffusion": {"name": "Analog Film", "icon": "📸", "category": "Style", "description": "膠片攝影風格"},
            "synthwave-diffusion": {"name": "Synthwave", "icon": "🌆", "category": "Style", "description": "合成波風格"},
            "cyberpunk-anime": {"name": "Cyberpunk Anime", "icon": "🤖", "category": "Style", "description": "賽博朋克動漫"},
            "pixel-art-xl": {"name": "Pixel Art XL", "icon": "🎮", "category": "Style", "description": "像素藝術"},
            "papercut-diffusion": {"name": "Papercut", "icon": "✂️", "category": "Style", "description": "剪紙藝術"},
            "ink-painting": {"name": "Ink Painting", "icon": "🖋️", "category": "Style", "description": "水墨畫風格"},
        }
    },
    
    "NavyAI": {
        "name": "NavyAI",
        "base_url_default": "https://api.navy/v1",
        "icon": "⚓",
        "description": "商業級AI API服務平台",
        "hardcoded_models": {
            "flux-pro": {"name": "Flux Pro", "icon": "🏆", "category": "FLUX", "description": "商業級FLUX"},
            "flux-schnell": {"name": "Flux Schnell", "icon": "⚡", "category": "FLUX", "description": "快速生成"},
            "stable-diffusion-xl": {"name": "SDXL", "icon": "💎", "category": "Stable Diffusion", "description": "高分辨率"},
            "midjourney-v6": {"name": "Midjourney v6", "icon": "🎭", "category": "Professional", "description": "最新Midjourney"},
            "dalle-3": {"name": "DALL-E 3", "icon": "🤖", "category": "Professional", "description": "OpenAI模型"},
        }
    },
    
    "Hugging Face": {
        "name": "Hugging Face Inference",
        "base_url_default": "https://api-inference.huggingface.co",
        "icon": "🤗",
        "description": "開源模型推理平台",
        "hardcoded_models": {
            "stable-diffusion-v1-5": {"name": "SD 1.5 (HF)", "icon": "🔰", "category": "Stable Diffusion", "description": "開源經典"},
            "stable-diffusion-xl-base-1.0": {"name": "SDXL Base (HF)", "icon": "💎", "category": "Stable Diffusion", "description": "開源SDXL"},
            "flux-1-dev": {"name": "Flux.1 Dev (HF)", "icon": "🛠️", "category": "FLUX", "description": "開源FLUX"},
            "stable-diffusion-2-1": {"name": "SD 2.1 (HF)", "icon": "🔄", "category": "Stable Diffusion", "description": "開源SD2.1"},
        }
    },
    
    "OpenAI Compatible": {
        "name": "OpenAI 兼容 API",
        "base_url_default": "https://api.openai.com/v1",
        "icon": "🤖",
        "description": "標準OpenAI兼容接口",
        "hardcoded_models": {
            "dall-e-3": {"name": "DALL-E 3", "icon": "🤖", "category": "OpenAI", "description": "最新DALL-E"},
            "dall-e-2": {"name": "DALL-E 2", "icon": "🔄", "category": "OpenAI", "description": "經典DALL-E"},
        }
    }
}

# 基礎模型集合（後備選項）
BASE_MODELS = {
    "flux.1-schnell": {"name": "FLUX.1 Schnell", "icon": "⚡", "priority": 1, "category": "FLUX", "description": "快速FLUX生成"},
    "stable-diffusion-xl": {"name": "Stable Diffusion XL", "icon": "💎", "priority": 2, "category": "Stable Diffusion", "description": "高分辨率SD"},
    "stable-diffusion-1.5": {"name": "Stable Diffusion 1.5", "icon": "🔰", "priority": 3, "category": "Stable Diffusion", "description": "經典SD版本"},
}

# === 核心功能函數 ===

def init_session_state():
    """初始化會話狀態"""
    # API配置初始化
    if 'api_profiles' not in st.session_state:
        try:
            base_profiles = st.secrets.get("api_profiles", {})
        except StreamlitSecretNotFoundError:
            base_profiles = {}
        
        # 默認配置
        default_profiles = {
            "預設 Pollinations": {
                'provider': 'Pollinations.ai',
                'api_key': '',
                'base_url': 'https://image.pollinations.ai',
                'validated': True,
                'pollinations_auth_mode': '免費',
                'pollinations_token': '',
                'pollinations_referrer': ''
            }
        }
        
        st.session_state.api_profiles = base_profiles.copy() if base_profiles else default_profiles
    
    # 活動配置初始化
    if ('active_profile_name' not in st.session_state or 
        st.session_state.active_profile_name not in st.session_state.api_profiles):
        st.session_state.active_profile_name = (
            list(st.session_state.api_profiles.keys())[0] 
            if st.session_state.api_profiles else ""
        )
    
    # 其他狀態初始化
    defaults = {
        'generation_history': [],
        'favorite_images': [],
        'discovered_models': {},
        'selected_model': None,
        'generation_in_progress': False,
        'last_generation_time': None,
        'ui_theme': 'light',
        'advanced_mode': False,
        'batch_processing': False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_active_config() -> Dict:
    """獲取當前活動的API配置"""
    return st.session_state.api_profiles.get(st.session_state.active_profile_name, {})

def validate_api_key(api_key: str, base_url: str, provider: str) -> Tuple[bool, str]:
    """驗證API密鑰"""
    try:
        if provider == "Pollinations.ai":
            return True, "Pollinations.ai 無需驗證"
        
        elif provider == "Hugging Face":
            if not api_key:
                return False, "Hugging Face 需要 API Token"
            
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(f"{base_url}/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True, "Hugging Face API Token 驗證成功"
            else:
                return False, f"Hugging Face API 驗證失敗: {response.status_code}"
        
        else:
            # OpenAI兼容API驗證
            client = OpenAI(api_key=api_key, base_url=base_url)
            client.models.list()
            return True, "API 密鑰驗證成功"
            
    except Exception as e:
        return False, f"API 驗證失敗: {str(e)[:100]}"

def auto_discover_models(client, provider: str, base_url: str) -> Dict[str, Dict]:
    """自動發現可用模型"""
    discovered = {}
    
    try:
        if provider == "Pollinations.ai":
            response = requests.get(f"{base_url}/models", timeout=15)
            if response.ok:
                models = response.json()
                for model_name in models:
                    # 智能分類
                    category = categorize_model_name(model_name)
                    icon = get_model_icon(model_name, category)
                    
                    discovered[model_name] = {
                        "name": format_model_name(model_name),
                        "icon": icon,
                        "category": category,
                        "description": f"Pollinations {category} 模型"
                    }
            else:
                st.warning(f"無法從 Pollinations 獲取模型列表: HTTP {response.status_code}")
        
        elif provider == "Hugging Face":
            # HF模型發現邏輯
            popular_models = [
                "runwayml/stable-diffusion-v1-5",
                "stabilityai/stable-diffusion-xl-base-1.0",
                "black-forest-labs/flux-schnell",
                "stabilityai/stable-diffusion-2-1",
            ]
            
            for model_id in popular_models:
                category = categorize_model_name(model_id)
                icon = get_model_icon(model_id, category)
                
                discovered[model_id] = {
                    "name": format_model_name(model_id.split('/')[-1]),
                    "icon": icon,
                    "category": category,
                    "description": f"HF {category} 模型"
                }
        
        elif client:
            # OpenAI兼容API模型發現
            models = client.models.list().data
            for model in models:
                if any(keyword in model.id.lower() for keyword in 
                      ['flux', 'stable', 'dall', 'midjourney', 'sd', 'xl']):
                    
                    category = categorize_model_name(model.id)
                    icon = get_model_icon(model.id, category)
                    
                    discovered[model.id] = {
                        "name": format_model_name(model.id),
                        "icon": icon,
                        "category": category,
                        "description": f"API {category} 模型"
                    }
    
    except Exception as e:
        st.error(f"模型發現失敗: {str(e)[:100]}")
    
    return discovered

def categorize_model_name(model_name: str) -> str:
    """根據模型名稱智能分類"""
    name_lower = model_name.lower()
    
    if any(x in name_lower for x in ['flux', 'kontext']):
        return "FLUX"
    elif any(x in name_lower for x in ['stable-diffusion', 'stable_diffusion', 'sd-', 'sdxl']):
        return "Stable Diffusion"
    elif any(x in name_lower for x in ['anime', 'waifu', 'anything', 'counterfeit']):
        return "Anime"
    elif any(x in name_lower for x in ['midjourney', 'dalle', 'playground', 'leonardo']):
        return "Professional"
    elif any(x in name_lower for x in ['analog', 'synthwave', 'cyberpunk', 'pixel']):
        return "Style"
    else:
        return "Community"

def get_model_icon(model_name: str, category: str) -> str:
    """獲取模型圖標"""
    name_lower = model_name.lower()
    
    if 'flux' in name_lower:
        return "⚡"
    elif 'stable' in name_lower or 'sd' in name_lower:
        return "💎"
    elif 'dall' in name_lower:
        return "🤖"
    elif 'midjourney' in name_lower:
        return "🎭"
    elif 'anime' in name_lower or 'waifu' in name_lower:
        return "🎌"
    elif category == "Style":
        return "🎨"
    elif category == "Professional":
        return "🏆"
    else:
        return "🌟"

def format_model_name(model_name: str) -> str:
    """格式化模型名稱顯示"""
    # 移除常見前綴
    name = model_name.replace('stabilityai/', '').replace('runwayml/', '')
    name = name.replace('black-forest-labs/', '').replace('-', ' ').replace('_', ' ')
    
    # 首字母大寫
    return ' '.join(word.capitalize() for word in name.split())

def merge_models() -> Dict[str, Dict]:
    """合併硬編碼和發現的模型"""
    provider = get_active_config().get('provider')
    discovered = st.session_state.get('discovered_models', {})
    
    if provider in API_PROVIDERS:
        hardcoded = API_PROVIDERS[provider].get('hardcoded_models', {})
        merged = {**hardcoded, **discovered}
    else:
        merged = {**BASE_MODELS, **discovered}
    
    return merged

def get_models_by_category(models: Dict[str, Dict]) -> Dict[str, Dict[str, Dict]]:
    """按類別組織模型"""
    categorized = {}
    for model_id, model_info in models.items():
        category = model_info.get('category', 'Other')
        if category not in categorized:
            categorized[category] = {}
        categorized[category][model_id] = model_info
    
    # 排序類別
    priority_order = ["FLUX", "Stable Diffusion", "Professional", "Anime", "Style", "Community", "Other"]
    sorted_categorized = {}
    
    for category in priority_order:
        if category in categorized:
            sorted_categorized[category] = categorized[category]
    
    # 添加其他未知類別
    for category, models in categorized.items():
        if category not in sorted_categorized:
            sorted_categorized[category] = models
    
    return sorted_categorized

# === 圖像生成功能 ===

def generate_images_with_retry(client, **params) -> Tuple[bool, any]:
    """統一的圖像生成入口"""
    provider = get_active_config().get('provider')
    n_images = params.get("n", 1)
    
    st.session_state.generation_in_progress = True
    
    try:
        if provider == "Pollinations.ai":
            return generate_pollinations_images(params, n_images)
        elif provider == "Hugging Face":
            return generate_huggingface_images(params, n_images)
        else:
            return generate_openai_compatible_images(client, params, n_images)
    finally:
        st.session_state.generation_in_progress = False
        st.session_state.last_generation_time = datetime.datetime.now()

def generate_pollinations_images(params: Dict, n_images: int) -> Tuple[bool, any]:
    """Pollinations.ai 圖像生成"""
    generated_images = []
    cfg = get_active_config()
    
    # 創建進度條
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(n_images):
        try:
            status_text.text(f"正在生成第 {i+1}/{n_images} 張圖片...")
            progress_bar.progress((i) / n_images)
            
            current_params = params.copy()
            current_params["seed"] = random.randint(0, 2**32 - 1)
            
            # 構建提示詞
            prompt = current_params.get("prompt", "")
            if neg_prompt := current_params.get("negative_prompt"):
                prompt += f" --no {neg_prompt}"
            
            # 解析尺寸
            width, height = str(current_params.get("size", "1024x1024")).split('x')
            
            # API參數
            api_params = {}
            for key, value in {
                "model": current_params.get("model"),
                "width": width,
                "height": height,
                "seed": current_params.get("seed"),
                "nologo": current_params.get("nologo"),
                "private": current_params.get("private"),
                "enhance": current_params.get("enhance"),
                "safe": current_params.get("safe")
            }.items():
                if value is not None:
                    api_params[key] = value
            
            # 認證頭
            headers = {}
            auth_mode = cfg.get('pollinations_auth_mode', '免費')
            
            if auth_mode == '令牌' and cfg.get('pollinations_token'):
                headers['Authorization'] = f"Bearer {cfg['pollinations_token']}"
            elif auth_mode == '域名' and cfg.get('pollinations_referrer'):
                headers['Referer'] = cfg['pollinations_referrer']
            
            # 發送請求
            url = f"{cfg['base_url']}/prompt/{quote(prompt)}?{urlencode(api_params)}"
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            
            if response.ok:
                b64_json = base64.b64encode(response.content).decode()
                image_obj = type('Image', (object,), {'b64_json': b64_json})
                generated_images.append(image_obj)
            else:
                st.warning(f"第 {i+1} 張圖片生成失敗: HTTP {response.status_code}")
                
        except Exception as e:
            st.warning(f"第 {i+1} 張圖片生成錯誤: {str(e)[:100]}")
            continue
    
    # 清理UI
    progress_bar.progress(1.0)
    status_text.text(f"完成生成 {len(generated_images)}/{n_images} 張圖片")
    time.sleep(1)
    progress_bar.empty()
    status_text.empty()
    
    if generated_images:
        response_obj = type('Response', (object,), {'data': generated_images})
        return True, response_obj
    else:
        return False, "所有圖片生成均失敗"

def generate_huggingface_images(params: Dict, n_images: int) -> Tuple[bool, any]:
    """Hugging Face 圖像生成"""
    generated_images = []
    cfg = get_active_config()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(n_images):
        try:
            status_text.text(f"正在通過HF生成第 {i+1}/{n_images} 張圖片...")
            progress_bar.progress(i / n_images)
            
            headers = {"Authorization": f"Bearer {cfg['api_key']}"}
            model = params.get("model")
            prompt = params.get("prompt", "")
            
            # HF API payload
            payload = {
                "inputs": prompt,
                "parameters": {
                    "negative_prompt": params.get("negative_prompt", ""),
                    "num_inference_steps": 25,
                    "guidance_scale": 7.5,
                    "width": int(str(params.get("size", "512x512")).split('x')[0]),
                    "height": int(str(params.get("size", "512x512")).split('x')[1]),
                }
            }
            
            url = f"{cfg['base_url']}/models/{model}"
            response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
            
            if response.ok:
                b64_json = base64.b64encode(response.content).decode()
                image_obj = type('Image', (object,), {'b64_json': b64_json})
                generated_images.append(image_obj)
            else:
                st.warning(f"第 {i+1} 張圖片生成失敗: HTTP {response.status_code}")
                
        except Exception as e:
            st.warning(f"第 {i+1} 張圖片生成錯誤: {str(e)[:100]}")
            continue
    
    progress_bar.progress(1.0)
    status_text.text(f"完成生成 {len(generated_images)}/{n_images} 張圖片")
    time.sleep(1)
    progress_bar.empty()
    status_text.empty()
    
    if generated_images:
        response_obj = type('Response', (object,), {'data': generated_images})
        return True, response_obj
    else:
        return False, "所有圖片生成均失敗"

def generate_openai_compatible_images(client, params: Dict, n_images: int) -> Tuple[bool, any]:
    """OpenAI兼容API圖像生成"""
    try:
        sdk_params = {
            "model": params.get("model"),
            "prompt": params.get("prompt"),
            "size": str(params.get("size")),
            "n": n_images,
            "response_format": "b64_json"
        }
        
        # 添加負向提示詞支持（如果API支持）
        if params.get("negative_prompt"):
            sdk_params["negative_prompt"] = params.get("negative_prompt")
        
        # 過濾空值
        sdk_params = {k: v for k, v in sdk_params.items() 
                     if v is not None and v != ""}
        
        return True, client.images.generate(**sdk_params)
        
    except Exception as e:
        return False, str(e)[:200]

# === 歷史和收藏管理 ===

def add_to_history(prompt: str, negative_prompt: str, model: str, 
                  images: List[str], metadata: Dict):
    """添加到歷史記錄"""
    history = st.session_state.generation_history
    
    new_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now(),
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "model": model,
        "images": images,
        "metadata": metadata
    }
    
    history.insert(0, new_entry)
    st.session_state.generation_history = history[:MAX_HISTORY_ITEMS]

def display_image_with_actions(b64_json: str, image_id: str, history_item: Dict):
    """顯示圖片及操作按鈕"""
    try:
        img_data = base64.b64decode(b64_json)
        img = Image.open(BytesIO(img_data))
        
        # 顯示圖片
        st.image(img, use_container_width=True)
        
        # 圖片信息
        if st.session_state.get('advanced_mode', False):
            with st.expander("🔍 圖片信息"):
                st.json({
                    "尺寸": f"{img.size[0]}x{img.size[1]}",
                    "模式": img.mode,
                    "文件大小": f"{len(img_data)} bytes"
                })
        
        # 操作按鈕
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                "📥 下載",
                img_data,
                f"ai_generated_{image_id}.png",
                "image/png",
                key=f"dl_{image_id}",
                use_container_width=True
            )
        
        with col2:
            is_fav = any(fav['id'] == image_id 
                        for fav in st.session_state.favorite_images)
            if st.button(
                "⭐" if is_fav else "☆",
                key=f"fav_{image_id}",
                use_container_width=True,
                help="收藏/取消收藏"
            ):
                if is_fav:
                    st.session_state.favorite_images = [
                        f for f in st.session_state.favorite_images
                        if f['id'] != image_id
                    ]
                else:
                    if len(st.session_state.favorite_images) < MAX_FAVORITE_ITEMS:
                        st.session_state.favorite_images.append({
                            "id": image_id,
                            "image_b64": b64_json,
                            "timestamp": datetime.datetime.now(),
                            "history_item": history_item
                        })
                    else:
                        st.warning(f"收藏已達上限 ({MAX_FAVORITE_ITEMS})")
                rerun_app()
        
        with col3:
            if st.button(
                "🎨 變體",
                key=f"vary_{image_id}",
                use_container_width=True,
                help="使用此提示生成變體"
            ):
                st.session_state.update({
                    'vary_prompt': history_item['prompt'],
                    'vary_negative_prompt': history_item.get('negative_prompt', ''),
                    'vary_model': history_item['model']
                })
                rerun_app()
                
    except Exception as e:
        st.error(f"圖像顯示錯誤: {str(e)[:100]}")

# === API客戶端管理 ===

def init_api_client():
    """初始化API客戶端"""
    cfg = get_active_config()
    if (cfg and cfg.get('api_key') and 
        cfg.get('provider') not in ["Pollinations.ai", "Hugging Face"]):
        try:
            return OpenAI(api_key=cfg['api_key'], base_url=cfg['base_url'])
        except Exception:
            return None
    return None

# === UI組件 ===

def editor_provider_changed():
    """供應商變更回調"""
    provider = st.session_state.editor_provider_selectbox
    st.session_state.editor_base_url = API_PROVIDERS[provider]['base_url_default']
    st.session_state.editor_api_key = ""

def load_profile_to_editor_state(profile_name: str):
    """加載配置到編輯器狀態"""
    config = st.session_state.api_profiles.get(profile_name, {})
    provider = config.get('provider', 'Pollinations.ai')
    
    st.session_state.editor_provider_selectbox = provider
    st.session_state.editor_base_url = config.get(
        'base_url',
        API_PROVIDERS.get(provider, {}).get('base_url_default', '')
    )
    st.session_state.editor_api_key = config.get('api_key', '')
    st.session_state.editor_auth_mode = config.get('pollinations_auth_mode', '免費')
    st.session_state.editor_referrer = config.get('pollinations_referrer', '')
    st.session_state.editor_token = config.get('pollinations_token', '')
    st.session_state.profile_being_edited = profile_name

def show_api_settings():
    """顯示API設置面板"""
    st.subheader("⚙️ API 存檔管理")
    
    profile_names = list(st.session_state.api_profiles.keys())
    if not profile_names:
        st.warning("沒有可用的 API 存檔。請新增一個。")
        return
    
    # 選擇活動配置
    current_index = (profile_names.index(st.session_state.get('active_profile_name'))
                    if st.session_state.get('active_profile_name') in profile_names
                    else 0)
    
    active_profile_name = st.selectbox(
        "活動存檔",
        profile_names,
        index=current_index,
        help="選擇要使用的API配置"
    )
    
    # 檢查是否需要重載
    if (st.session_state.get('active_profile_name') != active_profile_name or
        'profile_being_edited' not in st.session_state or
        st.session_state.profile_being_edited != active_profile_name):
        
        st.session_state.active_profile_name = active_profile_name
        load_profile_to_editor_state(active_profile_name)
        st.session_state.discovered_models = {}
        rerun_app()
    
    # 配置管理按鈕
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ 新增存檔", use_container_width=True):
            new_name = "新存檔"
            count = 1
            while new_name in st.session_state.api_profiles:
                new_name = f"新存檔_{count}"
                count += 1
            
            st.session_state.api_profiles[new_name] = {
                'provider': 'Pollinations.ai',
                'validated': False,
                'base_url': API_PROVIDERS['Pollinations.ai']['base_url_default']
            }
            st.session_state.active_profile_name = new_name
            rerun_app()
    
    with col2:
        if st.button(
            "🗑️ 刪除當前存檔",
            use_container_width=True,
            disabled=len(profile_names) <= 1 or not active_profile_name
        ):
            if active_profile_name and len(profile_names) > 1:
                del st.session_state.api_profiles[active_profile_name]
                st.session_state.active_profile_name = list(st.session_state.api_profiles.keys())[0]
                rerun_app()
    
    # 編輯當前配置
    if active_profile_name:
        show_profile_editor(active_profile_name)

def show_profile_editor(profile_name: str):
    """顯示配置編輯器"""
    with st.expander("📝 編輯當前活動存檔", expanded=True):
        # 基本信息
        st.text_input(
            "存檔名稱",
            value=profile_name,
            key="editor_profile_name",
            help="為此API配置設置一個易識別的名稱"
        )
        
        # 供應商選擇
        provider_options = list(API_PROVIDERS.keys())
        st.selectbox(
            "API 提供商",
            provider_options,
            key='editor_provider_selectbox',
            on_change=editor_provider_changed,
            help="選擇您的API服務提供商"
        )
        
        # 端點URL
        st.text_input(
            "API 端點 URL",
            key='editor_base_url',
            help="API服務的基礎URL"
        )
        
        provider = st.session_state.editor_provider_selectbox
        
        # 特定供應商配置
        if provider == "Pollinations.ai":
            show_pollinations_config()
        else:
            st.text_input(
                "API 密鑰",
                key='editor_api_key',
                type="password",
                help="您的API密鑰或令牌"
            )
        
        # 保存按鈕
        if st.button("💾 保存/更新存檔", type="primary"):
            save_profile_config(profile_name, provider)

def show_pollinations_config():
    """顯示Pollinations.ai特定配置"""
    st.radio(
        "認證模式",
        ["免費", "域名", "令牌"],
        key='editor_auth_mode',
        horizontal=True,
        help="選擇Pollinations.ai的認證方式"
    )
    
    if st.session_state.editor_auth_mode == '域名':
        st.text_input(
            "應用域名 (Referrer)",
            key='editor_referrer',
            help="您的應用網域，用於域名驗證"
        )
    
    if st.session_state.editor_auth_mode == '令牌':
        st.text_input(
            "API 令牌 (Token)",
            key='editor_token',
            type="password",
            help="Pollinations.ai的付費API令牌"
        )

def save_profile_config(profile_name: str, provider: str):
    """保存配置"""
    new_config = {
        'provider': provider,
        'base_url': st.session_state.editor_base_url
    }
    
    if provider == "Pollinations.ai":
        new_config.update({
            'api_key': '',
            'pollinations_auth_mode': st.session_state.editor_auth_mode,
            'pollinations_referrer': st.session_state.get('editor_referrer', ''),
            'pollinations_token': st.session_state.get('editor_token', '')
        })
    else:
        new_config.update({
            'api_key': st.session_state.editor_api_key,
            'pollinations_auth_mode': '免費',
            'pollinations_referrer': '',
            'pollinations_token': ''
        })
    
    # 驗證配置
    is_valid, msg = validate_api_key(
        new_config['api_key'],
        new_config['base_url'],
        new_config['provider']
    )
    new_config['validated'] = is_valid
    
    # 保存配置
    new_name = st.session_state.editor_profile_name
    if new_name != profile_name:
        del st.session_state.api_profiles[profile_name]
    
    st.session_state.api_profiles[new_name] = new_config
    st.session_state.active_profile_name = new_name
    
    # 顯示結果
    if is_valid:
        st.success(f"存檔 '{new_name}' 已保存並驗證成功！")
    else:
        st.warning(f"存檔 '{new_name}' 已保存，但驗證失敗: {msg}")
    
    time.sleep(1.5)
    rerun_app()

def show_model_selector(all_models: Dict[str, Dict]) -> Optional[str]:
    """顯示模型選擇器"""
    if not all_models:
        st.warning("⚠️ 沒有可用的模型。請在側邊欄配置API或點擊「發現模型」。")
        return None
    
    categorized_models = get_models_by_category(all_models)
    
    # 獲取當前選中的模型
    current_selection = st.session_state.get('selected_model')
    if current_selection not in all_models:
        current_selection = list(all_models.keys())[0]
        st.session_state.selected_model = current_selection
    
    # 顯示當前選中的模型
    if current_selection:
        model_info = all_models[current_selection]
        st.success(
            f"🎯 當前模型: {model_info.get('icon', '🤖')} "
            f"{model_info.get('name', current_selection)}"
        )
        
        if model_info.get('description'):
            st.caption(f"📝 {model_info['description']}")
    
    st.markdown("---")
    
    # 統計信息
    total_models = len(all_models)
    categories_count = len(categorized_models)
    st.caption(f"📊 可用模型: **{total_models}** 個，分為 **{categories_count}** 個類別")
    
    # 快速搜索
    search_term = st.text_input(
        "🔍 搜索模型",
        placeholder="輸入模型名稱或關鍵詞...",
        help="快速搜索特定模型"
    )
    
    # 過濾模型
    if search_term:
        filtered_models = {}
        for model_id, model_info in all_models.items():
            if (search_term.lower() in model_id.lower() or
                search_term.lower() in model_info.get('name', '').lower()):
                filtered_models[model_id] = model_info
        
        if filtered_models:
            st.write(f"🔍 找到 {len(filtered_models)} 個匹配的模型:")
            show_model_grid(filtered_models, "搜索結果")
        else:
            st.warning("🔍 沒有找到匹配的模型")
        
        return current_selection
    
    # 按類別顯示模型
    for category, models in categorized_models.items():
        show_model_grid(models, category)
    
    return current_selection

def show_model_grid(models: Dict[str, Dict], category_name: str):
    """顯示模型網格"""
    with st.expander(f"📁 {category_name} ({len(models)} 個模型)", expanded=True):
        # 創建網格布局
        cols = st.columns(3)
        
        for i, (model_id, model_info) in enumerate(models.items()):
            col = cols[i % 3]
            
            with col:
                # 模型按鈕
                button_text = f"{model_info.get('icon', '🤖')} {model_info.get('name', model_id)}"
                is_selected = st.session_state.get('selected_model') == model_id
                
                if st.button(
                    button_text,
                    key=f"select_model_{model_id}_{category_name}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state.selected_model = model_id
                    rerun_app()
                
                # 模型描述
                if model_info.get('description') and st.session_state.get('advanced_mode'):
                    st.caption(model_info['description'])

def show_generation_interface():
    """顯示生成界面"""
    # 獲取變體參數
    prompt_default = st.session_state.pop('vary_prompt', '')
    neg_prompt_default = st.session_state.pop('vary_negative_prompt', '')
    
    # 主要參數設置
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 風格選擇
        selected_style = st.selectbox(
            "🎨 風格預設",
            list(STYLE_PRESETS.keys()),
            help="選擇預定義的藝術風格"
        )
        
        # 提示詞
        prompt_val = st.text_area(
            "✍️ 提示詞",
            value=prompt_default,
            height=120,
            placeholder="描述您想要生成的圖像，越詳細越好...",
            help="詳細描述您想要的圖像內容、風格、構圖等"
        )
        
        # 負向提示詞選擇
        neg_preset = st.selectbox(
            "🚫 負向提示詞預設",
            list(NEGATIVE_PROMPTS.keys()),
            help="選擇預定義的負向提示詞"
        )
        
        # 負向提示詞
        negative_prompt_val = st.text_area(
            "🚫 負向提示詞（可選）",
            value=neg_prompt_default or NEGATIVE_PROMPTS.get(neg_preset, ""),
            height=80,
            placeholder="描述您不想要的內容...",
            help="指定您不希望出現在圖像中的元素"
        )
    
    with col2:
        # 生成參數
        n_images = st.slider(
            "🖼️ 生成數量",
            1, MAX_BATCH_SIZE, 1,
            help=f"一次生成的圖片數量（最大 {MAX_BATCH_SIZE}）"
        )
        
        # 圖像尺寸
        size_preset = st.selectbox(
            "📐 圖像尺寸",
            options=list(IMAGE_SIZES.keys()),
            format_func=lambda x: IMAGE_SIZES[x],
            help="選擇圖像的尺寸比例"
        )
        
        # 自定義尺寸
        if size_preset == "自定義...":
            col_w, col_h = st.columns(2)
            with col_w:
                width = st.slider("寬度", 256, 2048, 1024, 64)
            with col_h:
                height = st.slider("高度", 256, 2048, 1024, 64)
            final_size_str = f"{width}x{height}"
        else:
            final_size_str = size_preset
        
        # 高級選項切換
        st.session_state.advanced_mode = st.toggle(
            "🔧 高級選項",
            value=st.session_state.get('advanced_mode', False)
        )
    
    return {
        'prompt': prompt_val,
        'negative_prompt': negative_prompt_val,
        'style': selected_style,
        'size': final_size_str,
        'n_images': n_images
    }

def show_advanced_options(provider: str) -> Dict:
    """顯示高級選項"""
    options = {}
    
    if not st.session_state.get('advanced_mode', False):
        return options
    
    with st.expander("🔧 高級生成參數", expanded=True):
        if provider == "Pollinations.ai":
            col1, col2 = st.columns(2)
            
            with col1:
                options['enhance'] = st.checkbox(
                    "✨ 增強提示詞",
                    value=True,
                    help="自動優化和豐富提示詞"
                )
                options['private'] = st.checkbox(
                    "🔒 私密模式",
                    value=True,
                    help="不在公共畫廊中顯示"
                )
            
            with col2:
                options['nologo'] = st.checkbox(
                    "🚫 移除標誌",
                    value=True,
                    help="移除生成圖片上的水印"
                )
                options['safe'] = st.checkbox(
                    "🛡️ 安全模式",
                    value=False,
                    help="啟用內容安全過濾"
                )
        
        elif provider == "Hugging Face":
            col1, col2 = st.columns(2)
            
            with col1:
                options['num_inference_steps'] = st.slider(
                    "推理步驟",
                    10, 100, 25,
                    help="更多步驟通常產生更好質量"
                )
                options['guidance_scale'] = st.slider(
                    "引導強度",
                    1.0, 20.0, 7.5, 0.5,
                    help="控制對提示詞的遵循程度"
                )
            
            with col2:
                options['scheduler'] = st.selectbox(
                    "調度器",
                    ["DPMSolverMultistep", "EulerDiscrete", "DDIM", "PNDMScheduler"],
                    help="選擇採樣調度器"
                )
    
    return options

# === 主應用邏輯 ===

def main():
    """主應用函數"""
    # 初始化
    init_session_state()
    client = init_api_client()
    cfg = get_active_config()
    api_configured = cfg and cfg.get('validated', False)
    
    # 側邊欄
    with st.sidebar:
        show_sidebar(api_configured, client, cfg)
    
    # 主標題
    st.title(APP_TITLE)
    st.caption(f"支援 FLUX、Stable Diffusion、DALL-E 及更多模型 | {VERSION}")
    
    # 主界面標籤頁
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚀 生成圖像",
        f"📚 歷史 ({len(st.session_state.generation_history)})",
        f"⭐ 收藏 ({len(st.session_state.favorite_images)})",
        "ℹ️ 關於"
    ])
    
    with tab1:
        show_generation_tab(api_configured, client)
    
    with tab2:
        show_history_tab()
    
    with tab3:
        show_favorites_tab()
    
    with tab4:
        show_about_tab()
    
    # 頁腳
    show_footer()

def show_sidebar(api_configured: bool, client, cfg: Dict):
    """顯示側邊欄"""
    show_api_settings()
    
    st.markdown("---")
    
    # API狀態顯示
    if api_configured:
        provider_info = API_PROVIDERS.get(cfg['provider'], {})
        st.success(f"🟢 已連接: {st.session_state.active_profile_name}")
        st.info(f"{provider_info.get('icon', '🤖')} {provider_info.get('name', cfg['provider'])}")
        
        # 模型發現
        can_discover = (client is not None) or (cfg.get('provider') in ["Pollinations.ai", "Hugging Face"])
        
        if st.button("🔍 發現模型", use_container_width=True, disabled=not can_discover):
            with st.spinner("🔍 正在發現可用模型..."):
                discovered = auto_discover_models(client, cfg['provider'], cfg['base_url'])
                st.session_state.discovered_models = discovered
                
                if discovered:
                    st.success(f"✅ 發現 {len(discovered)} 個新模型！")
                else:
                    st.warning("⚠️ 未發現新模型")
                
                time.sleep(1)
                rerun_app()
    
    elif st.session_state.api_profiles:
        st.error(f"🔴 配置錯誤: '{st.session_state.active_profile_name}' 未驗證")
    else:
        st.warning("⚠️ 請配置至少一個API供應商")
    
    st.markdown("---")
    
    # 統計信息
    st.info(f"""
    **📊 使用統計**
    - 歷史記錄: {len(st.session_state.generation_history)}/{MAX_HISTORY_ITEMS}
    - 收藏圖片: {len(st.session_state.favorite_images)}/{MAX_FAVORITE_ITEMS}
    - 批次上限: {MAX_BATCH_SIZE}
    """)
    
    # 快捷操作
    if st.button("🗑️ 清空歷史", use_container_width=True):
        st.session_state.generation_history = []
        st.success("歷史記錄已清空")
        time.sleep(1)
        rerun_app()
    
    if st.button("🗑️ 清空收藏", use_container_width=True):
        st.session_state.favorite_images = []
        st.success("收藏已清空")
        time.sleep(1)
        rerun_app()

def show_generation_tab(api_configured: bool, client):
    """顯示生成標籤頁"""
    if not api_configured:
        st.warning("⚠️ 請在側邊欄配置並驗證API供應商")
        return
    
    # 獲取可用模型
    all_models = merge_models()
    if not all_models:
        st.warning("⚠️ 沒有可用模型。請在側邊欄點擊「發現模型」")
        return
    
    # 模型選擇
    selected_model = show_model_selector(all_models)
    if not selected_model:
        return
    
    st.markdown("---")
    
    # 生成參數設置
    gen_params = show_generation_interface()
    
    # 高級選項
    cfg = get_active_config()
    advanced_options = show_advanced_options(cfg.get('provider', ''))
    
    # 生成按鈕和邏輯
    generation_disabled = (
        not gen_params['prompt'].strip() or
        st.session_state.get('generation_in_progress', False)
    )
    
    button_text = "🎨 正在生成..." if st.session_state.get('generation_in_progress') else "🚀 生成圖像"
    
    if st.button(
        button_text,
        type="primary",
        use_container_width=True,
        disabled=generation_disabled
    ):
        # 構建最終提示詞
        final_prompt = gen_params['prompt']
        if gen_params['style'] != "無" and STYLE_PRESETS[gen_params['style']]:
            final_prompt = f"{final_prompt}, {STYLE_PRESETS[gen_params['style']]}"
        
        # 生成參數
        params = {
            "model": selected_model,
            "prompt": final_prompt,
            "negative_prompt": gen_params['negative_prompt'],
            "size": gen_params['size'],
            "n": gen_params['n_images'],
            **advanced_options
        }
        
        # 顯示生成信息
        model_name = all_models[selected_model]['name']
        with st.spinner(f"🎨 正在使用 {model_name} 生成 {gen_params['n_images']} 張圖像..."):
            success, result = generate_images_with_retry(client, **params)
        
        # 處理結果
        if success and hasattr(result, 'data') and result.data:
            img_b64s = [img.b64_json for img in result.data]
            
            # 添加到歷史
            add_to_history(
                gen_params['prompt'],
                gen_params['negative_prompt'],
                selected_model,
                img_b64s,
                {
                    "size": gen_params['size'],
                    "provider": cfg['provider'],
                    "style": gen_params['style'],
                    "n": gen_params['n_images'],
                    "model_name": model_name,
                    "advanced_options": advanced_options
                }
            )
            
            st.success(f"✨ 成功生成 {len(img_b64s)} 張圖像！")
            
            # 顯示生成的圖像
            if len(img_b64s) == 1:
                display_image_with_actions(
                    img_b64s[0],
                    f"{st.session_state.generation_history[0]['id']}_0",
                    st.session_state.generation_history[0]
                )
            else:
                cols = st.columns(2)
                for i, b64_json in enumerate(img_b64s):
                    with cols[i % 2]:
                        display_image_with_actions(
                            b64_json,
                            f"{st.session_state.generation_history[0]['id']}_{i}",
                            st.session_state.generation_history[0]
                        )
            
            # 清理內存
            gc.collect()
        
        else:
            st.error(f"❌ 生成失敗: {result}")

def show_history_tab():
    """顯示歷史標籤頁"""
    if not st.session_state.generation_history:
        st.info("📭 還沒有生成歷史。快去生成一些圖片吧！")
        return
    
    st.subheader(f"📚 生成歷史 ({len(st.session_state.generation_history)} 條記錄)")
    
    # 歷史記錄操作
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ 清空歷史"):
            st.session_state.generation_history = []
            rerun_app()
    
    # 顯示歷史記錄
    for item in st.session_state.generation_history:
        timestamp_str = item['timestamp'].strftime('%m-%d %H:%M')
        
        # 獲取模型信息
        all_models = merge_models()
        model_info = all_models.get(item['model'], {})
        model_name = model_info.get('name', item['model'])
        
        with st.expander(
            f"🎨 {item['prompt'][:60]}{'...' if len(item['prompt']) > 60 else ''} "
            f"| {model_name} | {timestamp_str}"
        ):
            # 顯示詳細信息
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**✍️ 提示詞:** {item['prompt']}")
                if item.get('negative_prompt'):
                    st.markdown(f"**🚫 負向提示詞:** {item['negative_prompt']}")
            
            with col2:
                st.markdown(f"**🤖 模型:** {model_name}")
                if item.get('metadata', {}).get('style'):
                    st.markdown(f"**🎨 風格:** {item['metadata']['style']}")
                if item.get('metadata', {}).get('size'):
                    st.markdown(f"**📐 尺寸:** {item['metadata']['size']}")
            
            # 顯示圖像
            if len(item['images']) == 1:
                display_image_with_actions(
                    item['images'][0],
                    f"hist_{item['id']}_0",
                    item
                )
            else:
                cols = st.columns(2)
                for i, b64_json in enumerate(item['images']):
                    with cols[i % 2]:
                        display_image_with_actions(
                            b64_json,
                            f"hist_{item['id']}_{i}",
                            item
                        )

def show_favorites_tab():
    """顯示收藏標籤頁"""
    if not st.session_state.favorite_images:
        st.info("⭐ 還沒有收藏的圖像。在生成的圖片上點擊星號收藏吧！")
        return
    
    st.subheader(f"⭐ 我的收藏 ({len(st.session_state.favorite_images)} 張)")
    
    # 收藏操作
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ 清空收藏"):
            st.session_state.favorite_images = []
            rerun_app()
    
    # 顯示收藏的圖像
    sorted_favorites = sorted(
        st.session_state.favorite_images,
        key=lambda x: x['timestamp'],
        reverse=True
    )
    
    cols = st.columns(3)
    for i, fav in enumerate(sorted_favorites):
        with cols[i % 3]:
            display_image_with_actions(
                fav['image_b64'],
                fav['id'],
                fav.get('history_item', {})
            )
            
            # 收藏時間
            fav_time = fav['timestamp'].strftime('%m-%d %H:%M')
            st.caption(f"⭐ 收藏於: {fav_time}")

def show_about_tab():
    """顯示關於標籤頁"""
    st.markdown("""
    # 🎨 AI 圖像生成器 - 完整多模型版
    
    這是一個功能強大的AI圖像生成應用，支持多種頂級AI模型和供應商。
    
    ## ✨ 主要特性
    
    ### 🤖 多模型支持
    - **FLUX 系列**: 最新的高質量圖像生成模型
    - **Stable Diffusion**: 從SD 1.5到SD 3.5的完整系列
    - **專業模型**: DALL-E 3、Midjourney等頂級模型
    - **特化模型**: 動漫、風格化、社區調優模型
    
    ### 🔌 多供應商集成
    - **Pollinations.ai**: 免費開放平台
    - **Hugging Face**: 開源模型中心
    - **NavyAI**: 商業級API服務
    - **OpenAI Compatible**: 標準兼容接口
    
    ### 🎨 豐富的創作工具
    - **30+ 風格預設**: 從攝影到藝術流派
    - **智能提示詞**: 預設和自定義組合
    - **批量生成**: 一次生成多張圖片
    - **歷史管理**: 自動保存和收藏系統
    
    ### 🛠️ 高級功能
    - **分類管理**: 按模型類型組織
    - **搜索功能**: 快速找到目標模型
    - **參數控制**: 專業級生成參數
    - **多格式支持**: 各種尺寸和比例
    
    ## 🚀 使用建議
    
    ### 選擇合適的模型
    - **寫實照片**: SD 3.5 Large, Realistic Vision
    - **藝術創作**: Midjourney, DALL-E 3
    - **動漫風格**: Anything v5, Waifu Diffusion
    - **快速預覽**: Flux Schnell, SDXL Turbo
    
    ### 優化提示詞
    - 使用具體而詳細的描述
    - 結合風格預設增強效果
    - 利用負向提示詞避免不需要的內容
    - 參考成功的歷史記錄
    
    ## 📞 技術支持
    
    如果遇到問題或需要幫助:
    1. 檢查API配置是否正確
    2. 確認網絡連接穩定
    3. 查看模型是否支持當前參數
    4. 參考各供應商的使用限制
    
    ## 🔗 相關資源
    
    - [Pollinations.ai](https://pollinations.ai/)
    - [Hugging Face](https://huggingface.co/)
    - [NavyAI](https://api.navy/)
    - [OpenAI](https://openai.com/)
    
    ---
    
    **版本**: {VERSION}  
    **更新時間**: 2025年10月  
    **開發框架**: Streamlit + Python
    """.format(VERSION=VERSION))

def show_footer():
    """顯示頁腳"""
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #888; margin-top: 2rem;">
        <small>
            🎨 <strong>AI 圖像生成器 {VERSION}</strong> | 
            支持多模型和多供應商 | 
            讓創意無限延伸 🎨
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()