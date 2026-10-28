from src.generate_data import generate_synthetic_ehr_data
from src.assertions import ReadmissionSanityChecker
from rich.console import Console
from rich.table import Table

def main():
    console = Console()
    
    console.print("\n[bold cyan]================================================================================[/bold cyan]")
    console.print("[bold yellow]               CLINICAL DATA SANITY CHECKER — PIPELINE AUDIT REPORT             [/bold yellow]")
    console.print("[bold cyan]================================================================================[/bold cyan]\n")

    # 1. Load Synthetic EHR Data
    df = generate_synthetic_ehr_data()
    
    # 2. Run Sanity Checks
    checker = ReadmissionSanityChecker(df)
    results = checker.run_all()

    # 3. Print Results Summary
    total_checks = 5
    critical_count = len(results[results['severity'] == 'CRITICAL'])
    
    console.print(f"Total Encounters Checked : [bold white]{len(df)}[/bold white]")
    console.print(f"Total Facilities Audited : [bold white]{df['facility_id'].nunique()}[/bold white]")
    console.print(f"Total Issues Flagged     : [bold red]{len(results)}[/bold red]")
    console.print(f"Critical Anomalies       : [bold red]{critical_count} (Pipeline Blocking)[/bold red]\n")

    # 4. Render Table of Flagged Issues
    table = Table(title="Data Quality Assertion Failures", show_header=True, header_style="bold magenta")
    table.add_column("Rule ID", style="cyan", width=10)
    table.add_column("Severity", style="bold red", width=10)
    table.add_column("Category", style="yellow", width=25)
    table.add_column("Facility", style="white", width=10)
    table.add_column("Message", style="green")

    for _, row in results.head(10).iterrows():
        table.add_row(
            row['rule_id'],
            row['severity'],
            row['category'],
            row['facility_id'],
            row['message']
        )

    console.print(table)
    
    if critical_count > 0:
        console.print("\n[bold red]❌ PRE-FLIGHT VALIDATION FAILED: Executive pipeline execution blocked.[/bold red]\n")

if __name__ == "__main__":
    main()