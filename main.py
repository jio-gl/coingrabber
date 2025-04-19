#!/usr/bin/env python3
"""
CoinGrabber - Cryptocurrency Portfolio Manager
"""

import sys
import os
import webbrowser
from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

from coins import CoinDB
from portfolio import PortfolioAnalyzer
from optimization import OptimalPortfolio, OptimizerGUI
from scraper2024 import get_coins

class CoinGrabberGUI:
    def __init__(self, master):
        self.master = master
        master.title("CoinGrabber 3.0")
        master.geometry("1200x800")
        
        self.coin_db = CoinDB()
        self.analyzer = PortfolioAnalyzer(interval='1D')
        self.current_portfolio = {}
        
        self.create_widgets()
        self.load_initial_data()

    def create_widgets(self):
        # Configure main container
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(fill=BOTH, expand=1)

        # Create notebook for multiple tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=BOTH, expand=1)

        # Create tabs
        self.create_data_tab()
        self.create_analysis_tab()
        self.create_optimization_tab()
        
        # Status bar
        self.status = ttk.Label(self.master, text="Ready", relief=SUNKEN)
        self.status.pack(side=BOTTOM, fill=X)

    def create_data_tab(self):
        # Data management tab
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="Data Management")
        
        # Coin list
        self.coin_list = ttk.Treeview(data_frame, columns=('coin', 'prices'), show='headings')
        self.coin_list.heading('coin', text='Coin')
        self.coin_list.heading('prices', text='Price Data Points')
        self.coin_list.pack(fill=BOTH, expand=1, padx=5, pady=5)
        
        # Data controls
        btn_frame = ttk.Frame(data_frame)
        btn_frame.pack(fill=X)
        ttk.Button(btn_frame, text="Refresh Data", command=self.refresh_data).pack(side=LEFT)
        ttk.Button(btn_frame, text="Export CSV", command=self.export_data).pack(side=LEFT)

    def create_analysis_tab(self):
        # Portfolio analysis tab
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Portfolio Analysis")
        
        # Portfolio controls
        control_frame = ttk.Frame(analysis_frame)
        control_frame.pack(fill=X)
        ttk.Button(control_frame, text="Load Portfolio", command=self.load_portfolio).pack(side=LEFT)
        ttk.Button(control_frame, text="Save Portfolio", command=self.save_portfolio).pack(side=LEFT)
        
        # Analysis results
        self.analysis_text = tk.Text(analysis_frame, height=15)
        self.analysis_text.pack(fill=BOTH, expand=1)

    def create_optimization_tab(self):
        # Portfolio optimization tab
        opt_frame = ttk.Frame(self.notebook)
        self.notebook.add(opt_frame, text="Optimization")
        
        # Embed the OptimizerGUI
        self.optimizer = OptimizerGUI(opt_frame)

    def load_initial_data(self):
        self.update_status("Loading coin data...")
        self.coin_list.delete(*self.coin_list.get_children())
        # Get coins from scraper2024 and format for display
        for coin in get_coins():
            display_name = ' '.join([word.capitalize() for word in coin.split('-')])
            prices = self.coin_db.prices(coin, '1D')
            self.coin_list.insert('', 'end', values=(display_name, len(prices)))
        self.update_status("Ready")

    def refresh_data(self):
        self.update_status("Downloading latest data...")
        # Add data refresh logic here
        self.load_initial_data()
        self.update_status("Data updated")

    def export_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Add export logic here
                self.update_status(f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    def load_portfolio(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Add portfolio loading logic
                self.update_status("Portfolio loaded")
            except Exception as e:
                messagebox.showerror("Load Error", str(e))

    def save_portfolio(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Add portfolio saving logic
                self.update_status("Portfolio saved")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

    def update_status(self, message):
        self.status.config(text=message)
        self.master.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = CoinGrabberGUI(root)
    root.mainloop()
