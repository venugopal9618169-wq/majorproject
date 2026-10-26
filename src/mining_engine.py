"""
Association Rule Mining Engine: Apriori and FP-Growth implementations
Designed for ETL/ELT metadata and operational transaction profiling.
"""

import time
from collections import defaultdict
from itertools import combinations
import pandas as pd
import numpy as np


class FPTreeNode:
    """Node in the FP-Tree"""
    def __init__(self, item, count=1, parent=None):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.node_link = None

    def increment(self, count=1):
        self.count += count


class FPGrowthMiner:
    """
    Frequent Pattern Growth (FP-Growth) Mining Engine
    Builds a compact prefix-tree (FP-Tree) and mines conditional trees
    requiring only 2 scans of the transaction database.
    """
    def __init__(self, min_support=0.15):
        self.min_support = min_support

    def fit_transform(self, transactions):
        total_txns = len(transactions)
        min_count = max(1, int(self.min_support * total_txns))

        # Pass 1: Item frequency count
        item_counts = defaultdict(int)
        for txn in transactions:
            for item in txn:
                item_counts[item] += 1

        # Filter items above min_support
        frequent_items = {item: count for item, count in item_counts.items() if count >= min_count}
        if not frequent_items:
            return pd.DataFrame(columns=['itemsets', 'support', 'count'])

        # Sort order for deterministic tree insertion
        sorted_items = sorted(frequent_items.keys(), key=lambda x: (frequent_items[x], str(x)), reverse=True)
        rank = {item: i for i, item in enumerate(sorted_items)}

        # Pass 2: Build FP-Tree
        root = FPTreeNode(None, 0, None)
        header_table = {item: [frequent_items[item], None] for item in frequent_items}

        for txn in transactions:
            # Filter and sort items according to rank
            filtered_txn = [item for item in txn if item in frequent_items]
            filtered_txn.sort(key=lambda x: rank[x])

            curr_node = root
            for item in filtered_txn:
                if item in curr_node.children:
                    curr_node.children[item].increment(1)
                else:
                    new_node = FPTreeNode(item, 1, curr_node)
                    curr_node.children[item] = new_node
                    # Update header link
                    if header_table[item][1] is None:
                        header_table[item][1] = new_node
                    else:
                        head = header_table[item][1]
                        while head.node_link is not None:
                            head = head.node_link
                        head.node_link = new_node
                curr_node = curr_node.children[item]

        # Mine FP-Tree
        patterns = {}
        self._mine_tree(header_table, min_count, set(), patterns)

        results = []
        for itemset, cnt in patterns.items():
            results.append({
                'itemsets': frozenset(itemset),
                'support': round(cnt / total_txns, 4),
                'count': cnt
            })

        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values(by=['support', 'count'], ascending=False).reset_index(drop=True)
        return df

    def _mine_tree(self, header_table, min_count, prefix, patterns):
        # Sort items in ascending frequency order
        sorted_items = sorted(header_table.keys(), key=lambda x: header_table[x][0])

        for item in sorted_items:
            new_prefix = prefix.copy()
            new_prefix.add(item)
            item_count = header_table[item][0]
            patterns[frozenset(new_prefix)] = item_count

            # Find conditional pattern base
            cond_patterns = []
            node = header_table[item][1]
            while node is not None:
                path = []
                p = node.parent
                while p.item is not None:
                    path.append(p.item)
                    p = p.parent
                if path:
                    cond_patterns.append((path, node.count))
                node = node.node_link

            # Build conditional tree
            cond_counts = defaultdict(int)
            for path, count in cond_patterns:
                for elem in path:
                    cond_counts[elem] += count

            cond_header = {el: [cond_counts[el], None] for el in cond_counts if cond_counts[el] >= min_count}
            if not cond_header:
                continue

            cond_rank = {el: i for i, el in enumerate(sorted(cond_header.keys(), key=lambda x: cond_header[x][0], reverse=True))}
            cond_root = FPTreeNode(None, 0, None)

            for path, count in cond_patterns:
                filtered_path = [el for el in path if el in cond_header]
                filtered_path.sort(key=lambda x: cond_rank[x])

                curr = cond_root
                for el in filtered_path:
                    if el in curr.children:
                        curr.children[el].increment(count)
                    else:
                        new_node = FPTreeNode(el, count, curr)
                        curr.children[el] = new_node
                        if cond_header[el][1] is None:
                            cond_header[el][1] = new_node
                        else:
                            h = cond_header[el][1]
                            while h.node_link is not None:
                                h = h.node_link
                            h.node_link = new_node
                    curr = curr.children[el]

            self._mine_tree(cond_header, min_count, new_prefix, patterns)


