angular.module('hosts')

.controller('hostListCtrl', ($scope, $http, Host) ->
    $scope.hosts = []

    $http.get('/api/v1/hosts/')
        .success (data) ->
            for item in data
                host = new Host()
                host.fromServer(item)
                $scope.hosts.push(host)
)