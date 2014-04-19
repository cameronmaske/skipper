installedApps = [
    # 3rd party.
    'ui.router'
    'ngTemplates'

    # Local.
    'common'
    'hosts'
]

app = angular.module('app', installedApps)

app.config(($stateProvider, $urlRouterProvider) ->
  $stateProvider
    .state('_'
      url: '/'
      templateUrl: 'base.template')
    .state('_.hosts'
      url: 'hosts/'
      templateUrl: 'hostList.template'
      controller: 'hostListCtrl')
    .state('_.hosts.create'
      url: 'add/'
      resolve:
        host: (Host) ->
          return new Host({})
      views:
        "@_":
          templateUrl: 'hostDetail.template'
          controller: 'hostDetailCtrl')
    .state('_.hosts.detail'
      url: '{hostId}/'
      resolve:
        host: (Host, $stateParams) ->
          host = new Host({id: $stateParams.hostId})
          host.fetch()
          return host
      views:
        "@_":
          templateUrl: 'hostDetail.template'
          controller: 'hostDetailCtrl')
  $urlRouterProvider.otherwise('/')
)

.config(($httpProvider) ->
    # Makes any POST http requests play nicely with Django's CSRF protection.
    # Add Header to comply with Django's CSRF implementation
    $httpProvider.defaults.headers.common['X-CSRFToken'] = CSRF
)

.run(($rootScope, $state, Oops, pleaseHold) ->
    $rootScope.errors = Oops.init()
    $rootScope.loading = pleaseHold.init()
    $rootScope.$state = $state
)