class AprioriMiner:
    """
    Classic Apriori Mining Engine
    Iteratively generates (k)-candidate itemsets and validates support
    by scanning the transactions repeatedly.
    """
    def __init__(self, min_support=0.15):
        self.min_support = min_support

    def fit_transform(self, transactions):
        total_txns = len(transactions)
        min_count = max(1, int(self.min_support * total_txns))
        
        # 1-itemsets
        item_counts = defaultdict(int)
        for txn in transactions:
            for item in txn:
                item_counts[frozenset([item])] += 1

        frequent = {itemset: cnt for itemset, cnt in item_counts.items() if cnt >= min_count}
        all_frequent = dict(frequent)
        current_frequent = set(frequent.keys())
        k = 2

        while current_frequent:
            # Candidate generation (join step)
            items = list(set().union(*current_frequent))
            candidates = set()
            for c in combinations(items, k):
                c_set = frozenset(c)
                # Prune step
                subsets = [frozenset(s) for s in combinations(c, k - 1)]
                if all(sub in current_frequent for sub in subsets):
                    candidates.add(c_set)

            if not candidates:
                break

            # Scan transactions
            candidate_counts = defaultdict(int)
            for txn in transactions:
                txn_set = set(txn)
                for cand in candidates:
                    if cand.issubset(txn_set):
                        candidate_counts[cand] += 1

            current_frequent = {cand: cnt for cand, cnt in candidate_counts.items() if cnt >= min_count}
            all_frequent.update(current_frequent)
            k += 1

        results = []
        for itemset, cnt in all_frequent.items():
            results.append({
                'itemsets': itemset,
                'support': round(cnt / total_txns, 4),
                'count': cnt
            })

        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values(by=['support', 'count'], ascending=False).reset_index(drop=True)
        return df


def generate_association_rules(frequent_itemsets_df, min_confidence=0.6, min_lift=1.0):
    """
    Generates association rules from mined frequent itemsets:
    X -> Y with Support, Confidence, Lift, and Conviction metrics.
    """
    if frequent_itemsets_df.empty:
        return pd.DataFrame(columns=['antecedents', 'consequents', 'support', 'confidence', 'lift', 'conviction'])

    itemset_support = {row['itemsets']: row['support'] for _, row in frequent_itemsets_df.iterrows()}
    rules = []

    for itemset, sup_xy in itemset_support.items():
        if len(itemset) < 2:
            continue

        for r in range(1, len(itemset)):
            for ante in combinations(itemset, r):
                ante = frozenset(ante)
                cons = itemset - ante
                sup_x = itemset_support.get(ante)
                sup_y = itemset_support.get(cons)

                if sup_x and sup_y:
                    conf = sup_xy / sup_x
                    lift = conf / sup_y

                    # Conviction: (1 - sup_y) / (1 - conf)
                    if conf < 1.0:
                        conviction = (1 - sup_y) / (1 - conf)
                    else:
                        conviction = np.inf

                    if conf >= min_confidence and lift >= min_lift:
                        rules.append({
                            'antecedents': list(ante),
                            'consequents': list(cons),
                            'support': round(sup_xy, 4),
                            'confidence': round(conf, 4),
                            'lift': round(lift, 4),
                            'conviction': round(conviction, 4) if conviction != np.inf else 999.0
                        })

    df_rules = pd.DataFrame(rules)
    if not df_rules.empty:
        df_rules = df_rules.sort_values(by=['confidence', 'lift'], ascending=False).reset_index(drop=True)
    return df_rules
