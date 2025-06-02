from zeep import Client

WSDL_URL = 'http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL'


client = Client(wsdl=WSDL_URL)

def get_countries():
    countries = client.service.ListOfCountryNamesByName()
    return [(c.sName, c.sISOCode) for c in countries]

def main():
    print("Fetching list of countries...\n")
    countries = get_countries()

    for i, (name, code) in enumerate(countries[:100]):
        print(f"{i+1}. {name} ({code})")

if __name__ == "__main__":
    main()
