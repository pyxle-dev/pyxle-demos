import React, { useState, useEffect } from 'react';
import { Link, ClientOnly } from 'pyxle/client';

/* ════════════════════════════════════════════════════════════════
   PULSE — the design system. A status page lives and dies by its
   colour vocabulary, so that's the heart of it: one map from a
   status string to a consistent dot + text + surface tint.
   ════════════════════════════════════════════════════════════════ */

// service status → tailwind colour family
export const STATUS_COLOR = {
    operational: { dot: 'text-emerald-400', text: 'text-emerald-400', chip: 'bg-emerald-500/10 text-emerald-300 ring-emerald-500/20', bar: 'bg-emerald-500' },
    degraded:    { dot: 'text-amber-400',   text: 'text-amber-400',   chip: 'bg-amber-500/10 text-amber-300 ring-amber-500/20',     bar: 'bg-amber-500' },
    partial:     { dot: 'text-orange-400',  text: 'text-orange-400',  chip: 'bg-orange-500/10 text-orange-300 ring-orange-500/20',   bar: 'bg-orange-500' },
    major:       { dot: 'text-red-400',     text: 'text-red-400',     chip: 'bg-red-500/10 text-red-300 ring-red-500/20',           bar: 'bg-red-500' },
    maintenance: { dot: 'text-sky-400',     text: 'text-sky-400',     chip: 'bg-sky-500/10 text-sky-300 ring-sky-500/20',           bar: 'bg-sky-500' },
};

// incident severity → colour family
export const SEVERITY_COLOR = {
    minor:       'bg-amber-500/10 text-amber-300 ring-amber-500/20',
    major:       'bg-orange-500/10 text-orange-300 ring-orange-500/20',
    critical:    'bg-red-500/10 text-red-300 ring-red-500/20',
    maintenance: 'bg-sky-500/10 text-sky-300 ring-sky-500/20',
};

export const INCIDENT_STATUS_LABEL = {
    investigating: 'Investigating',
    identified: 'Identified',
    monitoring: 'Monitoring',
    resolved: 'Resolved',
    maintenance: 'Maintenance',
};

function colorFor(status) {
    return STATUS_COLOR[status] || STATUS_COLOR.operational;
}

/* A live heartbeat dot — solid core, expanding ring (CSS-only). */
export function LivePulse({ status = 'operational', className = '' }) {
    const c = colorFor(status);
    return <span className={`pulse-dot ${c.dot} ${className}`} aria-hidden="true" />;
}

/* Static status dot (no animation) for dense lists. */
export function Dot({ status, className = '' }) {
    const c = colorFor(status);
    return <span className={`inline-block h-2.5 w-2.5 rounded-full ${c.dot.replace('text-', 'bg-')} ${className}`} aria-hidden="true" />;
}

export function StatusChip({ status, label }) {
    const c = colorFor(status);
    return (
        <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ${c.chip}`}>
            <span className={`inline-block h-1.5 w-1.5 rounded-full ${c.dot.replace('text-', 'bg-')}`} />
            {label || status}
        </span>
    );
}

export function SeverityChip({ severity }) {
    return (
        <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ring-1 ${SEVERITY_COLOR[severity] || SEVERITY_COLOR.minor}`}>
            {severity}
        </span>
    );
}

/* 90-day uptime bars. Hovering a bar reveals its day + status. */
export function UptimeBars({ days = [], uptime90 }) {
    return (
        <div>
            <div className="flex items-center gap-[2px]" role="img" aria-label={`90-day uptime ${uptime90}%`}>
                {days.map((d) => {
                    const c = colorFor(d.status);
                    return (
                        <span
                            key={d.day}
                            title={`${d.day} · ${d.status} · ${d.uptime}%`}
                            className={`h-7 flex-1 rounded-[2px] ${c.bar} ${d.status === 'operational' ? 'opacity-70 hover:opacity-100' : 'opacity-95'} transition-opacity`}
                        />
                    );
                })}
            </div>
            <div className="mt-1.5 flex items-center justify-between font-mono text-[10px] uppercase tracking-wider text-zinc-600">
                <span>90 days ago</span>
                <span className="text-zinc-500">{uptime90}% uptime</span>
                <span>today</span>
            </div>
        </div>
    );
}

/* Card surface — the panel everything sits on. */
export function Card({ children, className = '', as: As = 'div' }) {
    return (
        <As className={`rounded-2xl border border-white/[0.06] bg-panel/70 ${className}`}>
            {children}
        </As>
    );
}

export function MonoLabel({ children, className = '' }) {
    return (
        <p className={`font-mono text-[11px] uppercase tracking-[0.18em] text-zinc-500 ${className}`}>
            {children}
        </p>
    );
}

/* Hydration-safe relative time: the server prints an absolute UTC
   timestamp; the client upgrades it to "2m ago" and keeps it live. */
function ago(iso) {
    const then = Date.parse(iso.replace(' ', 'T') + (iso.endsWith('Z') ? '' : 'Z'));
    if (Number.isNaN(then)) return iso;
    const secs = Math.max(0, Math.floor((Date.now() - then) / 1000));
    if (secs < 45) return 'just now';
    if (secs < 90) return '1 min ago';
    if (secs < 3600) return `${Math.floor(secs / 60)} min ago`;
    if (secs < 7200) return '1 hour ago';
    if (secs < 86400) return `${Math.floor(secs / 3600)} hours ago`;
    if (secs < 172800) return 'yesterday';
    return `${Math.floor(secs / 86400)} days ago`;
}

function LiveAgo({ iso }) {
    const [, tick] = useState(0);
    useEffect(() => {
        const t = setInterval(() => tick((n) => n + 1), 20000);
        return () => clearInterval(t);
    }, []);
    return <time dateTime={iso} title={iso + ' UTC'}>{ago(iso)}</time>;
}

export function RelativeTime({ iso, className = '' }) {
    const absolute = (iso || '').slice(0, 16) + ' UTC';
    return (
        <span className={className}>
            <ClientOnly fallback={<time dateTime={iso}>{absolute}</time>}>
                <LiveAgo iso={iso} />
            </ClientOnly>
        </span>
    );
}

/* The Pulse wordmark — a heartbeat glyph that draws a beat. */
export function Brand({ size = 26 }) {
    return (
        <Link href="/" className="focus-ring inline-flex items-center gap-2 rounded">
            <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true">
                <rect x="1.5" y="1.5" width="29" height="29" rx="8" stroke="url(#pg)" strokeWidth="1.5" />
                <path d="M5 16h4l2.5-7 4 14 3-9 2 2h6.5" stroke="url(#pg)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <defs>
                    <linearGradient id="pg" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                        <stop stopColor="#22d3ee" />
                        <stop offset="1" stopColor="#3b82f6" />
                    </linearGradient>
                </defs>
            </svg>
            <span className="text-[15px] font-semibold tracking-tight text-white">Pulse</span>
        </Link>
    );
}

/* A small feature tag that labels which Pyxle capability a surface
   demonstrates — turns the product into a reference without noise. */
export function FeatureTag({ children }) {
    return (
        <span className="inline-flex items-center gap-1 rounded-md bg-signal-400/[0.08] px-2 py-0.5 font-mono text-[10px] font-medium text-signal-400 ring-1 ring-signal-400/15">
            {children}
        </span>
    );
}
