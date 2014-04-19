angular.module('hosts')

.controller('hostDetailCtrl', ($scope, host) ->
    $scope.host = host
)