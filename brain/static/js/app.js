var app, installedApps;
installedApps = [
  'ui.router',
  'ngTemplates',
  'common',
  'hosts'
];
app = angular.module('app', installedApps);
app.config([
  '$stateProvider',
  '$urlRouterProvider',
  function ($stateProvider, $urlRouterProvider) {
    $stateProvider.state('_', {
      url: '/',
      templateUrl: 'base.template'
    }).state('_.hosts', {
      url: 'hosts/',
      templateUrl: 'hostList.template',
      controller: 'hostListCtrl'
    }).state('_.hosts.detail', {
      url: '{hostId}/',
      templateUrl: 'hostDetail.template',
      controller: 'hostDetailCtrl'
    });
    return $urlRouterProvider.otherwise('/');
  }
]).config([
  '$httpProvider',
  function ($httpProvider) {
    return $httpProvider.defaults.headers.common['X-CSRFToken'] = CSRF;
  }
]).run([
  '$rootScope',
  '$state',
  'Oops',
  'pleaseHold',
  function ($rootScope, $state, Oops, pleaseHold) {
    $rootScope.errors = Oops.init();
    $rootScope.loading = pleaseHold.init();
    return $rootScope.$state = $state;
  }
]);
angular.module('hosts', []);
angular.module('common', []);
angular.module('common').factory('Oops', function () {
  var errors;
  errors = { current: null };
  return {
    init: function () {
      return errors;
    },
    clearError: function () {
      return error.current = null;
    },
    setError: function (message) {
      return error.current = message;
    }
  };
});
angular.module('common').factory('pleaseHold', function () {
  var loading;
  loading = {
    state: false,
    message: null
  };
  return {
    init: function () {
      return loading;
    },
    start: function (message) {
      if (message == null) {
        message = null;
      }
      loading.state = true;
      return loading.message = null;
    },
    finished: function () {
      loading.state = false;
      return loading.message = null;
    }
  };
});
angular.module('hosts').controller('hostDetailCtrl', [
  '$scope',
  '$http',
  function ($scope, $http) {
    $scope.hosts = [];
    return $http.get('/api/hosts', function (results) {
      var host, _i, _len, _results;
      _results = [];
      for (_i = 0, _len = results.length; _i < _len; _i++) {
        host = results[_i];
        _results.push($scope.hosts.push(host));
      }
      return _results;
    });
  }
]);
angular.module('hosts').controller('hostListCtrl', [
  '$scope',
  function ($scope) {
  }
]);