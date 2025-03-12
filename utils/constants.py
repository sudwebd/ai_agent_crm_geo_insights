CREDENTIALS = "keys/credentials.json"
TOKENS = "keys/tokens.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/gmail.send"]

ANALYSIS_PROMPT = """
I have a dataset containing customer purchase data with the following columns:
- Customer Name
- Full Address (including Street, City, State, Country)
- Latitude
- Longitude
- Quantity Purchased
- Total Purchase Value (USD)
- Purchase Date

This data is from an e-commerce business selling products across multiple regions. I need you to generate actionable business insights and recommendations for improving customer engagement and increasing sales. Specifically, I want insights on the following:

1. **Customer Segmentation:**
   - Identify high-value vs. low-value customers based on Total Purchase Value.
   - Segment customers by purchase frequency and volume.
   - Provide recommendations for personalized marketing strategies for each segment.

2. **Geographical Analysis:**
   - Analyze sales distribution by region (City, State, and Country).
   - Identify regions with high sales potential or underperformance.
   - Suggest location-based marketing campaigns or expansion opportunities.

3. **Purchase Trends:**
   - Identify seasonal or time-based purchase patterns.
   - Determine top-selling products or categories.
   - Provide insights on inventory planning and sales forecasting.

4. **Actionable Recommendations:**
   - Suggest personalized promotions or upsell opportunities for each customer segment.
   - Recommend retention strategies for high-value customers.
   - Propose re-engagement tactics for inactive or low-value customers.

"""

# Construct the full prompt with an explicit JSON schema request
FULL_PROMPT = f"""
{ANALYSIS_PROMPT}

Generate the report **ONLY in HTML format**, ensuring structured sections for each type of insight:
1. **Customer Segmentation Insights:**
   - Detailed Analysis:
   - Actionable Recommendations:
2. **Geographical Analysis Insights:**
   - Detailed Analysis:
   - Actionable Recommendations:
3. **Purchase Trends Insights:**
   - Detailed Analysis:
   - Actionable Recommendations:
4. **Overall Business Recommendations:**
   - Key Strategies:
   - Expected Impact:

Be concise but insightful, and ensure the recommendations are practical for implementation in a CRM strategy.

### **Formatting Rules:**
- The report **must** use:
  - `<h2>` for main sections.
  - `<h3>` for sub-sections.
  - `<ul>` and `<li>` for bullet points.
  - `<strong>` for key highlights.
- **Do NOT use plain paragraphs (`<p>`) for insights or recommendations**.
- **Do NOT wrap the HTML inside Markdown-style code fences (` ```html `).**

Here is the customer data:
"""