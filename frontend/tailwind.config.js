/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: '#1E293B',
          light: '#64748B',
        },
        navy: {
          DEFAULT: '#0B2E33',
          light: '#0F3A3F',
        },
        teal: {
          DEFAULT: '#028090',
          light: '#02A8BD',
        },
        mint: {
          DEFAULT: '#02C39A',
          light: '#CFF5EA',
        },
        coral: {
          DEFAULT: '#E0574B',
          light: '#FBE4E1',
        },
        surface: '#F7F9F8',
      },
      fontFamily: {
        display: ['"Fraunces"', 'serif'],
        body: ['"Inter"', 'sans-serif'],
      },
      fontFeatureSettings: {
        tabular: '"tnum"',
      },
      boxShadow: {
        card: '0 1px 3px rgba(11, 46, 51, 0.06), 0 1px 2px rgba(11, 46, 51, 0.04)',
        soft: '0 4px 16px rgba(11, 46, 51, 0.08)',
      },
      borderRadius: {
        xl: '0.875rem',
      },
    },
  },
  plugins: [],
}
