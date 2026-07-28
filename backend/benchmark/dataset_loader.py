import asyncio
import os
from .config import DATASET_DIR, DOCUMENT_CATEGORIES, DOCUMENT_SIZES, DOCUMENTS_PER_CATEGORY
from api.dependencies import get_llm_service

async def generate_document(llm_service, category: str, size: str) -> str:
    word_count_map = {"Small": 200, "Medium": 500, "Large": 1000}
    prompt = (
        f"Generate a realistic {size.lower()} {category} for a fictional enterprise company. "
        f"It should be detailed, realistic, and contain multiple sections. "
        f"Target approximately {word_count_map.get(size, 500)} words. "
        f"Use proper Markdown formatting with headers, lists, and bold text. "
        f"Do not include introductory text, just output the document."
    )
    print(f"Requesting {size} {category} from LLM provider...")
    result = await llm_service.generate_raw(prompt)
    print(f"Generated {size} {category} using {result.get('provider')} ({result.get('model')}) in {result.get('latency_ms')}ms")
    return result["text"]

async def _gen_and_save(llm_service, category: str, size: str, index: int):
    filename = f"{category.replace(' ', '_')}_{size}_{index}.md"
    filepath = DATASET_DIR / filename
    
    if filepath.exists():
        print(f"Skipping {filename}, already exists.")
        return
        
    print(f"Generating {size} {category} ({index+1}/{DOCUMENTS_PER_CATEGORY})...")
    try:
        content = await generate_document(llm_service, category, size)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved {filename}")
    except Exception as e:
        print(f"Failed to generate {filename}: {e}")

async def generate_datasets():
    llm_service = get_llm_service()
    
    for category in DOCUMENT_CATEGORIES:
        for size in DOCUMENT_SIZES:
            for i in range(DOCUMENTS_PER_CATEGORY):
                await _gen_and_save(llm_service, category, size, i)
                await asyncio.sleep(5)  # Rate limit pacing
    print("Dataset generation complete.")

if __name__ == "__main__":
    asyncio.run(generate_datasets())
