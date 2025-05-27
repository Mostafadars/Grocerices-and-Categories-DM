import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from miner_logic import AssociationRuleMinerLogic
import webbrowser
import os
import pandas as pd


class AssociationRuleMinerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Groceries Association Rule Miner")
        self.root.geometry("1200x850")
        
        # Initialize the logic handler
        self.miner = AssociationRuleMinerLogic()
        self.miner.set_progress_callback(self.update_progress_log)
        
        # Set theme
        self.style = ttk.Style(theme='pulse')
        
        # Variables
        self.file_path = tk.StringVar()
        self.min_support = tk.DoubleVar(value=0.01)
        self.min_confidence = tk.DoubleVar(value=0.5)
        self.data_percentage = tk.DoubleVar(value=100.0)
        self.lowercase_items = tk.BooleanVar(value=True)
        
        # Create UI
        self.create_widgets()
    
    def update_progress_log(self, message: str):
        """Callback function to update the progress log"""
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.root.update_idletasks()  # Ensure UI updates
    
    def create_widgets(self):
        # Header Frame
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill=X, padx=10, pady=(10, 5))
        
        ttk.Label(
            header_frame, 
            text="Groceries Association Rule Miner", 
            font=('Helvetica', 16, 'bold'),
            bootstyle=PRIMARY
        ).pack(side=LEFT)
        
        # Help button
        ttk.Button(
            header_frame, 
            text="Help", 
            command=self.show_help, 
            bootstyle=(INFO, OUTLINE),
            width=8
        ).pack(side=RIGHT, padx=5)
        
        # Main container frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=YES, padx=10, pady=5)
        
        # Left panel (controls)
        control_frame = ttk.Frame(main_frame, width=350, padding=10)
        control_frame.pack(side=LEFT, fill=Y)
        
        # File Selection
        file_frame = ttk.Labelframe(
            control_frame, 
            text=" Input File ", 
            padding=15,
            bootstyle=PRIMARY
        )
        file_frame.pack(fill=X, pady=5)
        
        ttk.Label(file_frame, text="CSV File:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        file_entry = ttk.Entry(
            file_frame, 
            textvariable=self.file_path, 
            width=30,
            bootstyle=PRIMARY
        )
        file_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=EW)
        ttk.Button(
            file_frame, 
            text="Browse", 
            command=self.browse_file, 
            width=8,
            bootstyle=(PRIMARY, OUTLINE)
        ).grid(row=1, column=2, padx=5)
        
        # Preprocessing Options
        preprocess_frame = ttk.Labelframe(
            control_frame, 
            text=" Preprocessing Options ", 
            padding=15,
            bootstyle=INFO
        )
        preprocess_frame.pack(fill=X, pady=5)
        
        ttk.Checkbutton(
            preprocess_frame, 
            text="Convert items to lowercase", 
            variable=self.lowercase_items,
            bootstyle="info-roundtoggle"
        ).pack(anchor=W, padx=5, pady=2)
        
        # Parameters
        param_frame = ttk.Labelframe(
            control_frame, 
            text=" Mining Parameters ", 
            padding=15,
            bootstyle=SUCCESS
        )
        param_frame.pack(fill=X, pady=5)
        
        # Data percentage
        ttk.Label(param_frame, text="Data Percentage (%):").grid(row=0, column=0, padx=5, pady=2, sticky=W)
        ttk.Entry(
            param_frame, 
            textvariable=self.data_percentage, 
            width=8,
            bootstyle=SUCCESS
        ).grid(row=0, column=1, padx=5, pady=2, sticky=W)
        ttk.Label(param_frame, text="(1-100)").grid(row=0, column=2, padx=5, pady=2, sticky=W)
        
        # Min support
        ttk.Label(param_frame, text="Min Support:").grid(row=1, column=0, padx=5, pady=2, sticky=W)
        ttk.Entry(
            param_frame, 
            textvariable=self.min_support, 
            width=8,
            bootstyle=SUCCESS
        ).grid(row=1, column=1, padx=5, pady=2, sticky=W)
        ttk.Label(param_frame, text="(count or decimal)").grid(row=1, column=2, padx=5, pady=2, sticky=W)
        
        # Min confidence
        ttk.Label(param_frame, text="Min Confidence (%):").grid(row=2, column=0, padx=5, pady=2, sticky=W)
        ttk.Entry(
            param_frame, 
            textvariable=self.min_confidence, 
            width=8,
            bootstyle=SUCCESS
        ).grid(row=2, column=1, padx=5, pady=2, sticky=W)
        ttk.Label(param_frame, text="(0-100)").grid(row=2, column=2, padx=5, pady=2, sticky=W)
        
        # Buttons
        button_frame = ttk.Frame(control_frame, padding=10)
        button_frame.pack(fill=X, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Run Analysis", 
            command=self.run_analysis,
            bootstyle=SUCCESS,
            width=20
        ).pack(fill=X, pady=3)
        
        ttk.Button(
            button_frame, 
            text="Clear Results", 
            command=self.clear_results,
            bootstyle=(DANGER, OUTLINE),
            width=20
        ).pack(fill=X, pady=3)
        
        ttk.Button(
            button_frame, 
            text="Export Results", 
            command=self.export_results,
            bootstyle=(PRIMARY, OUTLINE),
            width=20
        ).pack(fill=X, pady=3)
        
        # Right panel (results)
        results_frame = ttk.Frame(main_frame, padding=10)
        results_frame.pack(side=RIGHT, fill=BOTH, expand=YES)
        
        # Results Notebook
        self.results_notebook = ttk.Notebook(results_frame, bootstyle=PRIMARY)
        self.results_notebook.pack(fill=BOTH, expand=YES)
        
        # Progress Tab
        self.progress_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.progress_frame, text="Progress Log")
        
        self.progress_text = tk.Text(
            self.progress_frame, 
            wrap="word", 
            font=('Consolas', 9),
            padx=10, 
            pady=10
        )
        scroll_y = ttk.Scrollbar(
            self.progress_frame, 
            orient=VERTICAL, 
            command=self.progress_text.yview,
            bootstyle=ROUND
        )
        self.progress_text.configure(yscrollcommand=scroll_y.set)
        
        scroll_y.pack(side=RIGHT, fill=Y)
        self.progress_text.pack(fill=BOTH, expand=YES)
        
        # Frequent Itemsets Tab
        self.frequent_itemsets_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.frequent_itemsets_frame, text="Frequent Itemsets")
        
        self.frequent_itemsets_text = tk.Text(
            self.frequent_itemsets_frame, 
            wrap="none", 
            font=('Consolas', 9),
            padx=10, 
            pady=10
        )
        scroll_y = ttk.Scrollbar(
            self.frequent_itemsets_frame, 
            orient=VERTICAL, 
            command=self.frequent_itemsets_text.yview,
            bootstyle=ROUND
        )
        scroll_x = ttk.Scrollbar(
            self.frequent_itemsets_frame, 
            orient=HORIZONTAL, 
            command=self.frequent_itemsets_text.xview,
            bootstyle=ROUND
        )
        self.frequent_itemsets_text.configure(
            yscrollcommand=scroll_y.set, 
            xscrollcommand=scroll_x.set
        )
        
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.pack(side=BOTTOM, fill=X)
        self.frequent_itemsets_text.pack(fill=BOTH, expand=YES)
        
        # Association Rules Tab
        self.association_rules_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.association_rules_frame, text="Association Rules")
        
        self.association_rules_text = tk.Text(
            self.association_rules_frame, 
            wrap="none", 
            font=('Consolas', 9),
            padx=10, 
            pady=10
        )
        scroll_y = ttk.Scrollbar(
            self.association_rules_frame, 
            orient=VERTICAL, 
            command=self.association_rules_text.yview,
            bootstyle=ROUND
        )
        scroll_x = ttk.Scrollbar(
            self.association_rules_frame, 
            orient=HORIZONTAL, 
            command=self.association_rules_text.xview,
            bootstyle=ROUND
        )
        self.association_rules_text.configure(
            yscrollcommand=scroll_y.set, 
            xscrollcommand=scroll_x.set
        )
        
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.pack(side=BOTTOM, fill=X)
        self.association_rules_text.pack(fill=BOTH, expand=YES)
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=SUNKEN,
            anchor=W,
            bootstyle=(PRIMARY, INVERSE),
            font=('Helvetica', 9)
        )
        self.status_bar.pack(side=BOTTOM, fill=X)
        
        # Configure the grid to make the entry expand
        file_frame.columnconfigure(0, weight=1)
    
    def show_help(self):
        """Show help information"""
        help_text = """
        Association Rule Miner Help
        
        1. Select a CSV file containing transaction data
        2. Set preprocessing options if needed
        3. Configure mining parameters:
           - Data Percentage: Use a subset of data for testing
           - Min Support: Minimum frequency for itemsets
           - Min Confidence: Minimum strength for rules
        4. Click 'Run Analysis' to start mining
        5. View results in the tabs
        6. Export results if desired
        
        Note: The CSV should have columns for Member_number, Date, and itemDescription.
        """
        messagebox.showinfo("Help", help_text.strip())
    
    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filename:
            self.file_path.set(filename)
            self.status_var.set(f"Selected file: {filename}")
            self.progress_text.insert(tk.END, f"Input file selected: {filename}\n")
    
    def clear_results(self):
        self.progress_text.delete(1.0, tk.END)
        self.frequent_itemsets_text.delete(1.0, tk.END)
        self.association_rules_text.delete(1.0, tk.END)
        self.status_var.set("Results cleared. Ready for new analysis.")
        self.progress_text.insert(tk.END, "Results cleared. Ready for new analysis.\n")
    
    def export_results(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Results As"
            )
            
            if file_path:
                with open(file_path, "w") as f:
                    f.write("=== Association Rule Mining Results ===\n\n")
                    f.write("PROGRESS LOG:\n")
                    f.write(self.progress_text.get(1.0, tk.END))
                    f.write("\n\nFREQUENT ITEMSETS:\n")
                    f.write(self.frequent_itemsets_text.get(1.0, tk.END))
                    f.write("\n\nASSOCIATION RULES:\n")
                    f.write(self.association_rules_text.get(1.0, tk.END))
                
                self.status_var.set(f"Results successfully exported to {file_path}")
                self.progress_text.insert(tk.END, f"\nResults exported to: {file_path}\n")
                
                # Open the containing folder
                if messagebox.askyesno("Export Complete", "Results exported successfully. Open containing folder?"):
                    webbrowser.open(f"file://{os.path.dirname(os.path.abspath(file_path))}")
                    
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
            self.status_var.set("Export failed")
            self.progress_text.insert(tk.END, f"\nError during export: {str(e)}\n")

    def run_analysis(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a CSV file first")
            return
        
        try:
            self.clear_results()  # Clear previous results
            self.status_var.set("Processing data...")
            self.root.update()
            
            # Validate parameters
            percentage = self.data_percentage.get()
            if not (1 <= percentage <= 100):
                messagebox.showerror("Error", "Data percentage must be between 1 and 100")
                return
            
            min_confidence = self.min_confidence.get()
            if not (0 <= min_confidence <= 100):
                messagebox.showerror("Error", "Confidence must be between 0 and 100")
                return
            
            # Read and preprocess data
            df = pd.read_csv(self.file_path.get())
            transactions = self.miner.preprocess_data(df, self.lowercase_items.get())
            
            # Apply percentage selection
            if percentage < 100.0:
                num_transactions = int(len(transactions) * percentage / 100.0)
                transactions = random.sample(transactions, num_transactions)
                self.status_var.set(f"Processing {len(transactions)} transactions ({percentage}% of data)...")
                self.root.update()
            
            # Convert to vertical format
            vertical_data = self.miner.create_vertical_format(transactions)
            
            # Get min support count (convert from percentage to absolute count)
            min_support_count = self.min_support.get()
            if min_support_count < 1:  # Assume it's a percentage if < 1
                min_support_count = max(1, int(min_support_count * len(transactions)))
            
            # Mine frequent itemsets with progress reporting
            self.status_var.set("Mining frequent itemsets...")
            self.root.update()
            
            # Add progress tab to notebook
            self.results_notebook.select(self.progress_frame)
            
            # Get both all frequent itemsets and the last level's itemsets
            all_frequent_itemsets, last_level_itemsets = self.miner.apriori_vertical(
                vertical_data, 
                min_support_count
            )
            
            # Generate association rules only from the last level's itemsets
            self.status_var.set("Generating association rules from largest itemsets...")
            self.root.update()
            
            association_rules = self.miner.generate_association_rules(
                last_level_itemsets, 
                min_confidence/100.0,
                all_frequent_itemsets=all_frequent_itemsets
            )
            
            # Display results (still show all frequent itemsets, but rules only from last level)
            itemsets_text, rules_text = self.miner.get_results_text(all_frequent_itemsets, association_rules)
            
            self.frequent_itemsets_text.insert(tk.END, itemsets_text)
            self.association_rules_text.insert(tk.END, rules_text)
            
            self.status_var.set(f"Analysis complete. Found {len(all_frequent_itemsets)} itemsets and {len(association_rules)} rules.")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred during analysis")
            self.progress_text.insert(tk.END, f"\nError: {str(e)}\n")

if __name__ == "__main__":
    root = ttk.Window(themename="pulse")
    
    # Set window icon (replace with your own icon if available)
    try:
        root.iconbitmap('rule_miner_icon.ico')  # Windows
    except:
        pass
    
    app = AssociationRuleMinerUI(root)
    
    # Center the window
    window_width = 1200
    window_height = 850
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    root.mainloop()