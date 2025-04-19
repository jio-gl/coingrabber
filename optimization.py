import tkinter as tk
from tkinter import ttk
import time
import math
import random
import numpy
import csv
import os
import sys
import queue
import threading
from functools import reduce
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dateconfig import DateRange
from coins import CoinDB
from portfolio import PortfolioAnalyzer
from cvxopt import matrix, solvers

# https://wellecks.wordpress.com/2014/03/23/portfolio-optimization-with-python/


#symbols = ['GOOG', 'AIMC', 'GS', 'BH', 'TM', 
#           'F', 'HLS', 'DIS', 'LUV', 'MSFT']

def ccy2ticker(ccy):
    return ccy.upper() + '=X'#'%3DX'

class OptimalPortfolio(object):

    symbols = [
    #        'bitcoin',  'dash',              'factom',       'litecoin',  'nem',   'stellar',]
    #        'bitshares',     'dogecoin',          'gamecredits',  'monero',    'ripple',            
    #        'bytecoin-bcn',  'nem',       'shadowcoin',          
    #        'counterparty',  'ethereum',          'lisk',         'nem',   'ethereum',  
             'SPY', ccy2ticker('EUR'), ccy2ticker('JPY')
            ]

    def __init__(self, symbols,start=None,end=None,maxDays=None):

        if symbols:
            self.symbols = symbols

        self.n = len(symbols)

        # Check for valid symbols
        if self.n < 1:
            raise ValueError("At least one symbol required")

        self.start = start
        #start = '2/26/2014'
        self.end = end
        #end = '2/26/2017'
        self.maxDays = maxDays

        # average yearly return for each stock
        r_avg = list(map(lambda s: stocks.avg_return(s, start, end, 'd', maxDays), symbols))
        
        # covariance of asset returns
        try:
            sigma = numpy.array(stocks.cov_matrix(symbols, start, end, 'd',maxDays))
            self.bad = False
        except:
            self.bad = True
            return 
        self.r_avg = matrix(r_avg)
        sigma = matrix(sigma)
        # that was easy
        self.P = sigma
        self.q = matrix(numpy.zeros((self.n, 1)))


    def findOptimalPortfolio(self, minReturn):
        if self.bad:
            return None
        
        r_min = minReturn
        
        try:
            sol = solvers.qp(self.P, self.q, G, h, A, b)
        except ValueError:
            print('Warning: couldnt find optimal portfolio, probably minimum return is to big!')
            return None
        
        print()
        pfolio = {}
        total = 0.0
        for s,w in zip(self.symbols,list(sol['x'])):
            if w < 0.0001 or round(w*10000.0,1) == 0.0:
                continue
            total += w
            pfolio[s] = w
        for k in pfolio:
            pfolio[k] = pfolio[k]/total
        return pfolio


if __name__ == "__main__":
    try:
    opt = OptimalPortfolio(OptimalPortfolio.symbols)
    r_min = 0.01
    p = opt.findOptimalPortfolio(minReturn=r_min)
    if not p:
            print(f'ERROR: Could not find portfolio for {r_min*100}% return')
        else:
            print("Optimal Portfolio:", p)
    except Exception as e:
        print(f"Optimization failed: {str(e)}")

