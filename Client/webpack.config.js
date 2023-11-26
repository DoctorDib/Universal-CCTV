const nodeExternals = require('webpack-node-externals');

module.exports = {
    // other configurations...

    target: 'node',  // Set the target to Node.js environment
    externals: [nodeExternals()],  // Exclude Node.js core modules

    resolve: {
        fallback: {
            crypto: false
        }
    },
};
