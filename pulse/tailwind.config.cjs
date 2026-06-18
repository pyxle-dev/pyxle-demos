/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'class',
    content: [
        "./pages/**/*.{pyxl,js,jsx,ts,tsx}",
        "./.pyxle-build/client/pages/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
                mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
            },
            colors: {
                // Pulse's signal palette — a cool cyan→blue brand with the
                // severity colors a status page lives by.
                ink: '#08090d',          // page background
                panel: '#0c0e14',        // raised surface
                signal: {
                    400: '#22d3ee',      // cyan — "live"
                    500: '#38bdf8',      // sky
                    600: '#3b82f6',      // blue
                },
            },
            keyframes: {
                pulsering: {
                    '0%':   { transform: 'scale(0.6)', opacity: '0.7' },
                    '100%': { transform: 'scale(2.4)', opacity: '0' },
                },
                streamin: {
                    '0%':   { opacity: '0', transform: 'translateY(6px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
            },
            animation: {
                pulsering: 'pulsering 1.8s ease-out infinite',
                streamin: 'streamin 0.4s ease-out both',
            },
        },
    },
    plugins: [],
};
