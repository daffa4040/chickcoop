# APS STUDIO
# JOIN TELEGRAM : https://t.me/apsstudiotech
# JOIN DISCORD : https://discord.gg/N9caefVJ7F
import requests
import time
import json
import threading

def extract_profile_data(response_data):
    profile = response_data['data']['profile']
    farm_capacity = response_data['data']['laboratory']['regular']['farmCapacity']
    egg_value = response_data['data']['laboratory']['regular']['eggValue']
    laying_rate = response_data['data']['laboratory']['regular']['layingRate']
    return {
        "id": profile['id'],
        "username": profile['username'],
        "cash": response_data['data']['cash'],
        "gem": response_data['data']['gem'],
        "farmValue": response_data['data']['farmValue'],
        "capacity": response_data['data']['farmCapacity']['capacity'],
        "farmCapacity_level": farm_capacity['level'],
        "farmCapacity_tier": farm_capacity['tier'],
        "eggValue_level": egg_value['level'],
        "eggValue_tier": egg_value['tier'],
        "layingRate_level": laying_rate['level'],
        "layingRate_tier": laying_rate['tier'],
        "chicken_quantity": response_data['data']['chickens']['quantity'],
        "egg_quantity": response_data['data']['eggs']['quantity']
    }

def display_profile_data(profile_data, description):
    print(f"Profile {description}:")
    print(f"ID: {profile_data['id']}")
    print(f"Username: {profile_data['username']}")
    print(f"Cash: {profile_data['cash']}")
    print(f"Gem: {profile_data['gem']}")
    print(f"Farm Value: {profile_data['farmValue']}")
    print(f"Capacity: {profile_data['capacity']}")
    print(f"Farm Capacity Level: {profile_data['farmCapacity_level']}")
    print(f"Farm Capacity Tier: {profile_data['farmCapacity_tier']}")
    print(f"Egg Value Level: {profile_data['eggValue_level']}")
    print(f"Egg Value Tier: {profile_data['eggValue_tier']}")
    print(f"Laying Rate Level: {profile_data['layingRate_level']}")
    print(f"Laying Rate Tier: {profile_data['layingRate_tier']}")
    print(f"Chicken Quantity: {profile_data['chicken_quantity']}")
    print(f"Egg Quantity: {profile_data['egg_quantity']}")
    print("----------")

def get_profile(headers):
    url = "https://api.chickcoop.io/user/state"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            decoded_content = response.content.decode('utf-8')
            response_data = json.loads(decoded_content)
            profile_data = extract_profile_data(response_data)
            return profile_data
        except (UnicodeDecodeError, KeyError, json.JSONDecodeError) as e:
            print("Error fetching profile data:", e)
    else:
        print("Failed to fetch profile data. Status Code:", response.status_code)
    return None

def auto_click(headers, stop_event):
    url = "https://api.chickcoop.io/hatch/manual"
    loop_count = 0

    while not stop_event.is_set():
        response = requests.post(url, headers=headers)
        loop_count += 1

        if response.status_code == 200:
            try:
                decoded_content = response.content.decode('utf-8')
                response_data = json.loads(decoded_content)
                profile_data = extract_profile_data(response_data)

                print(f"Loop count: {loop_count}")
                display_profile_data(profile_data, f"after loop {loop_count}")

                if profile_data["chicken_quantity"] >= profile_data["capacity"]:
                    auto_buy_research(headers, "3", 1)
                
            except (UnicodeDecodeError, KeyError, json.JSONDecodeError) as e:
                print(f"Error on loop {loop_count}:", e)
        else:
            print(f"Failed to fetch data on loop {loop_count}. Status Code:", response.status_code)

        time.sleep(0.1)

def claim_gift(headers):
    url = "https://api.chickcoop.io/gift/claim"
    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        try:
            decoded_content = response.content.decode('utf-8')
            response_data = json.loads(decoded_content)

            profile_data = extract_profile_data(response_data)
            display_profile_data(profile_data, "before claiming gift")

            if response_data["ok"]:
                print("Gift claimed successfully.")
            else:
                print(f"Gift claim failed. Error: {response_data['error']}")
            
            display_profile_data(profile_data, "after claiming gift")
        except (UnicodeDecodeError, KeyError, json.JSONDecodeError) as e:
            print("Error:", e)
    else:
        print("Failed to claim gift. Status Code:", response.status_code)

