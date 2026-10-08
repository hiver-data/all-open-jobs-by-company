"""Every open job for a list of companies to one CSV, via the hiver/all-open-jobs-by-company Actor on Apify.

    pip install -r requirements.txt
    export APIFY_TOKEN=...   # Apify Console > Settings > API & Integrations
    python jobs_to_csv.py stripe.com ramp.com Spotify --title engineer --max-jobs 300

Companies can be names ("Spotify") or websites ("stripe.com"). Websites match more reliably.
"""
import argparse
import csv
import os
import sys
from decimal import Decimal

from apify_client import ApifyClient

ACTOR = "hiver/all-open-jobs-by-company"
COLUMNS = [
    "company", "source", "title", "location", "workplaceType", "isRemote", "department", "employmentType",
    "postedAt", "salaryMin", "salaryMax", "salaryCurrency", "salaryInterval", "url", "applyUrl", "inputCompany",
]


def main() -> None:
    p = argparse.ArgumentParser(description="All open jobs at these companies, from their own career sites, to CSV.")
    p.add_argument("companies", nargs="+", help="company names or websites, e.g. stripe.com Spotify")
    p.add_argument("--title", nargs="+", help="keep jobs whose title contains one of these words")
    p.add_argument("--location", nargs="+", help="keep jobs whose location contains one of these words")
    p.add_argument("--remote", action="store_true", help="only jobs the company marks as remote")
    p.add_argument("--posted-within", type=int, help="only jobs posted in the last N days")
    p.add_argument("--max-jobs", type=int, default=500, help="hard cap on jobs delivered and charged (default 500)")
    p.add_argument("--max-charge", type=Decimal, default=Decimal("1.00"),
                   help="stop the run once it has cost this many USD (default 1.00)")
    p.add_argument("--out", default="jobs.csv")
    args = p.parse_args()

    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN (Apify Console > Settings > API & Integrations).")

    run_input = {"companies": args.companies, "maxJobs": args.max_jobs, "includeDescription": False}
    if args.title:
        run_input["titleKeywords"] = args.title
    if args.location:
        run_input["locations"] = args.location
    if args.remote:
        run_input["remoteOnly"] = True
    if args.posted_within:
        run_input["postedWithinDays"] = args.posted_within

    # APIFY_API_BASE_URL is only for testing against a mock server; leave it unset.
    client = ApifyClient(token, api_url=os.environ.get("APIFY_API_BASE_URL", "https://api.apify.com"))
    run = client.actor(ACTOR).call(run_input=run_input, max_total_charge_usd=args.max_charge)
    if run is None or run.status != "SUCCEEDED":
        sys.exit(f"Run did not succeed: {run.status if run else 'not started'} {run.status_message if run else ''}")

    rows = 0
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for job in client.dataset(run.default_dataset_id).iterate_items():
            writer.writerow({k: str(v).lower() if isinstance(v, bool) else v for k, v in job.items()})
            rows += 1
    print(f"{rows} jobs -> {args.out}")

    # Which career board each company matched, with the evidence; unmatched companies cost nothing.
    record = client.key_value_store(run.default_key_value_store_id).get_record("COMPANY_MATCHES")
    for company, match in ((record or {}).get("value") or {}).items():
        if match.get("status") == "matched":
            print(f"  {company}: {', '.join(match.get('boards', []))} ({match.get('evidence', '')})")
        else:
            print(f"  {company}: not matched ({match.get('reason', '')})")


if __name__ == "__main__":
    main()
