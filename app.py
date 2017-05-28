# coding: utf-8
from __future__ import division
from backtest import *
import os
basedir = os.path.abspath(os.path.dirname(__file__))
datadir=basedir + '/data'
import pandas as pd
from math import floor

import random
from io import BytesIO
# from StringIO import StringIO  # python 2.7x

import base64

from flask import Flask, make_response,session, flash
from flask import render_template, request, url_for, redirect 
from forms import IndexAnalyzer
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap()


app = Flask(__name__)
# Update parameters required by the Instagram. The secret_key could be anything
app.config.update(
    WTF_CSRF_ENABLED = True
    ,SECRET_KEY = "pass"
    )

# Routes

@app.route('/', methods=['GET', 'POST'])
def main():
    form = IndexAnalyzer(request.form)
    if form.validate_on_submit():
        indextype = form.indextype.data
        session['indextype'] = form.indextype.data
        text = form.frequencytime.data
        session['frequency'] = form.frequencytime.data
        return redirect(url_for('index_analyze', user_input=text))
    return render_template('index.html', form=form)



"""
The beginning of the route @app.route("/index_analyze/<user_input>") picks
up what the user had passed as a search. ".png" is then appended to user_input to create
the image title. 

The ending of the url will show up as the input and reference the filename.
Both routes have "/index_analyze/..." this causes the response route to render
the user_input with the ".png" ending
@app.route("/index_analyze/<image_name>.png")
"""

#@app.route("/index_analyze/<image_name>.png")  # 3
#def image(image_name):
"""
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]

    axis.plot(xs, ys)
"""
    # rendering matplotlib image to Flask view
"""
    canvas = FigureCanvas(fig)
    output = BytesIO()
"""
    # output = StringIO()  # python 2.7x
"""
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response
"""
    # pulls in the scraper and creates the DataFrame
    #index_analyzed = index_analyzer(image_name)

    # formats the DataFrame to display plots
    #index_graph(index_analyzed)

    # rendering matplotlib image to Flask view
"""
    canvas = FigureCanvas(plt.gcf())
    output = StringIO()
    canvas.print_png(output)
"""
    # make_response converts the return value from a view
    # function to a real response object that is an instance
    # of response_class.

@app.route('/about')
def home():
    return render_template('about.html')
#import matplotlib
#matplotlib.use('Agg')

# 获取股票数据
def get_stock_data(index):
    all_stock = pd.DataFrame()
    # 遍历数据文件夹中所有股票文件的文件名，得到股票代码列表
    #stock_data = pd.read_csv('./data/' + index + '.csv' )
    index_data = pd.read_csv(os.path.join(datadir, index+'.csv'), parse_dates=[0],encoding='windows-1252' )
    index_count = len(index_data)
    count=len(index_data.columns)
    count=count//2
    window = 1
    common_index=[]
    for i in range(window, window+1):
        start_month = index_data.columns[2*(i-window)+1]  # 排名期第一个月
        #print start_month
        #start_month = by_month['index'].iloc[i - window]  # 排名期第一个月
        #end_month = by_month['index'].iloc[i]  # 排名期最后一个月
        end_month = index_data.columns[2*(i-window)+1+2*1]  # 排名期最后一个月
        
        #start_index=index_data[1:,start_month]  # 
        start_index=index_data.iloc[1:,[2*(i-window)]]
        end_index=index_data.iloc[1:,[2*(i-window)+2*1]]
        for j in  range(len(end_index)):
            #if start_index.iat[j,0]==end_index.iat[j,0]:
            common_index.append(end_index.iat[j,0])
    #print common_index
    # 此处为股票数据文件的本地路径，请自行修改
    df=pd.read_csv(os.path.join(datadir, 'allprice.csv') , parse_dates=[0])
    df.rename(columns = {df.columns[0]:'date'},inplace = True)
    
    for code in common_index:
        df2 = df.copy(deep=True)
        df2= df2[['date',code]]
        df2['code'] = code
        df2.rename(columns = {code:'price'},inplace = True)
        df2['change'] = df2['price'].pct_change()
        all_stock = all_stock.append(df2, ignore_index=True)
    return all_stock[['code', 'date', 'change']]
    #return df[:,[start_month,end_month]]

    #for i in range(window, len(by_month) - 1):
    # 此处为股票数据文件的本地路径，请自行修改
    #stock_data = pd.read_csv('./data/' + index + '.csv', parse_dates=['date'])
    #stock_data = stock_data[['code', 'date', 'open', 'close', 'change']].sort_values(by='date')
    #stock_data.reset_index(drop=True, inplace=True)
    # 计算复权价
    #stock_data[['open', 'close']] = cal_right_price(stock_data, type='后复权')
    # 判断每天开盘是否涨停
    #stock_data.ix[stock_data['open'] > stock_data['close'].shift(1) * 1.097, 'limit_up'] = 1
    #stock_data['limit_up'].fillna(0, inplace=True)

    #all_stock = all_stock.append(stock_data, ignore_index=True)

    #return all_stock[['code', 'date', 'change', 'limit_up']]