def auto_buy_research(headers, research_choice, buy_count):
    research_options = {
        "1": "laboratory.regular.layingRate",
        "2": "laboratory.regular.eggValue",
        "3": "laboratory.regular.farmCapacity"
    }

    if research_choice in research_options:
        url = "https://api.chickcoop.io/laboratory/research"
        payload = json.dumps({"researchType": research_options[research_choice]})

        for _ in range(buy_count):
            response = requests.post(url, headers=headers, data=payload)

            if response.status_code == 200:
                try:
                    decoded_content = response.content.decode('utf-8')
                    response_data = json.loads(decoded_content)

                    profile_data = extract_profile_data(response_data)
                    display_profile_data(profile_data, "before buying research")

                    if response_data["ok"]:
                        print("Research bought successfully.")
                    else:
                        print(f"Research purchase failed. Error: {response_data['error']}")
                    
                    display_profile_data(profile_data, "after buying research")
                except (UnicodeDecodeError, KeyError, json.JSONDecodeError) as e:
                    print("Error:", e)
            else:
                print("Failed to buy research. Status Code:", response.status_code)
    else:
        print("Invalid choice.")

def sell_eggs(headers, egg_quantity):
    url = "https://api.chickcoop.io/user/sell-eggs"
    payload = json.dumps({"numberOfEggs": egg_quantity})

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        try:
            decoded_content = response.content.decode('utf-8')
            response_data = json.loads(decoded_content)

            profile_data = extract_profile_data(response_data)
            display_profile_data(profile_data, "before selling eggs")

            if response_data["ok"]:
                print(f"{egg_quantity} eggs sold successfully.")
            else:
                print(f"Egg sale failed. Error: {response_data['error']}")
            
            display_profile_data(profile_data, "after selling eggs")
        except (UnicodeDecodeError, KeyError, json.JSONDecodeError) as e:
            print("Error:", e)
    else:
        print("Failed to sell eggs. Status Code:", response.status_code)

def schedule_task(interval, task, headers, stop_event, *args):
    def task_wrapper():
        while not stop_event.is_set():
            task(headers, *args)
            time.sleep(interval)
    
    thread = threading.Thread(target=task_wrapper)
    thread.start()
    return thread

def main():
    print("Join Telegram: https://t.me/apsstudiotech")
    print("Join Discord: https://discord.gg/N9caefVJ7F")
    print("Dibuat oleh APS Studio")

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": "query_id=xxxxxx",
        "Cache-Control": "no-cache",
        "Content-Length": "0",
        "Content-Type": "application/octet-stream",
        "Origin": "https://game.chickcoop.io",
        "Pragma": "no-cache",
        "Referer": "https://game.chickcoop.io/",
        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
    }

    profile_data = get_profile(headers)
    if profile_data:
        display_profile_data(profile_data, "current")

    enable_claim_gift = input("Enable Claim Gift? (yes/no): ").strip().lower() == "yes"
    enable_auto_buy_research = input("Enable Auto Buy Research for Farm Capacity? (yes/no): ").strip().lower() == "yes"
    enable_sell_eggs = input("Enable Sell Eggs? (yes/no): ").strip().lower() == "yes"
    enable_laying_rate = input("Enable Auto Buy Research for Laying Rate? (yes/no): ").strip().lower() == "yes"
    laying_rate_count = int(input("How many times to buy Laying Rate research each hour? ")) if enable_laying_rate else 0
    enable_egg_value = input("Enable Auto Buy Research for Egg Value? (yes/no): ").strip().lower() == "yes"
    egg_value_count = int(input("How many times to buy Egg Value research each hour? ")) if enable_egg_value else 0

    stop_event = threading.Event()
    threads = []

    if enable_claim_gift:
        claim_gift(headers)
    
    auto_click_thread = threading.Thread(target=auto_click, args=(headers, stop_event))
    auto_click_thread.start()
    threads.append(auto_click_thread)

    if enable_sell_eggs:
        sell_eggs_thread = schedule_task(1800, sell_eggs, headers, stop_event, profile_data["egg_quantity"])  # Every 30 minutes
        threads.append(sell_eggs_thread)

    if enable_laying_rate:
        laying_rate_thread = schedule_task(3600 / laying_rate_count, auto_buy_research, headers, stop_event, "1", laying_rate_count)  # Every hour divided by count
        threads.append(laying_rate_thread)

    if enable_egg_value:
        egg_value_thread = schedule_task(3600 / egg_value_count, auto_buy_research, headers, stop_event, "2", egg_value_count)  # Every hour divided by count
        threads.append(egg_value_thread)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        for thread in threads:
            thread.join()

if __name__ == "__main__":
    main()
