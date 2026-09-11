import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database.connection import SessionLocal, init_database
from backend.app.database.models import Company, FinancialFact, FinancialConcept


COMPANIES_DATA = [
    {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "industry": "Consumer Electronics",
        "sector": "Technology",
        "country": "USA",
    },
    {
        "ticker": "MSFT",
        "company_name": "Microsoft Corporation",
        "industry": "Software—Infrastructure",
        "sector": "Technology",
        "country": "USA",
    },
    {
        "ticker": "AMZN",
        "company_name": "Amazon.com, Inc.",
        "industry": "Internet Retail",
        "sector": "Consumer Cyclical",
        "country": "USA",
    },
    {
        "ticker": "GOOGL",
        "company_name": "Alphabet Inc.",
        "industry": "Internet Content & Information",
        "sector": "Communication Services",
        "country": "USA",
    },
    {
        "ticker": "TSLA",
        "company_name": "Tesla, Inc.",
        "industry": "Auto Manufacturers",
        "sector": "Consumer Cyclical",
        "country": "USA",
    },
    {
        "ticker": "NVDA",
        "company_name": "Nvidia Corporation",
        "industry": "Semiconductors",
        "sector": "Technology",
        "country": "USA",
    },
    {
        "ticker": "META",
        "company_name": "Meta Platforms, Inc.",
        "industry": "Internet Content & Information",
        "sector": "Communication Services",
        "country": "USA",
    },
]

CONCEPTS_DATA = [
    {
        "concept": "Revenue",
        "description": "Total sales revenue recognized from contracts with customers during the period.",
        "category": "IncomeStatement",
        "synonyms": ["Sales", "Turnover", "Total Revenue", "Net Sales", "Top Line"],
        "unit": "USD",
    },
    {
        "concept": "CostOfRevenue",
        "description": "Direct costs incurred in producing goods or rendering services.",
        "category": "IncomeStatement",
        "synonyms": ["COGS", "Cost of Goods Sold", "Cost of Sales"],
        "unit": "USD",
    },
    {
        "concept": "GrossProfit",
        "description": "Revenue minus cost of revenue.",
        "category": "IncomeStatement",
        "synonyms": ["Gross Margin", "Gross Income"],
        "unit": "USD",
    },
    {
        "concept": "OperatingExpenses",
        "description": "Costs associated with maintenance and administrative activities (R&D, SG&A).",
        "category": "IncomeStatement",
        "synonyms": ["OPEX", "Operating Costs"],
        "unit": "USD",
    },
    {
        "concept": "OperatingIncome",
        "description": "Profit realized from normal business operations before interest and tax.",
        "category": "IncomeStatement",
        "synonyms": ["Operating Profit", "EBIT", "Operating Earnings"],
        "unit": "USD",
    },
    {
        "concept": "NetIncome",
        "description": "Total earnings or profit of a company after deducting all expenses, interest, and taxes.",
        "category": "IncomeStatement",
        "synonyms": ["Net Profit", "Net Earnings", "Profit After Tax", "Bottom Line"],
        "unit": "USD",
    },
    {
        "concept": "EarningsPerShare",
        "description": "Diluted earnings per share allocated to each outstanding common share.",
        "category": "Ratios",
        "synonyms": ["EPS", "Diluted EPS", "Earnings per Share Diluted"],
        "unit": "per-share",
    },
    {
        "concept": "CashAndCashEquivalents",
        "description": "Currency, bank accounts, and short-term liquid investments readily convertible to cash.",
        "category": "BalanceSheet",
        "synonyms": ["Cash", "Cash & Equivalents", "Liquid Reserves", "Cash and Equivalents"],
        "unit": "USD",
    },
    {
        "concept": "TotalAssets",
        "description": "Total economic resources owned and controlled by the corporation.",
        "category": "BalanceSheet",
        "synonyms": ["Assets", "Total Asset Base"],
        "unit": "USD",
    },
    {
        "concept": "TotalLiabilities",
        "description": "Aggregate financial debts and settlement obligations owed to external parties.",
        "category": "BalanceSheet",
        "synonyms": ["Liabilities", "Total Debt & Obligations"],
        "unit": "USD",
    },
    {
        "concept": "Equity",
        "description": "Stockholders' equity representing the residual interest in the corporate assets.",
        "category": "BalanceSheet",
        "synonyms": ["Stockholders Equity", "Shareholders Equity", "Net Worth"],
        "unit": "USD",
    },
]

