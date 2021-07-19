import flask
from strategies import *
from graph import *

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route("/", methods=['GET'])
def home():
    file1 = open("data.txt")
    contents = file1.read()
    if not contents:
        return render_template('home.html')
    else:
        return get_existing_portfolio()


@app.route("/reset", methods=['GET'])
def reset():
    return render_template('home.html')


@app.route("/chatbot", methods=['POST', 'GET'])
def chatbot():
    return render_template('chatbot.html')


@app.route("/strategy", methods=['POST', 'GET'])
def portfolio():
    if request.method == "POST":
        formValues = request.form.to_dict()
        data = strategize(float(formValues['amount']), request.form.getlist('strategy'))
        strategies = data['strategy']
        length = len(strategies)
        # strategies.append({})
        with open('data.txt', 'w') as file:
            json.dump(data, file)
        file.close()
        dailyGraph = get_daily_graph(data)
        graphStrategy1 = get_pie_graph(data['strategy'][0])
        graphStrategy2 = None
        strategy2 = None
        if length > 1:
            graphStrategy2 = get_pie_graph(data['strategy'][1])
            strategy2 = data['strategy'][1]
        graphStrategy_all = get_pie_graph_all(data)

        return render_template('strategy.html', strategy1=data['strategy'][0], strategy2=strategy2,
                               image1=dailyGraph, image2=graphStrategy1, image3=graphStrategy2,
                               image4=graphStrategy_all, total_amt_invested=data['total_amt_invested'],net_value=data['net_value'],net_profit_or_loss=data['net_profit_or_loss'])

    elif request.method == "GET":
        return get_existing_portfolio()


def get_existing_portfolio():
    data = {}
    with open('data.txt') as file:
        data = json.load(file)
    file.close()
    if data:
        data = update_current_values(data)
        net_value = 0
        for strategy in data['strategy']:
            net_value += strategy['actual_strategy_amt']
        data['net_value'] = round(net_value, 2)
        data['net_profit_or_loss'] = round(data['net_value'] - data['total_amt_invested'], 2)
        daily_graph = get_daily_graph(data)
        pie_chart_1 = get_pie_graph(data['strategy'][0])
        pie_chart_2 = None
        strategy2 = None
        if len(data['strategy']) > 1:
            pie_chart_2 = get_pie_graph(data['strategy'][1])
            strategy2 = data['strategy'][1]
        pie_chart_all = get_pie_graph_all(data)
        return render_template('strategy.html', strategy1=data['strategy'][0], strategy2=strategy2,
                               image1=daily_graph, image2=pie_chart_1, image3=pie_chart_2, image4=pie_chart_all,
                               total_amt_invested=data['total_amt_invested'],net_value=data['net_value'],net_profit_or_loss=data['net_profit_or_loss'])


app.run()
