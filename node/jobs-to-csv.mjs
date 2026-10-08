// Every open job for a list of companies to one CSV, via the hiver/all-open-jobs-by-company Actor on Apify.
//
//   npm install
//   export APIFY_TOKEN=...   # Apify Console > Settings > API & Integrations
//   node jobs-to-csv.mjs stripe.com ramp.com Spotify --title engineer --max-jobs 300
//
// Companies can be names ("Spotify") or websites ("stripe.com"). Websites match more reliably.
import { writeFileSync } from 'node:fs';
import { parseArgs } from 'node:util';
import { ApifyClient } from 'apify-client';

const ACTOR = 'hiver/all-open-jobs-by-company';
const COLUMNS = ['company', 'source', 'title', 'location', 'workplaceType', 'isRemote', 'department', 'employmentType',
    'postedAt', 'salaryMin', 'salaryMax', 'salaryCurrency', 'salaryInterval', 'url', 'applyUrl', 'inputCompany'];

const { values: opt, positionals: companies } = parseArgs({
    allowPositionals: true,
    options: {
        title: { type: 'string' }, // comma-separated title words, e.g. engineer,designer
        location: { type: 'string' }, // comma-separated, e.g. London,Remote
        remote: { type: 'boolean', default: false },
        'posted-within': { type: 'string' }, // days
        'max-jobs': { type: 'string', default: '500' }, // hard cap on jobs delivered and charged
        'max-charge': { type: 'string', default: '1.00' }, // stop the run once it has cost this many USD
        out: { type: 'string', default: 'jobs.csv' },
    },
});
if (!companies.length) throw new Error('Give at least one company name or website, e.g. stripe.com Spotify');
if (!process.env.APIFY_TOKEN) throw new Error('Set APIFY_TOKEN (Apify Console > Settings > API & Integrations).');

const input = {
    companies,
    maxJobs: Number(opt['max-jobs']),
    includeDescription: false,
    ...(opt.title && { titleKeywords: opt.title.split(',') }),
    ...(opt.location && { locations: opt.location.split(',') }),
    ...(opt.remote && { remoteOnly: true }),
    ...(opt['posted-within'] && { postedWithinDays: Number(opt['posted-within']) }),
};

// APIFY_API_BASE_URL is only for testing against a mock server; leave it unset.
const client = new ApifyClient({ token: process.env.APIFY_TOKEN, baseUrl: process.env.APIFY_API_BASE_URL });
const run = await client.actor(ACTOR).call(input, { maxTotalChargeUsd: Number(opt['max-charge']) });
if (run.status !== 'SUCCEEDED') throw new Error(`Run did not succeed: ${run.status} ${run.statusMessage ?? ''}`);

const { items } = await client.dataset(run.defaultDatasetId).listItems();
const cell = (v) => {
    const s = v === null || v === undefined ? '' : String(v);
    return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
const lines = [COLUMNS.join(','), ...items.map((j) => COLUMNS.map((c) => cell(j[c])).join(','))];
writeFileSync(opt.out, `${lines.join('\r\n')}\r\n`);
console.log(`${items.length} jobs -> ${opt.out}`);

// Which career board each company matched, with the evidence; unmatched companies cost nothing.
const record = await client.keyValueStore(run.defaultKeyValueStoreId).getRecord('COMPANY_MATCHES');
for (const [company, m] of Object.entries(record?.value ?? {})) {
    console.log(m.status === 'matched'
        ? `  ${company}: ${(m.boards ?? []).join(', ')} (${m.evidence ?? ''})`
        : `  ${company}: not matched (${m.reason ?? ''})`);
}
