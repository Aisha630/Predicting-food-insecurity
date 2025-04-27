import json
import pandas as pd
from openai import OpenAI
import concurrent.futures
from tqdm import tqdm
import logging
from dotenv import load_dotenv
from argparse import ArgumentParser
from utils import *
from typing import Optional
from pathlib import Path
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_exponential
from prompts import *

file_handler = logging.FileHandler("district_classifier_urdupoint.log", mode="w")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(color_formatter)

logging.basicConfig(
    level=logging.WARNING,
    handlers=[
        file_handler,
        stream_handler
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()
client = OpenAI()

@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
@sleep_and_retry
@limits(calls=20000, period=60)
def classify_districts(content: str, title: str,  model_name: str = MODEL) -> Optional[Classification]:
    full_prompt = PROMPT + f'\n\nArticle:\n"""{content}"""'
    try:
        response = client.beta.chat.completions.parse(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0,
            response_format=Classification
        )
        text = response.choices[0].message

        if text.refusal:
            logger.warning(f"\nModel refused to answer for article: {title}\n")
            return None
        else:
            return text.parsed

    except Exception as e:
        logger.warning(f"Error calling model for {title}:\n {e}\n")
        return None


def load_existing_titles(output_file: Path):
    if output_file.exists():
        existing_df = pd.read_csv(output_file)
        return set(existing_df['title'].dropna().tolist())
    return set()


def process_article(article: dict, existing_titles: set, district: str, csv_output_file: Path, idx: int, model_name:str=MODEL):
    title = article.get("title", "").strip()
    date = article.get("date", "").strip()
    content = article.get("content", "").strip()

    if not content or title in existing_titles:
        logger.warning(f"⚠️ Skipping article {idx + 1}: {title} (already processed or empty content)")
        return

    logger.info(f"\n🚀 Processing article {idx + 1}: {title} with {model_name}")
    result = classify_districts(content, title, model_name)

    if result:
        row = {
            "title": title,
            "date": date,
            "districts_mentioned": district,
            "relevant_features": ", ".join(result.relevant_features_present or None)
        }

        df = pd.DataFrame([row])
        if csv_output_file.exists():
            df.to_csv(csv_output_file, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_output_file, index=False)

        logger.info(f"✅ Appended article {idx + 1} to {csv_output_file} using {model_name}")
    else:
        logger.warning(f"⚠️ Unable to process {idx + 1}: {title}")
        # logger.warning(f"⚠️ No districts mentioned for article {idx + 1}: {title}")


def main(files: list, csv_output_file: Path, model_name: str=MODEL):
    for json_input_file in files:
        file_path = Path("district_articles_translated") / json_input_file
        with file_path.open('r', encoding='utf-8') as f:
            articles = json.load(f)
        district = json_input_file.split("_")[0]
        logger.info(f"📄 Loaded {len(articles)} articles from {json_input_file}")
        existing_titles = load_existing_titles(csv_output_file)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(process_article, article, existing_titles, district, csv_output_file, idx, model_name)
                for idx, article in enumerate(articles)
            ]

            for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing"):
                pass

        logger.info(f"✅ Finished processing articles and updating {csv_output_file} using {model_name}")


if __name__ == "__main__":
    parser = ArgumentParser(description="District Classifier")
    parser.add_argument("--output_file", help="Output CSV file to save results", default="output-urdupoint.csv", required=False)
    args = parser.parse_args()

    input_files = list(Path("district_articles_translated").glob("*.json"))
    csv_output_file = Path(args.output_file)

    main(input_files, csv_output_file)
