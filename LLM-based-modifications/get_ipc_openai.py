import json
import pandas as pd
import requests
import concurrent.futures
import logging
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
from utils import *
from typing import Optional, List
from ratelimit import limits, sleep_and_retry
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tenacity import retry, stop_after_attempt, wait_exponential
import random
from prompts import *
import openmeteo_requests
import requests_cache
from retry_requests import retry as retry_requests

cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry_requests(cache_session, retries = 5, backoff_factor = 0.2)

results = []

logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])
logger = logging.getLogger(__name__)

load_dotenv()
client = OpenAI()
openmeteo = openmeteo_requests.Client(session =retry_session)

@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=4, min=60, max=200))
@sleep_and_retry
@limits(calls=100, period=60)
def get_lat_lon(district: str) -> Optional[dict]:

    logger.info(f"Retrieving geolocation for {district}")
    

    params = {
        'q': f"{district}, Pakistan",
        'format': 'json',
        'limit': 1
    }
    headers = {
        "User-Agent": "DistrictIPCClassifier/1.0 (safa16salam@gmail.com)"
    }
    response = requests.get(GEOCODE_URL, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    if data:
        logger.info(f"Geolocation retrieved for {district}: {data[0]['lat']}, {data[0]['lon']}")
        return {'lat': float(data[0]['lat']), 'lon': float(data[0]['lon'])}
    logger.warning(f"Geolocation failed for {district}")
    return None


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=4, min=60, max=200))
@sleep_and_retry
@limits(calls=100, period=60)
def get_weather_features(lat: float, lon: float) -> dict:

    logger.info(f"Retrieving weather data for lat/lon: {lat}, {lon}")
    
    base_date = datetime(PREDICTION_DATE[0], PREDICTION_DATE[1], PREDICTION_DATE[2])
    start_date = (base_date - relativedelta(months=BACKDATE_MONTHS)).strftime("%Y-%m-%d")
    end_date = base_date.strftime("%Y-%m-%d")
    
    variable_names = [
        "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "sunshine_duration",
        "precipitation_sum", "rain_sum", "wind_speed_10m_max", "et0_fao_evapotranspiration",
        "relative_humidity_2m_mean", "soil_temperature_0_to_100cm_mean", "soil_moisture_0_to_100cm_mean"
    ]
    params = {
        'latitude': lat,
        'longitude': lon,
        'start_date': start_date,
        'end_date': end_date,
        'daily': variable_names,
        'timezone': 'Asia/Karachi'
    }
    responses = openmeteo.weather_api(HISTORICAL_WEATHER, params=params)
    response = responses[0]
    daily = response.Daily()
    if not daily:
        logger.warning(f"Weather data retrieval failed for lat/lon: {lat}, {lon}")
        raise ValueError("No daily data found in the response.")
        return {}

    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )
    }

    for i, var in enumerate(variable_names):
        daily_data[var] = daily.Variables(i).ValuesAsNumpy()

    df = pd.DataFrame(daily_data).set_index("date")

    monthly_avg = df.resample("ME").mean()

    monthly_dict = {
        month.strftime("%Y-%m"): row.to_dict()
        for month, row in monthly_avg.iterrows()
    }

    logger.info(f"Monthly weather data retrieved for lat/lon: {lat}, {lon}")
    return monthly_dict


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
@sleep_and_retry
@limits(calls=10000, period=60)
def get_ipc(district: str, articles: List[dict], traditional_data:dict, model_name: str = MODEL) -> Optional[IPC]:
    full_prompt = PROMPT_IPC_TEMPLATE.substitute(
        district=district,
        prediction_period=PREDICTION_PERIOD,
    ) + "\n\n".join([
        f"Article {i+1}:\n{article['date']}\n{article['title']}\n" for i, article in enumerate(articles)
    ]) + "\n\n" + "\n".join([
        f"Weather data for {month}:\n{month_data}" for month, month_data in traditional_data.items()
    ]) if traditional_data else ""
    
    # logger.info(f"\nFull prompt for {district}:\n{full_prompt}\n")

    try:
        response = client.beta.chat.completions.parse(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_IPC},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0,
            response_format=IPC
        )
        text = response.choices[0].message

        if text.refusal:
            logger.warning(f"\nModel refused to answer for {district}\n")
            return None
        else:
            return text.parsed

    except Exception as e:
        logger.warning(f"Error calling model for {district}:\n {e}")
        return None

def process_district(district: str, province: str, months_ago_df: pd.DataFrame):
    global results

    logger.info(f"Processing {district}")

    district_articles = months_ago_df[months_ago_df["location"] == district].to_dict(orient="records")
    province_articles = months_ago_df[months_ago_df["location"] == province].to_dict(orient="records")

    if len(district_articles) < NUMBER_OF_ARTICLES:
        logger.warning(f"Not enough articles for {district}. Using province fallback.")
        additional = NUMBER_OF_ARTICLES - len(district_articles)
        random_province_articles = random.sample(province_articles, min(additional, len(province_articles)))
        articles = district_articles + random_province_articles
        # return
    else:
        articles = district_articles[:NUMBER_OF_ARTICLES]

    if not articles:
        logger.warning(f"No articles for {district}")
        return
    weather_data = {}
    try:
        coords = get_lat_lon(district)
        if not coords:
            logger.warning(f"Geolocation failed for {district}")
        weather_data = get_weather_features(coords['lat'], coords['lon'])
    except Exception as e:
        logger.warning(f"Weather data retrieval failed for {district}: {e}")
        return

    try:
        ipc_result = get_ipc(district=district, articles=articles, traditional_data = weather_data, model_name=MODEL)
        ipc_phase = ipc_result.ipc_phase if ipc_result else None
        justification = ipc_result.justification if ipc_result else None
    except Exception as e:
        return

    new_row = pd.DataFrame([{
        "district": district,
        "province": province,
        "prediction_period": PREDICTION_PERIOD,
        "ipc_phase": ipc_phase,
        "articles": json.dumps(articles, default=str),
        "justification": justification,
        "features": json.dumps(weather_data),
        "weather_data": json.dumps(weather_data, default=str),
    }])

    results.append(new_row)
    logger.info(f"Results saved for {district}.")

def main():
    global results
    results_df = pd.DataFrame(columns=["district", "province", "prediction_period", "ipc_phase", "articles", "justification", "weather_data"])
    
    df = pd.read_csv(INPUT_FILE)
    months_ago = datetime(PREDICTION_DATE[0], PREDICTION_DATE[1], PREDICTION_DATE[2]) - relativedelta(months=BACKDATE_MONTHS)
    months_ago_df = df[df["date"] >= months_ago.strftime('%Y-%m-%d')].sort_values(by=["date"], ascending=False)

    districts_with_provinces = list(DISTRICT_PROVINCE.items())

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [
            executor.submit(process_district, district, province, months_ago_df)
            for district, province in districts_with_provinces
        ]

    results_df = pd.concat(results, ignore_index=True)
    results_df.to_csv(RESULTS_FILE, index=False)

if __name__ == "__main__":
    main()