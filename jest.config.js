module.exports = {
    testEnvironment: 'node',
    testMatch: ['**/_tests_/**/*.js?(x)', '**/?(*.)+(spec|test).js?(x)'],
    moduleFileExtensions: ['js', 'json', 'jsx', 'node'],
    transformIgnorePatterns: ["/node_modules/(?!axios).+\\.js$"],
};