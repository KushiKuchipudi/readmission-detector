import pandas as pd
import numpy as np

class ReadmissionSanityChecker:
    """
    Automated data quality assertion framework for post-acute EHR pipelines.
    Designed to catch silent ETL failures and schema drift before executive reporting.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.issues = []

    def check_zero_count_anomalies(self, min_beds: int = 50, window_days: int = 30):
        """RULE_001: Flags facilities with high bed capacity reporting zero transfers."""
        transfers = self.df.groupby('facility_id').agg(
            active_beds=('active_beds', 'max'),
            total_transfers=('is_hospital_transfer', 'sum')
        )
        anomalies = transfers[
            (transfers['active_beds'] > min_beds) & 
            (transfers['total_transfers'] == 0)
        ]
        
        for fac_id in anomalies.index:
            self.issues.append({
                "rule_id": "RULE_001",
                "severity": "CRITICAL",
                "category": "Silent Failure (Mapping Loss)",
                "facility_id": fac_id,
                "message": f"Facility {fac_id} (> {min_beds} beds) reported EXACTLY 0 hospital transfers in {window_days}d window. Unmapped transfer codes suspected."
            })

    def check_date_logic(self):
        """RULE_002: Flags discharge dates preceding admission dates."""
        invalid = self.df[self.df['discharge_date'] < self.df['admission_date']]
        for _, row in invalid.iterrows():
            discharge_str = row['discharge_date'].strftime('%Y-%m-%d') if pd.notnull(row['discharge_date']) else 'NaT'
            admit_str = row['admission_date'].strftime('%Y-%m-%d') if pd.notnull(row['admission_date']) else 'NaT'
            self.issues.append({
                "rule_id": "RULE_002",
                "severity": "HIGH",
                "category": "Temporal Anomaly",
                "facility_id": row['facility_id'],
                "message": f"Patient {row['patient_id']}: Discharge ({discharge_str}) precedes Admission ({admit_str})."
            })

    def check_mme_thresholds(self, threshold: float = 90.0):
        """RULE_003: Flags daily MME exceeding safety limits without override flag."""
        high_mme = self.df[(self.df['daily_mme'] > threshold) & (~self.df['clinician_override'].fillna(False))]
        for _, row in high_mme.iterrows():
            self.issues.append({
                "rule_id": "RULE_003",
                "severity": "HIGH",
                "category": "Clinical Safety",
                "facility_id": row['facility_id'],
                "message": f"Patient {row['patient_id']}: Daily MME ({row['daily_mme']}) exceeds safety limit ({threshold}) without clinician override."
            })

    def check_readmission_bounds(self):
        """RULE_004: Flags invalid readmission calculation boundaries."""
        bounds = self.df[(self.df['days_to_readmit'] <= 0) | (self.df['days_to_readmit'] > 365)]
        for _, row in bounds.iterrows():
            self.issues.append({
                "rule_id": "RULE_004",
                "severity": "MEDIUM",
                "category": "Data Hygiene",
                "facility_id": row['facility_id'],
                "message": f"Patient {row['patient_id']}: Out-of-bounds readmission interval ({row['days_to_readmit']} days)."
            })

    def check_payer_mapping(self):
        """RULE_005: Flags null or unmapped payer records."""
        unmapped = self.df[self.df['payer_type'].isin(['UNKNOWN', 'UNMAPPED', '', None]) | self.df['payer_type'].isna()]
        for _, row in unmapped.iterrows():
            self.issues.append({
                "rule_id": "RULE_005",
                "severity": "LOW",
                "category": "Schema Compliance",
                "facility_id": row['facility_id'],
                "message": f"Patient {row['patient_id']}: Encounter missing valid payer mapping."
            })

    def run_all(self) -> pd.DataFrame:
        self.check_zero_count_anomalies()
        self.check_date_logic()
        self.check_mme_thresholds()
        self.check_readmission_bounds()
        self.check_payer_mapping()
        return pd.DataFrame(self.issues)