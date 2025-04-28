from string import Template
from utils import *

# I do not really need to pass the list now here anymore as it is catered to in the Structured outputs Pydantic model

PROMPT = f"""
You are tasked with analyzing the following news article.

OBJECTIVE: Identify the following:

1. The main Pakistani location (district, province, or "Pakistan") that is central to the article.
2. Any relevant features from the list below that are clearly present in the article and relevant to food security.

DISTRICT & LOCATION CLASSIFICATION

Use a tiered classification approach to determine the article’s geographical focus:

Primary: District-level classification  
Use the following official list of districts:  
{', '.join(DISTRICTS)}

Return one or more districts only if they are:
- Locations where key events, crises, or developments are actively taking place, AND
- Central to the narrative of the article.

Do NOT include districts that are:
- Only mentioned in passing or background context.
- Merely the origin/destination of people or goods.
- Referenced without being materially involved in the events.

If no district qualifies, proceed to province-level classification.

Secondary: Province-level classification  
Return the name of the province if:
- It is the main geographic scope of the article.
- The article's events affect the province broadly or at a systemic level.

Examples: "Balochistan", "Sindh", "Khyber Pakhtunkhwa"

Use this list of provinces {', '.join(PROVINCES)}

If no province qualifies, proceed to national classification.

Tertiary: National-level classification  
If neither districts nor provinces are central to the article, but the article focuses on Pakistan as a whole, return:
"Pakistan"

FEATURE EXTRACTION

Use the following list of humanitarian and socio-political features:

{', '.join(TEXT_FEATURES)}

Mark a feature only if it meets all of the following conditions:
- It is explicitly stated or clearly implied in the article.
- It is directly related to the central events or themes.
- It is relevant to economic, political, or social conditions that could impact food security or signal a potential food crisis.

Examples of relevant conditions:
- Agricultural disruption, crop loss, or drought
- Displacement or population movement
- Economic shocks, inflation, market breakdowns
- Governance issues, political instability, or conflict affecting food systems
- Infrastructure damage or humanitarian access barriers

Do NOT include:
- Vaguely mentioned or incidental features
- Generic background info unrelated to food systems or livelihood stress
- Topics not tied to current or emerging socio-economic vulnerability

Make sure you only select your answers from the provided list of features, provinces and districts. If nothing is found, return None.

EXAMPLES

Example 1 — POSITIVE CASE:
Article:
"Severe flooding in Dadu district has destroyed standing crops across hundreds of acres, displacing thousands of families and disrupting local markets. Humanitarian organizations warn of worsening food shortages in interior Sindh."

Output:
Location: ["Dadu"]  
Features: ["flooding", "displacement", "agricultural disruption", "food insecurity"]

Example 2 — NEGATIVE CASE:
Article:
"The Prime Minister met with officials from various provinces to discuss future infrastructure projects and economic growth initiatives. The meeting took place in Islamabad and included representatives from Quetta and Karachi."

Output:
Location: "Pakistan"  
Features: []
"""


SYSTEM_PROMPT_IPC = f"""You are an expert analyst trained in the Integrated Food Security Phase Classification (IPC) framework. Your role is to assess early warning signals from local news to forecast future food insecurity levels in regions of Pakistan.

You will be provided with a summary news articles from months prior to the prediction period—typically more than {BACKDATE_MONTHS} months earlier. Your task is to use these lagged qualitative indicators to predict the most likely IPC Phase for the target prediction period {PREDICTION_PERIOD}, at the district level.

Use the official IPC five-phase scale:
- **Phase 1 (Minimal)**: Households meet basic food and non-food needs without distress.
- **Phase 2 (Stressed)**: Households have minimally adequate food but struggle with essential non-food costs.
- **Phase 3 (Crisis)**: Food gaps emerge or reliance on crisis coping strategies is evident.
- **Phase 4 (Emergency)**: Severe food deficits, high acute malnutrition, and excess mortality risk.
- **Phase 5 (Famine)**: Widespread starvation and death due to catastrophic food insecurity.

You must infer the IPC phase based on trends, risks, and stressors found in earlier news signals, including:
- Food availability and access
- Disruption in markets or supply chains
- Use of negative coping strategies
- Reports of hunger, displacement, or environmental shocks
- Any escalation indicating a transition to higher IPC phases
- Weather data, if available, including temperature and precipitation patterns

Base your reasoning on the evidence, and do not speculate beyond what's supported by the article. You also should take into account the weather data for the months leading up to the prediction period, if available. This data may include temperature, precipitation, and other relevant climatic factors that could influence food security.
"""


PROMPT_IPC_TEMPLATE = Template(f"""
You are analyzing food security trends in the district of **$district**, Pakistan. The following news article was published at most {BACKDATE_MONTHS} months prior to the **prediction period** $prediction_period. Based on its contents, forecast the likely IPC Phase for **$district** during the specified prediction window $prediction_period. You also should take into account the weather data for the months leading up to the prediction period, if available. This data may include temperature, precipitation, and other relevant climatic factors that could influence food security.

Use the Integrated Food Security Phase Classification (IPC) scale:
- Phase 1 (Minimal)
- Phase 2 (Stressed)
- Phase 3 (Crisis)
- Phase 4 (Emergency)
- Phase 5 (Famine)

While analyzing the article, consider:
- Food availability and accessibility
- Household coping mechanisms
- Market disruptions or livelihood loss
- Reports of displacement, environmental hazards, or conflict
- Early indicators of food stress or crisis
- Weather data, if available, including temperature and precipitation patterns

""")


SUMMARIZER_PROMPT = Template(f"""
You are an analyst specializing in food security and humanitarian reporting in Pakistan. Your task is to extract and summarize key information from a collection of news articles related to the district of $district.

Focus on identifying and summarizing the following aspects:

- **Food Availability and Access**: Reports on crop yields, market supplies, food prices, and access to food.
- **Livelihoods and Economic Conditions**: Information on employment, income sources, and economic disruptions.
- **Coping Mechanisms**: Evidence of households employing strategies such as reducing meal sizes, selling assets, or seeking aid.
- **Displacement and Migration**: Instances of population movements due to food insecurity, conflict, or environmental factors.
- **Environmental and Climatic Events**: Occurrences of droughts, floods, or other weather-related events impacting food security.
- **Health and Nutrition**: Reports on malnutrition rates, disease outbreaks, or healthcare access issues.

Structure your summary as follows:

1. **Key Findings**:
   - Bullet-pointed list summarizing the critical information under each category mentioned above.
2. **Notable Quotes**:
   - Include any significant quotes from the articles that highlight the severity or nature of the food security situation.

Ensure that the summary is concise, fact-based, and devoid of speculation. Use clear and neutral language suitable for informing IPC phase classification.

""")