def momentum_and_contrarian(all_stock, start_date, end_date, window=3):
    """
    :param all_stock: 所有股票的数据集
    :param start_date: 起始日期（包含排名期）
    :param end_date: 结束日期
    :param window: 排名期的月份数，默认为3个月
    :return: 返回动量策略和反转策略的收益率和资金曲线
    """
    # 取出指数数据作为交易天数的参考标准, 此处为指数数据文件的本地路径，请自行修改
    #index_data = pd.read_csv('./data/allprice.csv', parse_dates=True, index_col=0)
    #index_data.sort_index(inplace=True)
    #index_data = index_data[start_date:end_date]
    # 转换成月度数据
    #by_month = index_data[['000001.SZ']].resample('M', how='last')
    #by_month.reset_index(inplace=True)
    index_data = pd.read_csv(os.path.join(datadir,'hs300.csv'), parse_dates=True ,encoding='windows-1252')
    #print index_data.iloc[1:,3:6]
    index_count = len(index_data)
    count=len(index_data.columns)
    count=count//2
    #print count
    momentum_portfolio_all = pd.DataFrame()
    contrarian_portfolio_all = pd.DataFrame()

    for i in range(window, count - 1):
        start_month = index_data.columns[2*(i-window)]  # 排名期第一个月
        #start_month = by_month['index'].iloc[i - window]  # 排名期第一个月
        #end_month = by_month['index'].iloc[i]  # 排名期最后一个月
        end_month = index_data.columns[2*i]  # 排名期最后一个月
        hold_month = index_data.columns[2*(i+1)]  # 排名期最后一个月
        if i==count -2:
            hold_month = '2017-1-26'

        
        # 取出在排名期内的数据
        stock_temp = all_stock[(all_stock['date'] > start_month) & (all_stock['date'] <= end_month)]
        #xindex_list=
        #stock_temp = all_stock[(all_stock['start_month':['end_month'] , > start_month) & (all_stock['date'] <= end_month)]

        # 将指数在这段时间的数据取出作为交易日天数的标准
        #index_temp = index_data[start_month:end_month]

        # 统计每只股票在排名期的交易日天数
        #trading_days = stock_temp['code'].value_counts()
        # 剔除在排名期内累计停牌超过（5*月数）天的股票，即如果排名期为3个月，就剔除累计停牌超过15天的股票
        #keep_list = trading_days[trading_days >= (len(index_temp) - 5 * window)].index
        #stock_temp = stock_temp[stock_temp['code'].isin(keep_list)]

        # 计算每只股票在排名期的累计收益率
        grouped = stock_temp.groupby('code')['change'].agg({'return': lambda x: (x + 1).prod() - 1})
        # 将累计收益率排序
        grouped.sort_values(by='return', inplace=True)
        # 取排序后前5%的股票构造反转策略的组合，后5%的股票构造动量策略的组合
        num = floor(len(grouped) * 0.05)
        momentum_code_list = grouped.index[-num:]  # 动量组合的股票代码列表
        contrarian_code_list = grouped.index[0:num]  # 反转组合的股票代码列表

        # ============================动量组合============================
        # 取出动量组合内股票当月的数据
        momentum = all_stock.ix[(all_stock['code'].isin(momentum_code_list)) &
                                (all_stock['date'] > end_month) & (all_stock['date'] <= hold_month)]
                                #(all_stock['date'] > end_month) & (all_stock['date'] <= by_month['date'].iloc[i + 1])]

        # 剔除动量组合里在当月第一个交易日涨停的股票
        #temp = momentum.groupby('code')['limit_up'].first()
        #hold_list = temp[temp == 0].index
        #momentum = momentum[momentum['code'].isin(momentum_code_list)].reset_index(drop=True)
        #momentum = momentum[momentum['code'].isin(hold_list)].reset_index(drop=True)
        # 动量组合
        momentum_portfolio = momentum.pivot('date', 'code', 'change').fillna(0)

        # 计算动量组合的收益率
        num = momentum_portfolio.shape[1]
        weights = num * [1. / num]
        momentum_portfolio['pf_rtn'] = np.dot(np.array(momentum_portfolio), np.array(weights))
        momentum_portfolio.reset_index(inplace=True)

        # 将每个月的动量组合收益数据合并
        momentum_portfolio_all = momentum_portfolio_all.append(momentum_portfolio[['date', 'pf_rtn']],
                                                               ignore_index=True)
        # 计算动量策略的资金曲线
        momentum_portfolio_all['capital'] = (1 + momentum_portfolio_all['pf_rtn']).cumprod()

        # ============================反转组合=============================
        # 取出反转组合内股票当月的数据
        contrarian = all_stock.ix[(all_stock['code'].isin(contrarian_code_list)) &
                                  (all_stock['date'] > end_month) & (all_stock['date'] <= hold_month)]
                                  #(all_stock['date'] > end_month) & (all_stock['date'] <= by_month['date'].iloc[i + 1])]

        # 剔除反转组合里在当月第一个交易日涨停的股票
        #temp = contrarian.groupby('code')['limit_up'].first()
        #hold_list = temp[temp == 0].index
        #contrarian = contrarian[contrarian['code'].isin(hold_list)].reset_index(drop=True)
        # 反转组合
        contrarian_portfolio = contrarian.pivot('date', 'code', 'change').fillna(0)

        # 计算反转组合的收益率
        num = contrarian_portfolio.shape[1]
        weights = num * [1. / num]
        contrarian_portfolio['pf_rtn'] = np.dot(np.array(contrarian_portfolio), np.array(weights))
        contrarian_portfolio.reset_index(inplace=True)

        # 将每个月的反转组合收益合并
        contrarian_portfolio_all = contrarian_portfolio_all.append(contrarian_portfolio[['date', 'pf_rtn']],
                                                                   ignore_index=True)
        # 计算反转策略的资金曲线
        contrarian_portfolio_all['capital'] = (1 + contrarian_portfolio_all['pf_rtn']).cumprod()

    return momentum_portfolio_all, contrarian_portfolio_all


