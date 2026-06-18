import React from 'react';
import { Card, MonoLabel, FeatureTag, SeverityChip, INCIDENT_STATUS_LABEL } from '../components/ui.jsx';

/*
 * _ImpactPanel — incident analytics derived entirely from the incident's own
 * update history: total duration, update count, responders, the status
 * progression, and a cadence sparkline. Everything is computed deterministically
 * (no Date.now() in render), so the server-rendered markup and the client
 * hydration always agree.
 *
 * It also demonstrates *streaming SSR*: it deliberately stalls ~2.5s on the
 * server (stallOnServer below), wrapped in a <Suspense> boundary on the page —
 * the shell streams first, this panel streams in when it resolves.
 */

/* A deliberate server-side stall so the streaming is *visible*. On the SERVER
   this suspends for ~2.5s: renderToPipeableStream flushes the page shell + the
   <Suspense> fallback immediately, then streams this panel in when the promise
   resolves. On the CLIENT it never stalls — it renders synchronously, so the
   hydrated markup matches the streamed HTML exactly (no mismatch). The cache is
   re-armed after each render so every refresh shows the stream again. */
function stallOnServer(key, ms) {
    if (typeof window !== 'undefined') return; // client: render now, no delay
    const cache = (globalThis.__pulseStreamStall ||= new Map());
    let entry = cache.get(key);
    if (!entry) {
        entry = { done: false };
        entry.promise = new Promise((resolve) => {
            setTimeout(() => { entry.done = true; resolve(); }, ms);
        });
        cache.set(key, entry);
    }
    if (!entry.done) throw entry.promise;
    cache.delete(key); // re-arm for the next request
}

function parse(ts) {
    if (!ts) return NaN;
    return Date.parse(ts.replace(' ', 'T') + (ts.endsWith('Z') ? '' : 'Z'));
}

function humanizeDelta(ms) {
    if (!Number.isFinite(ms) || ms < 0) return '—';
    const mins = Math.round(ms / 60000);
    if (mins < 1) return 'under a minute';
    if (mins < 60) return `${mins} min`;
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    return m ? `${h}h ${m}m` : `${h}h`;
}

function Stat({ label, value, accent }) {
    return (
        <div className="rounded-xl border border-white/[0.06] bg-ink/60 px-4 py-3">
            <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-zinc-600">{label}</p>
            <p className={`mt-1 text-lg font-semibold ${accent || 'text-white'}`}>{value}</p>
        </div>
    );
}

export default function ImpactPanel({ incident }) {
    // Deliberately slow on the server so the streaming is visible (see above).
    stallOnServer(`impact:${incident.slug}`, 2500);

    const updates = Array.isArray(incident.updates) ? incident.updates : [];
    // updates arrive newest-first; walk oldest→newest for the timeline math.
    const chrono = [...updates].sort((a, b) => parse(a.created_at) - parse(b.created_at));
    const opened = parse(incident.created_at);
    const last = chrono.length ? parse(chrono[chrono.length - 1].created_at) : opened;
    const resolved = incident.status === 'resolved';
    const span = (resolved && incident.resolved_at ? parse(incident.resolved_at) : last) - opened;

    const responders = new Set(chrono.map((u) => (u.author || '').split('·')[0].trim()).filter(Boolean));
    const stages = chrono.map((u) => u.status);

    // Cadence sparkline — minutes between consecutive updates.
    const gaps = [];
    for (let i = 1; i < chrono.length; i += 1) {
        gaps.push(Math.max(0, parse(chrono[i].created_at) - parse(chrono[i - 1].created_at)));
    }
    const maxGap = gaps.length ? Math.max(...gaps, 1) : 1;

    return (
        <Card className="p-5">
            <div className="flex flex-wrap items-center gap-2">
                <MonoLabel>Impact summary</MonoLabel>
                <FeatureTag>streamed · &lt;Suspense&gt;</FeatureTag>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
                <Stat label={resolved ? 'Total duration' : 'Open for'} value={humanizeDelta(span)} accent={resolved ? 'text-emerald-400' : 'text-amber-400'} />
                <Stat label="Updates" value={updates.length} />
                <Stat label="Responders" value={responders.size || 1} />
                <Stat label="Severity" value={<SeverityChip severity={incident.severity} />} />
            </div>

            {stages.length > 0 && (
                <div className="mt-5">
                    <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-zinc-600">Progression</p>
                    <div className="mt-2 flex flex-wrap items-center gap-1.5">
                        {stages.map((s, i) => (
                            <React.Fragment key={i}>
                                <span className="rounded-md bg-white/[0.05] px-2 py-0.5 font-mono text-[11px] text-zinc-300">
                                    {INCIDENT_STATUS_LABEL[s] || s}
                                </span>
                                {i < stages.length - 1 && <span className="text-zinc-700">→</span>}
                            </React.Fragment>
                        ))}
                    </div>
                </div>
            )}

            {gaps.length > 0 && (
                <div className="mt-5">
                    <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-zinc-600">Update cadence</p>
                    <div className="mt-2 flex items-end gap-1.5" role="img" aria-label="Time between updates">
                        {gaps.map((g, i) => (
                            <div
                                key={i}
                                title={`${humanizeDelta(g)} between updates`}
                                className="w-full rounded-sm bg-gradient-to-t from-signal-600/50 to-signal-400/80"
                                style={{ height: `${8 + Math.round((g / maxGap) * 40)}px` }}
                            />
                        ))}
                    </div>
                </div>
            )}
        </Card>
    );
}
