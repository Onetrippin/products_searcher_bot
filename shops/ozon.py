import json
from typing import Tuple
import re
import html

from curl_cffi.requests.exceptions import HTTPError
from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser


url = 'https://www.ozon.ru/'

async def get_first_search_request(session: AsyncSession, query: str) -> Tuple[str, list, int]:
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '__Secure-ETC=077eaf8ff1c5e2c143f65421cf9ec9b1; __Secure-ab-group=6; __Secure-user-id=0; __Secure-access-token=6.0.IqrHU-kJSEGqwZJR0RcVuA.6.AYGan5VjrDL7qC40rqNFChE9Fp66v08WXx1DhsH4GZpTuS3MlpzUNiLHNj_xq5VGww..20250114002806.8rsTEsirM5ViChqdcFIim6tWu1tYs6WIIAvMM8qDOUU.1e188b8dae674d308; __Secure-refresh-token=6.0.IqrHU-kJSEGqwZJR0RcVuA.6.AYGan5VjrDL7qC40rqNFChE9Fp66v08WXx1DhsH4GZpTuS3MlpzUNiLHNj_xq5VGww..20250114002806.nLfD87kFQM13h4_Rl-RND7AnhZRxhZ54qwBRBHTG3xU.1d60f7d9b860363ec; TS0121feed=0187c00a180278ba983e07f0e55dd89d2b6c6dcd8de3f7bdf6081dc65d0c84f3349f3cab4e67b1365f863379fae305d795362e5c8a; xcid=c5928c055f716fefc8b9f89ab34506cd; __Secure-ext_xcid=c5928c055f716fefc8b9f89ab34506cd; ADDRESSBOOKBAR_WEB_CLARIFICATION=1736807287; TS0149423d=0187c00a18c122bd7a1bcb3476f8da0c3de0523dc80fff9c7e5bd9d7bca06aa25c89d8b3c18def41539e9f4f4f814f4c8564ae3bee; rfuid=NjkyNDcyNDUyLDEyNC4wNDM0NzUyNzUxNjA3NCwxMDQ0MjEyNTc2LC0xLC01NTczNTY4MSxXM3NpYm1GdFpTSTZJbEJFUmlCV2FXVjNaWElpTENKa1pYTmpjbWx3ZEdsdmJpSTZJbEJ2Y25SaFlteGxJRVJ2WTNWdFpXNTBJRVp2Y20xaGRDSXNJbTFwYldWVWVYQmxjeUk2VzNzaWRIbHdaU0k2SW1Gd2NHeHBZMkYwYVc5dUwzQmtaaUlzSW5OMVptWnBlR1Z6SWpvaWNHUm1JbjBzZXlKMGVYQmxJam9pZEdWNGRDOXdaR1lpTENKemRXWm1hWGhsY3lJNkluQmtaaUo5WFgwc2V5SnVZVzFsSWpvaVEyaHliMjFsSUZCRVJpQldhV1YzWlhJaUxDSmtaWE5qY21sd2RHbHZiaUk2SWxCdmNuUmhZbXhsSUVSdlkzVnRaVzUwSUVadmNtMWhkQ0lzSW0xcGJXVlVlWEJsY3lJNlczc2lkSGx3WlNJNkltRndjR3hwWTJGMGFXOXVMM0JrWmlJc0luTjFabVpwZUdWeklqb2ljR1JtSW4wc2V5SjBlWEJsSWpvaWRHVjRkQzl3WkdZaUxDSnpkV1ptYVhobGN5STZJbkJrWmlKOVhYMHNleUp1WVcxbElqb2lRMmh5YjIxcGRXMGdVRVJHSUZacFpYZGxjaUlzSW1SbGMyTnlhWEIwYVc5dUlqb2lVRzl5ZEdGaWJHVWdSRzlqZFcxbGJuUWdSbTl5YldGMElpd2liV2x0WlZSNWNHVnpJanBiZXlKMGVYQmxJam9pWVhCd2JHbGpZWFJwYjI0dmNHUm1JaXdpYzNWbVptbDRaWE1pT2lKd1pHWWlmU3g3SW5SNWNHVWlPaUowWlhoMEwzQmtaaUlzSW5OMVptWnBlR1Z6SWpvaWNHUm1JbjFkZlN4N0ltNWhiV1VpT2lKTmFXTnliM052Wm5RZ1JXUm5aU0JRUkVZZ1ZtbGxkMlZ5SWl3aVpHVnpZM0pwY0hScGIyNGlPaUpRYjNKMFlXSnNaU0JFYjJOMWJXVnVkQ0JHYjNKdFlYUWlMQ0p0YVcxbFZIbHdaWE1pT2x0N0luUjVjR1VpT2lKaGNIQnNhV05oZEdsdmJpOXdaR1lpTENKemRXWm1hWGhsY3lJNkluQmtaaUo5TEhzaWRIbHdaU0k2SW5SbGVIUXZjR1JtSWl3aWMzVm1abWw0WlhNaU9pSndaR1lpZlYxOUxIc2libUZ0WlNJNklsZGxZa3RwZENCaWRXbHNkQzFwYmlCUVJFWWlMQ0prWlhOamNtbHdkR2x2YmlJNklsQnZjblJoWW14bElFUnZZM1Z0Wlc1MElFWnZjbTFoZENJc0ltMXBiV1ZVZVhCbGN5STZXM3NpZEhsd1pTSTZJbUZ3Y0d4cFkyRjBhVzl1TDNCa1ppSXNJbk4xWm1acGVHVnpJam9pY0dSbUluMHNleUowZVhCbElqb2lkR1Y0ZEM5d1pHWWlMQ0p6ZFdabWFYaGxjeUk2SW5Ca1ppSjlYWDFkLFd5SnlkUzFTVlNKZCwwLDEsMCwyNCwyMzc0MTU5MzAsOCwyMjcxMjY1MjAsMCwxLDAsLTQ5MTI3NTUyMyxSMjl2WjJ4bElFbHVZeTRnVG1WMGMyTmhjR1VnUjJWamEyOGdWMmx1TXpJZ05TNHdJQ2hYYVc1a2IzZHpJRTVVSURFd0xqQTdJRmRwYmpZME95QjROalFwSUVGd2NHeGxWMlZpUzJsMEx6VXpOeTR6TmlBb1MwaFVUVXdzSUd4cGEyVWdSMlZqYTI4cElFTm9jbTl0WlM4eE16RXVNQzR3TGpBZ1UyRm1ZWEpwTHpVek55NHpOaUF5TURBek1ERXdOeUJOYjNwcGJHeGgsZXlKamFISnZiV1VpT25zaVlYQndJanA3SW1selNXNXpkR0ZzYkdWa0lqcG1ZV3h6WlN3aVNXNXpkR0ZzYkZOMFlYUmxJanA3SWtSSlUwRkNURVZFSWpvaVpHbHpZV0pzWldRaUxDSkpUbE5VUVV4TVJVUWlPaUpwYm5OMFlXeHNaV1FpTENKT1QxUmZTVTVUVkVGTVRFVkVJam9pYm05MFgybHVjM1JoYkd4bFpDSjlMQ0pTZFc1dWFXNW5VM1JoZEdVaU9uc2lRMEZPVGs5VVgxSlZUaUk2SW1OaGJtNXZkRjl5ZFc0aUxDSlNSVUZFV1Y5VVQxOVNWVTRpT2lKeVpXRmtlVjkwYjE5eWRXNGlMQ0pTVlU1T1NVNUhJam9pY25WdWJtbHVaeUo5ZlgxOSw2NSw1MjEwNTE5MTEsMSwxLC0xLDE2OTk5NTQ4ODcsMTY5OTk1NDg4NywzMzYwMDc5MzMsNg==; abt_data=7.TFTppsObvrOel4Tlz6zkqb0pQUuZn-fxsxVgsvDGdSzPMkleLMoeHJi5jvXNlQyAQpfTxKOPcvZFZRK7TiNDA9wLsDT3I_NhZzEJss17M6blD83PwicJk7Hvdp-YeeyPQ1tvk_ZD3CSrkaQli_nflZ2H6coIb1Sbdaj_QB3xGs2BPYxy-L4bXnaaILvKtlILrr59wnnq9ol4EBLJHfCOup2LDmehjmVG7fuayMHaozWVdX-rkwGE-7FIWdcAbkxH1fnsxfQXRC6zwDk3R6rK5cnSkvWuOZ-ktnteFAiPB7rz98A-vnZKbvEGKL45wzVIphseU5o-NqpH2pYwqSChnm8JOpKTY6PrLwu89H8RyL3jW_TdNd7VUfdGsqK70e04LbaiEtLxheCKWnvd83Qy_u3r4C_peg4mgWg_An6KkXncXGISUpoRM0sSp0gnW8WkOr0iE8Y_TwvOfc8',
        'dnt': '1',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'service-worker-navigation-preload': 'true',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }
    params = {
        'from_global': 'true',
        'sorting': 'price',
        'text': query
    }
    try:
        response = await session.get(f'{url}search',
                                     headers=headers,
                                     params=params)
        response.raise_for_status()
        next_url = await get_redirect_link(response.text)
    except HTTPError as err:
        print(f'Ошибка {err} при отправке запроса к озону')
        return '', [], 0
    if not next_url:
        return await parse_first_search_request(response.text)
    try:
        response = await session.get(next_url,
                                     headers=headers)
        response.raise_for_status()
        return await parse_first_search_request(response.text)
    except HTTPError as err:
        print(f'Ошибка {err} при отправке запроса к озону')
        return '', [], 0