class OptimizerGUI:
    def __init__(self, master):
        self.master = master
        self.coin_db = CoinDB()
        self.assets = self.coin_db.coins
        self.create_widgets()
        self.running = False
        self.queue = queue.Queue()
        self.thread = None

    def create_widgets(self):
        # Control Panel
        control_frame = ttk.LabelFrame(self.master, text="Optimization Controls")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Coin Selection
        self.coin_vars = {}
        coin_scroll = tk.Scrollbar(control_frame)
        coin_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.coin_list = tk.Listbox(control_frame, selectmode=tk.MULTIPLE, yscrollcommand=coin_scroll.set)
        for coin in sorted(self.assets):
            self.coin_list.insert(tk.END, coin)
        self.coin_list.pack(fill=tk.BOTH, expand=1)
        coin_scroll.config(command=self.coin_list.yview)

        # Optimization Parameters
        param_frame = ttk.Frame(control_frame)
        param_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(param_frame, text="Generations:").grid(row=0, column=0, sticky=tk.W)
        self.generations = ttk.Entry(param_frame)
        self.generations.grid(row=0, column=1)
        self.generations.insert(0, "100")

        ttk.Label(param_frame, text="Population:").grid(row=1, column=0, sticky=tk.W)
        self.population = ttk.Entry(param_frame)
        self.population.grid(row=1, column=1)
        self.population.insert(0, "50")

        ttk.Label(param_frame, text="Mutation Rate:").grid(row=2, column=0, sticky=tk.W)
        self.mutation = ttk.Entry(param_frame)
        self.mutation.grid(row=2, column=1)
        self.mutation.insert(0, "0.1")
        
        # Optimization Objective
        ttk.Label(param_frame, text="Objective:").grid(row=3, column=0, sticky=tk.W)
        self.objective = ttk.Combobox(param_frame, values=["Best Return", "Best Risk", "Best Sharpe Ratio"])
        self.objective.grid(row=3, column=1)
        self.objective.set("Best Sharpe Ratio")
        self.objective.state(["readonly"])

        # Buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.toggle_optimization)
        self.start_btn.pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Save Results", command=self.save_results).pack(side=tk.LEFT)

        # Results Display
        results_frame = ttk.LabelFrame(self.master, text="Optimization Results")
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1, padx=5, pady=5)

        self.figure = plt.Figure(figsize=(8,6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=results_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        self.result_text = tk.Text(results_frame, height=10)
        self.result_text.pack(fill=tk.X)

    def toggle_optimization(self):
        if self.running:
            self.running = False
            self.start_btn.config(text="Start")
    else:
            self.running = True
            self.start_btn.config(text="Stop")
            self.thread = threading.Thread(target=self.run_optimization)
            self.thread.start()
        self.master.after(100, self.process_queue)

    def run_optimization(self):
        selected_coins = [self.coin_list.get(i) for i in self.coin_list.curselection()]
        if not selected_coins:
            self.queue.put(("error", "No coins selected!"))
            return

        params = {
            'generations': int(self.generations.get()),
            'population': int(self.population.get()),
            'mutation': float(self.mutation.get()),
            'coins': selected_coins,
            'objective': self.objective.get()
        }

        optimizer = PortfolioOptimizer(**params)
        for result in optimizer.optimize():
            if not self.running:
                break
            self.queue.put(("update", result))
        self.queue.put(("done", None))

    def process_queue(self):
        try:
            while True:
                msg_type, data = self.queue.get_nowait()
                if msg_type == "error":
                    self.result_text.insert(tk.END, f"Error: {data}\n")
                elif msg_type == "update":
                    self.update_display(data)
                elif msg_type == "done":
                    self.running = False
                    self.start_btn.config(text="Start")
        except queue.Empty:
            pass
        if self.running:
            self.master.after(100, self.process_queue)

    def update_display(self, data):
        self.ax.clear()
        self.ax.plot(data['frontier']['risk'], data['frontier']['return'], 'b-')
        self.ax.scatter(data['best']['risk'], data['best']['return'], c='red')
        self.ax.set_xlabel('Risk (σ)')
        self.ax.set_ylabel('Return')
        self.ax.set_title('Efficient Frontier')
        self.canvas.draw()

        # Display generation info
        text = f"Generation {data['generation']}: Best Return {data['best']['return']:.2%}, Risk {data['best']['risk']:.2%}\n"
        
        # Add portfolio composition if available
        if 'portfolio' in data['best']:
            text += "Portfolio Composition:\n"
            for coin, weight in data['best']['portfolio'].items():
                text += f"  - {coin.capitalize():<10} {weight:.2%}\n"
        
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)

    def save_results(self):
        pass  # Implement save functionality

class PortfolioOptimizer:
    def __init__(self, generations=100, population=50, mutation=0.1, coins=None, objective="Best Sharpe Ratio"):
        self.generations = generations
        self.population = population
        self.mutation = mutation
        self.coins = coins or []
        self.objective = objective
        self.analyzer = PortfolioAnalyzer(interval='1D')

    def optimize(self):
        population = self.initialize_population()
        for gen in range(self.generations):
            population = self.evolve(population)
            best = self.select_best(population)
            frontier = self.calculate_frontier(population)
            yield {
                'generation': gen+1,
                'best': self.get_portfolio_stats(best),
                'frontier': frontier
            }

    def select_best(self, population):
        if self.objective == "Best Return":
            return max(population, key=lambda p: self.analyzer.portfolioReturn(p))
        elif self.objective == "Best Risk":
            return min(population, key=lambda p: self.analyzer.portfolioStandardDev(p))
        else:  # Best Sharpe Ratio (default)
            return max(population, key=self.fitness)

    def initialize_population(self):
        return [self.random_portfolio() for _ in range(self.population)]

    def random_portfolio(self):
        weights = numpy.random.random(len(self.coins))
        weights /= weights.sum()
        return dict(zip(self.coins, weights))

    def fitness(self, portfolio):
        ret = self.analyzer.portfolioReturn(portfolio)
        risk = self.analyzer.portfolioStandardDev(portfolio)
        return ret / risk if risk > 0 else 0

    def evolve(self, population):
        population.sort(key=self.fitness, reverse=True)
        keep = int(len(population)*0.2)
        next_gen = population[:keep]
        
        while len(next_gen) < len(population):
            parents = random.choices(population[:keep], k=2)
            child = self.crossover(parents[0], parents[1])
            child = self.mutate(child)
            next_gen.append(child)
            
        return next_gen

    def crossover(self, p1, p2):
        alpha = random.random()
        return {coin: alpha*p1[coin] + (1-alpha)*p2[coin] for coin in self.coins}

    def mutate(self, portfolio):
        if random.random() < self.mutation:
            coin = random.choice(self.coins)
            delta = random.uniform(-0.1, 0.1)
            portfolio[coin] = max(0, min(1, portfolio[coin] + delta))
            total = sum(portfolio.values())
            for coin in portfolio:
                portfolio[coin] /= total
        return portfolio

    def calculate_frontier(self, population):
        returns = [self.analyzer.portfolioReturn(p) for p in population]
        risks = [self.analyzer.portfolioStandardDev(p) for p in population]
        return {'return': returns, 'risk': risks}

    def get_portfolio_stats(self, portfolio):
        return {
            'return': self.analyzer.portfolioReturn(portfolio),
            'risk': self.analyzer.portfolioStandardDev(portfolio),
            'portfolio': portfolio  # Include the full portfolio composition
        }

if __name__ == "__main__":
    root = tk.Tk()
    gui = OptimizerGUI(root)
    root.mainloop()

# Add this at the top of the file to suppress solver output
solvers.options['show_progress'] = False
