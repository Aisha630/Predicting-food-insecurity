import colorlog
from pydantic import BaseModel
from typing import Optional, List, Literal
import logging
from pathlib import Path
from enum import Enum


MODEL = "gpt-4o" 
# PREDICTION_PERIOD = "Mar-June,2024"
# PREDICTION_DATE = (2024, 3, 1) # this should be the start date of the earliest month in the preiciton period
PREDICTION_PERIOD = "Nov-Mar,2024-2025"
PREDICTION_DATE = (2024, 11, 1)
BACKDATE_MONTHS  = 9
NUMBER_OF_ARTICLES = 30
LOGFILE = Path("logs", "ipc.log")
RESULTS_FILE = Path("outputs", f"results_ipc_{MODEL}_{PREDICTION_PERIOD}.csv")
INPUT_FILE = Path("outputs", "merged_df_new.csv")
IPCFILE = Path("inputs", "pak_ipc.csv")

HISTORICAL_WEATHER = "https://archive-api.open-meteo.com/v1/archive"
GEOCODE_URL = "https://nominatim.openstreetmap.org/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s - %(levelname)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
        }
    )

file_handler = logging.FileHandler(LOGFILE, mode="w")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(color_formatter)


SYSTEM_PROMPT = """
You are a highly accurate geopolitical news analyst specializing in Pakistan. Your task is to analyze news articles and extract two things:

1. The **main Pakistani location** that is central to the article’s narrative. This must be a specific district if possible, or a province if no district qualifies, or "Pakistan" if neither is appropriate. You must apply a strict filtering criterion to avoid false positives.

2. The presence of any **specific humanitarian or socio-political features** from a predefined list. Only extract features that are clearly relevant to the economic, political, or social conditions that could impact food security or signal the potential for a food crisis.

Your analysis must be:
- Highly conservative in assigning relevance—only extract what is justified directly by the text.
- Based on explicit or clearly implied information, with no speculative interpretation.
- Focused on identifying signals that reflect structural vulnerability or acute disruptions that could influence food access, availability, or stability.

Do not include general mentions of locations or features that are not core to the events or conditions described.
"""


DISTRICTS = ["Chagai", "Gwadar", "Jaffarabad", "Jhal Magsi", "Kachhi", "Kalat", "Kech", "Kharan", "Khuzdar", "Killa Abdullah",
    "Qila Saifullah", "Lasbela", "Loralai", "Musakhel", "Nasirabad", "Nushki", "Panjgur", "Pishin", "Quetta", "Sibi",
    "Sohbatpur", "Usta Muhammad", "Washuk", "Zhob", "Ziarat", "Badin", "Dadu", "Ghotki", "Jacobabad", "Jamshoro",
    "Kashmore", "Khairpur", "Larkana", "Mirpur Khas", "Naushahro Feroze", "Qambar Shahdadkot", "Sanghar",
    "Shaheed Benazir Abad", "Shikarpur", "Sujawal", "Tharparkar", "Thatta", "Umer Kot", "Bajaur", "Bannu", "Batagram",
    "Buner", "Chitral Lower", "Chitral Upper", "Dera Ismail Khan", "Hangu", "Karak", "Khyber", "Kohistan Lower",
    "Kohistan Upper", "Kolai Palas Kohistan", "Kurram", "Lakki Marwat", "Lower Dir", "Mohmand", "North Waziristan",
    "Orakzai", "Shangla", "South Waziristan", "Swat", "Tank", "Tor Ghar", "Upper Dir" ]  

