import pandas as pd
import collections
import numpy as np
import cvxopt as opt
from cvxopt import blas, solvers
from pandas.plotting import register_matplotlib_converters
import datetime

register_matplotlib_converters()
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 15)

# Turn off progress printing
solvers.options['show_progress'] = False


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def get_values_in_the_intersection(intersec, data, list_ticker_symbol):
    new_data_inters = collections.OrderedDict()
    for symbol in list_ticker_symbol:
        company_data = data[symbol]
        company_return = []
        company_dates = []
        for position, el in enumerate(list(company_data[0])):
            if el in intersec and el != 'C':
                company_return.append(list(company_data[1])[position])
                company_dates.append(el)
        if len(intersec) != len(company_return):
            print("length inconsistency")
            exit()
        new_data_inters[symbol] = company_return

    return new_data_inters


def prepare_data(df_data, list_ticker_symbol):
    new_data = {}
    for symbol in list_ticker_symbol:
        new_df = df_data[df_data["Ticker Symbol"] == symbol]
        dates = new_df["Names Date"]
        returns = new_df["Returns"]
        new_data[symbol] = [dates, returns]

    dates_intersect = new_data[list_ticker_symbol[0]][0]
    for symbol in list_ticker_symbol:
        dates_intersect = intersection(list(dates_intersect), list(new_data[symbol][0]))

    company_data = get_values_in_the_intersection(dates_intersect, new_data, list_ticker_symbol)
    companydf = pd.DataFrame.from_dict(company_data)
    return companydf, dates_intersect


def statistics(data_df, plot=1):
    statistics_data = {}
    mean_returns = data_df.mean()
    var_returns = data_df.var()
    std_returns = data_df.std()
    cov_returns = data_df.cov()
    corr_returns = data_df.corr()
    # print(cov_returns)
    statistics_data["mean_returns"] = mean_returns
    statistics_data["var_returns"] = var_returns
    statistics_data["std_returns"] = std_returns
    statistics_data["cov_returns"] = cov_returns
    statistics_data["corr_returns"] = corr_returns
    return statistics_data


def pd_to_numpy(pandas, list_of_symbols):
    np_data = []
    for symbol in list_of_symbols:
        np_data.append([float(el) for el in list(pandas[symbol])])
    np_data = np.asarray(np_data)
    return np_data


def slice_pd(df, list_of_symbols):
    np_data = {}
    for symbol in list_of_symbols:
        np_data[symbol] = np.asarray(list(df[symbol]))
    return pd.DataFrame(np_data)


def convert_to_datime(dates):
    dates_datetime = []
    for date in dates:
        date = str(date)
        year = date[0:4]
        month = date[4:6]
        day = date[6:]
        new_date_dtime = datetime.datetime(year=int(year), month=int(month), day=int(day))
        dates_datetime.append(new_date_dtime)
    return dates_datetime


def optimal_portfolio(returns, short_shell=0):
    n = len(returns)
    returns = np.asmatrix(returns)
    N = 20
    mus = [10 ** (5.0 * t / N - 1.0) for t in range(N)]

    # Convert to cvxopt matrices
    S = opt.matrix(np.cov(returns))
    pbar = opt.matrix(np.mean(returns, axis=1))

    # Create constraint matrices
    constr_weights = np.eye(n)

    G = -opt.matrix(constr_weights)  # negative n x n identity matrix
    if short_shell:
        h = opt.matrix(1.0, (n, 1))
    else:
        h = opt.matrix(0.0, (n, 1))

    A = opt.matrix(1.0, (1, n))
    b = opt.matrix(1.0)

    # Calculate efficient frontier weights using quadratic programming
    portfolios = [solvers.qp(mu * S, -pbar, G, h, A, b)['x']
                  for mu in mus]
    # CALCULATE RISKS AND RETURNS FOR FRONTIER
    returns = [blas.dot(pbar, x) for x in portfolios]
    risks = [np.sqrt(blas.dot(x, S * x)) for x in portfolios]
    # CALCULATE THE 2ND DEGREE POLYNOMIAL OF THE FRONTIER CURVE
    m1 = np.polyfit(returns, risks, 2)
    x1 = np.sqrt(m1[2] / m1[0])
    # CALCULATE THE OPTIMAL PORTFOLIO
    # wt = solvers.qp(opt.matrix(x1 * S), -pbar, G, h, A, b)['x']
    #  CALCULATE THE OPTIMAL PORTFOLIO : maximize sharp ratio
    max_pos_sharp_ratio = int(np.argmax((np.asarray(returns) - 0.01) / risks))
    w = portfolios[max_pos_sharp_ratio]

    return np.asarray(w), returns, risks, max_pos_sharp_ratio


