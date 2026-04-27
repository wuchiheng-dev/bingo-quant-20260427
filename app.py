# app.py
from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
from collections import Counter
import random

app = Flask(__name__)

# =========================
# 抓資料（台彩）
# =========================
def fetch_history(limit=300):
    url = "https://www.taiwanlottery.com/lotto/result/bingo_bingo"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    draws = []
    for row in soup.select("tr"):
        nums = [int(x) for x in row.get_text().split() if x.isdigit()]
        if len(nums) >= 20:
            draws.append(nums[-20:])
        if len(draws) >= limit:
            break

    return draws


# =========================
# 策略1：熱號
# =========================
def strategy_hot(draws, count=5):
    c = Counter()
    for d in draws:
        c.update(d)

    return [n for n, _ in c.most_common(count)]


# =========================
# 策略2：冷號
# =========================
def strategy_cold(draws, count=5):
    c = Counter()
    for d in draws:
        c.update(d)

    return [n for n, _ in sorted(c.items(), key=lambda x: x[1])[:count]]


# =========================
# 策略3：隨機
# =========================
def strategy_random(count=5):
    return random.sample(range(1, 81), count)


# =========================
# 🎯 回測系統
# =========================
def backtest(draws, strategy_func):

    results = []

    # 滾動回測（避免未來資料）
    for i in range(50, len(draws)-1):

        history = draws[:i]
        next_draw = draws[i]

        pick = strategy_func(history)

        hit = len(set(pick) & set(next_draw))
        results.append(hit)

    return {
        "avg_hit": round(sum(results)/len(results), 2),
        "max_hit": max(results),
        "trend": results
    }


# =========================
# API：策略比較
# =========================
@app.route("/compare")
def compare():

    draws = fetch_history(300)

    hot = backtest(draws, strategy_hot)
    cold = backtest(draws, strategy_cold)
    rand = backtest(draws, lambda d: strategy_random())

    return jsonify({
        "hot": hot,
        "cold": cold,
        "random": rand
    })


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)