# Historical financial figures calibrated to actual 10-K filings (values in USD)
# For FY 2020 - 2025 across companies
COMPANY_ANNUAL_DATA = {
    "AAPL": {
        # Apple fiscal year ends last Saturday of September
        "periods": {
            2020: {"start": date(2019, 9, 29), "end": date(2020, 9, 26), "filing": date(2020, 10, 30)},
            2021: {"start": date(2020, 9, 27), "end": date(2021, 9, 25), "filing": date(2021, 10, 29)},
            2022: {"start": date(2021, 9, 26), "end": date(2022, 9, 24), "filing": date(2022, 10, 28)},
            2023: {"start": date(2022, 9, 25), "end": date(2023, 9, 30), "filing": date(2023, 11, 3)},
            2024: {"start": date(2023, 10, 1), "end": date(2024, 9, 28), "filing": date(2024, 11, 1)},
            2025: {"start": date(2024, 9, 29), "end": date(2025, 9, 27), "filing": date(2025, 11, 2)},
        },
        "metrics": {
            "Revenue": [274515000000, 365817000000, 394328000000, 383285000000, 391035000000, 412000000000],
            "GrossProfit": [104956000000, 152836000000, 170782000000, 169148000000, 180683000000, 192500000000],
            "OperatingIncome": [66288000000, 108949000000, 119437000000, 114301000000, 123216000000, 131800000000],
            "NetIncome": [57411000000, 94680000000, 99803000000, 96995000000, 93736000000, 104500000000],
            "EarningsPerShare": [3.28, 5.61, 6.11, 6.13, 6.08, 6.85],
            "TotalAssets": [323888000000, 351002000000, 352755000000, 352583000000, 364980000000, 378000000000],
            "TotalLiabilities": [258549000000, 287912000000, 302083000000, 290437000000, 308030000000, 312000000000],
            "CashAndCashEquivalents": [38016000000, 34940000000, 23646000000, 29965000000, 29943000000, 32000000000],
            "OperatingExpenses": [38668000000, 43887000000, 51345000000, 54847000000, 57467000000, 60700000000],
        }
    },
    "MSFT": {
        # Microsoft fiscal year ends June 30
        "periods": {
            2020: {"start": date(2019, 7, 1), "end": date(2020, 6, 30), "filing": date(2020, 7, 31)},
            2021: {"start": date(2020, 7, 1), "end": date(2021, 6, 30), "filing": date(2021, 7, 30)},
            2022: {"start": date(2021, 7, 1), "end": date(2022, 6, 30), "filing": date(2022, 7, 28)},
            2023: {"start": date(2022, 7, 1), "end": date(2023, 6, 30), "filing": date(2023, 7, 27)},
            2024: {"start": date(2023, 7, 1), "end": date(2024, 6, 30), "filing": date(2024, 7, 31)},
            2025: {"start": date(2024, 7, 1), "end": date(2025, 6, 30), "filing": date(2025, 7, 30)},
        },
        "metrics": {
            "Revenue": [143015000000, 168088000000, 198270000000, 211915000000, 245122000000, 281000000000],
            "GrossProfit": [96937000000, 115856000000, 135620000000, 146052000000, 170724000000, 196000000000],
            "OperatingIncome": [52959000000, 69916000000, 83383000000, 88523000000, 109433000000, 126000000000],
            "NetIncome": [44281000000, 61271000000, 72738000000, 72361000000, 88136000000, 101000000000],
            "EarningsPerShare": [5.76, 8.05, 9.65, 9.68, 11.80, 13.50],
            "TotalAssets": [301311000000, 333779000000, 364840000000, 411976000000, 512163000000, 560000000000],
            "TotalLiabilities": [183007000000, 191791000000, 198298000000, 205753000000, 243686000000, 260000000000],
            "CashAndCashEquivalents": [13576000000, 14224000000, 13931000000, 34704000000, 18300000000, 24000000000],
            "OperatingExpenses": [43978000000, 45940000000, 52237000000, 57529000000, 61291000000, 70000000000],
        }
    },
    "AMZN": {
        "periods": {
            y: {"start": date(y, 1, 1), "end": date(y, 12, 31), "filing": date(y + 1, 2, 2)}
            for y in range(2020, 2026)
        },
        "metrics": {
            "Revenue": [386064000000, 469822000000, 513983000000, 574785000000, 637965000000, 715000000000],
            "GrossProfit": [152757000000, 197478000000, 225152000000, 270046000000, 307300000000, 350000000000],
            "OperatingIncome": [22899000000, 24879000000, 12248000000, 36852000000, 60600000000, 78000000000],
            "NetIncome": [21331000000, 33364000000, -2722000000, 30425000000, 59248000000, 72000000000],
            "EarningsPerShare": [2.09, 3.24, -0.27, 2.90, 5.53, 6.75],
            "TotalAssets": [321195000000, 420549000000, 462675000000, 527854000000, 609800000000, 680000000000],
            "TotalLiabilities": [227791000000, 282304000000, 316632000000, 326100000000, 342000000000, 370000000000],
            "CashAndCashEquivalents": [42122000000, 36224000000, 35438000000, 73387000000, 86780000000, 95000000000],
            "OperatingExpenses": [129858000000, 172599000000, 212904000000, 233194000000, 246700000000, 272000000000],
        }
    },
    "GOOGL": {
        "periods": {
            y: {"start": date(y, 1, 1), "end": date(y, 12, 31), "filing": date(y + 1, 2, 4)}
            for y in range(2020, 2026)
        },
        "metrics": {
            "Revenue": [182527000000, 257637000000, 282836000000, 307394000000, 350018000000, 402000000000],
            "GrossProfit": [97795000000, 146698000000, 156633000000, 174316000000, 201200000000, 235000000000],
            "OperatingIncome": [41224000000, 78714000000, 74842000000, 84293000000, 111382000000, 132000000000],
            "NetIncome": [40269000000, 76033000000, 59972000000, 73795000000, 94297000000, 112000000000],
            "EarningsPerShare": [2.93, 5.61, 4.56, 5.80, 7.54, 8.95],
            "TotalAssets": [319616000000, 359268000000, 365264000000, 402392000000, 450100000000, 510000000000],
            "TotalLiabilities": [97072000000, 107633000000, 109122000000, 119041000000, 128500000000, 140000000000],
            "CashAndCashEquivalents": [26465000000, 20945000000, 21879000000, 24048000000, 25200000000, 30000000000],
            "OperatingExpenses": [56571000000, 67984000000, 81791000000, 90023000000, 89818000000, 103000000000],
        }
    },
    "TSLA": {
        "periods": {
            y: {"start": date(y, 1, 1), "end": date(y, 12, 31), "filing": date(y + 1, 1, 28)}
            for y in range(2020, 2026)
        },
        "metrics": {
            "Revenue": [31536000000, 53823000000, 81462000000, 96773000000, 97690000000, 115000000000],
            "GrossProfit": [6630000000, 13606000000, 20853000000, 17660000000, 17890000000, 22000000000],
            "OperatingIncome": [1994000000, 6523000000, 13656000000, 8891000000, 7420000000, 11000000000],
            "NetIncome": [721000000, 5519000000, 12583000000, 14997000000, 7090000000, 10500000000],
            "EarningsPerShare": [0.24, 1.87, 4.02, 4.30, 2.04, 3.05],
            "TotalAssets": [52148000000, 62131000000, 82338000000, 106618000000, 121000000000, 140000000000],
            "TotalLiabilities": [28469000000, 30548000000, 36440000000, 43009000000, 45200000000, 50000000000],
            "CashAndCashEquivalents": [19384000000, 17576000000, 16253000000, 29094000000, 33600000000, 38000000000],
            "OperatingExpenses": [4636000000, 7083000000, 7197000000, 8769000000, 10470000000, 11000000000],
        }
    },
    "NVDA": {
        # Nvidia fiscal year ends late January (e.g. FY2024 ended Jan 2024)
        "periods": {
            2020: {"start": date(2019, 1, 28), "end": date(2020, 1, 26), "filing": date(2020, 2, 20)},
            2021: {"start": date(2020, 1, 27), "end": date(2021, 1, 31), "filing": date(2021, 2, 26)},
            2022: {"start": date(2021, 2, 1), "end": date(2022, 1, 30), "filing": date(2022, 3, 18)},
            2023: {"start": date(2022, 1, 31), "end": date(2023, 1, 29), "filing": date(2023, 2, 24)},
            2024: {"start": date(2023, 1, 30), "end": date(2024, 1, 28), "filing": date(2024, 2, 21)},
            2025: {"start": date(2024, 1, 29), "end": date(2025, 1, 26), "filing": date(2025, 2, 26)},
        },
        "metrics": {
            "Revenue": [10918000000, 16675000000, 26914000000, 26974000000, 60922000000, 130500000000],
            "GrossProfit": [6768000000, 10400000000, 17475000000, 15356000000, 44301000000, 98000000000],
            "OperatingIncome": [2846000000, 4532000000, 10041000000, 4224000000, 32972000000, 81000000000],
            "NetIncome": [2796000000, 4332000000, 9752000000, 4368000000, 29760000000, 71000000000],
            "EarningsPerShare": [1.13, 1.73, 3.85, 1.74, 11.93, 28.50],
            "TotalAssets": [17315000000, 28791000000, 44187000000, 41182000000, 65728000000, 112000000000],
            "TotalLiabilities": [5112000000, 11893000000, 17575000000, 19081000000, 22750000000, 32000000000],
            "CashAndCashEquivalents": [10896000000, 11561000000, 1990000000, 3389000000, 7280000000, 14000000000],
            "OperatingExpenses": [3922000000, 5868000000, 7434000000, 11132000000, 11329000000, 17000000000],
        }
    },
    "META": {
        "periods": {
            y: {"start": date(y, 1, 1), "end": date(y, 12, 31), "filing": date(y + 1, 2, 2)}
            for y in range(2020, 2026)
        },
        "metrics": {
            "Revenue": [85965000000, 117929000000, 116609000000, 134902000000, 164500000000, 192000000000],
            "GrossProfit": [69273000000, 95280000000, 92113000000, 108943000000, 134000000000, 158000000000],
            "OperatingIncome": [34203000000, 46753000000, 28944000000, 46751000000, 69400000000, 82000000000],
            "NetIncome": [29146000000, 39370000000, 23200000000, 39098000000, 62400000000, 74000000000],
            "EarningsPerShare": [3.88, 5.16, 3.00, 5.19, 8.25, 9.80],
            "TotalAssets": [159316000000, 165987000000, 185727000000, 229623000000, 271000000000, 315000000000],
            "TotalLiabilities": [31026000000, 41108000000, 59956000000, 76449000000, 86000000000, 98000000000],
            "CashAndCashEquivalents": [17576000000, 16601000000, 14681000000, 31809000000, 34500000000, 42000000000],
            "OperatingExpenses": [35070000000, 48527000000, 63169000000, 62192000000, 64600000000, 76000000000],
        }
    },
}