async def get_redirect_link(html_code: str) -> str:
    tree = HTMLParser(html_code)
    script_tags = tree.css('script[type="application/javascript"]')
    for script in script_tags:
        script_content = script.text()
        if 'location.replace' in script_content:
            start_index = script_content.find('location.replace("') + len('location.replace("')
            end_index = script_content.find('");')
            raw_url = script_content[start_index:end_index]
            decoded_url = raw_url.replace(r'\/', '/').encode().decode('unicode_escape')
            return decoded_url

async def parse_first_search_request(html_code: str) -> Tuple[str, list, int]:
    tree = HTMLParser(html_code)
    client_state = tree.css_first('div.client-state')
    search_results = client_state.css_first('div[id*="searchResultsV2"]')
    if not search_results:
        return '', [], 0
    data_state = json.loads(search_results.attrs['data-state'])
    products = data_state.get('items')
    products_list = await get_products_info(products)
    mega_paginator = client_state.css_first('div[id*="megaPaginator"]')
    data_state = json.loads(mega_paginator.attrs['data-state'])
    next_url = data_state.get('nextPage')
    total_products = int(re.search(r'"totalFound":(\d+)', html_code).group(1))
    return next_url, products_list, total_products

async def get_products_info(products: dict) -> list:
    products_list = []
    for product in products:
        product_info = {'link': f'{url[:-1]}{product.get("action").get("link")}'}
        atoms = product.get('mainState')
        for atom in atoms:
            atom_object = atom.get('atom')
            if not atom_object:
                continue
            atom_type = atom_object.get('type')
            if atom_type == 'priceV2':
                price = atom_object.get('priceV2', {}).get('price')
                product_info['price'] = int(price[0].get('text').replace(' ', '').replace('\u2009', '')[:-1].strip())
                if len(price) > 1:
                    product_info['orig_price'] = int(price[1].get('text').replace(' ', '').replace('\u2009', '')[:-1].strip())
                    product_info['discount'] = atom_object.get('priceV2', {}).get('discount').replace('\u2212', '')
            elif atom_type == 'textAtom':
                title = html.unescape(atom_object.get('textAtom', {}).get('text'))
                title_32 = re.sub(r'&#[xX]?[0-9a-fA-F]+;', '', title)[:29]
                product_info['full_title'] = title
                product_info['title'] = title_32[:title_32.rfind(' ')] + '...'
            elif atom_type == 'labelList':
                item = atom_object.get('labelList', {}).get('items')[0]
                if item.get('icon', {}).get('tintColor') == 'ozRating':
                    product_info['rating'] = item.get('title').strip()
        product_info['image'] = product.get('tileImage', {}).get('items')[0].get('image', {}).get('link')
        product_info['shop'] = 'Ozon'
        products_list.append(product_info)
    return products_list