def optimal_weights_risky_on_CAL(port_mean, port_var, rf, risk_aversion):
    y = (port_mean - rf) / (0.01 * risk_aversion * (port_var ** 2))
    return y


def portf_mean_var(W, cov, mean_returns):
    portf_mean = np.dot(mean_returns, W)
    portf_std = np.sqrt(np.dot(W.transpose(), np.dot(W.transpose(), cov).transpose()))
    return portf_mean, portf_std


def portfolio(data_path, risk_aversion, symbol_to_use=[]):
    df = pd.read_excel(data_path)
    ticker_symbol = ["COG", "BR", "CPB", "CHRW", "COF", "CAH", "KORS", "CDNS", "BF", "KMX"]
    if len(symbol_to_use) < 1:
        symbol_to_use = ticker_symbol
    # n stocks
    # data preparation
    company_returns_df, dates = prepare_data(df, symbol_to_use)
    dates = convert_to_datime(dates)
    np_returns = pd_to_numpy(company_returns_df, symbol_to_use)
    cov = np.cov(np_returns)
    mean_returns = np.mean(np_returns, axis=1)
    std_returns = np.std(np_returns, axis=1)
    statistics_data = statistics(company_returns_df, plot=0)
    rf = 0.01
    ## short sell
    weights_short, returns_short, risks_short, max_pos_sharp_ratio_short = optimal_portfolio(np_returns, short_shell=1)
    # print("the optimal weights for short are respectively {} and {} for {}".format(weights_short[0], weights_short[1],
    #                                                                                symbol_to_use))
    portf_mean_short, port_std_short = portf_mean_var(weights_short, cov, mean_returns)
    y_opt_risky_short = \
        optimal_weights_risky_on_CAL(portf_mean_short * 100, port_std_short * 100, rf * 100,
                                     risk_aversion=risk_aversion)[0]
    new_weights_risky_short = weights_short * y_opt_risky_short
    weights_risk_free_short = 1 - y_opt_risky_short
    check_sum = weights_risk_free_short + np.sum(new_weights_risky_short)
    # if (int(check_sum)) != 1.:
    #     print("error : the weights sum is different from 1")
    ## no short
    weights_no_short, returns_no_short, risks_no_short, max_pos_sharp_ratio_no_short = optimal_portfolio(np_returns,
                                                                                                         short_shell=0)
    portf_mean_no_short, port_std_no_short = portf_mean_var(weights_no_short, cov, mean_returns)
    y_opt_risky_no_short = \
        optimal_weights_risky_on_CAL(portf_mean_no_short * 100, port_std_no_short * 100, rf * 100, risk_aversion=3)[
            0]
    new_weights_risky_no_short = weights_no_short * y_opt_risky_no_short
    weights_risk_free_no_short = 1 - y_opt_risky_no_short
    check_sum = weights_risk_free_no_short + np.sum(new_weights_risky_no_short)
    # if (int(check_sum)) != 1.:
    #     print("error : the weights sum is different from 1 :{}".format(check_sum))

    # short
    CAL_X_short = port_std_short * np.arange(0, 2, 0.01)
    CAL_Y_short = rf + ((portf_mean_short - rf) / port_std_short) * CAL_X_short

    # no short
    CAL_X_no_short = port_std_no_short * np.arange(0, 2, 0.01)
    CAL_Y_no_short = rf + ((portf_mean_no_short - rf) / port_std_no_short) * CAL_X_no_short

    risky_alloc = new_weights_risky_short * 10000
    risk_free_alloc = weights_risk_free_short * 10000
    out_data = {}
    out_data["CAL_10_stocks_with_short"] = [np.squeeze(CAL_X_short), np.squeeze(CAL_Y_short)]
    out_data["CAL_10_stocks_without_short"] = [np.squeeze(CAL_X_no_short), np.squeeze(CAL_Y_no_short)]
    out_data["EF_10_with_short"] = [np.squeeze(risks_short), np.squeeze(returns_short)]
    out_data["EF_10_without_short"] = [np.squeeze(risks_no_short), np.squeeze(returns_no_short)]
    out_data["mean_return"] = mean_returns
    out_data["risk"] = std_returns
    out_data["risky_alloc"] = np.append(risky_alloc, risk_free_alloc)
    out_data["risk_free_alloc"] = risk_free_alloc
    out_data["symbol"] = symbol_to_use + ["risk_free"]
    # print("run ok")
    return out_data, company_returns_df, dates


if __name__ == "__main__":
    data_path = "Data.xlsx"
    portfolio(data_path, 3, ['BF', 'BR'])
