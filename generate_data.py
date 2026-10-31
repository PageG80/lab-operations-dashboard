import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

def generate_lab_data(num_records=5000):
    print(f"Generating {num_records} synthetic hospital lab records...")

    departments = ['Hematology', 'Biochemistry', 'Immunology', 'Microbiology']
    machines = {
        'Hematology': ['Sysmex-XN1000', 'Mindray-BC6800'],
        'Biochemistry': ['Cobas-6000', 'Abbott-Architect'],
        'Immunology': ['Atellica-IM', 'Access-2'],
        'Microbiology': ['Vitek-2', 'Bactec-FX']
    }
    
    sample_conditions = ['Normal', 'Hemolyzed', 'Clotted', 'Contaminated', 'Insufficient Volume']
    condition_weights = [0.80, 0.08, 0.05, 0.04, 0.03] # Realistic error distribution

    start_date = datetime.now() - timedelta(days=90)
    timestamps_collection = [
        start_date + timedelta(seconds=int(np.random.randint(0, 90 * 86400))) 
        for _ in range(num_records)
    ]
    timestamps_collection.sort()

    data = []
    for i in range(num_records):
        test_id = f"TST-{10000 + i}"
        patient_id = f"PAT-{np.random.randint(1000, 9999)}"
        dept = np.random.choice(departments, p=[0.35, 0.40, 0.15, 0.10])
        machine = np.random.choice(machines[dept])
        
        col_time = timestamps_collection[i]
        
        queue_delay_mins = int(np.random.exponential(scale=25) + np.random.randint(5, 30))
        proc_time_mins = int(np.random.normal(loc=15, scale=5))
        proc_time_mins = max(5, proc_time_mins) # Minimum 5 mins
        
        processing_time = col_time + timedelta(minutes=queue_delay_mins)
        completion_time = processing_time + timedelta(minutes=proc_time_mins)
        
        total_tat_mins = int((completion_time - col_time).total_seconds() / 60)
        
        condition = np.random.choice(sample_conditions, p=condition_weights)
        is_rejected = condition != 'Normal'
        
        is_critical = np.random.choice([True, False], p=[0.05, 0.95])

        data.append({
            'test_id': test_id,
            'patient_id': patient_id,
            'department': dept,
            'machine_id': machine,
            'collection_timestamp': col_time.strftime('%Y-%m-%d %H:%M:%S'),
            'completion_timestamp': completion_time.strftime('%Y-%m-%d %H:%M:%S'),
            'turnaround_time_mins': total_tat_mins,
            'sample_condition': condition,
            'is_rejected': 1 if is_rejected else 0,
            'critical_flag': 1 if is_critical else 0
        })

    df = pd.DataFrame(data)
    return df

def save_to_sqlite(df, db_path='data/lab_data.db'):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    df.to_sql('lab_operations', conn, if_exists='replace', index=False)
    conn.close()
    print(f"Successfully saved database to {db_path} with {len(df)} rows.")

if __name__ == '__main__':
    df = generate_lab_data(5000)
    save_to_sqlite(df)