DistrictLiteral = Literal[
    "Chagai", "Gwadar", "Jaffarabad", "Jhal Magsi", "Kachhi", "Kalat", "Kech", "Kharan", "Khuzdar", "Killa Abdullah",
    "Qila Saifullah", "Lasbela", "Loralai", "Musakhel", "Nasirabad", "Nushki", "Panjgur", "Pishin", "Quetta", "Sibi",
    "Sohbatpur", "Usta Muhammad", "Washuk", "Zhob", "Ziarat", "Badin", "Dadu", "Ghotki", "Jacobabad", "Jamshoro",
    "Kashmore", "Khairpur", "Larkana", "Mirpur Khas", "Naushahro Feroze", "Qambar Shahdadkot", "Sanghar",
    "Shaheed Benazir Abad", "Shikarpur", "Sujawal", "Tharparkar", "Thatta", "Umer Kot", "Bajaur", "Bannu", "Batagram",
    "Buner", "Chitral Lower", "Chitral Upper", "Dera Ismail Khan", "Hangu", "Karak", "Khyber", "Kohistan Lower",
    "Kohistan Upper", "Kolai Palas Kohistan", "Kurram", "Lakki Marwat", "Lower Dir", "Mohmand", "North Waziristan",
    "Orakzai", "Shangla", "South Waziristan", "Swat", "Tank", "Tor Ghar", "Upper Dir", "Sindh", "Punjab", "Khyber Pakhtunkhwa", "Balochistan", "Gilgit Baltistan", "Azad Jammu and Kashmir"
]


PROVINCES  =["Sindh", "Punjab", "Khyber Pakhtunkhwa", "Balochistan", "Gilgit Baltistan", "Azad Jammu and Kashmir"]
ProvincesLiteral  =Literal["Sindh", "Punjab", "Khyber Pakhtunkhwa", "Balochistan", "Gilgit Baltistan", "Azad Jammu and Kashmir"]


DISTRICT_PROVINCE = {
    # Balochistan
    "Chagai": "Balochistan",
    "Gwadar": "Balochistan",
    "Jaffarabad": "Balochistan",
    "Jhal Magsi": "Balochistan",
    "Kachhi": "Balochistan",
    "Kalat": "Balochistan",
    "Kech": "Balochistan",
    "Kharan": "Balochistan",
    "Khuzdar": "Balochistan",
    "Killa Abdullah": "Balochistan",
    "Qila Saifullah": "Balochistan",
    "Lasbela": "Balochistan",
    "Loralai": "Balochistan",
    "Musakhel": "Balochistan",
    "Nasirabad": "Balochistan",
    "Nushki": "Balochistan",
    "Panjgur": "Balochistan",
    "Pishin": "Balochistan",
    "Quetta": "Balochistan",
    "Sibi": "Balochistan",
    "Sohbatpur": "Balochistan",
    "Usta Muhammad": "Balochistan",
    "Washuk": "Balochistan",
    "Zhob": "Balochistan",
    "Ziarat": "Balochistan",

    # Sindh
    "Badin": "Sindh",
    "Dadu": "Sindh",
    "Ghotki": "Sindh",
    "Jacobabad": "Sindh",
    "Jamshoro": "Sindh",
    "Kashmore": "Sindh",
    "Khairpur": "Sindh",
    "Larkana": "Sindh",
    "Mirpur Khas": "Sindh",
    "Naushahro Feroze": "Sindh",
    "Qambar Shahdadkot": "Sindh",
    "Sanghar": "Sindh",
    "Shaheed Benazir Abad": "Sindh",
    "Shikarpur": "Sindh",
    "Sujawal": "Sindh",
    "Tharparkar": "Sindh",
    "Thatta": "Sindh",
    "Umer Kot": "Sindh",

    # Khyber Pakhtunkhwa
    "Bajaur": "Khyber Pakhtunkhwa",
    "Bannu": "Khyber Pakhtunkhwa",
    "Batagram": "Khyber Pakhtunkhwa",
    "Buner": "Khyber Pakhtunkhwa",
    "Chitral Lower": "Khyber Pakhtunkhwa",
    "Chitral Upper": "Khyber Pakhtunkhwa",
    "Dera Ismail Khan": "Khyber Pakhtunkhwa",
    "Hangu": "Khyber Pakhtunkhwa",
    "Karak": "Khyber Pakhtunkhwa",
    "Khyber": "Khyber Pakhtunkhwa",
    "Kohistan Lower": "Khyber Pakhtunkhwa",
    "Kohistan Upper": "Khyber Pakhtunkhwa",
    "Kolai Palas Kohistan": "Khyber Pakhtunkhwa",
    "Kurram": "Khyber Pakhtunkhwa",
    "Lakki Marwat": "Khyber Pakhtunkhwa",
    "Lower Dir": "Khyber Pakhtunkhwa",
    "Mohmand": "Khyber Pakhtunkhwa",
    "North Waziristan": "Khyber Pakhtunkhwa",
    "Orakzai": "Khyber Pakhtunkhwa",
    "Shangla": "Khyber Pakhtunkhwa",
    "South Waziristan": "Khyber Pakhtunkhwa",
    "Swat": "Khyber Pakhtunkhwa",
    "Tank": "Khyber Pakhtunkhwa",
    "Tor Ghar": "Khyber Pakhtunkhwa",
    "Upper Dir": "Khyber Pakhtunkhwa"
}



