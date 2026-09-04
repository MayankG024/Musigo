/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  // Pruned content globs to reduce file system scanning overhead.
  // Using Next.js App Router: primary source locations are ./app, ./src (lib/components), and ./components if kept separate.
  // Removed legacy './pages' (unused) and avoided redundant overlap.
  content: [
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      fontFamily: {
        'spotify': ['Poppins', 'sans-serif'],
      },
      colors: {
        spotify: {
          green: '#1DB954',
        },
        // Aliases used by discover page (map to emerald/stone to avoid unknown classes)
        musigo: {
          green: {
            600: '#059669',
            700: '#047857',
            800: '#065f46',
          },
          beige: {
            50: '#fafaf9',
            100: '#f5f5f4',
          },
        },
        dark: {
          primary: 'hsl(240, 30%, 8%)',
          secondary: 'hsl(250, 35%, 12%)',
          tertiary: 'hsl(260, 40%, 16%)',
        },
        bright: {
            purple: 'hsl(280, 100%, 75%)',
            blue: 'hsl(220, 100%, 70%)',
            green: 'hsl(160, 80%, 60%)',
            yellow: 'hsl(50, 100%, 70%)',
            pink: 'hsl(320, 100%, 75%)',
            cyan: 'hsl(180, 100%, 70%)',
        },
        text: {
          bright: 'hsl(0, 0%, 95%)',
          medium: 'hsl(0, 0%, 80%)',
          dim: 'hsl(0, 0%, 65%)',
        },
        glass: {
          dark: 'rgba(255, 255, 255, 0.1)',
          border: 'rgba(255, 255, 255, 0.2)',
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: { DEFAULT: 'hsl(var(--primary))', foreground: 'hsl(var(--primary-foreground))' },
        secondary: { DEFAULT: 'hsl(var(--secondary))', foreground: 'hsl(var(--secondary-foreground))' },
        destructive: { DEFAULT: 'hsl(var(--destructive))', foreground: 'hsl(var(--destructive-foreground))' },
        muted: { DEFAULT: 'hsl(var(--muted))', foreground: 'hsl(var(--muted-foreground))' },
        accent: { DEFAULT: 'hsl(var(--accent))', foreground: 'hsl(var(--accent-foreground))' },
        popover: { DEFAULT: 'hsl(var(--popover))', foreground: 'hsl(var(--popover-foreground))' },
        card: { DEFAULT: 'hsl(var(--card))', foreground: 'hsl(var(--card-foreground))' },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
