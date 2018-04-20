import requests

STOCK_NAME_INDEX = 0
STOCK_PRICE_INDEX = 3
STOCK_NAME_TITLE = "Symbol"
FILE_DIR = "DataFiles/"
FILE_NAME = "/rank_1.xls"
STOCK_PRICE_API = "https://api.iextrading.com/1.0/stock/{}/price"  # from https://iextrading.com/developer/docs/#price

virtualCash = 150000.00
virtualStockValue = 0.00
total_gains = 0.0

# all dictionaries should be replaced by database
dict_daily_cash_stock = {0: [virtualCash, virtualStockValue]}
dict_stock_prices_latest = {}
dict_shares_count = {}
dict_stock_price_latest_from_api = {}


def get_latest_stock_price(symbol):
    # get the default offline value read from file
    if symbol in dict_stock_prices_latest.keys():
        latest_price = dict_stock_prices_latest[symbol]

    try:
        response = requests.get(STOCK_PRICE_API.format(symbol))
        if response.status_code == 200:
            latest_price = float(response.content)
            print("Latest price received successfully for {}:{}".format(symbol, latest_price))
            dict_stock_price_latest_from_api[symbol] = latest_price
        else:
            print("Failed to fetch the latest stock price for {} status_code {}. Defaulting to offline data {}"
                  .format(symbol, response.status_code, latest_price))
    except Exception:
        print("Failed to fetch the latest stock price for {}: {} . Defaulting to offline data {}"
              .format(symbol, Exception.message, latest_price))
    finally:
        return latest_price


def get_stock_data(filename):
    global dict_stock_prices_latest
    stock_data_dict = {}
    total_buying_cost = 0.0

    with open(filename, "r") as f:
        lines = f.readlines()

        for line in lines:
            stock_name = line.split("\t")[STOCK_NAME_INDEX].strip()

            # DataFiles contain first blank line and second title line
            # Filter first two line
            if stock_name != "" and stock_name != STOCK_NAME_TITLE:
                try:
                    stock_price = float(line.split("\t")[STOCK_PRICE_INDEX])
                except Exception:
                    continue

                # print stockName, stockPrice
                stock_data_dict[stock_name] = stock_price
                dict_stock_prices_latest[stock_name] = stock_price
                total_buying_cost += stock_price

    return stock_data_dict


def sell(day, stock_data_dict):
    global virtualCash
    global virtualStockValue
    sold_stocks = {}

    print("\n\nStarting selling for day:", day)

    # if the stock in portfolio is not rank_1 stock this day,
    # then sell it
    for stock in dict_shares_count:
        if stock not in stock_data_dict:
            stock_count = dict_shares_count[stock]

            stock_buy_value = dict_stock_prices_latest[stock]
            stock_sell_value = get_latest_stock_price(stock)

            gains = (stock_sell_value - stock_buy_value) * stock_count
            global total_gains
            total_gains += gains

            # sell
            # print "Selling {} shares of {} priced each at {}".format(stockCount, stock, stockValue)
            virtualCash += stock_sell_value * stock_count
            virtualStockValue -= stock_buy_value * stock_count
            sold_stocks[stock] = "POP_ME"

    # remove from sharesCount
    for stock in sold_stocks:
        dict_shares_count.pop(stock)

    dict_daily_cash_stock[day] = [virtualCash, virtualStockValue]
    print("Ending selling for day:", day)
    print("Day {}, virtualCash {}, virtualStockValue {}, totalPortfolio {}"\
        .format(day, virtualCash, virtualStockValue, virtualCash + virtualStockValue))


def buy(day, stock_data_dict):
    global virtualCash
    global virtualStockValue

    print("\n\nStarting buying for day:", day)
    for stock in stock_data_dict:

        # if enough cash, buy, else print and break
        if virtualCash < stock_data_dict[stock]:
            print("Not enough cash. Breaking....")
            break

        # case-1: New stock
        if stock not in dict_shares_count.keys():
            dict_shares_count[stock] = 1
        # case-2: Stock repeated
        else:
            dict_shares_count[stock] += 1

        # buy the stock using virtualCash
        virtualCash -= stock_data_dict[stock]
        virtualStockValue += stock_data_dict[stock]

    dict_daily_cash_stock[day] = [virtualCash, virtualStockValue]
    print("Ending buying for day:", day)
    print("Day {}, virtualCash {}, virtualStockValue {}, totalPortfolio {}".format(day, virtualCash, virtualStockValue,
                                                                                   virtualCash + virtualStockValue))


def write_daily_performance_to_file(daily_cash_stock):
    with open("DailyPerformance.csv", "w") as f:
        line = "{},{},{}\n".format("Day", "virtualCash", "virtualStockValue")
        f.write(line)
    with open("DailyPerformance.csv", "a") as f:
        for day in daily_cash_stock:
            line = "{},{},{}\n".format(day, daily_cash_stock[day][0], daily_cash_stock[day][1])
            f.write(line)


def main():
    for day in range(1, 12):
        stock_data = get_stock_data(FILE_DIR + str(day).zfill(2) + FILE_NAME)
        if day == 1:
            buy(day, stock_data)
        else:
            sell(day, stock_data)
            buy(day, stock_data)

        print("\n\n\nTrade analysis:\n\n")
        print("Day: virtualCash, virtualPortfolio\n", dict_daily_cash_stock)
        print("Stock: shares\n", dict_shares_count)
        print("Total gains\n", total_gains)
        write_daily_performance_to_file(dict_daily_cash_stock)


if __name__ == '__main__':
    main()

