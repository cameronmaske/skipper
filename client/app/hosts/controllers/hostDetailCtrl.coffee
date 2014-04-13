angular.module('hosts')

.controller('hostDetailCtrl', ($scope, $http) ->
    $scope.hosts = []

    $http.get('/api/hosts', (results) ->
        for host in results
            $scope.hosts.push(host))

)