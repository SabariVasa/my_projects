import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
def web_scrape(request):
    """
    Scrapes multiple HTML tags from a given URL dynamically.
    Extracts content from specified tags and saves as separate CSV files.
    """
    url = request.data.get("url", "")
    tag_list = request.data.get("tags", ["th", "tr", "td", "div", "a", "span"])

    if not isinstance(tag_list, list):
        return Response({"error": "tags must be a list of strings"}, status=400)

    if not url:
        return Response({"error": "URL is required"}, status=400)

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return Response({"error": "Failed to fetch data"}, status=500)

    soup = BeautifulSoup(response.content, 'html.parser')

    extracted_data = []
    table_headers = []
    table_data = []
    other_tag_data = []

    if any(tag in tag_list for tag in ["th", "tr", "td"]):
        rows = soup.find_all("tr")

        for row in rows:
            cols = row.find_all(["th", "td"])
            cols = [col.text.strip().replace("\n", "") for col in cols]

            if cols:
                if not table_headers and row.find_all("th"):
                    table_headers = cols
                else:
                    table_data.append(cols)

    for tag in tag_list:
        if tag not in ["th", "tr", "td"]:
            elements = soup.find_all(tag)
            for element in elements:
                text_content = element.get_text(strip=True)
                other_tag_data.append({"content": text_content})

    if not table_data and not other_tag_data:
        return Response({"error": "No data found for the given tags"}, status=404)

    user_downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    os.makedirs(user_downloads_folder, exist_ok=True)

    csv_table_path = None
    if table_data:
        csv_table_filename = "scraped_table_data.csv"
        csv_table_path = os.path.join(user_downloads_folder, csv_table_filename)
        df_table = pd.DataFrame(table_data, columns=table_headers if table_headers else None)
        df_table.to_csv(csv_table_path, index=False, encoding="utf-8")

    csv_other_tags_path = None
    if other_tag_data:
        csv_other_tags_filename = "scraped_other_tags.csv"
        csv_other_tags_path = os.path.join(user_downloads_folder, csv_other_tags_filename)
        df_other_tags = pd.DataFrame(other_tag_data)
        df_other_tags.to_csv(csv_other_tags_path, index=False, encoding="utf-8")

    return Response({
        "message": "Data scraped and saved successfully",
        "table_csv_file": csv_table_path if table_data else "No table data found",
        "other_tags_csv_file": csv_other_tags_path if other_tag_data else "No non-table data found",
        "table_data_sample": table_data[:5] if table_data else [],
        "other_tags_sample": other_tag_data[:5] if other_tag_data else []
    })
