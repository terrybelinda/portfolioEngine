import random
import yfinance as yf
import json

strategy_map = {}
with open('strategy_map.json') as f:
    strategy_map = json.load(f)


def get_portfolio_stocks(strategy_stocks, amt):
    stock_list = list()
    residue_amt = 0
    data = yf.download(
        strategy_stocks[0]['symbol'] + ' ' + strategy_stocks[1]['symbol'] + ' ' + strategy_stocks[2]['symbol'],
        period='1d')
    data = data.reset_index()
    for stock in strategy_stocks:
        company = stock['name']
        price = round(float(data.iloc[0]['Close'][stock['symbol']]), 2)
        share = round(float((stock['weight'] / 100) * amt), 2)
        qty = int(share / price)
        amt_invested = round(qty * price, 2)
        residue_amt = residue_amt + share - amt_invested
        s = {"company": company, "current_price": price, "buy_price": price, "qty": qty, "symbol": stock['symbol'],
             "amt_invested": amt_invested, "current_value": amt_invested, "profit_or_loss": 0}
        stock_list.append(s)

    final_stock_list = list()
    for stock in stock_list:
        price = stock['current_price']
        qty = int(residue_amt / price)
        if qty > 0:
            stock['qty'] = stock['qty'] + qty
            extra_amt = round(price * qty, 2)
            stock['amt_invested'] = round(stock['amt_invested'] + extra_amt, 2)
            residue_amt = round(residue_amt - extra_amt, 2)
            stock['current_value'] = stock['amt_invested']
        final_stock_list.append(stock)
    print(residue_amt)
    return final_stock_list


def get_strategies(total_amt, chosen_strategies):
    amts = list()
    if len(chosen_strategies) < 2:
        amt_1 = total_amt
        amts.append(amt_1)
    else:
        random_muliplier = round(float(random.uniform(0.5, 0.6)), 2)
        amt_1 = round(float(random_muliplier * total_amt), 2)
        amt_2 = total_amt - amt_1
        amts = [amt_1, amt_2]
    count = 0
    total_amt = 0
    strategies = list()
    for strategy in chosen_strategies:
        stock_list = get_portfolio_stocks(strategy_map[strategy], amts[count])
        data = {'0': stock_list[0], '1': stock_list[1], '2': stock_list[2]}
        amts[count] = round(stock_list[0]['amt_invested'] + stock_list[1]['amt_invested'] + stock_list[2][
            'amt_invested'], 2)
        strategies.append({"strategy": strategy, "data": data, "actual_strategy_amt": amts[count]})
        total_amt += amts[count]
        count = count + 1
    if len(chosen_strategies) > 1:
        strategies[0]["share"] = round((amts[1] / total_amt) * 100, 2)
        strategies[1]["share"] = round(100 - strategies[0]["share"], 2)
    else:
        strategies[0]["share"] = 100
    return strategies


def strategize(amount, strategy):
    strategies = get_strategies(amount, strategy)
    total_amt_invested = 0
    for strategy in strategies:
        total_amt_invested += strategy['actual_strategy_amt']
    total_amt_invested = round(total_amt_invested, 2)
    data = {'total_amt_invested': total_amt_invested, 'strategy': strategies, 'net_value': total_amt_invested,
            'net_profit_or_loss': 0}
    return data


def update_current_values(data):
    count = 0
    for strategy in data['strategy']:
        stocks = strategy['data']
        y_data = yf.download(stocks['0']['symbol'] + ' ' + stocks['1']['symbol'] + ' ' + stocks['2']['symbol'],
                             period='1d')
        y_data = y_data.reset_index()
        stocks['0']['current_price'] = round(float(y_data.iloc[0]['Close'][stocks['0']['symbol']]), 2)
        stocks['0']['current_value'] = round(stocks['0']['current_price'] * stocks['0']['qty'], 2)
        stocks['0']['profit_or_loss'] = round(stocks['0']['current_value'] - stocks['0']['amt_invested'], 2)
        stocks['1']['current_price'] = round(float(y_data.iloc[0]['Close'][stocks['1']['symbol']]), 2)
        stocks['1']['current_value'] = round(stocks['1']['current_price'] * stocks['1']['qty'], 2)
        stocks['1']['profit_or_loss'] = round(stocks['1']['current_value'] - stocks['1']['amt_invested'], 2)
        stocks['2']['current_price'] = round(float(y_data.iloc[0]['Close'][stocks['2']['symbol']]), 2)
        stocks['2']['current_value'] = round(stocks['2']['current_price'] * stocks['2']['qty'], 2)
        stocks['2']['profit_or_loss'] = round(stocks['2']['current_value'] - stocks['2']['amt_invested'], 2)
        strategy['data'] = stocks
        data['strategy'][count] = strategy
        count = count + 1

    return data
