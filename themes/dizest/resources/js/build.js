var json_array_parse = function (val, defaultvalue) {
    try {
        return JSON.parse(val);
    } catch (e) {
        if (defaultvalue)
            return defaultvalue;
    }
    return val;
}

var _builder = function ($scope, $timeout) {
    $scope.monaco = function (language) {
        var opt = {
            value: '',
            language: language,
            theme: "vs",
            fontSize: 14,
            automaticLayout: true,
            minimap: {
                enabled: false
            }
        };

        return opt;
    }
}

var cache_builder = function (version) {
    return {
        get: function (_default) {
            return json_array_parse(localStorage[version], _default);
        },
        update: function (value) {
            localStorage[version] = JSON.stringify(angular.copy(value));
        },
        claer: function () {
            delete localStorage[version];
        }
    };
}