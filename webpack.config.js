const webpack = require('webpack');
const path = require('path');

const config = {
    entry: {
        bundle: [path.resolve(__dirname, 'unemployment', 'js/index.jsx')],
        application_details: [path.resolve(__dirname, 'applications', 'js/details.jsx')]
    },
    output: {
        path: path.resolve(__dirname, 'static'),
        filename: '[name].js',
    },
    module: {
        rules: [
            {
                test: /\.css$/i,
                use: [
                    'style-loader',
                    'css-loader'
                ]
            }
        ]
    },
    resolve: {
        extensions: ['.js', '.jsx', '.css']
    },
    plugins: [
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery'
        })
    ]
};

module.exports = config;

    
