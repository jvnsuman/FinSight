/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: '#02C39A', // mint
        accent: '#028090',  // teal
        ink: {
          DEFAULT: '#1E293B',
          light: '#64748B',
          dark: '#0B2E33', // navy
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
      animation: {
        'fade-in-up': 'fadeInUp 0.8s ease-out forwards',
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      }
    },
  },
  plugins: [],
}