YEARS = [2020, 2021, 2022, 2023, 2024, 2025]


def seed_database():
    init_database()
    db = SessionLocal()

    try:
        # Clear existing seed facts
        db.query(FinancialFact).delete()
        db.query(FinancialConcept).delete()
        db.query(Company).delete()
        db.commit()

        print("Seeding companies...")
        company_map = {}
        for c in COMPANIES_DATA:
            comp = Company(**c)
            db.add(comp)
            db.flush()
            company_map[c["ticker"]] = comp.company_id

        print("Seeding financial concepts...")
        for c in CONCEPTS_DATA:
            conc = FinancialConcept(**c)
            db.add(conc)
        db.flush()

        print("Seeding financial facts (2020-2025)...")
        facts = []
        for ticker, data in COMPANY_ANNUAL_DATA.items():
            cid = company_map[ticker]
            periods = data["periods"]
            metrics = data["metrics"]

            for year_idx, year in enumerate(YEARS):
                p_info = periods[year]
                for concept_name, values in metrics.items():
                    val = values[year_idx]
                    unit = "per-share" if concept_name == "EarningsPerShare" else "USD"
                    
                    fact = FinancialFact(
                        company_id=cid,
                        concept=concept_name,
                        concept_description=f"{concept_name} for {ticker} in FY{year}",
                        value=val,
                        unit=unit,
                        period_start=p_info["start"],
                        period_end=p_info["end"],
                        filing_date=p_info["filing"],
                        fiscal_year=year,
                        fiscal_period="FY",
                        form="10-K",
                        statement_type="IncomeStatement" if concept_name in ["Revenue", "GrossProfit", "OperatingIncome", "NetIncome", "OperatingExpenses", "CostOfRevenue"] else "BalanceSheet",
                        reporting_type="consolidated",
                        is_restated=False,
                        source="SEC EDGAR 10-K (Calibrated Demo)"
                    )
                    facts.append(fact)

        # Add realistic historical restated values for edge case testing (Apple and Microsoft)
        # e.g., Apple's FY2022 revenue was slightly adjusted in FY2023 comparative 10-K
        apple_id = company_map["AAPL"]
        facts.append(FinancialFact(
            company_id=apple_id,
            concept="Revenue",
            concept_description="Restated Revenue for AAPL in FY2022 due to accounting reclassification",
            value=394328000000,
            unit="USD",
            period_start=date(2021, 9, 26),
            period_end=date(2022, 9, 24),
            filing_date=date(2023, 11, 3),
            fiscal_year=2022,
            fiscal_period="FY",
            form="10-K",
            statement_type="IncomeStatement",
            reporting_type="consolidated",
            is_restated=True,
            source="SEC EDGAR 10-K / Restated"
        ))

        # Add a standalone (unconsolidated) fact for testing consolidated vs standalone handling
        facts.append(FinancialFact(
            company_id=apple_id,
            concept="Revenue",
            concept_description="Standalone parent entity revenue for AAPL in FY2023",
            value=298000000000,
            unit="USD",
            period_start=date(2022, 9, 25),
            period_end=date(2023, 9, 30),
            filing_date=date(2023, 11, 3),
            fiscal_year=2023,
            fiscal_period="FY",
            form="10-K",
            statement_type="IncomeStatement",
            reporting_type="standalone",
            is_restated=False,
            source="Internal Parent Company Ledger"
        ))

        db.add_all(facts)
        db.commit()
        print(f"Successfully seeded {len(COMPANIES_DATA)} companies, {len(CONCEPTS_DATA)} concepts, and {len(facts)} financial facts.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
