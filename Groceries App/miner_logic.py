import pandas as pd
from itertools import combinations
from collections import defaultdict
import random
from typing import List, Tuple, Dict, Callable, Optional

class AssociationRuleMinerLogic:
    def __init__(self):
        self.transactions = []
        self.vertical_data = defaultdict(set)
        self.frequent_itemsets = []
        self.association_rules = []
        self.progress_callback: Optional[Callable[[str], None]] = None
    
    # to put callback
    def set_progress_callback(self, callback: Callable[[str], None]):
        self.progress_callback = callback
    
    # log all the process made
    def _log_progress(self, message: str):
        if self.progress_callback:
            self.progress_callback(message)
    
    def preprocess_data(self, data, lowercase_items=True):
        self._log_progress("Starting data preprocessing...")
        data = data.copy()
        
        data['Member_number'] = data['Member_number'].astype(str).str.strip()
        data['Date'] = data['Date'].astype(str).str.strip()
        data['itemDescription'] = data['itemDescription'].astype(str).str.strip()

        if lowercase_items:
            data['itemDescription'] = data['itemDescription'].str.lower()
            self._log_progress("Converted items to lowercase")
        
        data = data.dropna(subset=['Member_number', 'Date', 'itemDescription'])
        self._log_progress(f"Removed rows with null values, {len(data)} remaining")
        
        data = data[data['itemDescription'] != '']
        self._log_progress(f"Removed empty items, {len(data)} remaining")
        
        transactions = data.groupby(['Member_number', 'Date'])['itemDescription'].apply(list).reset_index()
        
        transactions = transactions[transactions['itemDescription'].apply(len) > 0]
        self._log_progress(f"Created {len(transactions)} transactions")
        
        self.transactions = transactions['itemDescription'].tolist()
        return self.transactions
    
    # apply vertical format algorithm
    def create_vertical_format(self, transactions):
        self._log_progress("Converting to vertical format...")
        self.vertical_data = defaultdict(set)
        
        for idx, transaction in enumerate(transactions):
            transaction_id = f"T{idx+1}"
            for item in transaction:
                self.vertical_data[item].add(transaction_id)
        
        self._log_progress(f"Created vertical format with {len(self.vertical_data)} unique items")
        return self.vertical_data
    
    # run the apriori for vertical algorithm
    def apriori_vertical(self, vertical_data, min_support_count):
        self._log_progress("\nStarting Apriori algorithm...")
        self._log_progress(f"Minimum support count: {min_support_count}")
        
        items = [frozenset([item]) for item in vertical_data.keys()]
        
        self.frequent_itemsets = []
        level = 1
        current_frequent = []
        last_level_frequent = []
        itemset_counter = 0
        
        self._log_progress("\nGenerating 1-itemsets...")
        
        # Generate 1-itemsets
        for item in items:
            support = len(vertical_data[list(item)[0]])
            if support >= min_support_count:
                itemset_counter += 1
                current_frequent.append((item, support))
                self._log_progress(f"Frequent itemset {itemset_counter}: {list(item)[0]} (support: {support})")
        
        self.frequent_itemsets.extend(current_frequent)
        last_level_frequent = current_frequent.copy()
        
        while current_frequent:
            level += 1
            next_level = []
            
            self._log_progress(f"\nGenerating {level}-itemsets...")
            candidates = self.generate_candidates([itemset for itemset, _ in current_frequent], level)
            
            for candidate in candidates:
                items_list = list(candidate)
                common_transactions = vertical_data[items_list[0]]
                
                for item in items_list[1:]:
                    common_transactions = common_transactions & vertical_data[item]
                
                support = len(common_transactions)
                
                if support >= min_support_count:
                    itemset_counter += 1
                    next_level.append((candidate, support))
                    self._log_progress(f"Frequent itemset {itemset_counter}: {', '.join(candidate)} (support: {support})")
            
            if not next_level:
                self._log_progress(f"\nNo frequent {level}-itemsets found. Stopping.")
                break
                
            current_frequent = next_level
            self.frequent_itemsets.extend(current_frequent)
            last_level_frequent = current_frequent.copy()
        
        self._log_progress(f"\nTotal frequent itemsets found: {len(self.frequent_itemsets)}")
        self._log_progress(f"Largest itemset size: {level-1}")
        
        return self.frequent_itemsets, last_level_frequent
    
    def generate_association_rules(self, itemsets, min_confidence, all_frequent_itemsets=None):
        self._log_progress("\nGenerating association rules from largest itemsets...")
        self._log_progress(f"Minimum confidence: {min_confidence:.2f}")
        
        self.association_rules = []
        rule_counter = 0
        
        # Create a dictionary for quick support lookup
        support_dict = {itemset: support for itemset, support in all_frequent_itemsets}
        
        # get the size of the largest itemsets
        if not itemsets:
            self._log_progress("\nNo itemsets available for rule generation.")
            return self.association_rules
        
        itemset_size = len(next(iter(itemsets))[0])
        self._log_progress(f"\nGenerating rules from {itemset_size}-itemsets...")
        
        for itemset, support_count in itemsets:
            if len(itemset) < 2:
                continue
                
            # Generate all non-empty subsets
            items = list(itemset)
            for i in range(1, len(itemset)):
                for antecedent in combinations(items, i):
                    antecedent = frozenset(antecedent)
                    consequent = itemset - antecedent
                    
                    antecedent_support = support_dict.get(antecedent, 0)
                    
                    # Only create rule if we have support for the left side
                    if antecedent_support > 0:
                        confidence = support_count / antecedent_support
                        
                        if confidence >= min_confidence:
                            consequent_support = support_dict.get(consequent, 0)
                            lift = confidence / (consequent_support / support_count) if consequent_support > 0 else float('inf')
                            
                            rule_counter += 1
                            self.association_rules.append((antecedent, consequent, support_count, confidence, lift))
                            self._log_progress(
                                f"Rule {rule_counter}: {{{', '.join(antecedent)}}} => {{{', '.join(consequent)}}} "
                                f"(support: {support_count}, confidence: {confidence:.2f}, lift: {lift:.2f})"
                            )
        
        self._log_progress(f"\nTotal association rules found: {len(self.association_rules)}")
        return self.association_rules
        
    # get candidate itemsets of the specified level
    def generate_candidates(self, prev_itemsets, level):
        candidates = set()
        
        for i in range(len(prev_itemsets)):
            for j in range(i+1, len(prev_itemsets)):
                # Union of two itemsets
                new_candidate = prev_itemsets[i].union(prev_itemsets[j])
                
                if len(new_candidate) == level:
                    # Check if all subsets are frequent
                    all_subsets_frequent = True
                    for subset in combinations(new_candidate, level-1):
                        if frozenset(subset) not in prev_itemsets:
                            all_subsets_frequent = False
                            break
                    
                    if all_subsets_frequent:
                        candidates.add(new_candidate)
        
        return list(candidates)
    
    def get_results_text(self, frequent_itemsets, association_rules):
        # Format frequent itemsets
        itemsets_text = "Frequent Itemsets (sorted by support):\n"
        itemsets_text += "="*70 + "\n\n"
        
        # Sort itemsets by support (descending)
        frequent_itemsets.sort(key=lambda x: x[1], reverse=True)
        
        # Group itemsets by their size (1-itemsets, 2-itemsets, etc.)
        itemsets_by_size = defaultdict(list)
        for itemset, support in frequent_itemsets:
            itemsets_by_size[len(itemset)].append((itemset, support))
        
        # Display each group separately
        for size in sorted(itemsets_by_size.keys()):
            itemsets_text += f"frequent itemset {size}\n"
            itemsets_text += "-"*18 + "\n"
            
            for itemset, support in itemsets_by_size[size]:
                items_str = ", ".join(itemset)
                itemsets_text += f"Itemset: {{{items_str}}}, Support: {support}\n"
            
            itemsets_text += "\n"  # Add empty line between groups
        
        # Format association rules
        rules_text = "Association Rules (sorted by confidence):\n"
        rules_text += "="*70 + "\n"
        
        # Sort rules by confidence (descending)
        association_rules.sort(key=lambda x: x[3], reverse=True)
        
        for antecedent, consequent, support, confidence, lift in association_rules:
            ant_str = ", ".join(antecedent)
            cons_str = ", ".join(consequent)
            rules_text += (
                f"Rule: {{{ant_str}}} => {{{cons_str}}}, "
                f"Support: {support}, Confidence: {confidence:.2f}, Lift: {lift:.2f}\n"
            )
        
        return itemsets_text, rules_text