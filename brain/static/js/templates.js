(function(module) {
try {
  module = angular.module('ngTemplates');
} catch (e) {
  module = angular.module('ngTemplates', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('base.template',
    '<div class="container"><!-- Static navbar --><div class="navbar navbar-default" role="navigation"><div class="container-fluid"><div class="navbar-header"><button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse"><span class="sr-only">Toggle navigation</span> <span class="icon-bar"></span> <span class="icon-bar"></span> <span class="icon-bar"></span></button> <a class="navbar-brand" ui-sref="_">skipper</a></div><div class="navbar-collapse collapse"><ul class="nav navbar-nav"><li><a ui-sref="_.hosts">Hosts</a></li></ul></div></div></div><p ng-repeat="(name, errror) in errors.current" class="alert alert-danger" ng-show="errors.current"><strong>{{ name }}</strong>: {{ error.join(\', \') }}</p><div ui-view=""></div></div>');
}]);
})();

(function(module) {
try {
  module = angular.module('ngTemplates');
} catch (e) {
  module = angular.module('ngTemplates', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('hostDetail.template',
    'Host Detail');
}]);
})();

(function(module) {
try {
  module = angular.module('ngTemplates');
} catch (e) {
  module = angular.module('ngTemplates', []);
}
module.run(['$templateCache', function($templateCache) {
  $templateCache.put('hostList.template',
    '<div class="list-group"><a class="list-group-item active" ng-repeat="host in host" ui-sref="_.hosts.detail({hostId:host.id})"><h4 class="list-group-item-heading">{{ host.hostname}}:{{host.port}}</h4><p class="list-group-item-text">Status Check</p></a></div><a class="list-group-item active" ng-show="!hosts.length" ui-sref="_.host.create">Add a host.</a>');
}]);
})();
