import datetime
import requests
from flask import Flask, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os


load_dotenv()

TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")

app = Flask(__name__)

def get_ip_address():
    
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip_address = response.json().get('ip')
        return ip_address
    except requests.RequestException:
        return "IP not found"

def login_to_twitter(driver):
    try:
        driver.get("https://twitter.com/login")
        username_input = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="text"]'))
        )
        username_input.send_keys(TWITTER_USERNAME)
        username_input.send_keys(Keys.RETURN)

        password_input = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
        password_input.send_keys(TWITTER_PASSWORD)
        password_input.send_keys(Keys.RETURN)

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="AppTabBar_Home_Link"]'))
        )
        print("Login successful!")

    except Exception as e:
        print(f"Error occurred during login: {e}")

def fetch_trending_topics(driver):
    try:
        driver.get("https://twitter.com/explore/tabs/trending")
        print("Waiting for trends section...")
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]'))
        )
        
        trends = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]')
        if not trends:
            print("No trends found.")
            return []

        print(f"Found {len(trends)} trends.")
        top_5_trends = [trend.text.strip() for trend in trends if trend.text.strip()][:5]
        return top_5_trends

    except Exception as e:
        print(f"Error occurred while fetching trends: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trends')
def trends():
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    
    login_to_twitter(driver)

    
    trends = fetch_trending_topics(driver)

    
    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    
    ip_address = get_ip_address()

    
    trends_json = [
        {"_id": {"trend_id": f"trend{index + 1}"}, f"nameoftrend{index + 1}": trend}
        for index, trend in enumerate(trends)
    ]

    
    driver.quit()

    
    return jsonify({
        "date_time": end_time,
        "ip_address": ip_address,
        "trends": trends,
        "trends_json": trends_json
    })

if __name__ == "__main__":
    app.run(debug=True)



