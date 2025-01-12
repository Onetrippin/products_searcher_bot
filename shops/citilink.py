from typing import Tuple
import json

from curl_cffi.requests.exceptions import HTTPError
from curl_cffi.requests import AsyncSession

from utils.constants import OFFSET_COEFFICIENTS


url = 'https://www.citilink.ru/'

async def get_search_request(session: AsyncSession, query: str, offset: int) -> Tuple[list, int]:
    offset += 1
    headers = {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://www.citilink.ru',
        'priority': 'u=1, i',
        'referer': 'https://www.citilink.ru/search/?text=%D0%BF%D0%B5%D1%80%D0%B5%D1%85%D0%BE%D0%B4%D0%BD%D0%B8%D0%BA&sorting=price_asc',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }
    data = {
        'query': 'query GetFullSearchProductsFilter($fullSearchProductsFilterInput:CatalogFilter_FullSearchFilterInput!){fullSearchFilter(filter:$fullSearchProductsFilterInput){record{...FullSearchProductsFilter},error{... on CatalogFilter_ProductsFilterInternalError{__typename,message},... on CatalogFilter_ProductsFilterIncorrectArgumentsError{__typename,message}}}}fragment FullSearchProductsFilter on CatalogFilter_ProductsFilter{__typename,products{...ProductSnippetFull},sortings{id,name,slug,directions{id,isSelected,name,slug,isDefault}},groups{...SubcategoryProductsFilterGroup},categories{...FilterCategoryInfo},pageInfo{...Pagination},searchStrategy}fragment ProductSnippetFull on Catalog_Product{...ProductSnippetShort,propertiesShort{...ProductProperty},rating,counters{opinions,reviews}}fragment ProductSnippetShort on Catalog_Product{...ProductSnippetBase,labels{...ProductLabel},delivery{__typename,self{__typename,availabilityByDays{__typename,deliveryTime,storeCount},availableInFavoriteStores{store{id,shortName},productsCount}}},stock{countInStores,maxCountInStock},yandexPay{withYandexSplit}}fragment ProductSnippetBase on Catalog_Product{id,name,shortName,slug,isAvailable,images{citilink{...Image}},price{...ProductPrice},category{id,name},brand{name},multiplicity,quantityInPackageFromSupplier}fragment Image on Image{sources{url,size}}fragment ProductPrice on Catalog_ProductPrice{current,old,club,clubPriceViewType}fragment ProductLabel on Catalog_Label{id,type,title,description,target{...Target},textColor,backgroundColor,expirationTime}fragment Target on Catalog_Target{action{...TargetAction},url,inNewWindow}fragment TargetAction on Catalog_TargetAction{id}fragment ProductProperty on Catalog_Property{name,value}fragment SubcategoryProductsFilterGroup on CatalogFilter_FilterGroup{id,isCollapsed,isDisabled,name,filter{... on CatalogFilter_ListFilter{__typename,isSearchable,logic,filters{id,isDisabled,isInShortList,isInTagList,isSelected,name,total,childGroups{id,isCollapsed,isDisabled,name,filter{... on CatalogFilter_ListFilter{__typename,isSearchable,logic,filters{id,isDisabled,isInShortList,isInTagList,name,isSelected,total}},... on CatalogFilter_RangeFilter{__typename,fromValue,isInTagList,maxValue,minValue,serifValues,scaleStep,toValue,unit}}}}},... on CatalogFilter_RangeFilter{__typename,fromValue,isInTagList,maxValue,minValue,serifValues,scaleStep,toValue,unit}}}fragment FilterCategoryInfo on CatalogFilter_CategoryInfo{category{...Category},isSelected,productsCount}fragment Category on Catalog_Category{__typename,id,name,slug}fragment Pagination on PageInfo{hasNextPage,hasPreviousPage,perPage,page,totalItems,totalPages}',
        'variables':
            {
                'fullSearchProductsFilterInput':
                    {
                        'categoryId':  '0',
                        'pagination':
                            {
                                'page': offset,
                                'perPage': OFFSET_COEFFICIENTS['citilink']
                            },
                        'conditions': [],
                        'sorting':
                            {
                                'id': 'price',
                                'direction': 'SORT_DIRECTION_ASC'
                            },
                        'searchText': query,
                        'popularitySegmentId': 'THREE'
                    }
            }
    }
    try:
        response = await session.post(f'{url}graphql/',
                                      headers=headers,
                                      json=data)
        response.raise_for_status()
        return await parse_search_request(response.text)
    except HTTPError as err:
        print(f'Ошибка {err} при отправке запроса к ситилинку')
        return [], 0

async def parse_search_request(result_str: str) -> Tuple[list, int]:
    result = json.loads(result_str)
    record = result.get('data', {}).get('fullSearchFilter', {}).get('record', {})
    total_products = record.get('pageInfo', {}).get('totalItems')
    products = record.get('products')
    if not products:
        return [], 0
    products_list = []
    for product in products:
        title = product.get('name')
        title_32 = title[:29]
        price = product.get('price', {})
        if not price.get('club'):
            continue
        product_dict = {
            'link': f'{url}product/{product.get("id")}/',
            'full_title': title,
            'title': title_32[:title_32.rfind(' ')] + '...',
            # 'image': product.get('images', {}).get('citilink', [{}])[0].get('sources', [{}, {}, {}])[2].get('url'),
            'price': int(product.get('price', {}).get('club')),
            'orig_price': int(product.get('price', {}).get('old')) \
                if product.get('price', {}).get('old') \
                else int(product.get('price', {}).get('current')),
            'rating': product.get('rating') if product.get('rating') != '0' else None,
            'shop': 'Ситилинк'
        }
        citilink = product.get('images', {}).get('citilink')
        if not citilink:
            product_dict['image'] = None
        else:
            product_dict['image'] = citilink[0].get('sources', [{}, {}, {}])[2].get('url')
        products_list.append(product_dict)
    return products_list, total_products


async def get_search_result(session: AsyncSession, query: str, offset: int, link: str) -> Tuple[list, int]:
    if not link or int(link) > 0:
        return await get_search_request(session, query, offset)
    return [], 0