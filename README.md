# Every open job for a list of companies, in one CSV

Runnable Python and Node.js examples for [Company Jobs Scraper: All Open Jobs by Company Name or Website](https://apify.com/hiver/all-open-jobs-by-company?utm_source=github&utm_campaign=all-open-jobs-by-company), an Apify Actor built by hiver.

You give it company names (`Spotify`) or websites (`stripe.com`). It finds each company's own career board on one of 17 sources (Workday, Greenhouse, Lever, Ashby, SmartRecruiters, Workable, Recruitee, Oracle Recruiting, Eightfold, Phenom, iCIMS/Jibe, Amazon.jobs, Rippling, Personio, Teamtailor, Breezy HR, and career sites that publish schema.org JobPosting sitemaps) and returns every open job with the same columns: company, source system, title, location, workplace type, department, posting date, salary range where published, job URL and apply URL.

```
company,source,title,location,workplaceType,isRemote,department,employmentType,postedAt,...
Stripe,greenhouse,Abuse Investigator,Dublin,,,8611 Security Analytics,,2026-09-03T17:32:53Z,...
spotify,lever,Android Engineer - Experience,London,hybrid,false,Engineering,Permanent,2026-06-23T11:29:45.805000Z,...
nvidia,workday,Senior Software Engineer - Simulation,"US, CA, Santa Clara",,,,Full time,2026-10-07T00:00:00Z,...
```

## Run it

You need an Apify account (the free plan includes $5 of usage a month) and its API token from Apify Console > Settings > API & Integrations.

Python 3.11+:

```bash
cd python
pip install -r requirements.txt
export APIFY_TOKEN=your_token
python jobs_to_csv.py stripe.com ramp.com Spotify --title engineer --max-jobs 300
```

Node.js 18+:

```bash
cd node
npm install
export APIFY_TOKEN=your_token
node jobs-to-csv.mjs stripe.com ramp.com Spotify --title engineer --max-jobs 300
```

Both write `jobs.csv` and then print which career board each company matched, with the evidence, or why it was not matched. Options: `--title` and `--location` (keep jobs containing one of these words), `--remote`, `--posted-within DAYS`, `--max-jobs` (hard cap on jobs delivered and charged; default 500), `--max-charge` (the run stops once it has cost this many dollars; default $1.00).

No code: open the [Actor page](https://apify.com/hiver/all-open-jobs-by-company?utm_source=github&utm_campaign=all-open-jobs-by-company), paste the companies and download CSV, Excel or JSON.

## Wrong matches are worse than no match

"Tide" is a UK bank and a detergent brand. The Actor matches a company only when the company's own website links to the board, or the board or its job ads name the company. Otherwise it reports the company as unmatched instead of guessing. Every run saves a `COMPANY_MATCHES` record with the board used for each company and the evidence; the scripts print it. A website matches more reliably than a name, and large employers with in-house career sites that have no public job feed may not match at all.

## What it costs

$1.50 per 1,000 jobs on the free plan (less on higher Apify plans), plus Apify's $0.00005 start fee per run. Companies that are not found or have no open jobs cost nothing.

## What we measured

Our test bench (2026-10-07, build 0.2.2) ran this Actor and the three other Apify Store Actors that also take company names or websites on the same six companies: Stripe, Ramp and Spotify in one case, NVIDIA, Salesforce and Airbnb by name only in a second. Every answer was checked against the company's real board, read from that board's public API.

| | This Actor | Best alternative |
|---|---|---|
| Test cases that returned the companies' jobs | 2 of 2 | 1 of 2 |
| Checks passed (job URL on the company's real board, job system named correctly) | 11 of 11 (100%) | 55% |
| Job fields filled | 95% | 86% |
| Price per 1,000 jobs in these runs | $1.51 | $2.01 and $3.01 |

"Best alternative" is the best of the three other Actors on each row. Six companies is a small sample. The bench runs again after every new build.

## Monitoring

Set `onlyNewSinceLastRun: true` in the Actor input and put it on an Apify schedule. The first run delivers every open job; later runs deliver, and charge for, only jobs not delivered before.

## Notes

- Unofficial. Not affiliated with any of the job systems named here or with any company whose jobs you read. The Actor reads only public job-board data that companies publish for job seekers, with no login.
- Something wrong or missing for a company? Open an issue on the Actor's Issues tab on Apify, or here. Each report becomes a test case for the next build.

MIT licensed examples. Built by [hiver](https://apify.com/hiver?utm_source=github&utm_campaign=all-open-jobs-by-company).
