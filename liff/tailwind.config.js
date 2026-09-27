/** @type {import('tailwindcss').Config} */
// 畢業紀念冊：深綠布面封面、燙金、銅版紙白頁、原子筆藍、印章紅。
//   brand   = 原子筆藍     可點擊、選取中、連結
//   accent  = 燙金         第一名、史詩
//   danger  = 印章紅       傳說、錯誤
//   success = 綠           增加、完成
//   cloth   = 布面深綠     封面帶、選取中的分段控制
//   trip    = 牛皮紙棕     旅行
// slate 換成中性灰（略帶綠），所有頁面自動套用。
export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        slate: {
          50: '#F7F8F6',
          100: '#EEF0ED',
          200: '#DDE1DC',
          300: '#C5CAC4',
          400: '#8C938C',
          500: '#646B65',
          600: '#4B524C',
          700: '#373D38',
          800: '#262B27',
          900: '#191D1A',
          950: '#101310',
        },
        brand: {
          50: '#EEF1FA',
          100: '#D8DFF3',
          200: '#B0BEE6',
          300: '#7F95D2',
          400: '#4F6CBD',
          500: '#2346A0',
          600: '#1E3C8A',
          700: '#193272',
          800: '#14285B',
          900: '#0F1E45',
          950: '#0A142E',
        },
        accent: {
          50: '#FAF5E9',
          100: '#F2E6C6',
          200: '#E6D09A',
          300: '#D6B872',
          400: '#C6A252',
          500: '#B8943A',
          600: '#8F7020',
          700: '#6E5618',
          800: '#554213',
          900: '#3D2F0D',
          950: '#281F09',
        },
        success: {
          50: '#EAF4EE',
          100: '#CFE6D8',
          200: '#A1CCB2',
          300: '#6DAF87',
          400: '#3F9463',
          500: '#2E7D4F',
          600: '#266A43',
          700: '#1F5736',
          800: '#18442A',
          900: '#11311E',
          950: '#0A1F13',
        },
        danger: {
          50: '#FBEDEB',
          100: '#F4D3CF',
          200: '#E8A69F',
          300: '#DA766C',
          400: '#C9523F',
          500: '#B8332A',
          600: '#9C2A23',
          700: '#80221C',
          800: '#641B16',
          900: '#48130F',
          950: '#300C0A',
        },
        info: {
          50: '#EEF1FA',
          100: '#D8DFF3',
          500: '#2346A0',
          600: '#1E3C8A',
          700: '#193272',
        },
        trip: {
          50: '#F6F0E7',
          100: '#EADCC5',
          200: '#D6BB90',
          500: '#9A7040',
          600: '#7E5A32',
          700: '#624527',
        },
        sign: '#1E3A2F',
        cloth: '#1E3A2F',
        foil: '#B8943A',
        surface: {
          DEFAULT: '#FFFFFF',
          subtle: '#F7F8F6',
          muted: '#EEF0ED',
        },
      },
      fontFamily: {
        sans: ['"Noto Sans TC"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"Barlow Semi Condensed"', '"Noto Sans TC"', 'sans-serif'],
        num: ['"Barlow Semi Condensed"', '"Noto Sans TC"', 'sans-serif'],
        // 封面大標題：明體（紀念冊封面、獎狀）
        display: ['"Noto Serif TC"', 'serif'],
        // 同學留言、稱號：手寫楷體
        hand: ['"LXGW WenKai TC"', '"Noto Sans TC"', 'serif'],
      },
      boxShadow: {
        card: 'none',
        lift: 'none',
        pop: '0 12px 28px -12px rgba(17,18,20,0.35)',
        glow: 'none',
        sm: 'none',
        md: 'none',
        lg: 'none',
        xl: 'none',
        '2xl': 'none',
        xs: 'none',
        '2xs': 'none',
        inner: 'none',
      },
      borderRadius: {
        sm: '2px',
        DEFAULT: '3px',
        md: '3px',
        lg: '4px',
        xl: '4px',
        '2xl': '4px',
        '3xl': '6px',
        xl2: '4px',
      },
      transitionTimingFunction: {
        'out-expo': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'in-out-soft': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
}
