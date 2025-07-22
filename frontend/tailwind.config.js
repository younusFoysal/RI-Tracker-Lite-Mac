/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
        extend: {
            animation: {
                'spin-fast': 'spin 0.5s linear 2', // 2 spins over 1s
            },
        },
    },
    plugins: [],
}
