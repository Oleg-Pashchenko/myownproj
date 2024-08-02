import requests
import bs4
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_detail_page(url, headers):
    retries = 3
    while retries > 0:
        try:
            resp2 = requests.get(url, headers=headers, stream=True, verify=False)
            resp2.raise_for_status()
            return resp2.text
        except requests.exceptions.RequestException as e:
            print(f'Error fetching detail URL {url}: {e}')
            retries -= 1
            if retries == 0:
                return None
            time.sleep(5)  # Wait for 5 seconds before retrying


def get_stats():
    url = 'http://abitur.penzgtu.ru/ru/'

    # Set headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.RequestException as e:
        print(f'Error fetching main URL: {e}')
        return 'Ошибка при получении данных'

    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    table = soup.find('div', {'class': 'table'})
    if not table:
        return 'Ошибка при получении данных'

    trs = table.find_all('tr')
    answer = ''
    summary_count = 0
    details = []
    for tr in trs[1::]:
        try:
            count = int(tr.find_all('td')[2].text)
            td = tr.find_all('td')[1]
            detail_url = 'http://abitur.penzgtu.ru/ru' + td.find_next('a').get('href')
            text = td.text.strip()
            details.append((detail_url, text, count))
        except Exception as e:
            continue  # Skip to the next row if there's an error

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetch_detail_page, detail_url, headers): (detail_url, text, count) for detail_url, text, count in details}

        for future in as_completed(future_to_url):
            detail_url, text, count = future_to_url[future]
            try:
                resp_text = future.result()
                if resp_text:
                    soup2 = bs4.BeautifulSoup(resp_text, 'html.parser')
                    blues = len(soup2.find_all('tr', {'style': 'background: #00B9FF; color: #ffffff !important;'}))
                    answer += f'{text} - {count - blues} ({blues} / {count})\n'
                    summary_count += count - blues
            except Exception as e:
                print(f'Error processing detail page for {detail_url}: {e}')

    answer += f'Свободных мест: {summary_count}'
    return answer