async def get_not_first_search_request(session: AsyncSession, now_url: str) -> Tuple[str, list, int]:
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '__Secure-user-id=0; __Secure-ab-group=65; xcid=0b08f598c0a46e92fc9363f3c445d820; __Secure-ext_xcid=0b08f598c0a46e92fc9363f3c445d820; rfuid=NjkyNDcyNDUyLDEyNC4wNDM0NzUyNzUxNjA3NCwxMDQ0MjEyNTc2LC0xLC0xMTI5MzU3NTU4LFczc2libUZ0WlNJNklsQkVSaUJXYVdWM1pYSWlMQ0prWlhOamNtbHdkR2x2YmlJNklsQnZjblJoWW14bElFUnZZM1Z0Wlc1MElFWnZjbTFoZENJc0ltMXBiV1ZVZVhCbGN5STZXM3NpZEhsd1pTSTZJbUZ3Y0d4cFkyRjBhVzl1TDNCa1ppSXNJbk4xWm1acGVHVnpJam9pY0dSbUluMHNleUowZVhCbElqb2lkR1Y0ZEM5d1pHWWlMQ0p6ZFdabWFYaGxjeUk2SW5Ca1ppSjlYWDBzZXlKdVlXMWxJam9pUTJoeWIyMWxJRkJFUmlCV2FXVjNaWElpTENKa1pYTmpjbWx3ZEdsdmJpSTZJbEJ2Y25SaFlteGxJRVJ2WTNWdFpXNTBJRVp2Y20xaGRDSXNJbTFwYldWVWVYQmxjeUk2VzNzaWRIbHdaU0k2SW1Gd2NHeHBZMkYwYVc5dUwzQmtaaUlzSW5OMVptWnBlR1Z6SWpvaWNHUm1JbjBzZXlKMGVYQmxJam9pZEdWNGRDOXdaR1lpTENKemRXWm1hWGhsY3lJNkluQmtaaUo5WFgwc2V5SnVZVzFsSWpvaVEyaHliMjFwZFcwZ1VFUkdJRlpwWlhkbGNpSXNJbVJsYzJOeWFYQjBhVzl1SWpvaVVHOXlkR0ZpYkdVZ1JHOWpkVzFsYm5RZ1JtOXliV0YwSWl3aWJXbHRaVlI1Y0dWeklqcGJleUowZVhCbElqb2lZWEJ3YkdsallYUnBiMjR2Y0dSbUlpd2ljM1ZtWm1sNFpYTWlPaUp3WkdZaWZTeDdJblI1Y0dVaU9pSjBaWGgwTDNCa1ppSXNJbk4xWm1acGVHVnpJam9pY0dSbUluMWRmU3g3SW01aGJXVWlPaUpOYVdOeWIzTnZablFnUldSblpTQlFSRVlnVm1sbGQyVnlJaXdpWkdWelkzSnBjSFJwYjI0aU9pSlFiM0owWVdKc1pTQkViMk4xYldWdWRDQkdiM0p0WVhRaUxDSnRhVzFsVkhsd1pYTWlPbHQ3SW5SNWNHVWlPaUpoY0hCc2FXTmhkR2x2Ymk5d1pHWWlMQ0p6ZFdabWFYaGxjeUk2SW5Ca1ppSjlMSHNpZEhsd1pTSTZJblJsZUhRdmNHUm1JaXdpYzNWbVptbDRaWE1pT2lKd1pHWWlmVjE5TEhzaWJtRnRaU0k2SWxkbFlrdHBkQ0JpZFdsc2RDMXBiaUJRUkVZaUxDSmtaWE5qY21sd2RHbHZiaUk2SWxCdmNuUmhZbXhsSUVSdlkzVnRaVzUwSUVadmNtMWhkQ0lzSW0xcGJXVlVlWEJsY3lJNlczc2lkSGx3WlNJNkltRndjR3hwWTJGMGFXOXVMM0JrWmlJc0luTjFabVpwZUdWeklqb2ljR1JtSW4wc2V5SjBlWEJsSWpvaWRHVjRkQzl3WkdZaUxDSnpkV1ptYVhobGN5STZJbkJrWmlKOVhYMWQsV3lKeWRTMVNWU0pkLDAsMSwwLDI0LDIzNzQxNTkzMCw4LDIyNzEyNjUyMCwwLDEsMCwtNDkxMjc1NTIzLFIyOXZaMnhsSUVsdVl5NGdUbVYwYzJOaGNHVWdSMlZqYTI4Z1YybHVNeklnTlM0d0lDaFhhVzVrYjNkeklFNVVJREV3TGpBN0lGZHBialkwT3lCNE5qUXBJRUZ3Y0d4bFYyVmlTMmwwTHpVek55NHpOaUFvUzBoVVRVd3NJR3hwYTJVZ1IyVmphMjhwSUVOb2NtOXRaUzh4TWprdU1DNHdMakFnVTJGbVlYSnBMelV6Tnk0ek5pQXlNREF6TURFd055Qk5iM3BwYkd4aCxleUpqYUhKdmJXVWlPbnNpWVhCd0lqcDdJbWx6U1c1emRHRnNiR1ZrSWpwbVlXeHpaU3dpU1c1emRHRnNiRk4wWVhSbElqcDdJa1JKVTBGQ1RFVkVJam9pWkdsellXSnNaV1FpTENKSlRsTlVRVXhNUlVRaU9pSnBibk4wWVd4c1pXUWlMQ0pPVDFSZlNVNVRWRUZNVEVWRUlqb2libTkwWDJsdWMzUmhiR3hsWkNKOUxDSlNkVzV1YVc1blUzUmhkR1VpT25zaVEwRk9UazlVWDFKVlRpSTZJbU5oYm01dmRGOXlkVzRpTENKU1JVRkVXVjlVVDE5U1ZVNGlPaUp5WldGa2VWOTBiMTl5ZFc0aUxDSlNWVTVPU1U1SElqb2ljblZ1Ym1sdVp5SjlmWDE5LDY1LDUyMTA1MTkxMSwxLDEsLTEsMTY5OTk1NDg4NywxNjk5OTU0ODg3LDMzNjAwNzkzMyw2; is_cookies_accepted=1; __Secure-access-token=6.0.0PyJUInaTRmZmfFgyvwz9A.65.AfH1pIWJ_r-mCv5HT7YCSkPmA_0L1PscwhSW6mllJN8sGi61dSjC2Mr4kFM3UwTTdA..20241020194849.knQc1AzIH6aOC68Q3xm4s6m4PTesU_yVTg03vPeb5uw.16743d37b9cfff11d; __Secure-refresh-token=6.0.0PyJUInaTRmZmfFgyvwz9A.65.AfH1pIWJ_r-mCv5HT7YCSkPmA_0L1PscwhSW6mllJN8sGi61dSjC2Mr4kFM3UwTTdA..20241020194849.o6aqBmqrehVltE1swx_MOTaJ_Qt8RYJp_Mhf2QvVQLY.1ee471951dd0baf1c; __Secure-ETC=a36c1f57e4cf421799e41bb3e9168319; abt_data=7.3mzE6kYPxZA7to5l6E4_hKoArFucaZnNdD40ppj9wQqygVW6IzdF5XiicZSkeLSXcajVvhVfkaNrUyU3KlLN4dZlIsKMeCPTPAM9ONky1gPH8YoQB9sJmYqiZlLP9NrVcGuhC2BotgO7jNqmYZeqGdasRY7dLEipciwa6_wnX3b-hor0-AoRQ3AmBq6r3IwlB_RuqKwE8GqDE_sOedKGw9RkKpR6WLucQoqHP_O6PRZfdyOubJsgUuOPdWrJr4gcDMDcn4aoKwq3ULoPwxoOFNtG-i3RH2cjAf0FTbtbyaz1x8cAE_WO3a1i1viwCAfeWvGHjKzNtnuXc-RyrWJU_rR7mOYavhEJQDrmpkT5RO7sWAvaSNufGgx84O2pdB2APeGfmG0Zigc2RQHt0UEVHIIXth9pkbbYsDl_Rshh5iTrC6Iy47nhY0CKmIWznUl-QU_Rxa5dnSzY89Go8zLyZTvUEqS3-b6oPo3gBA',
        'dnt': '1',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'service-worker-navigation-preload': 'true',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }
    try:
        response = await session.get(f'{url}api/entrypoint-api.bx/page/json/v2?url={now_url}',
                                     headers=headers)
        response.raise_for_status()
        return await parse_not_first_search_request(response.text)
    except HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return '', [], 0

async def parse_not_first_search_request(page_code: str) -> Tuple[str, list, int]:
    page_dict = json.loads(page_code)
    widget_states = page_dict.get('widgetStates')
    if not widget_states:
        return '', [], 0
    found_key = None
    for key in widget_states.keys():
        if key.startswith('searchResultsV2'):
            found_key = key
    products = json.loads(widget_states.get(found_key)).get('items')
    products_list = await get_products_info(products)
    return page_dict.get('nextPage'), products_list, 0

async def get_search_result(session: AsyncSession,
                            query: str,
                            offset: int,
                            link: str) -> Tuple[str, list, int]:
    if offset == 0:
        return await get_first_search_request(session, query)
    elif len(link) < 5:
        return '', [], 0
    return await get_not_first_search_request(session, link)