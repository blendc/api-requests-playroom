from zeep import Client

WSDL_URL = 'http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL'

client = Client(wsdl=WSDL_URL)


def get_countries():
    countries = client.service.ListOfCountryNamesByName()
    return [(country.sName, country.sISOCode) for country in countries]


def main():
    print("=" * 60)
    print("Fetching Country Information via SOAP Web Service")
    print("=" * 60)
    print()
    
    countries = get_countries()
    
    print(f"Total countries available: {len(countries)}")
    print("\nShowing first 100 countries:\n")
    
    for index, (name, code) in enumerate(countries[:100], start=1):
        print(f"{index:3d}. {name:40s} ({code})")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
