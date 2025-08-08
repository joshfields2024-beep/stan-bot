from scrapers.scraper_oglasi_rs import search_oglasi_rs

def main():
    settings = {}
    result = search_oglasi_rs(settings)
    print(result)

if __name__ == "__main__":
    main()
