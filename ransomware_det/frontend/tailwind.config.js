/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
  	extend: {
  		fontFamily: {
  			century: [
  				'Century Gothic',
  				'sans-serif'
  			],
  		roboto: [
  				'Roboto',
  				'sans-serif'
  			]
  		}
  	}
  },
  plugins: [],
};
