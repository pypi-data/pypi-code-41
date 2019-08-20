from .config import Mode

javascript_libraries = {
    Mode.DEVELOPMENT: [{
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/react/16.8.6/umd/react.development.js',
            'hash': 'sha256-9H05eCUa5x4G28dytYBwoAXkR3XgPE3sCogyXhrINwo=',
        },{
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/react-dom/16.8.4/umd/react-dom.development.js',
            'hash': 'sha256-zaBIa6kuwEspzOIU5TeB5bATnxmvJFmht9smi5jLH/Q=',
        },{
            'url': 'https://unpkg.com/@material-ui/core@4.3.1/umd/material-ui.development.js',
            'hash': 'sha256-upouvKCn4yjDmMAMdOYw4RwWGG9xNm7KifNX81sp9Ag=',
        },{
            'url': 'https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-svg-core@1.2.21/index.js',
            'hash': 'sha256-v0YHQ2mwbxSbi6TzwAlY3vjJFG3FN9HRJGmXE/hCecs=',
        }, {
            'url': 'https://cdn.jsdelivr.net/npm/@fortawesome/free-solid-svg-icons@5.10.1/index.js',
            'hash': 'sha256-oSkdBl+Zjb67LV7yVUSCgWSMq3bfHzJ9Jz5l+Te4Y6s=',
        }, {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.24.0/moment-with-locales.js',
            'hash': 'sha256-dgFbqbQVzjkZPQxWd8PBtzGiRBhChc4I2wO/q/s+Xeo=',
        }, {
            'url': 'https://cdn.jsdelivr.net/npm/react-draggable@3.3.0/dist/react-draggable.js',
            'hash': 'sha256-dx6xPZVJdlAEbit+OnKSKb1JOwcJ7vyMdwatshRtm/U=',
        }, {
            'url': 'https://unpkg.com/prop-types/prop-types.min.js',
            'hash': 'sha256-TIg1BRfugqpPM2jmfvGkU8pmNtz6ZEm049b6pch3Bm4=',
        }, {
            'url': 'https://unpkg.com/recharts/umd/Recharts.min.js',
            'hash': 'sha256-1UBekyQ4ydBFe1qngtBJZUc0NhsSLbrl85xJxaNsl1o=',
        }, {
            'url': 'https://unpkg.com/react-redux@latest/dist/react-redux.js',
            'hash': 'sha256-gwdmcqoEI0ZtF7xXwDtX1afD9vSVsBCRKfoDrMF8z9U=',
        }],
    Mode.PRODUCTION: [{
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/react/16.8.6/umd/react.production.min.js',
            'hash': 'sha256-3vo65ZXn5pfsCfGM5H55X+SmwJHBlyNHPwRmWAPgJnM=',
        },{
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/react-dom/16.8.6/umd/react-dom.production.min.js',
            'hash': 'sha256-qVsF1ftL3vUq8RFOLwPnKimXOLo72xguDliIxeffHRc=',
        },{
            'url': 'https://unpkg.com/@material-ui/core@4.3.1/umd/material-ui.production.min.js',
            'hash': 'sha256-Ulx0cEzoGy7n7MfY5i4p1eMoYYMvoiS4aE2WpSQ2o1M=',
        },{
            'url': 'https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-svg-core@1.2.21/index.min.js',
            'hash': 'sha256-rP06f4bKRPwHs7l65xPApnEtLhaPvduxlgoBKgIzeSY=',
        }, {
            'url': 'https://cdn.jsdelivr.net/npm/@fortawesome/free-solid-svg-icons@5.10.1/index.min.js',
            'hash': 'sha256-NI6DpORWIWtjcLkVGZ6/uqbtYgU/DkNhwsX+QaLd5u4=',
        }, {
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.24.0/moment-with-locales.min.js',
            'hash': 'sha256-AdQN98MVZs44Eq2yTwtoKufhnU+uZ7v2kXnD5vqzZVo=',
        }, {
            'url': 'https://cdn.jsdelivr.net/npm/react-draggable@3.3.2/dist/react-draggable.min.js',
            'hash': 'sha256-Bz00T+A2ZjG2P8ULO5VodkZd/JKF0sAHWFxz+uBRkxE=',
        }, {
            'url': 'https://unpkg.com/prop-types/prop-types.min.js',
            'hash': 'sha256-TIg1BRfugqpPM2jmfvGkU8pmNtz6ZEm049b6pch3Bm4=',
        }, {
            'url': 'https://unpkg.com/recharts/umd/Recharts.min.js',
            'hash': 'sha256-1UBekyQ4ydBFe1qngtBJZUc0NhsSLbrl85xJxaNsl1o=',
        }, {
            'url': 'https://unpkg.com/react-redux@latest/dist/react-redux.min.js',
            'hash': 'sha256-nTG59mYUbOhPTfrbR/WDccIPzEDBGOv6+cQHCsMTHtk=',
        }],
}
