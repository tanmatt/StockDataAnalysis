
STOCK_NAME_INDEX = 0
STOCK_PRICE_INDEX = 3
STOCK_NAME_TITLE = "Symbol"
FILE_DIR = "DataFiles/"
FILE_NAME = "/rank_1.xls"

virtualCash = 150000.00
virtualStockValue = 0.00

dailyCashStock = {}
dailyCashStock[0] = [virtualCash, virtualStockValue]

stockPricesLatest = {}
sharesCount = {}


def getStockData(filename):
    global stockPricesLatest
    stockDataDict = {}
    totalBuyingCost = 0.0

    with open(filename, "r") as f:
        lines = f.readlines()

        for line in lines:
            stockName = line.split("\t")[STOCK_NAME_INDEX].strip()

            # DataFiles contain first blank line and second title line
            # Filter first two line
            if stockName != "" and stockName != STOCK_NAME_TITLE:
                try:
                    stockPrice = float(line.split("\t")[STOCK_PRICE_INDEX])
                except Exception:
                    continue

                # print stockName, stockPrice
                stockDataDict[stockName] = stockPrice
                stockPricesLatest[stockName] = stockPrice
                totalBuyingCost += stockPrice

    return stockDataDict


def sell(day, stockDataDict):
    global virtualCash
    global virtualStockValue
    soldStocks = {}

    print "\n\nStarting selling for day:", day

    # if the stock in portfolio is not rank_1 stock this day,
    # then sell it
    for stock in sharesCount:
        if stock not in stockDataDict:
            stockCount = sharesCount[stock]
            stockValue = stockPricesLatest[stock]
            # sell
            # print "Selling {} shares of {} priced each at {}".format(stockCount, stock, stockValue)
            virtualCash += stockValue * stockCount
            virtualStockValue -= stockValue * stockCount
            soldStocks[stock] = "POP_ME"

    # remove from sharesCount
    for stock in soldStocks:
        sharesCount.pop(stock)

    dailyCashStock[day] = [virtualCash, virtualStockValue]
    print "Ending selling for day:", day
    print "Day {}, virtualCash {}, virtualStockValue {}, totalPortfolio {}".format(day, virtualCash, virtualStockValue,
                                                                                   virtualCash + virtualStockValue)



def buy(day, stockDataDict):
    global virtualCash
    global virtualStockValue

    print "\n\nStarting buying for day:", day
    for stock in stockDataDict:

        # if enough cash, buy, else print and break
        if virtualCash < stockDataDict[stock]:
            print "Not enough cash. Breaking...."
            break

        # case-1: New stock
        if stock not in sharesCount.keys():
            sharesCount[stock] = 1
        # case-2: Stock repeated
        else:
            sharesCount[stock] += 1

        # buy the stock using virtualCash
        virtualCash -= stockDataDict[stock]
        virtualStockValue += stockDataDict[stock]

    dailyCashStock[day] = [virtualCash, virtualStockValue]
    print "Ending buying for day:", day
    print "Day {}, virtualCash {}, virtualStockValue {}, totalPortfolio {}".format(day, virtualCash, virtualStockValue,
                                                                                   virtualCash + virtualStockValue)



def writeDailyPerformaceToFile(dailyCashStock):
    with open("DailyPerformance.csv", "w") as f:
        line = "{},{},{}\n".format("Day", "virtualCash", "virtualStockValue")
        f.write(line)
    with open("DailyPerformance.csv", "a") as f:
        for day in dailyCashStock:
            line = "{},{},{}\n".format(day, dailyCashStock[day][0], dailyCashStock[day][1])
            f.write(line)


def main():
    for day in range(1, 24):
        stockData = getStockData(FILE_DIR + str(day).zfill(2) + FILE_NAME)
        if day == 1:
            buy(day, stockData)
        else:
            sell(day, stockData)
            buy(day, stockData)

        print "\n\n\nTrade analysis:\n\n"
        print "Day: virtualCash, virtualPortfolio\n", dailyCashStock
        print "Stock: shares\n", sharesCount
        writeDailyPerformaceToFile(dailyCashStock)


if __name__ == '__main__':
    main()