# God bless gemini for extracting these form the image. GPT was stupid.
TEXT_FEATURES = [
    "rise", "conflict", "coup", "terrorism", "corruption", "flee", "refugees", "displaced", "migration", "drought",
    "tragedy", "climate change", "siege", "looting", "floods", "foreign troops", "pirates", "human rights abuses",
    "economic crisis", "catastrophe", "repression", "foreign aid", "secession", "land reform", "price rise",
    "natural disaster", "the offensive", "humanitarian situation", "blockade", "food insecurity", "power struggle",
    "asylum seekers", "overthrow", "food crisis", "malnourished", "cyclone", "apathy", "farmland", "military junta",
    "air attack", "military dictatorship", "bombing campaign", "dysfunction", "food assistance", "militia groups",
    "dehydrated", "epidemics", "dictators", "convoys", "cholera outbreak", "corrupt government",
    "environmental degradation", "infant mortality", "humanitarian disaster", "totalitarian", "carbon", "civil strife",
    "pests", "international intervention", "land grab", "gastrointestinal", "d'etat", "rising inflation",
    "police torture", "jihadist groups", "land seizures", "slave trade", "international terrorists", "warlord",
    "rebel insurgency", "burning houses", "ecological crisis", "price of food", "terrorist", "politically engineered",
    "reduced national output", "lack of rains", "internal strife", "years of warfare", "self reliance",
    "major offensive", "alarming level", "water availability", "transport bottleneck", "inadequate rainfall",
    "hunger crises", "aid appeal", "rinderpest", "land invasions", "brutal government", "without international aid",
    "collapse of government", "massive starvation", "locusts", "mass hunger", "greenhouse gases", "mayhem",
    "rising food prices", "call for donations", "withheld relief", "brain drain", "potato blight", "clans",
    "gangs of bandits", "water distribution shortages", "lack of authority", "continued strife", "infrastructure damage",
    "harvest decline", "pushing peasants off", "mismanagement", "scanty rainfall", "forests destroyed",
    "toll on livestock", "makeshift camps", "cycle of poverty", "wreaked havoc", "failed crops", "harvests are devastated",
    "bad harvests", "stolen food aid", "destructive pattern", "slashed export", "regimes were toppled",
    "land degradation", "increased external debt", "man-made disaster", "prolonged fighting", "cattle death",
    "disrupted trade", "prolonged dry spell", "rival warlords", "authoritarian", "shortage of rains",
    "economic impoverishment", "severe rains", "failed rains", "life-threatening hunger", "violent suppression",
    "international embargo", "disruption to farming", "restricted humanitarian access", "clan warfare",
    "collapsing economy", "climatic hazards", "weather extremes", "poor soil quality", "acute hunger",
    "lack of agricultural infrastructure", "lack of roads", "reduced imports", "population crisis", "cattle plague",
    "continued deterioration", "clan battle", "aid workers died", "international alarm", "devastated the economy",
    "anti-western policies", "lack of alternatives", "livestock had died", "abnormally low rainfall",
    "oppressive regimes", "lack of cultivation", "restricted relief flights", "unable to sow", "civilians uprooted"
]
TextLiteral = Literal[
    "rise", "conflict", "coup", "terrorism", "corruption", "flee", "refugees", "displaced", "migration", "drought",
    "tragedy", "climate change", "siege", "looting", "floods", "foreign troops", "pirates", "human rights abuses",
    "economic crisis", "catastrophe", "repression", "foreign aid", "secession", "land reform", "price rise",
    "natural disaster", "the offensive", "humanitarian situation", "blockade", "food insecurity", "power struggle",
    "asylum seekers", "overthrow", "food crisis", "malnourished", "cyclone", "apathy", "farmland", "military junta",
    "air attack", "military dictatorship", "bombing campaign", "dysfunction", "food assistance", "militia groups",
    "dehydrated", "epidemics", "dictators", "convoys", "cholera outbreak", "corrupt government",
    "environmental degradation", "infant mortality", "humanitarian disaster", "totalitarian", "carbon", "civil strife",
    "pests", "international intervention", "land grab", "gastrointestinal", "d'etat", "rising inflation",
    "police torture", "jihadist groups", "land seizures", "slave trade", "international terrorists", "warlord",
    "rebel insurgency", "burning houses", "ecological crisis", "price of food", "terrorist", "politically engineered",
    "reduced national output", "lack of rains", "internal strife", "years of warfare", "self reliance",
    "major offensive", "alarming level", "water availability", "transport bottleneck", "inadequate rainfall",
    "hunger crises", "aid appeal", "rinderpest", "land invasions", "brutal government", "without international aid",
    "collapse of government", "massive starvation", "locusts", "mass hunger", "greenhouse gases", "mayhem",
    "rising food prices", "call for donations", "withheld relief", "brain drain", "potato blight", "clans",
    "gangs of bandits", "water distribution shortages", "lack of authority", "continued strife", "infrastructure damage",
    "harvest decline", "pushing peasants off", "mismanagement", "scanty rainfall", "forests destroyed",
    "toll on livestock", "makeshift camps", "cycle of poverty", "wreaked havoc", "failed crops", "harvests are devastated",
    "bad harvests", "stolen food aid", "destructive pattern", "slashed export", "regimes were toppled",
    "land degradation", "increased external debt", "man-made disaster", "prolonged fighting", "cattle death",
    "disrupted trade", "prolonged dry spell", "rival warlords", "authoritarian", "shortage of rains",
    "economic impoverishment", "severe rains", "failed rains", "life-threatening hunger", "violent suppression",
    "international embargo", "disruption to farming", "restricted humanitarian access", "clan warfare",
    "collapsing economy", "climatic hazards", "weather extremes", "poor soil quality", "acute hunger",
    "lack of agricultural infrastructure", "lack of roads", "reduced imports", "population crisis", "cattle plague",
    "continued deterioration", "clan battle", "aid workers died", "international alarm", "devastated the economy",
    "anti-western policies", "lack of alternatives", "livestock had died", "abnormally low rainfall",
    "oppressive regimes", "lack of cultivation", "restricted relief flights", "unable to sow", "civilians uprooted"
]


class Classification(BaseModel):
    relevant_features_present: Optional[List[TextLiteral]] = None
    location: Optional[List[DistrictLiteral]] = None

# class IPC(BaseModel):
#     ipc_phase: Literal[1,2,3, 4, 5]
#     justification: str



class IPCPhaseEnum(str, Enum):
    phase_1 = "1"
    phase_2 = "2"
    phase_3 = "3"
    phase_4 = "4"
    phase_5 = "5"

class IPC(BaseModel):
    ipc_phase: IPCPhaseEnum
    justification: str
