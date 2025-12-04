import requests
from datetime import datetime


def get_latest_launch():
    response = requests.get('https://api.spacexdata.com/v4/launches/latest')
    data = response.json()
    
    return {
        'name': data['name'],
        'date_utc': data['date_utc'],
        'rocket_id': data['rocket'],
        'success': data['success'],
    }


def get_rocket_name(rocket_id):
    response = requests.get(f'https://api.spacexdata.com/v4/rockets/{rocket_id}')
    data = response.json()
    return data.get('name', 'Unknown Rocket')


def format_date(date_str):
    dt = datetime.fromisoformat(date_str.rstrip('Z'))
    return dt.strftime('%Y-%m-%d %H:%M:%S UTC')


def main():
    latest = get_latest_launch()
    rocket_name = get_rocket_name(latest['rocket_id'])
    formatted_date = format_date(latest['date_utc'])

    print("=" * 50)
    print("Latest SpaceX Launch Information")
    print("=" * 50)
    print(f"Mission Name: {latest['name']}")
    print(f"Launch Date:  {formatted_date}")
    print(f"Rocket:       {rocket_name}")
    print(f"Success:      {'✓ Yes' if latest['success'] else '✗ No'}")
    print("=" * 50)


if __name__ == '__main__':
    main()
