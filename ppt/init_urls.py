from .setup_database import DatabaseController

class InitUrls:
    start_urls = []
    num_per_page = 96
    keywords = {
                'finance': '2,621',
                'pitchdeck': '3,431',
                'business': '19,099',
                'marketing': '5,223',
                'music': '218',
                'technology': '2,371',
                'shipping': '42',
                'insurance': '128',
                'bank': '119',
                'education': '1',
                'broker': '17',
                'agent': '176',
                'marine': '22',
                'movie': '41',
                'history': '1',
                'philosophy': '1',
                'creative': '1',
                'innovative': '1'
                }
    default_urls = [
        'https://elements.envato.com/api/v1/items.json?presentationTemplatesApplicationsSupported=PowerPoint&type=presentation-templates&page=1&languageCode=en&perPage=96',
        'https://elements.envato.com/api/v1/items.json?presentationTemplatesApplicationsSupported=PowerPoint&type=presentation-templates&page=1&sortBy=latest&languageCode=en&perPage=96'
    ]
    sort_types = ["relevant", "popular", "latest"]
    base_url_with_keyword_default = "https://elements.envato.com/api/v1/items.json?" \
                                    "presentationTemplatesApplicationsSupported=PowerPoint&features=showcased_collections" \
                                    "&type=presentation-templates&page=1&searchTerms={}&languageCode=en&perPage=96"
    base_url_with_keyword = "https://elements.envato.com/api/v1/items.json?" \
                            "presentationTemplatesApplicationsSupported=PowerPoint&features=showcased_collections" \
                            "&type=presentation-templates&page=1&searchTerms={}&sortBy={}&languageCode=en&perPage=96"

    def init_keywords(self):
        self.keywords.update(DatabaseController().get_tags_as_dict("ppt_item"))

    def initiate_start_urls(self):
        self.init_keywords()
        for keyword, number in self.keywords.items():
            if int(number.replace(",", "")) > 96 * 50:  # when pages are over 50, need to sort by sort_type
                for sort_type in self.sort_types:
                    if sort_type == "relevant":  # default value
                        url = self.base_url_with_keyword_default.format(keyword)
                        self.start_urls.append(url)
                    else:
                        url = self.base_url_with_keyword.format(keyword, sort_type)
                        self.start_urls.append(url)
            else:
                url = self.base_url_with_keyword_default.format(keyword)
                self.start_urls.append(url)
        self.start_urls.extend(self.default_urls)
        return self.start_urls

if __name__=="__main__":
    obj = InitUrls()
    obj.initiate_start_urls()
    for url in obj.start_urls:
        print(url)
