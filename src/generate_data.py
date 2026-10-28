import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_synthetic_ehr_data(num_records: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Generates synthetic post-acute EHR dataset containing intentional anomalies:
    1. FAC_104 (120 beds) has 0 hospital transfers (simulates unmapped staging code).
    2. Date logic violations (discharge_date < admission_date).
    3. Daily MME values exceeding 90 without clinician override.
    4. Out-of-bounds readmission intervals.
    5. Null / unmapped payer categories.
    """
    np.random.seed(seed)
    base_date = datetime(2026, 10, 1)

    facilities = {
        'FAC_101': {'beds': 30,  'transfer_rate': 0.08},
        'FAC_102': {'beds': 45,  'transfer_rate': 0.12},
        'FAC_103': {'beds': 80,  'transfer_rate': 0.05},
        'FAC_104': {'beds': 120, 'transfer_rate': 0.00},  # INJECTED ANOMALY: Unmapped transfer codes
        'FAC_105': {'beds': 65,  'transfer_rate': 0.10},
    }

    fac_ids = np.random.choice(list(facilities.keys()), size=num_records)
    patient_ids = [f"PAT_{i:05d}" for i in range(1, num_records + 1)]
    
    admit_offsets = np.random.randint(0, 30, size=num_records)
    admission_dates = [base_date + timedelta(days=int(o)) for o in admit_offsets]
    
    los_days = np.random.randint(1, 14, size=num_records)
    discharge_dates = [admit + timedelta(days=int(l)) for admit, l in zip(admission_dates, los_days)]

    is_transfer = [int(np.random.random() < facilities[fac]['transfer_rate']) for fac in fac_ids]
    daily_mme = np.random.choice([15.0, 30.0, 45.0, 60.0, 110.0, 140.0], size=num_records, p=[0.4, 0.3, 0.15, 0.08, 0.04, 0.03])
    clinician_override = [bool(mme > 90 and np.random.random() < 0.3) for mme in daily_mme]
    days_to_readmit = np.random.choice([12, 24, 29, -2, 400], size=num_records, p=[0.4, 0.3, 0.2, 0.05, 0.05])
    payers = np.random.choice(['MEDICARE', 'MEDICAID', 'COMMERCIAL', 'UNMAPPED', 'UNKNOWN'], size=num_records, p=[0.5, 0.3, 0.15, 0.03, 0.02])

    df = pd.DataFrame({
        'encounter_id': [f"ENC_{i:06d}" for i in range(1, num_records + 1)],
        'patient_id': patient_ids,
        'facility_id': fac_ids,
        'active_beds': [facilities[f]['beds'] for f in fac_ids],
        'admission_date': admission_dates,
        'discharge_date': discharge_dates,
        'is_hospital_transfer': is_transfer,
        'daily_mme': daily_mme,
        'clinician_override': clinician_override,
        'days_to_readmit': days_to_readmit,
        'payer_type': payers
    })

    # Injected temporal logic anomaly
    df.loc[12, 'discharge_date'] = df.loc[12, 'admission_date'] - timedelta(days=2)
    df.loc[45, 'discharge_date'] = df.loc[45, 'admission_date'] - timedelta(days=5)

    return df

if __name__ == "__main__":
    df = generate_synthetic_ehr_data()
    print(f"✅ Dataset generated with {len(df)} records.")
    print(df.head(3))