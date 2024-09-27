
# ./data/price_ethereum.csv

#     if not os.path.exists('data'):
#         os.makedirs('data')
#   data = get_data(coin_number=31656, range='1D')

import pandas as pd
from numpy import sign, mean, var

def load_csv(name):
    df = pd.read_csv('data/price_%s.csv' % name)
    return df

def get_trend(df):
    trend = df['prices'].diff()
    return trend

def get_returns(df):
    returns = df['prices'].pct_change()
    return returns

def returns(prices):
    returns = []
    for i in range(1, len(prices)):
        return_value = (prices[i] - prices[i-1]) / prices[i-1]
        returns.append(return_value)
    return returns==[] and [0.0] or returns

def get_slices(returns, n):
    slices = []
    for i in range(len(returns)-n):
        slice = returns[i:i+n]
        slices.append(slice)
    return slices

def get_streaks(returns):
    streaks = []
    streak = []
    for i in range(len(returns)):
        if len(streak) == 0:
            streak.append(returns[i])
        elif returns[i] * returns[i-1] > 0:
            streak.append(returns[i])
        else:
            if len(streak) > 0:
                streaks.append(streak)
            streak = [returns[i]]
    if len(streak) > 0:
        streaks.append(streak)
    return streaks

def get_streak_sizes(streaks):
    streak_sizes = [len(streak) for streak in streaks]
    return streak_sizes

def get_last_streaks(slices):
    ret = []
    for slice in slices:
        streaks = get_streaks(slice)
        ret.append(streaks[-1])
    return ret

def get_last_streaks_and_point(slices):
    ret = []
    for slice in slices:
        streaks = get_streaks(slice[:-1])
        ret.append((streaks[-1], slice[-1]))
    return ret

def get_streak_point_trade(streak_points):
    return [ (streak,int((sign(point)+1)/2)) for streak, point in streak_points]

def reduce(streaks, func):
    return [func(streak) for streak in streaks]

def reduce_streak_points(streak_points, func):
    return [ (func(streak), point) for streak, point in streak_points]

def flat_streak_points(streak_points1, reduced_streak_points2):
    for (streak1, point1), (reduced, point2) in zip(streak_points1, reduced_streak_points2):
        #print((streak1, point1), (reduced, point2))
        yield (streak1+[reduced], point1)

def filter_nan(returns):
    return [ret for ret in returns if not pd.isna(ret)]


def main():
    coin = 'ethereum'
    df = load_csv(coin)
    myreturns = get_returns(df)
    myreturns = filter_nan(myreturns)
    print(max(myreturns), min(myreturns))

    slices = get_slices(myreturns, 15)
    streak_points = get_last_streaks_and_point(slices)
    streak_point_trade = get_streak_point_trade(streak_points)
    #for i,j in zip(streak_point_trade,streak_points):
    #    print(i,j)

    len_streak_points = reduce_streak_points(streak_point_trade, lambda x: [len(x)]) #/12])
    mean_streak_points = reduce_streak_points(streak_point_trade, lambda x : abs(mean(x)))
    var_streak_points = reduce_streak_points(streak_point_trade, lambda x : var(x))
    direction_streak_points = reduce_streak_points(streak_point_trade, lambda x : sign(x[0]))#int((sign(x[0])+1)/2))
    convexity_streak_points = reduce_streak_points(streak_point_trade, lambda x : abs(mean(returns(x))))
    convex_direction_streak_points = reduce_streak_points(streak_point_trade, lambda x : sign((mean(returns(x)))))
    #for j in convexity_streak_points:
    #    print(j)
    two_streak_points = flat_streak_points(len_streak_points, direction_streak_points)
    three_streak_points = flat_streak_points(two_streak_points, mean_streak_points)
    four_streak_points = flat_streak_points(three_streak_points, var_streak_points)
    five_streak_points = flat_streak_points(four_streak_points, convexity_streak_points)
    six_streak_points = flat_streak_points(five_streak_points, convex_direction_streak_points)
    for i in six_streak_points:
        print(i)

    streaks = get_streaks(myreturns)
    streak_sizes = get_streak_sizes(streaks)
    #print( max(streak_sizes))
    #print(list(zip(streak_sizes,streaks)))

if __name__ == '__main__':
    main()