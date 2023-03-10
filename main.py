#####################################################################################################################
###########______________ RELOAD PAGE SERVER________ uvicorn main:app --reload ____________ #########################
#####################################################################################################################

from fastapi import FastAPI, Request, Form

import sqlite3

import alpaca_trade_api as tradeapi

from fastapi.templating import Jinja2Templates
from fastapi.responses  import RedirectResponse
from datetime import datetime, timedelta

app = FastAPI()
templates = Jinja2Templates(directory="templates")

########### Calculate Yesterday ###############
d = datetime.today() - timedelta(days=1)
yesterday = d.strftime("%Y/%m/%d 05:00:00")

##################################################
############ Control Index page ##################
##################################################

###################### New Closing Highs ###########################
@app.get("/")

def index(request: Request):
    stock_filter = request.query_params.get('filter', False)

    connection = sqlite3.connect('/Users/thomas/Documents/Full_Stack_Trading_App/app.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    ########### FIND NEW CLOSING HIGHS #################
    print(stock_filter)
    if stock_filter == 'new_closing_highs':
        cursor.execute("""select*from (

                    select symbol, company, stock_id, max(close), date
                    from stock_price join stock on stock.id = stock_price.stock_id
                    group by stock_id
                    order by symbol
                ) where date  = (select max(date) from stock_price)""")

    ################# New Closing Lows #########################
    elif stock_filter == 'new_closing_lows':
        cursor.execute("""select*from (

                    select symbol, company, stock_id, min(close), date
                    from stock_price join stock on stock.id = stock_price.stock_id
                    group by stock_id
                    order by symbol
                ) where date  = (select max(date) from stock_price);""")
    else:
        cursor.execute(""" SELECT symbol, company, id FROM stock ORDER BY symbol""")

    rows = cursor.fetchall()

    cursor.execute("""
    SELECT symbol, rsi_14, sma_20, sma_50, close
    FROM stock Join stock_price on stock_price.stock_id = stock.id
    WHERE date = ? """, (yesterday,))

    indicator_rows = cursor.fetchall()

    indicator_values = {}

    for row in indicator_rows:
        indicator_values[row['symbol']] = row

    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "indicator_values": indicator_values})

    return {"title":"DAshboard", "stocks": rows}





##########################################################
############ Control Individual Stock Page ###############
##########################################################


@app.get("/stock/{symbol}")

def stock_detail(request: Request, symbol):
    connection = sqlite3.connect('/Users/thomas/Documents/Full_Stack_Trading_App/app.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM strategy 
    """)

    strategies = cursor.fetchall()

    cursor.execute(""" SELECT symbol, company, id FROM stock WHERE symbol = ? """, (symbol,))

    row = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM stock_price WHERE stock_id = ? ORDER BY date DESC
    """, (row['id'],))

    prices = cursor.fetchall()

    return templates.TemplateResponse("stock_detail.html", {"request": request, "stock": row, "bars": prices, "strategies": strategies})


@app.post("/apply_strategy")
def apply_strategy(strategy_id: int = Form(...), stock_id: int = Form(...)):
    connection = sqlite3.connect('/Users/thomas/Documents/Full_Stack_Trading_App/app.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO stock_strategy (stock_id,strategy_id) VALUES (?,?)
    """, (stock_id, strategy_id))

    connection.commit()

    return RedirectResponse(url=f"/strategy/{strategy_id}", status_code=303)

@app.get("/strategy/{strategy_id}")
def strategy(request: Request, strategy_id):
    connection = sqlite3.connect('/Users/thomas/Documents/Full_Stack_Trading_App/app.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id, name
    FROM strategy
    WHERE id = ?
    """, (strategy_id,))

    strategy = cursor.fetchone()

    cursor.execute("""
        SELECT symbol, company
        FROM stock JOIN stock_strategy on stock_strategy.stock_id = stock.id
        WHERE strategy_id = ?
        """, (strategy_id,))

    stocks = cursor.fetchall()

    return templates.TemplateResponse("strategy.html", {"request": request, "stocks": stocks, "strategy": strategy})



