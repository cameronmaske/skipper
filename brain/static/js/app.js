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
    }).state('_.hosts.create', {
      url: 'add/',
      resolve: {
        host: function (Host) {
          return new Host({});
        }
      },
      views: {
        '@_': {
          templateUrl: 'hostDetail.template',
          controller: 'hostDetailCtrl'
        }
      }
    }).state('_.hosts.detail', {
      url: '{hostId}/',
      resolve: {
        host: function (Host, $stateParams) {
          var host;
          host = new Host({ id: $stateParams.hostId });
          host.fetch();
          return host;
        }
      },
      views: {
        '@_': {
          templateUrl: 'hostDetail.template',
          controller: 'hostDetailCtrl'
        }
      }
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
angular.module('common', []);
angular.module('hosts', []);
var __indexOf = [].indexOf || function (item) {
    for (var i = 0, l = this.length; i < l; i++) {
      if (i in this && this[i] === item)
        return i;
    }
    return -1;
  };
angular.module('common').factory('Model', [
  '$q',
  '$log',
  '$http',
  function ($q, $log, $http) {
    var Model, camelCase, notImplementedException, underScore;
    camelCase = function (input) {
      return input.toLowerCase().replace(/-(.)/g, function (match, group) {
        return group.toUpperCase();
      });
    };
    underScore = function (input) {
      return input.replace(/([A-Z])/g, function (match) {
        return '_' + match.toLowerCase();
      });
    };
    notImplementedException = function (message) {
      return message;
    };
    Model = function () {
      /*
    A base model class that does most of the common heavy lifting!
    
    Example:
    
        class User extends Model
            @id 'id', defaults: null
            @field 'name', default: 'Jonathan'
            @field 'friends', defaults: -> []
            url: -> "/api/user/{@id}"
    
        >>> user = new User()
        >>> user.name
        'Jonathan'
        >>> user.friends.length
        0
    
    Note: When declaring a field that points to a javascript object (e.g
    {}, [], new Object()...) it's best to declare to be invoked by a function
    (e.g. the 'friends field above').
    Otherwise, all models made will share the same Object. This means that
    declaring a 'new Model' with not reset the field.
     */
      Model.field = function (name, options) {
        if (this.fields == null) {
          this.fields = {};
        }
        return this.fields[name] = options || {};
      };
      function Model(attributes, kwargs) {
        var fieldNames, name, options, value, _ref;
        if (kwargs == null) {
          kwargs = {};
        }
        fieldNames = [];
        _ref = this.constructor.fields;
        for (name in _ref) {
          options = _ref[name];
          value = attributes != null ? attributes[name] : void 0;
          if (_.isUndefined(attributes != null ? attributes[name] : void 0)) {
            value = angular.isFunction(options['default']) ? options['default']() : options['default'];
          }
          this[name] = value;
          fieldNames.push(name);
        }
        this.fieldNames = fieldNames;
      }
      Model.prototype.toServer = function () {
        var attributes, field, value, _i, _len, _ref;
        attributes = {};
        _ref = this.fieldNames;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          field = _ref[_i];
          value = this[field];
          attributes[underScore(field)] = value;
        }
        return attributes;
      };
      Model.prototype.fromServer = function (attributes) {
        var camelKey, key, value, _results;
        _results = [];
        for (key in attributes) {
          value = attributes[key];
          camelKey = camelCase(key);
          if (__indexOf.call(this.fieldNames, camelKey) >= 0) {
            _results.push(this[camelKey] = value);
          } else {
            _results.push(void 0);
          }
        }
        return _results;
      };
      Model.prototype.url = function () {
        throw new notImplementedException('url() function is not implemented.');
      };
      Model.prototype.save = function () {
        var deferred;
        deferred = $q.defer();
        $http({
          method: 'POST',
          url: this.url(),
          data: this.toServer()
        }).success(function (_this) {
          return function (data) {
            _this.fromServer(data);
            $log.info('Succesfully saved the ' + _this.constructor.name + '.');
            return deferred.resolve(data);
          };
        }(this)).error(function (_this) {
          return function (data) {
            $log.error('Failed to save the ' + _this.constructor.name + '..');
            return deferred.reject(data);
          };
        }(this));
        return deferred.promise;
      };
      Model.prototype.remove = function () {
        var deferred;
        deferred = $q.defer();
        $http({
          method: 'DELETE',
          url: this.url()
        }).success(function (data) {
          $log.info('Succesfully delete the ' + this.constructor.name);
          return deferred.resolve(data);
        }).error(function (data) {
          $log.error('Failed to delete the ' + this.constructor.name);
          return deferred.reject(data);
        });
        return deferred.promise;
      };
      return Model;
    }();
    return Model;
  }
]);
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
  'host',
  function ($scope, host) {
    return $scope.host = host;
  }
]);
angular.module('hosts').controller('hostListCtrl', [
  '$scope',
  '$http',
  'Host',
  function ($scope, $http, Host) {
    $scope.hosts = [];
    return $http.get('/api/v1/hosts/').success(function (data) {
      var host, item, _i, _len, _results;
      _results = [];
      for (_i = 0, _len = data.length; _i < _len; _i++) {
        item = data[_i];
        host = new Host();
        host.fromServer(item);
        _results.push($scope.hosts.push(host));
      }
      return _results;
    });
  }
]);
var __hasProp = {}.hasOwnProperty, __extends = function (child, parent) {
    for (var key in parent) {
      if (__hasProp.call(parent, key))
        child[key] = parent[key];
    }
    function ctor() {
      this.constructor = child;
    }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor();
    child.__super__ = parent.prototype;
    return child;
  };
angular.module('hosts').factory('Host', [
  '$http',
  'Model',
  function ($http, Model) {
    var Host;
    Host = function (_super) {
      __extends(Host, _super);
      function Host() {
        return Host.__super__.constructor.apply(this, arguments);
      }
      Host.field('id', { defaults: null });
      Host.field('address', { 'default': null });
      Host.field('port', { 'default': 22 });
      Host.prototype.url = function () {
        if (this.id) {
          return '/api/v1/hosts/' + id + '/';
        } else {
          return '/api/v1/hosts/';
        }
      };
      return Host;
    }(Model);
    return Host;
  }
]);