@app.route("/index_analyze/<user_input>")  # 1
def index_analyze(user_input):

    indextype = session.get('indextype')
    window = session.get('frequency')
    index='hs300'
    if indextype == '0':
        index='HS300'
        annualreturn=0.017
    elif indextype == '1':
        index='ZZ500'
        annualreturn=0.044
    else:
        index='ZZ800'
        annualreturn=0.025
    user_input=index
    #user_input="指数"+index+" 时间"+user_input+"月"
    flash('基准年化收益率:%f' % annualreturn)
    return render_template(
        'index_analyzer.html',
        input=user_input,
        filename=user_input+".png"  # 2 Hardcoding the png which will help us display the graphs
    )

#@app.route('/plot.png')
@app.route("/index_analyze/<image_name>.png")  # 3
def image(image_name):

    # 读取股票数据
    indextype = session.get('indextype')
    window = int(session.get('frequency'))
    index='hs300'
    if indextype == '0':
        index='hs300'
    elif indextype == '1':
        index='zz500'
    else:
        index='zz800'

    all_stock = get_stock_data(index)

    # 从2011年1月开始形成排名期，排名期3个月，每月初根据前3个月的排名换仓
    m, c = momentum_and_contrarian(all_stock, '2010-12-31', '2017-1-26', window)

    date_line = list(m['date'])
    capital_line = list(m['capital'])
    return_line = list(m['pf_rtn'])
    #flash('=====================动量策略主要回测指标=====================')
    m_title="momentum "
    m_return=annual_return(date_line, capital_line)
    #max_drawdown(date_line, capital_line)
    #sharpe_ratio(date_line, capital_line, return_line)

    date_line = list(c['date'])
    capital_line = list(c['capital'])
    return_line = list(c['pf_rtn'])
    #flash('=====================反转策略主要回测指标=====================')
    c_title ="contrarian "
    c_return=annual_return(date_line, capital_line)
    #max_drawdown(date_line, capital_line)
    #sharpe_ratio(date_line, capital_line, return_line)

 
    fig=plt.figure(figsize=(10, 7))
    m.set_index('date', inplace=True)
    c.set_index('date', inplace=True)
    #index_data['cum_ret'] = (index_data['change'] + 1).cumprod() - 1
    #index_data.set_index('date', inplace=True)
    (m['capital'] - 1).plot()
    (c['capital'] - 1).plot()

    #index_data['cum_ret'].plot()
    #plt.title('Cumulative Return')
    plt.title(m_title+m_return+" vs " +c_title+c_return)
    plt.legend(['momentum', 'contrarian'], loc='best')
    #plt.legend(['momentum', 'contrarian', 'index'], loc='best')
    #plt.show()

    canvas = FigureCanvas(fig)
    output = BytesIO()
    # output = StringIO()  # python 2.7x
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == '__main__':
  bootstrap.init_app(app)
  app.run(debug=True,host='0.0.0.0',port=80)
