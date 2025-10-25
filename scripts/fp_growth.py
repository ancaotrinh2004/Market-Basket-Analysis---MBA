"""
FP-Growth Algorithm for Market Basket Analysis
Generates association rules and saves to PostgreSQL

Usage:
    python scripts/fp_growth.py --min-support 0.01 --min-confidence 0.1 --min-lift 1.0
"""

import argparse
import pandas as pd
from sqlalchemy import create_engine
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def get_database_connection():
    """Tạo kết nối PostgreSQL"""
    db_url = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/mba_db'
    )
    return create_engine(db_url)

def load_transactions(engine):
    """Load transaction data từ PostgreSQL"""
    print("Loading transactions from database...")
    query = "SELECT txn_id, item_name FROM stg_transaction_items ORDER BY txn_id"
    df = pd.read_sql(query, engine)
    
    # Group by transaction
    basket = df.groupby('txn_id')['item_name'].apply(list).tolist()
    print(f"Loaded {len(basket)} transactions")
    return basket

def apply_fp_growth(basket, min_support=0.01):
    """Áp dụng FP-Growth algorithm"""
    print(f"\nRunning FP-Growth with min_support={min_support}...")
    
    # Transaction encoding
    te = TransactionEncoder()
    te_ary = te.fit(basket).transform(basket)
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
    
    # FP-Growth
    frequent_itemsets = fpgrowth(
        df_encoded, 
        min_support=min_support, 
        use_colnames=True,
        max_len=None  # Không giới hạn độ dài itemset
    )
    
    print(f"Found {len(frequent_itemsets)} frequent itemsets")
    return frequent_itemsets

def generate_rules(frequent_itemsets, min_confidence=0.1, min_lift=1.0):
    """Generate association rules"""
    print(f"\nGenerating rules with min_confidence={min_confidence}, min_lift={min_lift}...")
    
    rules = association_rules(
        frequent_itemsets,
        metric="confidence",
        min_threshold=min_confidence,
        num_itemsets=len(frequent_itemsets)
    )
    
    # Filter by lift
    rules = rules[rules['lift'] >= min_lift]
    
    # Convert frozenset to string
    rules['antecedent'] = rules['antecedents'].apply(lambda x: ', '.join(list(x)))
    rules['consequent'] = rules['consequents'].apply(lambda x: ', '.join(list(x)))
    
    # Select và rename columns
    rules_clean = rules[[
        'antecedent', 
        'consequent', 
        'support', 
        'confidence', 
        'lift'
    ]].copy()
    
    # Round numbers
    rules_clean['support'] = rules_clean['support'].round(4)
    rules_clean['confidence'] = rules_clean['confidence'].round(4)
    rules_clean['lift'] = rules_clean['lift'].round(4)
    
    print(f"Generated {len(rules_clean)} rules")
    return rules_clean

def save_to_database(rules, engine, table_name='fp_growth_rules'):
    """Lưu rules vào PostgreSQL"""
    print(f"\nSaving {len(rules)} rules to table '{table_name}'...")
    
    # Add timestamp
    rules['created_at'] = datetime.now()
    
    # Save to database (replace existing table)
    rules.to_sql(
        table_name, 
        engine, 
        if_exists='replace', 
        index=False,
        method='multi'
    )
    
    print(f"✓ Rules saved successfully to '{table_name}' table")

def print_summary(rules):
    """In ra thống kê tóm tắt"""
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Total rules: {len(rules)}")
    print(f"\nSupport range: {rules['support'].min():.4f} - {rules['support'].max():.4f}")
    print(f"Confidence range: {rules['confidence'].min():.4f} - {rules['confidence'].max():.4f}")
    print(f"Lift range: {rules['lift'].min():.4f} - {rules['lift'].max():.4f}")
    
    print("\n" + "-"*60)
    print("TOP 10 RULES BY LIFT:")
    print("-"*60)
    top_rules = rules.nlargest(10, 'lift')
    print(top_rules.to_string(index=False))
    print("="*60)

def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='FP-Growth Market Basket Analysis')
    parser.add_argument('--min-support', type=float, default=0.01,
                        help='Minimum support threshold (default: 0.01)')
    parser.add_argument('--min-confidence', type=float, default=0.1,
                        help='Minimum confidence threshold (default: 0.1)')
    parser.add_argument('--min-lift', type=float, default=1.0,
                        help='Minimum lift threshold (default: 1.0)')
    parser.add_argument('--table-name', type=str, default='fp_growth_rules',
                        help='Output table name (default: fp_growth_rules)')
    parser.add_argument('--no-save', action='store_true',
                        help='Do not save to database (dry run)')
    
    args = parser.parse_args()
    
    try:
        # Connect to database
        engine = get_database_connection()
        
        # Load data
        basket = load_transactions(engine)
        
        # Apply FP-Growth
        frequent_itemsets = apply_fp_growth(basket, args.min_support)
        
        # Generate rules
        rules = generate_rules(
            frequent_itemsets,
            args.min_confidence,
            args.min_lift
        )
        
        # Print summary
        print_summary(rules)
        
        # Save to database
        if not args.no_save:
            save_to_database(rules, engine, args.table_name)
        else:
            print("\n[DRY RUN] Rules not saved (use without --no-save to save)")
        
        print("\n✓ Process completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())